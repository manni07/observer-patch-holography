#!/usr/bin/env python3
"""Closed-form one-loop Thomson transport kernels."""

from __future__ import annotations

from decimal import Decimal, localcontext

from interval_backend import DecimalIntervalBackend, Interval
from paper_math import _dec, decimal_pi


def one_loop_integral_closed(z: Decimal | int | str | float, *, precision: int = 80) -> Decimal:
    """Evaluate int_0^1 x(1-x) log(1 + z x(1-x)) dx in closed form."""
    with localcontext() as ctx:
        ctx.prec = precision
        z_dec = _dec(z)
        if z_dec <= 0:
            raise ValueError("z must be positive")
        one = Decimal(1)
        a = z_dec / Decimal(4)
        sqrt_a = a.sqrt()
        sqrt_one_plus_a = (one + a).sqrt()
        asinh_sqrt_a = (sqrt_a + sqrt_one_plus_a).ln()
        return +(
            -Decimal(5) / Decimal(18)
            + one / (Decimal(6) * a)
            + ((Decimal(2) * a - one) * sqrt_one_plus_a * asinh_sqrt_a)
            / (Decimal(6) * a * sqrt_a)
        )


def one_loop_kernel_closed(
    q_scale: Decimal | int | str | float,
    mass: Decimal | int | str | float,
    charge_squared: Decimal | int | str | float,
    multiplicity: Decimal | int | str | float,
    *,
    precision: int = 80,
) -> Decimal:
    """Evaluate the closed-form one-loop inverse-alpha transport kernel."""
    with localcontext() as ctx:
        ctx.prec = precision
        q = _dec(q_scale)
        m = _dec(mass)
        if q <= 0 or m <= 0:
            raise ValueError("q_scale and mass must be positive")
        z = (q * q) / (m * m)
        pi = decimal_pi(precision + 8)
        return +(Decimal(2) * _dec(multiplicity) * _dec(charge_squared) / pi * one_loop_integral_closed(z, precision=precision))


def one_loop_kernel_closed_interval(
    q_scale: Interval,
    mass: Interval,
    charge_squared: Decimal | int | str | float,
    multiplicity: Decimal | int | str | float,
    *,
    precision: int = 96,
) -> Interval:
    """Conservative Decimal interval enclosure for the positive kernel.

    For positive q and m, the kernel is monotone increasing in z=(q/m)^2.  The
    interval therefore evaluates the two endpoint ratios and pads the result
    through the DecimalIntervalBackend.
    """
    if q_scale.lo <= 0 or mass.lo <= 0:
        raise ValueError("q_scale and mass intervals must be positive")
    backend = DecimalIntervalBackend(precision=precision)
    with localcontext() as ctx:
        ctx.prec = precision
        z_lo = (q_scale.lo * q_scale.lo) / (mass.hi * mass.hi)
        z_hi = (q_scale.hi * q_scale.hi) / (mass.lo * mass.lo)
        k_lo = one_loop_kernel_closed(z_lo.sqrt(), Decimal(1), charge_squared, multiplicity, precision=precision)
        k_hi = one_loop_kernel_closed(z_hi.sqrt(), Decimal(1), charge_squared, multiplicity, precision=precision)
        return backend.interval(k_lo, k_hi)
