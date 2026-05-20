"""Rollout-based policy evaluation."""

from __future__ import annotations

from typing import Callable

import gymnasium as gym
import numpy as np


def rollout_eval(
    env: gym.Env,
    policy: Callable[[int], int],
    *,
    num_episodes: int = 5_000,
    seed: int = 0,
    track_inadmissible: bool = True,
) -> dict:
    """Roll out `policy` for `num_episodes` episodes and return aggregate stats.

    The env is reset with seed=seed at the start; subsequent resets use the
    env's internal rng to ensure episode independence yet seed-reproducibility.

    Returns dict with keys:
        return_mean, return_std, return_stderr, ep_len_mean, ep_len_std,
        unsafe_rate_deployed (only if `track_inadmissible` and env exposes
        `admissible_actions` in info),
        num_episodes_completed.
    """
    returns = np.zeros(num_episodes, dtype=np.float64)
    ep_lens = np.zeros(num_episodes, dtype=np.int64)
    inadm_steps = 0
    total_steps = 0

    obs, info = env.reset(seed=seed)
    for ep in range(num_episodes):
        if ep > 0:
            obs, info = env.reset()
        ep_return = 0.0
        ep_len = 0
        while True:
            action = policy(obs)
            admissible = info.get("admissible_actions", None)
            if track_inadmissible and admissible is not None:
                if action not in admissible:
                    inadm_steps += 1
            obs, reward, terminated, truncated, info = env.step(action)
            ep_return += float(reward)
            ep_len += 1
            total_steps += 1
            if terminated or truncated:
                break
        returns[ep] = ep_return
        ep_lens[ep] = ep_len

    out = {
        "return_mean": float(returns.mean()),
        "return_std": float(returns.std(ddof=0)),
        "return_stderr": float(returns.std(ddof=0) / np.sqrt(num_episodes)),
        "ep_len_mean": float(ep_lens.mean()),
        "ep_len_std": float(ep_lens.std(ddof=0)),
        "num_episodes_completed": int(num_episodes),
        "total_env_steps": int(total_steps),
    }
    if track_inadmissible and total_steps > 0:
        out["unsafe_rate_deployed"] = float(inadm_steps / total_steps)
    return out
