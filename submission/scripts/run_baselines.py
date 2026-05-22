"""Tbl 1: exact baseline reproduction (Random / Expert / Optimal).

Computes d0-weighted policy value J(pi) = E_{s~d0}[V^pi(s)] exactly via policy
evaluation on the known dynamics (gamma=1, so J = benchmark survival rate).
Matches the ICU-Sepsis paper's Random ~0.78 / Expert ~0.78 / Optimal ~0.88.

Outputs: results/baselines/summary.json

Run: python scripts/run_baselines.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.env_utils import (  # noqa: E402
    N_ACTIONS,
    compute_Vpi,
    compute_Vstar,
    get_dynamics,
    make_env,
)


def main():
    out_dir = ROOT / "results" / "baselines"
    out_dir.mkdir(parents=True, exist_ok=True)

    env = make_env("mean")
    d = get_dynamics(env)
    tx, r, d0 = d["tx_mat"], d["r_mat"], d["d_0"]

    optimal_pi, V_star = compute_Vstar(tx, r, gamma=1.0, tol=1e-9)
    J_opt = float(d0 @ V_star)

    random_pi = np.full((tx.shape[0], N_ACTIONS), 1.0 / N_ACTIONS)
    J_rand = float(d0 @ compute_Vpi(random_pi, tx, r, gamma=1.0, tol=1e-9))

    expert = np.asarray(d["expert_policy"], dtype=np.float64)
    J_expert = float(d0 @ compute_Vpi(expert, tx, r, gamma=1.0, tol=1e-9))

    summary = {
        "metric": "d0_weighted_policy_value (= survival rate, gamma=1)",
        "Random": J_rand,
        "Expert": J_expert,
        "Optimal": J_opt,
        "paper_reference": {"Random": 0.78, "Expert": 0.78, "Optimal": 0.88},
    }
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
