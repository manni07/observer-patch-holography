#!/usr/bin/env python3
"""Smoke tests for the P/alpha fixed-point witness surface."""

from __future__ import annotations

from decimal import Decimal
import unittest

from alpha_gap_audit import build_alpha_gap_audit
from paper_math import PaperMathContext, build_contraction_certificate, build_fixed_point_witness
from transport_theorem_manifest import build_manifest


class FixedPointWitnessTests(unittest.TestCase):
    def test_external_alpha_maps_to_pixel_ratio(self) -> None:
        ctx = PaperMathContext(precision=24, su2_cutoff=4, su3_cutoff=4)
        alpha_inv = Decimal("128")
        p_value = ctx.p_from_inverse_alpha(alpha_inv)
        expected = ctx.outer_p_from_alpha(Decimal(1) / alpha_inv)

        self.assertEqual(p_value, expected)

    def test_witness_has_no_default_external_compare_value(self) -> None:
        witness = build_fixed_point_witness(
            precision=10,
            mode="mz_anchor",
            su2_cutoff=6,
            su3_cutoff=4,
            scan_points=8,
            max_iterations=3,
            derivative_step="0.0001",
            sample_points=1,
        )

        self.assertEqual(witness["claim_status"], "numerical_witness_not_interval_certificate")
        self.assertNotIn("external_compare_only", witness)
        self.assertGreater(Decimal(witness["finite_difference"]["max_abs_sample_slope"]), Decimal("0"))

    def test_witness_keeps_explicit_compare_value_out_of_solver_inputs(self) -> None:
        witness = build_fixed_point_witness(
            precision=10,
            mode="mz_anchor",
            su2_cutoff=6,
            su3_cutoff=4,
            scan_points=8,
            max_iterations=3,
            derivative_step="0.0001",
            sample_points=1,
            compare_alpha_inv="128",
            compare_alpha_inv_uncertainty="0.1",
        )

        self.assertEqual(witness["external_compare_only"]["alpha_inv"], "128")
        self.assertEqual(witness["external_compare_only"]["alpha_inv_standard_uncertainty"], "0.1")
        self.assertIn("fixed_point_minus_compare_alpha_inv", witness["external_compare_only"])

    def test_contraction_certificate_records_sampled_status(self) -> None:
        certificate = build_contraction_certificate(
            precision=10,
            mode="mz_anchor",
            su2_cutoff=6,
            su3_cutoff=4,
            scan_points=8,
            max_iterations=3,
            interval_half_width="0.0001",
            derivative_step="0.0001",
            sample_points=3,
        )

        self.assertEqual(certificate["claim_status"], "numerical_local_contraction_certificate")
        self.assertTrue(certificate["alpha_interval"]["bracket_changes_sign"])
        self.assertTrue(certificate["sample_contraction_observed"])
        self.assertLess(Decimal(certificate["max_abs_centered_slope"]), Decimal("1"))

    def test_alpha_gap_audit_keeps_compare_target_out_of_solver(self) -> None:
        audit = build_alpha_gap_audit(
            {
                "mode": "synthetic",
                "precision": 10,
                "alpha_inv": "10",
                "source_anchor_alpha_inv": "8",
                "p": "1.2",
                "phi": "1",
                "sqrt_pi": "2",
                "structured_running": {"total_delta_alpha_inv": "2"},
            },
            compare_alpha_inv=Decimal("11"),
            compare_alpha_inv_uncertainty=Decimal("0.1"),
        )

        self.assertEqual(audit["claim_status"], "open_transport_gap_not_full_derivation")
        self.assertEqual(audit["implemented_transport_delta_alpha_inv"], "2")
        self.assertEqual(audit["required_transport_delta_alpha_inv"], "3")
        self.assertEqual(audit["missing_transport_delta_alpha_inv"], "1")
        self.assertEqual(audit["alpha_inv_gap_sigma"], "1E+1")

    def test_transport_manifest_does_not_promote_open_theorems(self) -> None:
        manifest = build_manifest(
            {
                "mode": "synthetic",
                "precision": 10,
                "alpha_inv": "10",
                "source_anchor_alpha_inv": "8",
                "p": "1.2",
                "phi": "1",
                "sqrt_pi": "2",
                "structured_running": {"total_delta_alpha_inv": "2"},
            }
        )

        self.assertEqual(
            manifest["claim_status"],
            "missing_theorems_scaffold_not_measured_alpha_derivation",
        )
        self.assertFalse(manifest["promotion_rule"]["codata_may_enter_solver"])
        self.assertTrue(manifest["promotion_rule"]["requires_source_emitted_hadronic_spectral_density"])
        self.assertTrue(all(not theorem["promotable_to_measured_alpha"] for theorem in manifest["theorems"]))


if __name__ == "__main__":
    unittest.main()
