#!/usr/bin/env python3
"""Emit the shared browser/runtime contract for the P-driven quark evaluator.

Chain role: keep the current off-canonical quark slider surface synchronized
between the Python runtime and OPH Lab without promoting it past its live math
status.

Mathematics: the contract records the reduced candidate evaluator: exact
selected-class masses at the canonical anchor, candidate alpha-driven
``sigma_u(P), sigma_d(P)`` motion, affine sector means, and centered even-log
readout.

OPH-derived inputs: current edge-statistics bridge, odd-response, and pure-B
source-value artifacts are read only to decide whether theorem promotion is
allowed. With the live artifacts, promotion remains blocked.

Output: a browser-safe evaluator contract that can be mirrored by OPH Lab and
checked in tests.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p_driven_flavor_candidate import build_shared_p_driven_evaluator_contract


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EDGE_STATS = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"
DEFAULT_ODD_RESPONSE = ROOT / "particles" / "runs" / "flavor" / "quark_odd_response_law.json"
DEFAULT_PURE_B_VALUES = ROOT / "particles" / "runs" / "flavor" / "quark_diagonal_common_gap_shift_source_values.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_p_driven_shared_evaluator_contract.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_optional(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _closed_or_status(payload: dict[str, Any] | None, *keys: str) -> str | None:
    if payload is None:
        return None
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return str(value)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the shared P-driven quark evaluator contract.")
    parser.add_argument("--edge-stats", default=str(DEFAULT_EDGE_STATS))
    parser.add_argument("--odd-response", default=str(DEFAULT_ODD_RESPONSE))
    parser.add_argument("--pure-b-values", default=str(DEFAULT_PURE_B_VALUES))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    edge_stats = _load_optional(Path(args.edge_stats))
    odd_response = _load_optional(Path(args.odd_response))
    pure_b_values = _load_optional(Path(args.pure_b_values))
    contract = build_shared_p_driven_evaluator_contract(
        edge_statistics_bridge_status=_closed_or_status(edge_stats, "bridge_status", "proof_status"),
        odd_response_proof_status=_closed_or_status(odd_response, "proof_status", "status"),
        pure_b_source_status=_closed_or_status(pure_b_values, "proof_status", "status"),
    )
    contract["generated_utc"] = _timestamp()
    contract["input_artifacts"] = {
        "edge_statistics": None if edge_stats is None else edge_stats.get("artifact"),
        "odd_response": None if odd_response is None else odd_response.get("artifact"),
        "pure_b_source_values": None if pure_b_values is None else pure_b_values.get("artifact"),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
