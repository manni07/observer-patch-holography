#!/usr/bin/env python3
"""Smoke tests for the particle derivation gap ledger."""

from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_derivation_gap_ledger import build_ledger  # noqa: E402


def test_gap_ledger_keeps_compressed_trunk_claim_safe() -> None:
    ledger = build_ledger()

    assert ledger["promotion_policy"]["compressed_p_trunk_is_live_prediction_root"] is False
    assert ledger["promotion_policy"]["torus_mode_language_allowed_in_pipeline"] is False
    gap_ids = {row["id"] for row in ledger["rows"]}
    assert "d10.ward-projected-thomson-endpoint" in gap_ids
    assert "pclosure.live-codepath-adoption" in gap_ids
