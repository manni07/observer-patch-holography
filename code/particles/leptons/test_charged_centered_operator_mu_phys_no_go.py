#!/usr/bin/env python3
"""Guard the no-go theorem for mu_phys from centered operator data alone."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHYSICAL_DESCENT_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_mu_physical_descent_reduction.py"
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_centered_operator_mu_phys_no_go.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_centered_operator_mu_phys_no_go.json"


def test_charged_centered_operator_mu_phys_no_go() -> None:
    subprocess.run([sys.executable, str(PHYSICAL_DESCENT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_charged_centered_operator_mu_phys_no_go"
    assert payload["status"] == "promotion_only_absolute_scalar_no_go"
    assert payload["input_surface"]["trace_zero_by_construction"] is True
    assert payload["target_scalar"]["id"] == "charged_physical_affine_scalar_mu"
    assert payload["no_go_theorem"]["id"] == "charged_centered_operator_cannot_emit_mu_phys"
    assert "mu_phys" in payload["no_go_theorem"]["statement"]
    assert payload["remaining_exact_object_after_no_go"]["id"] == "charged_physical_affine_scalar_mu"
