#!/usr/bin/env python3
"""Integration test for the hadron production writeback runner."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SEQUENCE_POPULATION = ROOT / "particles" / "runs" / "hadron" / "stable_channel_sequence_population.json"
RECEIPT = ROOT / "particles" / "runs" / "hadron" / "runtime_schedule_receipt_N_therm_and_N_sep.json"
PAYLOAD = ROOT / "particles" / "runs" / "hadron" / "stable_channel_cfg_source_measure_payload.json"
RUNNER = ROOT / "particles" / "hadron" / "run_production_backend_writeback.py"


def _write_json(path: pathlib.Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _synthetic_backend_export(payload: dict) -> dict:
    backend = {"artifact": "oph_hadron_backend_raw_export_inlined", "ensembles": {}}
    for ensemble in payload["ensemble_payloads"]:
        ensemble_id = str(ensemble["ensemble_id"])
        family_index = int(ensemble["family_index"])
        t_extent = int(ensemble["T"])
        cfgs = {}
        for cfg_index, cfg_id in enumerate(ensemble["cfg_ids"]):
            sources = {}
            for src_index, src_desc in enumerate((ensemble.get("source_descriptors_by_cfg") or {}).get(cfg_id, [])):
                src_id = str(src_desc["src_id"])
                norm_src = "src0" if src_id in {"s0", "src0"} else "src1"
                m_pi = 0.05 + 0.002 * family_index + 0.0005 * cfg_index + 0.0002 * src_index
                m_n = 0.09 + 0.003 * family_index + 0.0007 * cfg_index + 0.0003 * src_index
                amp_pi = 1.0 + 0.03 * family_index + 0.01 * cfg_index + 0.005 * src_index
                amp_dir = 1.3 + 0.05 * family_index + 0.02 * cfg_index + 0.01 * src_index
                amp_ex = 0.18 + 0.01 * family_index + 0.005 * cfg_index + 0.002 * src_index
                sources[norm_src] = {
                    "coord": list(src_desc["coords"]),
                    "pi_iso": [amp_pi * math.exp(-m_pi * t) for t in range(t_extent)],
                    "N_iso_direct": [amp_dir * math.exp(-m_n * t) for t in range(t_extent)],
                    "N_iso_exchange": [amp_ex * math.exp(-(m_n + 0.01) * t) for t in range(t_extent)],
                }
            cfgs[str(cfg_id)] = {
                "trajectory_stop": 2048 + 512 * cfg_index,
                "sources": sources,
            }
        backend["ensembles"][ensemble_id] = {
            "ensemble_id": ensemble_id,
            "cfgs": cfgs,
        }
    return backend


def test_production_backend_writeback_runner_roundtrips_temp_bundle() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        sequence_population_path = tmpdir / "sequence_population.json"
        receipt_path = tmpdir / "receipt.json"
        payload_path = tmpdir / "payload.json"
        backend_path = tmpdir / "backend_input.json"
        dump_path = tmpdir / "backend_correlator_dump.production.json"
        manifest_path = tmpdir / "oph_hadron_production_backend_manifest.json"
        evaluation_path = tmpdir / "stable_channel_sequence_evaluation.json"
        closure_path = tmpdir / "hadron_production_closure_validation_report.json"
        readiness_path = tmpdir / "hadron_production_readiness_report.json"

        sequence_population = json.loads(SEQUENCE_POPULATION.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))

        _write_json(sequence_population_path, sequence_population)
        _write_json(receipt_path, receipt)
        _write_json(payload_path, payload)
        _write_json(backend_path, _synthetic_backend_export(payload))

        subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--sequence-population",
                str(sequence_population_path),
                "--receipt",
                str(receipt_path),
                "--payload",
                str(payload_path),
                "--backend-bundle",
                str(backend_path),
                "--dump-output",
                str(dump_path),
                "--manifest-output",
                str(manifest_path),
                "--evaluation-output",
                str(evaluation_path),
                "--closure-output",
                str(closure_path),
                "--readiness-output",
                str(readiness_path),
                "--n-therm",
                "2048",
                "--n-sep",
                "512",
                "--schedule-provenance",
                "temp_test_runtime_receipt",
            ],
            check=True,
            cwd=ROOT,
        )

        receipt_out = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload_out = json.loads(payload_path.read_text(encoding="utf-8"))
        dump_out = json.loads(dump_path.read_text(encoding="utf-8"))
        manifest_out = json.loads(manifest_path.read_text(encoding="utf-8"))
        evaluation_out = json.loads(evaluation_path.read_text(encoding="utf-8"))
        closure_out = json.loads(closure_path.read_text(encoding="utf-8"))
        readiness_out = json.loads(readiness_path.read_text(encoding="utf-8"))

        assert receipt_out["status"] == "receipt_filled_waiting_backend_dump"
        assert receipt_out["required_schedule_scalars"] == {"N_therm": 2048, "N_sep": 512}
        assert dump_out["artifact"] == "backend_correlator_dump.production"
        assert dump_out["production_execution"] is True
        assert manifest_out["artifact"] == "oph_hadron_production_backend_manifest"
        assert payload_out["status"] == "production_backend_dump_ingested"
        assert payload_out["smallest_constructive_missing_object"] == "oph_hadron_stable_channel_sequence_evaluator"
        assert evaluation_out["status"] == "production_measure_evaluation_complete"
        assert evaluation_out["smallest_constructive_missing_object"] == "StableChannelForwardWindowConvergence"
        assert closure_out["artifact"] == "oph_hadron_closure_validation_report"
        assert closure_out["public_unsuppression_ready"] is True
        assert closure_out["smallest_live_residual_object"] is None
        assert readiness_out["artifact"] == "oph_hadron_production_readiness_report"
        assert readiness_out["closure_status"]["public_unsuppression_ready"] is True
        assert readiness_out["publication_bundle_ready"] is False
        assert readiness_out["smallest_backend_residual_object"] == "publication-complete backend manifest provenance on the seeded family"
