#!/usr/bin/env python3
"""Guard the realized transported cap-local UV system artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "uv" / "derive_bw_realized_transported_cap_local_system.py"
OUTPUT = ROOT / "particles" / "runs" / "uv" / "bw_realized_transported_cap_local_system.json"


def test_bw_realized_transported_cap_local_system() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_realized_transported_cap_local_system"
    assert payload["status"] == "constructed_prelimit_system_one_emitted_witness_still_missing"
    assert payload["fills_contract_witnesses"] == [
        "reference_cap_local_test_system",
        "projectively_compatible_transported_cap_marginal_family",
        "asymptotic_transport_equivalence_certificate",
    ]
    assert payload["remaining_missing_emitted_witness"] == "vanishing_carried_collar_schedule_on_fixed_local_collars"
    assert payload["remaining_missing_witness_contract"]["formula"].startswith("eta_{n,m,delta} = r_FR")
    assert payload["smaller_remaining_raw_datum"]["id"] == "fixed_local_collar_markov_faithfulness_datum"
    assert payload["next_exact_object"]["id"] == "canonical_scaling_cap_pair_realization_from_transported_cap_marginals"
