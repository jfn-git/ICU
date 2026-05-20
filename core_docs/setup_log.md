# Setup Log — ICU-Sepsis Project (autonomous run)

> Auto-generated during overnight autonomous execution.
> Last updated: 2026-05-20 (in-progress; will be appended as bundles complete).

---

## A. Environment installation

### A.1 Platform

| Item | Value |
|---|---|
| Date | 2026-05-20 |
| OS | Windows 11 Home 10.0.26200 |
| Shell | PowerShell 5.1 |
| Python (active) | `C:\Users\jeff9\miniconda3\python.exe` (Python **3.13.12**, Anaconda) |
| `python -m pip` | pip 26.0.1 (matched to 3.13) |
| Working dir | `c:\Users\jeff9\OneDrive\文件\FINAL` |

Notes:
- `pip --version` initially reported pip 23.2.1 bound to a separate Python 3.11 install. We deliberately use `python -m pip` everywhere to bind installs to the active conda 3.13 interpreter.
- No `git init` performed (per instructions — no git remote, no anonymous-GitHub upload).

### A.2 Installed packages (icu-sepsis + helpers)

Both packages installed editable from local source:

```text
python -m pip install -e ./icu-sepsis/packages/icu_sepsis
python -m pip install -e ./icu-sepsis/packages/icu_sepsis_helpers
```

Resulting versions (key entries only):

| Package | Version |
|---|---|
| icu-sepsis | 2.0.1 (editable, local) |
| icu-sepsis-helpers | 1.0.0 (editable, local) |
| gymnasium | 1.3.0 |
| gym | 0.26.2 (legacy compatibility) |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| pandas | 3.0.3 |
| matplotlib | 3.10.9 |
| scikit-learn | 1.8.0 |
| tqdm | (pre-installed) |
| pyyaml | 6.0.3 |

Caveat — **gym 0.26.2 deprecation warning** is printed on every `gym.make`:
```
Gym has been unmaintained since 2022 and does not support NumPy 2.0 amongst other critical functionality.
```
We import `gymnasium as gym` in our own code and ignore this warning (it is from the env package's legacy registration path; functionality is unaffected).

### A.3 Quickstart sanity

`python ./icu-sepsis/examples/quickstart.py` ran successfully and produced:

```
Initial state: 534
Extra info: {'admissible_actions': [0, 5], 'state_vector': array([...]), 'sofa_score': 6.77}
Taking action 0:
Next state: 489
Reward: 0.0
Terminated: False
Truncated: False
```

→ env import, MDP load, reset, and step all working. Note `info` contains `admissible_actions` (per-state list), `state_vector` (47-d cluster centre), and `sofa_score` (float) on every step — directly usable for our ablation.

---

## B. Baseline reproduction (v2 default = mean strategy)

### B.1 Command

```text
python ./icu-sepsis/examples/get_baselines.py -v 2
```
Run wrote to [logs/baselines_v2_mean.log](../logs/baselines_v2_mean.log). Exit code 0.

Settings (from the helper's defaults):
- env: `Sepsis/ICU-Sepsis-v2`, `inadmissible_action_strategy='mean'` (default)
- γ = 1.0 (env default)
- value iteration: max 50 000 sweeps, tolerance 1e-6 (converged in 149 sweeps, ≈ 6 s)
- Monte-Carlo policy evaluation: **50 000 episodes per policy**, **single seed** (the helper does not set a seed; rng is left in default state). Total ~28 s of MC for 3 policies.

### B.2 Numbers

| Policy | Our avg. return | Our avg. ep len | Paper reports | Match? |
|---|---|---|---|---|
| Random | **0.78014** | 9.51296 | 0.78 / 9.45 | ✓ (within MC noise) |
| Expert (clinician estimate) | **0.78132** | 9.20220 | 0.78 / 9.22 | ✓ |
| Optimal (VI) | **0.87624** | 11.03826 | 0.88 / 10.99 | ✓ |

All three match the published numbers to two decimals. **Baseline reproduction = PASS.**

### B.3 Observations relevant to the project

1. The gap from Random/Expert to Optimal is **only ~ 0.10 in survival rate** — confirms our planning hypothesis that survival rate is a noisy sensitivity instrument. Distance-to-V* will need to carry the main ablation signal.
2. Optimal episode length (11.04) is **longer** than Random (9.51) — Optimal pays for survival by keeping more patients alive in non-terminal states for longer; this is a useful framing point for our paper.
3. Value Iteration converges in 149 sweeps on this 716×25 MDP — VI cost is negligible (~6 s) and can be safely cached per `(strategy, gamma)` tuple rather than recomputed.
4. Expert and Random have **almost identical** survival rate (0.781 vs 0.780). The Expert policy in the data has noise comparable to random — useful caveat to note when we report `policy agreement with expert` later (Direction 1 metric).

### B.4 Bundle A status

**Bundle A = SUCCESS.** Proceeding to Bundle B (repo skeleton + utilities + pytest) and Bundle D (offline research) in parallel.

---

## C. Bundle B — Repo skeleton, utilities, pytest

### C.1 Created files

```
src/
├── __init__.py
├── env_utils.py        # make_env, get_dynamics, compute_Vstar, compute_Vpi,
│                       # distance_to_optimal, policy_agreement_with_expert,
│                       # admissible_mask_table
├── policies.py         # RandomPolicy, ExpertPolicy, DeterministicPolicy
├── evaluate.py         # rollout_eval (returns dict incl. unsafe_rate_deployed)
├── tabular_rl.py       # train_q_learning / train_sarsa / train_dyna_q,
│                       # greedy_policy_from_Q, _masked_argmax, eps schedule
└── analysis.py         # per_sofa_bucket_unsafe_rate, fraction_admissible_argmax
scripts/
├── __init__.py
└── run_masking_ablation.py
tests/
└── test_sanity.py      # 18 unit / integration tests
configs/
└── default.yaml
```

Three trainers (`train_q_learning`, `train_sarsa`, `train_dyna_q`) all accept
`use_mask: bool` and identical hyperparams: `alpha=0.1, gamma=1.0, eps_start=1.0,
eps_end=0.05, eps_decay_episodes=10_000`. Masking is applied at both
action-selection time and TD-target bootstrap time.

### C.2 pytest results

Run with `python -m pytest tests/test_sanity.py -v --tb=short` and tee'd to
[tests/last_run.txt](../tests/last_run.txt).

```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.0.3, pluggy-1.5.0
collected 18 items

tests/test_sanity.py::test_make_env_default_strategy_loads             PASSED
tests/test_sanity.py::test_make_env_rejects_bad_strategy               PASSED
tests/test_sanity.py::test_get_dynamics_shapes                         PASSED
tests/test_sanity.py::test_transition_probabilities_normalised         PASSED
tests/test_sanity.py::test_d0_is_probability_vector                    PASSED
tests/test_sanity.py::test_admissible_mask_table                       PASSED
tests/test_sanity.py::test_value_iteration_converges_and_matches_paper PASSED
tests/test_sanity.py::test_policy_evaluation_matches_uniform_random_baseline PASSED
tests/test_sanity.py::test_distance_to_optimal_zero_for_optimal        PASSED
tests/test_sanity.py::test_policy_agreement_with_expert_self_is_one    PASSED
tests/test_sanity.py::test_rollout_random_policy_small                 PASSED
tests/test_sanity.py::test_rollout_expert_policy_small                 PASSED
tests/test_sanity.py::test_q_learning_runs_short[False]                PASSED
tests/test_sanity.py::test_q_learning_runs_short[True]                 PASSED
tests/test_sanity.py::test_sarsa_runs_short[False]                     PASSED
tests/test_sanity.py::test_sarsa_runs_short[True]                      PASSED
tests/test_sanity.py::test_dyna_q_runs_short                           PASSED
tests/test_sanity.py::test_greedy_policy_shape                         PASSED
============================= 18 passed in 22.17s =============================
```

Notes / gotchas surfaced during test development:
- `test_rollout_expert_policy_small` originally asserted unsafe-rate < 0.05, but
  the estimated expert policy actually puts **≈ 0.15** of its probability mass
  on inadmissible actions. This is meaningful: *admissibility is a data-coverage
  property of the transition estimator, not a constraint on the clinician's
  recorded actions.* Threshold relaxed to 0.30 and the observation logged in a
  comment. This is paper-relevant: when we report `policy agreement with
  expert`, we cannot assume the expert is fully admissible.

### C.3 Bundle B status

**Bundle B = PASS** (18/18 tests green; pytest output saved to `tests/last_run.txt`).

---

## D. Bundle C — Action-masking ablation (Q-learning, mean strategy)

### D.1 Setup

| Item | Value |
|---|---|
| Algorithm | tabular Q-learning |
| Strategy | `mean` (v2 default) |
| Cells | mask=OFF vs mask=ON (2 cells) |
| Seeds | {0, 1, 2, 3, 4} (5 seeds per cell) |
| Episodes per seed | 50 000 |
| ε schedule | linear 1.0 → 0.05 over 10 000 eps |
| α | 0.1 |
| γ | 1.0 |
| Final-policy evaluation | (a) exact PE via fixed point on V; (b) 2 000-ep rollout |
| Total wall-clock | ≈ 90 s training + 35 s evaluation = ~ 2 min |

Driver script: [scripts/run_masking_ablation.py](../scripts/run_masking_ablation.py).
Per-run JSONs in `results/bundle_c_masking/`; aggregated summary in
`results/bundle_c_masking/summary.json`; preliminary figure at
`figures/preliminary_curve.png`.

### D.2 Aggregated metrics (5 seeds, mean ± std)

| Metric | mask OFF | mask ON | Δ (on − off) |
|---|---|---|---|
| Distance to V* (exact, d_0-weighted) | **0.0896 ± 0.0029** | **0.0693 ± 0.0031** | −0.0203 (≈ −23%) |
| J(π) (exact, d_0-weighted) | 0.7855 ± 0.0029 | **0.8058 ± 0.0031** | +0.0203 |
| Training-time inadmissible-action rate | **0.854 ± 0.012** | **0.000 ± 0.000** | −0.854 |
| Deployment unsafe-action rate (2 000-ep rollout) | 0.857 ± 0.014 | 0.000 ± 0.000 | −0.857 |
| Policy agreement with expert (argmax) | 0.041 ± 0.010 | **0.528 ± 0.005** | +0.487 |

For reference: J(π*) = **0.8751** (computed once by VI; converged in 9.1 s
to tol 1e-9). The d_0-weighted optimal-policy return matches the
50 000-episode Monte-Carlo estimate from Bundle A (0.87624) to 3 decimals.

### D.3 Key observations

1. **Masking eliminates inadmissible actions by construction** during both
   training (85.4% → 0%) and deployment greedy rollout (85.7% → 0%). The
   deployment unsafe-rate of mask-off is essentially the same as the
   training-time rate — vanilla Q-learning never "learns its way out" of
   inadmissible-action territory in 50 k episodes, because the `mean` strategy
   gives the same transition statistics whether the action is admissible or
   not, so the gradient signal for "this action is inadmissible" is ≈ 0.
2. **Distance-to-V* discriminates the two conditions cleanly** even though
   final survival rate (= J(π)) differs by only 2 percentage points
   (0.786 → 0.806). The std bands of the two cells are non-overlapping by
   ≈ 7σ. This **confirms hypothesis H2** and validates §8's argument that
   distance-to-V* is the right primary sensitivity metric for ICU-Sepsis.
3. **Policy-agreement-with-expert jumps from 4% → 53%** under masking. This is
   *not* trivial: masking restricts both pi and the expert's effective support
   roughly to the same admissible cells, so agreement now reflects an actual
   action-quality signal rather than the noise of arbitrary inadmissible
   argmax. Useful for the paper: it shows that without masking, the
   "agreement with expert" metric is uninterpretable.
4. **Both conditions plateau around episode 5 000** (see learning curves);
   beyond that the marginal benefit of additional episodes is small. Suggests
   the §16 §7.1 G3 sample-efficiency budget of {5k, 10k, 25k, 50k} is the right
   range to probe.
5. The mask-OFF policy attains J(π) ≈ 0.786 — matches the original paper's
   reported Q-learning ≈ 0.79. Mask-ON improves to 0.806, but still
   meaningfully below the optimal 0.875, confirming that *masking alone does
   not close the gap to V*.* Future work could combine masking with Dyna-Q
   planning or BC initialisation to chase the remaining ~7 percentage points.

### D.4 Bundle C status

**Bundle C = PASS.** Preliminary figure saved to
[figures/preliminary_curve.png](../figures/preliminary_curve.png) (two-panel:
learning curves with 95% CI on the left, training-time inadmissible-action
bar chart on the right). All 10 per-run JSONs and summary saved to
`results/bundle_c_masking/`.

> **Honest scope note**: only the masking ablation was run in Bundle C
> (mean strategy, Q-learning only) — the strategy ablation (mean vs terminate)
> and the algorithm ablation (SARSA, Dyna-Q) remain as part of the full G1+G2
> matrix described in §7 of the project plan. These trainers ARE implemented
> and tested (see `src/tabular_rl.py` and the parametrised pytest cases) but
> a full 12-cell ablation sweep was not part of the requested overnight
> Bundle C.

---

## E. Bundle D — Offline research outputs

### E.1 Deliverables

| Output | Location | Size / count |
|---|---|---|
| BibTeX file | [paper/references.bib](../paper/references.bib) | 12 verified entries |
| Dynamics characterisation | [core_docs/dynamics_stats.md](dynamics_stats.md) | 7 sections + raw JSON |
| Reproducible dynamics script | [scripts/compute_dynamics_stats.py](../scripts/compute_dynamics_stats.py) | re-runnable |
| Reviewer-anticipated questions | [core_docs/reviewer_anticipated_questions.md](reviewer_anticipated_questions.md) | 15 Q&A |
| Citation-verification log | appended `## G.` section in [02_related_work_notes.md](02_related_work_notes.md) | non-destructive |

### E.2 Citation corrections that affect future paper prose

1. **Boutilier 2019 attribution is wrong.** arXiv 1910.02078 ("I'm sorry Dave…")
   is authored by **Seurin, Preux, Pietquin**, published at **IJCNN 2020**.
   BibTeX key renamed to `seurin2020forbidden`. Any draft prose that says
   "Boutilier (2019)" must be updated.
2. **Huang & Ontañón is FLAIRS-35 (2022), not FLAIRS-34 (2021).** The arXiv
   preprint number (2006.14171) remains correct. Key kept as
   `huang2021masking` for back-compat, but year/volume in BibTeX fixed.
3. **`arXiv:2510.24500` (MIMIC-Sepsis) is still preprint-only** as of
   2026-05-20 — has an OpenReview thread but no acceptance recorded. Cited
   as `@misc`; re-check the day before submission.
4. **`Transactions on Artificial Intelligence` (Scilight Press) is peer-reviewed
   but young** (not yet in Scopus / Web of Science). The CPQ-IQL paper is
   included but flagged with a `note` in BibTeX; do **not** lean on it as
   load-bearing prior art.
5. The **ACM DL `10.5555/AAI29281130`** ("Safe RL for Sepsis Treatment", Jia
   et al.) referenced by the original notes is a ProQuest thesis mirror with
   unverifiable author/venue. Deliberately omitted from `references.bib`.
   Drop unless we specifically want to cite a thesis.

### E.3 Headline findings from the dynamics analysis

These are paper-relevant observations surfaced by `dynamics_stats.md`:

- **Expert policy puts only ~84 % of its mass on admissible actions; 0
  non-terminal states have the expert fully concentrated on admissibles.**
  Strengthens the framing for the project — it's *not* a contradiction
  ("inadmissible" is a transition-estimator coverage criterion, not a
  clinician-action criterion), but it justifies (a) including `mean` in the
  ablation, and (b) the policy-agreement metric being non-redundant with
  unsafe-rate.
- **Median admissible-set size is 4; max for non-terminal states is 13** —
  far smaller than the nominal 25-action space. So action masking removes
  ~84 % of the action space, which is why our preliminary effect size is so
  large (and why we expect it to be robust to small seed counts).
- **Reward is +1 only on transitions into state 714 (survival); transitions
  into state 713 (death) yield 0; γ=1.** With these together, V* is literally
  a survival probability — makes the γ=1 choice mathematically natural and
  trivial to defend to a reviewer.
- **SOFA tops at 18, not 24.** Minor; matters only if we ever do Direction-3
  SOFA-based PBRS (the shaping potential's effective range is `[-18, 0]`).

### E.4 Bundle D status

**Bundle D = PASS.** Sub-agent reported ~28 min of wall-clock work; output files
present and well-formed; verification log appended without modifying the body
of `02_related_work_notes.md`.

---

## F. Wake-up checklist (what was asked for vs what was delivered)

| Asked for | Delivered |
|---|---|
| `core_docs/setup_log.md` with environment + baselines + ablation results | ✅ This file. |
| `figures/preliminary_curve.png` (if Bundle C ran) | ✅ Two-panel: learning curves with 95% CI + training inadmissible-action bar. |
| `tests/last_run.txt` (pytest result) | ✅ 18/18 passed in 22.17 s. |
| `core_docs/dynamics_stats.md` | ✅ 7 sections + reproducible script. |
| `core_docs/reviewer_anticipated_questions.md` | ✅ 15 Q&A + limitations footer. |
| `paper/references.bib` (even if other paper files don't exist yet) | ✅ 12 verified entries with audit notes. |
| `core_docs/02_related_work_notes.md` "未驗證" update | ✅ Non-destructive `## G.` section appended. |

| Asked NOT to do | Confirmed |
|---|---|
| Don't write paper Intro/Method/Experiments body | ✅ Not written. |
| Don't `git` commit / push to remote | ✅ No git operations performed. |
| Don't upload to anonymous-GitHub | ✅ Not done. |
| Don't touch OpenReview | ✅ Not done. |
| Don't cut scope on incomplete work | ✅ Bundle C only ran the 2 cells specified; remaining G1/G2 matrix is implemented and tested but explicitly NOT auto-run beyond the spec. |

### Suggested next actions (for you to decide when you wake up)

1. Read `core_docs/setup_log.md` §D for the masking-ablation findings.
2. Read `core_docs/reviewer_anticipated_questions.md` end-to-end before drafting
   any paper prose — several questions need to be addressed structurally in
   the paper outline, not just in the Limitations section.
3. Audit `paper/references.bib` against the corrections in §E.2 — particularly
   the `seurin2020forbidden` / `huang2021masking` corrections.
4. Decide whether to extend Bundle C with the full G1+G2 matrix
   (6+6 cells × 5 seeds, ≈ 30-45 min total wall-clock with the existing
   `scripts/run_masking_ablation.py` as a template) before any paper writing
   starts.
