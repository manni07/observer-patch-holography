# OPH Code

This directory is the canonical code surface for OPH derivation work.

Primary surfaces:

- `P_derivation/`: compressed `P -> alpha` closure and fixed-point artifacts.
- `particles/`: particle-spectrum builders, status surfaces, and gap campaigns.
- `consensus/`: packet-net, consensus-protocol, and fixed-cutoff Z2/S3 reference-architecture benchmark artifacts.
- `dark_matter/`: dark-sector simulation and likelihood utilities.

For the reference-architecture benchmark suite:

```bash
python3 code/consensus/reference_architecture_benchmark_suite.py
python3 -m pytest code/consensus/test_reference_architecture_benchmark_suite.py
```

The current emitted artifact is `code/consensus/runs/reference_architecture_benchmark_suite_current.json`.

For the particle program, start with:

```bash
cd particles
python3 compute_current_output_table.py --no-print-table --show-paths
python3 scripts/build_derivation_gap_ledger.py
```

The particle gap campaign lives at `particles/campaigns/gap_bundle/`.
