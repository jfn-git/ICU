"""T1: component ablation + Q-value-leakage diagnostic + conservative (CQL-style) cell.

Locates WHERE the inadmissible-action failure lives by masking each component
independently, and adds a value-level conservative remedy:

  vanilla        : mask nothing
  behavior_only  : mask only epsilon-greedy behavior
  target_only    : mask only the Bellman backup (max over admissible)
  policy_only    : train vanilla, mask only the final greedy policy at deployment
  full_mask      : mask behavior + target + final policy
  conservative_k1: CQL-style value conservatism toward admissible support (kappa=1)
  conservative_k2: same, kappa=2

Mechanistic diagnostic: Q-value leakage(s) = max_{a not in Adm(s)} Q(s,a)
                        - max_{a in Adm(s)} Q(s,a), averaged over non-terminal s.
Positive leakage => inadmissible actions are over-valued (the hidden failure).

All metrics exact (known dynamics). Outputs:
  - results/component_ablation/<tag>.json, summary.json
  - figures/component_ablation.png

Run: python scripts/run_component_ablation.py
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
from src.tabular_rl import greedy_policy_from_Q, train_q_learning  # noqa: E402

SEEDS = [0, 1, 2, 3, 4]
NUM_EPISODES = 50_000
SNAP = 2_500
NON_TERMINAL = np.array(
    [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
)

VARIANTS = {
    "vanilla":         dict(kw=dict(mask_behavior=False, mask_target=False), final_mask=False),
    "behavior_only":   dict(kw=dict(mask_behavior=True,  mask_target=False), final_mask=False),
    "target_only":     dict(kw=dict(mask_behavior=False, mask_target=True),  final_mask=False),
    "policy_only":     dict(kw=dict(mask_behavior=False, mask_target=False), final_mask=True),
    "full_mask":       dict(kw=dict(mask_behavior=True,  mask_target=True),  final_mask=True),
    "conservative_k1": dict(kw=dict(conservative_kappa=1.0), final_mask=False),
    "conservative_k2": dict(kw=dict(conservative_kappa=2.0), final_mask=False),
}
LEAKAGE_PLOT = ["vanilla", "behavior_only", "target_only", "full_mask", "conservative_k1"]


def q_leakage(Q, admissible_mask):
    Qnt = Q[NON_TERMINAL]
    adm = admissible_mask[NON_TERMINAL]
    neg = -1e9
    q_adm = np.where(adm, Qnt, neg).max(axis=1)
    q_inadm = np.where(~adm, Qnt, neg).max(axis=1)
    return float((q_inadm - q_adm).mean())


def run_one(name, spec, seed, d, V_star, admissible_mask):
    env = make_env("mean", seed=seed)
    t0 = time.time()
    out = train_q_learning(env, num_episodes=NUM_EPISODES, alpha=0.1, gamma=1.0,
                           eps_start=1.0, eps_end=0.05, eps_decay_episodes=10_000,
                           seed=seed, log_every=500, snapshot_every=SNAP, **spec["kw"])
    wall = time.time() - t0
    fm = admissible_mask if spec["final_mask"] else None

    dist_curve, leak_curve = [], []
    for ep, Q in out["q_snapshots"]:
        pi = greedy_policy_from_Q(Q, admissible_mask=fm)
        V_pi = compute_Vpi(pi, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-7)
        dist_curve.append((ep, float(distance_to_optimal(V_pi, V_star, d["d_0"]))))
        leak_curve.append((ep, q_leakage(Q, admissible_mask)))

    pi_final = greedy_policy_from_Q(out["Q"], admissible_mask=fm)
    V_final = compute_Vpi(pi_final, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-8)
    a = pi_final[NON_TERMINAL]
    deploy_unsupp = float((~admissible_mask[NON_TERMINAL, a]).mean())
    return {
        "tag": f"{name}_seed{seed}", "cell": name, "seed": seed,
        "wall_time_train_sec": wall,
        "distance_curve": dist_curve, "leakage_curve": leak_curve,
        "inadmissible_action_rate_training": out["inadmissible_action_rate_training"],
        "final_policy_distance_to_Vstar": float(distance_to_optimal(V_final, V_star, d["d_0"])),
        "final_policy_value_dweighted": float(d["d_0"] @ V_final),
        "deployment_unsupported_state_frac": deploy_unsupp,
        "final_q_leakage": q_leakage(out["Q"], admissible_mask),
        "final_policy_agreement_with_expert": policy_agreement_with_expert(pi_final, d["expert_policy"]),
    }


def main():
    out_dir = ROOT / "results" / "component_ablation"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "component_ablation.png"

    env = make_env("mean")
    d = get_dynamics(env)
    _, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    admissible_mask = admissible_mask_table(d["admissible_actions"])
    print(f"J* = {d['d_0'] @ V_star:.4f}")

    all_runs = []
    for name, spec in VARIANTS.items():
        for seed in SEEDS:
            r = run_one(name, spec, seed, d, V_star, admissible_mask)
            all_runs.append(r)
            json.dump(r, open(out_dir / f"{r['tag']}.json", "w"), indent=2)
            print(f"  {r['tag']:>20} | dist-V*={r['final_policy_distance_to_Vstar']:.4f} "
                  f"| leak={r['final_q_leakage']:+.4f} "
                  f"| deploy-unsupp={r['deployment_unsupported_state_frac']:.3f} "
                  f"| agree={r['final_policy_agreement_with_expert']:.3f}")

    keys = ["final_policy_distance_to_Vstar", "final_policy_value_dweighted",
            "inadmissible_action_rate_training", "deployment_unsupported_state_frac",
            "final_q_leakage", "final_policy_agreement_with_expert"]
    summary = {"j_star_dweighted": float(d["d_0"] @ V_star), "cells": {}}
    for cn in VARIANTS:
        rs = [r for r in all_runs if r["cell"] == cn]
        summary["cells"][cn] = {k + "_mean": float(np.mean([r[k] for r in rs])) for k in keys} | \
                               {k + "_std": float(np.std([r[k] for r in rs], ddof=1)) for k in keys}
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=2)
    print("\nSummary written:", out_dir / "summary.json")

    # --- Figure: (left) distance-to-V* bar; (right) Q-leakage curves ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    order = list(VARIANTS.keys())
    ys = [summary["cells"][c]["final_policy_distance_to_Vstar_mean"] for c in order]
    yerr = [summary["cells"][c]["final_policy_distance_to_Vstar_std"] for c in order]
    palette = {"vanilla": "#d62728", "behavior_only": "#ff7f0e", "target_only": "#9467bd",
               "policy_only": "#8c564b", "full_mask": "#1f77b4",
               "conservative_k1": "#2ca02c", "conservative_k2": "#17becf"}
    axes[0].bar(range(len(order)), ys, yerr=yerr, capsize=4,
                color=[palette[c] for c in order], alpha=0.88)
    axes[0].set_xticks(range(len(order)))
    axes[0].set_xticklabels(order, rotation=35, ha="right", fontsize=9)
    axes[0].set_ylabel("Distance-to-V* (lower = better)")
    axes[0].set_title("Component ablation: which mask recovers value?")
    axes[0].grid(True, axis="y", alpha=0.3)
    for i, c in enumerate(order):
        u = summary["cells"][c]["deployment_unsupported_state_frac_mean"]
        axes[0].text(i, ys[i], f"u={u:.2f}", ha="center", va="bottom", fontsize=7)

    for cn in LEAKAGE_PLOT:
        rs = [r for r in all_runs if r["cell"] == cn]
        eps_axis = [pt[0] for pt in rs[0]["leakage_curve"]]
        arr = np.array([[pt[1] for pt in r["leakage_curve"]] for r in rs])
        mean = arr.mean(axis=0)
        sem = arr.std(axis=0, ddof=1) / np.sqrt(arr.shape[0])
        axes[1].plot(eps_axis, mean, color=palette[cn], label=cn, lw=2)
        axes[1].fill_between(eps_axis, mean - 1.96 * sem, mean + 1.96 * sem,
                             color=palette[cn], alpha=0.15)
    axes[1].axhline(0, color="black", lw=0.8, ls="--", alpha=0.6)
    axes[1].set_xlabel("Training episodes")
    axes[1].set_ylabel("Q-value leakage  (max inadmissible Q − max admissible Q)")
    axes[1].set_title("Mechanism: value leakage from unsupported actions")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=8)

    fig.suptitle("ICU-Sepsis (v2, mean): component ablation & value-leakage mechanism "
                 "(Q-learning, 5 seeds × 50k eps, exact V*)", fontsize=11)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print("Figure saved:", fig_path)


if __name__ == "__main__":
    main()
