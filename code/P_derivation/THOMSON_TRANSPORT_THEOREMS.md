# Thomson Transport Theorem Suite

This file states the theorem package needed to turn the current `P/alpha`
fixed-point witness into a measured fine-structure derivation.

The theorem package is not fully closed. The lepton one-loop transport is
implemented as a numerical kernel. The hadronic spectral object and the final
certified contraction theorem remain open.

## Objects

Let

```text
P = phi + alpha * sqrt(pi)
```

and let the D10 source solve emit

```text
Q_src(P) = (alpha_2(m_Z;P), alpha_Y(m_Z;P), alpha_3(m_Z;P), v(P), a0(P))
```

where

```text
a0(P) = alpha_em^-1(m_Z^2;P).
```

The desired Thomson endpoint is

```text
alpha_Th^-1(P) = a0(P) + Delta_Th(P).
```

The missing source-only theorem is a derivation of `Delta_Th(P)` from the same
Ward-projected `U(1)_Q` family as `a0(P)`.

## Theorem 1: Ward-Projected Source Lock

**Status:** closed at criterion level in the paper, not a populated transport
calculation.

Let the D10 source family be fixed by the forward pixel solve, and let the
realized low-energy charge operator be

```text
Q = T_3 + Y.
```

Let the electroweak transport kernel be

```text
K_D10^EW(q^2;P) = {Pi_AA, Pi_AZ, Pi_ZZ, Pi_WW}
```

with a Ward projector `W_Q` onto the unbroken electromagnetic channel. If

```text
W_Q[Pi_AZ(0;P)] = 0
```

and the projected `U(1)_Q` edge-sector probabilities satisfy

```text
p_n(q^2;P) proportional to exp(-t_Q(q^2;P) n^2),
```

then the electromagnetic readout on this lane is

```text
alpha_em^-1(q^2;P) = 8*pi^2 / t_Q(q^2;P).
```

Therefore

```text
alpha_Th^-1(P) = lim_{q^2 -> 0} 8*pi^2 / t_Q(q^2;P).
```

This theorem identifies the correct lane. It does not by itself compute
`t_Q(0;P)`.

## Theorem 2: Leptonic One-Loop Source Transport

**Status:** implemented as a numerical continuation, conditional on the current
Stage-5 charged-lepton mass emitter.

Assume the source branch emits charged-lepton masses

```text
m_e(P), m_mu(P), m_tau(P)
```

and the same Ward-projected scheme is used at `m_Z^2` and at the Thomson
endpoint. Then the perturbative charged-lepton contribution is

```text
Delta_lep(P) =
  sum_f K_f(m_Z(P)^2; m_f(P), Q_f^2 = 1, N_c = 1)
```

where

```text
K_f(Q^2;m_f,Q_f^2,N_c) =
  (2 N_c Q_f^2 / pi) * integral_0^1 x(1-x)
  log(1 + Q^2 x(1-x) / m_f^2) dx.
```

This is the exact one-loop kernel used by `paper_math.py`.

What remains to promote this to theorem grade:

1. prove that the Stage-5 lepton mass emitter is the source-only emitter on the
   same branch used by `a0(P)`;
2. attach a certified quadrature error bound;
3. prove the scheme match between `a0(P)` and the zero-momentum readout.

## Theorem 3: Hadronic Spectral Transport

**Status:** open.

The quark part cannot be theorem-grade if it is only a free-quark sum multiplied
by a simple screening factor. A source-only theorem must emit a positive
Ward-projected hadronic spectral density

```text
rho_had(s;P) >= 0
```

for the electromagnetic current-current correlator on the same D10 branch.

The required theorem is:

If `rho_had(s;P)` is emitted by the source branch, satisfies Ward positivity,
has the correct threshold support, and matches the high-energy quark/OPE tail
of the same `U(1)_Q` current, then the hadronic transport contribution is the
subtracted dispersion transport

```text
Delta_had(P) = Integral[ W_had(s, m_Z(P)^2) * rho_had(s;P) ds ],
```

with the subtraction chosen so that the same `a0(P)` scheme is used at
`m_Z^2`.

This theorem is the main missing physics object. It must replace the current
free-quark screened ansatz.

Constructive implementation target:

- `thomson_endpoint_contract.py`
- `runtime/thomson_endpoint_contract_current.json`
- `../particles/hadron/ward_projected_spectral_measure.schema.json`

Workers should not return obstruction-only text for this branch. If the current
free-quark screened route fails, the required replacement is a populated
Ward-projected spectral-measure export or a code/schema patch that moves that
export toward the endpoint builder.

## Theorem 4: Electroweak Matching Remainder

**Status:** open as a bound.

A full endpoint theorem also needs a residual matching term

```text
Delta_EW(P)
```

covering the difference between the D10 electroweak anchor convention and the
zero-momentum electromagnetic Thomson convention. The theorem must show either

```text
Delta_EW(P) = 0
```

in the declared scheme, or provide a source-only formula and an explicit error
bound.

## Theorem 5: Full Thomson Endpoint

**Status:** conditional theorem, not closed.

If Theorems 2, 3, and 4 are closed on the same source family and scheme, define

```text
Delta_Th(P) = Delta_lep(P) + Delta_had(P) + Delta_EW(P).
```

Then

```text
alpha_Th^-1(P) = a0(P) + Delta_Th(P)
```

is the source-only Thomson endpoint on the Ward-projected `U(1)_Q` lane.

At the current p80 report,

```text
a0(P) = 128.308268057804920945587248022104657547...
```

The compare-only CODATA target would require

```text
Delta_Th(P) = 8.727731119195079054412751977895342453...
```

The current implemented ansatz gives

```text
Delta_impl(P) = 8.686567144452067333731552158679540632...
```

so the open source-only theorem must account for

```text
Delta_missing(P) = 0.041163974743011720681199819215801821...
```

without using the measured endpoint as an input.

## Theorem 6: Fixed-Point Closure With Certified Transport

**Status:** open.

Once `Delta_Th(P)` is emitted, define

```text
G(alpha) =
  1 / (a0(phi + alpha * sqrt(pi)) + Delta_Th(phi + alpha * sqrt(pi))).
```

A theorem-grade fine-structure derivation requires an interval `I` such that

```text
G(I) subset I
sup_{alpha in I} |G'(alpha)| < 1
```

or another certified uniqueness argument. Then the fixed point

```text
alpha_* = G(alpha_*)
```

exists uniquely in `I`, and

```text
P_* = phi + alpha_* * sqrt(pi)
```

is the source-only OPH pixel closure.

The current `fixed_point_certificate.py` is a local numerical certificate for
the implemented map only. It is not this final theorem.

## Promotion Rule

No theorem in this file may be promoted to a measured-alpha derivation unless
all of the following are true:

1. `rho_had(s;P)` is emitted from the OPH source branch, not imported from a
   measured endpoint.
2. The same renormalization and matching scheme is used by `a0(P)` and
   `Delta_Th(P)`.
3. The transport integral has a certified numerical error bound.
4. The final fixed-point map has an interval-level existence and uniqueness
   certificate.
5. The CODATA/NIST value appears only in a final compare-only block.
