#!/usr/bin/env python3
"""Guard the compare-only neutrino attachment-normalizer audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_normalizer_candidate_audit.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_normalizer_candidate_audit.json"


def test_neutrino_attachment_normalizer_candidate_audit() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_attachment_normalizer_candidate_audit"
    assert payload["status"] == "compare_only_normalizer_search"
    assert payload["exact_bridge_scalar_conversion"]["definition"] == "B_nu = F_nu * q_mean^p_nu"
    assert payload["exact_bridge_scalar_conversion"]["q_mean_to_p_nu"] > 0.0
    assert payload["best_simple_symmetric_candidate"]["complexity"] in (1, 2)
    assert payload["best_simple_symmetric_candidate"]["relative_error"] < 0.01
    converted = payload["best_bridge_scalar_candidate_after_exact_q_mean_factorization"]
    assert converted["formula"] == "ratio_hat^-0.5 * sum_defect^-1"
    assert converted["converted_formula"] == "(ratio_hat^-0.5 * sum_defect^-1) * q_mean^p_nu"
    assert converted["converted_relative_error"] < 0.003
    assert payload["hard_guard"]["status"] == "do_not_promote"
