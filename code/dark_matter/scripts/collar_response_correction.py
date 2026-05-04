#!/usr/bin/env python3
"""Finite-collar response-correction bookkeeping for the OPH dark branch."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Any

from d6_capacity_calculator import compute as compute_d6


@dataclass(frozen=True)
class Target:
    name: str
    a0_target_m_s2: float
    source: str


DEFAULT_TARGETS = (
    Target(
        "SPARC all-data weighted chi2",
        1.119530397e-10,
        "sparc_audit_sensitivity.py",
    ),
    Target(
        "SPARC all-data unweighted RMS",
        1.162058177e-10,
        "sparc_audit_sensitivity.py",
    ),
    Target(
        "SPARC binned weighted RMS",
        1.172891285e-10,
        "sparc_audit_sensitivity.py",
    ),
    Target(
        "SPARC fixed-M/L rotation chi2",
        1.198555482e-10,
        "sparc_audit_sensitivity.py",
    ),
)


def analyze_target(target: Target, a0_oph: float) -> dict[str, Any]:
    response_factor = target.a0_target_m_s2 / a0_oph
    lambda_collar = math.sqrt(a0_oph / target.a0_target_m_s2)
    tau_cut = -2.0 * math.log(lambda_collar)
    return {
        "name": target.name,
        "source": target.source,
        "a0_target_m_s2": target.a0_target_m_s2,
        "a0_target_over_OPH": response_factor,
        "lambda_collar_if_OPH_a0_fixed": lambda_collar,
        "C_response": response_factor,
        "tau_cut_if_lambda_exp_minus_tau_over_2": tau_cut,
        "edge_t_if_tau_cut_equals_3t": tau_cut / 3.0,
        "N_scr_factor_if_wrongly_tuned": (a0_oph / target.a0_target_m_s2) ** 2,
        "Lambda_factor_if_wrongly_tuned": response_factor**2,
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    targets = list(DEFAULT_TARGETS)
    for index, value in enumerate(args.target_a0, start=1):
        targets.append(Target(f"user target {index}", value, "command line"))

    rows = [analyze_target(target, a0_oph) for target in targets]
    return {
        "status": {
            "category": "finite-collar response correction",
            "claim": "bookkeeping only",
            "warning": (
                "lambda_collar and C_response are not fitted OPH predictions here. "
                "They are the microphysical correction values a future collar theorem "
                "would have to derive independently."
            ),
        },
        "inputs": {
            "N_scr": args.n_scr,
            "a0_OPH_m_s2": a0_oph,
            "lambda_model": "a0_eff = a0_OPH / lambda_collar^2",
            "tau_model": "lambda_collar = exp(-tau_cut/2)",
            "edge_t_diagnostic": "if tau_cut is identified with the S3 standard-irrep eigenvalue 3 times t, then t = tau_cut/3",
        },
        "targets": rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# Collar Response Correction")
    print()
    print(payload["status"]["warning"])
    print()
    print(f"a0_OPH: `{payload['inputs']['a0_OPH_m_s2']:.9e} m/s^2`")
    print()
    print(
        "| Target | a0_target m/s^2 | C_response | lambda_collar | "
        "tau_cut | edge t if tau=3t | forbidden N_scr factor |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["targets"]:
        print(
            f"| {row['name']} | {row['a0_target_m_s2']:.9e} | "
            f"{row['C_response']:.6f} | "
            f"{row['lambda_collar_if_OPH_a0_fixed']:.6f} | "
            f"{row['tau_cut_if_lambda_exp_minus_tau_over_2']:.6f} | "
            f"{row['edge_t_if_tau_cut_equals_3t']:.6f} | "
            f"{row['N_scr_factor_if_wrongly_tuned']:.6f} |"
        )
    print()
    print(
        "The final column is shown only to make the no-cheating rule explicit: "
        "changing `N_scr` to fit galaxies would move the independent D6 "
        "capacity/Lambda branch."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument(
        "--target-a0",
        action="append",
        type=float,
        default=[],
        help="Additional target acceleration scale in m/s^2.",
    )
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
