#!/usr/bin/env python3
"""Emit the emitted-local singleton theorem for the quark sigma_ud orbit.

Chain role: close the solver-side same-label left-handed orbit when the current
local corpus already proves that only one canonical representative survives.

Mathematics: combine the local chirality-basis exclusion result with the
published standard CKM gauge on the D12 reference sheet. If only the ordered
L/L choice is physically admissible and the five-anchor standard gauge removes
all residual diagonal rephasing except the trivial global phase, then the
emitted local same-label left-handed orbit is the singleton {sigma_ref}.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sigma_ud_orbit_provider import load_sigma_ud_singleton_uniqueness_witness


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_sigma_ud_singleton_uniqueness_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the quark sigma_ud singleton uniqueness theorem artifact.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    witness = load_sigma_ud_singleton_uniqueness_witness()
    payload = {
        "artifact": "oph_quark_sigma_ud_singleton_uniqueness_theorem",
        "generated_utc": _timestamp(),
        **witness,
        "public_promotion_allowed": False,
        "notes": [
            "This theorem closes the emitted local same-label left-handed orbit only.",
            "It selects sigma_ref without manufacturing any nonlocal relative-sheet provider.",
            "The selected singleton is still the current D12 sheet, so the physical CKM-shell mismatch survives unchanged.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
