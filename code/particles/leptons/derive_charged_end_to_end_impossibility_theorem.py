#!/usr/bin/env python3
"""Emit the decisive charged end-to-end non-closure theorem artifact.

This script packages the current charged-lane verdict in one place:

1. The live corpus still does not promote ``C_hat_e^{cand}`` to a theorem-grade
   charged sector-response operator because the branch-generator splitting
   theorem remains open.
2. Even if the minimal central-split transfer extension were internalized, the
   charged absolute scale would still remain open because the present theorem
   surface fixes only the common-shift quotient class.

So the current charged lane cannot be closed end-to-end on the live corpus.
The exact irreducible chain is the promotion theorem for ``C_hat_e`` followed
by the affine-covariant absolute anchor ``A_ch``.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FORWARD_JSON = ROOT / "particles" / "runs" / "leptons" / "forward_charged_leptons.json"
READOUT_JSON = ROOT / "particles" / "runs" / "leptons" / "lepton_log_spectrum_readout.json"
UNDERDETERMINATION_JSON = (
    ROOT / "particles" / "runs" / "leptons" / "charged_absolute_scale_underdetermination_theorem.json"
)
ANCHOR_SECTION_JSON = ROOT / "particles" / "runs" / "leptons" / "charged_absolute_anchor_section.json"
GENERATOR_JSON = ROOT / "particles" / "runs" / "flavor" / "generation_bundle_branch_generator.json"
TRANSFER_JSON = ROOT / "particles" / "runs" / "flavor" / "charged_central_split_transfer_extension.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "leptons" / "charged_end_to_end_impossibility_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(
    forward: dict[str, Any],
    readout: dict[str, Any],
    underdetermination: dict[str, Any],
    anchor_section: dict[str, Any],
    generator: dict[str, Any],
    transfer: dict[str, Any],
) -> dict[str, Any]:
    charged_candidate = dict(generator["charged_sector_response_operator_candidate"])
    promotion_gate = dict(generator["promotion_gate"])
    centered_logs = [float(value) for value in readout["E_e_log_centered"]]
    current_values = [float(value) for value in forward["singular_values_abs"]]

    return {
        "artifact": "oph_charged_end_to_end_impossibility_theorem",
        "generated_utc": _timestamp(),
        "verdict": "no_current_corpus_end_to_end_closure",
        "public_promotion_allowed": False,
        "closure_now": False,
        "charged_public_masses_emitted": False,
        "theorem_statement": (
            "On the live charged corpus there is no theorem-grade end-to-end closure. "
            "The current same-carrier chain emits only the centered charged shape modulo "
            "common shift; the latent operator C_hat_e^{cand} remains undeclared because "
            "oph_generation_bundle_branch_generator_splitting is still open; and even the "
            "minimal central-split transfer extension would only promote theorem-grade "
            "centered operator data, not the affine-covariant absolute anchor A_ch. "
            "Therefore no theorem-grade g_e, Delta_e_abs, or charged masses are emitted "
            "on the current corpus."
        ),
        "current_concrete_surface": {
            "same_carrier_shape_status": "closed_mod_common_shift",
            "current_singular_values_abs": current_values,
            "current_centered_log": centered_logs,
            "eta_e_split_log_per_side": float(readout["eta_e_split_log_per_side"]),
            "sigma_e_total_log_per_side": float(readout["sigma_e_total_log_per_side"]),
            "hierarchy_mode": readout["hierarchy_mode"],
        },
        "operator_side_no_go": {
            "current_object": charged_candidate["name"],
            "current_status": charged_candidate["declaration_status"],
            "exact_missing_theorem": charged_candidate["declaration_missing_theorem"],
            "exact_missing_clause": charged_candidate["smallest_missing_clause"],
            "proof_gate": promotion_gate,
            "theorem_grade_C_hat_e_available_now": False,
            "no_hidden_promotion_in_current_corpus": True,
            "why_not": (
                "The live generator artifact records neither exact vanishing nor uniform "
                "quadratic smallness of the compression-descendant commutator after the "
                "central split."
            ),
        },
        "minimal_operator_extension": {
            "id": transfer["theorem"]["id"],
            "status": transfer["status"],
            "current_corpus_contains_theorem": False,
            "effect_if_internalized": "promote_C_hat_e_only",
            "non_sufficiency_for_absolute_scale": (
                "Internalizing the central-split transfer extension would promote C_hat_e, "
                "but it would still leave charged_absolute_anchor_A_ch open."
            ),
            "local_numeric_margin_if_extension_proved": transfer["local_numeric_promotion_test"],
        },
        "absolute_anchor_no_go": {
            "current_theorem_output": underdetermination["theorem_emit"]["meaning"],
            "common_shift_no_go_id": underdetermination["no_go_theorem"]["id"],
            "exact_missing_object": anchor_section["exact_missing_object"],
            "required_contract": anchor_section["covariance_contract"],
            "theorem_grade_A_ch_available_now": False,
            "no_replacement_law_on_current_surface": True,
            "why_not": (
                "Any current-corpus functional that factors only through centered charged data "
                "or other common-shift invariant readouts cannot emit A_ch, because A_ch must "
                "transform affinely under logm -> logm + c*(1,1,1)."
            ),
            "hard_rejections": anchor_section["hard_rejections"],
        },
        "exact_irreducible_chain": [
            {
                "id": charged_candidate["declaration_missing_theorem"],
                "smallest_missing_clause": charged_candidate["smallest_missing_clause"],
                "effect_on_fill": "theorem_grade_C_hat_e",
            },
            {
                "id": anchor_section["exact_missing_object"],
                "required_contract": anchor_section["covariance_contract"],
                "effect_on_fill": "g_e_Delta_e_abs_and_public_charged_masses",
            },
        ],
        "future_symbolic_forward_surface": {
            "if_A_ch_exists": {
                "g_e": "exp(A_ch)",
                "Delta_e_abs": "log(g_ch_shared) - A_ch",
                "m_e": "exp(A_ch + e_log_centered)",
                "m_mu": "exp(A_ch + mu_log_centered)",
                "m_tau": "exp(A_ch + tau_log_centered)",
            }
        },
        "theorem_forbid_emit_now": [
            "theorem_grade_C_hat_e",
            "A_ch",
            "g_e",
            "Delta_e_abs",
            "m_e",
            "m_mu",
            "m_tau",
        ],
        "notes": [
            "This is stronger than a blocker audit: it rules out end-to-end charged closure on the present corpus.",
            "The exact minimal operator-side extension is the central_split_quadratic_commutator_transfer theorem.",
            "The exact irreducible absolute object beyond the present scaffolds is charged_absolute_anchor_A_ch.",
            "Measured charged masses and compare-only D12 absolute targets remain forbidden from theorem artifacts.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged end-to-end impossibility theorem artifact.")
    parser.add_argument("--forward", default=str(FORWARD_JSON))
    parser.add_argument("--readout", default=str(READOUT_JSON))
    parser.add_argument("--underdetermination", default=str(UNDERDETERMINATION_JSON))
    parser.add_argument("--anchor-section", default=str(ANCHOR_SECTION_JSON))
    parser.add_argument("--generator", default=str(GENERATOR_JSON))
    parser.add_argument("--transfer", default=str(TRANSFER_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        _load_json(Path(args.forward)),
        _load_json(Path(args.readout)),
        _load_json(Path(args.underdetermination)),
        _load_json(Path(args.anchor_section)),
        _load_json(Path(args.generator)),
        _load_json(Path(args.transfer)),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
