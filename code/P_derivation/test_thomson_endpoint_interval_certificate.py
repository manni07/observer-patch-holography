#!/usr/bin/env python3
"""Tests for the blocked fine-structure interval-certificate package."""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path

from thomson_endpoint_interval_certificate import build_interval_certificate


PACKAGE = Path(__file__).resolve().parent / "runtime" / "thomson_endpoint_package_current.json"


def test_interval_certificate_blocks_without_source_r_q() -> None:
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    certificate, r_q_contract = build_interval_certificate(package)

    assert certificate["artifact"] == "oph_fine_structure_interval_certificate"
    assert certificate["github_issue"] == 235
    assert certificate["status"] == "closed_blocker_isolated_missing_R_Q"
    assert certificate["promotion_allowed"] is False
    assert certificate["issue_235_resolution"]["exact_alpha_promoted"] is False
    assert certificate["R_Q_certificate"]["status"] == "missing_source_artifact"
    assert r_q_contract["status"] == "closed_blocker_isolated_missing_source_R_Q"
    assert r_q_contract["promotion_allowed"] is False
    assert r_q_contract["issue_235_resolution"]["first_missing_lemma"] == (
        "source-emitted same-scheme Ward-projected R_Q(P)"
    )


def test_conditional_banach_budget_is_recorded() -> None:
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    certificate, _r_q_contract = build_interval_certificate(package)
    composition = certificate["composition"]

    assert composition["banach_conditional_pass"] is True
    assert Decimal(composition["contraction_kappa_with_target_bounds"]) < Decimal(1)
    assert Decimal(composition["R_Q_prime_ceiling_if_L_B_target_holds"]) > Decimal("1000")


def test_required_residual_interval_contains_center_residual() -> None:
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    _certificate, r_q_contract = build_interval_certificate(package)

    center = Decimal(r_q_contract["required_center_at_compare_pixel"])
    image = r_q_contract["required_image_on_I_P"]
    assert Decimal(image["lo"]) < center < Decimal(image["hi"])
    assert "CODATA/NIST alpha" in r_q_contract["forbidden_inputs"]
