#!/usr/bin/env python3
"""Guard the charged uncentered trace-lift scalar-cocycle reduction."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRACE_LIFT_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_uncentered_trace_lift_scaffold.py"
DETERMINANT_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_determinant_line_section_extension.py"
ANCHOR_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_absolute_anchor_section.py"
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_uncentered_trace_lift_cocycle_reduction.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_uncentered_trace_lift_cocycle_reduction.json"


def test_charged_uncentered_trace_lift_cocycle_reduction() -> None:
    subprocess.run([sys.executable, str(TRACE_LIFT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(DETERMINANT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(ANCHOR_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_charged_uncentered_trace_lift_cocycle_reduction"
    assert payload["status"] == "conditional_scalar_cocycle_reduction"
    assert payload["single_slot_preserved"] == "refinement_stable_uncentered_trace_lift"
    assert payload["matrix_vs_scalar_content"]["uniqueness_mod_scalar_identity"] is True
    assert payload["matrix_vs_scalar_content"]["irreducible_new_degree_of_freedom"] == (
        "scalar affine cocycle primitive mu"
    )
    assert payload["exact_descended_scalar_artifact_ref"] == (
        "code/particles/runs/leptons/charged_mu_physical_descent_reduction.json"
    )
    assert payload["scalar_cocycle_contract"]["pairwise_difference_rule"] == (
        "C_tilde_e(r') - C_tilde_e(r) = delta(r,r') I"
    )
    assert payload["equivalent_presentations_on_fill"]["affine_anchor"]["object"] == (
        "charged_absolute_anchor_A_ch"
    )
    assert payload["correspondence_on_fill"]["section_to_anchor"] == "A_ch = (1/3) * s_det"
