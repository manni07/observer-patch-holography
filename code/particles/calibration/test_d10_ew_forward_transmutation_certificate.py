#!/usr/bin/env python3
"""Validate the D10 forward transmutation certificate artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
FAMILY_SCRIPT = ROOT / "particles" / "calibration" / "derive_d10_ew_observable_family.py"
SOURCE_PAIR_SCRIPT = ROOT / "particles" / "calibration" / "derive_d10_ew_source_transport_pair.py"
SCRIPT = ROOT / "particles" / "calibration" / "derive_d10_ew_forward_transmutation_certificate.py"
OUTPUT = ROOT / "particles" / "runs" / "calibration" / "d10_ew_forward_transmutation_certificate.json"


def test_d10_forward_transmutation_certificate_is_non_circular_and_source_consistent() -> None:
    subprocess.run([sys.executable, str(FAMILY_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SOURCE_PAIR_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_d10_ew_forward_transmutation_certificate"
    assert payload["status"] == "closed_forward_p_to_t_map"
    assert payload["object_id"] == "EWForwardTransmutationCertificate_D10"

    notation = payload["notation_split"]
    assert notation["beta_ratio_EW"]["value"] == 0.5385291530498766
    assert notation["beta_transmutation_EW"]["value"] == 4

    core = payload["forward_core_solution"]
    assert abs(core["alpha_u"] - 0.04112498041477454) < 1.0e-18
    assert abs(core["t_unified"] - 1.6235491507854898) < 1.0e-15
    assert abs(core["t2_mz_run"] - 1.3335192143600498) < 1.0e-15
    assert abs(core["t3_mz_run"] - 4.67176653937017) < 1.0e-14
    assert abs(core["t_transmutation"] - 38.195673552967165) < 1.0e-12

    source = payload["source_only_reconstruction"]
    assert abs(source["alpha_u_from_source"] - core["alpha_u"]) < 1.0e-18
    assert abs(source["t_unified_from_source"] - core["t_unified"]) < 1.0e-15
    assert abs(source["t_transmutation_from_source"] - core["t_transmutation"]) < 1.0e-12
    assert abs(source["v_from_source_transmutation_gev"] - core["v_report_gev"]) < 1.0e-12

    checks = payload["forward_checks"]
    assert abs(checks["pixel_residual"]) < 1.0e-15
    assert abs(checks["mz_fixed_point_residual_gev"]) < 1.0e-12
    assert abs(checks["alpha_u_source_vs_core_residual"]) < 1.0e-18
    assert abs(checks["t_transmutation_source_vs_core_residual"]) < 1.0e-12
