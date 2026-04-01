#!/usr/bin/env python3
"""Guard the charged uncentered trace-lift scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_uncentered_trace_lift_scaffold.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_uncentered_trace_lift_scaffold.json"


def test_charged_uncentered_trace_lift_scaffold() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_charged_uncentered_trace_lift_scaffold"
    assert payload["exact_missing_object"] == "refinement_stable_uncentered_trace_lift"
    assert payload["upstream_prerequisites"]["promotion_theorem"] == "oph_generation_bundle_branch_generator_splitting"
    assert payload["upstream_prerequisites"]["smaller_upstream_clause"] == (
        "compression_descendant_commutator_vanishes_or_is_uniformly_quadratic_small_after_central_split"
    )
    assert payload["upstream_prerequisites"]["current_waiting_set"]["mandatory_package_b"]["id"] == "refinement_stable_uncentered_trace_lift"
    assert payload["internal_scalarization"]["artifact_ref"] == (
        "code/particles/runs/leptons/charged_uncentered_trace_lift_cocycle_reduction.json"
    )
    assert payload["internal_scalarization"]["exact_descended_scalar_artifact_ref"] == (
        "code/particles/runs/leptons/charged_mu_physical_descent_reduction.json"
    )
    assert payload["internal_scalarization"]["irreducible_new_degree_of_freedom"] == (
        "scalar affine cocycle primitive mu"
    )
    assert payload["canonical_formula_on_fill"]["A_ch"].startswith("mu = (1/3)")
    assert payload["induced_objects"]["charged_absolute_anchor"] == "charged_absolute_anchor_A_ch"
