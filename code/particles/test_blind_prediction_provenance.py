#!/usr/bin/env python3
"""Smoke tests for the quantitative particle provenance audit."""

from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_blind_prediction_provenance import build_payload  # noqa: E402


def test_blind_prediction_provenance_records_target_use_and_open_sensitivity_gate() -> None:
    payload = build_payload()

    assert payload["artifact"] == "oph_blind_prediction_provenance_audit"
    assert payload["github_issue"] == 234
    assert payload["status"] == "provenance_ledger_emitted_convention_sensitivity_contract_open"
    assert payload["promotion_allowed"] is False
    assert payload["closure_gate"]["closable_now"] is False
    assert payload["convention_sensitivity"]["status"] == "contract_open_not_quantified"
    row_map = {row["particle_id"]: row for row in payload["rows"]}
    assert row_map["photon"]["blind_status"] == "blind_structural"
    assert row_map["w_boson"]["row_class"] == "compare_only_reproduction"
    assert row_map["electron"]["target_use"] == "target_values_used_to_anchor_current_family_witness"
    assert row_map["higgs"]["blind_status"] == "conditionally_blind_on_declared_surface"
    assert row_map["top_quark"]["row_class"] == "selected_class_exact_theorem"
    assert row_map["electron_neutrino"]["target_use"] == "no_absolute_mass_target_input"
    workflows = {workflow["id"]: workflow for workflow in payload["preregistered_blind_workflows"]}
    assert workflows["new_quantity_pre_reference_lock"]["status"] == "protocol_emitted_not_yet_exercised"
    assert workflows["convention_sensitivity_sweep"]["status"] == "blocked_on_rg_matching_threshold_contract"
