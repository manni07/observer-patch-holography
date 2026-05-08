#!/usr/bin/env python3
"""Tests for the reference-architecture benchmark suite."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference_architecture_benchmark_suite as suite  # noqa: E402


def test_suite_runs_all_named_benchmarks_and_schedules() -> None:
    payload = suite.build_payload()
    assert payload["artifact"] == "oph_reference_architecture_benchmark_suite"
    assert payload["issue"] == 237
    assert payload["suite"]["total_runs"] == 9 * 6
    assert payload["phase1_architecture_pass"] is True
    assert set(payload["suite"]["benchmarks"]) == {
        "Z2-0-clean",
        "Z2-1-stale-record",
        "Z2-2-collar-flip",
        "Z2-3-double-overlap",
        "Z2-4-frustrated-cycle",
        "S3-0-clean",
        "S3-1-transposition",
        "S3-2-threecycle",
        "S3-3-mixed-class-cycle",
    }


def test_packet_closure_and_scope_boundary_are_explicit() -> None:
    payload = suite.build_payload()
    assert all(run["packet_closure"] for run in payload["runs"])
    assert all(
        run["repair_complete"] or run["residual_obstruction_detected"]
        for run in payload["runs"]
    )
    assert "continuum or gravity scaling-limit closure" in payload["scope"]["does_not_establish"]
    assert payload["benchmark_summary"]["Z2-4-frustrated-cycle"]["max_final_phi"] == 1
    assert payload["gates"]["residual_obstruction_gate"] is True


def test_exported_payload_roundtrips(tmp_path: Path) -> None:
    out = tmp_path / "reference_architecture_benchmark_suite_current.json"
    payload = suite.build_payload()
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["object_id"] == "ReferenceArchitectureBenchmarkSuite_Issue237"
    assert loaded["commands"]["run"] == "python3 code/consensus/reference_architecture_benchmark_suite.py"
    assert loaded["negative_controls"]
