#!/usr/bin/env python3
"""Emit the charged absolute-anchor extension scaffold.

This is not a closure theorem. It records the exact contract the future
theorem-grade affine-covariant charged anchor ``A_ch`` must satisfy once the
upstream charged operator candidate is promoted.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    ANCHOR_SECTION_JSON,
    GENERATION_BUNDLE_JSON,
    TRACE_LIFT_COCYCLE_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    TRACE_LIFT_JSON,
    UNDERDETERMINATION_JSON,
    anchor_hard_rejections,
    anchor_input_contract,
    artifact_ref,
    charged_waiting_set,
    load_json,
)

DEFAULT_OUT = ANCHOR_SECTION_JSON


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged absolute-anchor section scaffold.")
    parser.add_argument("--underdetermination", default=str(UNDERDETERMINATION_JSON))
    parser.add_argument("--generation-bundle", default=str(GENERATION_BUNDLE_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    underdetermination = load_json(Path(args.underdetermination))
    generation_bundle = load_json(Path(args.generation_bundle))
    current_status = charged_waiting_set(generation_bundle)

    artifact = {
        "artifact": "oph_charged_absolute_anchor_section",
        "generated_utc": _timestamp(),
        "status": "missing_theorem_side_breaker",
        "public_promotion_allowed": False,
        "exact_missing_object": "charged_absolute_anchor_A_ch",
        "section_kind": "common_shift_torsor_section",
        "current_surface": "charged_shape_only_common_shift_quotient",
        "upstream_prerequisite": {
            "required_theorem": "oph_generation_bundle_branch_generator_splitting",
            "required_clause": "compression_descendant_commutator_vanishes_or_is_uniformly_quadratic_small_after_central_split",
            "current_status": current_status,
        },
        "input_contract": anchor_input_contract(),
        "covariance_contract": "A_ch(logm + c*(1,1,1)) = A_ch(logm) + c",
        "required_new_scalar": "A_ch",
        "derived_quantities_on_fill": {
            "g_e": "exp(A_ch)",
            "Delta_e_abs": "log(g_ch_shared) - A_ch",
        },
        "induced_by_exact_smaller_object": "refinement_stable_uncentered_trace_lift",
        "induced_by_exact_smaller_object_artifact": artifact_ref(TRACE_LIFT_JSON),
        "same_slot_scalarization_artifact": artifact_ref(TRACE_LIFT_COCYCLE_JSON),
        "exact_descended_scalar_artifact": artifact_ref(TRACE_LIFT_PHYSICAL_DESCENT_JSON),
        "induced_formula_on_fill": "A_ch = (1/3) * log(det(Y_e)) = (1/3) * tr(log Y_e)",
        "hard_rejections": anchor_hard_rejections(underdetermination),
        "notes": [
            "This scaffold exists to package the exact future contract for the charged absolute anchor.",
            "Promotion of C_hat_e^cand is upstream and necessary, but not sufficient: it promotes theorem-grade centered data, not the affine common-shift breaker itself.",
            "Any candidate A_ch must exhibit the affine +c covariance explicitly, not merely reproduce one preferred numerical representative.",
            "Inside the post-promotion lift slot, A_ch is the scalar primitive mu rather than an independent extra theorem beyond the uncentered trace lift.",
            "Because that lift is already required to be refinement-stable on theorem-grade physical Y_e, the primitive further descends to one physical affine scalar mu_phys(Y_e).",
            "Once a refinement-stable uncentered trace lift exists on theorem-grade physical Y_e or an equivalent determinant line, A_ch is induced rather than independent.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
