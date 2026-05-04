#!/usr/bin/env python3
"""Compute the OPH Jacobi repair-clock diagnostic."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Any

from d6_capacity_calculator import G


M_SUN_KG = 1.988_47e30
KPC_M = 3.085_677_581_491_3673e19
SEC_PER_GYR = 365.25 * 24.0 * 3600.0 * 1.0e9


@dataclass(frozen=True)
class ClockScale:
    name: str
    mass_msun: float
    radius_kpc: float


DEFAULT_SCALES = [
    ClockScale("inner spiral disk", 6.0e10, 10.0),
    ClockScale("outer spiral disk", 6.0e10, 30.0),
    ClockScale("dwarf scale", 1.0e9, 5.0),
    ClockScale("cluster core", 1.0e14, 300.0),
    ClockScale("massive cluster aperture", 1.0e15, 1000.0),
]


def tau_j_gyr(mass_msun: float, radius_kpc: float) -> float:
    mass = mass_msun * M_SUN_KG
    radius = radius_kpc * KPC_M
    return math.sqrt(radius**3 / (G * mass)) / SEC_PER_GYR


def compute(args: argparse.Namespace) -> dict[str, Any]:
    rows = []
    for scale in DEFAULT_SCALES:
        tau = tau_j_gyr(scale.mass_msun, scale.radius_kpc)
        retained = math.exp(-args.time_since_passage_gyr / tau)
        rows.append(
            {
                "name": scale.name,
                "mass_Msun": scale.mass_msun,
                "radius_kpc": scale.radius_kpc,
                "tau_J_Gyr": tau,
                "orbital_period_Gyr": 2.0 * math.pi * tau,
                "retention_fraction": retained,
                "retained_offset_kpc": args.initial_offset_kpc * retained,
            }
        )
    return {
        "status": {
            "category": "Jacobi repair-clock diagnostic",
            "paper_grade": False,
            "named_premise": "repair timing is set by overlap-visible Jacobi mismatch",
            "notes": [
                "Gamma_J = (E_ij E^ij / 6)^(1/4).",
                "For a spherical point source, tau_J = sqrt(r^3 / GM).",
                "This is a no-fit dynamic clock candidate, not a cluster likelihood.",
            ],
        },
        "inputs": {
            "initial_offset_kpc": args.initial_offset_kpc,
            "time_since_passage_Gyr": args.time_since_passage_gyr,
        },
        "rows": rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    inputs = payload["inputs"]
    print("# OPH Jacobi Repair Clock")
    print()
    print(
        f"Offset diagnostic: `d0 = {inputs['initial_offset_kpc']:.6g} kpc`, "
        f"`t = {inputs['time_since_passage_Gyr']:.6g} Gyr`."
    )
    print()
    print("| Scale | M Msun | r kpc | tau_J Gyr | 2pi tau_J Gyr | retained offset kpc |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["rows"]:
        print(
            f"| {row['name']} | {row['mass_Msun']:.6g} | "
            f"{row['radius_kpc']:.6g} | {row['tau_J_Gyr']:.6g} | "
            f"{row['orbital_period_Gyr']:.6g} | {row['retained_offset_kpc']:.6g} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-offset-kpc", type=float, default=200.0)
    parser.add_argument("--time-since-passage-gyr", type=float, default=0.2)
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
