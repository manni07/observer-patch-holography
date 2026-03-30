#!/usr/bin/env python3
"""Validate the decisive charged end-to-end non-closure theorem artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_end_to_end_impossibility_theorem.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_end_to_end_impossibility_theorem.json"


def test_charged_lane_is_not_end_to_end_closed_on_live_corpus() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_charged_end_to_end_impossibility_theorem"
    assert payload["verdict"] == "no_current_corpus_end_to_end_closure"
    assert payload["closure_now"] is False
    assert payload["charged_public_masses_emitted"] is False
    assert payload["operator_side_no_go"]["theorem_grade_C_hat_e_available_now"] is False
    assert payload["operator_side_no_go"]["exact_missing_theorem"] == "oph_generation_bundle_branch_generator_splitting"
    assert payload["operator_side_no_go"]["exact_missing_clause"] == "compression_descendant_commutator_vanishes_or_is_uniformly_quadratic_small_after_central_split"
    assert payload["minimal_operator_extension"]["id"] == "central_split_quadratic_commutator_transfer"
    assert payload["minimal_operator_extension"]["current_corpus_contains_theorem"] is False
    assert payload["absolute_anchor_no_go"]["exact_missing_object"] == "charged_absolute_anchor_A_ch"
    assert payload["absolute_anchor_no_go"]["theorem_grade_A_ch_available_now"] is False
    assert payload["absolute_anchor_no_go"]["no_replacement_law_on_current_surface"] is True
    assert payload["exact_irreducible_chain"][1]["id"] == "charged_absolute_anchor_A_ch"
    assert payload["future_symbolic_forward_surface"]["if_A_ch_exists"]["g_e"] == "exp(A_ch)"
    assert "m_e" in payload["theorem_forbid_emit_now"]
