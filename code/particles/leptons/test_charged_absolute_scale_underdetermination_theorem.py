#!/usr/bin/env python3
"""Validate the charged absolute-scale underdetermination theorem artifact."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_absolute_scale_underdetermination_theorem.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_absolute_scale_underdetermination_theorem.json"


def test_charged_absolute_scale_is_explicitly_underdetermined() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_charged_absolute_scale_underdetermination_theorem"
    assert payload["proof_status"] == "centered_shape_closed_absolute_scale_underdetermined"
    assert payload["public_promotion_allowed"] is False
    assert abs(payload["centered_sum_rule"]["value"]) < 1.0e-12
    assert payload["next_exact_missing_object"] == "charged_common_refinement_transport_equalizer"
    assert payload["minimal_new_theorem"]["required_new_scalar"] == "Delta_e_abs"

    compare = payload["compare_only_continuation_target"]
    assert math.isclose(compare["g_e_star"], 0.04577885783568762, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(compare["delta_e_abs_star"], 3.003986333402356, rel_tol=0.0, abs_tol=1.0e-12)
