"""T2: offline RL on an empirical MDP -- dataset-size sweep with exact evaluation.

Makes the offline-RL framing literal. We collect N transitions by the estimated
clinician (expert) behavior policy in the TRUE MDP, build the certainty-equivalent
empirical model, and compare three offline value methods that mirror our online
remedy spectrum:

  naive        : unseen (s,a) imputed by the per-state MEAN of observed actions,
                 plain value iteration            (the ICU-Sepsis `mean` analogue)
  pessimistic  : VI with a count-based lower-confidence bonus b = c/sqrt(n(s,a)),
                 unseen actions excluded          (VI-LCB / CQL-style pessimism)
  masked       : VI restricted to the benchmark admissible set
                 (admissibility masking, oracle support)

Because the true model is known we evaluate three things exactly vs dataset size:
  (A) value OVERESTIMATION = model's self-estimate (d0.V_model) - true value
      -- the canonical offline-RL pathology; naive overestimates, pessimism does not;
  (B) realized distance-to-V* of the learned policy (true dynamics);
  (C) deployed unsupported (inadmissible) action rate of the learned policy.

Key point: ICU-Sepsis compresses every policy's value into a narrow band, so (B)
barely separates -- but (A) and (C) expose the offline-RL failure clearly. This
is exactly the benchmark's "hidden failure" theme in the offline setting.

Outputs: results/offline_datasize/summary.json, figures/offline_datasize.png
Run: python scripts/run_offline_datasize.py
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
    TERMINAL_STATES,
    N_STATES,
    N_ACTIONS,
)

SEEDS = [0, 1, 2, 3, 4]
N_LIST = [1_000, 2_500, 5_000, 10_000, 25_000, 50_000, 100_000]
NMAX = max(N_LIST)
LCB_C = 0.1
NON_TERMINAL = np.array(
    [s for s in range(N_STATES) if s not in TERMINAL_STATES], dtype=np.int64
)


def collect(tx, d0, behavior, n_steps, rng):
    S_arr = np.empty(n_steps, dtype=np.int32)
    A_arr = np.empty(n_steps, dtype=np.int32)
    Sn_arr = np.empty(n_steps, dtype=np.int32)
    s = int(rng.choice(N_STATES, p=d0))
    for t in range(n_steps):
        a = int(rng.choice(N_ACTIONS, p=behavior[s]))
        sn = int(rng.choice(N_STATES, p=tx[s, a]))
        S_arr[t], A_arr[t], Sn_arr[t] = s, a, sn
        s = int(rng.choice(N_STATES, p=d0)) if sn in TERMINAL_STATES else sn
    return S_arr, A_arr, Sn_arr


def build_model(S_arr, A_arr, Sn_arr, N):
    counts = np.zeros((N_STATES, N_ACTIONS, N_STATES))
    np.add.at(counts, (S_arr[:N], A_arr[:N], Sn_arr[:N]), 1.0)
    n = counts.sum(axis=2)
    with np.errstate(invalid="ignore", divide="ignore"):
        P_hat = counts / n[:, :, None]
    return n, np.nan_to_num(P_hat)


def naive_impute(P_hat, n):
    P = P_hat.copy()
    seen = n > 0
    for s in NON_TERMINAL:
        sa = np.flatnonzero(seen[s])
        if len(sa) == 0:
            continue
        mean_row = P_hat[s, sa].mean(axis=0)
        for a in range(N_ACTIONS):
            if not seen[s, a]:
                P[s, a] = mean_row
    return P


def vi(P_hat, r, valid, bonus, gamma=1.0, iters=5000, tol=1e-8):
    """Returns (pi, V). V is the model's (possibly pessimistic) value estimate."""
    V = np.zeros(N_STATES)
    all_invalid = ~valid.any(axis=1)
    for _ in range(iters):
        Q = np.sum(P_hat * (r + gamma * V[None, None, :]), axis=2) - bonus
        Qm = np.where(valid, Q, -np.inf)
        Vn = Qm.max(axis=1)
        Vn[all_invalid] = 0.0
        if np.max(np.abs(Vn - V)) < tol:
            V = Vn
            break
        V = Vn
    Q = np.sum(P_hat * (r + gamma * V[None, None, :]), axis=2) - bonus
    Qm = np.where(valid, Q, -np.inf)
    pi = Qm.argmax(axis=1).astype(np.int64)
    pi[all_invalid] = 0
    return pi, V


def metrics(pi, V_model, tx, r, V_star, d0, admissible_mask):
    V_true = compute_Vpi(pi, tx, r, gamma=1.0, tol=1e-8)
    a = pi[NON_TERMINAL]
    return {
        "overestimation": float(d0 @ V_model - d0 @ V_true),
        "distance_to_Vstar": float(distance_to_optimal(V_true, V_star, d0)),
        "deployed_unsupported": float((~admissible_mask[NON_TERMINAL, a]).mean()),
    }


def main():
    out_dir = ROOT / "results" / "offline_datasize"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = ROOT / "figures" / "offline_datasize.png"

    d = get_dynamics(make_env("mean"))
    tx, r, d0 = d["tx_mat"], d["r_mat"], d["d_0"]
    admissible_mask = admissible_mask_table(d["admissible_actions"])
    _, V_star = compute_Vstar(tx, r, gamma=1.0, tol=1e-9)
    j_star = float(d0 @ V_star)
    # Realistic offline data: the estimated clinician (expert) behavior policy,
    # under which inadmissible (low-support) actions are sampled only rarely --
    # so count-based pessimism naturally aligns with admissibility.
    behavior = np.asarray(d["expert_policy"], dtype=np.float64)
    print(f"J* = {j_star:.4f}")

    METHODS = ["naive", "pessimistic", "masked"]
    MET = ["overestimation", "distance_to_Vstar", "deployed_unsupported"]
    res = {m: {k: {N: [] for N in N_LIST} for k in MET} for m in METHODS}

    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        t0 = time.time()
        S_arr, A_arr, Sn_arr = collect(tx, d0, behavior, NMAX, rng)
        for N in N_LIST:
            n, P_hat = build_model(S_arr, A_arr, Sn_arr, N)
            P_imp = naive_impute(P_hat, n)
            seen = n > 0
            runs = {
                "naive": vi(P_imp, r, np.ones_like(n, bool), np.zeros_like(n)),
                "pessimistic": vi(P_hat, r, seen, np.where(seen, LCB_C / np.sqrt(np.maximum(n, 1)), 0.0)),
                "masked": vi(P_imp, r, admissible_mask, np.zeros_like(n)),
            }
            for m, (pi, Vm) in runs.items():
                mt = metrics(pi, Vm, tx, r, V_star, d0, admissible_mask)
                for k in MET:
                    res[m][k][N].append(mt[k])
        print(f"  seed {seed} done in {time.time()-t0:.0f}s")

    summary = {"j_star": j_star, "lcb_c": LCB_C, "behavior": "expert",
               "N_list": N_LIST, "methods": {}}
    for m in METHODS:
        summary["methods"][m] = {
            k + "_mean": [float(np.mean(res[m][k][N])) for N in N_LIST] for k in MET
        } | {k + "_std": [float(np.std(res[m][k][N], ddof=1)) for N in N_LIST] for k in MET}
    json.dump(summary, open(out_dir / "summary.json", "w"), indent=2)
    print(json.dumps(summary["methods"], indent=2))

    # --- Figure: 3 panels ---
    colors = {"naive": "#d62728", "pessimistic": "#2ca02c", "masked": "#1f77b4"}
    labels = {"naive": "naive (mean-impute) = vanilla",
              "pessimistic": "pessimistic VI-LCB = conservative",
              "masked": "admissibility-masked = masking"}
    titles = {"overestimation": "(A) Value OVERESTIMATION (self-estimate − true)",
              "distance_to_Vstar": "(B) Realized distance-to-V*",
              "deployed_unsupported": "(C) Deployed unsupported-action rate"}
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    for ax, k in zip(axes, MET):
        for m in METHODS:
            mean = np.array(summary["methods"][m][k + "_mean"])
            sem = np.array(summary["methods"][m][k + "_std"]) / np.sqrt(len(SEEDS))
            ax.plot(N_LIST, mean, "o-", color=colors[m], label=labels[m], lw=2)
            ax.fill_between(N_LIST, mean - 1.96 * sem, mean + 1.96 * sem,
                            color=colors[m], alpha=0.16)
        ax.set_xscale("log")
        ax.set_xlabel("Offline dataset size N")
        ax.set_title(titles[k])
        ax.grid(True, alpha=0.3, which="both")
        if k == "overestimation":
            ax.axhline(0, color="black", lw=0.8, ls="--", alpha=0.6)
            ax.legend(fontsize=8)
    axes[0].set_ylabel("value")
    fig.suptitle("ICU-Sepsis offline empirical-MDP sweep (expert behavior, 5 dataset seeds, 95% CI): "
                 "naive overestimates & stagnates; pessimism is calibrated and improves with data; "
                 "masking removes unsupported actions", fontsize=10)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    print("Figure saved:", fig_path)


if __name__ == "__main__":
    main()
