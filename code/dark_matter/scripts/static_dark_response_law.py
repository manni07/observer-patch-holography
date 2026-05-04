#!/usr/bin/env python3
"""Evaluate the static OPH dark-response law candidate.

This script implements the weak-field law derived in
`dark_response_static_derivation.md`. It is a D12 continuation diagnostic, not a
theorem-grade dark-matter solver.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any

from d6_capacity_calculator import G, compute as compute_d6


KPC_M = 3.085_677_581_491_3673e19
M_SUN_KG = 1.988_47e30
DEFAULT_RADII_KPC = [
    0.5,
    1.0,
    2.0,
    5.0,
    10.0,
    20.0,
    50.0,
    100.0,
]


def activation_fraction(x: float) -> float:
    if x <= 0.0:
        return 0.0
    return 1.0 - math.exp(-math.sqrt(x))


def nu_oph(x: float) -> float:
    p = activation_fraction(x)
    if p == 0.0:
        return math.inf
    return 1.0 / p


def response_from_gb(g_b: float, a0: float) -> dict[str, float]:
    x = g_b / a0 if a0 > 0.0 else math.inf
    nu = nu_oph(x)
    g_obs = nu * g_b
    return {
        "x_gb_over_a0": x,
        "activation_fraction": activation_fraction(x),
        "nu": nu,
        "g_b_m_s2": g_b,
        "g_obs_m_s2": g_obs,
        "g_anom_m_s2": g_obs - g_b,
        "g_obs_over_g_b": nu,
    }


def enclosed_point_mass_response(
    baryonic_mass_msun: float,
    radii_kpc: list[float],
    a0: float,
) -> list[dict[str, float]]:
    mass_kg = baryonic_mass_msun * M_SUN_KG
    rows = []
    for radius_kpc in radii_kpc:
        radius_m = radius_kpc * KPC_M
        g_b = G * mass_kg / radius_m**2
        response = response_from_gb(g_b, a0)
        g_obs = response["g_obs_m_s2"]
        m_dyn_kg = g_obs * radius_m**2 / G
        m_anom_kg = max(0.0, m_dyn_kg - mass_kg)
        v_c_m_s = math.sqrt(g_obs * radius_m)
        row = {
            "radius_kpc": radius_kpc,
            "v_c_km_s": v_c_m_s / 1000.0,
            "M_dyn_Msun": m_dyn_kg / M_SUN_KG,
            "M_anom_Msun": m_anom_kg / M_SUN_KG,
            "M_lens_static_no_slip_Msun": m_dyn_kg / M_SUN_KG,
        }
        row.update(response)
        rows.append(row)
    return rows


def density_from_mass_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    density_rows = []
    for index in range(1, len(rows) - 1):
        left = rows[index - 1]
        right = rows[index + 1]
        radius_m = rows[index]["radius_kpc"] * KPC_M
        dmass_kg = (
            right["M_anom_Msun"] - left["M_anom_Msun"]
        ) * M_SUN_KG
        dr_m = (right["radius_kpc"] - left["radius_kpc"]) * KPC_M
        rho = dmass_kg / (4.0 * math.pi * radius_m**2 * dr_m)
        density_rows.append(
            {
                "radius_kpc": rows[index]["radius_kpc"],
                "rho_anom_kg_m3_numeric": rho,
                "rho_anom_Msun_kpc3_numeric": rho / M_SUN_KG * KPC_M**3,
            }
        )
    return density_rows


def compute(
    n_scr: float,
    baryonic_mass_msun: float,
    radii_kpc: list[float],
) -> dict[str, Any]:
    d6 = compute_d6(n_scr)
    a0 = d6["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    rows = enclosed_point_mass_response(baryonic_mass_msun, radii_kpc, a0)
    return {
        "status": {
            "category": "D12 static response-law candidate",
            "activation_law_proven_from_OPH_core": False,
            "metric_slip": "Phi = Psi in minimal static no-slip completion",
        },
        "inputs": {
            "N_scr": n_scr,
            "baryonic_mass_Msun": baryonic_mass_msun,
            "radii_kpc": radii_kpc,
        },
        "law": {
            "a0_OPH_m_s2": a0,
            "x": "g_b / a0_OPH",
            "activation_fraction": "p(x) = 1 - exp(-sqrt(x))",
            "nu": "nu(x) = 1 / p(x)",
            "g_obs": "g_obs = nu(g_b/a0_OPH) g_b",
            "rho_anom": "rho_anom = -(1/(4 pi G)) div[(nu - 1) g_b]",
        },
        "point_mass_rows": rows,
        "numeric_anom_density_rows": density_from_mass_rows(rows),
    }


def print_markdown(payload: dict[str, Any]) -> None:
    law = payload["law"]
    inputs = payload["inputs"]
    print("# Static OPH Dark Response Law Candidate")
    print()
    print("Status: D12 static weak-field law; activation law not yet core-proved.")
    print()
    print(f"a0_OPH: `{law['a0_OPH_m_s2']:.9e} m/s^2`")
    print(f"baryonic point mass: `{inputs['baryonic_mass_Msun']:.6e} Msun`")
    print()
    print("| r kpc | g_b/a0 | nu | g_obs/g_b | v_c km/s | M_dyn Msun | M_anom Msun |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["point_mass_rows"]:
        print(
            f"| {row['radius_kpc']:.3g} | "
            f"{row['x_gb_over_a0']:.6g} | "
            f"{row['nu']:.6g} | "
            f"{row['g_obs_over_g_b']:.6g} | "
            f"{row['v_c_km_s']:.6g} | "
            f"{row['M_dyn_Msun']:.6e} | "
            f"{row['M_anom_Msun']:.6e} |"
        )
    print()
    print("No-slip static completion: `M_lens = M_dyn` for the spherical table.")


def parse_csv_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--baryonic-mass-msun", type=float, default=6.0e10)
    parser.add_argument(
        "--radii-kpc",
        default=",".join(str(value) for value in DEFAULT_RADII_KPC),
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compute(
        n_scr=args.n_scr,
        baryonic_mass_msun=args.baryonic_mass_msun,
        radii_kpc=parse_csv_floats(args.radii_kpc),
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
