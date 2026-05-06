#!/usr/bin/env python3
"""Tests for closed-form one-loop Thomson kernels."""

from __future__ import annotations

from decimal import Decimal

from paper_math import PaperMathContext
from thomson_kernel_interval import one_loop_kernel_closed


def test_closed_form_matches_paper_math_exact_kernel() -> None:
    ctx = PaperMathContext(precision=50, su2_cutoff=4, su3_cutoff=4)
    q = Decimal("91.1876")
    mass = Decimal("0.1056583755")

    direct = one_loop_kernel_closed(q, mass, Decimal(1), Decimal(1), precision=70)
    paper = ctx.fermion_transport_kernel_exact(q, mass, Decimal(1), Decimal(1))

    assert abs(direct - paper) < Decimal("1e-55")


def test_simpson_audit_is_not_the_exact_kernel_for_large_ratios() -> None:
    ctx = PaperMathContext(precision=50, su2_cutoff=4, su3_cutoff=4)
    exact = ctx.fermion_transport_kernel_exact(Decimal("1000"), Decimal("1"), Decimal(1), Decimal(1))
    simpson = ctx.fermion_transport_kernel_simpson_audit(Decimal("1000"), Decimal("1"), Decimal(1), Decimal(1))

    assert simpson > exact
    assert simpson - exact > Decimal("1e-9")
