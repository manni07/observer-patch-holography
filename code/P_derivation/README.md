# P Derivation

This directory is a clean paper-math implementation of the OPH `P <-> alpha`
closure experiment.

The goal is to avoid the current public-facing ambiguity between the paper
equations and the larger `code/particles` calibration stack. The code here is
therefore built directly from the equations stated in:

- `paper/deriving_the_particle_zoo_from_observer_consistency.tex`
- `paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.tex`
- `paper/observers_are_all_you_need.tex`

## What is implemented

For a trial pixel constant `P`, the code reproduces the paper D10 forward map:

1. `M_U(P) = E_P * exp(-2*pi) * P^(1/6)`
2. `E_cell(P) = E_P / sqrt(P)`
3. Solve the one-dimensional D10 pixel-closure equation for `alpha_U(P)`:
   `ellbar_SU(2)(t2) + ellbar_SU(3)(t3) - P/4 = 0`
4. Build the source-locked electroweak anchor
   `a0(P) = alpha_em^-1(m_Z^2; P)`

The new closure step then inserts that paper-side `P -> alpha` map into Alex's
equation:

`P = phi + alpha * sqrt(pi)`

## Terms

`P ratio (pixel size)` means the dimensionless screen-cell area

`P = a_cell / l_P^2`

so it is the outer pixel area measured in Planck units.

`inside minimal observation` means the electromagnetic coupling that acts as the
smallest durable observation scale inside the emitted universe. In the strict
D10 core this is the source anchor `a0(P) = alpha_em^-1(m_Z^2; P)`. In the
full low-energy extension it is the Thomson-limit coupling after internal
running.

Informally, the closure program is:

- the outer description says how far the realized pixel sits above the
  golden-ratio equilibrium, via `P = phi + alpha * sqrt(pi)`
- the inner description says what electromagnetic observation scale that same
  pixel emits through the OPH chain
- the derivation solves for the unique `alpha` where those two descriptions
  agree, and only then computes `P`

## Readout modes

Two alpha readout modes are supported:

- `thomson_structured_running`
  This is the default. It uses the D10 core for
  `a0(P) = alpha_em^-1(m_Z^2;P)`, then computes
  `Delta alpha^-1(P)` from the internal Stage-5 charged-spectrum continuation
  together with the quark screening factor `1 - N_c alpha_s(P)/pi`.
  No paper endpoint, frozen ratio, or imported charged bundle is inserted.

- `mz_anchor`
  Uses the source anchor `a0(P) = alpha_em^-1(m_Z^2; P)` directly. This is
  mainly a debugging surface.

The important claim-boundary caveat is:

- `paper_math.py` is now zero-insert with respect to paper-side target values:
  it contains no hard-coded reference `P`, no hard-coded Thomson endpoint, and
  no imported compare bundle from `code/particles`.
- `thomson_structured_running` is therefore the cleanest internal closure
  experiment in this directory.
- It is still a continuation beyond the strict theorem-grade D10 core, because
  the final low-energy transport law is being modeled by the current internal
  Stage-5 structured-running ansatz rather than by a closed theorem.

## Usage

From `reverse-engineering-reality/code/P_derivation/`:

```bash
python3 derive_p.py --mode thomson_structured_running --precision 40
```

If you only want the shortest possible entrypoint that prints the derived
fine-structure constant, use:

```bash
python3 minimal_alpha.py --precision 40
```

To emit a full JSON report:

```bash
python3 derive_p.py --mode thomson_structured_running --precision 40 --json
```

To save the report:

```bash
python3 derive_p.py --mode thomson_structured_running --precision 40 --output runtime/report.json
```

## Output

The CLI prints:

- the solved `alpha` and `alpha^-1`
- the implied `P`
- the source anchor `a0(P)`
- the D10 point at the closure solution
- the internal structured-running decomposition used to reach the Thomson limit

The JSON report also includes every alpha-space closure step.
