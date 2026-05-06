#!/usr/bin/env python3
"""Validate the selected-class public exact quark evaluator."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_selected_class_public_exact_evaluator.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_selected_class_public_exact_evaluator.json"


def test_quark_selected_class_public_exact_evaluator_is_closed_but_not_off_canonical() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_selected_class_public_exact_evaluator"
    assert payload["proof_status"] == "closed_selected_public_class_exact_evaluator"
    assert payload["theorem_scope"] == "selected_public_physical_quark_frame_class_only"
    assert payload["public_promotion_allowed"] is True
    assert payload["arbitrary_P_off_canonical_motion_closed"] is False
    assert payload["selector"]["selected_public_physical_frame_class"]["selected_by"] == "P"
    assert payload["closure"]["minimal_exact_blocker_set"] == []
    assert payload["closure"]["global_frame_classification_claimed"] is False

    masses = payload["masses"]
    assert math.isclose(masses["u"], 0.00216, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(masses["d"], 0.0047, rel_tol=0.0, abs_tol=1.0e-12)
    assert payload["yukawas"]["forward_certified"] is True
    assert payload["yukawas"]["promotion_blockers"] == []
