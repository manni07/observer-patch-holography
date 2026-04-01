#!/usr/bin/env python3
"""Reduce the charged post-promotion lift slot to its scalar cocycle content."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    ANCHOR_SECTION_JSON,
    DETERMINANT_LINE_JSON,
    GENERATION_BUNDLE_JSON,
    TRACE_LIFT_COCYCLE_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    TRACE_LIFT_JSON,
    artifact_ref,
    charged_waiting_set,
    load_json,
    trace_lift_scalar_cocycle_contract,
)


DEFAULT_OUT = TRACE_LIFT_COCYCLE_JSON


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(
    generation_bundle: dict,
    trace_lift: dict,
    determinant_line: dict,
    anchor: dict,
) -> dict:
    waiting_set = charged_waiting_set(generation_bundle)
    cocycle_contract = trace_lift_scalar_cocycle_contract()
    promotion_gate = dict(generation_bundle.get("promotion_gate", {}))
    charged_candidate = dict(generation_bundle.get("charged_sector_response_operator_candidate", {}))
    return {
        "artifact": "oph_charged_uncentered_trace_lift_cocycle_reduction",
        "generated_utc": _timestamp(),
        "status": "conditional_scalar_cocycle_reduction",
        "public_promotion_allowed": False,
        "role": (
            "Reduce the post-promotion charged absolute-side blocker to its exact scalar content: "
            "after centered promotion, the only remaining degree of freedom in an uncentered "
            "trace lift is the affine scalar identity mode."
        ),
        "single_slot_preserved": trace_lift.get("exact_missing_object"),
        "upstream_prerequisites": {
            "promotion_theorem": charged_candidate.get(
                "declaration_missing_theorem",
                generation_bundle.get("remaining_missing_theorem"),
            ),
            "smallest_missing_clause": charged_candidate.get(
                "smallest_missing_clause",
                promotion_gate.get("smaller_exact_missing_clause"),
            ),
            "promoted_centered_object": trace_lift.get("upstream_prerequisites", {}).get("promoted_centered_object"),
            "required_operator_surface": determinant_line.get("upstream_prerequisites", {}).get(
                "required_operator_surface"
            ),
            "current_waiting_set": waiting_set,
        },
        "matrix_vs_scalar_content": {
            "centered_operator_fixed_on_fill": "theorem_grade_C_hat_e",
            "admissible_uncentered_extension": "C_tilde_e = C_hat_e + mu I",
            "uniqueness_mod_scalar_identity": True,
            "irreducible_new_degree_of_freedom": "scalar affine cocycle primitive mu",
        },
        "scalar_cocycle_contract": cocycle_contract,
        "exact_descended_scalar_artifact_ref": artifact_ref(TRACE_LIFT_PHYSICAL_DESCENT_JSON),
        "equivalent_presentations_on_fill": {
            "uncentered_trace_lift": {
                "artifact": trace_lift.get("artifact"),
                "artifact_ref": artifact_ref(TRACE_LIFT_JSON),
                "object": trace_lift.get("exact_missing_object"),
                "formula": "C_tilde_e(r) = C_hat_e(r) + mu(r) I",
            },
            "determinant_line_section": {
                "artifact": determinant_line.get("artifact"),
                "artifact_ref": artifact_ref(DETERMINANT_LINE_JSON),
                "object": determinant_line.get("exact_missing_object"),
                "formula": "s_det(r) = 3 * mu(r)",
            },
            "affine_anchor": {
                "artifact": anchor.get("artifact"),
                "artifact_ref": artifact_ref(ANCHOR_SECTION_JSON),
                "object": anchor.get("exact_missing_object"),
                "formula": "A_ch(r) = mu(r)",
            },
        },
        "correspondence_on_fill": {
            "lift_to_section": "s_det = tr(C_tilde_e - C_hat_e) = 3 * mu",
            "section_to_anchor": "A_ch = (1/3) * s_det",
            "anchor_to_lift": "C_tilde_e = C_hat_e + A_ch I",
            "determinant_formula": "A_ch = mu = (1/3) * log(det(Y_e)) = (1/3) * tr(log Y_e)",
        },
        "theorem_statement": (
            "Assuming theorem-grade promotion of C_hat_e on theorem-grade physical Y_e, the "
            "post-promotion charged absolute-side blocker is not an additional matrix-valued "
            "refinement theorem. Any admissible uncentered lift differs from the centered "
            "operator only by a scalar multiple of the identity, and the pairwise refinement "
            "differences of that scalar form an additive cocycle. Trivializing that cocycle by "
            "a primitive mu is equivalent to giving the uncentered trace lift, the determinant-line "
            "section, and the affine anchor A_ch."
        ),
        "why_this_is_sharp": [
            "It keeps the existing single-slot frontier intact: the missing object remains the refinement-stable uncentered trace lift.",
            "It removes a weaker reading in which an extra matrix theorem or separate determinant trivialization would still be needed after centered promotion.",
            "It identifies the exact post-promotion burden as one scalar cocycle primitive on the refinement family.",
            "Once refinement stability on theorem-grade physical Y_e is imposed, even that primitive descends further to one physical affine scalar.",
        ],
        "do_not_claim_now": [
            "current-corpus theorem-grade C_hat_e",
            "closed scalar cocycle primitive on the live refinement family",
            "theorem-grade determinant-line section",
            "theorem-grade A_ch",
        ],
        "notes": [
            "This artifact is a conditional reduction of the future single slot, not a proof that the slot is already filled.",
            "The cocycle language is used only after centered promotion identifies the non-scalar part across refinements.",
            "Measured charged masses remain outside the defining data of this reduction.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the charged uncentered trace-lift scalar-cocycle reduction artifact."
    )
    parser.add_argument("--generation-bundle", default=str(GENERATION_BUNDLE_JSON))
    parser.add_argument("--trace-lift", default=str(TRACE_LIFT_JSON))
    parser.add_argument("--determinant-line", default=str(DETERMINANT_LINE_JSON))
    parser.add_argument("--anchor-section", default=str(ANCHOR_SECTION_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        load_json(Path(args.generation_bundle)),
        load_json(Path(args.trace_lift)),
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
