#!/usr/bin/env python3
"""Rule out mu_phys readout from the promoted centered charged operator alone."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    CENTERED_OPERATOR_MU_NO_GO_JSON,
    GENERATION_BUNDLE_JSON,
    TRACE_LIFT_PHYSICAL_DESCENT_JSON,
    load_json,
)


DEFAULT_OUT = CENTERED_OPERATOR_MU_NO_GO_JSON


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(generation_bundle: dict, physical_descent: dict) -> dict:
    candidate = dict(generation_bundle.get("charged_sector_response_operator_candidate", {}))
    spectrum = [float(value) for value in candidate.get("ordered_spectrum", [])]
    trace_zero = abs(sum(spectrum)) <= 1.0e-12 if spectrum else None
    return {
        "artifact": "oph_charged_centered_operator_mu_phys_no_go",
        "generated_utc": _timestamp(),
        "status": "promotion_only_absolute_scalar_no_go",
        "public_promotion_allowed": False,
        "scope": "post_promotion_centered_operator_only",
        "input_surface": {
            "hypothetical_promoted_object": "theorem_grade_C_hat_e",
            "formula_origin": candidate.get("formula"),
            "ordered_spectrum_sum": None if not spectrum else sum(spectrum),
            "trace_zero_by_construction": trace_zero,
            "common_shift_invariance": "C_hat_e(exp(c) * Y_e) = C_hat_e(Y_e)",
        },
        "target_scalar": {
            "id": physical_descent.get("exact_smaller_missing_object"),
            "kind": physical_descent.get("exact_smaller_missing_object_kind"),
            "required_covariance": "mu_phys(exp(c) * Y_e) = mu_phys(Y_e) + c",
            "equivalent_readouts_on_fill": [
                "A_ch(Y_e) = mu_phys(Y_e)",
                "(1/3) * log(det(Y_e)) = mu_phys(Y_e)",
                "log(g_e) = mu_phys(Y_e)",
            ],
        },
        "no_go_theorem": {
            "id": "charged_centered_operator_cannot_emit_mu_phys",
            "statement": (
                "Let F be any theorem-grade readout that factors only through the promoted centered "
                "charged operator C_hat_e. Because C_hat_e is unchanged under the physical common-shift "
                "action Y_e -> exp(c) Y_e, every such F is common-shift invariant. Therefore no such F "
                "can equal the affine physical scalar mu_phys(Y_e), nor any equivalent readout such as "
                "A_ch, (1/3) log det(Y_e), or log(g_e), all of which transform by +c."
            ),
            "proof_skeleton": [
                "C_hat_e is centered, so scalar identity shifts are removed by construction.",
                "Hence C_hat_e(exp(c) * Y_e) = C_hat_e(Y_e) on the hypothetical promoted surface.",
                "Any readout F(C_hat_e(Y_e)) is therefore invariant under Y_e -> exp(c) Y_e.",
                "But mu_phys(exp(c) * Y_e) = mu_phys(Y_e) + c, so F cannot equal mu_phys.",
            ],
        },
        "forbidden_readout_classes": [
            "centered spectrum only",
            "trace-zero spectral invariants only",
            "any function of theorem-grade C_hat_e alone",
        ],
        "remaining_exact_object_after_no_go": {
            "id": physical_descent.get("exact_smaller_missing_object"),
            "artifact": physical_descent.get("artifact"),
            "artifact_ref": "code/particles/runs/leptons/charged_mu_physical_descent_reduction.json",
            "summary": "one physical affine scalar on theorem-grade physical Y_e",
        },
        "notes": [
            "This theorem does not block future closure absolutely; it blocks only the false route that tries to recover mu_phys from centered operator data alone.",
            "The upstream promotion theorem for C_hat_e remains necessary, but it is not sufficient for absolute closure.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the charged centered-operator no-go theorem for mu_phys."
    )
    parser.add_argument("--generation-bundle", default=str(GENERATION_BUNDLE_JSON))
    parser.add_argument("--physical-descent", default=str(TRACE_LIFT_PHYSICAL_DESCENT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        load_json(Path(args.generation_bundle)),
        load_json(Path(args.physical_descent)),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
