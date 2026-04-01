#!/usr/bin/env python3
"""Run the hadron production writeback path end to end.

Chain role: execute the task-10 production dump/writeback flow from one command
so the hadron lane can move from a backend export to payload, evaluation, and
closure-report artifacts without manual step drift.

Mathematics: no new hadron theorem is claimed here; this script orchestrates the
already-defined runtime receipt, normalized backend dump, cfg/source writeback,
jackknife evaluation, and closure validator path.

OPH-derived inputs: the seeded stable-channel sequence population, cfg/source
payload shell, runtime receipt shell, and a backend export artifact.

Output: a filled receipt plus synchronized dump, manifest, payload, evaluation,
and closure-report artifacts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from particles.hadron.backend_export_bundle import load_backend_input_artifact
from particles.hadron.derive_hadron_production_readiness_report import build_readiness_report
from particles.hadron.derive_stable_channel_sequence_evaluation import build_artifact as build_sequence_evaluation
from particles.hadron.production_execution_support import (
    build_backend_manifest,
    build_production_dump,
    fill_runtime_receipt,
    ingest_dump_into_payload,
    populate_evaluation_from_dump,
)
from particles.hadron.validate_production_hadron_closure import build_closure_report


DEFAULT_SEQUENCE_POPULATION = ROOT / "particles" / "runs" / "hadron" / "stable_channel_sequence_population.json"
DEFAULT_RECEIPT = ROOT / "particles" / "runs" / "hadron" / "runtime_schedule_receipt_N_therm_and_N_sep.json"
DEFAULT_PAYLOAD = ROOT / "particles" / "runs" / "hadron" / "stable_channel_cfg_source_measure_payload.json"
DEFAULT_DUMP = ROOT / "particles" / "runs" / "hadron" / "backend_correlator_dump.production.json"
DEFAULT_MANIFEST = ROOT / "particles" / "runs" / "hadron" / "oph_hadron_production_backend_manifest.json"
DEFAULT_EVALUATION = ROOT / "particles" / "runs" / "hadron" / "stable_channel_sequence_evaluation.json"
DEFAULT_CLOSURE = ROOT / "particles" / "runs" / "hadron" / "hadron_production_closure_validation_report.json"
DEFAULT_READINESS = ROOT / "particles" / "runs" / "hadron" / "hadron_production_readiness_report.json"


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the hadron production backend writeback path.")
    parser.add_argument("--sequence-population", default=str(DEFAULT_SEQUENCE_POPULATION))
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    parser.add_argument("--payload", default=str(DEFAULT_PAYLOAD))
    parser.add_argument("--backend-bundle", required=True)
    parser.add_argument("--receipt-output", default=None)
    parser.add_argument("--payload-output", default=None)
    parser.add_argument("--dump-output", default=str(DEFAULT_DUMP))
    parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--evaluation-output", default=str(DEFAULT_EVALUATION))
    parser.add_argument("--closure-output", default=str(DEFAULT_CLOSURE))
    parser.add_argument("--readiness-output", default=str(DEFAULT_READINESS))
    parser.add_argument("--n-therm", type=int, default=None)
    parser.add_argument("--n-sep", type=int, default=None)
    parser.add_argument("--schedule-provenance", default=None)
    args = parser.parse_args()

    sequence_population = _load_json(args.sequence_population)
    receipt = _load_json(args.receipt)
    payload = _load_json(args.payload)
    backend_input = load_backend_input_artifact(args.backend_bundle)

    filled_receipt = fill_runtime_receipt(
        receipt,
        n_therm=args.n_therm,
        n_sep=args.n_sep,
        schedule_provenance=args.schedule_provenance,
    )
    dump = build_production_dump(filled_receipt, payload, backend_input)
    manifest = build_backend_manifest(
        filled_receipt,
        payload,
        backend_input,
        backend_input_path=args.backend_bundle,
    )
    payload_with_writeback = ingest_dump_into_payload(payload, dump, filled_receipt)
    evaluation_seed = build_sequence_evaluation(
        sequence_population,
        payload_with_writeback,
        filled_receipt,
    )
    evaluation = populate_evaluation_from_dump(evaluation_seed, dump)
    closure_report = build_closure_report(filled_receipt, evaluation, dump=dump)
    readiness_report = build_readiness_report(
        filled_receipt,
        payload_with_writeback,
        manifest=manifest,
        dump=dump,
        evaluation=evaluation,
        closure_report=closure_report,
    )

    receipt_output = args.receipt_output or args.receipt
    payload_output = args.payload_output or args.payload
    _write_json(receipt_output, filled_receipt)
    _write_json(args.dump_output, dump)
    _write_json(args.manifest_output, manifest)
    _write_json(payload_output, payload_with_writeback)
    _write_json(args.evaluation_output, evaluation)
    _write_json(args.closure_output, closure_report)
    _write_json(args.readiness_output, readiness_report)

    print(f"wrote {receipt_output}")
    print(f"wrote {args.dump_output}")
    print(f"wrote {args.manifest_output}")
    print(f"wrote {payload_output}")
    print(f"wrote {args.evaluation_output}")
    print(f"wrote {args.closure_output}")
    print(f"wrote {args.readiness_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
