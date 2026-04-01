#!/usr/bin/env python3
"""Emit the charged determinant-line section extension scaffold.

This does not close the charged lane. It sharpens the absolute-anchor problem:
the determinant-line section is not the exact irreducible blocker. Once a
refinement-stable uncentered trace lift exists on theorem-grade physical
``Y_e`` (or an equivalent determinant line), the determinant-line section and
the affine anchor are induced canonically.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    DETERMINANT_LINE_JSON,
    TRACE_LIFT_COCYCLE_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    TRACE_LIFT_JSON,
    UNDERDETERMINATION_JSON,
    anchor_hard_rejections,
    anchor_input_contract,
    artifact_ref,
    load_json,
)


ROOT = Path(__file__).resolve().parents[2]
CENTRAL_SPLIT_EXTENSION_JSON = (
    ROOT / "particles" / "runs" / "flavor" / "charged_central_split_transfer_extension.json"
)
DEFAULT_OUT = DETERMINANT_LINE_JSON


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_artifact(underdetermination: dict, transfer_extension: dict) -> dict:
    return {
        "artifact": "oph_charged_determinant_line_section_extension",
        "generated_utc": _timestamp(),
        "status": "minimal_constructive_extension",
        "public_promotion_allowed": False,
        "extension_kind": "determinant_line_section",
        "exact_missing_object": "charged_determinant_line_section",
        "exact_smaller_missing_object": "refinement_stable_uncentered_trace_lift",
        "exact_smaller_missing_object_artifact": artifact_ref(TRACE_LIFT_JSON),
        "section_induced_by_exact_smaller_object": True,
        "extra_trivialization_required": False,
        "extra_metric_compatibility_required": False,
        "same_slot_scalarization_artifact": artifact_ref(TRACE_LIFT_COCYCLE_JSON),
        "exact_descended_scalar_artifact": artifact_ref(TRACE_LIFT_PHYSICAL_DESCENT_JSON),
        "upstream_prerequisites": {
            "promotion_theorem": "oph_generation_bundle_branch_generator_splitting",
            "promotion_effect": "theorem_grade_C_hat_e",
            "required_operator_surface": "theorem_grade_physical_Y_e_or_equivalent_determinant_line",
            "transfer_extension_artifact": transfer_extension.get("artifact"),
        },
        "section_contract": {
            "kind": "determinant_torsor_section",
            "required_covariance": "s_det(exp(3c) * detY) = s_det(detY) + 3c",
            "charged_anchor_readout": "A_ch = (1/3) * s_det(det Y_e)",
            "derived_quantities": {
                "g_e": "exp(A_ch)",
                "Delta_e_abs": "log(g_ch_shared) - A_ch",
                "masses": "exp(A_ch + centered_log_i)",
            },
        },
        "canonical_formula_on_fill": {
            "A_ch": "(1/3) * log(det(Y_e))",
            "g_e": "exp((1/3) * log(det(Y_e)))",
            "determinant_rule": "det(Y_e) = exp(3 * A_ch)",
        },
        "reduction_theorem": {
            "id": "charged_determinant_line_reduces_to_uncentered_trace_lift",
            "statement": (
                "Once theorem-grade centered promotion exists, a refinement-stable uncentered trace lift "
                "C_tilde_e = C_hat_e + mu I on theorem-grade physical Y_e or equivalent determinant line "
                "canonically induces the determinant-line section and A_ch = mu = (1/3) log det(Y_e)."
            ),
            "induced_data": [
                "determinant_torsor_section",
                "charged_absolute_anchor_A_ch",
                "g_e",
                "Delta_e_abs",
            ],
        },
        "why_this_is_sharper_than_bare_A_ch": [
            "The common-shift quotient acts on the determinant line by det(Y_e) -> exp(3c) det(Y_e).",
            "A section of that line is exactly the affine object needed to break the quotient symmetry.",
            "This packages the charged absolute anchor as a determinant-torsor coordinate rather than an abstract free scalar.",
        ],
        "input_contract": anchor_input_contract(),
        "hard_rejections": anchor_hard_rejections(underdetermination),
        "notes": [
            "This is a constructive extension route, not a theorem hidden in the current corpus.",
            "Promoting C_hat_e^cand is still upstream and necessary, but the determinant-line section is induced only after the uncentered trace lift exists on the promoted surface.",
            "The smaller exact missing object beneath this section is the refinement-stable uncentered trace lift that keeps the determinant coordinate canonical across the live refinement family.",
            "Inside that single slot, the only new post-promotion content is the scalar identity-mode cocycle primitive mu; no extra matrix-valued theorem sits between the lift and this section.",
            "Once refinement stability is imposed on theorem-grade physical Y_e, even that primitive descends to one physical affine scalar mu_phys(Y_e).",
            "Therefore the determinant-line section is not an additional independent blocker once that lift exists.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged determinant-line section extension scaffold.")
    parser.add_argument("--underdetermination", default=str(UNDERDETERMINATION_JSON))
    parser.add_argument("--transfer-extension", default=str(CENTRAL_SPLIT_EXTENSION_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    underdetermination = load_json(Path(args.underdetermination))
    transfer_extension = load_json(Path(args.transfer_extension))
    payload = build_artifact(underdetermination, transfer_extension)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
