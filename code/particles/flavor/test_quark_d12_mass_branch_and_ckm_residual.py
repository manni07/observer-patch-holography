#!/usr/bin/env python3
"""Validate the D12 quark mass-branch and CKM closure artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_mass_branch_and_ckm_residual.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_branch_and_ckm_residual.json"


def test_quark_d12_ckm_transport_closes_on_d12_continuation_branch() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_d12_mass_branch_and_ckm_closure"
    assert payload["status"] == "d12_continuation_ckm_cp_closed_mass_value_laws_open"
    assert payload["public_promotion_allowed"] is False
    assert payload["candidate_mass_branch_from_t1_over_5"]["Delta_ud_overlap"] > 0.0
    assert payload["forward_same_label_transport"]["principal_log_exists_uniquely"] is True
    assert payload["same_label_transport_generator"]["generator_invariants"]["theta_12_K"] > 0.0
    assert payload["closure_residual"]["fro_norm"] < 1.0e-12
