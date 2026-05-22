"""P2 (supplement): expert-guided exploration with admissible projection.

ICU-Sepsis ships an estimated clinician (expert) policy that places ~16% of its
probability mass on inadmissible (low-support) actions. We test whether using
the expert as an exploration prior speeds learning, and whether *projecting*
that prior onto the admissible set (so exploration never injects unsupported
actions) gives a better-supported, faster learner.

Cells (Q-learning, mean strategy, unmasked greedy/bootstrap):
  - vanilla            : uniform-random exploration
  - expert_raw         : exploration ~ expert_policy(s)
  - expert_projected   : exploration ~ expert_policy(s) renormalised on Adm(s)

Exact sample-efficiency curves via policy snapshots + value iteration.

Outputs:
  - results/expert_prior/<tag>.json, summary.json
  - figures/expert_prior_curve.png

Run: python scripts/run_expert_prior.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

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
    policy_agreement_with_expert,
    TERMINAL_STATES,
    N_STATES,
)
from src.tabular_rl import train_q_learning_expert  # noqa: E402

SEEDS = [0, 1, 2, 3, 4]
NUM_EPISODES = 50_000
NON_TERMINAL = np.array(
    [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
)
CELLS = {
    "vanilla": dict(expert_explore=False, project_to_admissible=False),
    "expert_raw": dict(expert_explore=True, project_to_admissible=False),
    "expert_projected": dict(expert_explore=True, project_to_admissible=True),
}


def run_one(name, kw, seed, d, V_star, admissible_mask):
    env = make_env("mean", seed=seed)
    t0 = time.time()
    out = train_q_learning_expert(
        env, d["expert_policy"], num_episodes=NUM_EPISODES, alpha=0.1, gamma=1.0,
        eps_start=1.0, eps_end=0.05, eps_decay_episodes=10_000,
        seed=seed, log_every=500, snapshot_every=2_500, **kw)
    wall = time.time() - t0

    # Exact distance-to-V* curve from snapshots
    dist_curve = []
    for ep, pi_list in out["policy_snapshots"]:
        pi = np.array(pi_list, dtype=np.int64)
        V_pi = compute_Vpi(pi, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-7)
        dist_curve.append((ep, float(distance_to_optimal(V_pi, V_star, d["d_0"]))))

    pi_final = out["Q"].argmax(axis=1).astype(np.int64)
    V_final = compute_Vpi(pi_final, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-8)
    a = pi_final[NON_TERMINAL]
    deploy_unsupp = float((~admissible_mask[NON_TERMINAL, a]).mean())
    return {
        "tag": f"{name}_seed{seed}", "cell": name, "config": {**kw, "seed": seed},
        "wall_time_train_sec": wall,
        "distance_curve": dist_curve,
        "inadmissible_action_rate_training": out["inadmissible_action_rate_training"],
        "final_policy_distance_to_Vstar": float(distance_to_optimal(V_final, V_star, d["d_0"])),
        "final_policy_value_dweighted": float(d["d_0"] @ V_final),
        "deployment_unsupported_state_frac": deploy_unsupp,
        "final_policy_agreement_with_expert": policy_agreement_with_expert(pi_final, d["expert_policy"]),
    }


def main():
    out_dir = ROOT / "results" / "expert_prior"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "expert_prior_curve.png"

    env = make_env("mean")
    d = get_dynamics(env)
    _, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    admissible_mask = admissible_mask_table(d["admissible_actions"])
    j_star = float(d["d_0"] @ V_star)

    # Report expert's own inadmissible mass for context
    expert = np.asarray(d["expert_policy"], dtype=np.float64)
    adm = admissible_mask[NON_TERMINAL]
    ex_nt = expert[NON_TERMINAL]
    inadm_mass = float((ex_nt * (~adm)).sum() / ex_nt.sum())
    print(f"J* = {j_star:.4f} | expert inadmissible mass (non-terminal) = {inadm_mass:.4f}")

    all_runs = []
    for name, kw in CELLS.items():
        for seed in SEEDS:
            r = run_one(name, kw, seed, d, V_star, admissible_mask)
            all_runs.append(r)
            json.dump(r, open(out_dir / f"{r['tag']}.json", "w"), indent=2)
            print(f"  {r['tag']:>22} | dist-V*={r['final_policy_distance_to_Vstar']:.4f} "
                  f"| unsafe-train={r['inadmissible_action_rate_training']:.3f} "
                  f"| deploy-unsupp={r['deployment_unsupported_state_frac']:.3f} "
                  f"| agree={r['final_policy_agreement_with_expert']:.3f}")

    keys = ["final_policy_distance_to_Vstar", "final_policy_value_dweighted",
            "inadmissible_action_rate_training", "deployment_unsupported_state_frac",
            "final_policy_agreement_with_expert"]
    summary = {"j_star_dweighted": j_star, "expert_inadmissible_mass": inadm_mass, "cells": {}}
    for cn in CELLS:
        rs = [r for r in all_runs if r["cell"] == cn]
        summary["cells"][cn] = {k + "_mean": float(np.mean([r[k] for r in rs])) for k in keys} | \
                               {k + "_std": float(np.std([r[k] for r in rs], ddof=1)) for k in keys}
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=2)

    # --- Figure: exact distance-to-V* sample-efficiency curves ---
    fig, ax = plt.subplots(figsize=(7.5, 5))
    colors = {"vanilla": "#d62728", "expert_raw": "#ff7f0e", "expert_projected": "#2ca02c"}
    labels = {"vanilla": "vanilla (uniform explore)",
              "expert_raw": "expert prior (raw)",
              "expert_projected": "expert prior (projected to admissible)"}
    for cn in CELLS:
        rs = [r for r in all_runs if r["cell"] == cn]
        eps_axis = [pt[0] for pt in rs[0]["distance_curve"]]
        arr = np.array([[pt[1] for pt in r["distance_curve"]] for r in rs])
        mean = arr.mean(axis=0)
        sem = arr.std(axis=0, ddof=1) / np.sqrt(arr.shape[0])
        ax.plot(eps_axis, mean, color=colors[cn], label=labels[cn], lw=2)
        ax.fill_between(eps_axis, mean - 1.96 * sem, mean + 1.96 * sem,
                        color=colors[cn], alpha=0.18)
    ax.set_xlabel("Training episodes")
    ax.set_ylabel("Distance-to-V*  (exact, lower = better)")
    ax.set_title(f"Expert-guided exploration sample efficiency\n"
                 f"(ICU-Sepsis v2 mean, 5 seeds, 95% CI; expert inadm. mass={inadm_mass:.2f})")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print("Figure saved:", fig_path)


if __name__ == "__main__":
    main()
