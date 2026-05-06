#!/usr/bin/env python3
"""Tests for the source-facing Thomson spectral transport gate."""

from __future__ import annotations

from thomson_spectral_transport import (
    build_source_transport_interval_certificate,
    blocked_missing_source_transport,
    validate_source_transport_payload,
)


def _budget() -> dict:
    return {"bound_interval": {"lo": "0", "hi": "1e-30"}}


def _source_measure() -> dict:
    return {
        "artifact": "oph_qcd_ward_projected_hadronic_spectral_measure",
        "finite_volume_levels": [
            {
                "ensemble_id": "ens0",
                "channel": "U1_Q",
                "levels": [{"level_id": "rho0", "s": "1.0", "energy": "1.0", "weight": "1.0"}],
            }
        ],
        "ward_projected_residues": [
            {"level_id": "rho0", "residue": "0.25", "current_normalization": "Q=T3+Y"}
        ],
        "current_normalization": "Q=T3+Y",
        "rho_had_or_measure": {
            "representation": "primitive_spectral_measure",
            "support_variable": "s",
            "pushforward_rule": "certified finite-volume continuum pushforward",
            "positivity_status": "certified_positive",
        },
        "transport_moment_certificate": {
            "kernel": "mZ(P)^2/(3*pi*s*(s+mZ(P)^2))",
            "Delta_had_image": {"lo": "4.30", "hi": "4.40"},
            "quadrature_error_bound": "1e-40",
            "tail_bound": "1e-40",
        },
        "systematics": {
            "statistical_budget": _budget(),
            "continuum_budget": _budget(),
            "finite_volume_budget": _budget(),
            "chiral_budget": _budget(),
            "current_matching_budget": _budget(),
            "quadrature_budget": _budget(),
            "endpoint_remainder_budget": _budget(),
        },
        "guards": {
            "stable_channel_only": False,
            "surrogate_hadron_artifact": False,
            "compare_only_external_endpoint": False,
        },
    }


def _valid_payload() -> dict:
    return {
        "artifact": "oph_source_ward_projected_thomson_transport",
        "source_only": True,
        "source_family_id": "d10_running_tree",
        "current": "U1_Q",
        "scheme": {
            "same_subtraction_as_a0": True,
            "scheme_id": "d10_u1q_thomson_v1",
            "normalization_convention": "Q=T3+Y",
        },
        "interval_backend": {
            "theorem_grade": True,
            "directed_outward_rounding": True,
            "library": "arb",
            "certificate": "arb-directed-outward-proof",
        },
        "p_interval": {"lo": "1.6308", "hi": "1.6311"},
        "endpoint_map": {
            "alpha_inv_image": {"lo": "136", "hi": "138"},
            "derivative_abs_bound": "5",
            "transport_error_bound": "1e-30",
            "components": {
                "a0_image": {"lo": "128.3", "hi": "128.4"},
                "Delta_lep_image": {"lo": "4.30", "hi": "4.31"},
                "Delta_had_image": {"lo": "4.30", "hi": "4.40"},
                "Delta_EW_image": {"lo": "0", "hi": "0.01"},
                "R_Q_image": {"lo": "0.03", "hi": "0.05"},
            },
        },
        "source_measure": _source_measure(),
        "delta_EW": {"zero_theorem": "declared_scheme_zero"},
        "fixed_point_certificate": {
            "self_map_pass": True,
            "uniqueness_pass": True,
            "G_image": {"lo": "1.6308", "hi": "1.6311"},
            "contraction_kappa": "0.001",
        },
    }


def test_missing_source_transport_blocks_promotion() -> None:
    result = blocked_missing_source_transport()

    assert result["status"] == "blocked_source_spectral_measure_missing"
    assert result["promotion_allowed"] is False
    assert "required_field_missing:source_measure" in result["reasons"]


def test_source_transport_rejects_hidden_alpha_compare_keys() -> None:
    payload = _valid_payload()
    payload["compare_alpha_inv"] = "137.035999177"

    result = validate_source_transport_payload(payload)

    assert result.promotion_allowed is False
    assert any(reason.startswith("forbidden_external_or_compare_key") for reason in result.reasons)


def test_source_transport_requires_scheme_and_fixed_point_certificate() -> None:
    payload = _valid_payload()
    payload["scheme"] = {"same_subtraction_as_a0": False}
    payload["fixed_point_certificate"]["uniqueness_pass"] = False

    result = validate_source_transport_payload(payload)

    assert result.promotion_allowed is False
    assert "scheme_not_locked_to_a0" in result.reasons
    assert "fixed_point_uniqueness_missing" in result.reasons


def test_complete_source_transport_contract_can_promote() -> None:
    result = validate_source_transport_payload(_valid_payload())

    assert result.status == "source_transport_interval_certificate_satisfied"
    assert result.promotion_allowed is True


def test_boolean_only_source_transport_no_longer_promotes() -> None:
    payload = {
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

    result = validate_source_transport_payload(payload)

    assert result.promotion_allowed is False
    assert "required_field_missing:source_measure" in result.reasons
    assert "required_field_missing:interval_backend" in result.reasons


def test_interval_certificate_builder_uses_source_payload_not_compare_alpha() -> None:
    certificate = build_source_transport_interval_certificate(_valid_payload())

    assert certificate["promotion_allowed"] is True
    assert certificate["external_inputs_used"] is False
    assert certificate["certified_intervals"]["alpha_interval"]["lo"].startswith("0.0072")
    assert "CODATA" not in str(certificate)


def test_interval_certificate_rejects_non_self_map() -> None:
    payload = _valid_payload()
    payload["p_interval"] = {"lo": "1.0", "hi": "1.1"}

    certificate = build_source_transport_interval_certificate(payload)

    assert certificate["promotion_allowed"] is False
    assert "fixed_point_self_map_failed" in certificate["reasons"]
