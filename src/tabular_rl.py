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
    num_episodes: int = 50_000,
    alpha: float = 0.1,
    gamma: float = 1.0,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    eps_decay_episodes: int = 10_000,
    seed: int = 0,
    log_every: int = 500,
) -> dict:
    """Tabular Q-learning. Logs learning curve as list of (episode, mean_return_last100).

    Returns dict: {Q, learning_curve, inadmissible_action_rate_training,
                  total_steps, num_episodes}.
    """
    rng = np.random.default_rng(seed)
    np.random.seed(seed)  # for _masked_argmax tiebreak
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
        ep_return = 0.0
        while True:
            admissible = info["admissible_actions"]
            action = _select_action(Q[obs], admissible, eps, rng, use_mask=use_mask)
            if action not in admissible:
                inadm += 1
            next_obs, reward, terminated, truncated, next_info = env.step(action)
            # Q-learning target: bootstrap over masked or unmasked max
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
