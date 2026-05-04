#!/usr/bin/env python3
"""Profile SPARC rotation curves with stellar, distance, inclination, and gas nuisances."""

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
    KPC_M,
    parse_mass_model_rows,
)


DEFAULT_GALAXY_SAMPLE = ROOT / "data" / "external" / "SPARC_Lelli2016c.mrt"
P_PIXEL = 1.630968209403959
LAMBDA_Z6_POISSON = math.exp(-P_PIXEL / 24.0)


def parse_galaxy_sample(path: Path) -> dict[str, dict[str, Any]]:
    sample: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 18:
            continue
        try:
            int(parts[1])
            row = {
                "Galaxy": parts[0],
                "T": int(parts[1]),
                "D_Mpc": float(parts[2]),
                "e_D_Mpc": float(parts[3]),
                "distance_method": int(parts[4]),
                "Inc_deg": float(parts[5]),
                "e_Inc_deg": float(parts[6]),
                "Q": int(parts[17]),
            }
        except ValueError:
            continue
        sample[row["Galaxy"]] = row
    return sample


def group_by_galaxy(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["ID"]].append(row)
    return dict(grouped)


def has_bulge(rows: list[dict[str, Any]]) -> bool:
    return any(abs(row["Vbul_km_s"]) > 1.0e-9 for row in rows)


def median(values: list[float]) -> float:
    values_sorted = sorted(values)
    n = len(values_sorted)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2:
        return values_sorted[mid]
    return 0.5 * (values_sorted[mid - 1] + values_sorted[mid])


def sin_deg(value: float) -> float:
    return math.sin(math.radians(value))


def scaled_model_velocity_km_s(
    row: dict[str, Any],
    a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
    distance_mpc: float,
    gas_scale: float,
) -> float | None:
    distance_ratio = distance_mpc / row["D_Mpc"]
    if distance_ratio <= 0.0 or row["R_kpc"] <= 0.0:
        return None
    vgas = row["Vgas_km_s"]
    vbar2 = distance_ratio * (
        gas_scale * vgas * abs(vgas)
        + upsilon_disk * row["Vdisk_km_s"] ** 2
        + upsilon_bulge * row["Vbul_km_s"] ** 2
    )
    if vbar2 <= 0.0:
        return None
    radius_m = row["R_kpc"] * distance_ratio * KPC_M
    gbar = vbar2 * 1.0e6 / radius_m
    sqrt_x = math.sqrt(gbar / a0)
    p_active = 1.0 - math.exp(-sqrt_x)
    if p_active <= 0.0:
        return None
    gmodel = gbar / p_active
    return math.sqrt(gmodel * radius_m) / 1000.0


def observed_velocity_with_inclination(
    row: dict[str, Any],
    sample: dict[str, Any],
    inclination_deg: float,
) -> tuple[float, float]:
    base_sin = sin_deg(sample["Inc_deg"])
    fit_sin = sin_deg(inclination_deg)
    if base_sin <= 0.0 or fit_sin <= 0.0:
        return row["Vobs_km_s"], row["e_Vobs_km_s"]
    scale = base_sin / fit_sin
    return row["Vobs_km_s"] * scale, row["e_Vobs_km_s"] * scale


def chi2_for_galaxy(
    rows: list[dict[str, Any]],
    sample: dict[str, Any],
    a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
    distance_mpc: float,
    inclination_deg: float,
    gas_scale: float,
    args: argparse.Namespace,
) -> tuple[float, list[float]]:
    chi2 = 0.0
    residuals = []
    for row in rows:
        v_model = scaled_model_velocity_km_s(
            row,
            a0,
            upsilon_disk,
            upsilon_bulge,
            distance_mpc,
            gas_scale,
        )
        if v_model is None:
            continue
        v_obs, e_vobs = observed_velocity_with_inclination(row, sample, inclination_deg)
        sigma2 = e_vobs**2 + args.intrinsic_scatter_km_s**2
        if sigma2 <= 0.0:
            continue
        resid = v_obs - v_model
        residuals.append(resid)
        chi2 += resid * resid / sigma2

    if args.ml_prior_sigma_dex > 0.0:
        chi2 += (math.log10(upsilon_disk / args.disk_prior) / args.ml_prior_sigma_dex) ** 2
        if has_bulge(rows):
            chi2 += (math.log10(upsilon_bulge / args.bulge_prior) / args.ml_prior_sigma_dex) ** 2
    if args.profile_distance and sample["e_D_Mpc"] > 0.0:
        chi2 += ((distance_mpc - sample["D_Mpc"]) / sample["e_D_Mpc"]) ** 2
    if args.profile_inclination and sample["e_Inc_deg"] > 0.0:
        chi2 += ((inclination_deg - sample["Inc_deg"]) / sample["e_Inc_deg"]) ** 2
    if args.profile_gas and args.gas_prior_sigma_dex > 0.0:
        chi2 += (math.log10(gas_scale) / args.gas_prior_sigma_dex) ** 2
    return chi2, residuals


def minimize_log_scalar(
    fn: Callable[[float], float],
    left: float,
    right: float,
) -> tuple[float, float]:
    if right <= left:
        value = max(left, 1.0e-12)
        return value, fn(value)
    best_log, best_value = golden_section_minimize(
        lambda log_value: fn(10.0**log_value),
        math.log10(left),
        math.log10(right),
        tol=1.0e-5,
        max_iter=80,
    )
    return 10.0**best_log, best_value


def minimize_linear_scalar(
    fn: Callable[[float], float],
    left: float,
    right: float,
) -> tuple[float, float]:
    if right <= left:
        return left, fn(left)
    return golden_section_minimize(fn, left, right, tol=1.0e-5, max_iter=80)


def distance_bounds(sample: dict[str, Any], args: argparse.Namespace) -> tuple[float, float]:
    if not args.profile_distance or sample["e_D_Mpc"] <= 0.0:
        return sample["D_Mpc"], sample["D_Mpc"]
    span = args.distance_sigma_window * sample["e_D_Mpc"]
    return max(args.distance_min_mpc, sample["D_Mpc"] - span), sample["D_Mpc"] + span


def inclination_bounds(sample: dict[str, Any], args: argparse.Namespace) -> tuple[float, float]:
    if not args.profile_inclination or sample["e_Inc_deg"] <= 0.0:
        return sample["Inc_deg"], sample["Inc_deg"]
    span = args.inclination_sigma_window * sample["e_Inc_deg"]
    return (
        max(args.inclination_min_deg, sample["Inc_deg"] - span),
        min(args.inclination_max_deg, sample["Inc_deg"] + span),
    )


def profile_galaxy(
    rows: list[dict[str, Any]],
    sample: dict[str, Any],
    a0: float,
    args: argparse.Namespace,
) -> dict[str, Any]:
    disk = args.disk_prior
    bulge = args.bulge_prior
    distance = sample["D_Mpc"]
    inclination = sample["Inc_deg"]
    gas = 1.0
    bulged = has_bulge(rows)
    d_left, d_right = distance_bounds(sample, args)
    i_left, i_right = inclination_bounds(sample, args)

    def objective(
        disk_value: float,
        bulge_value: float,
        distance_value: float,
        inclination_value: float,
        gas_value: float,
    ) -> tuple[float, list[float]]:
        return chi2_for_galaxy(
            rows,
            sample,
            a0,
            disk_value,
            bulge_value,
            distance_value,
            inclination_value,
            gas_value,
            args,
        )

    for _ in range(args.coordinate_iterations):
        disk, _ = minimize_log_scalar(
            lambda value: objective(value, bulge, distance, inclination, gas)[0],
            args.disk_min,
            args.disk_max,
        )
        if bulged:
            bulge, _ = minimize_log_scalar(
                lambda value: objective(disk, value, distance, inclination, gas)[0],
                args.bulge_min,
                args.bulge_max,
            )
        if args.profile_distance:
            distance, _ = minimize_linear_scalar(
                lambda value: objective(disk, bulge, value, inclination, gas)[0],
                d_left,
                d_right,
            )
        if args.profile_inclination:
            inclination, _ = minimize_linear_scalar(
                lambda value: objective(disk, bulge, distance, value, gas)[0],
                i_left,
                i_right,
            )
        if args.profile_gas:
            gas, _ = minimize_log_scalar(
                lambda value: objective(disk, bulge, distance, inclination, value)[0],
                args.gas_min,
                args.gas_max,
            )

    chi2, residuals = objective(disk, bulge, distance, inclination, gas)
    param_count = 1 + int(bulged)
    param_count += int(args.profile_distance)
    param_count += int(args.profile_inclination)
    param_count += int(args.profile_gas)
    return {
        "ID": rows[0]["ID"],
        "point_count": len(residuals),
        "has_bulge": bulged,
        "upsilon_disk": disk,
        "upsilon_bulge": bulge if bulged else 0.0,
        "distance_ratio": distance / sample["D_Mpc"],
        "inclination_delta_deg": inclination - sample["Inc_deg"],
        "gas_scale": gas,
        "chi2_profiled": chi2,
        "parameter_count": param_count,
        "residuals_km_s": residuals,
    }


def filter_rows(
    rows: list[dict[str, Any]],
    sample: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    filtered = []
    for row in rows:
        meta = sample.get(row["ID"])
        if meta is None:
            continue
        if meta["Q"] > args.max_quality:
            continue
        if meta["Inc_deg"] < args.min_inclination_deg:
            continue
        filtered.append(row)
    return filtered


def profile_dataset(
    rows: list[dict[str, Any]],
    sample: dict[str, dict[str, Any]],
    a0: float,
    args: argparse.Namespace,
) -> dict[str, Any]:
    grouped = group_by_galaxy(rows)
    profiled = [
        profile_galaxy(galaxy_rows, sample[galaxy_id], a0, args)
        for galaxy_id, galaxy_rows in grouped.items()
        if galaxy_id in sample
    ]
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
        "median_distance_ratio": median([row["distance_ratio"] for row in profiled]),
        "median_inclination_delta_deg": median(
            [row["inclination_delta_deg"] for row in profiled]
        ),
        "median_gas_scale": median([row["gas_scale"] for row in profiled]),
        "galaxy_rows": profiled,
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    sample = parse_galaxy_sample(args.galaxy_sample)
    rows = filter_rows(parse_mass_model_rows(args.mass_models), sample, args)
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
        stats = profile_dataset(rows, sample, a0, args)
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
            "category": "SPARC systematic likelihood scaffold",
            "profiled_nuisance": [
                "per-galaxy disk M/L",
                "per-galaxy bulge M/L when present",
                "distance with SPARC prior",
                "inclination with SPARC prior",
                "gas scale with shared prior width",
            ],
            "missing_nuisance": [
                "full covariance",
                "stellar-population hyperpriors",
                "beam-smearing model",
                "asymmetric-drift model",
                "survey-selection model",
            ],
        },
        "inputs": {
            "mass_models_path": str(args.mass_models),
            "galaxy_sample_path": str(args.galaxy_sample),
            "N_scr": args.n_scr,
            "lambda_Z6_poisson": LAMBDA_Z6_POISSON,
            "max_quality": args.max_quality,
            "min_inclination_deg": args.min_inclination_deg,
            "ml_prior_sigma_dex": args.ml_prior_sigma_dex,
            "intrinsic_scatter_km_s": args.intrinsic_scatter_km_s,
            "gas_prior_sigma_dex": args.gas_prior_sigma_dex,
            "raw_rows_after_cuts": len(rows),
        },
        "scenarios": scenario_rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    inputs = payload["inputs"]
    print("# SPARC Systematic Likelihood Scaffold")
    print()
    print(
        "Profiles stellar M/L, distance, inclination, and gas scale per galaxy "
        "with fixed priors declared before branch comparison."
    )
    print()
    print(
        f"Cuts: Q <= `{inputs['max_quality']}`, "
        f"inclination >= `{inputs['min_inclination_deg']} deg`; "
        f"rows after cuts `{inputs['raw_rows_after_cuts']}`."
    )
    print()
    print(
        "| Scenario | a0 m/s^2 | a0/OPH | chi2/pt | chi2/dof | RMS km/s | "
        "median disk M/L | median D/D0 | median di deg | median gas |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["scenarios"]:
        stats = row["stats"]
        print(
            f"| {row['name']} | {row['a0_m_s2']:.9e} | "
            f"{row['a0_over_OPH_unit']:.6f} | "
            f"{stats['chi2_per_point']:.6f} | {stats['chi2_per_dof']:.6f} | "
            f"{stats['rms_residual_km_s']:.6f} | "
            f"{stats['median_disk_upsilon']:.6f} | "
            f"{stats['median_distance_ratio']:.6f} | "
            f"{stats['median_inclination_delta_deg']:.6f} | "
            f"{stats['median_gas_scale']:.6f} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mass-models", type=Path, default=DEFAULT_MASS_MODELS)
    parser.add_argument("--galaxy-sample", type=Path, default=DEFAULT_GALAXY_SAMPLE)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--max-quality", type=int, default=2)
    parser.add_argument("--min-inclination-deg", type=float, default=30.0)
    parser.add_argument("--disk-prior", type=float, default=0.5)
    parser.add_argument("--bulge-prior", type=float, default=0.7)
    parser.add_argument("--ml-prior-sigma-dex", type=float, default=0.15)
    parser.add_argument("--intrinsic-scatter-km-s", type=float, default=8.0)
    parser.add_argument("--disk-min", type=float, default=0.05)
    parser.add_argument("--disk-max", type=float, default=1.5)
    parser.add_argument("--bulge-min", type=float, default=0.05)
    parser.add_argument("--bulge-max", type=float, default=2.0)
    parser.add_argument("--profile-distance", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--distance-min-mpc", type=float, default=0.1)
    parser.add_argument("--distance-sigma-window", type=float, default=3.0)
    parser.add_argument("--profile-inclination", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--inclination-min-deg", type=float, default=5.0)
    parser.add_argument("--inclination-max-deg", type=float, default=89.5)
    parser.add_argument("--inclination-sigma-window", type=float, default=3.0)
    parser.add_argument("--profile-gas", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--gas-prior-sigma-dex", type=float, default=0.08)
    parser.add_argument("--gas-min", type=float, default=0.5)
    parser.add_argument("--gas-max", type=float, default=1.5)
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
