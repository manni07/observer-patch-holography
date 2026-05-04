#!/usr/bin/env python3
"""Audit SPARC comparison sensitivity and possible non-cheating improvements."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any, Callable

from d6_capacity_calculator import compute as compute_d6
from sparc_rar_compare import (
    DEFAULT_RAR_ALL,
    DEFAULT_RAR_BINS,
    all_data_stats,
    binned_stats,
    golden_section_minimize,
    log_model,
    parse_numeric_rows,
)
from sparc_rotation_curve_compare import (
    DEFAULT_MASS_MODELS,
    parse_mass_model_rows,
    scenario_stats,
)


def fit_a0_for_scalar(
    fn: Callable[[float], float],
    fit_min_a0: float,
    fit_max_a0: float,
) -> tuple[float, float]:
    best_log, best_value = golden_section_minimize(
        lambda log_value: fn(10.0**log_value),
        math.log10(fit_min_a0),
        math.log10(fit_max_a0),
    )
    return 10.0**best_log, best_value


def binned_weighted_rms(rows: list[list[float]], a0: float) -> float:
    return binned_stats(rows, a0)["rms_residual_dex_weighted_by_N"]


def all_rms(rows: list[list[float]], a0: float) -> float:
    return all_data_stats(rows, a0)["rms_residual_dex"]


def all_chi2(rows: list[list[float]], a0: float) -> float:
    return all_data_stats(rows, a0)["chi2_no_intrinsic"]


def rotation_chi2(rows: list[dict[str, Any]], a0: float, upsilon_disk: float, upsilon_bulge: float) -> float:
    return scenario_stats(rows, a0, upsilon_disk, upsilon_bulge)[
        "chi2_statistical_velocity_only"
    ]


def generalized_log_model(log_gbar: float, a0: float, alpha: float) -> float:
    gbar = 10.0**log_gbar
    x = gbar / a0
    p = 1.0 - math.exp(-(x**alpha))
    return math.log10(gbar / p)


def generalized_chi2(rows: list[list[float]], a0: float, alpha: float) -> float:
    terms = []
    for log_gbar, e_gbar, log_gobs, e_gobs in rows:
        pred = generalized_log_model(log_gbar, a0, alpha)
        h = 1.0e-4
        slope = (
            generalized_log_model(log_gbar + h, a0, alpha)
            - generalized_log_model(log_gbar - h, a0, alpha)
        ) / (2.0 * h)
        sigma = math.sqrt(e_gobs**2 + (slope * e_gbar) ** 2)
        terms.append(((log_gobs - pred) / sigma) ** 2)
    return sum(terms)


def compute(args: argparse.Namespace) -> dict[str, Any]:
    rar_rows = parse_numeric_rows(args.rar_all, 4)
    bin_rows = parse_numeric_rows(args.rar_bins, 4)
    mass_rows = parse_mass_model_rows(args.mass_models)
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]

    fits = {}
    for name, fn in {
        "all_data_weighted_chi2": lambda a0: all_chi2(rar_rows, a0),
        "all_data_unweighted_rms": lambda a0: all_rms(rar_rows, a0),
        "binned_weighted_rms": lambda a0: binned_weighted_rms(bin_rows, a0),
        "rotation_fixed_ML_chi2": lambda a0: rotation_chi2(
            mass_rows, a0, args.upsilon_disk, args.upsilon_bulge
        ),
    }.items():
        a0_fit, metric_value = fit_a0_for_scalar(fn, args.fit_min_a0, args.fit_max_a0)
        fits[name] = {
            "a0_fit_m_s2": a0_fit,
            "a0_fit_over_OPH": a0_fit / a0_oph,
            "metric_value": metric_value,
            "lambda_channel_efficiency_if_OPH_a0_fixed": math.sqrt(a0_oph / a0_fit),
            "N_scr_factor_needed_if_only_capacity_changes": (a0_oph / a0_fit) ** 2,
            "Lambda_factor_needed_if_only_capacity_changes": (a0_fit / a0_oph) ** 2,
            "anomaly_prefactor_factor_needed": a0_fit / a0_oph,
        }

    best_alpha_log, best_alpha_metric = golden_section_minimize(
        lambda alpha: generalized_chi2(rar_rows, a0_oph, alpha),
        args.alpha_min,
        args.alpha_max,
    )
    alpha_half_metric = generalized_chi2(rar_rows, a0_oph, 0.5)

    return {
        "status": {
            "category": "SPARC audit and sensitivity",
            "main_cheating_risk": "The OPH static law uses the same functional form as the published empirical RAR interpolation; current data comparison mostly tests normalization.",
        },
        "inputs": {
            "N_scr": args.n_scr,
            "a0_OPH_m_s2": a0_oph,
            "rar_rows": len(rar_rows),
            "rar_bin_rows": len(bin_rows),
            "mass_model_rows": len(mass_rows),
            "upsilon_disk": args.upsilon_disk,
            "upsilon_bulge": args.upsilon_bulge,
        },
        "fits": fits,
        "activation_alpha_check_fixed_OPH_a0": {
            "best_alpha_for_all_data_chi2": best_alpha_log,
            "best_alpha_chi2": best_alpha_metric,
            "alpha_half_chi2": alpha_half_metric,
            "alpha_half_required_for_flat_deep_IR_rotation": True,
            "warning": "Moving alpha away from 1/2 may improve finite-range fit but changes the deep-IR BTFR slope unless compensated by another derived mechanism.",
        },
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# SPARC Audit Sensitivity")
    print()
    print(payload["status"]["main_cheating_risk"])
    print()
    print(f"a0_OPH: `{payload['inputs']['a0_OPH_m_s2']:.9e} m/s^2`")
    print()
    print("| Fit target | a0_fit m/s^2 | fit/OPH | lambda if OPH a0 fixed | N_scr factor | prefactor factor |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name, row in payload["fits"].items():
        print(
            f"| {name} | {row['a0_fit_m_s2']:.9e} | "
            f"{row['a0_fit_over_OPH']:.6f} | "
            f"{row['lambda_channel_efficiency_if_OPH_a0_fixed']:.6f} | "
            f"{row['N_scr_factor_needed_if_only_capacity_changes']:.6f} | "
            f"{row['anomaly_prefactor_factor_needed']:.6f} |"
        )
    alpha = payload["activation_alpha_check_fixed_OPH_a0"]
    print()
    print(
        "Generalized activation `p=1-exp(-x^alpha)` with fixed OPH a0: "
        f"best alpha `{alpha['best_alpha_for_all_data_chi2']:.6f}`, "
        f"while flat deep-IR rotation requires `alpha = 0.5`."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rar-all", default=DEFAULT_RAR_ALL)
    parser.add_argument("--rar-bins", default=DEFAULT_RAR_BINS)
    parser.add_argument("--mass-models", default=DEFAULT_MASS_MODELS)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--upsilon-disk", type=float, default=0.5)
    parser.add_argument("--upsilon-bulge", type=float, default=0.7)
    parser.add_argument("--fit-min-a0", type=float, default=0.2e-10)
    parser.add_argument("--fit-max-a0", type=float, default=3.0e-10)
    parser.add_argument("--alpha-min", type=float, default=0.25)
    parser.add_argument("--alpha-max", type=float, default=0.8)
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
