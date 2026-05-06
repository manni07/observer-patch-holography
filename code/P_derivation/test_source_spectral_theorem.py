#!/usr/bin/env python3
"""Tests for the Ward-projected source-spectral theorem artifact."""

from __future__ import annotations

from source_spectral_theorem import build_source_spectral_theorem


def _valid_source_payload() -> dict:
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
        "delta_EW": {"source_bound": {"lo": "0", "hi": "0"}},
        "fixed_point_certificate": {"self_map_pass": True, "uniqueness_pass": True},
    }


def test_source_spectral_theorem_blocks_without_measure_payload() -> None:
    payload = build_source_spectral_theorem()

    assert payload["artifact"] == "oph_ward_projected_source_spectral_theorem"
    assert payload["theorem_id"] == "WardProjectedHadronicSpectralEmission_Q"
    assert payload["status"] == "source_spectral_reduction_theorem_emitted_measure_payload_absent"
    assert payload["promotion_allowed"] is False
    assert payload["external_inputs_used"] is False
    assert payload["source_payload_validation"]["status"] == "blocked_source_spectral_measure_missing"
    assert payload["current_corpus_obstruction"]["production_dump_present"] is False
    assert payload["current_corpus_obstruction"]["finite_volume_levels_populated"] is False
    assert payload["conclusion"]["source_spectral_reduction_closed"] is True
    assert payload["conclusion"]["exact_alpha_emitted_from_current_corpus"] is False


def test_source_spectral_theorem_rejects_fitted_scalars() -> None:
    payload = build_source_spectral_theorem()

    assert payload["source_only_guard"]["residual_fit_allowed"] is False
    rejected = set(payload["nonidentifiability_corollary"]["fitted_scalars_rejected"])
    assert "c_Q" in rejected
    assert "S_required" in rejected
    assert "missing_source_transport_delta_alpha_inv" in rejected


def test_source_spectral_theorem_accepts_complete_source_payload_contract() -> None:
    payload = build_source_spectral_theorem(source_transport_payload=_valid_source_payload())

    assert payload["status"] == "source_spectral_payload_contract_satisfied"
    assert payload["promotion_allowed"] is True
    assert payload["source_payload_validation"]["status"] == "source_transport_contract_satisfied"
    assert payload["conclusion"]["source_transport_payload_accepted"] is True
    assert payload["conclusion"]["exact_alpha_promotion_allowed_for_supplied_payload"] is True
