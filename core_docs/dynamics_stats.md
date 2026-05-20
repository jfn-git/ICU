# Dynamics statistics of the ICU-Sepsis-v2 MDP

> **Source.** All numbers below come from the env's own `dynamics` dict, plus the
> `sofa_scores` and `expert_policy` properties, on the pip-installed `icu-sepsis`
> package (v2.0.1). They are reproduced by `scripts/compute_dynamics_stats.py`,
> whose raw JSON output is archived at `core_docs/dynamics_stats_raw.txt`.
> Date of run: 2026-05-20.

## 1. State / action sizes

| Quantity | Value |
|---|---|
| Number of states (`S`) | 716 |
| Number of actions (`A`) | 25 (5 fluid levels × 5 vasopressor levels) |
| Maximum episode steps | 500 |
| Terminal states | `{713, 714, 715}` = {death, survival, s_inf} |
| Non-terminal states | 713 |
| Initial-state support (`d_0 > 0`) | 712 of 716 states |
| Max initial-state probability | 0.0185 |
| Smallest positive `d_0` entry | 4.80e-5 |

The initial distribution touches almost every non-terminal state (712 out of 713)
and is highly diffuse — no single starting state dominates.

## 2. Admissible-action structure (the heart of the project)

The admissible action set per state is defined by the original ICU-Sepsis paper
as "actions seen ≥ τ = 20 times in that state in the source cohort."
Over ALL states (including terminals, whose admissible sets are `[0, …, 24]`):

| Statistic | Value |
|---|---|
| min `|admissible(s)|` | 1 |
| median `|admissible(s)|` | 4 |
| max `|admissible(s)|` | 25 (only for terminal states) |
| mean `|admissible(s)|` | 3.23 |
| fraction of `(s, a)` cells admissible | 12.92 % |

Restricting to **non-terminal states only**:

| Statistic | Value |
|---|---|
| min `|admissible(s)|` | 1 |
| median `|admissible(s)|` | 4 |
| max `|admissible(s)|` | **13** |
| mean `|admissible(s)|` | 3.14 |
| fraction of `(s, a)` cells admissible | 12.56 % |

Distribution of admissible-action counts across the 713 non-terminal states:

| Bucket | # states |
|---|---|
| `|adm|` ∈ [1, 5) | **626** |
| `|adm|` ∈ [5, 10) | 80 |
| `|adm|` ∈ [10, 15) | 7 |
| `|adm|` ∈ [15, 25] | 0 |

**Surprising:** the max admissible count for a *non-terminal* state is only 13, not 25.
The vast majority of patient states have between 1 and 4 "clinically supported"
actions out of 25 — so action masking has the potential to remove ~87 % of
the action space from exploration, which is a large effect size and one of
the main reasons we expect the masking ablation to matter.

## 3. Transition matrix sparsity

Computed over the 2 313 admissible `(s, a)` cells:

| Statistic | Value |
|---|---|
| mean fraction of zero entries in `tx_mat[s, a, :]` | 94.26 % |
| median | 94.83 % |
| min (densest row) | 73.60 % |
| max (sparsest row) | 99.86 % |
| row-sum sanity (should be 1.0) | min 1 − 6e-16, max 1 + 4e-16 |

So an admissible action typically transitions to ~41 of 716 successor states
(`(1 − 0.9426) × 716 ≈ 41`). Combined with `S = 716`, the joint admissible
transition tensor has effective support of order `2,313 × 41 ≈ 95k` non-zero
entries — small enough to be computed exactly, which justifies the project's
choice to use the **ground-truth V\*** as a reference rather than OPE.

## 4. Reward structure

We scanned `r_mat` for non-zero entries:

| Target state of transition | # non-zero entries in `r_mat` | distinct reward values |
|---|---|---|
| 714 (survival) | 17 875 | `{+1.0}` |
| All other targets | 0 | — |

**Confirmed:** the per-step reward is 0 everywhere *except* on transitions
into state 714 (survival), where it is +1. Transitions into state 713 (death)
yield reward 0. Episodic return is therefore a binary indicator of survival.
(Combined with `γ = 1` this means `V*(s)` equals the expert/optimal survival
probability from `s`.)

## 5. SOFA-score distribution across the 716 states

| Statistic | Value |
|---|---|
| min | 0.00 |
| median | 6.46 |
| max | **18.02** (NOT 24 — SOFA's nominal upper bound) |
| mean | 6.83 |

Quintile bucket edges (cuts at the 0/20/40/60/80/100 % quantiles):

| Quintile | Range | # states |
|---|---|---|
| Q1 | 0.00 – 4.21 | 143 |
| Q2 | 4.21 – 5.79 | 143 |
| Q3 | 5.79 – 7.19 | 143 |
| Q4 | 7.19 – 9.08 | 143 |
| Q5 | 9.08 – 18.02 | 144 |

Fixed-width histogram (more visually informative):

| SOFA bucket | # states |
|---|---|
| [0, 3) | 45 |
| [3, 6) | 262 |
| [6, 9) | 262 |
| [9, 12) | 103 |
| [12, 15) | 34 |
| [15, 18) | 9 |
| [18, 24) | 1 |

**Mildly surprising:** SOFA tops out at ~18 even though the official SOFA
scale goes to 24. This reflects the cohort: extremely sick patients (SOFA ≥
18) are rare in the source MIMIC-III pipeline after cluster averaging.
For SOFA-based reward shaping, this matters because the shaping potential
range is effectively `[0, 18]`, not `[0, 24]`.

## 6. Expert-policy entropy

For each non-terminal state we compute Shannon entropy (base 2)
of `expert_policy[s, :]`:

| Statistic | Value |
|---|---|
| min | 0.029 bits |
| median | 2.325 bits |
| max | 4.172 bits |
| mean | 2.035 bits |
| Maximum possible (uniform over 25 actions) | `log2(25)` = 4.644 bits |

Histogram across the 713 non-terminal states:

| Entropy bucket (bits) | # states |
|---|---|
| [0.0, 0.5) | **164** |
| [0.5, 1.0) | 50 |
| [1.0, 1.5) | 11 |
| [1.5, 2.0) | 21 |
| [2.0, 2.5) | 162 |
| [2.5, 3.0) | 140 |
| [3.0, 3.5) | 91 |
| [3.5, 4.0) | 67 |
| [4.0, 5.0) | 7 |

Two further summaries:

- **Near-deterministic expert states** (entropy < 0.5 bits): **164** of 713.
  Roughly 23 % of non-terminal states have an essentially unique
  "clinically dominant" action.
- **Near-uniform-over-admissible expert states** (entropy ≥ 0.95 ⋅ log₂|admissible(s)|):
  **463** of 713 — about 65 %. In two-thirds of states, the expert spreads its
  probability roughly uniformly across the admissible actions, providing very
  little policy signal beyond admissibility itself.

The distribution is therefore **bimodal**: a sizeable peaked tail
(≈23 % deterministic) and a much larger near-uniform mass (≈65 %).

## 7. Expert mass on the admissible set

For each non-terminal state, we sum `expert_policy[s, admissible(s)]`:

| Statistic | Value |
|---|---|
| min | 0.123 |
| median | 0.902 |
| max | 0.997 |
| mean | 0.844 |
| # states with full admissible mass (`> 0.9999`) | **0** |

**This is the single most reviewer-relevant finding from the dynamics analysis.**
The published "expert policy" assigns, on average, **~16 % of its probability
to *inadmissible* actions**, and in zero states is the expert fully concentrated
on the admissible set. That is, the env's own notion of "expert" and its own
notion of "admissible" are not perfectly consistent. This is important because:

1. It justifies including the `mean` strategy in the ablation — clinicians
   themselves sometimes select actions with insufficient cohort support.
2. It means *policy-agreement-with-expert* and *unsafe-action-rate* will not
   be mathematically redundant metrics; an agent could match the expert
   distribution-wise and still incur inadmissible actions, or vice versa.
3. Action masking will deliberately *deviate* from the expert in a measurable
   way — which is itself a finding worth reporting.

---

## Implications for the ablation design

- Because median `|admissible(s)|` is 4 out of 25, action masking removes
  ~84 % of the nominal action space; we should expect the masked variants to
  show large sample-efficiency gains over the unmasked variants, and that
  large effect size makes the ablation hard for a reviewer to dismiss as
  noise even with only 5 seeds.
- Because the expert places ~16 % of its mass on inadmissible actions, the
  per-state "unsafe-action-rate" metric is genuinely informative and is
  **not** simply driven to 0 by the masked variants — the unmasked + `mean`
  strategy can still pick inadmissible actions, and this is the baseline
  we contrast against.
- Because rewards are 0 everywhere except into state 714, the value function
  is a survival probability and `γ = 1` is *the* mathematically natural choice;
  this also means there is no "discounting-vs-survival" confound to worry
  about in defending the choice of γ.
- Because SOFA tops at 18, any SOFA-based potential `Φ(s) = -SOFA(s)`
  has range `[-18, 0]`, not `[-24, 0]`; this matters for tuning the
  shaping magnitude if Direction 3 is pursued.

---

*Script:* `scripts/compute_dynamics_stats.py`
*Raw JSON:* `core_docs/dynamics_stats_raw.txt`
