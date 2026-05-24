"""Exact dist-V* learning curves from the component-ablation snapshots.

Unlike the benchmark's rollout-return learning curves (a noisy, narrow-band metric),
this plots the EXACT distance-to-V* of each policy snapshot over training, on the
same exact axis as the rest of the paper. It visualizes the mechanism story: vanilla
plateaus far from optimal, deployment-only masking barely helps dist-V*, CQL-style
conservatism helps, and full (behavior) masking reaches the best plateau.

Reads:  results/component_ablation/<cell>_seed<0-4>.json  (each has distance_curve)
Writes: submission/figures/exact_dist_curve.png

Run: python scripts/plot_exact_learning_curve.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "results" / "component_ablation"
OUT = ROOT / "submission" / "figures" / "exact_dist_curve.png"
SEEDS = [0, 1, 2, 3, 4]

# cell tag -> (label, color)
CELLS = {
    "vanilla":         ("vanilla", "#d62728"),
    "policy_only":     ("deployment-mask only", "#8c564b"),
    "conservative_k1": (r"CQL-style ($\kappa{=}1$)", "#2ca02c"),
    "full_mask":       ("full / behavior mask", "#1f77b4"),
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    for tag, (label, color) in CELLS.items():
        curves = []
        eps = None
        for s in SEEDS:
            d = json.load(open(IN_DIR / f"{tag}_seed{s}.json"))
            dc = d["distance_curve"]
            eps = [p[0] for p in dc]
            curves.append([p[1] for p in dc])
        arr = np.asarray(curves)                      # (5, T)
        mean = arr.mean(axis=0)
        sem = arr.std(axis=0, ddof=1) / np.sqrt(arr.shape[0])
        ax.plot(eps, mean, color=color, lw=2, label=label)
        ax.fill_between(eps, mean - 1.96 * sem, mean + 1.96 * sem,
                        color=color, alpha=0.15)
    ax.set_xlabel("Training episodes")
    ax.set_ylabel(r"Exact distance-to-$V^\star$  (lower = better)")
    ax.set_title("Exact learning curves (ICU-Sepsis mean, Q-learning, 5 seeds, 95% CI)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print("saved:", OUT)


if __name__ == "__main__":
    main()
