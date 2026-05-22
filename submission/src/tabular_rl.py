"""Tabular Q-learning / SARSA / Dyna-Q with optional action masking."""

from __future__ import annotations

from typing import Optional

import gymnasium as gym
import numpy as np

from .env_utils import N_ACTIONS, N_STATES


def _eps_schedule(ep: int, eps_start: float, eps_end: float, decay_episodes: int) -> float:
    if ep >= decay_episodes:
        return eps_end
    frac = ep / max(1, decay_episodes)
    return eps_start + (eps_end - eps_start) * frac


def _masked_argmax(q_row: np.ndarray, admissible: list[int]) -> int:
    """argmax restricted to admissible actions (random tiebreak)."""
    vals = q_row[admissible]
    best = vals.max()
    candidates = [a for a, v in zip(admissible, vals) if v == best]
    return int(candidates[0]) if len(candidates) == 1 else int(np.random.choice(candidates))


def _select_action(
    q_row: np.ndarray,
    admissible: list[int],
    eps: float,
    rng: np.random.Generator,
    *,
    use_mask: bool,
) -> int:
    if use_mask:
        if rng.random() < eps:
            return int(rng.choice(admissible))
        return _masked_argmax(q_row, admissible)
    else:
        if rng.random() < eps:
            return int(rng.integers(0, N_ACTIONS))
        # Unrestricted argmax with random tiebreak among ties
        best_val = q_row.max()
        ties = np.flatnonzero(q_row == best_val)
        return int(ties[0]) if ties.size == 1 else int(rng.choice(ties))


def _record_curve_point(curve: list, ep: int, return_so_far: list, window: int = 100) -> None:
    """Append a smoothed (mean over last `window` episodes) checkpoint."""
    recent = return_so_far[-window:]
    curve.append((int(ep), float(np.mean(recent)) if recent else 0.0))


def train_q_learning(
    env: gym.Env,
    *,
    use_mask: bool = False,
    mask_behavior: Optional[bool] = None,
    mask_target: Optional[bool] = None,
    inadmissible_penalty: float = 0.0,
    conservative_kappa: float = 0.0,
    num_episodes: int = 50_000,
    alpha: float = 0.1,
    gamma: float = 1.0,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    eps_decay_episodes: int = 10_000,
    seed: int = 0,
    log_every: int = 500,
    snapshot_every: int = 0,
) -> dict:
    """Tabular Q-learning spanning the OOD-action remedy spectrum.

    Args:
        use_mask: convenience flag; when True (and the granular flags are left
            None) it turns on BOTH behavior and target masking. The hard-mask
            endpoint of the spectrum.
        mask_behavior: if set, overrides use_mask for behavior selection
            (epsilon-greedy restricted to admissible actions).
        mask_target: if set, overrides use_mask for the Bellman backup (the
            max in the TD target restricted to next-state admissible actions).
            Splitting these two enables the component ablation that locates
            *where* the failure lives.
        inadmissible_penalty: soft support penalty lambda; subtract from the TD
            target reward when the taken action is inadmissible (behavior-level
            conservatism).
        conservative_kappa: CQL-style value-level conservatism. At each visited
            state, nudge Q toward the admissible support: subtract
            alpha*kappa*(softmax(Q[s]) - uniform_over_admissible). This suppresses
            inadmissible Q-values (incl. their effect on the backup max) without
            a hard constraint -- the principled middle of the spectrum.
        snapshot_every: if > 0, store a copy of Q every this many episodes
            (for exact distance-to-V* and Q-value-leakage curves).

    Returns dict: {Q, learning_curve, q_snapshots, inadmissible_action_rate_training,
                  total_steps, num_episodes}.
    """
    mb = use_mask if mask_behavior is None else mask_behavior
    mt = use_mask if mask_target is None else mask_target
    rng = np.random.default_rng(seed)
    np.random.seed(seed)  # for _masked_argmax tiebreak
    Q = np.zeros((N_STATES, N_ACTIONS), dtype=np.float64)
    returns: list[float] = []
    curve: list[tuple[int, float]] = []
    snapshots: list[tuple[int, np.ndarray]] = []
    inadm = 0
    total_steps = 0

    obs, info = env.reset(seed=seed)
    for ep in range(num_episodes):
        if ep > 0:
            obs, info = env.reset()
        eps = _eps_schedule(ep, eps_start, eps_end, eps_decay_episodes)
        ep_return = 0.0
        while True:
            admissible = info["admissible_actions"]
            action = _select_action(Q[obs], admissible, eps, rng, use_mask=mb)
            is_inadmissible = action not in admissible
            if is_inadmissible:
                inadm += 1
            next_obs, reward, terminated, truncated, next_info = env.step(action)
            # Soft support penalty: give a learnable negative signal for OOD actions.
            shaped_reward = reward - inadmissible_penalty if is_inadmissible else reward
            # Q-learning target: bootstrap over masked or unmasked max
            if terminated:
                td_target = shaped_reward
            else:
                if mt:
                    next_admissible = next_info["admissible_actions"]
                    bootstrap = Q[next_obs, next_admissible].max()
                else:
                    bootstrap = Q[next_obs].max()
                td_target = shaped_reward + gamma * bootstrap
            Q[obs, action] += alpha * (td_target - Q[obs, action])

            # CQL-style value-level conservatism toward the admissible support.
            if conservative_kappa > 0.0:
                q_s = Q[obs]
                p = np.exp(q_s - q_s.max())
                p /= p.sum()
                target = np.zeros(N_ACTIONS)
                target[admissible] = 1.0 / len(admissible)
                Q[obs] -= alpha * conservative_kappa * (p - target)

            obs, info = next_obs, next_info
            ep_return += float(reward)
            total_steps += 1
            if terminated or truncated:
                break
        returns.append(ep_return)
        if (ep + 1) % log_every == 0 or ep == 0:
            _record_curve_point(curve, ep + 1, returns)
        if snapshot_every > 0 and (ep + 1) % snapshot_every == 0:
            snapshots.append((ep + 1, Q.copy()))

    return {
        "Q": Q,
        "learning_curve": curve,
        "q_snapshots": snapshots,
        "inadmissible_action_rate_training": float(inadm / max(1, total_steps)),
        "total_steps": int(total_steps),
        "num_episodes": int(num_episodes),
    }


def train_sarsa(
    env: gym.Env,
    *,
    use_mask: bool = False,
    num_episodes: int = 50_000,
    alpha: float = 0.1,
    gamma: float = 1.0,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    eps_decay_episodes: int = 10_000,
    seed: int = 0,
    log_every: int = 500,
) -> dict:
    """Tabular on-policy SARSA. Same return schema as train_q_learning."""
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    Q = np.zeros((N_STATES, N_ACTIONS), dtype=np.float64)
    returns: list[float] = []
    curve: list[tuple[int, float]] = []
    inadm = 0
    total_steps = 0

    obs, info = env.reset(seed=seed)
    for ep in range(num_episodes):
        if ep > 0:
            obs, info = env.reset()
        eps = _eps_schedule(ep, eps_start, eps_end, eps_decay_episodes)
        admissible = info["admissible_actions"]
        action = _select_action(Q[obs], admissible, eps, rng, use_mask=use_mask)
        if action not in admissible:
            inadm += 1
        ep_return = 0.0
        while True:
            next_obs, reward, terminated, truncated, next_info = env.step(action)
            ep_return += float(reward)
            total_steps += 1
            if terminated:
                td_target = reward
                Q[obs, action] += alpha * (td_target - Q[obs, action])
                break
            next_admissible = next_info["admissible_actions"]
            next_action = _select_action(
                Q[next_obs], next_admissible, eps, rng, use_mask=use_mask
            )
            if next_action not in next_admissible:
                inadm += 1
            td_target = reward + gamma * Q[next_obs, next_action]
            Q[obs, action] += alpha * (td_target - Q[obs, action])
            obs, info, action, admissible = next_obs, next_info, next_action, next_admissible
            if truncated:
                break
        returns.append(ep_return)
        if (ep + 1) % log_every == 0 or ep == 0:
            _record_curve_point(curve, ep + 1, returns)

    return {
        "Q": Q,
        "learning_curve": curve,
        "inadmissible_action_rate_training": float(inadm / max(1, total_steps)),
        "total_steps": int(total_steps),
        "num_episodes": int(num_episodes),
    }


def train_dyna_q(
    env: gym.Env,
    *,
    use_mask: bool = False,
    num_episodes: int = 50_000,
    alpha: float = 0.1,
    gamma: float = 1.0,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    eps_decay_episodes: int = 10_000,
    dyna_n: int = 5,
    seed: int = 0,
    log_every: int = 500,
) -> dict:
    """Tabular Dyna-Q (deterministic single-sample model)."""
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    Q = np.zeros((N_STATES, N_ACTIONS), dtype=np.float64)
    # Model: (s, a) -> (r, s'); last-seen single-sample
    model: dict[tuple[int, int], tuple[float, int, bool]] = {}
    visited_keys: list[tuple[int, int]] = []
    returns: list[float] = []
    curve: list[tuple[int, float]] = []
    inadm = 0
    total_steps = 0

    obs, info = env.reset(seed=seed)
    for ep in range(num_episodes):
        if ep > 0:
            obs, info = env.reset()
        eps = _eps_schedule(ep, eps_start, eps_end, eps_decay_episodes)
        ep_return = 0.0
        while True:
            admissible = info["admissible_actions"]
            action = _select_action(Q[obs], admissible, eps, rng, use_mask=use_mask)
            if action not in admissible:
                inadm += 1
            next_obs, reward, terminated, truncated, next_info = env.step(action)
            if terminated:
                td_target = reward
            else:
                if use_mask:
                    next_admissible = next_info["admissible_actions"]
                    bootstrap = Q[next_obs, next_admissible].max()
                else:
                    bootstrap = Q[next_obs].max()
                td_target = reward + gamma * bootstrap
            Q[obs, action] += alpha * (td_target - Q[obs, action])

            # Update model
            key = (int(obs), int(action))
            if key not in model:
                visited_keys.append(key)
            model[key] = (float(reward), int(next_obs), bool(terminated))

            # Planning steps
            if visited_keys:
                idxs = rng.integers(0, len(visited_keys), size=dyna_n)
                for i in idxs:
                    s_p, a_p = visited_keys[i]
                    r_p, sn_p, term_p = model[(s_p, a_p)]
                    if term_p:
                        plan_target = r_p
                    else:
                        plan_target = r_p + gamma * Q[sn_p].max()
                    Q[s_p, a_p] += alpha * (plan_target - Q[s_p, a_p])

            obs, info = next_obs, next_info
            ep_return += float(reward)
            total_steps += 1
            if terminated or truncated:
                break
        returns.append(ep_return)
        if (ep + 1) % log_every == 0 or ep == 0:
            _record_curve_point(curve, ep + 1, returns)

    return {
        "Q": Q,
        "learning_curve": curve,
        "inadmissible_action_rate_training": float(inadm / max(1, total_steps)),
        "total_steps": int(total_steps),
        "num_episodes": int(num_episodes),
    }


def train_q_learning_expert(
    env: gym.Env,
    expert_policy: np.ndarray,
    *,
    expert_explore: bool = True,
    project_to_admissible: bool = False,
    num_episodes: int = 50_000,
    alpha: float = 0.1,
    gamma: float = 1.0,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    eps_decay_episodes: int = 10_000,
    seed: int = 0,
    log_every: int = 500,
    snapshot_every: int = 2_500,
) -> dict:
    """Q-learning whose exploration draws from an expert (clinician) prior.

    When an exploration step fires (prob eps):
      - expert_explore=False -> uniform random over all actions (vanilla);
      - expert_explore=True  -> sample from expert_policy[s];
      - project_to_admissible=True -> expert prior renormalised over the
        admissible set in s (so exploration never injects unsupported actions).

    Greedy steps and bootstrap are unmasked, isolating the effect of the
    exploration prior. Returns the usual dict plus `policy_snapshots`
    (list of (episode, argmax-policy)) for exact sample-efficiency curves.
    """
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    Q = np.zeros((N_STATES, N_ACTIONS), dtype=np.float64)
    returns: list[float] = []
    curve: list[tuple[int, float]] = []
    snapshots: list[tuple[int, list[int]]] = []
    inadm = 0
    total_steps = 0

    obs, info = env.reset(seed=seed)
    for ep in range(num_episodes):
        if ep > 0:
            obs, info = env.reset()
        eps = _eps_schedule(ep, eps_start, eps_end, eps_decay_episodes)
        while True:
            admissible = info["admissible_actions"]
            if rng.random() < eps:
                if expert_explore:
                    p = np.array(expert_policy[obs], dtype=np.float64)
                    if project_to_admissible:
                        keep = np.zeros_like(p)
                        keep[admissible] = 1.0
                        p = p * keep
                    tot = p.sum()
                    if tot > 0:
                        action = int(rng.choice(N_ACTIONS, p=p / tot))
                    else:
                        action = int(rng.choice(admissible))
                else:
                    action = int(rng.integers(0, N_ACTIONS))
            else:
                best_val = Q[obs].max()
                ties = np.flatnonzero(Q[obs] == best_val)
                action = int(ties[0]) if ties.size == 1 else int(rng.choice(ties))

            if action not in admissible:
                inadm += 1
            next_obs, reward, terminated, truncated, next_info = env.step(action)
            td_target = reward if terminated else reward + gamma * Q[next_obs].max()
            Q[obs, action] += alpha * (td_target - Q[obs, action])
            obs, info = next_obs, next_info
            total_steps += 1
            if terminated or truncated:
                returns.append(float(reward) if terminated else 0.0)
                break
        if (ep + 1) % log_every == 0 or ep == 0:
            _record_curve_point(curve, ep + 1, returns)
        if (ep + 1) % snapshot_every == 0:
            snapshots.append((ep + 1, Q.argmax(axis=1).astype(int).tolist()))

    return {
        "Q": Q,
        "learning_curve": curve,
        "policy_snapshots": snapshots,
        "inadmissible_action_rate_training": float(inadm / max(1, total_steps)),
        "total_steps": int(total_steps),
        "num_episodes": int(num_episodes),
    }


def greedy_policy_from_Q(
    Q: np.ndarray,
    admissible_mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Convert Q-table to deterministic argmax policy (N_S,). If admissible_mask
    given, restricts argmax to admissible cells."""
    if admissible_mask is None:
        return Q.argmax(axis=1).astype(np.int64)
    Q_masked = np.where(admissible_mask, Q, -np.inf)
    return Q_masked.argmax(axis=1).astype(np.int64)
