#!/usr/bin/env python3
"""Source-facing Ward-projected Thomson endpoint validator.

This module is deliberately a gate, not a fitted endpoint solver.  It accepts a
source-emitted spectral transport payload only if the payload carries the same
D10 family/scheme identifiers as the anchor, declares a Ward-projected
hadronic spectral measure, supplies an EW remainder statement, and keeps all
external fine-structure comparison values out of the source path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FORBIDDEN_SOURCE_KEYS = {
    "CODATA",
    "NIST",
    "codata",
    "nist",
    "compare_alpha",
    "compare_alpha_inv",
    "measured_alpha",
    "measured_alpha_inv",
    "P_C",
    "S_required",
    "c_Q",
    "residual_second_order_coefficient",
    "missing_source_transport_delta_alpha_inv",
    "required_transport_delta_alpha_inv",
}


@dataclass(frozen=True)
class TransportValidation:
    status: str
    promotion_allowed: bool
    reasons: tuple[str, ...]

    def to_json(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "promotion_allowed": self.promotion_allowed,
            "reasons": list(self.reasons),
        }


def _walk_keys(payload: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key)
            full = f"{prefix}.{key_text}" if prefix else key_text
            keys.add(key_text)
            keys.add(full)
            keys.update(_walk_keys(value, full))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            keys.update(_walk_keys(value, f"{prefix}[{index}]"))
    return keys


def source_payload_forbidden_keys(payload: dict[str, Any]) -> set[str]:
    keys = _walk_keys(payload)
    return {key for key in keys if key in FORBIDDEN_SOURCE_KEYS}


def validate_source_transport_payload(payload: dict[str, Any]) -> TransportValidation:
    reasons: list[str] = []

    forbidden = sorted(source_payload_forbidden_keys(payload))
    if forbidden:
        reasons.append("forbidden_external_or_compare_key:" + ",".join(forbidden))

    if payload.get("artifact") != "oph_source_ward_projected_thomson_transport":
        reasons.append("artifact_mismatch")

    if not payload.get("source_only", False):
        reasons.append("source_only_false_or_missing")

    if payload.get("source_family_id") != "d10_running_tree":
        reasons.append("source_family_id_mismatch")

    if payload.get("current") != "U1_Q":
        reasons.append("ward_current_mismatch")

    scheme = payload.get("scheme", {})
    if not isinstance(scheme, dict) or not scheme.get("same_subtraction_as_a0", False):
        reasons.append("scheme_not_locked_to_a0")

    rho = payload.get("rho_had")
    if not isinstance(rho, dict):
        reasons.append("rho_had_missing")
    else:
        if not rho.get("positivity_certificate", False):
            reasons.append("rho_had_positivity_missing")
        if not rho.get("threshold_support", False):
            reasons.append("rho_had_threshold_support_missing")
        if not rho.get("ope_tail_certificate", False):
            reasons.append("rho_had_ope_tail_missing")
        if not rho.get("quadrature_error_bound"):
            reasons.append("rho_had_quadrature_bound_missing")

    delta_ew = payload.get("delta_EW")
    if not isinstance(delta_ew, dict):
        reasons.append("delta_EW_missing")
    elif not (delta_ew.get("zero_theorem") or delta_ew.get("source_bound")):
        reasons.append("delta_EW_zero_or_bound_missing")

    fixed_point = payload.get("fixed_point_certificate")
    if not isinstance(fixed_point, dict):
        reasons.append("fixed_point_certificate_missing")
    else:
        if not fixed_point.get("self_map_pass", False):
            reasons.append("fixed_point_self_map_missing")
        if not fixed_point.get("uniqueness_pass", False):
            reasons.append("fixed_point_uniqueness_missing")

    if reasons:
        return TransportValidation(
            status="blocked_source_transport_contract_failed",
            promotion_allowed=False,
            reasons=tuple(reasons),
        )

    return TransportValidation(
        status="source_transport_contract_satisfied",
        promotion_allowed=True,
        reasons=(),
    )


def blocked_missing_source_transport() -> dict[str, Any]:
    return TransportValidation(
        status="blocked_source_spectral_measure_missing",
        promotion_allowed=False,
        reasons=(
            "rho_had_missing",
            "delta_EW_missing",
            "fixed_point_certificate_missing",
        ),
    ).to_json()
