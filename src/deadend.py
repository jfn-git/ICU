"""Exact dead-end / harm structure on ICU-Sepsis using known dynamics.

Because reward is a pure survival indicator and gamma = 1, the optimal value
V*(s) is *exactly* the maximum achievable survival probability from state s.
This lets us compute -- exactly, not by estimation -- which states are
dead-ends (death essentially inevitable) and which actions are "harmful"
(they sacrifice survival probability relative to the optimal action).

Fatemi et al. (NeurIPS 2021) estimate dead-ends from data; here the tabular
ICU-Sepsis MDP gives us the ground truth.
"""

from __future__ import annotations

import numpy as np

from .env_utils import N_ACTIONS, N_STATES, STATE_DEATH, TERMINAL_STATES


def compute_Qstar(
    tx_mat: np.ndarray, r_mat: np.ndarray, V_star: np.ndarray, gamma: float = 1.0
) -> np.ndarray:
    """Q*(s,a) = Σ_s' tx[s,a,s'] (r[s,a,s'] + γ V*[s']).  Shape (N_S, N_A)."""
    return np.sum(tx_mat * (r_mat + gamma * V_star[None, None, :]), axis=2)


def non_terminal_states() -> np.ndarray:
    return np.array(
        [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
    )


def state_occupancy(
    pi_table: np.ndarray, tx_mat: np.ndarray, d_0: np.ndarray
) -> np.ndarray:
    """Expected (undiscounted) state-visitation counts under a policy.

    Solves d_T = d0_T + P_TT^T d_T over transient (non-terminal) states, i.e.
    d_T = (I - P_TT^T)^{-1} d0_T. Returns full (N_S,) vector (terminals = 0).

    Args:
        pi_table: (N_S,) deterministic actions or (N_S, N_A) stochastic.
    """
    n_s, n_a, _ = tx_mat.shape
    if pi_table.ndim == 1:
        pi = np.zeros((n_s, n_a))
        pi[np.arange(n_s), pi_table.astype(np.int64)] = 1.0
    else:
        pi = pi_table.astype(np.float64)
        rs = pi.sum(axis=1, keepdims=True)
        pi = pi / np.where(rs > 0, rs, 1.0)
    P_pi = np.einsum("sa,sak->sk", pi, tx_mat)  # (N_S, N_S)

    T = non_terminal_states()
    P_TT = P_pi[np.ix_(T, T)]
    d0_T = d_0[T]
    d_T = np.linalg.solve(np.eye(len(T)) - P_TT.T, d0_T)
    d = np.zeros(n_s)
    d[T] = d_T
    return d


def deadend_structure(
    tx_mat: np.ndarray,
    r_mat: np.ndarray,
    V_star: np.ndarray,
    d_0: np.ndarray,
    admissible_mask: np.ndarray,
    *,
    deadend_thr: float = 1e-6,
    near_deadend_thr: float = 0.10,
    secured_thr: float = 0.90,
    harm_thr: float = 0.05,
) -> dict:
    """Exact dead-end and harmful-action structure.

    Returns a JSON-serialisable dict of summary statistics.
    """
    Q_star = compute_Qstar(tx_mat, r_mat, V_star)        # (N_S, N_A)
    gap = V_star[:, None] - Q_star                        # (N_S, N_A) >= 0
    death_risk = tx_mat[:, :, STATE_DEATH]                # one-step P(death)

    T = non_terminal_states()
    Vt = V_star[T]

    # --- State-level dead-end census (among non-terminal states) ---
    n_hard = int((Vt <= deadend_thr).sum())
    n_near = int((Vt < near_deadend_thr).sum())
    n_secured = int((Vt >= secured_thr).sum())

    # Reachability weighting: occupancy under a uniform-random policy
    rand_pi = np.full((N_STATES, N_ACTIONS), 1.0 / N_ACTIONS)
    occ = state_occupancy(rand_pi, tx_mat, d_0)
    occ_T = occ[T]
    occ_w = occ_T / occ_T.sum() if occ_T.sum() > 0 else occ_T
    frac_hard_w = float(occ_w[Vt <= deadend_thr].sum())
    frac_near_w = float(occ_w[Vt < near_deadend_thr].sum())

    # --- Admissibility vs harm (the key cross-tab) ---
    adm = admissible_mask[T]                              # (|T|, N_A) bool
    gap_T = gap[T]
    death_T = death_risk[T]
    adm_flat = adm.reshape(-1)
    gap_flat = gap_T.reshape(-1)
    death_flat = death_T.reshape(-1)
    mean_gap_adm = float(gap_flat[adm_flat].mean())
    mean_gap_inadm = float(gap_flat[~adm_flat].mean())
    mean_death_adm = float(death_flat[adm_flat].mean())
    mean_death_inadm = float(death_flat[~adm_flat].mean())
    # Of all "harmful" (gap > harm_thr) actions, what fraction are inadmissible?
    harmful_flat = gap_flat > harm_thr
    frac_harmful_inadm = (
        float((harmful_flat & ~adm_flat).sum() / max(1, harmful_flat.sum()))
    )

    return {
        "params": {
            "deadend_thr": deadend_thr,
            "near_deadend_thr": near_deadend_thr,
            "secured_thr": secured_thr,
            "harm_thr": harm_thr,
        },
        "n_non_terminal": int(len(T)),
        "Vstar_nonterminal_mean": float(Vt.mean()),
        "Vstar_nonterminal_median": float(np.median(Vt)),
        "Vstar_nonterminal_min": float(Vt.min()),
        "state_census": {
            "n_hard_deadend": n_hard,
            "n_near_deadend": n_near,
            "n_secured": n_secured,
            "frac_hard_deadend": float(n_hard / len(T)),
            "frac_near_deadend": float(n_near / len(T)),
            "frac_secured": float(n_secured / len(T)),
            "reach_weighted_frac_hard_deadend": frac_hard_w,
            "reach_weighted_frac_near_deadend": frac_near_w,
        },
        "admissibility_vs_harm": {
            "mean_gap_admissible": mean_gap_adm,
            "mean_gap_inadmissible": mean_gap_inadm,
            "mean_one_step_death_admissible": mean_death_adm,
            "mean_one_step_death_inadmissible": mean_death_inadm,
            "frac_harmful_actions_that_are_inadmissible": frac_harmful_inadm,
        },
    }


def policy_harm_mass(
    pi_table: np.ndarray,
    tx_mat: np.ndarray,
    r_mat: np.ndarray,
    V_star: np.ndarray,
    d_0: np.ndarray,
    *,
    harm_thr: float = 0.05,
) -> dict:
    """Visitation-weighted expected per-step probability that a policy takes a
    harmful action (Q*-gap > harm_thr), plus expected per-step one-step death
    probability. Works for deterministic (N_S,) or stochastic (N_S, N_A)."""
    Q_star = compute_Qstar(tx_mat, r_mat, V_star)
    gap = V_star[:, None] - Q_star
    harmful = (gap > harm_thr).astype(np.float64)         # (N_S, N_A)
    death_risk = tx_mat[:, :, STATE_DEATH]

    if pi_table.ndim == 1:
        pi = np.zeros((N_STATES, N_ACTIONS))
        pi[np.arange(N_STATES), pi_table.astype(np.int64)] = 1.0
    else:
        pi = pi_table.astype(np.float64)
        rs = pi.sum(axis=1, keepdims=True)
        pi = pi / np.where(rs > 0, rs, 1.0)

    occ = state_occupancy(pi, tx_mat, d_0)
    T = non_terminal_states()
    w = occ[T]
    w = w / w.sum() if w.sum() > 0 else w

    harm_per_state = (pi[T] * harmful[T]).sum(axis=1)      # P(harmful | s)
    death_per_state = (pi[T] * death_risk[T]).sum(axis=1)  # E[death | s]
    return {
        "expected_harmful_action_prob": float((w * harm_per_state).sum()),
        "expected_one_step_death_prob": float((w * death_per_state).sum()),
    }
