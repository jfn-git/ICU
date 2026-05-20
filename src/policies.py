"""Baseline policies (Random / Expert / Optimal) as callables."""

from __future__ import annotations

import numpy as np

from .env_utils import N_ACTIONS


class RandomPolicy:
    """Uniform-random action selection."""

    def __init__(self, n_actions: int = N_ACTIONS, rng: np.random.Generator | None = None):
        self.n_actions = n_actions
        self.rng = rng if rng is not None else np.random.default_rng()

    def __call__(self, state: int) -> int:
        return int(self.rng.integers(0, self.n_actions))


class ExpertPolicy:
    """Sample action from the env's estimated clinician policy."""

    def __init__(self, expert_policy: np.ndarray, rng: np.random.Generator | None = None):
        self.expert_policy = expert_policy
        self.rng = rng if rng is not None else np.random.default_rng()

    def __call__(self, state: int) -> int:
        p = self.expert_policy[state]
        return int(self.rng.choice(self.expert_policy.shape[1], p=p))


class DeterministicPolicy:
    """Wrap a (N_S,) table of argmax actions as a callable."""

    def __init__(self, action_table: np.ndarray):
        self.action_table = action_table.astype(np.int64)

    def __call__(self, state: int) -> int:
        return int(self.action_table[state])
