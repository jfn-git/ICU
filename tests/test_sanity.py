"""Smoke tests for env, model-known utilities, and tabular RL trainers.

Designed to run in well under 1 minute on a CPU.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to sys.path so `import src.*` works without install.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.env_utils import (  # noqa: E402
    N_ACTIONS,
    N_STATES,
    TERMINAL_STATES,
    admissible_mask_table,
    compute_Vpi,
    compute_Vstar,
    distance_to_optimal,
    get_dynamics,
    make_env,
    policy_agreement_with_expert,
)
from src.evaluate import rollout_eval  # noqa: E402
from src.policies import RandomPolicy, ExpertPolicy, DeterministicPolicy  # noqa: E402
from src.tabular_rl import (  # noqa: E402
    greedy_policy_from_Q,
    train_dyna_q,
    train_q_learning,
    train_sarsa,
)


# ---------------- Env / dynamics ------------------


def test_make_env_default_strategy_loads():
    env = make_env("mean")
    obs, info = env.reset(seed=0)
    assert 0 <= obs < N_STATES
    assert "admissible_actions" in info
    assert isinstance(info["admissible_actions"], list)
    assert all(0 <= a < N_ACTIONS for a in info["admissible_actions"])


def test_make_env_rejects_bad_strategy():
    with pytest.raises(ValueError):
        make_env("not_a_strategy")


def test_get_dynamics_shapes():
    env = make_env("mean")
    d = get_dynamics(env)
    assert d["tx_mat"].shape == (N_STATES, N_ACTIONS, N_STATES)
    assert d["r_mat"].shape == (N_STATES, N_ACTIONS, N_STATES)
    assert d["d_0"].shape == (N_STATES,)
    assert d["expert_policy"].shape == (N_STATES, N_ACTIONS)
    assert d["sofa_scores"].shape == (N_STATES,)
    assert len(d["admissible_actions"]) == N_STATES


def test_transition_probabilities_normalised():
    env = make_env("mean")
    d = get_dynamics(env)
    tx = d["tx_mat"]
    # For every (s, a), Σ_s' tx[s,a,s'] should be 1 (or 0 for "no info" cells)
    sums = tx.sum(axis=2)
    # All sums must be close to 0 or close to 1
    close_to_one = np.isclose(sums, 1.0, atol=1e-6)
    close_to_zero = np.isclose(sums, 0.0, atol=1e-6)
    assert (close_to_one | close_to_zero).all(), (
        f"some tx rows neither sum to 0 nor 1: {(~(close_to_one|close_to_zero)).sum()} violations"
    )


def test_d0_is_probability_vector():
    env = make_env("mean")
    d = get_dynamics(env)
    d0 = d["d_0"]
    assert np.all(d0 >= 0)
    assert np.isclose(d0.sum(), 1.0, atol=1e-6)


def test_admissible_mask_table():
    env = make_env("mean")
    d = get_dynamics(env)
    mask = admissible_mask_table(d["admissible_actions"])
    assert mask.shape == (N_STATES, N_ACTIONS)
    assert mask.dtype == bool
    # Every non-terminal state has at least one admissible action
    for s in range(N_STATES):
        if s in TERMINAL_STATES:
            continue
        assert mask[s].any(), f"state {s} has no admissible actions"


# ---------------- Value iteration / policy evaluation ------------------


def test_value_iteration_converges_and_matches_paper():
    env = make_env("mean")
    d = get_dynamics(env)
    pi_star, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-8)
    assert pi_star.shape == (N_STATES,)
    assert V_star.shape == (N_STATES,)
    # All state values bounded in [0, 1] since reward is 0 or 1 with γ=1 and
    # terminal absorbs.
    assert V_star.min() >= -1e-6
    assert V_star.max() <= 1.0 + 1e-6
    # d_0-weighted V_star should match the paper's "Optimal" mean return ≈ 0.88
    j_star = float(d["d_0"] @ V_star)
    assert 0.85 < j_star < 0.92, f"V* d_0-weighted return = {j_star}"


def test_policy_evaluation_matches_uniform_random_baseline():
    env = make_env("mean")
    d = get_dynamics(env)
    # Uniform-random policy → ≈ 0.78
    pi_rand = np.full((N_STATES, N_ACTIONS), 1.0 / N_ACTIONS)
    V_rand = compute_Vpi(pi_rand, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-8)
    j_rand = float(d["d_0"] @ V_rand)
    assert 0.75 < j_rand < 0.81, f"Uniform-random d_0-weighted return = {j_rand}"


def test_distance_to_optimal_zero_for_optimal():
    env = make_env("mean")
    d = get_dynamics(env)
    pi_star, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    V_pi_star = compute_Vpi(pi_star, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    gap = distance_to_optimal(V_pi_star, V_star, d["d_0"])
    assert abs(gap) < 1e-6, f"distance-to-V* for π* should be 0, got {gap}"


def test_policy_agreement_with_expert_self_is_one():
    env = make_env("mean")
    d = get_dynamics(env)
    expert_argmax = d["expert_policy"].argmax(axis=1)
    agree = policy_agreement_with_expert(expert_argmax, d["expert_policy"])
    assert agree == pytest.approx(1.0, abs=1e-9)


# ---------------- Rollout / policies ------------------


def test_rollout_random_policy_small():
    env = make_env("mean")
    pol = RandomPolicy(N_ACTIONS, rng=np.random.default_rng(0))
    out = rollout_eval(env, pol, num_episodes=200, seed=0)
    assert 0.0 <= out["return_mean"] <= 1.0
    assert out["ep_len_mean"] > 0


def test_rollout_expert_policy_small():
    env = make_env("mean")
    d = get_dynamics(env)
    pol = ExpertPolicy(d["expert_policy"], rng=np.random.default_rng(0))
    out = rollout_eval(env, pol, num_episodes=200, seed=0)
    # Expert clinician policy is NOT guaranteed to be inside the admissibility
    # set — admissibility is a data-coverage criterion on transition estimation,
    # not on which actions the clinicians used. Empirically we observe ≈ 0.15
    # unsafe rate; we just check it is substantially better than a random
    # baseline (which would be roughly 1 - mean(|admissible|/N_actions)).
    assert out["unsafe_rate_deployed"] < 0.30, (
        f"Expert unsafe rate {out['unsafe_rate_deployed']} unexpectedly high "
        "(>0.30 would imply expert policy is no better than random)"
    )


# ---------------- Tabular RL trainers ------------------


@pytest.mark.parametrize("use_mask", [False, True])
def test_q_learning_runs_short(use_mask):
    env = make_env("mean")
    out = train_q_learning(
        env, use_mask=use_mask, num_episodes=500, eps_decay_episodes=200, seed=42
    )
    assert out["Q"].shape == (N_STATES, N_ACTIONS)
    assert len(out["learning_curve"]) > 0
    assert 0.0 <= out["inadmissible_action_rate_training"] <= 1.0
    if use_mask:
        # With masking, training-time unsafe rate should be ~0 by construction.
        assert out["inadmissible_action_rate_training"] < 1e-6


@pytest.mark.parametrize("use_mask", [False, True])
def test_sarsa_runs_short(use_mask):
    env = make_env("mean")
    out = train_sarsa(
        env, use_mask=use_mask, num_episodes=500, eps_decay_episodes=200, seed=42
    )
    assert out["Q"].shape == (N_STATES, N_ACTIONS)
    if use_mask:
        assert out["inadmissible_action_rate_training"] < 1e-6


def test_dyna_q_runs_short():
    env = make_env("mean")
    out = train_dyna_q(
        env, use_mask=False, num_episodes=200, dyna_n=3,
        eps_decay_episodes=100, seed=7,
    )
    assert out["Q"].shape == (N_STATES, N_ACTIONS)


def test_greedy_policy_shape():
    Q = np.random.randn(N_STATES, N_ACTIONS)
    pi = greedy_policy_from_Q(Q)
    assert pi.shape == (N_STATES,)
    env = make_env("mean")
    d = get_dynamics(env)
    mask = admissible_mask_table(d["admissible_actions"])
    pi_masked = greedy_policy_from_Q(Q, admissible_mask=mask)
    assert pi_masked.shape == (N_STATES,)
    # Every action picked must be admissible (for non-terminal states with ≥1 admissible)
    for s in range(N_STATES):
        if s in TERMINAL_STATES:
            continue
        if mask[s].any():
            assert mask[s, pi_masked[s]]
