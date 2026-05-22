"""P1 (spine): OOD-action remedy spectrum on ICU-Sepsis (mean strategy).

Compares a spectrum of remedies for inadmissible (out-of-distribution / low
data-support) actions, all evaluated with EXACT value metrics (known dynamics):

    vanilla  ->  support penalty(lambda) sweep  ->  hard admissibility mask

For each run we report (exactly, no rollout noise):
  - distance-to-V*  (E_{s~d0}[V*-V^pi])
  - J(pi)           (d0-weighted policy value)
  - training-time inadmissible-action rate
  - deployment unsupported-action rate  (state-count and visitation-weighted)
  - agreement-with-expert

Outputs:
  - results/penalty_sweep/<tag>.json           (per run)
  - results/penalty_sweep/summary.json         (per cell, mean +- std)
  - figures/penalty_tradeoff.png               (trade-off frontier + curves)

Run: python scripts/run_penalty_sweep.py
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
from src.deadend import state_occupancy  # noqa: E402
from src.tabular_rl import greedy_policy_from_Q, train_q_learning  # noqa: E402

SEEDS = [0, 1, 2, 3, 4]
NUM_EPISODES = 50_000
LAMBDAS = [0.01, 0.05, 0.1, 0.5, 1.0]
NON_TERMINAL = np.array(
    [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
)


def deployment_unsupported(pi, admissible_mask, tx_mat, d_0):
    """Fraction of non-terminal states (and visitation-weighted) where the
    greedy policy picks an inadmissible action."""
    a = pi[NON_TERMINAL]
    inadm = ~admissible_mask[NON_TERMINAL, a]
    state_frac = float(inadm.mean())
    occ = state_occupancy(pi, tx_mat, d_0)[NON_TERMINAL]
    w = occ / occ.sum() if occ.sum() > 0 else occ
    visit_frac = float((w * inadm).sum())
    return state_frac, visit_frac


def cells():
    yield ("vanilla", dict(use_mask=False, inadmissible_penalty=0.0))
    for lam in LAMBDAS:
        yield (f"penalty{lam}", dict(use_mask=False, inadmissible_penalty=lam))
    yield ("hardmask", dict(use_mask=True, inadmissible_penalty=0.0))


def run_one(name, kw, seed, d, V_star, admissible_mask):
    env = make_env("mean", seed=seed)
    t0 = time.time()
    out = train_q_learning(env, num_episodes=NUM_EPISODES, alpha=0.1, gamma=1.0,
                           eps_start=1.0, eps_end=0.05, eps_decay_episodes=10_000,
                           seed=seed, log_every=500, **kw)
    wall = time.time() - t0
    use_mask = kw["use_mask"]
    pi = greedy_policy_from_Q(out["Q"], admissible_mask=admissible_mask if use_mask else None)
    V_pi = compute_Vpi(pi, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-8)
    gap = distance_to_optimal(V_pi, V_star, d["d_0"])
    state_frac, visit_frac = deployment_unsupported(pi, admissible_mask, d["tx_mat"], d["d_0"])
    return {
        "tag": f"{name}_seed{seed}", "cell": name, "config": {**kw, "seed": seed},
        "wall_time_train_sec": wall,
        "learning_curve": out["learning_curve"],
        "inadmissible_action_rate_training": out["inadmissible_action_rate_training"],
        "final_policy_distance_to_Vstar": float(gap),
        "final_policy_value_dweighted": float(d["d_0"] @ V_pi),
        "deployment_unsupported_state_frac": state_frac,
        "deployment_unsupported_visit_frac": visit_frac,
        "final_policy_agreement_with_expert": policy_agreement_with_expert(pi, d["expert_policy"]),
    }


def main():
    out_dir = ROOT / "results" / "penalty_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "penalty_tradeoff.png"

    env = make_env("mean")
    d = get_dynamics(env)
    _, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    admissible_mask = admissible_mask_table(d["admissible_actions"])
    j_star = float(d["d_0"] @ V_star)
    print(f"J* = {j_star:.4f}")

    all_runs = []
    for name, kw in cells():
        for seed in SEEDS:
            r = run_one(name, kw, seed, d, V_star, admissible_mask)
            all_runs.append(r)
            json.dump(r, open(out_dir / f"{r['tag']}.json", "w"), indent=2)
            print(f"  {r['tag']:>18} | dist-V*={r['final_policy_distance_to_Vstar']:.4f} "
                  f"| unsafe-train={r['inadmissible_action_rate_training']:.3f} "
                  f"| unsupp-deploy(visit)={r['deployment_unsupported_visit_frac']:.3f} "
                  f"| agree={r['final_policy_agreement_with_expert']:.3f}")

    # --- Aggregate per cell ---
    cell_names = [c[0] for c in cells()]
    summary = {"j_star_dweighted": j_star, "cells": {}}
    keys = ["final_policy_distance_to_Vstar", "final_policy_value_dweighted",
            "inadmissible_action_rate_training", "deployment_unsupported_state_frac",
            "deployment_unsupported_visit_frac", "final_policy_agreement_with_expert"]
    for cn in cell_names:
        rs = [r for r in all_runs if r["cell"] == cn]
        summary["cells"][cn] = {
            k + "_mean": float(np.mean([r[k] for r in rs])) for k in keys
        } | {k + "_std": float(np.std([r[k] for r in rs], ddof=1)) for k in keys}
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=2)
    print("\nSummary written:", out_dir / "summary.json")

    # --- Figure: trade-off frontier + distance bars ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    order = cell_names
    xs = [summary["cells"][cn]["deployment_unsupported_visit_frac_mean"] for cn in order]
    ys = [summary["cells"][cn]["final_policy_distance_to_Vstar_mean"] for cn in order]
    yerr = [summary["cells"][cn]["final_policy_distance_to_Vstar_std"] for cn in order]
    xerr = [summary["cells"][cn]["deployment_unsupported_visit_frac_std"] for cn in order]

    ax = axes[0]
    ax.errorbar(xs, ys, xerr=xerr, yerr=yerr, fmt="none", ecolor="gray",
                alpha=0.5, capsize=3, zorder=1)
    for cn, x, y in zip(order, xs, ys):
        if cn == "vanilla":
            c, m = "#d62728", "s"
        elif cn == "hardmask":
            c, m = "#1f77b4", "D"
        else:
            c, m = "#2ca02c", "o"
        ax.scatter([x], [y], color=c, marker=m, s=80, zorder=2, edgecolor="k", linewidth=0.5)
        ax.annotate(cn.replace("penalty", "λ="), (x, y), textcoords="offset points",
                    xytext=(6, 5), fontsize=8)
    ax.set_xlabel("Deployment unsupported-action rate (visitation-weighted)")
    ax.set_ylabel("Distance-to-V*  (lower = better)")
    ax.set_title("OOD-action remedy spectrum: support–value trade-off")
    ax.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.bar(range(len(order)), ys, yerr=yerr, capsize=4,
            color=["#d62728" if c == "vanilla" else "#1f77b4" if c == "hardmask"
                   else "#2ca02c" for c in order], alpha=0.85)
    ax2.set_xticks(range(len(order)))
    ax2.set_xticklabels([o.replace("penalty", "λ=") for o in order], rotation=30, ha="right")
    ax2.set_ylabel("Distance-to-V*")
    ax2.set_title("Distance-to-V* by remedy (5 seeds, mean ± std)")
    ax2.grid(True, axis="y", alpha=0.3)

    fig.suptitle("ICU-Sepsis (v2, mean): exact evaluation of OOD-action remedies "
                 "(Q-learning, 5 seeds × 50k eps)", fontsize=11)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print("Figure saved:", fig_path)


if __name__ == "__main__":
    main()
