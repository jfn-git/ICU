# Admissibility-Aware Q-Learning on ICU-Sepsis — Code & Data

Reproducible code and data for our study of out-of-distribution (OOD) /
inadmissible-action handling on the ICU-Sepsis benchmark. ICU-Sepsis is a
tabular MDP (716 states, 25 actions) with **fully known dynamics**, so we
evaluate every policy **exactly** (value iteration gives the ground-truth
optimal value V*); no off-policy estimation noise is involved.

> All results are **benchmark-internal** (data-support based). "Inadmissible /
> unsupported" means insufficient data support under the benchmark's threshold,
> **not** medically incorrect. This is an algorithmic study, not a clinical
> recommendation.

---

## 1. What is here

```
submission/
├── README.md
├── requirements.txt
├── src/                      # core library (only modules used by the scripts)
│   ├── env_utils.py          # env, known dynamics, exact V*/V^pi, distance-to-V*
│   ├── tabular_rl.py         # Q-learning: behavior/target mask, penalty, CQL-style conservatism
│   └── deadend.py            # exact dead-end / harm structure from dynamics
├── scripts/                  # one script per result; each writes results/ + figures/
│   ├── run_baselines.py            # Table 1
│   ├── run_penalty_sweep.py        # main result  (Fig: OOD-remedy spectrum)
│   ├── run_component_ablation.py   # main result  (Fig: component ablation + value-leakage)
│   ├── run_offline_datasize.py     # main result  (Fig: offline empirical-MDP, dataset-size sweep)
│   ├── run_expert_prior.py         # supplement   (Fig: expert-guided sample efficiency)
│   ├── run_deadend_analysis.py     # supplement   (Fig: harm structure)
│   └── run_robustness.py           # supplement   (Fig: algorithm × strategy robustness)
├── configs/default.yaml      # default hyper-parameters
├── results/                  # JSON outputs (per-seed + aggregated summary)
│   ├── baselines/  penalty_sweep/  component_ablation/  offline_datasize/
│   └── expert_prior/  deadend/  robustness/
└── figures/                  # the figures used in the paper
    ├── penalty_tradeoff.png      component_ablation.png   offline_datasize.png
    ├── expert_prior_curve.png    deadend_structure.png    robustness.png
```

---

## 2. Install

```bash
pip install -r requirements.txt
# requires the ICU-Sepsis benchmark package (icu_sepsis), gymnasium, numpy, matplotlib
```

Tested with Python 3.13, NumPy. Each script registers `Sepsis/ICU-Sepsis-v2`
via `import icu_sepsis`.

---

## 3. Reproduce (each script is self-contained, CPU-only, minutes)

```bash
python scripts/run_baselines.py          # ~10 s   -> results/baselines/summary.json
python scripts/run_deadend_analysis.py   # ~10 s   -> results/deadend/, figures/deadend_structure.png
python scripts/run_penalty_sweep.py      # ~6 min  -> results/penalty_sweep/, figures/penalty_tradeoff.png
python scripts/run_component_ablation.py # ~7 min  -> results/component_ablation/, figures/component_ablation.png
python scripts/run_expert_prior.py       # ~4 min  -> results/expert_prior/, figures/expert_prior_curve.png
python scripts/run_robustness.py         # ~12 min -> results/robustness/, figures/robustness.png
python scripts/run_offline_datasize.py   # ~12 min -> results/offline_datasize/, figures/offline_datasize.png
```

All runs use 5 seeds (0–4), 50k episodes, alpha=0.1, gamma=1.0,
epsilon 1.0→0.05 decayed over 10k episodes (see `configs/default.yaml`).

---

## 4. Script → paper artifact mapping

| Script | Paper artifact | One-line finding |
|---|---|---|
| `run_baselines.py` | Table 1 | Exact J: Random 0.780 / Expert 0.782 / Optimal 0.875 (matches benchmark). |
| `run_penalty_sweep.py` | Main figure + table | The OOD-action remedy spectrum (vanilla → support penalty λ → hard mask): a reward penalty traces a support–value trade-off and can drive deployed unsupported actions to 0, but its distance-to-V* plateaus and is **Pareto-dominated** by hard admissibility masking. |
| `run_component_ablation.py` | Main figure + table | **Locates the failure.** Masking *behavior* alone is necessary **and sufficient** (== full mask exactly); masking only the Bellman *target* barely helps; masking only the deployed *policy* is a partial band-aid that leaves the Q-table corrupted (high value-leakage); a CQL-style value-conservatism cell is the best *soft* remedy but still trails the hard constraint and has a κ sweet spot. The Q-value-leakage curve gives the mechanism. |
| `run_expert_prior.py` | Supplement figure | Expert-guided exploration learns much faster than uniform; **projecting** the expert prior onto the admissible set drives deployed unsupported-action rate to ~0 while preserving value and raising expert agreement. |
| `run_deadend_analysis.py` | Supplement figure | ICU-Sepsis has **no dead-ends** (min V* = 0.198); severity (SOFA) correlates with lower survivability; under mean imputation, inadmissible actions carry higher one-step death risk but a *smaller* long-run Q*-gap (the imputation hides their risk). |
| `run_robustness.py` | Supplement figure | The hidden failure + masking fix hold across **Q-learning / SARSA / Dyna-Q** (not an algorithm artifact); under the `terminate` strategy vanilla naturally avoids unsupported actions (deploy rate 85% → ~3-4%), confirming the failure is **specific to `mean`**. |
| `run_offline_datasize.py` | Main/supplement figure | Offline empirical-MDP, dataset-size N sweep (expert behavior): **naive (mean-impute) overestimates its own value (+0.21) and its realized policy stagnates (~0.093) with more data; pessimistic VI-LCB is calibrated (~0) and improves to 0.069; admissibility-masking removes unsupported actions (0) and reaches 0.065.** Exact V* makes this measurable. |

---

## 5. Key numbers (mean over 5 seeds)

OOD-action remedy spectrum (`run_penalty_sweep.py`), J* = 0.8751:

| remedy | distance-to-V* | deployed unsupported-action rate | expert agreement |
|---|---:|---:|---:|
| vanilla Q-learning | 0.0896 | 0.85 | 0.04 |
| support penalty λ=0.1 | 0.0831 | 0.35 | 0.23 |
| support penalty λ=1.0 | 0.0865 | 0.00 | 0.52 |
| hard admissibility mask | **0.0693** | 0.00 | 0.53 |

Component ablation (`run_component_ablation.py`) — distance-to-V*, deployed unsupported rate, Q-value leakage:

| variant | distance-to-V* | deployed unsupp. | Q-leakage | reading |
|---|---:|---:|---:|---|
| vanilla | 0.0896 | 0.87 | +0.46 | failure: OOD actions over-valued |
| target-mask only | 0.0850 | 0.77 | +0.07 | cleans backup, but barely helps |
| policy-mask only (deploy) | 0.0834 | 0.00 | +0.46 | band-aid; Q still corrupted |
| CQL-style conservatism (κ=1) | 0.0801 | 0.00 | −2.95 | best *soft* remedy, still trails |
| **behavior-mask only** | **0.0693** | 0.00 | −0.80 | necessary **and** sufficient |
| full mask | 0.0693 | 0.00 | −0.80 | identical to behavior-only |

Mechanism: inadmissible actions only become competitive because they are *taken and
updated* under mean imputation; preventing that (behavior masking) is the decisive fix,
while target/policy masking and value penalties only partially help.

Expert-guided exploration (`run_expert_prior.py`):

| variant | distance-to-V* | deployed unsupported | expert agreement |
|---|---:|---:|---:|
| vanilla | 0.0896 | 0.87 | 0.04 |
| expert prior (raw) | 0.0736 | 0.08 | 0.60 |
| expert prior (projected to admissible) | 0.0731 | **0.005** | 0.65 |

---

## 6. Notes

- Exact evaluation: `compute_Vstar` / `compute_Vpi` in `src/env_utils.py` solve
  the known-dynamics MDP to tolerance 1e-8/1e-9; reported metrics are exact, not
  rollout estimates.
- `distance-to-V*` = E_{s~d0}[V*(s) − V^π(s)]; with γ=1 and a survival-indicator
  reward, J(π) = E_{s~d0}[V^π(s)] equals the benchmark survival rate.
- "Deployed unsupported-action rate" is the (visitation-weighted) fraction of
  steps where the final greedy policy selects an inadmissible action.
