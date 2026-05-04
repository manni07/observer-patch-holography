#!/usr/bin/env python3
"""Compare the static OPH dark response law with SPARC RAR measurements."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

from d6_capacity_calculator import compute as compute_d6


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAR_ALL = ROOT / "data" / "external" / "SPARC_RAR.mrt"
DEFAULT_RAR_BINS = ROOT / "data" / "external" / "SPARC_RARbins.mrt"
EMPIRICAL_RAR_A0 = 1.20e-10


def parse_numeric_rows(path: Path, expected_columns: int) -> list[list[float]]:
    rows: list[list[float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-") and set(stripped) == {"-"}:
            continue
        parts = stripped.split()
        if len(parts) != expected_columns:
            continue
        try:
            rows.append([float(part) for part in parts])
        except ValueError:
            continue
    return rows


def gobs_model(gbar: float, a0: float) -> float:
    if gbar <= 0.0:
        return 0.0
    x = gbar / a0
    p = 1.0 - math.exp(-math.sqrt(x))
    return gbar / p


def log_model(log_gbar: float, a0: float) -> float:
    return math.log10(gobs_model(10.0**log_gbar, a0))


def log_slope(log_gbar: float, a0: float) -> float:
    # Numerical derivative d log10(gobs) / d log10(gbar).
    h = 1.0e-4
    return (log_model(log_gbar + h, a0) - log_model(log_gbar - h, a0)) / (2.0 * h)


def all_data_stats(rows: list[list[float]], a0: float) -> dict[str, float]:
    residuals = []
    weighted_terms = []
    for log_gbar, e_gbar, log_gobs, e_gobs in rows:
        pred = log_model(log_gbar, a0)
        resid = log_gobs - pred
        residuals.append(resid)
        slope = log_slope(log_gbar, a0)
        sigma = math.sqrt(e_gobs**2 + (slope * e_gbar) ** 2)
        if sigma > 0.0:
            weighted_terms.append((resid / sigma) ** 2)

    n = len(residuals)
    rms = math.sqrt(sum(item * item for item in residuals) / n)
    mad = median([abs(item) for item in residuals])
    return {
        "N": float(n),
        "a0_m_s2": a0,
        "mean_residual_dex_data_minus_model": mean(residuals),
        "median_abs_residual_dex": mad,
        "rms_residual_dex": rms,
        "chi2_no_intrinsic": sum(weighted_terms),
        "chi2_per_point_no_intrinsic": sum(weighted_terms) / len(weighted_terms),
    }


def binned_stats(rows: list[list[float]], a0: float) -> dict[str, Any]:
    residual_rows = []
    for log_gbar, log_gobs, sd, n in rows:
        pred = log_model(log_gbar, a0)
        resid = log_gobs - pred
        residual_rows.append(
            {
                "log_gbar": log_gbar,
                "log_gobs": log_gobs,
                "log_model": pred,
                "residual_dex": resid,
                "sd_dex": sd,
                "N": int(n),
            }
        )
    residuals = [row["residual_dex"] for row in residual_rows]
    weighted = sum(row["N"] * row["residual_dex"] ** 2 for row in residual_rows)
    n_total = sum(row["N"] for row in residual_rows)
    return {
        "a0_m_s2": a0,
        "bin_count": len(residual_rows),
        "point_count_in_bins": n_total,
        "mean_residual_dex": mean(residuals),
        "rms_residual_dex_unweighted_bins": math.sqrt(
            sum(item * item for item in residuals) / len(residuals)
        ),
        "rms_residual_dex_weighted_by_N": math.sqrt(weighted / n_total),
        "rows": residual_rows,
    }


def median(values: list[float]) -> float:
    values_sorted = sorted(values)
    n = len(values_sorted)
    mid = n // 2
    if n % 2:
        return values_sorted[mid]
    return 0.5 * (values_sorted[mid - 1] + values_sorted[mid])


def objective(rows: list[list[float]], log10_a0: float) -> float:
    return all_data_stats(rows, 10.0**log10_a0)["chi2_no_intrinsic"]


def golden_section_minimize(
    fn,
    left: float,
    right: float,
    tol: float = 1.0e-7,
    max_iter: int = 200,
) -> tuple[float, float]:
    inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
    inv_phi2 = (3.0 - math.sqrt(5.0)) / 2.0
    h = right - left
    c = left + inv_phi2 * h
    d = left + inv_phi * h
    yc = fn(c)
    yd = fn(d)
    for _ in range(max_iter):
        if abs(right - left) < tol:
            break
        if yc < yd:
            right = d
            d = c
            yd = yc
            h = inv_phi * h
            c = left + inv_phi2 * h
            yc = fn(c)
        else:
            left = c
            c = d
            yc = yd
            h = inv_phi * h
            d = left + inv_phi * h
            yd = fn(d)
    x = 0.5 * (left + right)
    return x, fn(x)


def compute(args: argparse.Namespace) -> dict[str, Any]:
    all_rows = parse_numeric_rows(args.rar_all, 4)
    bin_rows = parse_numeric_rows(args.rar_bins, 4)
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    best_log_a0, _ = golden_section_minimize(
        lambda value: objective(all_rows, value),
        math.log10(args.fit_min_a0),
        math.log10(args.fit_max_a0),
    )
    a0_best = 10.0**best_log_a0
    scenarios = {
        "OPH_fixed_a0": a0_oph,
        "empirical_reference_a0": EMPIRICAL_RAR_A0,
        "best_fit_same_function": a0_best,
    }
    scenario_rows = []
    for name, a0 in scenarios.items():
        all_stats = all_data_stats(all_rows, a0)
        bin_stats = binned_stats(bin_rows, a0)
        scenario_rows.append(
            {
                "name": name,
                "a0_m_s2": a0,
                "a0_over_OPH": a0 / a0_oph,
                "all_data": all_stats,
                "binned_data": {
                    key: value
                    for key, value in bin_stats.items()
                    if key != "rows"
                },
            }
        )
    return {
        "status": {
            "category": "SPARC RAR measurement comparison",
            "model": "gobs = gbar / (1 - exp(-sqrt(gbar/a0)))",
            "log_space": True,
            "not_a_full_galaxy_rotation_curve_fit": True,
        },
        "sources": {
            "SPARC_page": "https://astroweb.cwru.edu/SPARC/",
            "RAR_all_data": "https://astroweb.cwru.edu/SPARC/RAR.mrt",
            "RAR_binned_data": "https://astroweb.cwru.edu/SPARC/RARbins.mrt",
            "RAR_paper": "https://arxiv.org/abs/1609.05917",
        },
        "inputs": {
            "rar_all_path": str(args.rar_all),
            "rar_bins_path": str(args.rar_bins),
            "N_scr": args.n_scr,
            "all_data_rows": len(all_rows),
            "binned_rows": len(bin_rows),
        },
        "scenarios": scenario_rows,
        "binned_residual_rows_OPH": binned_stats(bin_rows, a0_oph)["rows"],
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# SPARC RAR Comparison")
    print()
    print("Model: `gobs = gbar / (1 - exp(-sqrt(gbar/a0)))`.")
    print()
    print("| Scenario | a0 m/s^2 | a0/OPH | N | mean resid dex | RMS dex | chi2/pt | binned RMS dex |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["scenarios"]:
        all_stats = row["all_data"]
        bin_stats = row["binned_data"]
        print(
            f"| {row['name']} | {row['a0_m_s2']:.9e} | "
            f"{row['a0_over_OPH']:.6f} | {int(all_stats['N'])} | "
            f"{all_stats['mean_residual_dex_data_minus_model']:+.6f} | "
            f"{all_stats['rms_residual_dex']:.6f} | "
            f"{all_stats['chi2_per_point_no_intrinsic']:.6f} | "
            f"{bin_stats['rms_residual_dex_weighted_by_N']:.6f} |"
        )
    print()
    print("OPH binned residuals:")
    print()
    print("| log gbar | log gobs | log model | residual dex | N |")
    print("| ---: | ---: | ---: | ---: | ---: |")
    for row in payload["binned_residual_rows_OPH"]:
        print(
            f"| {row['log_gbar']:.2f} | {row['log_gobs']:.2f} | "
            f"{row['log_model']:.4f} | {row['residual_dex']:+.4f} | "
            f"{row['N']} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rar-all", type=Path, default=DEFAULT_RAR_ALL)
    parser.add_argument("--rar-bins", type=Path, default=DEFAULT_RAR_BINS)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--fit-min-a0", type=float, default=0.2e-10)
    parser.add_argument("--fit-max-a0", type=float, default=3.0e-10)
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
