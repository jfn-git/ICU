"""Re-plot the mechanism (component-ablation) figure from saved results.

Paper-style Figure 1 (no retraining; reads results/component_ablation/*.json):
  Left  : exact value gap to V* (bar, mean +/- std) for each support-control
          location; numbers above bars = deployed unsupported-action rate u.
          CQL (kappa=1) shown last as a soft conservative reference.
  Right : Q-value leakage over training (mean +/- 95% CI) for the masking
          locations only (vanilla / target-only / policy-only / behavior-only /
          full mask), so the y-axis zooms onto the masking trajectories.

Writes: paper_final/figures/component_ablation.png  (+ figures/ copy)
Run:    python scripts/plot_component_ablation.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "results" / "component_ablation"
OUTS = [ROOT / "paper_final" / "figures" / "component_ablation.png",
        ROOT / "figures" / "component_ablation.png"]
SEEDS = [0, 1, 2, 3, 4]

PALETTE = {
    "vanilla": "#d62728", "target_only": "#9467bd", "policy_only": "#8c564b",
    "behavior_only": "#ff7f0e", "full_mask": "#1f77b4",
}
PAPER_LABEL = {
    "vanilla": "vanilla", "target_only": "target-only", "policy_only": "policy-only",
    "behavior_only": "behavior-only", "full_mask": "full mask",
}
# Left bar order: masking locations only (CQL is a soft remedy -> remedy spectrum).
LEFT = ["vanilla", "target_only", "policy_only", "behavior_only", "full_mask"]
# Right curves: masking locations only (no CQL -> y-axis zooms in).
RIGHT = ["vanilla", "target_only", "policy_only", "behavior_only", "full_mask"]
# full mask coincides with behavior-only, and policy-only with vanilla;
# dash the duplicate so both curves in each coinciding pair stay visible.
RIGHT_STYLE = {"full_mask": "--", "policy_only": "--"}


def main() -> None:
    summary = json.load(open(IN_DIR / "summary.json"))
    cells = summary["cells"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

    # ---- Left: exact value gap to V* (mean +/- std) + deployed-unsupp annotation ----
    ys = [cells[t]["final_policy_distance_to_Vstar_mean"] for t in LEFT]
    yerr = [cells[t]["final_policy_distance_to_Vstar_std"] for t in LEFT]
    us = [cells[t]["deployment_unsupported_state_frac_mean"] for t in LEFT]
    axes[0].bar(range(len(LEFT)), ys, yerr=yerr, capsize=4,
                color=[PALETTE[t] for t in LEFT], alpha=0.88)
    axes[0].set_xticks(range(len(LEFT)))
    axes[0].set_xticklabels([PAPER_LABEL[t] for t in LEFT], rotation=30, ha="right", fontsize=9)
    axes[0].set_ylabel(r"Exact value gap to $V^\star$ (lower is better)")
    axes[0].set_title("Component ablation")
    axes[0].grid(True, axis="y", alpha=0.3)
    for i, (yi, ei, ui) in enumerate(zip(ys, yerr, us)):
        axes[0].text(i, yi + ei, f"$u$={ui:.2f}", ha="center", va="bottom", fontsize=8)

    # ---- Right: Q-value leakage over training (mean +/- 95% CI), masking only ----
    for tag in RIGHT:
        curves, eps = [], None
        for s in SEEDS:
            d = json.load(open(IN_DIR / f"{tag}_seed{s}.json"))
            lc = d["leakage_curve"]
            eps = [p[0] for p in lc]
            curves.append([p[1] for p in lc])
        arr = np.asarray(curves)
        mean = arr.mean(axis=0)
        sem = arr.std(axis=0, ddof=1) / np.sqrt(arr.shape[0])
        ls = RIGHT_STYLE.get(tag, "-")
        axes[1].plot(eps, mean, color=PALETTE[tag], lw=2, ls=ls, label=PAPER_LABEL[tag])
        axes[1].fill_between(eps, mean - 1.96 * sem, mean + 1.96 * sem,
                             color=PALETTE[tag], alpha=0.15)
    axes[1].axhline(0, color="black", lw=0.8, ls="--", alpha=0.6)
    axes[1].set_xlabel("Training episodes")
    axes[1].set_ylabel(r"$Q$-value leakage (max inadmissible $Q$ $-$ max admissible $Q$)")
    axes[1].set_title("$Q$-value leakage from unsupported actions")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    for out in OUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=200, bbox_inches="tight")
        print("saved:", out)


if __name__ == "__main__":
    main()
