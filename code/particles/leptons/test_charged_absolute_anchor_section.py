#!/usr/bin/env python3
"""Guard the charged absolute-anchor scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_absolute_anchor_section.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_absolute_anchor_section.json"


def test_charged_absolute_anchor_section() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_charged_absolute_anchor_section"
    assert payload["exact_missing_object"] == "charged_absolute_anchor_A_ch"
    assert payload["induced_by_exact_smaller_object"] == "refinement_stable_uncentered_trace_lift"
    assert payload["induced_by_exact_smaller_object_artifact"] == "code/particles/runs/leptons/charged_uncentered_trace_lift_scaffold.json"
    assert payload["same_slot_scalarization_artifact"] == (
        "code/particles/runs/leptons/charged_uncentered_trace_lift_cocycle_reduction.json"
    )
    assert payload["exact_descended_scalar_artifact"] == (
        "code/particles/runs/leptons/charged_mu_physical_descent_reduction.json"
    )
    assert payload["upstream_prerequisite"]["current_status"]["mandatory_package_b"]["id"] == "refinement_stable_uncentered_trace_lift"
    assert payload["hard_rejections"]["d12_compare_only_target"]["status"] == "compare_only_not_theorem"
    assert payload["covariance_contract"] == "A_ch(logm + c*(1,1,1)) = A_ch(logm) + c"
