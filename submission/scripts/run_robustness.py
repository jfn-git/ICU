"""T3: robustness across TD algorithms and inadmissible-action strategies.

Shows the hidden-failure / masking-fix is not specific to Q-learning or to the
`mean` strategy:

  algos     : q_learning, sarsa, dyna_q
  strategies: mean      (inadmissible -> average admissible transition; hides it)
              terminate (inadmissible -> death; makes the signal explicit)
  remedy    : vanilla (mask off) vs full admissibility mask (mask on)

Evaluation is exact. Because the env's stored `tx_mat` is identical across
strategies (the strategy is applied at step time, not in the model), we build
the `terminate` evaluation dynamics explicitly: every inadmissible (s,a) routes
to the death state with reward 0.

Outputs:
  - results/robustness/<tag>.json, summary.json
  - figures/robustness.png

Run: python scripts/run_robustness.py
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
    STATE_DEATH,
    TERMINAL_STATES,
    N_STATES,
)
from src.tabular_rl import (  # noqa: E402
    greedy_policy_from_Q,
    train_q_learning,
    train_sarsa,
    train_dyna_q,
)

SEEDS = [0, 1, 2, 3, 4]
NUM_EPISODES = 50_000
NON_TERMINAL = np.array(
    [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
)
TRAINERS = {"q_learning": train_q_learning, "sarsa": train_sarsa, "dyna_q": train_dyna_q}


def make_terminate_dynamics(tx, r, admissible_mask):
    """inadmissible (s,a) -> death deterministically, reward 0 (terminate strategy)."""
    txd, rd = tx.copy(), r.copy()
    for s in NON_TERMINAL:
        for a in range(tx.shape[1]):
            if not admissible_mask[s, a]:
                txd[s, a, :] = 0.0
                txd[s, a, STATE_DEATH] = 1.0
                rd[s, a, :] = 0.0
    return txd, rd


def run_one(algo, strategy, use_mask, seed, tx_eval, r_eval, V_star, d0,
            admissible_mask, expert):
    env = make_env(strategy, seed=seed)
    trainer = TRAINERS[algo]
    out = trainer(env, use_mask=use_mask, num_episodes=NUM_EPISODES, alpha=0.1,
                  gamma=1.0, eps_start=1.0, eps_end=0.05, eps_decay_episodes=10_000,
                  seed=seed, log_every=2_000)
    pi = greedy_policy_from_Q(out["Q"], admissible_mask=admissible_mask if use_mask else None)
    V_pi = compute_Vpi(pi, tx_eval, r_eval, gamma=1.0, tol=1e-8)
    a = pi[NON_TERMINAL]
    deploy_unsupp = float((~admissible_mask[NON_TERMINAL, a]).mean())
    return {
        "tag": f"{algo}_{strategy}_mask{'on' if use_mask else 'off'}_seed{seed}",
        "algo": algo, "strategy": strategy, "use_mask": use_mask, "seed": seed,
        "final_policy_distance_to_Vstar": float(distance_to_optimal(V_pi, V_star, d0)),
        "final_policy_value_dweighted": float(d0 @ V_pi),
        "inadmissible_action_rate_training": out["inadmissible_action_rate_training"],
        "deployment_unsupported_state_frac": deploy_unsupp,
    }


def main():
    out_dir = ROOT / "results" / "robustness"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "robustness.png"

    base = get_dynamics(make_env("mean"))
    tx, r, d0 = base["tx_mat"], base["r_mat"], base["d_0"]
    admissible_mask = admissible_mask_table(base["admissible_actions"])
    expert = base["expert_policy"]

    # Per-strategy evaluation dynamics + V*
    eval_dyn = {"mean": (tx, r)}
    txd, rd = make_terminate_dynamics(tx, r, admissible_mask)
    eval_dyn["terminate"] = (txd, rd)
    Vstar = {}
    for strat, (txe, re) in eval_dyn.items():
        _, Vs = compute_Vstar(txe, re, gamma=1.0, tol=1e-9)
        Vstar[strat] = Vs
        print(f"strategy={strat}: J* = {d0 @ Vs:.4f}")

    all_runs = []
    for strategy in ("mean", "terminate"):
        txe, re = eval_dyn[strategy]
        for algo in TRAINERS:
            for use_mask in (False, True):
                t0 = time.time()
                for seed in SEEDS:
                    rr = run_one(algo, strategy, use_mask, seed, txe, re,
                                 Vstar[strategy], d0, admissible_mask, expert)
                    all_runs.append(rr)
                    json.dump(rr, open(out_dir / f"{rr['tag']}.json", "w"), indent=2)
                cell = [x for x in all_runs if x["algo"] == algo and x["strategy"] == strategy
                        and x["use_mask"] == use_mask]
                md = np.mean([x["final_policy_distance_to_Vstar"] for x in cell])
                mu = np.mean([x["deployment_unsupported_state_frac"] for x in cell])
                print(f"  {algo:>10} | {strategy:>9} | mask={'on ' if use_mask else 'off'} "
                      f"| dist-V*={md:.4f} | deploy-unsupp={mu:.3f} | {time.time()-t0:.0f}s/5seeds")

    # --- Aggregate ---
    def agg(algo, strategy, use_mask, key):
        xs = [x[key] for x in all_runs if x["algo"] == algo and x["strategy"] == strategy
              and x["use_mask"] == use_mask]
        return float(np.mean(xs)), float(np.std(xs, ddof=1))

    summary = {"cells": {}}
    for strategy in ("mean", "terminate"):
        for algo in TRAINERS:
            for use_mask in (False, True):
                m, s = agg(algo, strategy, use_mask, "final_policy_distance_to_Vstar")
                mu, su = agg(algo, strategy, use_mask, "deployment_unsupported_state_frac")
                summary["cells"][f"{algo}_{strategy}_mask{'on' if use_mask else 'off'}"] = {
                    "distance_to_Vstar_mean": m, "distance_to_Vstar_std": s,
                    "deployment_unsupported_mean": mu, "deployment_unsupported_std": su,
                }
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=2)

    # --- Figure: 2 panels (mean | terminate); x=algo; bars vanilla vs mask ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    algos = list(TRAINERS.keys())
    width = 0.35
    x = np.arange(len(algos))
    for ax, strategy in zip(axes, ("mean", "terminate")):
        off = [agg(a, strategy, False, "final_policy_distance_to_Vstar")[0] for a in algos]
        off_e = [agg(a, strategy, False, "final_policy_distance_to_Vstar")[1] for a in algos]
        on = [agg(a, strategy, True, "final_policy_distance_to_Vstar")[0] for a in algos]
        on_e = [agg(a, strategy, True, "final_policy_distance_to_Vstar")[1] for a in algos]
        ax.bar(x - width / 2, off, width, yerr=off_e, capsize=4, label="vanilla", color="#d62728", alpha=0.85)
        ax.bar(x + width / 2, on, width, yerr=on_e, capsize=4, label="full mask", color="#1f77b4", alpha=0.85)
        for i, a in enumerate(algos):
            uoff = agg(a, strategy, False, "deployment_unsupported_state_frac")[0]
            ax.text(i - width / 2, off[i], f"u={uoff:.2f}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels(algos, rotation=15)
        ax.set_title(f"strategy = {strategy}")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("Distance-to-V* (lower = better)")
    fig.suptitle("ICU-Sepsis: robustness of the hidden-failure / masking-fix across "
                 "TD algorithms and strategies (5 seeds, exact eval)\n"
                 "u = deployed unsupported-action rate of vanilla", fontsize=11)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print("Figure saved:", fig_path)


if __name__ == "__main__":
    main()
