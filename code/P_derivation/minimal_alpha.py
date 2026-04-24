#!/usr/bin/env python3
"""Smallest entrypoint for printing the derived fine-structure constant."""

from __future__ import annotations

import argparse

from paper_math import compute_alpha


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the derived fine-structure constant.")
    parser.add_argument("--precision", type=int, default=40, help="Decimal precision for the solver.")
    args = parser.parse_args()

    alpha, alpha_inv = compute_alpha(precision=args.precision)
    print(f"alpha      = {alpha}")
    print(f"alpha^-1   = {alpha_inv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
