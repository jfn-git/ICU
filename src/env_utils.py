"""Environment wrappers and model-known utilities for ICU-Sepsis."""

from __future__ import annotations

import warnings
from typing import Sequence

import gymnasium as gym
import numpy as np

import icu_sepsis  # noqa: F401  (registers Sepsis/ICU-Sepsis-v* with gymnasium)

ENV_ID = "Sepsis/ICU-Sepsis-v2"
N_STATES = 716
N_ACTIONS = 25
STATE_DEATH = 713
STATE_SURVIVAL = 714
STATE_S_INF = 715
TERMINAL_STATES = (STATE_DEATH, STATE_SURVIVAL, STATE_S_INF)


def make_env(strategy: str = "mean", seed: int | None = None) -> gym.Env:
    """Construct an ICU-Sepsis-v2 env with the chosen inadmissible-action strategy.

    Args:
        strategy: 'mean' | 'terminate' | 'raise_exception'.
        seed: optional reset seed (applied via env.reset).
    """
    if strategy not in ("mean", "terminate", "raise_exception"):
        raise ValueError(f"Unknown inadmissible_action_strategy: {strategy}")
    env = gym.make(ENV_ID, inadmissible_action_strategy=strategy)
    if seed is not None:
        env.reset(seed=seed)
    return env


def get_dynamics(env: gym.Env) -> dict:
    """Return the env's known dynamics as a dict of arrays.

    Keys:
        tx_mat: (N_states, N_actions, N_states) transition probabilities
        r_mat:  (N_states, N_actions, N_states) deterministic terminal reward
        d_0:    (N_states,) initial state distribution
        admissible_actions: list[list[int]] of length N_states
        expert_policy: (N_states, N_actions) probabilities
        sofa_scores: (N_states,) avg SOFA per state
    """
    base = env.unwrapped
    return {
        "tx_mat": base.dynamics["tx_mat"],
        "r_mat": base.dynamics["r_mat"],
        "d_0": base.dynamics["d_0"],
        "admissible_actions": base.dynamics["admissible_actions"],
        "expert_policy": base.expert_policy,
        "sofa_scores": base.sofa_scores,
    }


def compute_Vstar(
    tx_mat: np.ndarray,
    r_mat: np.ndarray,
    gamma: float = 1.0,
    *,
    max_iter: int = 50_000,
    tol: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray]:
    """Value iteration. Returns (greedy_policy[N_S], V_star[N_S]).

    Uses dense computation; on 716x25 this finishes in <10 seconds.
    """
    n_s = tx_mat.shape[0]
    V = np.zeros(n_s, dtype=np.float64)
    for _ in range(max_iter):
        # Q[s,a] = Σ_s' tx[s,a,s'] (r[s,a,s'] + γ V[s'])
        Q = np.sum(tx_mat * (r_mat + gamma * V[None, None, :]), axis=2)
        V_new = Q.max(axis=1)
        if np.max(np.abs(V_new - V)) < tol:
            V = V_new
            break
        V = V_new
    Q = np.sum(tx_mat * (r_mat + gamma * V[None, None, :]), axis=2)
    policy = Q.argmax(axis=1).astype(np.int64)
    return policy, V


def compute_Vpi(
    pi_table: np.ndarray,
    tx_mat: np.ndarray,
    r_mat: np.ndarray,
    gamma: float = 1.0,
    *,
    max_iter: int = 50_000,
    tol: float = 1e-9,
) -> np.ndarray:
    """Exact policy evaluation via fixed-point iteration on V.

    Args:
        pi_table: either (N_S,) deterministic argmax actions, or (N_S, N_A)
            stochastic probabilities (rows sum to 1).
        tx_mat:   (N_S, N_A, N_S)
        r_mat:    (N_S, N_A, N_S)
        gamma:    discount.
    Returns:
        V_pi: (N_S,) state values.
    """
    n_s, n_a, _ = tx_mat.shape

    if pi_table.ndim == 1:
        # Deterministic: one-hot it.
        det = pi_table.astype(np.int64)
        pi = np.zeros((n_s, n_a), dtype=np.float64)
        pi[np.arange(n_s), det] = 1.0
    else:
        pi = pi_table.astype(np.float64)
        # Soft-renormalise in case of rounding.
        row_sum = pi.sum(axis=1, keepdims=True)
        # Avoid div-by-zero in terminal-only rows
        row_sum = np.where(row_sum > 0, row_sum, 1.0)
        pi = pi / row_sum

    # P_pi[s, s'] = Σ_a pi(a|s) tx[s,a,s']
    P_pi = np.einsum("sa,sak->sk", pi, tx_mat)
    # R_pi[s] = Σ_a pi(a|s) Σ_s' tx[s,a,s'] r[s,a,s']
    R_step = np.sum(tx_mat * r_mat, axis=2)  # (N_S, N_A)
    R_pi = np.sum(pi * R_step, axis=1)       # (N_S,)

    V = np.zeros(n_s, dtype=np.float64)
    for _ in range(max_iter):
        V_new = R_pi + gamma * P_pi @ V
        if np.max(np.abs(V_new - V)) < tol:
            V = V_new
            break
        V = V_new
    return V


def distance_to_optimal(V_pi: np.ndarray, V_star: np.ndarray, d_0: np.ndarray) -> float:
    """Initial-state-weighted optimality gap E_{s~d_0}[V*(s) - V^π(s)]."""
    return float(d_0 @ (V_star - V_pi))


def policy_agreement_with_expert(
    pi_table: np.ndarray, expert_policy: np.ndarray
) -> float:
    """Fraction of non-terminal states where argmax(pi) == argmax(expert).

    Args:
        pi_table: (N_S,) deterministic or (N_S, N_A) stochastic policy.
        expert_policy: (N_S, N_A).
    """
    if pi_table.ndim == 1:
        a_pi = pi_table.astype(np.int64)
    else:
        a_pi = pi_table.argmax(axis=1)
    a_ex = expert_policy.argmax(axis=1)
    non_terminal = np.array(
        [s for s in range(N_STATES) if s not in TERMINAL_STATES],
        dtype=np.int64,
    )
    return float((a_pi[non_terminal] == a_ex[non_terminal]).mean())


def admissible_mask_table(admissible_actions: Sequence[Sequence[int]]) -> np.ndarray:
    """Boolean (N_S, N_A) mask: True where action is admissible in state s."""
    mask = np.zeros((N_STATES, N_ACTIONS), dtype=bool)
    for s, acts in enumerate(admissible_actions):
        for a in acts:
            mask[s, a] = True
    return mask
