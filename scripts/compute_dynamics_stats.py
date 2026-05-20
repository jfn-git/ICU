"""Compute structural statistics of the ICU-Sepsis-v2 MDP.

Run from project root:
    python scripts/compute_dynamics_stats.py

Outputs a markdown-friendly numeric summary to stdout and writes a copy to
``core_docs/dynamics_stats_raw.txt`` for archival. The companion narrative
markdown lives at ``core_docs/dynamics_stats.md`` and is hand-edited.

All numbers come from the env's own ``dynamics`` dict + the ``sofa_scores``
and ``expert_policy`` properties, so the script is fully reproducible from
the pip-installed icu-sepsis package (v2.0.1) with no external data.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import gymnasium as gym
import icu_sepsis  # noqa: F401  -- registers the env

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = PROJECT_ROOT / "core_docs" / "dynamics_stats_raw.txt"


def shannon_entropy(p: np.ndarray, eps: float = 1e-12) -> float:
    p = np.asarray(p, dtype=np.float64)
    p = p[p > eps]
    if p.size == 0:
        return 0.0
    return float(-np.sum(p * np.log2(p)))


def main() -> None:
    env = gym.make("Sepsis/ICU-Sepsis-v2").unwrapped
    dyn = env.dynamics

    tx_mat: np.ndarray = dyn["tx_mat"]            # (S, A, S)
    r_mat: np.ndarray = dyn["r_mat"]              # (S, A, S)
    d_0: np.ndarray = dyn["d_0"]                  # (S,)
    admissible: list[list[int]] = dyn["admissible_actions"]
    sofa: np.ndarray = env.sofa_scores            # (S,)
    expert: np.ndarray = env.expert_policy        # (S, A)

    S, A, _ = tx_mat.shape
    out: dict = {}

    # ------------------------------------------------------------------ Core sizes
    out["num_states"] = int(S)
    out["num_actions"] = int(A)
    out["max_episode_steps"] = 500

    # ------------------------------------------------------------------ Terminals
    # Per the package constants: 713 = death, 714 = survival, 715 = s_inf.
    terminals = [713, 714, 715]
    out["terminal_states"] = terminals
    out["terminal_state_meanings"] = {
        "713": "death (absorbing, reward 0 on entry)",
        "714": "survival (absorbing, reward +1 on entry)",
        "715": "s_inf (absorbing)",
    }

    # ------------------------------------------------------------------ Admissibility
    adm_counts = np.array([len(a) for a in admissible], dtype=np.int64)
    # Distinguish non-terminal states (where admissibility is the interesting story)
    non_terminal_mask = np.ones(S, dtype=bool)
    non_terminal_mask[terminals] = False
    nt_counts = adm_counts[non_terminal_mask]

    out["admissible_per_state_all"] = {
        "min": int(adm_counts.min()),
        "median": float(np.median(adm_counts)),
        "max": int(adm_counts.max()),
        "mean": float(adm_counts.mean()),
    }
    out["admissible_per_state_nonterminal"] = {
        "min": int(nt_counts.min()),
        "median": float(np.median(nt_counts)),
        "max": int(nt_counts.max()),
        "mean": float(nt_counts.mean()),
    }
    out["frac_admissible_cells_all"] = float(adm_counts.sum() / (S * A))
    out["frac_admissible_cells_nonterminal"] = float(
        nt_counts.sum() / (non_terminal_mask.sum() * A)
    )

    # Histogram of admissible-action counts across non-terminal states
    hist_edges = [0, 1, 5, 10, 15, 20, 25, 26]
    hist, _ = np.histogram(nt_counts, bins=hist_edges)
    out["admissible_count_histogram_nonterminal"] = {
        f"[{hist_edges[i]},{hist_edges[i+1]})": int(hist[i])
        for i in range(len(hist))
    }

    # ------------------------------------------------------------------ tx_mat sparsity
    # Consider only admissible (s,a) cells. For each, count fraction of zero entries
    # across the S successor dimension.
    zero_frac_list: list[float] = []
    for s in range(S):
        for a in admissible[s]:
            row = tx_mat[s, a]
            zero_frac_list.append(float((row == 0).sum() / S))
    if zero_frac_list:
        zf = np.array(zero_frac_list)
        out["tx_mat_admissible_zero_frac"] = {
            "mean": float(zf.mean()),
            "median": float(np.median(zf)),
            "min": float(zf.min()),
            "max": float(zf.max()),
            "num_admissible_cells": len(zero_frac_list),
        }

    # Quick row-sum check (each (s,a) row should sum to ~1 if admissible)
    sum_check = np.array([tx_mat[s, a].sum()
                          for s in range(S) for a in admissible[s]])
    out["tx_mat_row_sum_admissible"] = {
        "min": float(sum_check.min()),
        "max": float(sum_check.max()),
        "mean": float(sum_check.mean()),
    }

    # ------------------------------------------------------------------ d_0 support
    d0_supp = int((d_0 > 0).sum())
    out["d0_support_size"] = d0_supp
    out["d0_total_mass"] = float(d_0.sum())
    out["d0_max_prob"] = float(d_0.max())
    out["d0_min_positive_prob"] = float(d_0[d_0 > 0].min()) if d0_supp > 0 else 0.0

    # ------------------------------------------------------------------ Reward structure
    # Confirm: reward is non-zero only on transition into state 714 (survival).
    # We scan r_mat for any non-zero entries and report which successor states they target.
    nz = np.argwhere(r_mat != 0)
    nz_targets, counts = np.unique(nz[:, 2], return_counts=True)
    nz_values = {}
    for t in nz_targets:
        v = np.unique(r_mat[..., t][r_mat[..., t] != 0])
        nz_values[int(t)] = [float(x) for x in v]
    out["reward_nonzero_target_states"] = {int(k): int(v)
                                            for k, v in zip(nz_targets, counts)}
    out["reward_nonzero_values_per_target"] = nz_values

    # ------------------------------------------------------------------ SOFA distribution
    out["sofa_stats"] = {
        "min": float(sofa.min()),
        "median": float(np.median(sofa)),
        "max": float(sofa.max()),
        "mean": float(sofa.mean()),
    }
    # 5-quantile (quintile) bucket counts
    qs = np.quantile(sofa, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    buckets, _ = np.histogram(sofa, bins=qs)
    out["sofa_quintile_edges"] = [float(x) for x in qs]
    out["sofa_quintile_bucket_counts"] = [int(x) for x in buckets]

    # Also a fixed-width histogram for readability
    fw_edges = [0, 3, 6, 9, 12, 15, 18, 24]
    fw_hist, _ = np.histogram(sofa, bins=fw_edges)
    out["sofa_fixedwidth_histogram"] = {
        f"[{fw_edges[i]},{fw_edges[i+1]})": int(fw_hist[i])
        for i in range(len(fw_hist))
    }

    # ------------------------------------------------------------------ Expert-policy entropy
    # For each non-terminal state, compute Shannon entropy of expert_policy[s, :].
    ents = np.array([shannon_entropy(expert[s]) for s in range(S)
                     if s not in terminals])
    out["expert_entropy_nonterminal"] = {
        "min_bits": float(ents.min()),
        "median_bits": float(np.median(ents)),
        "max_bits": float(ents.max()),
        "mean_bits": float(ents.mean()),
        "max_possible_bits": float(np.log2(A)),
    }
    ent_edges = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
    ent_hist, _ = np.histogram(ents, bins=ent_edges)
    out["expert_entropy_histogram_nonterminal"] = {
        f"[{ent_edges[i]:.1f},{ent_edges[i+1]:.1f})": int(ent_hist[i])
        for i in range(len(ent_hist))
    }
    # How many states have a near-deterministic expert (entropy < 0.5 bits)?
    out["expert_deterministic_threshold"] = {
        "threshold_bits": 0.5,
        "n_states_below": int((ents < 0.5).sum()),
    }
    # How many states have a near-uniform expert? Compare entropy to log2(|admissible|).
    near_uniform = 0
    for s in range(S):
        if s in terminals:
            continue
        k = len(admissible[s])
        if k <= 1:
            continue
        max_ent_s = np.log2(k)
        if shannon_entropy(expert[s]) >= 0.95 * max_ent_s:
            near_uniform += 1
    out["expert_near_uniform_count"] = int(near_uniform)
    out["expert_near_uniform_def"] = "entropy >= 0.95 * log2(|admissible(s)|)"

    # ------------------------------------------------------------------ Sanity: where does the expert place mass relative to admissible?
    # For each non-terminal state, sum expert prob over admissible actions.
    exp_adm_mass = []
    for s in range(S):
        if s in terminals:
            continue
        exp_adm_mass.append(float(expert[s, admissible[s]].sum()))
    exp_adm_mass = np.array(exp_adm_mass)
    out["expert_mass_on_admissible_nonterminal"] = {
        "min": float(exp_adm_mass.min()),
        "median": float(np.median(exp_adm_mass)),
        "max": float(exp_adm_mass.max()),
        "mean": float(exp_adm_mass.mean()),
        "n_states_with_full_admissible_mass": int((exp_adm_mass > 0.9999).sum()),
    }

    # ------------------------------------------------------------------ Emit
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=False)
        f.write("\n")

    print(json.dumps(out, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
