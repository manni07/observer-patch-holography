#!/usr/bin/env python3
"""Shared helpers for the off-canonical P-driven flavor candidate lane.

This module is intentionally conservative about status language.

The live corpus does not yet prove a theorem-grade off-canonical flavor kernel
or target-free sigma lift for arbitrary ``P``. The helpers here therefore do
two things explicitly:

1. thread real ``P``-dependence in from the D10 calibration family, and
2. anchor the resulting candidate lane to the exact default-universe quark
   surface so the canonical point stays exact.

TODO(issue): replace the default-universe anchor with a theorem-grade emitted
off-canonical flavor transport / sigma lift once that math is closed.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


ANCHOR_P = 1.63094
ANCHOR_ALPHA_U = 0.04112498041477454
ANCHOR_ALPHA_Y = 0.010131601067241625
ANCHOR_ALPHA2 = 0.03377843630219015
ANCHOR_ETA_SOURCE = 0.022147000871961295
ANCHOR_SIGMA_EW = -0.022147000871961295
ANCHOR_LOG_RATIO = math.log(ANCHOR_ALPHA_Y / ANCHOR_ALPHA2)

DEFAULT_EDGE_SIGMA_U = 5.578418804072826
DEFAULT_EDGE_SIGMA_D = 3.4210589139721543
EXACT_SIGMA_TARGET_U = 5.573928426395543
EXACT_SIGMA_TARGET_D = 3.296264198808688
SHARED_EVALUATOR_RHO_REFERENCE = 1.2942849363777058
SHARED_EVALUATOR_X2_REFERENCE = -0.5175863354681689
SHARED_EVALUATOR_ALPHA_EXPONENT_UP = 0.42519503064369524
SHARED_EVALUATOR_ALPHA_EXPONENT_DOWN = -0.5160176801329136
SHARED_EVALUATOR_UP_ANCHORS = [
    {"id": "up", "label": "up", "mass_gev": 0.00216},
    {"id": "charm", "label": "charm", "mass_gev": 1.273},
    {"id": "top", "label": "top", "mass_gev": 172.3523553288311},
]
SHARED_EVALUATOR_DOWN_ANCHORS = [
    {"id": "down", "label": "down", "mass_gev": 0.0047},
    {"id": "strange", "label": "strange", "mass_gev": 0.0935},
    {"id": "bottom", "label": "bottom", "mass_gev": 4.183},
]
SELECTED_CLASS_PURE_B_STATUSES = {
    "source_values_derived_from_source_emission",
    "closed_public_selected_class_source_values",
    "closed_public_selected_class_source_readback",
    "closed_public_selected_class_pure_B_source_payload",
}
OFF_CANONICAL_PURE_B_STATUS = "closed_off_canonical_pure_B_payload_family"

_BASE_T0 = np.asarray(
    [
        [1.0 + 0.0j, 0.1 + 0.2j, 0.0 + 0.1j],
        [0.1 - 0.2j, 0.7 + 0.0j, 0.2 + 0.0j],
        [0.0 - 0.1j, 0.2 + 0.0j, 0.4 + 0.0j],
    ],
    dtype=complex,
)
_BASE_T1 = np.asarray(
    [
        [1.02 + 0.0j, 0.11 + 0.19j, 0.01 + 0.09j],
        [0.11 - 0.19j, 0.69 + 0.0j, 0.18 + 0.01j],
        [0.01 - 0.09j, 0.18 - 0.01j, 0.41 + 0.0j],
    ],
    dtype=complex,
)
_BASE_HERMITIAN_LEVELS = (_BASE_T0 @ _BASE_T0.conj().T, _BASE_T1 @ _BASE_T1.conj().T)


def _encode_complex_matrix(matrix: np.ndarray) -> dict[str, list[list[float]]]:
    return {
        "real": np.real(matrix).tolist(),
        "imag": np.imag(matrix).tolist(),
    }


def _rotation12(theta: float) -> np.ndarray:
    c = math.cos(theta)
    s = math.sin(theta)
    return np.asarray(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=complex,
    )


def _rotation23(theta: float) -> np.ndarray:
    c = math.cos(theta)
    s = math.sin(theta)
    return np.asarray(
        [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c],
        ],
        dtype=complex,
    )


def _phase_diag(phi: float) -> np.ndarray:
    return np.diag([1.0 + 0.0j, np.exp(1j * phi), np.exp(-1j * phi)])


def _enforce_positive_simple_spectrum(eigenvalues: np.ndarray, minimum_gap: float = 1.0e-4) -> np.ndarray:
    values = np.sort(np.asarray(eigenvalues, dtype=float))
    if values[0] <= 1.0e-6:
        values = values + (1.0e-6 - values[0])
    for idx in range(1, len(values)):
        if values[idx] - values[idx - 1] < minimum_gap:
            values[idx] = values[idx - 1] + minimum_gap
    return values


def _matrix_sqrt_from_eigensystem(unitary: np.ndarray, eigenvalues: np.ndarray) -> np.ndarray:
    return unitary @ np.diag(np.sqrt(eigenvalues)) @ unitary.conj().T


def _ordered_gap_vectors() -> tuple[np.ndarray, np.ndarray]:
    gap_vec = np.asarray([-1.0, 0.0, 1.0], dtype=float)
    bend_vec = np.asarray([1.0, -2.0, 1.0], dtype=float)
    return gap_vec - np.mean(gap_vec), bend_vec - np.mean(bend_vec)


def d10_candidate_scalars(d10_family: dict[str, Any], d10_source_pair: dict[str, Any]) -> dict[str, float]:
    core = dict(d10_family.get("core_source", {}))
    predictive_point = dict(d10_source_pair.get("predictive_population_point", {}))
    alpha1 = float(core["alpha1_mz"])
    alpha2 = float(core["alpha2_mz"])
    alpha_y = 3.0 * alpha1 / 5.0
    eta_source = float(d10_source_pair["eta_source"])
    return {
        "p": float(d10_family.get("p", core.get("p", ANCHOR_P))),
        "alpha_u": float(core["alpha_u"]),
        "alpha_y": alpha_y,
        "alpha2": alpha2,
        "eta_source": eta_source,
        "sigma_ew": float(predictive_point.get("sigma_EW", ANCHOR_SIGMA_EW)),
        "log_ratio_y2": math.log(alpha_y / alpha2),
    }


def build_p_driven_transport_payload(d10_family: dict[str, Any], d10_source_pair: dict[str, Any]) -> dict[str, Any]:
    scalars = d10_candidate_scalars(d10_family, d10_source_pair)
    alpha_scale = scalars["alpha_u"] / ANCHOR_ALPHA_U
    eta_drive = scalars["eta_source"] / ANCHOR_ETA_SOURCE - 1.0
    log_drive = scalars["log_ratio_y2"] / ANCHOR_LOG_RATIO - 1.0
    p_drive = math.log(max(scalars["p"], 1.0e-9) / ANCHOR_P)
    sigma_drive = scalars["sigma_ew"] / ANCHOR_SIGMA_EW - 1.0 if ANCHOR_SIGMA_EW != 0.0 else 0.0
    span_scale = max(0.35, alpha_scale)
    gap_vec, bend_vec = _ordered_gap_vectors()

    refinements: list[dict[str, Any]] = []
    for level, base_h in enumerate(_BASE_HERMITIAN_LEVELS):
        base_evals, base_evecs = np.linalg.eigh(base_h)
        base_mean = float(np.mean(base_evals))
        base_centered = np.asarray(base_evals - base_mean, dtype=float)
        base_span = float(max(base_centered) - min(base_centered))
        level_bias = -0.5 if level == 0 else 0.5

        gap_coeff = base_span * (
            0.12 * eta_drive
            + 0.05 * p_drive
            + 0.03 * level_bias * log_drive
        )
        bend_coeff = base_span * (
            0.05 * log_drive
            + 0.03 * sigma_drive
            - 0.02 * eta_drive
            + 0.02 * level_bias * p_drive
        )
        centered = (
            span_scale * base_centered
            + gap_coeff * gap_vec
            + bend_coeff * bend_vec
        )
        centered = centered - np.mean(centered)
        candidate_mean = base_mean * (0.9 + 0.1 * span_scale)
        eigenvalues = _enforce_positive_simple_spectrum(candidate_mean + centered)

        theta12 = 0.22 * eta_drive + 0.05 * level_bias * p_drive
        theta23 = 0.10 * log_drive - 0.04 * level_bias * eta_drive
        phi = (0.16 + 0.04 * level) * (p_drive + 0.5 * sigma_drive)
        extra = _phase_diag(phi) @ _rotation23(theta23) @ _rotation12(theta12)
        unitary = base_evecs @ extra
        hermitian = unitary @ np.diag(eigenvalues) @ unitary.conj().T
        transport = _matrix_sqrt_from_eigensystem(unitary, eigenvalues)

        refinements.append(
            {
                "level": level,
                "transport_operator": _encode_complex_matrix(transport),
                "hermitian_descendant": _encode_complex_matrix(hermitian),
                "candidate_drive_scalars": {
                    "alpha_scale": alpha_scale,
                    "eta_drive": eta_drive,
                    "log_drive": log_drive,
                    "p_drive": p_drive,
                    "sigma_drive": sigma_drive,
                    "span_scale": span_scale,
                    "gap_coeff": gap_coeff,
                    "bend_coeff": bend_coeff,
                    "theta12": theta12,
                    "theta23": theta23,
                    "phi": phi,
                },
            }
        )

    return {
        "artifact": "oph_family_transport_kernel",
        "status": "p_driven_default_universe_anchor_candidate",
        "transport_kind": "conjugacy_class_family_kernel",
        "proof_status": "candidate_only",
        "refinements": refinements,
        "refinement_intertwiners": [
            {
                "from_level": 0,
                "to_level": 1,
                "intertwiner": _encode_complex_matrix(np.eye(3, dtype=complex)),
            }
        ],
        "metadata": {
            "candidate_kind": "d10_driven_default_universe_anchor_transport",
            "candidate_origin": "D10 electroweak source pair plus anchored flavor transport deformation",
            "d10_p": scalars["p"],
            "d10_alpha_u": scalars["alpha_u"],
            "d10_alpha_y": scalars["alpha_y"],
            "d10_alpha2": scalars["alpha2"],
            "d10_eta_source": scalars["eta_source"],
            "d10_sigma_ew": scalars["sigma_ew"],
            "d10_log_ratio_y2": scalars["log_ratio_y2"],
            "note": (
                "This is a P-driven candidate transport kernel, not a theorem-grade off-canonical flavor law. "
                "It threads real D10 P-dependence through the family transport shell and preserves the current "
                "default-universe transport surface at the anchor point. The remaining theorem debt is the "
                "target-free off-canonical flavor transport / sigma lift that would remove the anchor."
            ),
        },
    }


def anchored_sigma_pair_from_edge_candidate(
    candidate_sigma_u: float,
    candidate_sigma_d: float,
    *,
    exact_sigma_u: float = EXACT_SIGMA_TARGET_U,
    exact_sigma_d: float = EXACT_SIGMA_TARGET_D,
    default_candidate_sigma_u: float = DEFAULT_EDGE_SIGMA_U,
    default_candidate_sigma_d: float = DEFAULT_EDGE_SIGMA_D,
) -> dict[str, Any]:
    if default_candidate_sigma_u <= 0.0 or default_candidate_sigma_d <= 0.0:
        raise ValueError("default candidate sigma anchors must be positive")

    scale_u = exact_sigma_u / default_candidate_sigma_u
    scale_d = exact_sigma_d / default_candidate_sigma_d
    return {
        "sigma_u_total_log_per_side": scale_u * candidate_sigma_u,
        "sigma_d_total_log_per_side": scale_d * candidate_sigma_d,
        "anchor_scale_u": scale_u,
        "anchor_scale_d": scale_d,
        "anchor_formula_u": "sigma_u_exact(default) * sigma_u_candidate(P) / sigma_u_candidate(default)",
        "anchor_formula_d": "sigma_d_exact(default) * sigma_d_candidate(P) / sigma_d_candidate(default)",
    }


def ordered_profile_rays(rho_ord: float) -> tuple[list[float], list[float]]:
    denom = 3.0 * (1.0 + rho_ord)
    v_u = [
        -((2.0 * rho_ord) + 1.0) / denom,
        (rho_ord - 1.0) / denom,
        (rho_ord + 2.0) / denom,
    ]
    v_d = [
        -((rho_ord + 2.0) / denom),
        (1.0 - rho_ord) / denom,
        ((2.0 * rho_ord) + 1.0) / denom,
    ]
    return v_u, v_d


def sigma_to_even_logs(rho_ord: float, sigma_u: float, sigma_d: float) -> dict[str, list[float]]:
    v_u, v_d = ordered_profile_rays(rho_ord)
    return {
        "E_u_log": [sigma_u * value for value in v_u],
        "E_d_log": [sigma_d * value for value in v_d],
        "v_u": v_u,
        "v_d": v_d,
    }


def sigma_to_sector_means(
    rho_ord: float,
    x2: float,
    g_ch: float,
    sigma_u: float,
    sigma_d: float,
) -> dict[str, float]:
    sigma_seed_ud = 0.5 * (sigma_u + sigma_d)
    eta_ud = 0.5 * (sigma_u - sigma_d)
    mean_denominator = 1.0 + rho_ord - x2 * x2
    skew_denominator = 1.0 - x2 * x2 - (x2 * x2 / (1.0 + rho_ord))
    if abs(mean_denominator) <= 1.0e-12 or abs(skew_denominator) <= 1.0e-12:
        raise ValueError("current-family affine mean denominators are singular")

    a_ud = 1.0 / (2.0 * mean_denominator)
    b_ud = 1.0 / (2.0 * skew_denominator)
    log_shift_u = -(a_ud * sigma_seed_ud - b_ud * eta_ud)
    log_shift_d = -(a_ud * sigma_seed_ud + b_ud * eta_ud)
    return {
        "A_ud": a_ud,
        "B_ud": b_ud,
        "sigma_seed_ud": sigma_seed_ud,
        "eta_ud": eta_ud,
        "log_shift_u": log_shift_u,
        "log_shift_d": log_shift_d,
        "g_u": g_ch * math.exp(log_shift_u),
        "g_d": g_ch * math.exp(log_shift_d),
    }


def shared_candidate_sigmas_from_alpha_u(alpha_u: float) -> dict[str, float]:
    alpha_ratio = max(float(alpha_u), 1.0e-12) / ANCHOR_ALPHA_U
    return {
        "alpha_ratio": alpha_ratio,
        "sigma_u_total_log_per_side": EXACT_SIGMA_TARGET_U
        * math.pow(alpha_ratio, SHARED_EVALUATOR_ALPHA_EXPONENT_UP),
        "sigma_d_total_log_per_side": EXACT_SIGMA_TARGET_D
        * math.pow(alpha_ratio, SHARED_EVALUATOR_ALPHA_EXPONENT_DOWN),
    }


def shared_candidate_quark_masses_from_alpha_u(alpha_u: float) -> dict[str, Any]:
    sigmas = shared_candidate_sigmas_from_alpha_u(alpha_u)
    baseline_means = sigma_to_sector_means(
        SHARED_EVALUATOR_RHO_REFERENCE,
        SHARED_EVALUATOR_X2_REFERENCE,
        1.0,
        EXACT_SIGMA_TARGET_U,
        EXACT_SIGMA_TARGET_D,
    )
    baseline_logs = sigma_to_even_logs(
        SHARED_EVALUATOR_RHO_REFERENCE,
        EXACT_SIGMA_TARGET_U,
        EXACT_SIGMA_TARGET_D,
    )
    current_means = sigma_to_sector_means(
        SHARED_EVALUATOR_RHO_REFERENCE,
        SHARED_EVALUATOR_X2_REFERENCE,
        1.0,
        sigmas["sigma_u_total_log_per_side"],
        sigmas["sigma_d_total_log_per_side"],
    )
    current_logs = sigma_to_even_logs(
        SHARED_EVALUATOR_RHO_REFERENCE,
        sigmas["sigma_u_total_log_per_side"],
        sigmas["sigma_d_total_log_per_side"],
    )

    up_sector = []
    for idx, anchor in enumerate(SHARED_EVALUATOR_UP_ANCHORS):
        log_shift = (
            current_means["log_shift_u"]
            - baseline_means["log_shift_u"]
            + current_logs["E_u_log"][idx]
            - baseline_logs["E_u_log"][idx]
        )
        up_sector.append(
            {
                **anchor,
                "baseline_mass_gev": anchor["mass_gev"],
                "mass_gev": anchor["mass_gev"] * math.exp(log_shift),
                "log_shift": log_shift,
            }
        )

    down_sector = []
    for idx, anchor in enumerate(SHARED_EVALUATOR_DOWN_ANCHORS):
        log_shift = (
            current_means["log_shift_d"]
            - baseline_means["log_shift_d"]
            + current_logs["E_d_log"][idx]
            - baseline_logs["E_d_log"][idx]
        )
        down_sector.append(
            {
                **anchor,
                "baseline_mass_gev": anchor["mass_gev"],
                "mass_gev": anchor["mass_gev"] * math.exp(log_shift),
                "log_shift": log_shift,
            }
        )

    return {
        **sigmas,
        "rho_ord": SHARED_EVALUATOR_RHO_REFERENCE,
        "x2": SHARED_EVALUATOR_X2_REFERENCE,
        "up_sector": up_sector,
        "down_sector": down_sector,
    }


def build_shared_p_driven_evaluator_contract(
    *,
    edge_statistics_bridge_status: str | None = None,
    odd_response_proof_status: str | None = None,
    pure_b_source_status: str | None = None,
) -> dict[str, Any]:
    blockers = ["default_universe_anchor_not_removed"]
    if edge_statistics_bridge_status != "closed":
        blockers.append("edge_statistics_bridge_not_closed")
    if odd_response_proof_status != "closed":
        blockers.append("off_canonical_odd_response_not_closed")
    if pure_b_source_status == OFF_CANONICAL_PURE_B_STATUS:
        pass
    elif pure_b_source_status in SELECTED_CLASS_PURE_B_STATUSES:
        blockers.append("off_canonical_pure_B_payload_family_not_closed")
    else:
        blockers.append("pure_B_source_payload_not_closed")

    default_surface = shared_candidate_quark_masses_from_alpha_u(ANCHOR_ALPHA_U)
    return {
        "artifact": "oph_quark_p_driven_shared_evaluator_contract",
        "proof_status": "candidate_only",
        "runtime_status": "shared_candidate_evaluator",
        "public_promotion_allowed": False,
        "theorem_grade_closure": len(blockers) == 0,
        "promotion_blockers": blockers,
        "scope": (
            "Browser-safe off-canonical quark motion contract matching the repo-side reduced "
            "candidate evaluator. This is not the theorem-grade arbitrary-P flavor closure."
        ),
        "input_statuses": {
            "edge_statistics_bridge_status": edge_statistics_bridge_status,
            "odd_response_proof_status": odd_response_proof_status,
            "pure_b_source_status": pure_b_source_status,
        },
        "evaluator_constants": {
            "rho_ord": SHARED_EVALUATOR_RHO_REFERENCE,
            "x2": SHARED_EVALUATOR_X2_REFERENCE,
            "alpha_u_reference": ANCHOR_ALPHA_U,
            "sigma_u_reference": EXACT_SIGMA_TARGET_U,
            "sigma_d_reference": EXACT_SIGMA_TARGET_D,
            "alpha_exponent_up": SHARED_EVALUATOR_ALPHA_EXPONENT_UP,
            "alpha_exponent_down": SHARED_EVALUATOR_ALPHA_EXPONENT_DOWN,
            "up_anchors": SHARED_EVALUATOR_UP_ANCHORS,
            "down_anchors": SHARED_EVALUATOR_DOWN_ANCHORS,
        },
        "formulas": {
            "sigma_u(P)": "sigma_u_reference * (alpha_U(P) / alpha_u_reference) ** alpha_exponent_up",
            "sigma_d(P)": "sigma_d_reference * (alpha_U(P) / alpha_u_reference) ** alpha_exponent_down",
            "sector_means": "same affine mean readback as p_driven_flavor_candidate.sigma_to_sector_means",
            "centered_even_logs": "same ordered profile rays as p_driven_flavor_candidate.sigma_to_even_logs",
            "mass_readout": "m_i(P) = m_i(anchor) * exp(delta mean + delta centered even log)",
        },
        "default_anchor_check": {
            "alpha_u": ANCHOR_ALPHA_U,
            "sigma_u_total_log_per_side": default_surface["sigma_u_total_log_per_side"],
            "sigma_d_total_log_per_side": default_surface["sigma_d_total_log_per_side"],
            "up_sector": default_surface["up_sector"],
            "down_sector": default_surface["down_sector"],
        },
        "notes": [
            "The exact default-universe masses are still anchor values, not arbitrary-P theorem emissions.",
            "This contract exists to prevent browser/runtime drift while the theorem-grade off-canonical lane remains open.",
            "Closing issue #212 still requires replacing this candidate contract with emitted off-canonical sigma and pure-B data.",
            "Selected-class pure-B payload values do not by themselves close the arbitrary-P pure-B family.",
        ],
    }
