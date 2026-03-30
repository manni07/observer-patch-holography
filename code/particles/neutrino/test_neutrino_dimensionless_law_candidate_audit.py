#!/usr/bin/env python3
"""Guard the compare-only neutrino candidate-law audit surface."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_dimensionless_law_candidate_audit.json"


def test_midpoint_candidate_beats_current_ratio() -> None:
    payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    current = payload["candidates"]["current_law"]["absolute_ratio_error"]
    midpoint = payload["candidates"]["midpoint_normalized_gap_defect"]["absolute_ratio_error"]
    assert midpoint < current


def test_candidate_audit_stays_compare_only() -> None:
    payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    assert payload["status"] == "compare_only_law_space_audit"
    assert payload["public_promotion_allowed"] is False

