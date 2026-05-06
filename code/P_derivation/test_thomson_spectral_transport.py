#!/usr/bin/env python3
"""Tests for the source-facing Thomson spectral transport gate."""

from __future__ import annotations

from thomson_spectral_transport import blocked_missing_source_transport, validate_source_transport_payload


def _valid_payload() -> dict:
    return {
        "artifact": "oph_source_ward_projected_thomson_transport",
        "source_only": True,
        "source_family_id": "d10_running_tree",
        "current": "U1_Q",
        "scheme": {"same_subtraction_as_a0": True},
        "rho_had": {
            "positivity_certificate": True,
            "threshold_support": True,
            "ope_tail_certificate": True,
            "quadrature_error_bound": "1e-40",
        },
        "delta_EW": {"zero_theorem": "declared_scheme_zero"},
        "fixed_point_certificate": {"self_map_pass": True, "uniqueness_pass": True},
    }


def test_missing_source_transport_blocks_promotion() -> None:
    result = blocked_missing_source_transport()

    assert result["status"] == "blocked_source_spectral_measure_missing"
    assert result["promotion_allowed"] is False
    assert "rho_had_missing" in result["reasons"]


def test_source_transport_rejects_hidden_alpha_compare_keys() -> None:
    payload = _valid_payload()
    payload["compare_alpha_inv"] = "137.035999177"

    result = validate_source_transport_payload(payload)

    assert result.promotion_allowed is False
    assert any(reason.startswith("forbidden_external_or_compare_key") for reason in result.reasons)


def test_source_transport_requires_scheme_and_fixed_point_certificate() -> None:
    payload = _valid_payload()
    payload["scheme"] = {"same_subtraction_as_a0": False}
    payload["fixed_point_certificate"] = {"self_map_pass": True, "uniqueness_pass": False}

    result = validate_source_transport_payload(payload)

    assert result.promotion_allowed is False
    assert "scheme_not_locked_to_a0" in result.reasons
    assert "fixed_point_uniqueness_missing" in result.reasons


def test_complete_source_transport_contract_can_promote() -> None:
    result = validate_source_transport_payload(_valid_payload())

    assert result.status == "source_transport_contract_satisfied"
    assert result.promotion_allowed is True
