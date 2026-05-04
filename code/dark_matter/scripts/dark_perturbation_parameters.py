#!/usr/bin/env python3
"""Compute simple linear-perturbation parameters for the anomaly fluid."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any


def compute(
    omega_b: float,
    omega_cdm_like_anomaly: float,
    tau_rec_gyr: float,
    redshifts: list[float],
    h0_km_s_mpc: float,
    omega_lambda: float,
    omega_r: float,
) -> dict[str, Any]:
    omega_m = omega_b + omega_cdm_like_anomaly
    h0_gyr_inv = h0_km_s_mpc / 977.7922216807892
    gamma_rec = 1.0 / tau_rec_gyr
    rows = []
    for z in redshifts:
        a = 1.0 / (1.0 + z)
        hubble_gyr_inv = h0_gyr_inv * math.sqrt(
            omega_r * (1.0 + z) ** 4
            + omega_m * (1.0 + z) ** 3
            + omega_lambda
        )
        rows.append(
            {
                "z": z,
                "a": a,
                "Omega_A_over_Omega_m": omega_cdm_like_anomaly / omega_m,
                "mu_clustered_limit": 1.0,
                "gamma_no_slip": 1.0,
                "Gamma_rec_Gyr_inv": gamma_rec,
                "H_Gyr_inv": hubble_gyr_inv,
                "Gamma_over_H": gamma_rec / hubble_gyr_inv,
            }
        )
    return {
        "status": {
            "category": "linear perturbation bookkeeping, not a Boltzmann solver",
            "assumes_no_slip": True,
            "assumes_pressureless_anomaly": True,
        },
        "inputs": {
            "Omega_b": omega_b,
            "Omega_A": omega_cdm_like_anomaly,
            "Omega_m": omega_m,
            "Omega_Lambda": omega_lambda,
            "Omega_r": omega_r,
            "H0_km_s_Mpc": h0_km_s_mpc,
            "H0_Gyr_inv": h0_gyr_inv,
            "tau_rec_Gyr": tau_rec_gyr,
        },
        "equations": {
            "delta_A_prime": "-theta_A + 3 Phi_prime - a Gamma_rec q_A (delta_A - delta_A_eq)",
            "theta_A_prime": "-H theta_A + k^2 Psi",
            "slip": "Phi = Psi if sigma_A = 0",
            "poisson": "k^2 Phi = 4 pi G a^2 sum rho_i delta_i",
        },
        "rows": rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    inputs = payload["inputs"]
    print("# Dark Anomaly Perturbation Parameters")
    print()
    print(f"Omega_A/Omega_m: `{inputs['Omega_A'] / inputs['Omega_m']:.6g}`")
    print(f"Gamma_rec: `{1.0 / inputs['tau_rec_Gyr']:.6g} Gyr^-1`")
    print(f"H0: `{inputs['H0_Gyr_inv']:.6g} Gyr^-1`")
    print()
    print("| z | a | gamma | H Gyr^-1 | Gamma_rec Gyr^-1 | Gamma_rec/H |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["rows"]:
        print(
            f"| {row['z']:.6g} | {row['a']:.6g} | "
            f"{row['gamma_no_slip']:.6g} | {row['H_Gyr_inv']:.6g} | "
            f"{row['Gamma_rec_Gyr_inv']:.6g} | {row['Gamma_over_H']:.6g} |"
        )


def parse_csv_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--omega-b", type=float, default=0.049)
    parser.add_argument("--omega-anomaly", type=float, default=0.266)
    parser.add_argument("--omega-lambda", type=float, default=0.685)
    parser.add_argument("--omega-r", type=float, default=9.2e-5)
    parser.add_argument("--h0-km-s-mpc", type=float, default=67.4)
    parser.add_argument("--tau-rec-gyr", type=float, default=1.0)
    parser.add_argument("--redshifts", default="0,0.5,1,2,10,1100")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compute(
        omega_b=args.omega_b,
        omega_cdm_like_anomaly=args.omega_anomaly,
        tau_rec_gyr=args.tau_rec_gyr,
        redshifts=parse_csv_floats(args.redshifts),
        h0_km_s_mpc=args.h0_km_s_mpc,
        omega_lambda=args.omega_lambda,
        omega_r=args.omega_r,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
