"""Bundle-C preliminary ablation: Q-learning, mean strategy, mask on vs off.

Runs 5 seeds × {mask=off, mask=on} × 50k episodes on Sepsis/ICU-Sepsis-v2,
computes:
  - learning curve (smoothed over last 100 episodes, logged every 500),
  - training-time inadmissible-action rate,
  - final-policy distance-to-V*,
  - final-policy unsafe-rate-deployed (rollout, 2 000 episodes),
  - final-policy policy-agreement-with-expert.

Saves per-run JSON to results/, aggregated summary to
results/masking_ablation_summary.json, and the preliminary curve to
figures/preliminary_curve.png.
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
)
from src.evaluate import rollout_eval  # noqa: E402
from src.policies import DeterministicPolicy  # noqa: E402
from src.tabular_rl import greedy_policy_from_Q, train_q_learning  # noqa: E402


def run_one(strategy: str, use_mask: bool, seed: int, num_episodes: int,
            d, V_star, admissible_mask) -> dict:
    env = make_env(strategy, seed=seed)
    t0 = time.time()
    out = train_q_learning(
        env,
        use_mask=use_mask,
        num_episodes=num_episodes,
        alpha=0.1,
        gamma=1.0,
        eps_start=1.0,
        eps_end=0.05,
        eps_decay_episodes=10_000,
        seed=seed,
        log_every=500,
    )
    wall_train = time.time() - t0

    pi = greedy_policy_from_Q(
        out["Q"], admissible_mask=admissible_mask if use_mask else None
    )
    V_pi = compute_Vpi(pi, d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-8)
    gap = distance_to_optimal(V_pi, V_star, d["d_0"])
    final_return_dweighted = float(d["d_0"] @ V_pi)
    agree = policy_agreement_with_expert(pi, d["expert_policy"])

    # Rollout the learned greedy policy
    env_eval = make_env(strategy, seed=seed + 10_000)
    rollout = rollout_eval(
        env_eval,
        DeterministicPolicy(pi),
        num_episodes=2_000,
        seed=seed + 10_000,
    )

    return {
        "config": {
            "strategy": strategy,
            "use_mask": use_mask,
            "seed": seed,
            "num_episodes": num_episodes,
            "algo": "q_learning",
            "alpha": 0.1, "gamma": 1.0,
            "eps_start": 1.0, "eps_end": 0.05, "eps_decay_episodes": 10_000,
        },
        "wall_time_train_sec": wall_train,
        "learning_curve": out["learning_curve"],
        "inadmissible_action_rate_training": out["inadmissible_action_rate_training"],
        "total_env_steps_training": out["total_steps"],
        "final_policy_distance_to_Vstar": float(gap),
        "final_policy_value_dweighted": final_return_dweighted,
        "final_policy_agreement_with_expert": agree,
        "final_policy_rollout_return_mean": rollout["return_mean"],
        "final_policy_rollout_return_stderr": rollout["return_stderr"],
        "final_policy_rollout_unsafe_rate_deployed": rollout.get(
            "unsafe_rate_deployed"
        ),
    }


def main():
    out_dir = ROOT / "results" / "bundle_c_masking"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "preliminary_curve.png"
    fig_path.parent.mkdir(exist_ok=True)

    # Precompute env-derived constants once.
    env = make_env("mean")
    d = get_dynamics(env)
    print("Computing V* via value iteration...")
    t0 = time.time()
    _, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    print(f"  V* computed in {time.time() - t0:.2f}s, d_0-weighted J* = {d['d_0'] @ V_star:.4f}")
    admissible_mask = admissible_mask_table(d["admissible_actions"])

    seeds = [0, 1, 2, 3, 4]
    num_episodes = 50_000
    cells = [
        ("mean", False),
        ("mean", True),
    ]
    all_runs = []
    for strategy, use_mask in cells:
        for seed in seeds:
            tag = f"qlearning_{strategy}_mask{'on' if use_mask else 'off'}_seed{seed}"
            print(f"\n>>> {tag}")
            res = run_one(strategy, use_mask, seed, num_episodes,
                          d, V_star, admissible_mask)
            res["tag"] = tag
            all_runs.append(res)
            with open(out_dir / f"{tag}.json", "w") as f:
                json.dump(res, f, indent=2)
            print(
                f"    train {res['wall_time_train_sec']:.1f}s | "
                f"dist-to-V* = {res['final_policy_distance_to_Vstar']:.4f} | "
                f"J(π) = {res['final_policy_value_dweighted']:.4f} | "
                f"unsafe-train = {res['inadmissible_action_rate_training']:.4f} | "
                f"unsafe-deployed = {res['final_policy_rollout_unsafe_rate_deployed']:.4f} | "
                f"agree = {res['final_policy_agreement_with_expert']:.3f}"
            )

    # --- Aggregate ---
    def by_cell(name_a, name_b, runs, key):
        a = [r[key] for r in runs if not r["config"]["use_mask"]]
        b = [r[key] for r in runs if r["config"]["use_mask"]]
        return np.array(a), np.array(b)

    a_dist, b_dist = by_cell("off", "on", all_runs, "final_policy_distance_to_Vstar")
    a_unsafe, b_unsafe = by_cell("off", "on", all_runs, "inadmissible_action_rate_training")
    a_J, b_J = by_cell("off", "on", all_runs, "final_policy_value_dweighted")
    a_agree, b_agree = by_cell("off", "on", all_runs, "final_policy_agreement_with_expert")

    summary = {
        "j_star_dweighted": float(d["d_0"] @ V_star),
        "mask_off": {
            "distance_to_Vstar_mean": float(a_dist.mean()),
            "distance_to_Vstar_std": float(a_dist.std(ddof=1)),
            "unsafe_train_mean": float(a_unsafe.mean()),
            "unsafe_train_std": float(a_unsafe.std(ddof=1)),
            "J_pi_mean": float(a_J.mean()),
            "J_pi_std": float(a_J.std(ddof=1)),
            "agree_mean": float(a_agree.mean()),
            "agree_std": float(a_agree.std(ddof=1)),
        },
        "mask_on": {
            "distance_to_Vstar_mean": float(b_dist.mean()),
            "distance_to_Vstar_std": float(b_dist.std(ddof=1)),
            "unsafe_train_mean": float(b_unsafe.mean()),
            "unsafe_train_std": float(b_unsafe.std(ddof=1)),
            "J_pi_mean": float(b_J.mean()),
            "J_pi_std": float(b_J.std(ddof=1)),
            "agree_mean": float(b_agree.mean()),
            "agree_std": float(b_agree.std(ddof=1)),
        },
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSummary:")
    print(json.dumps(summary, indent=2))

    # --- Plot ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    j_star = float(d["d_0"] @ V_star)
    colors = {False: "#d62728", True: "#1f77b4"}
    labels = {False: "mask OFF (vanilla Q-learning)", True: "mask ON (action masking)"}

    for use_mask in (False, True):
        # All runs with this use_mask; align learning curves on common episode grid.
        curves = [r["learning_curve"] for r in all_runs
                  if r["config"]["use_mask"] == use_mask]
        # Each curve is list of (episode, mean_return_last100). Episodes already aligned.
        eps_axis = [pt[0] for pt in curves[0]]
        ret_arr = np.array([[pt[1] for pt in c] for c in curves])
        mean = ret_arr.mean(axis=0)
        sem = ret_arr.std(axis=0, ddof=1) / np.sqrt(ret_arr.shape[0])
        ci_lo = mean - 1.96 * sem
        ci_hi = mean + 1.96 * sem

        # Learning curve panel
        axes[0].plot(eps_axis, mean, color=colors[use_mask], label=labels[use_mask], linewidth=1.7)
        axes[0].fill_between(eps_axis, ci_lo, ci_hi, color=colors[use_mask], alpha=0.18)

    axes[0].axhline(j_star, ls="--", lw=1.0, color="black", alpha=0.7,
                    label=f"J(π*) = {j_star:.3f}")
    axes[0].set_xlabel("Training episodes")
    axes[0].set_ylabel("Mean return (smoothed, last 100 eps)")
    axes[0].set_title("Q-learning learning curves (mean strategy, 5 seeds, 95% CI)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="lower right", fontsize=9)

    # Bar of training-time inadmissible-action rate (mean ± std)
    bars_x = ["mask OFF", "mask ON"]
    bars_h = [a_unsafe.mean(), b_unsafe.mean()]
    bars_e = [a_unsafe.std(ddof=1), b_unsafe.std(ddof=1)]
    axes[1].bar(bars_x, bars_h, yerr=bars_e, capsize=6,
                color=[colors[False], colors[True]], alpha=0.85)
    axes[1].set_ylabel("Inadmissible-action rate (training)")
    axes[1].set_title("Training-time inadmissible-action rate (mean ± std)")
    axes[1].set_ylim(0, max(0.05, max(bars_h) * 1.25))
    axes[1].grid(True, axis="y", alpha=0.3)
    for x, (h, e) in enumerate(zip(bars_h, bars_e)):
        axes[1].text(x, h + e + 0.01, f"{h:.3f}", ha="center", fontsize=10)

    fig.suptitle(
        "ICU-Sepsis (v2, mean strategy): Action masking ablation — preliminary, "
        f"5 seeds × {num_episodes // 1000}k eps",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print(f"\nFigure saved: {fig_path}")

    return all_runs, summary


if __name__ == "__main__":
    main()
