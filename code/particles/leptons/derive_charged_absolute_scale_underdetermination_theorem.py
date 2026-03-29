#!/usr/bin/env python3
"""Emit the charged absolute-scale underdetermination theorem artifact.

Chain role: record the exact theorem the current charged-lepton lane actually
proves before any future absolute-scale closure is claimed.

Mathematics: the emitted charged centered log triple determines only the shape
class modulo a common additive shift; all current charged invariants are common
shift invariant, so the linear absolute scale ``g_e`` remains open.

OPH-derived inputs: the current-family charged exact readout, the shared
absolute-scale writeback shell, and the D12 continuation compare-only bridge.

Output: a theorem artifact stating that the present charged chain determines
only the centered charged quotient class and exposing the compare-only target
``Delta_e_abs`` a future determinant-transport theorem would need to emit.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
READOUT_JSON = ROOT / "particles" / "runs" / "leptons" / "lepton_current_family_exact_readout.json"
WRITEBACK_JSON = ROOT / "particles" / "runs" / "flavor" / "charged_shared_absolute_scale_writeback.json"
CONTINUATION_JSON = ROOT / "particles" / "runs" / "leptons" / "charged_d12_continuation_followup.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "leptons" / "charged_absolute_scale_underdetermination_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged absolute-scale underdetermination theorem artifact.")
    parser.add_argument("--readout", default=str(READOUT_JSON))
    parser.add_argument("--writeback", default=str(WRITEBACK_JSON))
    parser.add_argument("--continuation", default=str(CONTINUATION_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    readout = _load_json(Path(args.readout))
    writeback = _load_json(Path(args.writeback))
    continuation = _load_json(Path(args.continuation))

    centered_logs = [float(value) for value in readout["centered_log_shape_exact"]]
    centered_sum = float(sum(centered_logs))
    stored_shared_scale = float(writeback["stored_shared_absolute_scale_raw"])
    continuation_shape = [
        float(value)
        for value in continuation["d12_continuation_pair"]["shape_singular_values_emitted"]
    ]
    g_compare_only = float(
        continuation["compare_only_shape_check_against_reference_masses"]["g_e_compare_only_needed_for_exact_absolute_masses"]
    )
    delta_abs_compare_only = float(math.log(stored_shared_scale / g_compare_only))

    artifact = {
        "artifact": "oph_charged_absolute_scale_underdetermination_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "centered_shape_closed_absolute_scale_underdetermined",
        "public_promotion_allowed": False,
        "scope": "current_family_shape_closed_absolute_scale_open",
        "same_carrier_mass_formulas": {
            "m_e": "g_e * exp(e_log_centered)",
            "m_mu": "g_e * exp(mu_log_centered)",
            "m_tau": "g_e * exp(tau_log_centered)",
            "family_operator": "Y_e(c) = exp(c) * diag(exp(E_e_log_centered))",
        },
        "emitted_centered_log_shape": centered_logs,
        "centered_sum_rule": {
            "formula": "e_log_centered + mu_log_centered + tau_log_centered = 0",
            "value": centered_sum,
        },
        "determinant_rules": {
            "shape_operator": "det(Y_e_shape) = 1",
            "physical_operator": "det(Y_e) = g_e^3",
            "common_shift_rule": "(m_e, m_mu, m_tau) -> exp(c) * (m_e, m_mu, m_tau)",
            "invariants_unchanged_under_common_shift": [
                "eta_ext",
                "sigma_ext",
                "gamma21",
                "gamma32",
                "E_e_log_centered",
                "charged ratios",
            ],
        },
        "theorem_statement": (
            "The present charged OPH chain fixes only the centered charged log class "
            "E_e_log_centered in R^3 modulo the common shift direction (1,1,1). "
            "It does not emit the absolute scalar g_e."
        ),
        "shared_budget_seed": {
            "stored_shared_absolute_scale_raw": stored_shared_scale,
            "theorem_scope": writeback.get("theorem_scope"),
            "writeback_scope": writeback.get("writeback_scope"),
        },
        "compare_only_continuation_target": {
            "status": "compare_only_not_theorem_grade",
            "g_e_star": g_compare_only,
            "delta_e_abs_star": delta_abs_compare_only,
            "delta_formula": "Delta_e_abs_star = log(stored_shared_absolute_scale_raw / g_e_star)",
            "continuation_shape_singular_values": continuation_shape,
            "forward_compare_only_masses": [g_compare_only * value for value in continuation_shape],
        },
        "next_exact_missing_object": "charged_common_refinement_transport_equalizer",
        "minimal_new_theorem": {
            "id": "charged_absolute_determinant_transport_theorem",
            "formula": "g_e = g_ch_shared * exp(-Delta_e_abs)",
            "required_new_scalar": "Delta_e_abs",
            "source": "charged operator C_hat_e together with the common-refinement transport equalizer",
            "must_be_independent_of_measured_masses": True,
        },
        "notes": [
            "This artifact records the honest closure status of the charged absolute-scale lane: the shape is emitted, the absolute normalization is not.",
            "The compare-only continuation target is useful for audit and branch repair, but it must not be promoted as an OPH-emitted charged mass theorem.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
