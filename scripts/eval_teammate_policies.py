"""Exact-evaluate the teammate's saved policies on the true ICU-Sepsis dynamics.

Her repo reports `final return` = last-1000-episode rollout mean (the benchmark
protocol), which is noisy and can exceed V*. We re-evaluate her saved deterministic
policies EXACTLY (value iteration on the known mean-strategy dynamics), putting her
results on the same exact-V* axis as the rest of our paper.

Reads:  policy_<method>_s<seed>.npy  from POLICY_DIR (her cloned repo, data/raw/)
Writes: results/teammate_exact_eval/summary.json  + prints a table.

Run: python scripts/eval_teammate_policies.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.env_utils import (  # noqa: E402
    admissible_mask_table,
    compute_Vpi,
    compute_Vstar,
    distance_to_optimal,
    get_dynamics,
    make_env,
    N_STATES,
    TERMINAL_STATES,
)

POLICY_DIR = ROOT / "results" / "teammate_policies"  # vendored from teammate repo
OUT_DIR = ROOT / "results" / "teammate_exact_eval"

# Her rollout "final return" (data/summary/e1_main_table.md) for side-by-side.
HER_ROLLOUT = {
    "Sarsa": 0.789, "QLearning": 0.785, "DQN_T": 0.787, "PPO_T": 0.833,
    "AA_Sarsa": 0.799, "AA_QLearning": 0.811, "AA_DQN_T": 0.823, "AA_PPO_T": 0.862,
    "AA_MBRL_UCB": 0.874, "AA_MBRL_Shaped": 0.871, "AA_MBRL_KL": 0.879,
    "AA_MBRL_Full": 0.877, "AA_PPO_Shaped": 0.866, "AA_PPO_KL": 0.866,
    "AA_PPO_Full": 0.857,
}
ORDER = list(HER_ROLLOUT) + ["AA_MBRL_greedy", "MBRL_UCB_noMask"]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = get_dynamics(make_env("mean"))
    tx, r, d0 = d["tx_mat"], d["r_mat"], d["d_0"]
    _, V_star = compute_Vstar(tx, r, gamma=1.0, tol=1e-9)
    j_star = float(d0 @ V_star)
    adm = admissible_mask_table(d["admissible_actions"])
    non_terminal = np.array([s for s in range(N_STATES) if s not in TERMINAL_STATES],
                            dtype=np.int64)
    print(f"J* (exact VI optimum) = {j_star:.4f}\n")

    # Group policy files by method.
    groups: dict[str, list[Path]] = defaultdict(list)
    for f in sorted(POLICY_DIR.glob("policy_*.npy")):
        m = re.match(r"policy_(.+)_s(\d+)\.npy", f.name)
        if m:
            groups[m.group(1)].append(f)

    rows = {}
    for method, files in groups.items():
        Js, dists, deploys = [], [], []
        for f in sorted(files):
            pi = np.load(f).astype(np.int64)            # (716,) action per state
            V_pi = compute_Vpi(pi, tx, r, gamma=1.0, tol=1e-8)
            Js.append(float(d0 @ V_pi))
            dists.append(distance_to_optimal(V_pi, V_star, d0))
            a = pi[non_terminal]
            deploys.append(float((~adm[non_terminal, a]).mean()))
        rows[method] = dict(
            n_seeds=len(files),
            J_mean=float(np.mean(Js)), J_std=float(np.std(Js, ddof=1)),
            dist_mean=float(np.mean(dists)), dist_std=float(np.std(dists, ddof=1)),
            deploy_unsupp_mean=float(np.mean(deploys)),
        )

    json.dump({"j_star": j_star, "methods": rows},
              open(OUT_DIR / "summary.json", "w"), indent=2)

    # Print table.
    hdr = f"{'method':<18}{'exact J':>16}{'her rollout':>13}{'Δ':>9}{'exact dist-V*':>15}{'deploy-unsupp':>15}"
    print(hdr); print("-" * len(hdr))
    seen = set()
    for method in ORDER + [m for m in rows if m not in ORDER]:
        if method not in rows or method in seen:
            continue
        seen.add(method)
        x = rows[method]
        her = HER_ROLLOUT.get(method)
        her_s = f"{her:.3f}" if her is not None else "  -  "
        delta = f"{x['J_mean']-her:+.3f}" if her is not None else "  -  "
        print(f"{method:<18}{x['J_mean']:>10.4f}±{x['J_std']:<4.3f}{her_s:>13}{delta:>9}"
              f"{x['dist_mean']:>13.4f}  {x['deploy_unsupp_mean']:>13.3f}")
    print(f"\nWrote {OUT_DIR/'summary.json'}")


if __name__ == "__main__":
    main()
