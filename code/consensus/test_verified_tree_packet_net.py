#!/usr/bin/env python3
"""Tests for the verified tree packet-net repair domain."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import export_verified_tree_packet_net as domain  # noqa: E402


def test_tree_packet_domain_checks_close() -> None:
    payload = domain.build_payload()
    checks = payload["theorem_checks"]
    assert checks["total_states_checked"] == 3**4 * 2**4
    assert checks["repair_completeness"] is True
    assert checks["strict_lyapunov_descent"] is True
    assert checks["unique_terminal_normal_form"] is True
    assert checks["max_terminal_count_seen"] == 1


def test_exported_payload_roundtrips(tmp_path: Path) -> None:
    out = tmp_path / "verified_tree_packet_net_domain.json"
    assert domain.main.__module__ == "export_verified_tree_packet_net"
    payload = domain.build_payload()
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact"] == "oph_verified_tree_packet_net_domain"
    assert loaded["issue"] == 238
    assert loaded["petz_domain"]["cptp"] is True
    assert loaded["petz_domain"]["support_gap_gamma_sigma"] > 0.0
    assert loaded["petz_domain"]["trace_norm_contractive"] is True
    assert loaded["quotient_compatibility"]["descends_to_quotient"] is True
    assert "quotient normal form" in loaded["quotient_compatibility"]["physical_law_use"]
