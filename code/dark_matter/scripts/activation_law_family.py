#!/usr/bin/env python3
"""Explore OPH repair-channel activation laws.

The default OPH static candidate uses codimension-one repair channels:

    p(x) = 1 - exp(-x^alpha), alpha = 1/2.

This script shows why alpha=1/2 is special: it is the only power in this family
that gives a flat deep-IR rotation curve for a point baryonic mass.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any

from d6_capacity_calculator import G, compute as compute_d6


M_SUN_KG = 1.988_47e30
KPC_M = 3.085_677_581_491_3673e19


def activation(x: float, alpha: float) -> float:
    if x <= 0.0:
        return 0.0
    return 1.0 - math.exp(-(x**alpha))


def response(x: float, alpha: float) -> float:
    p = activation(x, alpha)
    return math.inf if p == 0.0 else 1.0 / p


def deep_ir_velocity_slope(alpha: float) -> float:
    # For a point mass, g_b ~ r^-2 and g = g_b / x^alpha.
    # Therefore g ~ r^(-2 + 2 alpha), v^2 = g r ~ r^(-1 + 2 alpha),
    # and v ~ r^(-1/2 + alpha).
    return -0.5 + alpha


def compute(
    n_scr: float,
    baryonic_mass_msun: float,
    radius_kpc: float,
    alphas: list[float],
) -> dict[str, Any]:
    a0 = compute_d6(n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    mass_kg = baryonic_mass_msun * M_SUN_KG
    radius_m = radius_kpc * KPC_M
    g_b = G * mass_kg / radius_m**2
    x = g_b / a0
    rows = []
    for alpha in alphas:
        nu = response(x, alpha)
        g_obs = nu * g_b
        rows.append(
            {
                "alpha": alpha,
                "activation": activation(x, alpha),
                "nu": nu,
                "v_c_km_s": math.sqrt(g_obs * radius_m) / 1000.0,
                "deep_ir_velocity_log_slope": deep_ir_velocity_slope(alpha),
                "gives_flat_deep_ir_rotation": abs(deep_ir_velocity_slope(alpha)) < 1e-12,
            }
        )
    return {
        "status": {
            "category": "activation-law family diagnostic",
            "alpha_half_is_codimension_one": True,
        },
        "inputs": {
            "N_scr": n_scr,
            "a0_OPH_m_s2": a0,
            "baryonic_mass_Msun": baryonic_mass_msun,
            "radius_kpc": radius_kpc,
            "g_b_over_a0": x,
        },
        "rows": rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    inputs = payload["inputs"]
    print("# OPH Activation-Law Family")
    print()
    print(f"g_b/a0 at diagnostic radius: `{inputs['g_b_over_a0']:.6g}`")
    print()
    print("| alpha | p(x) | nu | v_c km/s | deep-IR dlnv/dlnr | flat? |")
    print("| ---: | ---: | ---: | ---: | ---: | --- |")
    for row in payload["rows"]:
        print(
            f"| {row['alpha']:.6g} | {row['activation']:.6g} | "
            f"{row['nu']:.6g} | {row['v_c_km_s']:.6g} | "
            f"{row['deep_ir_velocity_log_slope']:.6g} | "
            f"{row['gives_flat_deep_ir_rotation']} |"
        )


def parse_csv_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--baryonic-mass-msun", type=float, default=6.0e10)
    parser.add_argument("--radius-kpc", type=float, default=50.0)
    parser.add_argument("--alphas", default="0.25,0.3333333333,0.5,0.6666666667,1.0")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compute(
        n_scr=args.n_scr,
        baryonic_mass_msun=args.baryonic_mass_msun,
        radius_kpc=args.radius_kpc,
        alphas=parse_csv_floats(args.alphas),
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
