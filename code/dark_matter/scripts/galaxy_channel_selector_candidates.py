#!/usr/bin/env python3
"""Evaluate OPH-native lambda_collar candidate ingredients.

This is a search diagnostic, not a fit.  It compares candidate activity
reserves that can be stated without using SPARC values as inputs.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from d6_capacity_calculator import compute as compute_d6
from sparc_rar_compare import (  # noqa: E402
    DEFAULT_RAR_ALL,
    DEFAULT_RAR_BINS,
    all_data_stats,
    binned_stats,
    parse_numeric_rows,
)
from sparc_rotation_curve_compare import (  # noqa: E402
    DEFAULT_MASS_MODELS,
    parse_mass_model_rows,
    scenario_stats,
)


P_PIXEL = 1.630968209403959
PHI = (1.0 + math.sqrt(5.0)) / 2.0
ALPHA_IN = (P_PIXEL - PHI) / math.sqrt(math.pi)
ELLBAR_SHARED = P_PIXEL / 4.0


@dataclass(frozen=True)
class Candidate:
    name: str
    reserve_fraction: float
    source: str
    status: str

    @property
    def lambda_collar(self) -> float:
        return 1.0 - self.reserve_fraction


def candidate_list() -> list[Candidate]:
    return [
        Candidate(
            "protected_record_reserve_1_over_15",
            1.0 / 15.0,
            "minimal S3 repair API priority vector if promoted to packing: 1/(2+2+1+10)",
            "best current theorem target; not yet theorem-grade",
        ),
        Candidate(
            "pixel_edge_entropy_over_z6",
            ELLBAR_SHARED / 6.0,
            "P/4 shared edge entropy distributed over six realized center labels",
            "finite-slot approximation or alternative model",
        ),
        Candidate(
            "pixel_edge_entropy_z6_poisson_thinning",
            1.0 - math.exp(-ELLBAR_SHARED / 6.0),
            "P/4 shared edge entropy over Z6 with Poisson zero-reserve thinning",
            "selected structural target under independent-increment reserve thinning",
        ),
        Candidate(
            "z6_angular_reserve",
            1.0 / (6.0 * math.pi),
            "one Z6 center-label reserve over a 2pi angular phase measure",
            "plausible but weaker geometric justification",
        ),
        Candidate(
            "one_reserve_per_24_slots",
            1.0 / 24.0,
            "integer slot diagnostic only",
            "matches all-data RAR pressure but slot count is not derived",
        ),
        Candidate(
            "one_reserve_per_16_slots",
            1.0 / 16.0,
            "integer slot diagnostic only",
            "near binned RAR pressure; no theorem target yet",
        ),
        Candidate(
            "z6_square_reserve",
            1.0 / 36.0,
            "uniform Z6 reserve squared",
            "too small for current SPARC pressure",
        ),
        Candidate(
            "pixel_detuning_reserve",
            ALPHA_IN,
            "outer/inner pixel detuning alpha_in",
            "too small for current SPARC pressure",
        ),
        Candidate(
            "sqrt_pixel_detuning_reserve",
            math.sqrt(ALPHA_IN),
            "square-root pixel detuning diagnostic",
            "overshoots and lacks repair-channel meaning",
        ),
    ]


def evaluate_candidate(
    candidate: Candidate,
    a0_oph: float,
    rar_rows: list[list[float]],
    bin_rows: list[list[float]],
    mass_rows: list[dict[str, Any]],
    upsilon_disk: float,
    upsilon_bulge: float,
) -> dict[str, Any]:
    lam = candidate.lambda_collar
    a0_eff = a0_oph / (lam * lam)
    all_stats = all_data_stats(rar_rows, a0_eff)
    bin_stats = binned_stats(bin_rows, a0_eff)
    rot_stats = scenario_stats(mass_rows, a0_eff, upsilon_disk, upsilon_bulge)
    return {
        "name": candidate.name,
        "reserve_fraction": candidate.reserve_fraction,
        "lambda_collar": lam,
        "C_response": 1.0 / (lam * lam),
        "a0_eff_m_s2": a0_eff,
        "a0_eff_over_OPH": a0_eff / a0_oph,
        "source": candidate.source,
        "status": candidate.status,
        "rar_all_rms_dex": all_stats["rms_residual_dex"],
        "rar_all_chi2_per_point": all_stats["chi2_per_point_no_intrinsic"],
        "rar_binned_weighted_rms_dex": bin_stats["rms_residual_dex_weighted_by_N"],
        "rotation_rms_km_s": rot_stats["rms_residual_km_s"],
        "rotation_chi2_per_point": rot_stats["chi2_per_point_statistical_velocity_only"],
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    rar_rows = parse_numeric_rows(args.rar_all, 4)
    bin_rows = parse_numeric_rows(args.rar_bins, 4)
    mass_rows = parse_mass_model_rows(args.mass_models)
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    rows = [
        evaluate_candidate(
            candidate,
            a0_oph,
            rar_rows,
            bin_rows,
            mass_rows,
            args.upsilon_disk,
            args.upsilon_bulge,
        )
        for candidate in candidate_list()
    ]
    rows.sort(key=lambda row: row["rar_all_chi2_per_point"])
    return {
        "status": {
            "category": "galaxy-channel selector candidate search",
            "claim": "diagnostic only",
            "warning": (
                "Candidates are OPH-native formulas that do not use SPARC as "
                "input, but none is theorem-grade until its reserve fraction is "
                "derived from collar microphysics."
            ),
        },
        "inputs": {
            "N_scr": args.n_scr,
            "a0_OPH_m_s2": a0_oph,
            "P_pixel": P_PIXEL,
            "phi": PHI,
            "alpha_in": ALPHA_IN,
            "ellbar_shared_P_over_4": ELLBAR_SHARED,
            "rar_rows": len(rar_rows),
            "rar_bin_rows": len(bin_rows),
            "mass_model_rows": len(mass_rows),
        },
        "candidates": rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# Galaxy-Channel Selector Candidate Search")
    print()
    print(payload["status"]["warning"])
    print()
    print(f"a0_OPH: `{payload['inputs']['a0_OPH_m_s2']:.9e} m/s^2`")
    print(f"P_pixel: `{payload['inputs']['P_pixel']:.15f}`")
    print(f"alpha_in: `{payload['inputs']['alpha_in']:.12f}`")
    print(f"ellbar_shared=P/4: `{payload['inputs']['ellbar_shared_P_over_4']:.12f}`")
    print()
    print(
        "| Candidate | reserve | lambda | C_response | a0_eff | "
        "RAR RMS dex | RAR chi2/pt | binned RMS | rot RMS km/s | rot chi2/pt |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["candidates"]:
        print(
            f"| {row['name']} | {row['reserve_fraction']:.6f} | "
            f"{row['lambda_collar']:.6f} | {row['C_response']:.6f} | "
            f"{row['a0_eff_m_s2']:.9e} | {row['rar_all_rms_dex']:.6f} | "
            f"{row['rar_all_chi2_per_point']:.6f} | "
            f"{row['rar_binned_weighted_rms_dex']:.6f} | "
            f"{row['rotation_rms_km_s']:.6f} | "
            f"{row['rotation_chi2_per_point']:.6f} |"
        )
    print()
    print(
        "Best theorem target by provenance, not by fit: "
        "`pixel_edge_entropy_z6_poisson_thinning`."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--rar-all", type=Path, default=DEFAULT_RAR_ALL)
    parser.add_argument("--rar-bins", type=Path, default=DEFAULT_RAR_BINS)
    parser.add_argument("--mass-models", type=Path, default=DEFAULT_MASS_MODELS)
    parser.add_argument("--upsilon-disk", type=float, default=0.5)
    parser.add_argument("--upsilon-bulge", type=float, default=0.7)
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
