#!/usr/bin/env python3
"""Validate the constructive direct-top bridge contract."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "calibration" / "derive_direct_top_bridge_contract.py"
OUTPUT = ROOT / "particles" / "runs" / "calibration" / "direct_top_bridge_contract.json"


def test_direct_top_bridge_contract_keeps_auxiliary_row_compare_only() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_direct_top_bridge_contract"
    assert payload["github_issue"] == 207
    assert payload["status"] == "constructive_conversion_contract_emitted_not_direct_top_theorem"
    assert payload["promotion_allowed"] is False
    assert payload["worker_result_policy"]["obstruction_only_result_allowed"] is False
    assert payload["current_theorem_coordinate"]["pdg_summary_id"] == "Q007TP4"
    assert payload["auxiliary_direct_top_coordinate"]["pdg_summary_id"] == "Q007TP"
    assert payload["current_theorem_coordinate"]["value_gev"] == pytest.approx(172.35235532883115)
    assert payload["auxiliary_direct_top_coordinate"]["value_gev"] == pytest.approx(172.5590883453979)
    assert payload["comparison_only_readout"]["direct_minus_current_coordinate_gev"] == pytest.approx(
        0.20673301656675,
        abs=1.0e-12,
    )
    assert payload["comparison_only_readout"]["within_combined_one_sigma"] is True
    assert payload["closure_gate"]["closable_now"] is False
    object_ids = {item["id"] for item in payload["constructive_objects"]}
    assert "cross_section_to_direct_top_response_kernel" in object_ids
    assert "direct_top_uncertainty_propagation" in object_ids
    assert "Q007TP_direct_top_central_value_as_calibration_input" in payload["forbidden_solver_inputs"]
