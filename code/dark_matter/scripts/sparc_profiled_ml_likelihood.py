#!/usr/bin/env python3
"""Profile SPARC rotation curves over per-galaxy stellar M/L nuisance parameters.

This is a likelihood scaffold, not a publication-grade SPARC analysis. It
profiles disk and bulge M/L per galaxy with Gaussian log10 priors and optional
intrinsic velocity scatter. Distance and inclination nuisance parameters are
missing from this scaffold.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from d6_capacity_calculator import compute as compute_d6  # noqa: E402
from sparc_rar_compare import EMPIRICAL_RAR_A0, golden_section_minimize  # noqa: E402
from sparc_rotation_curve_compare import (  # noqa: E402
    DEFAULT_MASS_MODELS,
    model_velocity_km_s,
    parse_mass_model_rows,
)


P_PIXEL = 1.630968209403959
LAMBDA_Z6_POISSON = math.exp(-P_PIXEL / 24.0)


def group_by_galaxy(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["ID"]].append(row)
    return dict(grouped)


def has_bulge(rows: list[dict[str, Any]]) -> bool:
    return any(abs(row["Vbul_km_s"]) > 1.0e-9 for row in rows)


def chi2_for_galaxy(
    rows: list[dict[str, Any]],
    a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
    disk_prior: float,
    bulge_prior: float,
    ml_prior_sigma_dex: float,
    intrinsic_scatter_km_s: float,
) -> tuple[float, list[float]]:
    chi2 = 0.0
    residuals = []
    for row in rows:
        v_model = model_velocity_km_s(row, a0, upsilon_disk, upsilon_bulge)
        if v_model is None:
            continue
        sigma2 = row["e_Vobs_km_s"] ** 2 + intrinsic_scatter_km_s**2
        if sigma2 <= 0.0:
            continue
        resid = row["Vobs_km_s"] - v_model
        residuals.append(resid)
        chi2 += resid * resid / sigma2

    if ml_prior_sigma_dex > 0.0:
        chi2 += (math.log10(upsilon_disk / disk_prior) / ml_prior_sigma_dex) ** 2
        if has_bulge(rows):
            chi2 += (math.log10(upsilon_bulge / bulge_prior) / ml_prior_sigma_dex) ** 2
    return chi2, residuals


def golden_minimize_scalar(
    fn: Callable[[float], float],
    left: float,
    right: float,
) -> tuple[float, float]:
    best_log, best_value = golden_section_minimize(
        lambda log_value: fn(10.0**log_value),
        math.log10(left),
        math.log10(right),
        tol=1.0e-5,
        max_iter=80,
    )
    return 10.0**best_log, best_value


def profile_galaxy(
    rows: list[dict[str, Any]],
    a0: float,
    args: argparse.Namespace,
) -> dict[str, Any]:
    disk = args.disk_prior
    bulge = args.bulge_prior
    bulged = has_bulge(rows)

    def objective(disk_value: float, bulge_value: float) -> tuple[float, list[float]]:
        return chi2_for_galaxy(
            rows,
            a0,
            disk_value,
            bulge_value,
            args.disk_prior,
            args.bulge_prior,
            args.ml_prior_sigma_dex,
            args.intrinsic_scatter_km_s,
        )

    for _ in range(args.coordinate_iterations):
        disk, _ = golden_minimize_scalar(
            lambda value: objective(value, bulge)[0],
            args.disk_min,
            args.disk_max,
        )
        if bulged:
            bulge, _ = golden_minimize_scalar(
                lambda value: objective(disk, value)[0],
                args.bulge_min,
                args.bulge_max,
            )

    chi2, residuals = objective(disk, bulge)
    param_count = 1 + int(bulged)
    return {
        "ID": rows[0]["ID"],
        "point_count": len(residuals),
        "has_bulge": bulged,
        "upsilon_disk": disk,
        "upsilon_bulge": bulge if bulged else 0.0,
        "chi2_profiled": chi2,
        "parameter_count": param_count,
        "residuals_km_s": residuals,
    }


def profile_dataset(
    rows: list[dict[str, Any]],
    a0: float,
    args: argparse.Namespace,
) -> dict[str, Any]:
    grouped = group_by_galaxy(rows)
    profiled = [profile_galaxy(galaxy_rows, a0, args) for galaxy_rows in grouped.values()]
    residuals = [resid for row in profiled for resid in row["residuals_km_s"]]
    chi2 = sum(row["chi2_profiled"] for row in profiled)
    point_count = len(residuals)
    param_count = sum(row["parameter_count"] for row in profiled)
    dof = max(1, point_count - param_count)
    disk_values = [row["upsilon_disk"] for row in profiled]
    bulge_values = [row["upsilon_bulge"] for row in profiled if row["has_bulge"]]
    return {
        "a0_m_s2": a0,
        "galaxy_count": len(profiled),
        "point_count": point_count,
        "profiled_parameter_count": param_count,
        "chi2_profiled": chi2,
        "chi2_per_point": chi2 / point_count,
        "chi2_per_dof": chi2 / dof,
        "mean_residual_km_s": mean(residuals),
        "rms_residual_km_s": math.sqrt(sum(value * value for value in residuals) / point_count),
        "median_disk_upsilon": median(disk_values),
        "median_bulge_upsilon": median(bulge_values) if bulge_values else 0.0,
        "galaxy_rows": profiled,
    }


def median(values: list[float]) -> float:
    values_sorted = sorted(values)
    n = len(values_sorted)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2:
        return values_sorted[mid]
    return 0.5 * (values_sorted[mid - 1] + values_sorted[mid])


def compute(args: argparse.Namespace) -> dict[str, Any]:
    rows = parse_mass_model_rows(args.mass_models)
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    a0_z6 = a0_oph / (LAMBDA_Z6_POISSON * LAMBDA_Z6_POISSON)
    scenarios = [
        ("OPH_unit_branch", a0_oph),
        ("OPH_Z6_poisson", a0_z6),
        ("empirical_reference", EMPIRICAL_RAR_A0),
    ]
    scenario_rows = []
    for name, a0 in scenarios:
        stats = profile_dataset(rows, a0, args)
        scenario_rows.append(
            {
                "name": name,
                "a0_m_s2": a0,
                "a0_over_OPH_unit": a0 / a0_oph,
                "stats": {key: value for key, value in stats.items() if key != "galaxy_rows"},
            }
        )
    return {
        "status": {
            "category": "SPARC profiled stellar M/L likelihood scaffold",
            "not_publication_grade": True,
            "profiled_nuisance": "per-galaxy disk and bulge M/L with log10 Gaussian priors",
            "missing_nuisance": ["distance", "inclination", "gas systematics", "covariance"],
        },
        "inputs": {
            "mass_models_path": str(args.mass_models),
            "N_scr": args.n_scr,
            "lambda_Z6_poisson": LAMBDA_Z6_POISSON,
            "disk_prior": args.disk_prior,
            "bulge_prior": args.bulge_prior,
            "ml_prior_sigma_dex": args.ml_prior_sigma_dex,
            "intrinsic_scatter_km_s": args.intrinsic_scatter_km_s,
            "raw_rows": len(rows),
        },
        "scenarios": scenario_rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# SPARC Profiled M/L Likelihood Scaffold")
    print()
    print(
        "Profiles per-galaxy stellar M/L with log10 Gaussian priors. "
        "Distance, inclination, gas systematics, and covariance are missing from this scaffold."
    )
    print()
    print(
        f"M/L priors: disk `{payload['inputs']['disk_prior']}`, "
        f"bulge `{payload['inputs']['bulge_prior']}`, "
        f"sigma `{payload['inputs']['ml_prior_sigma_dex']} dex`; "
        f"intrinsic scatter `{payload['inputs']['intrinsic_scatter_km_s']} km/s`."
    )
    print()
    print(
        "| Scenario | a0 m/s^2 | a0/OPH | chi2/pt | chi2/dof | "
        "RMS km/s | median disk M/L | median bulge M/L |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["scenarios"]:
        stats = row["stats"]
        print(
            f"| {row['name']} | {row['a0_m_s2']:.9e} | "
            f"{row['a0_over_OPH_unit']:.6f} | "
            f"{stats['chi2_per_point']:.6f} | {stats['chi2_per_dof']:.6f} | "
            f"{stats['rms_residual_km_s']:.6f} | "
            f"{stats['median_disk_upsilon']:.6f} | "
            f"{stats['median_bulge_upsilon']:.6f} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mass-models", type=Path, default=DEFAULT_MASS_MODELS)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--disk-prior", type=float, default=0.5)
    parser.add_argument("--bulge-prior", type=float, default=0.7)
    parser.add_argument("--ml-prior-sigma-dex", type=float, default=0.15)
    parser.add_argument("--intrinsic-scatter-km-s", type=float, default=8.0)
    parser.add_argument("--disk-min", type=float, default=0.05)
    parser.add_argument("--disk-max", type=float, default=1.5)
    parser.add_argument("--bulge-min", type=float, default=0.05)
    parser.add_argument("--bulge-max", type=float, default=2.0)
    parser.add_argument("--coordinate-iterations", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compute(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
