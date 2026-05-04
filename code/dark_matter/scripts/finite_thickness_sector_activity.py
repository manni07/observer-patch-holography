#!/usr/bin/env python3
"""Explore S3 finite-thickness sector-activity requirements.

This is a theorem diagnostic, not a fit. It asks what heat-kernel
parameter t would be required for simple activity masks to reproduce the
SPARC-backsolved lambda_collar values.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Any

from collar_response_correction import DEFAULT_TARGETS
from d6_capacity_calculator import compute as compute_d6


@dataclass(frozen=True)
class ActivityMode:
    name: str
    a_trivial: float
    a_sign: float
    a_standard: float
    interpretation: str


ACTIVITY_MODES = (
    ActivityMode("all_active", 1.0, 1.0, 1.0, "all S3 edge sectors carry the repair channel"),
    ActivityMode("sign_inactive", 1.0, 0.0, 1.0, "sign irrep is inactive"),
    ActivityMode("standard_inactive", 1.0, 1.0, 0.0, "standard irrep is inactive"),
    ActivityMode("nontrivial_inactive", 1.0, 0.0, 0.0, "only the trivial sector is active"),
)


def s3_sector_probabilities(t_value: float) -> dict[str, float]:
    sign = math.exp(-6.0 * t_value)
    standard_weight = 2.0 * math.exp(-3.0 * t_value)
    partition = 1.0 + sign + standard_weight
    return {
        "trivial": 1.0 / partition,
        "sign": sign / partition,
        "standard": standard_weight / partition,
    }


def lambda_for_mode(t_value: float, mode: ActivityMode, chi_pack: float) -> float:
    p = s3_sector_probabilities(t_value)
    return chi_pack * (
        mode.a_trivial * p["trivial"]
        + mode.a_sign * p["sign"]
        + mode.a_standard * p["standard"]
    )


def solve_t_for_lambda(
    target_lambda: float,
    mode: ActivityMode,
    chi_pack: float,
    t_min: float,
    t_max: float,
) -> dict[str, Any]:
    low_value = lambda_for_mode(t_min, mode, chi_pack)
    high_value = lambda_for_mode(t_max, mode, chi_pack)
    lo = min(low_value, high_value)
    hi = max(low_value, high_value)
    if not (lo <= target_lambda <= hi):
        return {
            "solvable": False,
            "lambda_at_t_min": low_value,
            "lambda_at_t_max": high_value,
            "reason": "target outside this activity mode range",
        }

    left = t_min
    right = t_max
    increasing = high_value >= low_value
    for _ in range(100):
        mid = 0.5 * (left + right)
        value = lambda_for_mode(mid, mode, chi_pack)
        if (value < target_lambda) == increasing:
            left = mid
        else:
            right = mid
    t_value = 0.5 * (left + right)
    return {
        "solvable": True,
        "t": t_value,
        "lambda": lambda_for_mode(t_value, mode, chi_pack),
        "sector_probabilities": s3_sector_probabilities(t_value),
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    targets = []
    for target in DEFAULT_TARGETS:
        target_lambda = math.sqrt(a0_oph / target.a0_target_m_s2)
        modes = {
            mode.name: {
                "activity": {
                    "trivial": mode.a_trivial,
                    "sign": mode.a_sign,
                    "standard": mode.a_standard,
                },
                "interpretation": mode.interpretation,
                "solution": solve_t_for_lambda(
                    target_lambda,
                    mode,
                    args.chi_pack,
                    args.t_min,
                    args.t_max,
                ),
            }
            for mode in ACTIVITY_MODES
        }
        targets.append(
            {
                "name": target.name,
                "target_lambda": target_lambda,
                "inactive_fraction_if_chi_pack_1": 1.0 - target_lambda,
                "modes": modes,
            }
        )

    return {
        "status": {
            "category": "finite-thickness sector-activity diagnostic",
            "claim": "theorem diagnostic",
            "warning": (
                "The broad connected repair theorem gives all sectors active, "
                "so lambda_collar = chi_pack. Nonunit values require a narrower "
                "galaxy-channel selector or packing/thickness law."
            ),
        },
        "inputs": {
            "N_scr": args.n_scr,
            "a0_OPH_m_s2": a0_oph,
            "chi_pack": args.chi_pack,
            "t_min": args.t_min,
            "t_max": args.t_max,
            "s3_weights": "1 : exp(-6t) : 2 exp(-3t)",
        },
        "targets": targets,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# Finite-Thickness Sector Activity")
    print()
    print(payload["status"]["warning"])
    print()
    print("| Target | lambda | inactive frac | sign inactive t | standard inactive t | trivial-only t |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for target in payload["targets"]:
        def fmt(mode_name: str) -> str:
            solution = target["modes"][mode_name]["solution"]
            if not solution["solvable"]:
                return "n/a"
            return f"{solution['t']:.6f}"

        print(
            f"| {target['name']} | {target['target_lambda']:.6f} | "
            f"{target['inactive_fraction_if_chi_pack_1']:.6f} | "
            f"{fmt('sign_inactive')} | "
            f"{fmt('standard_inactive')} | "
            f"{fmt('nontrivial_inactive')} |"
        )
    print()
    print("`all_active` is the broad connected repair theorem. It gives lambda_collar = chi_pack, so it cannot explain a nonunit value when chi_pack = 1.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--chi-pack", type=float, default=1.0)
    parser.add_argument("--t-min", type=float, default=0.0)
    parser.add_argument("--t-max", type=float, default=10.0)
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
