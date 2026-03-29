#!/usr/bin/env python3
"""Validate the flavor-to-neutrino realized same-label pullback builder."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_realized_same_label_gap_defect_readback.py"


def test_realized_same_label_gap_defect_readback_closes_from_flavor_inputs() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_realized_same_label_") as tmpdir:
        tmp = pathlib.Path(tmpdir)
        source = tmp / "source.json"
        kernel = tmp / "kernel.json"
        line = tmp / "line.json"
        out = tmp / "out.json"

        source.write_text(
            json.dumps(
                {
                    "artifact": "oph_defect_weighted_majorana_edge_weight_family",
                    "upstream_exact_clause": "same_label_overlap_nonzero_on_realized_refinement_arrows",
                    "same_label_readback_origin": "realized_arrow_pullback_from_flavor_gap_and_defect_certificates",
                    "selector_center": "principal_equal_split",
                    "kernel_choice": "1-cos",
                    "same_label_defect_rule": "d_e = 1 - overlap_sq_e",
                    "raw_edge_score_rule": "q_e = sqrt(gap_e * defect_e)",
                    "centered_log_rule": "eta_e = log(q_e) - mean_f(log q_f)",
                    "base_mu_nu": 0.02671877920542088,
                    "weight_rule": "mu_e = base_mu_nu * exp(eta_e) / mean_f(exp(eta_f))",
                    "realized_same_label_arrows": ["psi12", "psi23", "psi31"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        kernel.write_text(
            json.dumps(
                {
                    "refinements": [
                        {"level": 0, "eigenvalues": [3.0, 2.0, 1.0]},
                        {"level": 1, "eigenvalues": [3.2, 1.9, 0.9]},
                    ]
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        line.write_text(
            json.dumps(
                {
                    "same_label_overlap_by_label_and_refinement_pair": [
                        {
                            "label": "f1",
                            "left_refinement_level": 0,
                            "right_refinement_level": 1,
                            "chi_diagonal_trace": {"amplitude": 0.81},
                        },
                        {
                            "label": "f2",
                            "left_refinement_level": 0,
                            "right_refinement_level": 1,
                            "chi_diagonal_trace": {"amplitude": 0.64},
                        },
                        {
                            "label": "f3",
                            "left_refinement_level": 0,
                            "right_refinement_level": 1,
                            "chi_diagonal_trace": {"amplitude": 0.49},
                        },
                    ],
                    "transport_partial_isometry_by_label_and_refinement_pair": [
                        {
                            "label": "f1",
                            "source_projector": {"real": [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
                            "target_projector": {"real": [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
                        },
                        {
                            "label": "f2",
                            "source_projector": {"real": [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]], "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
                            "target_projector": {"real": [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]], "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
                        },
                        {
                            "label": "f3",
                            "source_projector": {"real": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
                            "target_projector": {"real": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(source),
                "--family-kernel",
                str(kernel),
                "--line-lift",
                str(line),
                "--output",
                str(out),
            ],
            check=True,
            cwd=ROOT,
        )

        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["strict_smallest_exact_missing_object"] is None
        assert payload["same_label"] == {"psi12": "f1", "psi23": "f2", "psi31": "f3"}
        assert payload["complete_by_arrow"] == {"psi12": True, "psi23": True, "psi31": True}
        assert payload["same_label_overlap_sq"]["psi12"] == 0.81
        assert payload["defect_e"]["psi23"] == 0.36
        assert payload["gap_e"]["psi31"] > 0.0

