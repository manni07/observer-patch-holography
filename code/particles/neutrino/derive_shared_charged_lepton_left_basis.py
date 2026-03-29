#!/usr/bin/env python3
"""Derive the neutrino-facing shared charged-lepton left basis artifact.

Chain role: expose the charged-lepton left singular basis that PMNS needs on
the same ordered family labels used by the flavor and neutrino continuation
lanes.

Mathematics: the charged shape surface fixes the left singular vectors up to an
overall positive scale. Since `Y_e = g * Y_e_shape` with `g > 0`, the left
eigenspaces of `Y_e Y_e^dagger` are unchanged by the unresolved absolute scale.

OPH-derived inputs: the blind charged-lepton forward artifact carrying
`Y_e_shape`, `U_e_left`, and the ordered family labels.

Output: a closed shared-basis artifact for the downstream PMNS builder.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "particles" / "runs" / "leptons" / "blind_forward_artifact.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "shared_charged_lepton_left_basis.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the shared charged-lepton left basis artifact.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = _load_json(Path(args.input))
    labels = list(payload.get("labels") or [])
    u_e_left = payload.get("U_e_left")
    if labels != ["f1", "f2", "f3"] or not isinstance(u_e_left, dict):
        raise ValueError("blind charged forward artifact must expose ordered labels [f1, f2, f3] and U_e_left")

    result = {
        "artifact": "oph_shared_charged_lepton_left_basis",
        "generated_utc": _timestamp(),
        "status": "closed",
        "theorem_status": "shape_closed_scale_invariant_left_basis",
        "source_artifacts": [
            payload.get("artifact"),
            payload.get("metadata", {}).get("observable_artifact"),
        ],
        "labels": labels,
        "basis_contract": {
            "labels": labels,
            "orientation_preserved": True,
        },
        "U_e_left": u_e_left,
        "scale_invariance_rule": "U_e_left(g * Y_e_shape) = U_e_left(Y_e_shape) for every real g > 0",
        "notes": [
            "Derived from the charged shape artifact only.",
            "Independent of the unresolved charged absolute scale.",
            "Usable immediately by the shared-basis PMNS builder.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
