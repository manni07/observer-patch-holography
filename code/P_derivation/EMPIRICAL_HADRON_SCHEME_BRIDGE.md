# Empirical Hadron Scheme Bridge

This note records the non-circular PDG/CERN hadron-input test for the OPH
fine-structure fixed point.

## Fixed-Point Law

The paper equation is

```text
P = phi + sqrt(pi) / A_T(P)
alpha(0) = 1 / A_T(P)
```

The current source-side decomposition at the public pixel uses

```text
A_T(P) = a0(P) + Delta_lep(P) + Delta_had(P) + Delta_rem(P).
```

The OPH source anchor and lepton packet are

```text
a0(P*)          = 128.307965473286248209961108741756716187...
Delta_lep(P*)  =   4.309397866452204027131743897534489402...
```

## PDG/CERN Hadron Input

PDG/CERN hadronic running values are dimensionless vacuum-polarization
denominator shifts, not additive inverse-alpha packets. In the on-shell
running convention,

```text
alpha(s) = alpha(0) / (1 - Delta_alpha(s)).
```

For an OPH pre-hadronic inverse-alpha value

```text
A_L = a0(P*) + Delta_lep(P*),
```

the direct denominator conversion is

```text
A_T = A_L / (1 - Delta_alpha_had^(5)(M_Z)).
```

Using the PDG electroweak-review row

```text
Delta_alpha_had^(5)(M_Z) = 0.02761
```

gives

```text
A_T(P*) = 136.382895072695577121415124218977165118...
alpha(0) = 0.007332297789007737228352620303723714557...
P* = 1.631030148202007612899638188646695522...
```

Against the NIST/CODATA comparison value

```text
alpha(0)^-1 = 137.035999177
```

the gap is

```text
-0.653104104304422878584875781022834882
```

inverse-alpha units.

## What Would Be Required

Keeping the current OPH source anchor and lepton packet fixed, the hadronic
denominator shift required to hit the NIST/CODATA comparison value is

```text
Delta_alpha_had_required = 0.03224434355788728882226849923695794742...
```

That is outside the PDG/CERN hadronic-running range around `0.0274` to
`0.0278`.

Keeping the PDG value fixed, the source anchor required to hit the same
comparison value is

```text
a0_required = 128.943037373270825972868256102465510598...
```

The current source anchor is

```text
a0_current = 128.307965473286248209961108741756716187...
```

so the same-scheme source-anchor bridge would need to emit

```text
Delta_a0_scheme = 0.635071899984577762907147360708794411...
```

inverse-alpha units.

## Closure Status

The exact source-only fine-structure lane is not closed by inserting raw
PDG/CERN `Delta_alpha_had^(5)(M_Z)`. That input is a valid empirical diagnostic,
but it exposes a same-scheme bridge gap between the OPH source anchor and the
standard on-shell electroweak running convention.

The valid closure routes are:

1. Emit a source-only Ward-projected endpoint map in the OPH scheme, including
   the hadronic spectral measure and the same-scheme electroweak remainder.
2. Derive a source-side electroweak scheme bridge that maps the OPH D10 anchor
   to the PDG/CERN on-shell running-alpha convention, then use the empirical
   hadronic dispersion input.
3. Keep the NIST/CODATA endpoint row as calibration-only. This hits the value
   by construction and must not be presented as a source-only derivation.

## Diagnostic Script

Run:

```bash
python3 code/P_derivation/fine_structure_fixed_point_demo.py
```

For comparison against NIST/CODATA, pass the comparison value explicitly:

```bash
python3 code/P_derivation/fine_structure_fixed_point_demo.py --compare-alpha-inv 137.035999177
```

The comparison value is not used in the solver path.

## References

- NIST/CODATA 2022 inverse fine-structure constant:
  `https://physics.nist.gov/cgi-bin/cuu/Value?eqalphinv=`
- PDG electroweak review, running alpha convention and hadronic-running rows:
  `https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf`
- CERN/DHMZ hadronic vacuum-polarization compilation:
  `https://cds.cern.ch/record/1300176/`
