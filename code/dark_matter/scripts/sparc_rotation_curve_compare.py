#!/usr/bin/env python3
"""Compare the static OPH RAR law against SPARC mass-model rotation curves.

This is not a full SPARC fit. It uses fixed stellar mass-to-light ratios and
statistical velocity errors only, so the chi2 values are diagnostic rather than
publication-grade.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

from d6_capacity_calculator import compute as compute_d6
from sparc_rar_compare import EMPIRICAL_RAR_A0, golden_section_minimize, gobs_model


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MASS_MODELS = ROOT / "data" / "external" / "SPARC_MassModels_Lelli2016c.mrt"
KPC_M = 3.085_677_581_491_3673e19


def parse_mass_model_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) != 10:
            continue
        try:
            rows.append(
                {
                    "ID": parts[0],
                    "D_Mpc": float(parts[1]),
                    "R_kpc": float(parts[2]),
                    "Vobs_km_s": float(parts[3]),
                    "e_Vobs_km_s": float(parts[4]),
                    "Vgas_km_s": float(parts[5]),
                    "Vdisk_km_s": float(parts[6]),
                    "Vbul_km_s": float(parts[7]),
                    "SBdisk": float(parts[8]),
                    "SBbul": float(parts[9]),
                }
            )
        except ValueError:
            continue
    return rows


def baryonic_velocity_squared(
    row: dict[str, Any],
    upsilon_disk: float,
    upsilon_bulge: float,
) -> float:
    vgas = row["Vgas_km_s"]
    return (
        vgas * abs(vgas)
        + upsilon_disk * row["Vdisk_km_s"] ** 2
        + upsilon_bulge * row["Vbul_km_s"] ** 2
    )


def model_velocity_km_s(
    row: dict[str, Any],
    a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
) -> float | None:
    vbar2 = baryonic_velocity_squared(row, upsilon_disk, upsilon_bulge)
    if vbar2 <= 0.0 or row["R_kpc"] <= 0.0:
        return None
    radius_m = row["R_kpc"] * KPC_M
    gbar = vbar2 * 1.0e6 / radius_m
    gmodel = gobs_model(gbar, a0)
    return math.sqrt(gmodel * radius_m) / 1000.0


def residual_rows(
    rows: list[dict[str, Any]],
    a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        v_model = model_velocity_km_s(row, a0, upsilon_disk, upsilon_bulge)
        if v_model is None or row["e_Vobs_km_s"] <= 0.0:
            continue
        resid = row["Vobs_km_s"] - v_model
        out.append(
            {
                "ID": row["ID"],
                "R_kpc": row["R_kpc"],
                "Vobs_km_s": row["Vobs_km_s"],
                "e_Vobs_km_s": row["e_Vobs_km_s"],
                "Vmodel_km_s": v_model,
                "residual_km_s": resid,
                "chi2": (resid / row["e_Vobs_km_s"]) ** 2,
            }
        )
    return out


def scenario_stats(
    rows: list[dict[str, Any]],
    a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
) -> dict[str, Any]:
    residuals = residual_rows(rows, a0, upsilon_disk, upsilon_bulge)
    resids = [row["residual_km_s"] for row in residuals]
    galaxy_count = len({row["ID"] for row in residuals})
    chi2 = sum(row["chi2"] for row in residuals)
    return {
        "a0_m_s2": a0,
        "point_count": len(residuals),
        "galaxy_count": galaxy_count,
        "mean_residual_km_s": mean(resids),
        "rms_residual_km_s": math.sqrt(sum(value * value for value in resids) / len(resids)),
        "median_abs_residual_km_s": median([abs(value) for value in resids]),
        "chi2_statistical_velocity_only": chi2,
        "chi2_per_point_statistical_velocity_only": chi2 / len(residuals),
    }


def median(values: list[float]) -> float:
    values_sorted = sorted(values)
    n = len(values_sorted)
    mid = n // 2
    if n % 2:
        return values_sorted[mid]
    return 0.5 * (values_sorted[mid - 1] + values_sorted[mid])


def fit_objective(
    rows: list[dict[str, Any]],
    log10_a0: float,
    upsilon_disk: float,
    upsilon_bulge: float,
) -> float:
    stats = scenario_stats(rows, 10.0**log10_a0, upsilon_disk, upsilon_bulge)
    return stats["chi2_statistical_velocity_only"]


def compute(args: argparse.Namespace) -> dict[str, Any]:
    rows = parse_mass_model_rows(args.mass_models)
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    best_log, _ = golden_section_minimize(
        lambda value: fit_objective(rows, value, args.upsilon_disk, args.upsilon_bulge),
        math.log10(args.fit_min_a0),
        math.log10(args.fit_max_a0),
    )
    a0_best = 10.0**best_log
    scenarios = {
        "OPH_fixed_a0": a0_oph,
        "empirical_reference_a0": EMPIRICAL_RAR_A0,
        "best_fit_fixed_ML_same_function": a0_best,
    }
    scenario_rows = []
    for name, a0 in scenarios.items():
        stats = scenario_stats(rows, a0, args.upsilon_disk, args.upsilon_bulge)
        scenario_rows.append(
            {
                "name": name,
                "a0_m_s2": a0,
                "a0_over_OPH": a0 / a0_oph,
                "stats": stats,
            }
        )
    oph_residuals = residual_rows(rows, a0_oph, args.upsilon_disk, args.upsilon_bulge)
    worst = sorted(oph_residuals, key=lambda item: abs(item["residual_km_s"]), reverse=True)[
        : args.worst_count
    ]
    return {
        "status": {
            "category": "SPARC mass-model rotation-curve diagnostic",
            "not_a_full_fit": True,
            "stellar_mass_to_light_fixed": True,
            "uses_statistical_velocity_errors_only": True,
        },
        "sources": {
            "SPARC_page": "https://astroweb.cwru.edu/SPARC/",
            "mass_model_data": "https://astroweb.cwru.edu/SPARC/MassModels_Lelli2016c.mrt",
            "SPARC_master_paper": "https://arxiv.org/abs/1606.09251",
        },
        "inputs": {
            "mass_models_path": str(args.mass_models),
            "N_scr": args.n_scr,
            "upsilon_disk": args.upsilon_disk,
            "upsilon_bulge": args.upsilon_bulge,
            "raw_rows": len(rows),
        },
        "scenarios": scenario_rows,
        "worst_OPH_velocity_residuals": worst,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# SPARC Rotation-Curve Diagnostic")
    print()
    print(
        "Fixed stellar mass-to-light ratios; statistical velocity errors only. "
        "This is not a full galaxy-by-galaxy fit."
    )
    print()
    print("| Scenario | a0 m/s^2 | a0/OPH | points | galaxies | mean resid km/s | RMS km/s | chi2/pt |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["scenarios"]:
        stats = row["stats"]
        print(
            f"| {row['name']} | {row['a0_m_s2']:.9e} | "
            f"{row['a0_over_OPH']:.6f} | {stats['point_count']} | "
            f"{stats['galaxy_count']} | {stats['mean_residual_km_s']:+.6f} | "
            f"{stats['rms_residual_km_s']:.6f} | "
            f"{stats['chi2_per_point_statistical_velocity_only']:.6f} |"
        )
    print()
    print("Largest absolute OPH velocity residuals:")
    print()
    print("| ID | R kpc | Vobs | Vmodel | residual km/s |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in payload["worst_OPH_velocity_residuals"]:
        print(
            f"| {row['ID']} | {row['R_kpc']:.3g} | {row['Vobs_km_s']:.3g} | "
            f"{row['Vmodel_km_s']:.3g} | {row['residual_km_s']:+.3g} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mass-models", type=Path, default=DEFAULT_MASS_MODELS)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--upsilon-disk", type=float, default=0.5)
    parser.add_argument("--upsilon-bulge", type=float, default=0.7)
    parser.add_argument("--fit-min-a0", type=float, default=0.2e-10)
    parser.add_argument("--fit-max-a0", type=float, default=3.0e-10)
    parser.add_argument("--worst-count", type=int, default=10)
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
