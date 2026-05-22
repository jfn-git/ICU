"""P0: Exact dead-end / harm-structure analysis on ICU-Sepsis (zero training).

Uses only the known dynamics + exact V* (= max survival probability, since
reward is a survival indicator and gamma=1). Produces:
  - results/deadend/summary.json
  - results/deadend/sofa_vs_vstar.json
  - figures/deadend_structure.png  (3 panels)

Run: python scripts/run_deadend_analysis.py
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
    compute_Vstar,
    get_dynamics,
    make_env,
)
from src.deadend import (  # noqa: E402
    compute_Qstar,
    deadend_structure,
    non_terminal_states,
    policy_harm_mass,
)


def sofa_bucketed_vstar(V_star, sofa, num_buckets=5):
    T = non_terminal_states()
    Vt, sofa_t = V_star[T], sofa[T]
    edges = np.quantile(sofa_t, np.linspace(0, 1, num_buckets + 1))
    edges[-1] += 1e-9
    centers = 0.5 * (edges[:-1] + edges[1:])
    mean_v, n = np.zeros(num_buckets), np.zeros(num_buckets, dtype=int)
    for b in range(num_buckets):
        m = (sofa_t >= edges[b]) & (sofa_t < edges[b + 1])
        n[b] = int(m.sum())
        mean_v[b] = float(Vt[m].mean()) if n[b] else np.nan
    return {
        "bucket_edges": edges.tolist(),
        "bucket_centers": centers.tolist(),
        "mean_vstar_per_bucket": mean_v.tolist(),
        "n_states_per_bucket": n.tolist(),
    }


def main():
    out_dir = ROOT / "results" / "deadend"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "deadend_structure.png"
    fig_path.parent.mkdir(exist_ok=True)

    env = make_env("mean")
    d = get_dynamics(env)
    t0 = time.time()
    optimal_pi, V_star = compute_Vstar(d["tx_mat"], d["r_mat"], gamma=1.0, tol=1e-9)
    admissible_mask = admissible_mask_table(d["admissible_actions"])
    sofa = np.asarray(d["sofa_scores"], dtype=np.float64)
    print(f"V* computed in {time.time()-t0:.2f}s; J* = {d['d_0'] @ V_star:.4f}")

    # --- Core structure ---
    summary = deadend_structure(
        d["tx_mat"], d["r_mat"], V_star, d["d_0"], admissible_mask
    )

    # --- Policy harm mass: expert / optimal / random ---
    rand_pi = np.full(V_star.shape[0], 0, dtype=np.int64)  # placeholder; use stochastic
    rand_stoch = np.full((V_star.shape[0], d["tx_mat"].shape[1]),
                         1.0 / d["tx_mat"].shape[1])
    expert = np.asarray(d["expert_policy"], dtype=np.float64)
    harm = {
        "optimal": policy_harm_mass(optimal_pi, d["tx_mat"], d["r_mat"], V_star, d["d_0"]),
        "expert": policy_harm_mass(expert, d["tx_mat"], d["r_mat"], V_star, d["d_0"]),
        "random": policy_harm_mass(rand_stoch, d["tx_mat"], d["r_mat"], V_star, d["d_0"]),
    }
    summary["policy_harm_mass"] = harm

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    sofa_stats = sofa_bucketed_vstar(V_star, sofa)
    with open(out_dir / "sofa_vs_vstar.json", "w") as f:
        json.dump(sofa_stats, f, indent=2)

    print("\n=== Dead-end summary ===")
    print(json.dumps(summary, indent=2))
    print("\n=== SOFA vs V* ===")
    print(json.dumps(sofa_stats, indent=2))

    # --- Figure (3 panels) ---
    T = non_terminal_states()
    Vt = V_star[T]
    Q_star = compute_Qstar(d["tx_mat"], d["r_mat"], V_star)
    gap = (V_star[:, None] - Q_star)[T]
    adm = admissible_mask[T]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))

    # Panel 1: V* histogram with dead-end region shaded
    axes[0].hist(Vt, bins=40, color="#4c72b0", alpha=0.85)
    axes[0].axvspan(0, 0.10, color="#c44e52", alpha=0.15)
    axes[0].set_xlabel("V*(s)  =  max achievable survival probability")
    axes[0].set_ylabel("# non-terminal states")
    axes[0].set_title(
        f"Exact survivability landscape\n"
        f"near-dead-ends (V*<0.1): {summary['state_census']['n_near_deadend']}"
        f" / {summary['n_non_terminal']}"
    )
    axes[0].grid(True, alpha=0.3)

    # Panel 2: mean V* by SOFA bucket
    centers = sofa_stats["bucket_centers"]
    meanv = sofa_stats["mean_vstar_per_bucket"]
    axes[1].plot(centers, meanv, "o-", color="#55a868", lw=2)
    axes[1].set_xlabel("SOFA score (bucket center)")
    axes[1].set_ylabel("Mean V*(s) in bucket")
    axes[1].set_title("Severity (SOFA) vs survivability")
    axes[1].grid(True, alpha=0.3)

    # Panel 3: admissible vs inadmissible mean Q*-gap + harmful mass per policy
    avh = summary["admissibility_vs_harm"]
    x = ["admissible", "inadmissible"]
    h = [avh["mean_gap_admissible"], avh["mean_gap_inadmissible"]]
    axes[2].bar(x, h, color=["#1f77b4", "#d62728"], alpha=0.85)
    axes[2].set_ylabel("Mean Q*-gap  (survival prob sacrificed)")
    axes[2].set_title(
        "Are inadmissible actions also more harmful?\n"
        f"harmful actions that are inadmissible: "
        f"{avh['frac_harmful_actions_that_are_inadmissible']:.2f}"
    )
    axes[2].grid(True, axis="y", alpha=0.3)
    for xi, hv in enumerate(h):
        axes[2].text(xi, hv, f"{hv:.3f}", ha="center", va="bottom", fontsize=10)

    fig.suptitle(
        "ICU-Sepsis (v2, mean): exact dead-end / harm structure from known dynamics",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print(f"\nFigure saved: {fig_path}")


if __name__ == "__main__":
    main()
