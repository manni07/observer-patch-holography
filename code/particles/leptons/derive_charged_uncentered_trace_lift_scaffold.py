#!/usr/bin/env python3
"""Emit the charged uncentered trace-lift scaffold.

This is the smaller exact object beneath the determinant-line section and the
affine charged anchor. It does not close the charged lane by itself.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    GENERATION_BUNDLE_JSON,
    TRACE_LIFT_COCYCLE_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    TRACE_LIFT_JSON,
    artifact_ref,
    charged_waiting_set,
    load_json,
    trace_lift_scalar_cocycle_contract,
)


DEFAULT_OUT = TRACE_LIFT_JSON


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_payload(generation_bundle: dict) -> dict:
    waiting_set = charged_waiting_set(generation_bundle)
    cocycle_contract = trace_lift_scalar_cocycle_contract()
    return {
        "artifact": "oph_charged_uncentered_trace_lift_scaffold",
        "generated_utc": _timestamp(),
        "status": "minimal_constructive_extension",
        "public_promotion_allowed": False,
        "exact_missing_object": "refinement_stable_uncentered_trace_lift",
        "role": (
            "Package the smaller exact charged object beneath the determinant-line section: "
            "an uncentered trace lift that keeps the absolute common-shift mode canonical across refinements."
        ),
        "upstream_prerequisites": {
            "promotion_theorem": "oph_generation_bundle_branch_generator_splitting",
            "smaller_upstream_clause": "compression_descendant_commutator_vanishes_or_is_uniformly_quadratic_small_after_central_split",
            "current_waiting_set": waiting_set,
            "promoted_centered_object": "theorem_grade_C_hat_e",
        },
        "contract": {
            "must_emit": "one theorem-grade uncentered lift C_tilde_e = C_hat_e + mu I on physical Y_e or an equivalent determinant-line presentation",
            "must_satisfy": [
                "refinement stability on the live refinement family",
                "common-shift covariance mu(logm + c*(1,1,1)) = mu(logm) + c",
                "compatibility with the centered promoted operator C_hat_e",
            ],
            "must_not_use": [
                "measured charged masses",
                "compare-only D12 continuation targets",
                "centered-shape-only functionals",
                "shared-budget seeds alone",
            ],
        },
        "internal_scalarization": {
            "artifact_ref": artifact_ref(TRACE_LIFT_COCYCLE_JSON),
            "irreducible_new_degree_of_freedom": "scalar affine cocycle primitive mu",
            "pairwise_difference_rule": cocycle_contract["pairwise_difference_rule"],
            "primitive_required_on_fill": cocycle_contract["primitive_required_on_fill"],
            "exact_descended_scalar_artifact_ref": artifact_ref(TRACE_LIFT_PHYSICAL_DESCENT_JSON),
        },
        "canonical_formula_on_fill": {
            "A_ch": "mu = (1/3) * tr(log Y_e) = (1/3) * log(det(Y_e))",
            "lift_formula": "C_tilde_e = C_hat_e + A_ch I",
        },
        "induced_objects": {
            "determinant_line_section": "oph_charged_determinant_line_section_extension",
            "charged_absolute_anchor": "charged_absolute_anchor_A_ch",
            "absolute_outputs": ["g_e", "Delta_e_abs", "m_e", "m_mu", "m_tau"],
        },
        "why_this_is_the_sharpest_lower_object": [
            "Once the uncentered trace lift exists, the determinant-line section is induced rather than independently chosen.",
            "The affine common-shift mode is exactly the missing charged degree of freedom, so the trace lift is the first object that can carry it canonically.",
            "Any object built only from centered data is still common-shift invariant and therefore cannot replace this lift.",
        ],
        "notes": [
            "This is not a theorem hidden in the current corpus.",
            "It sits strictly below the determinant-line section and A_ch in the charged reduction chain.",
            "Under the refinement-stability clause already required here, that scalar primitive descends further to one physical affine scalar mu_phys(Y_e).",
            "The branch-generator splitting theorem remains upstream and necessary before this lift can even be posed on theorem-grade physical data.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged uncentered trace-lift scaffold.")
    parser.add_argument("--generation-bundle", default=str(GENERATION_BUNDLE_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(load_json(Path(args.generation_bundle)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
