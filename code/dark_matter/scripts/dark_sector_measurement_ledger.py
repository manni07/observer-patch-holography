#!/usr/bin/env python3
"""Aggregate OPH dark-sector measurement diagnostics into one table."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sparc_profiled_ml_likelihood  # noqa: E402
import sparc_rar_compare  # noqa: E402
import sparc_rotation_curve_compare  # noqa: E402
import sparc_systematic_likelihood  # noqa: E402
import z6_shared_edge_reserve  # noqa: E402
from d6_capacity_calculator import compute as compute_d6  # noqa: E402


def percent_delta(value: float, reference: float) -> float:
    return 100.0 * (value / reference - 1.0)


def row_by_name(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for row in payload["scenarios"]:
        if row["name"] == name:
            return row
    raise KeyError(name)


def compute(args: argparse.Namespace) -> dict[str, Any]:
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]
    empirical_a0 = sparc_rar_compare.EMPIRICAL_RAR_A0

    common = {
        "n_scr": args.n_scr,
        "rar_all": args.rar_all,
        "rar_bins": args.rar_bins,
        "mass_models": args.mass_models,
    }
    rar_payload = sparc_rar_compare.compute(
        argparse.Namespace(
            **common,
            fit_min_a0=args.fit_min_a0,
            fit_max_a0=args.fit_max_a0,
        )
    )
    fixed_payload = sparc_rotation_curve_compare.compute(
        argparse.Namespace(
            **common,
            upsilon_disk=args.upsilon_disk,
            upsilon_bulge=args.upsilon_bulge,
            fit_min_a0=args.fit_min_a0,
            fit_max_a0=args.fit_max_a0,
            worst_count=0,
        )
    )
    profiled_payload = sparc_profiled_ml_likelihood.compute(
        argparse.Namespace(
            mass_models=args.mass_models,
            n_scr=args.n_scr,
            disk_prior=args.disk_prior,
            bulge_prior=args.bulge_prior,
            ml_prior_sigma_dex=args.ml_prior_sigma_dex,
            intrinsic_scatter_km_s=args.intrinsic_scatter_km_s,
            disk_min=args.disk_min,
            disk_max=args.disk_max,
            bulge_min=args.bulge_min,
            bulge_max=args.bulge_max,
            coordinate_iterations=args.coordinate_iterations,
        )
    )
    systematic_payload = sparc_systematic_likelihood.compute(
        argparse.Namespace(
            mass_models=args.mass_models,
            galaxy_sample=args.galaxy_sample,
            n_scr=args.n_scr,
            max_quality=args.max_quality,
            min_inclination_deg=args.min_inclination_deg,
            disk_prior=args.disk_prior,
            bulge_prior=args.bulge_prior,
            ml_prior_sigma_dex=args.ml_prior_sigma_dex,
            intrinsic_scatter_km_s=args.intrinsic_scatter_km_s,
            disk_min=args.disk_min,
            disk_max=args.disk_max,
            bulge_min=args.bulge_min,
            bulge_max=args.bulge_max,
            profile_distance=args.profile_distance,
            distance_min_mpc=args.distance_min_mpc,
            distance_sigma_window=args.distance_sigma_window,
            profile_inclination=args.profile_inclination,
            inclination_min_deg=args.inclination_min_deg,
            inclination_max_deg=args.inclination_max_deg,
            inclination_sigma_window=args.inclination_sigma_window,
            profile_gas=args.profile_gas,
            gas_prior_sigma_dex=args.gas_prior_sigma_dex,
            gas_min=args.gas_min,
            gas_max=args.gas_max,
            coordinate_iterations=args.coordinate_iterations,
        )
    )
    z6_payload = z6_shared_edge_reserve.compute(
        argparse.Namespace(
            **common,
            upsilon_disk=args.upsilon_disk,
            upsilon_bulge=args.upsilon_bulge,
        )
    )

    best_rar = row_by_name(rar_payload, "best_fit_same_function")
    unit_rar = row_by_name(rar_payload, "OPH_fixed_a0")
    empirical_rar = row_by_name(rar_payload, "empirical_reference_a0")
    fixed_unit = row_by_name(fixed_payload, "OPH_fixed_a0")
    fixed_empirical = row_by_name(fixed_payload, "empirical_reference_a0")
    fixed_best = row_by_name(fixed_payload, "best_fit_fixed_ML_same_function")
    profiled_unit = row_by_name(profiled_payload, "OPH_unit_branch")
    profiled_z6 = row_by_name(profiled_payload, "OPH_Z6_poisson")
    profiled_empirical = row_by_name(profiled_payload, "empirical_reference")
    systematic_unit = row_by_name(systematic_payload, "OPH_unit_branch")
    systematic_z6 = row_by_name(systematic_payload, "OPH_Z6_poisson")
    systematic_empirical = row_by_name(systematic_payload, "empirical_reference")
    z6_poisson = row_by_name(z6_payload, "z6_poisson_reserve_thinning")

    return {
        "inputs": {
            "a0_OPH_m_s2": a0_oph,
            "a0_empirical_reference_m_s2": empirical_a0,
            "a0_best_RAR_same_function_m_s2": best_rar["a0_m_s2"],
            "lambda_Z6_poisson": z6_poisson["lambda_collar"],
            "a0_Z6_poisson_m_s2": z6_poisson["a0_eff_m_s2"],
            "rar_points": int(rar_payload["inputs"]["all_data_rows"]),
            "rar_bins": int(rar_payload["inputs"]["binned_rows"]),
            "rotation_points": fixed_unit["stats"]["point_count"],
            "rotation_galaxies": fixed_unit["stats"]["galaxy_count"],
        },
        "scale_comparison": {
            "OPH_vs_best_RAR_percent": percent_delta(
                a0_oph, best_rar["a0_m_s2"]
            ),
            "OPH_vs_empirical_percent": percent_delta(a0_oph, empirical_a0),
            "Z6_vs_empirical_percent": percent_delta(
                z6_poisson["a0_eff_m_s2"], empirical_a0
            ),
            "Z6_vs_best_RAR_percent": percent_delta(
                z6_poisson["a0_eff_m_s2"], best_rar["a0_m_s2"]
            ),
        },
        "rar": {
            "unit": unit_rar,
            "z6_poisson": z6_poisson,
            "empirical": empirical_rar,
            "best": best_rar,
        },
        "fixed_ml_rotation": {
            "unit": fixed_unit,
            "z6_poisson": z6_poisson,
            "empirical": fixed_empirical,
            "best": fixed_best,
        },
        "profiled_ml": {
            "unit": profiled_unit,
            "z6_poisson": profiled_z6,
            "empirical": profiled_empirical,
        },
        "systematic_likelihood": {
            "unit": systematic_unit,
            "z6_poisson": systematic_z6,
            "empirical": systematic_empirical,
            "inputs": systematic_payload["inputs"],
        },
    }


def print_markdown(payload: dict[str, Any]) -> None:
    inputs = payload["inputs"]
    scales = payload["scale_comparison"]
    print("# Dark-Sector Measurement Ledger")
    print()
    print("| Quantity | Value | Measurement comparison |")
    print("| --- | ---: | --- |")
    print(
        f"| `a0_OPH` | `{inputs['a0_OPH_m_s2']:.9e}` | "
        f"{scales['OPH_vs_best_RAR_percent']:+.3f}% vs best same-function RAR; "
        f"{scales['OPH_vs_empirical_percent']:+.3f}% vs empirical reference |"
    )
    print(
        f"| `lambda_Z6` | `{inputs['lambda_Z6_poisson']:.9f}` | "
        "conditional coefficient from Poisson reserve thinning |"
    )
    print(
        f"| `a0_Z6` | `{inputs['a0_Z6_poisson_m_s2']:.9e}` | "
        f"{scales['Z6_vs_best_RAR_percent']:+.3f}% vs best same-function RAR; "
        f"{scales['Z6_vs_empirical_percent']:+.3f}% vs empirical reference |"
    )
    print()

    print("## SPARC RAR")
    print()
    print("| Scenario | a0 m/s^2 | RMS dex | binned RMS dex |")
    print("| --- | ---: | ---: | ---: |")
    rar_rows = [
        ("OPH unit", payload["rar"]["unit"]),
        ("Z6/Poisson", payload["rar"]["z6_poisson"]),
        ("empirical reference", payload["rar"]["empirical"]),
        ("best same-function", payload["rar"]["best"]),
    ]
    for name, row in rar_rows:
        if name == "Z6/Poisson":
            a0 = row["a0_eff_m_s2"]
            rms = row["rar_all_rms_dex"]
            binned = row["rar_binned_weighted_rms_dex"]
        else:
            a0 = row["a0_m_s2"]
            rms = row["all_data"]["rms_residual_dex"]
            binned = row["binned_data"]["rms_residual_dex_weighted_by_N"]
        print(f"| {name} | `{a0:.9e}` | `{rms:.6f}` | `{binned:.6f}` |")
    print()

    print("## SPARC Rotation Diagnostics")
    print()
    print("| Scenario | fixed-M/L RMS km/s | profiled-M/L chi2/pt | profiled RMS km/s |")
    print("| --- | ---: | ---: | ---: |")
    rows = [
        (
            "OPH unit",
            payload["fixed_ml_rotation"]["unit"]["stats"]["rms_residual_km_s"],
            payload["profiled_ml"]["unit"]["stats"],
        ),
        (
            "Z6/Poisson",
            payload["fixed_ml_rotation"]["z6_poisson"]["rotation_rms_km_s"],
            payload["profiled_ml"]["z6_poisson"]["stats"],
        ),
        (
            "empirical reference",
            payload["fixed_ml_rotation"]["empirical"]["stats"]["rms_residual_km_s"],
            payload["profiled_ml"]["empirical"]["stats"],
        ),
    ]
    for name, fixed_rms, profiled in rows:
        print(
            f"| {name} | `{fixed_rms:.6f}` | "
            f"`{profiled['chi2_per_point']:.6f}` | "
            f"`{profiled['rms_residual_km_s']:.6f}` |"
        )
    print()
    print("## SPARC Systematic Likelihood")
    print()
    systematic_inputs = payload["systematic_likelihood"]["inputs"]
    print(
        f"Cuts: Q <= `{systematic_inputs['max_quality']}`, "
        f"inclination >= `{systematic_inputs['min_inclination_deg']} deg`; "
        f"rows `{systematic_inputs['raw_rows_after_cuts']}`."
    )
    print()
    print("| Scenario | chi2/pt | chi2/dof | RMS km/s | median disk M/L | median D/D0 |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    systematic_rows = [
        ("OPH unit", payload["systematic_likelihood"]["unit"]["stats"]),
        ("Z6/Poisson", payload["systematic_likelihood"]["z6_poisson"]["stats"]),
        ("empirical reference", payload["systematic_likelihood"]["empirical"]["stats"]),
    ]
    for name, stats in systematic_rows:
        print(
            f"| {name} | `{stats['chi2_per_point']:.6f}` | "
            f"`{stats['chi2_per_dof']:.6f}` | "
            f"`{stats['rms_residual_km_s']:.6f}` | "
            f"`{stats['median_disk_upsilon']:.6f}` | "
            f"`{stats['median_distance_ratio']:.6f}` |"
        )
    print()
    print("## Verdict")
    print()
    print(
        "The unit branch is close to SPARC RAR, low in acceleration normalization, "
        "and favored in the profiled stellar-M/L scaffold. The Z6/Poisson branch "
        "lands close to the empirical acceleration scale and improves fixed-M/L "
        "rotation diagnostics, but loses that advantage when stellar M/L is "
        "profiled with the stated priors. The systematic likelihood scaffold "
        "also mildly favors the unit branch under its declared cuts and priors. "
        "The Z6 coefficient is a conditional "
        "microphysics target, not measurement evidence for the bridge theorem."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--rar-all", type=Path, default=sparc_rar_compare.DEFAULT_RAR_ALL)
    parser.add_argument("--rar-bins", type=Path, default=sparc_rar_compare.DEFAULT_RAR_BINS)
    parser.add_argument(
        "--mass-models",
        type=Path,
        default=sparc_rotation_curve_compare.DEFAULT_MASS_MODELS,
    )
    parser.add_argument(
        "--galaxy-sample",
        type=Path,
        default=sparc_systematic_likelihood.DEFAULT_GALAXY_SAMPLE,
    )
    parser.add_argument("--fit-min-a0", type=float, default=0.2e-10)
    parser.add_argument("--fit-max-a0", type=float, default=3.0e-10)
    parser.add_argument("--upsilon-disk", type=float, default=0.5)
    parser.add_argument("--upsilon-bulge", type=float, default=0.7)
    parser.add_argument("--disk-prior", type=float, default=0.5)
    parser.add_argument("--bulge-prior", type=float, default=0.7)
    parser.add_argument("--ml-prior-sigma-dex", type=float, default=0.15)
    parser.add_argument("--intrinsic-scatter-km-s", type=float, default=8.0)
    parser.add_argument("--disk-min", type=float, default=0.05)
    parser.add_argument("--disk-max", type=float, default=1.5)
    parser.add_argument("--bulge-min", type=float, default=0.05)
    parser.add_argument("--bulge-max", type=float, default=2.0)
    parser.add_argument("--coordinate-iterations", type=int, default=3)
    parser.add_argument("--max-quality", type=int, default=2)
    parser.add_argument("--min-inclination-deg", type=float, default=30.0)
    parser.add_argument("--profile-distance", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--distance-min-mpc", type=float, default=0.1)
    parser.add_argument("--distance-sigma-window", type=float, default=3.0)
    parser.add_argument("--profile-inclination", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--inclination-min-deg", type=float, default=5.0)
    parser.add_argument("--inclination-max-deg", type=float, default=89.5)
    parser.add_argument("--inclination-sigma-window", type=float, default=3.0)
    parser.add_argument("--profile-gas", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--gas-prior-sigma-dex", type=float, default=0.08)
    parser.add_argument("--gas-min", type=float, default=0.5)
    parser.add_argument("--gas-max", type=float, default=1.5)
    return parser.parse_args()


def main() -> int:
    print_markdown(compute(parse_args()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
