#!/usr/bin/env python3
"""Emit the constructive contract for RG matching and threshold closure.

This artifact turns the open running/matching issue into concrete local objects:
scheme locks, threshold certificates, beta-coefficient provenance, and interval
composition checks.  It does not promote the current declared conventions into
an OPH theorem.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path(__file__).resolve().parent / "runtime" / "rg_matching_threshold_contract_current.json"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_contract() -> dict[str, Any]:
    return {
        "artifact": "oph_rg_matching_threshold_contract",
        "generated_utc": _now_utc(),
        "github_issue": 32,
        "status": "constructive_contract_emitted_not_rg_matching_theorem",
        "promotion_allowed": False,
        "worker_result_policy": {
            "obstruction_only_result_allowed": False,
            "required_if_primary_route_fails": (
                "emit a smaller scheme-lock, threshold-map, beta-provenance, or interval-composition artifact"
            ),
        },
        "constructive_objects": [
            {
                "id": "scheme_lock",
                "kind": "certificate_interface",
                "target_status": "one_scheme_used_by_unification_anchor_endpoint_and_mass_readouts",
                "required_fields": [
                    "renormalization_scheme",
                    "normalization_of_U1",
                    "input_scale_definitions",
                    "conversion_maps",
                    "surfaces_using_the_scheme",
                ],
            },
            {
                "id": "threshold_map",
                "kind": "builder_interface",
                "target_status": "source_emitted_threshold_placements_or_declared_conventions",
                "required_fields": [
                    "particle_thresholds",
                    "superpartner_or_effective_thresholds",
                    "matching_scales",
                    "threshold_uncertainty_intervals",
                    "status_per_threshold",
                ],
            },
            {
                "id": "beta_provenance_table",
                "kind": "audit_table",
                "target_status": "every_beta_coefficient_is_oph_derived_declared_or_borrowed",
                "required_fields": [
                    "gauge_group",
                    "matter_content",
                    "loop_order",
                    "coefficient",
                    "status",
                    "source_artifact_or_reference",
                ],
            },
            {
                "id": "matching_interval_composition_certificate",
                "kind": "certificate_interface",
                "target_status": "interval_bound_for_composed_running_map",
                "required_fields": [
                    "input_intervals",
                    "composed_map",
                    "roundoff_budget",
                    "matching_budget",
                    "threshold_budget",
                    "image_interval",
                ],
            },
        ],
        "closure_gate": {
            "closable_now": False,
            "reason": (
                "The code path has an explicit declared running/matching surface, but the OPH-derived "
                "or declared status of every coefficient, threshold, and scheme conversion is not yet "
                "mechanically certified."
            ),
            "close_issue_when": [
                "all RG coefficients have source status in beta_provenance_table",
                "all matching and threshold placements have either OPH derivations or visible declared-convention status",
                "the composed running map has an interval certificate used by the P fixed-point and particle surfaces",
            ],
        },
        "local_next_steps": [
            "Populate beta_provenance_table from the existing D10/D11 builders.",
            "Split threshold placements into OPH-derived, QFT-borrowed, and declared-convention entries.",
            "Wire the interval-composition certificate into the compressed P trunk promotion gate.",
        ],
        "forbidden_promotions": [
            "silently_treating_declared_MSSM_running_as_OPH_derived",
            "using_threshold_choices_as_hidden_fit_parameters",
            "promoting_p_closure_root_without_interval_composition_certificate",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit the RG matching and threshold constructive contract.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()

    payload = build_contract()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    if args.print_json:
        print(text, end="")
    else:
        print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
