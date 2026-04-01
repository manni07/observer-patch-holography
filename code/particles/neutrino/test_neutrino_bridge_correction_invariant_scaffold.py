#!/usr/bin/env python3
"""Guard the reduced exact bridge-correction scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORRECTION_AUDIT_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_bridge_correction_candidate_audit.py"
IRREDUCIBILITY_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_irreducibility.py"
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_bridge_correction_invariant_scaffold.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_correction_invariant_scaffold.json"


def test_neutrino_bridge_correction_invariant_scaffold() -> None:
    subprocess.run([sys.executable, str(CORRECTION_AUDIT_SCRIPT)], check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, str(IRREDUCIBILITY_SCRIPT)], check=True, capture_output=True, text=True)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_bridge_correction_invariant_scaffold"
    assert payload["exact_missing_object"] == "oph_neutrino_bridge_correction_invariant"
    assert payload["parent_missing_object"] == "oph_neutrino_attachment_bridge_invariant"
    assert payload["residual_invariant_symbol"] == "C_nu"
    assert payload["internal_positive_proxy_object"]["route_id"] == "core_residual_scalar_route"
    assert payload["exact_reduction_theorem"]["bridge_reconstruction"] == "B_nu = (I_nu^0.5 * ratio_hat^0.5 * sum_defect^-1) * C_nu"
    assert payload["contract"]["must_emit"].startswith("one positive reduced bridge-correction scalar C_nu")
    assert payload["strongest_compare_only_correction_window"]["contains_compare_only_target"] is True
    assert payload["strongest_compare_only_correction_window"]["relative_half_width"] < 0.0011
    assert payload["induced_target_containing_bridge_scalar_window"]["contains_compare_only_target"] is True
    assert payload["induced_target_containing_bridge_scalar_window"]["relative_half_width"] < 0.0011
