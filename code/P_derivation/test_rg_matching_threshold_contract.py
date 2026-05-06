#!/usr/bin/env python3
"""Validate the RG matching and threshold constructive contract."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "rg_matching_threshold_contract.py"
OUTPUT = ROOT / "runtime" / "rg_matching_threshold_contract_current.json"


def test_rg_matching_threshold_contract_is_declared_and_nonpromoting() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_rg_matching_threshold_contract"
    assert payload["github_issue"] == 32
    assert payload["status"] == "closed_declared_convention_contract_not_rg_matching_theorem"
    assert payload["promotion_allowed"] is False
    assert payload["github_issue_state"] == "closed"
    assert payload["worker_result_policy"]["obstruction_only_result_allowed"] is False
    assert payload["closure_gate"]["closable_now"] is True
    assert payload["closure_gate"]["closed_as"] == "declared_convention_contract"
    object_ids = {item["id"] for item in payload["constructive_objects"]}
    assert object_ids == {
        "scheme_lock",
        "threshold_map",
        "beta_provenance_table",
        "matching_interval_composition_certificate",
    }
    assert "using_threshold_choices_as_hidden_fit_parameters" in payload["forbidden_promotions"]
