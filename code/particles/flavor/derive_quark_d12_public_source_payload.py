#!/usr/bin/env python3
"""Emit the selected-public-class D12 pure-B quark source payload.

Chain role: materialize the pure-B source readback pair from the public exact
quark theorem on the selected frame class.

Mathematics: the public exact quark theorem emits the selected-class light
ratio. The closed D12 value law gives

    Delta_ud_overlap = (1/6) log(m_d / m_u)
    t1 = 5 Delta_ud_overlap.

The pure-B source payload is then forced by the D12 source corollary:

    beta_u = t1 / 10, beta_d = -t1 / 10,
    source_u = beta_u * B_ord, source_d = beta_d * B_ord.

Output: a data-bearing source payload on the selected public class. This is
not an arbitrary-P off-canonical transport theorem.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLIC_YUKAWA = ROOT / "particles" / "runs" / "flavor" / "quark_public_exact_yukawa_end_to_end_theorem.json"
DEFAULT_T1_LAW = ROOT / "particles" / "runs" / "flavor" / "quark_d12_t1_value_law.json"
DEFAULT_SOURCE_READBACK = ROOT / "particles" / "runs" / "flavor" / "quark_diagonal_common_gap_shift_source_readback.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_public_source_payload.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(public_yukawa: dict[str, Any], t1_law: dict[str, Any], source_readback: dict[str, Any]) -> dict[str, Any]:
    exact_values = dict(public_yukawa["public_exact_outputs"]["exact_running_values_gev"])
    m_u = float(exact_values["u"])
    m_d = float(exact_values["d"])
    ell_ud = math.log(m_d / m_u)
    delta_ud_overlap = ell_ud / 6.0
    t1 = 5.0 * delta_ud_overlap
    beta_u = t1 / 10.0
    beta_d = -t1 / 10.0
    b_ord = [float(value) for value in source_readback["B_ord"]]
    source_u = [beta_u * value for value in b_ord]
    source_d = [beta_d * value for value in b_ord]
    b_norm_sq = float(sum(value * value for value in b_ord))

    return {
        "artifact": "oph_quark_d12_public_source_payload",
        "generated_utc": _timestamp(),
        "scope": "selected_public_physical_quark_frame_class_only",
        "proof_status": "closed_public_selected_class_pure_B_source_payload",
        "public_promotion_allowed": True,
        "off_canonical_promotion_allowed": False,
        "input_artifacts": {
            "public_exact_yukawa_theorem": public_yukawa.get("artifact"),
            "d12_t1_value_law": t1_law.get("artifact"),
            "source_readback_law": source_readback.get("artifact"),
        },
        "selected_public_physical_frame_class": public_yukawa["selected_public_physical_frame_class"],
        "theorem_statement": (
            "On the selected public quark frame class, the public exact quark theorem emits the exact light ratio "
            "m_d/m_u. The D12 value law gives Delta_ud_overlap = (1/6) log(m_d/m_u) and t1 = 5 Delta_ud_overlap. "
            "The pure-B source payload is therefore beta_u = t1/10, beta_d = -t1/10, with source readbacks "
            "beta_u * B_ord and beta_d * B_ord."
        ),
        "exact_light_ratio_source": {
            "m_u_gev": m_u,
            "m_d_gev": m_d,
            "ell_ud": ell_ud,
            "ell_ud_formula": "log(m_d / m_u)",
        },
        "d12_scalars": {
            "Delta_ud_overlap": delta_ud_overlap,
            "Delta_ud_overlap_formula": "(1/6) * log(m_d / m_u)",
            "t1": t1,
            "t1_formula": "(5/6) * log(m_d / m_u)",
        },
        "B_ord": b_ord,
        "B_ord_norm_sq": b_norm_sq,
        "beta_u_diag_B_source": beta_u,
        "beta_d_diag_B_source": beta_d,
        "J_B_source_u": beta_u,
        "J_B_source_d": beta_d,
        "source_readback_u_log_per_side": source_u,
        "source_readback_d_log_per_side": source_d,
        "J_B_source_u_formula": "t1 / 10",
        "J_B_source_d_formula": "-t1 / 10",
        "beta_u_diag_B_source_formula": "t1 / 10",
        "beta_d_diag_B_source_formula": "-t1 / 10",
        "source_readback_u_log_per_side_formula": "beta_u_diag_B_source * B_ord",
        "source_readback_d_log_per_side_formula": "beta_d_diag_B_source * B_ord",
        "pure_B_certificates": {
            "center_entry_u": source_u[1],
            "center_entry_d": source_d[1],
            "endpoint_sum_u": source_u[0] + source_u[2],
            "endpoint_sum_d": source_d[0] + source_d[2],
            "J_B_from_endpoint_u": (source_u[2] - source_u[0]) / 2.0,
            "J_B_from_endpoint_d": (source_d[2] - source_d[0]) / 2.0,
            "dot_u_over_norm": sum(u * b for u, b in zip(source_u, b_ord, strict=True)) / b_norm_sq,
            "dot_d_over_norm": sum(d * b for d, b in zip(source_d, b_ord, strict=True)) / b_norm_sq,
        },
        "off_canonical_boundary": {
            "arbitrary_P_transport_closed": False,
            "reason": (
                "This payload is evaluated on the selected public class emitted by OPH axioms + P. "
                "It does not classify all public quark frame classes or prove an arbitrary-P source-payload family."
            ),
        },
        "notes": [
            "This is a constructive data-bearing payload, not a placeholder shell.",
            "It uses the public exact selected-class output as theorem input, not a reference fit.",
            "Issue #212 still requires a separate arbitrary-P transport theorem before this can be promoted to an off-canonical evaluator family.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the selected-public-class quark D12 source payload.")
    parser.add_argument("--public-yukawa", default=str(DEFAULT_PUBLIC_YUKAWA))
    parser.add_argument("--t1-law", default=str(DEFAULT_T1_LAW))
    parser.add_argument("--source-readback", default=str(DEFAULT_SOURCE_READBACK))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        _load_json(Path(args.public_yukawa)),
        _load_json(Path(args.t1_law)),
        _load_json(Path(args.source_readback)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
