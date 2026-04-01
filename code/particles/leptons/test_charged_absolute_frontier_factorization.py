#!/usr/bin/env python3
"""Guard the layered charged absolute-frontier factorization artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UNDERDETERMINATION_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_absolute_scale_underdetermination_theorem.py"
TRACE_LIFT_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_uncentered_trace_lift_scaffold.py"
DETERMINANT_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_determinant_line_section_extension.py"
ANCHOR_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_absolute_anchor_section.py"
COCYCLE_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_uncentered_trace_lift_cocycle_reduction.py"
DESCENT_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_mu_physical_descent_reduction.py"
NO_GO_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_centered_operator_mu_phys_no_go.py"
ROUTE_SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_post_promotion_absolute_closure_route.py"
SCRIPT = ROOT / "particles" / "leptons" / "derive_charged_absolute_frontier_factorization.py"
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_absolute_frontier_factorization.json"


def test_charged_absolute_frontier_factorization() -> None:
    subprocess.run([sys.executable, str(UNDERDETERMINATION_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(TRACE_LIFT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(DETERMINANT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(ANCHOR_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(COCYCLE_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(DESCENT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(NO_GO_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(ROUTE_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_charged_absolute_frontier_factorization"
    assert payload["status"] == "layered_frontier_factorization_closed"
    assert payload["current_surface_layer"]["exact_missing_object"] == "charged_absolute_anchor_A_ch"
    assert payload["post_promotion_layer"]["irreducible_single_slot"]["id"] == "refinement_stable_uncentered_trace_lift"
    assert payload["post_promotion_layer"]["irreducible_single_slot"]["artifact_ref"] == "code/particles/runs/leptons/charged_uncentered_trace_lift_scaffold.json"
    assert payload["post_promotion_layer"]["irreducible_single_slot"]["internal_carrier"] == (
        "scalar_affine_cocycle_primitive"
    )
    assert payload["post_promotion_layer"]["irreducible_single_slot"]["internal_scalarization_artifact_ref"] == (
        "code/particles/runs/leptons/charged_uncentered_trace_lift_cocycle_reduction.json"
    )
    assert payload["post_promotion_layer"]["irreducible_single_slot"]["exact_descended_scalar"]["id"] == (
        "charged_physical_affine_scalar_mu"
    )
    assert payload["frontier_ledger"]["post_promotion_exact_descended_scalar"] == "charged_physical_affine_scalar_mu"
    assert payload["post_promotion_layer"]["promotion_only_no_go"]["theorem_id"] == (
        "charged_centered_operator_cannot_emit_mu_phys"
    )
    assert payload["frontier_ledger"]["reduction_theorem_id"] == "charged_determinant_line_reduces_to_uncentered_trace_lift"
