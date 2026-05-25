"""Verify Eq.(mean): in the shipped ICU-Sepsis `mean`-strategy dynamics, every
inadmissible action's transition row equals the unweighted mean of the admissible
rows in that state.

For each non-terminal state s with at least one inadmissible action a:
    P(.|s,a)  ?=  (1/|Adm(s)|) * sum_{a' in Adm(s)} P(.|s,a')

Reports the global maximum absolute deviation over all (s, inadmissible a) pairs.
Also reports the transition row-sum tolerance for reference (a *different* check).

Run: python scripts/verify_mean_imputation.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.env_utils import get_dynamics, make_env, TERMINAL_STATES, N_STATES  # noqa: E402


def main() -> None:
    d = get_dynamics(make_env("mean"))
    tx = d["tx_mat"]                       # (S, A, S)
    admissible = d["admissible_actions"]   # list[list[int]]

    max_dev = 0.0
    worst = None
    n_pairs = 0
    n_states_checked = 0

    for s in range(N_STATES):
        if s in TERMINAL_STATES:
            continue
        adm = list(admissible[s])
        if not adm:
            continue
        inadm = [a for a in range(tx.shape[1]) if a not in adm]
        if not inadm:
            continue
        n_states_checked += 1
        mean_row = tx[s, adm, :].mean(axis=0)          # admissible mean transition
        for a in inadm:
            dev = float(np.max(np.abs(tx[s, a, :] - mean_row)))
            n_pairs += 1
            if dev > max_dev:
                max_dev = dev
                worst = (s, a)

    # Reference: row-sum tolerance over admissible (s,a) cells (a DIFFERENT check).
    row_sums = np.array([tx[s, a].sum() for s in range(N_STATES) for a in admissible[s]])
    rowsum_dev = float(np.max(np.abs(row_sums - 1.0)))

    print(f"non-terminal states checked : {n_states_checked}")
    print(f"(s, inadmissible a) pairs   : {n_pairs}")
    print(f"MAX |P(.|s,a_inadm) - mean_admissible|  = {max_dev:.3e}   at (s,a)={worst}")
    print(f"[reference] max |row_sum - 1|           = {rowsum_dev:.3e}")
    print()
    if max_dev < 1e-12:
        print(f"=> Eq.(mean) holds to machine precision (<=1e-12). Report value: {max_dev:.1e}")
    else:
        print(f"=> Eq.(mean) deviation is {max_dev:.3e} -- NOT machine precision; investigate.")


if __name__ == "__main__":
    main()
