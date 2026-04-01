#!/usr/bin/env python3
"""Shrink the charged post-promotion scalar slot to one physical affine scalar."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    ANCHOR_SECTION_JSON,
    DETERMINANT_LINE_JSON,
    TRACE_LIFT_COCYCLE_JSON,
    TRACE_LIFT_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    artifact_ref,
    load_json,
    trace_lift_physical_descent_contract,
)


DEFAULT_OUT = TRACE_LIFT_PHYSICAL_DESCENT_JSON


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(trace_lift: dict, cocycle: dict, determinant_line: dict, anchor: dict) -> dict:
    descent_contract = trace_lift_physical_descent_contract()
    return {
        "artifact": "oph_charged_mu_physical_descent_reduction",
        "generated_utc": _timestamp(),
        "status": "exact_descended_scalar_reduction",
        "public_promotion_allowed": False,
        "larger_missing_object": trace_lift.get("exact_missing_object"),
        "larger_missing_object_artifact_ref": artifact_ref(TRACE_LIFT_JSON),
        "exact_smaller_missing_object": descent_contract["exact_smaller_missing_object"],
        "exact_smaller_missing_object_kind": "single_affine_scalar_on_theorem_grade_physical_Y_e",
        "descent_contract": descent_contract,
        "input_scalarization_artifact_ref": artifact_ref(TRACE_LIFT_COCYCLE_JSON),
        "reduction_theorem": {
            "id": "charged_refinement_stable_mu_descends_to_physical_scalar",
            "statement": (
                "Assume theorem-grade C_hat_e is promoted on theorem-grade physical Y_e and that an "
                "uncentered lift C_tilde_e = C_hat_e + mu I is refinement-stable on that physical surface. "
                "Then the refinement identity-mode cocycle vanishes on every pair of refinement representatives "
                "of the same physical Y_e, so mu descends to a unique physical scalar mu_phys(Y_e). Conversely, "
                "any such mu_phys defines the uncentered lift, determinant-line section, and affine anchor by "
                "C_tilde_e = C_hat_e + mu_phys I, s_det = 3 mu_phys, and A_ch = mu_phys."
            ),
        },
        "forced_vanishing": {
            "refinement_pair_rule_before_descent": cocycle.get("scalar_cocycle_contract", {}).get(
                "pairwise_difference_rule"
            ),
            "on_same_physical_Y_e": descent_contract["forced_refinement_identity_mode"],
            "reason": "refinement stability identifies all refinement representatives of the same physical operator",
        },
        "equivalent_presentations_on_fill": {
            "descended_scalar": "mu_phys(Y_e)",
            "uncentered_trace_lift": {
                "artifact": trace_lift.get("artifact"),
                "artifact_ref": artifact_ref(TRACE_LIFT_JSON),
                "formula": "C_tilde_e(Y_e) = C_hat_e(Y_e) + mu_phys(Y_e) I",
            },
            "determinant_line_section": {
                "artifact": determinant_line.get("artifact"),
                "artifact_ref": artifact_ref(DETERMINANT_LINE_JSON),
                "formula": "s_det(Y_e) = 3 * mu_phys(Y_e)",
            },
            "affine_anchor": {
                "artifact": anchor.get("artifact"),
                "artifact_ref": artifact_ref(ANCHOR_SECTION_JSON),
                "formula": "A_ch(Y_e) = mu_phys(Y_e)",
            },
        },
        "why_this_is_smaller": [
            "The family-wise scalar primitive mu(r) is only needed before refinement stability is imposed.",
            "Once the lift is required to live on theorem-grade physical Y_e, the refinement cocycle is forced to vanish.",
            "The remaining exact burden is therefore one physical affine scalar, not a refinement-family primitive.",
        ],
        "do_not_claim_now": [
            "theorem-grade mu_phys(Y_e) on the live corpus",
            "theorem-grade determinant-line section on the live corpus",
            "theorem-grade A_ch on the live corpus",
        ],
        "notes": [
            "This sharpens the post-promotion frontier only under the same refinement-stability contract already required by the lift scaffold.",
            "It does not promote current-corpus closure or bypass the upstream C_hat_e promotion theorem.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the charged physical-scalar descent reduction beneath the uncentered trace lift."
    )
    parser.add_argument("--trace-lift", default=str(TRACE_LIFT_JSON))
    parser.add_argument("--cocycle-reduction", default=str(TRACE_LIFT_COCYCLE_JSON))
    parser.add_argument("--determinant-line", default=str(DETERMINANT_LINE_JSON))
    parser.add_argument("--anchor-section", default=str(ANCHOR_SECTION_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        load_json(Path(args.trace_lift)),
        load_json(Path(args.cocycle_reduction)),
        load_json(Path(args.determinant_line)),
        load_json(Path(args.anchor_section)),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
