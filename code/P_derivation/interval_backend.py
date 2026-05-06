#!/usr/bin/env python3
"""Small Decimal interval helpers for blocked theorem-package artifacts.

This backend is intentionally conservative metadata plumbing, not a replacement
for Arb/MPFI directed rounding.  It evaluates with extra Decimal precision and
adds an explicit decimal pad after each operation.  Artifacts that use this file
must keep theorem promotion disabled until a directed-rounding backend replaces
it.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext


def _dec(value: Decimal | int | str | float) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    return Decimal(str(value))


@dataclass(frozen=True)
class Interval:
    lo: Decimal
    hi: Decimal

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError(f"invalid interval: {self.lo} > {self.hi}")

    @property
    def width(self) -> Decimal:
        return self.hi - self.lo

    @property
    def radius(self) -> Decimal:
        return (self.hi - self.lo) / Decimal(2)

    @property
    def abs_max(self) -> Decimal:
        return max(abs(self.lo), abs(self.hi))

    def contains(self, value: Decimal | int | str | float) -> bool:
        item = _dec(value)
        return self.lo <= item <= self.hi

    def subset_of(self, other: "Interval") -> bool:
        return other.lo <= self.lo and self.hi <= other.hi

    def to_json(self) -> dict[str, str]:
        return {"lo": format(self.lo, "f"), "hi": format(self.hi, "f")}


@dataclass(frozen=True)
class DualInterval:
    x: Interval
    dx: Interval


class DecimalIntervalBackend:
    """High-precision Decimal interval helper with explicit result padding."""

    def __init__(self, precision: int = 96, pad_exponent: int | None = None) -> None:
        self.precision = precision
        self.pad = Decimal(10) ** Decimal(pad_exponent if pad_exponent is not None else -(precision - 12))

    def interval(
        self,
        lo: Decimal | int | str | float,
        hi: Decimal | int | str | float | None = None,
    ) -> Interval:
        if hi is None:
            hi = lo
        return Interval(_dec(lo), _dec(hi))

    def _pad(self, value: Interval) -> Interval:
        return Interval(value.lo - self.pad, value.hi + self.pad)

    def add(self, a: Interval, b: Interval) -> Interval:
        with localcontext() as ctx:
            ctx.prec = self.precision
            return self._pad(Interval(+(a.lo + b.lo), +(a.hi + b.hi)))

    def sub(self, a: Interval, b: Interval) -> Interval:
        with localcontext() as ctx:
            ctx.prec = self.precision
            return self._pad(Interval(+(a.lo - b.hi), +(a.hi - b.lo)))

    def mul(self, a: Interval, b: Interval) -> Interval:
        with localcontext() as ctx:
            ctx.prec = self.precision
            products = (a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi)
            return self._pad(Interval(+min(products), +max(products)))

    def reciprocal(self, a: Interval) -> Interval:
        if a.lo <= 0 <= a.hi:
            raise ZeroDivisionError("interval reciprocal crosses zero")
        with localcontext() as ctx:
            ctx.prec = self.precision
            values = (Decimal(1) / a.lo, Decimal(1) / a.hi)
            return self._pad(Interval(+min(values), +max(values)))

    def div(self, a: Interval, b: Interval) -> Interval:
        return self.mul(a, self.reciprocal(b))

    def sqrt(self, a: Interval) -> Interval:
        if a.lo < 0:
            raise ValueError("sqrt interval lower endpoint is negative")
        with localcontext() as ctx:
            ctx.prec = self.precision
            return self._pad(Interval(+a.lo.sqrt(), +a.hi.sqrt()))

    def exp(self, a: Interval) -> Interval:
        with localcontext() as ctx:
            ctx.prec = self.precision
            return self._pad(Interval(+a.lo.exp(), +a.hi.exp()))

    def log(self, a: Interval) -> Interval:
        if a.lo <= 0:
            raise ValueError("log interval lower endpoint must be positive")
        with localcontext() as ctx:
            ctx.prec = self.precision
            return self._pad(Interval(+a.lo.ln(), +a.hi.ln()))

    def asinh_positive(self, a: Interval) -> Interval:
        """Return asinh(a) for a >= 0 using log(a + sqrt(1+a^2))."""
        if a.lo < 0:
            raise ValueError("asinh_positive expects a nonnegative interval")
        one = self.interval(1)
        a2 = self.mul(a, a)
        root = self.sqrt(self.add(one, a2))
        return self.log(self.add(a, root))
