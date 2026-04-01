#!/usr/bin/env python3
"""Validate the emitted-local singleton theorem for the quark sigma_ud orbit."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_sigma_ud_singleton_uniqueness_theorem.py"


def test_sigma_ud_singleton_uniqueness_theorem_closes_local_orbit() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_quark_sigma_ud_singleton_") as tmpdir:
        out = pathlib.Path(tmpdir) / "singleton.json"
        subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)], check=True, cwd=ROOT)
        payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_sigma_ud_singleton_uniqueness_theorem"
    assert payload["proof_status"] == "same_label_left_handed_local_orbit_singleton_closed"
    assert payload["theorem_grade_select"] is True
    assert payload["selected_sigma"]["sigma_id"] == "sigma_ref"
    assert payload["local_basis_admissibility"]["physical_admissible_count"] == 1
    assert payload["standard_rephasing_gauge_uniqueness"]["phase_constraint_rank"] == 5
    assert payload["standard_rephasing_gauge_uniqueness"]["phase_nullity"] == 1
    assert payload["standard_rephasing_gauge_uniqueness"]["standard_gauge_representative_unique"] is True
