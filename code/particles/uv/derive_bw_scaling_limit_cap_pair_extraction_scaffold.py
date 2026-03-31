#!/usr/bin/env python3
"""Emit the canonical scaling-limit cap-pair extraction scaffold."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "uv" / "bw_scaling_limit_cap_pair_extraction_scaffold.json"
PRELIMIT_SYSTEM = ROOT / "particles" / "runs" / "uv" / "bw_realized_transported_cap_local_system.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_payload() -> dict[str, object]:
    filled_witnesses = [
        "reference_cap_local_test_system",
        "projectively_compatible_transported_cap_marginal_family",
        "asymptotic_transport_equivalence_certificate",
    ]
    remaining_witness = "vanishing_carried_collar_schedule_on_fixed_local_collars"
    smaller_raw_datum = "fixed_local_collar_markov_faithfulness_datum"
    remaining_formula = (
        "eta_{n,m,delta} = r_FR(epsilon_{n,m,delta}) + "
        "4 * lambda_{*,n,m,delta}^{-1} * delta^M_{m,delta}(epsilon_{n,m,delta}) -> 0"
    )
    return {
        "artifact": "oph_bw_scaling_limit_cap_pair_extraction_scaffold",
        "generated_utc": _timestamp(),
        "status": "constructive_prelimit_system_one_emitted_witness_still_missing",
        "public_promotion_allowed": False,
        "exact_missing_object": "scaling_limit_cap_pair_extraction",
        "precise_missing_object_name": "canonical_scaling_cap_pair_realization_from_transported_cap_marginals",
        "theorem_contract_name": "conditional_scaling_limit_cap_pair_extraction_theorem",
        "goal": (
            "Extract a canonical scaling-limit cap pair (A_infty(C), omega_infty^C) "
            "from transported cap marginals along the realized refinement-stable branch."
        ),
        "input_contract": {
            "must_use": [
                "transported_cap_marginals along a realized refinement chain",
                "inherited strip data with oriented null generator and ordered cut pair",
                "support-map control on the quasi-local cap net",
            ],
            "must_not_assume": [
                "type-I survival in the scaling limit",
                "a pre-existing BW automorphism theorem",
                "a fixed-cutoff density-matrix identification of the limit",
            ],
        },
        "fills_contract_witnesses": filled_witnesses,
        "remaining_missing_emitted_witness": remaining_witness,
        "remaining_missing_emitted_witness_formula": remaining_formula,
        "remaining_missing_emitted_witness_components": [
            "r_FR(epsilon_{n,m,delta})",
            "lambda_{*,n,m,delta}",
            "delta^M_{m,delta}(epsilon_{n,m,delta})",
        ],
        "remaining_missing_emitted_witness_domain": "every fixed local collar model",
        "smaller_remaining_raw_datum": smaller_raw_datum,
        "smaller_remaining_raw_datum_components": [
            "epsilon_{n,m,delta} = I(A_{m,delta}:D_{m,delta}|B_{m,delta})_{omega_{n->m}} -> 0",
            "exists lambda_bar_{m,delta} > 0 with lambda_{*,n,m,delta} >= lambda_bar_{m,delta} eventually",
        ],
        "schedule_reduction_theorem": (
            "For each fixed local collar model, the eta_{n,m,delta} vanishing schedule follows once the collarwise conditional mutual information vanishes and the faithful lower spectral bound is eventually uniform."
        ),
        "missing_input_witnesses": [remaining_witness],
        "prelimit_realized_system_artifact": str(PRELIMIT_SYSTEM),
        "theorem_assumptions": [
            "countable directed cap-local test system in one fixed reference chart",
            "transported pullback states on each fixed local cap algebra",
            "projective restriction compatibility across the directed local system",
            "asymptotic transport coherence across admissible transport choices",
            "vanishing carried collar schedules on every fixed local collar model",
        ],
        "checks": [
            "local_weak_star_extraction",
            "diagonal_subnet_extraction_on_countable_local_test_family",
            "projective_gluing_of_limit_functionals",
            "GNS_completion_of_the_local_quotient_family",
            "vanishing_carried_collar_errors",
            "refinement_stable_transport_compatibility",
            "uniqueness_of_extracted_limit_action",
        ],
        "output_certificate": {
            "extracted_pair": "(A_infty(C), omega_infty^C)",
            "canonicality": "unique local *-isomorphism class inside the asymptotic transport-equivalence class",
            "typeI_required": False,
            "residual_modular_class": "q_BW(C) remains open until ordered-cut rigidity closes",
            "status_on_fill": "realized_limit_pair_closed",
        },
        "collar_corollary": (
            "Exact fixed-cutoff collar splice and additivity identities pass to the extracted pair whenever they are used only through carried-collar remainders that vanish on fixed local collar models."
        ),
        "follow_on_object": {
            "id": "ordered_null_cut_pair_rigidity",
            "role": (
                "Collapse the residual cap-preserving conformal freedom on the realized "
                "limit pair to the unique BW hyperbolic subgroup."
            ),
        },
        "final_target": "sigma_t^{omega_infty^C} = alpha_{lambda_C(2 pi t)}",
        "notes": [
            "This is the first half of the UV/BW internalization route.",
            "The local quotient/prelimit transported cap-local system can already be packaged from the current corpus at the reference-chart and asymptotic transport-equivalence level.",
            "The compactness/extraction theorem itself is not the missing proof; the current remaining blocker is one emitted carried-collar witness satisfying the vanishing schedule on fixed local collar models.",
            "The sharp current contract for that witness is eta_{n,m,delta} = r_FR(epsilon_{n,m,delta}) + 4 * lambda_{*,n,m,delta}^{-1} * delta^M_{m,delta}(epsilon_{n,m,delta}) -> 0 on every fixed local collar model.",
            "That combined schedule reduces one level lower to a fixed-local-collar Markov/faithfulness datum: collarwise CMI vanishing plus an eventual positive lower spectral bound.",
            "It does not by itself prove the BW automorphism law.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the BW scaling-limit cap-pair extraction scaffold.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
