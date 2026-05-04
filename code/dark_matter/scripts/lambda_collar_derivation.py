#!/usr/bin/env python3
"""Report the OPH lambda_collar unit branch and normalization audit."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any

from collar_response_correction import DEFAULT_TARGETS
from d6_capacity_calculator import compute as compute_d6


UNIT_BRANCH_LAMBDA_COLLAR = 1.0
UNIT_BRANCH_TAU_CUT = 0.0


def compute(args: argparse.Namespace) -> dict[str, Any]:
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    rows = []
    for target in DEFAULT_TARGETS:
        target_lambda = math.sqrt(a0_oph / target.a0_target_m_s2)
        rows.append(
            {
                "name": target.name,
                "source": target.source,
                "target_lambda_if_backsolved": target_lambda,
                "target_C_response": target.a0_target_m_s2 / a0_oph,
                "unit_branch_minus_target_lambda": UNIT_BRANCH_LAMBDA_COLLAR
                - target_lambda,
                "target_tau_cut_if_lambda_exp_minus_tau_over_2": -2.0
                * math.log(target_lambda),
            }
        )

    return {
        "status": {
            "category": "lambda_collar derivation",
            "claim": "OPH collar microphysics fixes the sqrt exponent; lambda_collar=1 is the unit-efficiency branch, not a theorem-grade normalization",
            "unit_branch_lambda_collar": UNIT_BRANCH_LAMBDA_COLLAR,
            "warning": (
                "A nonunity lambda_collar requires an additional finite-thickness "
                "or sector-activity theorem. The previous mu(r_M)=1 step is a "
                "normalization convention unless that theorem is supplied."
            ),
        },
        "inputs": {
            "N_scr": args.n_scr,
            "a0_OPH_m_s2": a0_oph,
        },
        "derived_values": {
            "sqrt_exponent_from_codimension_one_support": True,
        },
        "unit_branch_values": {
            "lambda_collar": UNIT_BRANCH_LAMBDA_COLLAR,
            "C_response": 1.0 / UNIT_BRANCH_LAMBDA_COLLAR**2,
            "tau_cut_if_lambda_exp_minus_tau_over_2": UNIT_BRANCH_TAU_CUT,
            "a0_eff_m_s2": a0_oph / UNIT_BRANCH_LAMBDA_COLLAR**2,
        },
        "measurement_pressure_not_used_in_derivation": rows,
        "rejected_shortcuts": [
            "repair diagnostic weights are operational costs, not physical channel-density constants",
            "heat-kernel t is branch or benchmark data unless a galaxy collar thickness theorem fixes it",
            "N_scr belongs to the D6 capacity/Lambda branch and cannot be tuned to galaxies",
            "SPARC backsolving is a diagnostic, not a derivation",
        ],
    }


def print_markdown(payload: dict[str, Any]) -> None:
    status = payload["status"]
    derived = payload["unit_branch_values"]
    print("# Lambda Collar Derivation")
    print()
    print(status["claim"] + ".")
    print(status["warning"])
    print()
    print(f"a0_OPH: `{payload['inputs']['a0_OPH_m_s2']:.9e} m/s^2`")
    print(f"unit-branch lambda_collar: `{derived['lambda_collar']:.6f}`")
    print(f"unit-branch C_response: `{derived['C_response']:.6f}`")
    print(f"unit-branch tau_cut: `{derived['tau_cut_if_lambda_exp_minus_tau_over_2']:.6f}`")
    print()
    print("| Diagnostic target | backsolved lambda | C_response | unit-target lambda | tau_cut |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in payload["measurement_pressure_not_used_in_derivation"]:
        print(
            f"| {row['name']} | "
            f"{row['target_lambda_if_backsolved']:.6f} | "
            f"{row['target_C_response']:.6f} | "
            f"{row['unit_branch_minus_target_lambda']:.6f} | "
            f"{row['target_tau_cut_if_lambda_exp_minus_tau_over_2']:.6f} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
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
