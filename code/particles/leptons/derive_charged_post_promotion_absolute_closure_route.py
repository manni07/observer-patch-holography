#!/usr/bin/env python3
"""Emit the sharpened charged post-promotion absolute-closure route."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    ANCHOR_SECTION_JSON,
    CENTERED_OPERATOR_MU_NO_GO_JSON,
    DETERMINANT_LINE_JSON,
    GENERATION_BUNDLE_JSON,
    POST_PROMOTION_ROUTE_JSON,
    TRACE_LIFT_COCYCLE_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    TRACE_LIFT_JSON,
    UNDERDETERMINATION_JSON,
    artifact_ref,
    load_json,
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(
    generation_bundle: dict,
    underdetermination: dict,
    trace_lift: dict,
    physical_descent: dict,
    centered_operator_no_go: dict,
    determinant_line: dict,
    anchor: dict,
) -> dict:
    promotion_gate = dict(generation_bundle.get("promotion_gate", {}))
    charged_candidate = dict(generation_bundle.get("charged_sector_response_operator_candidate", {}))
    compare = dict(underdetermination.get("compare_only_continuation_target", {}))
    hard_reject = dict(underdetermination.get("hard_reject", {}))
    trace_contract = dict(trace_lift.get("contract", {}))

    return {
        "artifact": "oph_charged_post_promotion_absolute_closure_route",
        "generated_utc": _timestamp(),
        "status": "minimal_constructive_extension",
        "public_promotion_allowed": False,
        "route_kind": "promotion_then_single_affine_mode_recovery",
        "summary": (
            "The sharpened charged absolute route is two-stage: first promote the latent "
            "centered charged operator to theorem-grade C_hat_e, then supply one "
            "refinement-stable uncentered trace lift. The determinant-line section, A_ch, "
            "and the absolute charged outputs are induced once that second step exists."
        ),
        "operator_promotion_gate": {
            "candidate_object": charged_candidate.get("name", "C_hat_e^{cand}"),
            "missing_theorem": charged_candidate.get(
                "declaration_missing_theorem",
                generation_bundle.get("remaining_missing_theorem"),
            ),
            "smallest_missing_clause": charged_candidate.get(
                "smallest_missing_clause",
                promotion_gate.get("smaller_exact_missing_clause"),
            ),
            "current_strength_statement": promotion_gate.get("current_strength_statement"),
            "effect_on_fill": "theorem_grade_C_hat_e",
        },
        "current_absolute_no_go": {
            "current_theorem_output": underdetermination.get("theorem_emit", {}).get("meaning"),
            "no_go_theorem_id": underdetermination.get("no_go_theorem", {}).get("id"),
            "current_surface_missing_object": underdetermination.get("next_exact_missing_object"),
            "current_surface_missing_scalar": underdetermination.get("minimal_new_theorem", {}).get(
                "required_new_scalar"
            ),
        },
        "post_promotion_single_slot": {
            "id": trace_lift.get("exact_missing_object"),
            "artifact": trace_lift.get("artifact"),
            "artifact_ref": artifact_ref(TRACE_LIFT_JSON),
            "role": trace_lift.get("role"),
            "must_emit": trace_contract.get("must_emit"),
            "must_satisfy": trace_contract.get("must_satisfy"),
            "internal_carrier": "scalar_affine_cocycle_primitive",
            "internal_scalarization_artifact_ref": artifact_ref(TRACE_LIFT_COCYCLE_JSON),
            "internal_pairwise_difference_rule": trace_lift.get("internal_scalarization", {}).get(
                "pairwise_difference_rule"
            ),
            "exact_descended_scalar": {
                "id": physical_descent.get("exact_smaller_missing_object"),
                "artifact": physical_descent.get("artifact"),
                "artifact_ref": artifact_ref(TRACE_LIFT_PHYSICAL_DESCENT_JSON),
                "kind": physical_descent.get("exact_smaller_missing_object_kind"),
            },
        },
        "promotion_only_no_go": {
            "artifact": centered_operator_no_go.get("artifact"),
            "artifact_ref": artifact_ref(CENTERED_OPERATOR_MU_NO_GO_JSON),
            "theorem_id": centered_operator_no_go.get("no_go_theorem", {}).get("id"),
            "forbidden_target": centered_operator_no_go.get("target_scalar", {}).get("id"),
            "why_promotion_alone_fails": centered_operator_no_go.get("no_go_theorem", {}).get("statement"),
        },
        "exact_irreducible_chain": [
            {
                "id": charged_candidate.get(
                    "declaration_missing_theorem",
                    generation_bundle.get("remaining_missing_theorem"),
                ),
                "smallest_missing_clause": charged_candidate.get(
                    "smallest_missing_clause",
                    promotion_gate.get("smaller_exact_missing_clause"),
                ),
                "effect_on_fill": "theorem_grade_C_hat_e",
            },
            {
                "id": trace_lift.get("exact_missing_object"),
                "artifact": trace_lift.get("artifact"),
                "required_contract": trace_contract.get("must_emit"),
                "internal_carrier": "scalar_affine_cocycle_primitive",
                "exact_descended_scalar": physical_descent.get("exact_smaller_missing_object"),
                "effect_on_fill": "induce_determinant_line_section_A_ch_and_absolute_charged_outputs",
            },
        ],
        "induced_once_post_promotion_slot_exists": {
            "determinant_line_section": {
                "id": determinant_line.get("exact_missing_object"),
                "artifact": determinant_line.get("artifact"),
                "artifact_ref": artifact_ref(DETERMINANT_LINE_JSON),
                "reduction_theorem_id": determinant_line.get("reduction_theorem", {}).get("id"),
            },
            "charged_absolute_anchor": {
                "id": anchor.get("exact_missing_object"),
                "artifact": anchor.get("artifact"),
                "artifact_ref": artifact_ref(ANCHOR_SECTION_JSON),
                "covariance_contract": anchor.get("covariance_contract"),
                "derived_formula": anchor.get("induced_formula_on_fill"),
            },
            "absolute_outputs": {
                "g_e": "exp(A_ch)",
                "Delta_e_abs": "log(g_ch_shared) - A_ch",
                "masses": "exp(A_ch + centered_log_i)",
            },
        },
        "reduction_theorem": determinant_line.get("reduction_theorem"),
        "why_this_is_the_sharpest_route": [
            "On the current theorem surface A_ch is still absent, but after centered promotion it is no longer an independent post-promotion blocker.",
            "Promotion of C_hat_e alone still cannot emit mu_phys(Y_e), because centered operator data is common-shift invariant.",
            "The determinant-line section is induced by the refinement-stable uncentered trace lift, so there is no extra determinant trivialization theorem slot beyond that lift.",
            "Inside that lift slot, the residual ambiguity is only a scalar affine cocycle primitive, not a further matrix-valued transport theorem.",
            "Because the lift is already required to be refinement-stable on theorem-grade physical Y_e, that primitive descends further to one physical affine scalar mu_phys(Y_e).",
            "This is strictly sharper than treating eta, sigma, or a bare free A_ch as the next honest theorem-facing frontier.",
        ],
        "do_not_promote": [
            "eta_source_support_extension_log_per_side",
            "sigma_source_support_extension_total_log_per_side",
            "compare_only_g_e_star",
            "compare_only_delta_e_abs_star",
            f"g_e = {hard_reject.get('g_e')}",
            f"Delta_e_abs = {hard_reject.get('Delta_e_abs')}",
        ],
        "compare_only_absolute_target": {
            "g_e_star": compare.get("g_e_star"),
            "Delta_e_abs_star": compare.get("delta_e_abs_star"),
            "status": compare.get("status"),
        },
        "notes": [
            "This route artifact does not claim current-corpus closure.",
            "It sharpens only the theorem-facing frontier above the promoted operator surface.",
            "The present corpus still lacks both the operator-promotion theorem and the post-promotion uncentered trace lift.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged post-promotion absolute-closure route.")
    parser.add_argument("--generation-bundle", default=str(GENERATION_BUNDLE_JSON))
    parser.add_argument("--underdetermination", default=str(UNDERDETERMINATION_JSON))
    parser.add_argument("--trace-lift", default=str(TRACE_LIFT_JSON))
    parser.add_argument("--physical-descent", default=str(TRACE_LIFT_PHYSICAL_DESCENT_JSON))
    parser.add_argument("--centered-operator-no-go", default=str(CENTERED_OPERATOR_MU_NO_GO_JSON))
    parser.add_argument("--determinant-line", default=str(DETERMINANT_LINE_JSON))
    parser.add_argument("--anchor-section", default=str(ANCHOR_SECTION_JSON))
    parser.add_argument("--output", default=str(POST_PROMOTION_ROUTE_JSON))
    args = parser.parse_args()

    artifact = build_artifact(
        load_json(Path(args.generation_bundle)),
        load_json(Path(args.underdetermination)),
        load_json(Path(args.trace_lift)),
        load_json(Path(args.physical_descent)),
        load_json(Path(args.centered_operator_no_go)),
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
