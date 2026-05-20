"""Diagnostic analysis: per-SOFA-bucket unsafe-action rate, etc."""

from __future__ import annotations

import numpy as np

from .env_utils import N_STATES, TERMINAL_STATES


def per_sofa_bucket_unsafe_rate(
    pi_action_table: np.ndarray,
    admissible_mask: np.ndarray,
    sofa_scores: np.ndarray,
    *,
    num_buckets: int = 5,
) -> dict:
    """For each SOFA-quantile bucket, fraction of non-terminal states where
    pi(s) is inadmissible.

    Args:
        pi_action_table: (N_S,) argmax action per state.
        admissible_mask: (N_S, N_A) bool.
        sofa_scores: (N_S,)
    Returns:
        dict with `bucket_edges`, `bucket_centers`, `unsafe_rate_per_bucket`,
        `n_states_per_bucket`.
    """
    non_terminal = np.array(
        [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
    )
    sofa_nt = sofa_scores[non_terminal]
    actions_nt = pi_action_table[non_terminal]
    inadmissible_flag = np.array(
        [not admissible_mask[s, a] for s, a in zip(non_terminal, actions_nt)]
    )
    edges = np.quantile(sofa_nt, np.linspace(0, 1, num_buckets + 1))
    edges[-1] += 1e-9  # include max
    centers = 0.5 * (edges[:-1] + edges[1:])
    unsafe = np.zeros(num_buckets)
    n = np.zeros(num_buckets, dtype=np.int64)
    for b in range(num_buckets):
        lo, hi = edges[b], edges[b + 1]
        in_bucket = (sofa_nt >= lo) & (sofa_nt < hi)
        n[b] = int(in_bucket.sum())
        if n[b] > 0:
            unsafe[b] = float(inadmissible_flag[in_bucket].mean())
    return {
        "bucket_edges": edges.tolist(),
        "bucket_centers": centers.tolist(),
        "unsafe_rate_per_bucket": unsafe.tolist(),
        "n_states_per_bucket": n.tolist(),
    }


def fraction_admissible_argmax(
    Q: np.ndarray, admissible_mask: np.ndarray
) -> float:
    """What fraction of non-terminal states have argmax(Q[s,:]) inside the
    admissible set? A diagnostic for whether Q-learning *learned* to avoid
    inadmissible actions even without explicit masking."""
    non_terminal = np.array(
        [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
    )
    a = Q[non_terminal].argmax(axis=1)
    is_adm = admissible_mask[non_terminal, a]
    return float(is_adm.mean())
