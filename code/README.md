# OPH Code

This directory is the canonical code surface for OPH derivation work.

Primary surfaces:

- `P_derivation/`: compressed `P -> alpha` closure and fixed-point artifacts.
- `particles/`: particle-spectrum builders, status surfaces, and gap campaigns.
- `consensus/`: packet-net and consensus-protocol code artifacts.
- `dark_matter/`: dark-sector simulation and likelihood utilities.

For the particle program, start with:

```bash
cd particles
python3 compute_current_output_table.py --no-print-table --show-paths
python3 scripts/build_derivation_gap_ledger.py
```

The particle gap campaign lives at `particles/campaigns/gap_bundle/`.
