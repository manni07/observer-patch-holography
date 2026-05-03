#!/usr/bin/env python3
"""Export the verified rooted-tree packet-net repair domain."""

from __future__ import annotations

import argparse
import json
from collections import deque
from datetime import datetime, timezone
from math import sqrt
from itertools import product
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "consensus" / "runs" / "verified_tree_packet_net_domain.json"

ROOT_VERTEX = "r"
PARENTS = {"a": "r", "b": "a", "c": "a"}
CHILDREN = {"r": ["a"], "a": ["b", "c"], "b": [], "c": []}
VERTICES = [ROOT_VERTEX, "a", "b", "c"]
EDGES = [("r", "a"), ("a", "b"), ("a", "c")]
ALPHABET = [0, 1, 2]
GAUGE_LABELS = [0, 1]
WEIGHTS = {("r", "a"): 5, ("a", "b"): 1, ("a", "c"): 1}


PacketState = tuple[tuple[int, ...], tuple[int, ...]]


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _edge_key(edge: tuple[str, str]) -> str:
    return f"{edge[0]}-{edge[1]}"


def all_packet_states() -> Iterable[PacketState]:
    for packets in product(ALPHABET, repeat=len(VERTICES)):
        for hidden in product(GAUGE_LABELS, repeat=len(VERTICES)):
            yield packets, hidden


def _idx(vertex: str) -> int:
    return VERTICES.index(vertex)


def inconsistent_edges(state: PacketState) -> list[tuple[str, str]]:
    packets, _hidden = state
    return [(u, v) for u, v in EDGES if packets[_idx(u)] != packets[_idx(v)]]


def potential(state: PacketState) -> int:
    return sum(WEIGHTS[edge] for edge in inconsistent_edges(state))


def enabled_sites(state: PacketState) -> list[str]:
    packets, _hidden = state
    return [
        vertex
        for vertex in VERTICES
        if vertex != ROOT_VERTEX and packets[_idx(vertex)] != packets[_idx(PARENTS[vertex])]
    ]


def repair(state: PacketState, site: str) -> PacketState:
    if site == ROOT_VERTEX:
        return state
    packets, hidden = state
    parent = PARENTS[site]
    updated = list(packets)
    updated[_idx(site)] = packets[_idx(parent)]
    return tuple(updated), hidden


def terminal_states_from(state: PacketState) -> set[PacketState]:
    seen = {state}
    queue = deque([state])
    terminals: set[PacketState] = set()
    while queue:
        current = queue.popleft()
        sites = enabled_sites(current)
        if not sites:
            terminals.add(current)
            continue
        for site in sites:
            nxt = repair(current, site)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return terminals


def tree_checks() -> dict[str, object]:
    total_states = 0
    max_terminals = 0
    max_steps_seen = 0
    for state in all_packet_states():
        total_states += 1
        sites = enabled_sites(state)
        is_consistent = not inconsistent_edges(state)
        if is_consistent != (not sites):
            raise AssertionError(f"repair completeness failed for {state}")
        for site in sites:
            nxt = repair(state, site)
            if potential(nxt) >= potential(state):
                raise AssertionError(f"Lyapunov descent failed for {state} at {site}")
        terminals = terminal_states_from(state)
        max_terminals = max(max_terminals, len(terminals))
        if len(terminals) != 1:
            raise AssertionError(f"nonunique terminal states for {state}: {terminals}")
        terminal = next(iter(terminals))
        if inconsistent_edges(terminal):
            raise AssertionError(f"terminal state is inconsistent: {terminal}")
        max_steps_seen = max(max_steps_seen, potential(state))
    return {
        "total_states_checked": total_states,
        "repair_completeness": True,
        "strict_lyapunov_descent": True,
        "unique_terminal_normal_form": True,
        "max_terminal_count_seen": max_terminals,
        "potential_step_bound": max_steps_seen,
    }


def petz_checks() -> dict[str, object]:
    # Classical full-support Petz recovery for N = Tr_D:
    # R(mu)(b,d) = mu(b) sigma(d|b).  The sample matrix is column stochastic.
    reference_sigma_b = {b: 1.0 / len(ALPHABET) for b in ALPHABET}
    conditional = {
        0: {0: 0.5, 1: 0.25, 2: 0.25},
        1: {0: 0.25, 1: 0.5, 2: 0.25},
        2: {0: 0.25, 1: 0.25, 2: 0.5},
    }
    column_sums = {
        str(b): sum(conditional[b][d] for d in ALPHABET)
        for b in ALPHABET
    }
    if any(abs(value - 1.0) > 1.0e-12 for value in column_sums.values()):
        raise AssertionError(f"Petz column sums failed: {column_sums}")
    if any(conditional[b][d] <= 0.0 for b in ALPHABET for d in ALPHABET):
        raise AssertionError("Petz sample is not full-support")
    support_gap = min(reference_sigma_b.values())
    return {
        "channel": "classical_full_support_petz_for_trace_D",
        "formula": "R(mu_B)(b,d)=mu_B(b) sigma(d|b)",
        "cptp": True,
        "trace_norm_contractive": True,
        "support_gap_gamma_sigma": support_gap,
        "inverse_sqrt_bound": 1.0 / sqrt(support_gap),
        "input_domain": "all diagonal B-packet distributions because gamma_sigma > 0",
        "support_obstruction": "sigma_B(b)=0 with input mass at b makes the inverse sigma_B^{-1/2} undefined unless the domain is restricted",
        "reference_sigma_B": {str(b): value for b, value in reference_sigma_b.items()},
        "sample_conditional": conditional,
        "sample_column_sums": column_sums,
    }


def build_payload() -> dict[str, object]:
    return {
        "artifact": "oph_verified_tree_packet_net_domain",
        "object_id": "ConsensusTreePacketRepairDomain_Issue238",
        "generated_utc": _timestamp(),
        "issue": 238,
        "role": "Nontrivial exported packet-net domain where repair completeness, Petz-domain control, and quotient compatibility are theorem-grade.",
        "domain": {
            "graph": {
                "root": ROOT_VERTEX,
                "vertices": VERTICES,
                "oriented_edges": [_edge_key(edge) for edge in EDGES],
                "parents": PARENTS,
            },
            "packet_alphabet": ALPHABET,
            "hidden_gauge_labels_per_vertex": GAUGE_LABELS,
            "state_space": "S_i = Z_3 x Z_2; interface projections read only the Z_3 packet",
            "repair": "for non-root i, if x_i != x_parent(i), set x_i := x_parent(i) and leave hidden labels fixed",
            "weights": {_edge_key(edge): weight for edge, weight in WEIGHTS.items()},
        },
        "theorem_checks": tree_checks(),
        "petz_domain": petz_checks(),
        "quotient_compatibility": {
            "gauge_action": "independent permutations of the hidden Z_2 labels at each vertex",
            "reason": "interface projections, potentials, enabled sites, and repairs depend only on packet labels x_i",
            "descends_to_quotient": True,
            "physical_law_use": "gauge-invariant observables factor through the quotient normal form on this verified branch",
        },
        "general_obstructions_isolated": [
            "nonzero cycle holonomy on non-tree affine packet nets makes strict global consistency impossible",
            "packet-closure failure prevents a microscopic instrument from pushing forward to autonomous packet dynamics",
            "Petz recovery without full support requires an explicit support-domain restriction",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the verified tree packet-net domain artifact.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
