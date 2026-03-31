#!/usr/bin/env python3
"""Emit the quotient/local-level transported cap-local UV system."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXTRACTION_SCAFFOLD = ROOT / "particles" / "runs" / "uv" / "bw_scaling_limit_cap_pair_extraction_scaffold.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "uv" / "bw_realized_transported_cap_local_system.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(extraction_scaffold: dict[str, object]) -> dict[str, object]:
    filled = list(extraction_scaffold["fills_contract_witnesses"])
    remaining = str(extraction_scaffold["remaining_missing_emitted_witness"])
    remaining_formula = str(extraction_scaffold.get("remaining_missing_emitted_witness_formula", ""))
    smaller_raw_datum = str(extraction_scaffold.get("smaller_remaining_raw_datum", ""))
    smaller_raw_components = list(extraction_scaffold.get("smaller_remaining_raw_datum_components", []))
    return {
        "artifact": "oph_realized_transported_cap_local_system",
        "generated_utc": _timestamp(),
        "status": "constructed_prelimit_system_one_emitted_witness_still_missing",
        "public_promotion_allowed": False,
        "role": (
            "Package the quotient/local *-isomorphism-level transported cap-local system "
            "that the scaling-limit cap-pair extraction theorem uses as input."
        ),
        "fills_contract_witnesses": filled,
        "remaining_missing_emitted_witness": remaining,
        "source_scaffold_artifact": extraction_scaffold["artifact"],
        "reference_cap_local_test_system": {
            "status": "packaged",
            "kind": "countable_directed_reference_test_family",
            "construction": (
                "Fix one reference cut presentation/chart along the cap boundary and use "
                "rational matrix-coefficient cap-local subalgebras on supported local regions "
                "s ⊂ C as the directed test family T_{m,s} ⊂ A_m(s)."
            ),
            "equivalence_level": "quotient_or_local_star_isomorphism_class",
        },
        "projectively_compatible_transported_cap_marginal_family": {
            "status": "packaged",
            "construction": (
                "For n ≥ m, define ω_{n→m}^{(χ)}(X) = ω_{ℓ_n}(τ_{n→m}^{(χ)}(X)), where τ_{n→m}^{(χ)} "
                "is refinement inclusion plus admissible recharting into the fixed reference chart."
            ),
            "compatibility": [
                "isotony of the directed local family",
                "projective restriction compatibility",
                "channel composition along the realized refinement chain",
            ],
        },
        "asymptotic_transport_equivalence_certificate": {
            "status": "packaged",
            "equivalence_statement": (
                "Admissible transport choices differ only by the derived boundary recharting/gauge action, "
                "so they define one OPH-stable local *-isomorphism class on the quotient test system."
            ),
            "scope": "reference_chart_transport_class",
        },
        "remaining_missing_witness_contract": {
            "id": remaining,
            "formula": remaining_formula,
            "for_fixed_models": "every fixed local collar model (m, delta)",
            "meaning": (
                "Carried-collar remainder schedules vanish along the realized refinement chain "
                "after transport to one fixed collar model."
            ),
        },
        "smaller_remaining_raw_datum": {
            "id": smaller_raw_datum,
            "components": smaller_raw_components,
            "role": "raw fixed-local-collar datum that implies the eta schedule once emitted",
        },
        "promotion_boundary": {
            "closed_here": [
                "reference_cap_local_test_system",
                "projectively_compatible_transported_cap_marginal_family",
                "asymptotic_transport_equivalence_certificate",
            ],
            "not_closed_here": [
                "canonical_scaling_cap_pair_realization_from_transported_cap_marginals",
                "ordered_null_cut_pair_rigidity",
            ],
        },
        "next_exact_object": {
            "id": "canonical_scaling_cap_pair_realization_from_transported_cap_marginals",
            "remaining_witness": remaining,
        },
        "notes": [
            "This artifact is constructive but not yet the realized scaling-limit cap pair.",
            "It packages the prelimit transported cap-local system at the quotient/local *-isomorphism level only.",
            "The only remaining emitted witness for cap-pair promotion is the vanishing carried-collar schedule on fixed local collar models.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the realized transported cap-local system artifact.")
    parser.add_argument("--extraction-scaffold", default=str(EXTRACTION_SCAFFOLD))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(_load_json(Path(args.extraction_scaffold)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
