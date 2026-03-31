#!/usr/bin/env python3
"""Guard the split UV/BW scaffolds."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXTRACTION = ROOT / "particles" / "uv" / "derive_bw_scaling_limit_cap_pair_extraction_scaffold.py"
RIGIDITY = ROOT / "particles" / "uv" / "derive_bw_ordered_cut_pair_rigidity_scaffold.py"
RUNS = ROOT / "particles" / "runs" / "uv"


def _run(script: Path) -> dict:
    output = RUNS / script.name.replace(".py", ".json")
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    return json.loads(output.read_text(encoding="utf-8"))


def test_scaling_limit_cap_pair_extraction_scaffold() -> None:
    payload = _run(EXTRACTION)
    assert payload["artifact"] == "oph_bw_scaling_limit_cap_pair_extraction_scaffold"
    assert payload["exact_missing_object"] == "scaling_limit_cap_pair_extraction"
    assert payload["precise_missing_object_name"] == "canonical_scaling_cap_pair_realization_from_transported_cap_marginals"
    assert payload["theorem_contract_name"] == "conditional_scaling_limit_cap_pair_extraction_theorem"
    assert "projectively_compatible_transported_cap_marginal_family" in payload["fills_contract_witnesses"]
    assert payload["remaining_missing_emitted_witness"] == "vanishing_carried_collar_schedule_on_fixed_local_collars"
    assert payload["remaining_missing_emitted_witness_formula"].startswith("eta_{n,m,delta} = r_FR")
    assert payload["smaller_remaining_raw_datum"] == "fixed_local_collar_markov_faithfulness_datum"
    assert payload["missing_input_witnesses"] == ["vanishing_carried_collar_schedule_on_fixed_local_collars"]
    assert payload["follow_on_object"]["id"] == "ordered_null_cut_pair_rigidity"


def test_ordered_cut_pair_rigidity_scaffold() -> None:
    payload = _run(RIGIDITY)
    assert payload["artifact"] == "oph_bw_ordered_cut_pair_rigidity_scaffold"
    assert payload["exact_missing_object"] == "ordered_null_cut_pair_rigidity"
    assert payload["symbolic_disk_halfline_witness"]["solution_dimension"] == 1
