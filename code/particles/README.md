# Compact Public Particle Surface

This directory is the compact public particle surface mirrored from the sibling
`/particles` workspace. It supports the papers, book, and repo README without
copying the Oracle batch archive, automation plumbing, or sandbox process
history.

## Layout

- `core/`: compatibility backbone for the public predictor modules
  that newer lanes still depend on.
- `calibration/`: D10 and D11 exactness-audit lane.
- `flavor/`: shared charged-sector, projector, transport, and quark
  continuation lane.
- `leptons/`: charged-lepton continuation lane.
- `neutrino/`: forward neutrino continuation lane and guards.
- `hadron/`: debug/systematics hadron lane, including baryon and
  `rho`-scattering scaffolds.
- `runs/`: frozen public artifacts.
- `RESULTS_STATUS.md`, `results_status.json`, `ledger.yaml`: compact status
  surfaces for the public claim boundary.

## Intentional Boundary

This export keeps the scientific code lanes and frozen public outputs. It
does not mirror:

- Oracle prompts, batch manifests, or transcripts
- autonomous supervisor tooling
- browser-profile or launchd setup
- quantum sandbox utilities
- planning docs, work trackers, and long run history

## Status

- `D10`: calibration closure lane
- `D11`: secondary quantitative Higgs/top lane
- charged leptons, flavor, neutrinos: continuation lanes with explicit
  artifact boundaries
- hadrons: simulation-dependent debug lane only

Code or artifacts in this directory do not promote those lanes to theorem-level
OPH output.

Some rows in `RESULTS_STATUS.md` still miss experiment, in some sectors by a
large margin. In `D10` and `D11`, the remaining mismatch is a missing
transport/readout closure problem, not a decimal-precision issue in `P`. In
the charged, flavor, and neutrino lanes, the remaining error sits behind
still-open shared-scale, family-excitation, and selector/evaluator objects. In
hadrons, the numbers come from a debug/systematics lane and are not closure
candidates. Work continues on those explicit missing objects.

## Minimal Dependencies

```bash
pip install -r code/particles/requirements.txt
```

## Useful Checks

```bash
python3 code/particles/calibration/test_single_p_consistency.py
python3 code/particles/calibration/test_d10_observable_family_artifact.py
python3 code/particles/flavor/test_flavor_dictionary_disambiguation.py
python3 code/particles/leptons/test_ratio_only_not_promoted.py
python3 code/particles/neutrino/test_bundle_descent_candidate_fields.py
python3 code/particles/tests/test_hadron_demo_not_promoted.py
```
