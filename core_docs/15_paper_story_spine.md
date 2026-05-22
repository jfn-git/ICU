# 15. Paper Story Spine — Integrated Blueprint (Claude × Codex)

> Single blueprint for writing the paper. Merges Codex's story-strengthening
> feedback (`14`) with the source/paper fact-check (`reviewer_anticipated_questions.md`
> Q16/Q17, `11` §4.3/B.3 positioning). All numbers verified against `results/*/summary.json`.
> Language rules are binding (benchmark-internal, never clinical).

---

## 0. Title (working options)

- **When Mean Imputation Hides Unsupported Actions: Diagnosing and Fixing an OOD-Action Failure Mode in ICU-Sepsis**
- alt: *Support-Aware Tabular RL on ICU-Sepsis: Locating and Repairing a Hidden Out-of-Distribution-Action Failure*

One-line pitch: *ICU-Sepsis's default mean-imputation makes data-unsupported
actions look average, so model-free agents drift into them at no apparent cost;
we use the benchmark's exact V* to localize the failure to behavior-level
sampling and to compare a spectrum of support-aware remedies.*

---

## 0b. Significance positioning (for Intro/Discussion) — L1/L2/L3 + red line

Value chain (each step is field consensus except step 4, which is our contribution):
1. medical RL is almost always **offline** (can't experiment on patients) — consensus.
2. the core difficulty of offline RL is **OOD / unsupported actions** — consensus.
3. "some treatments are rarely tried" is **intrinsic to medical data** — consensus.
4. **how a pipeline handles unsupported actions silently changes what the agent
   learns, and outcome metrics (survival rate) hide it** — our clean demonstration.
5. ⇒ offline medical-RL practitioners should treat unsupported-action handling as a
   consequential, often-hidden design choice; measure support diagnostics, not only
   outcomes; use behavior-level support-aware learning.

Three levels of value (pick wording by audience):
- **L1 (safest, benchmark)**: ICU-Sepsis users must report inadmissible-action handling
  and support diagnostics (distance-to-V*, unsupported rate), not just survival rate.
- **L2 (the push, defensible)**: a *methodological caution + diagnostic/remedy protocol*
  for offline medical RL broadly, since data-coverage gaps are intrinsic. What transfers
  is the **phenomenon + protocol + the behavior-level support-aware practice**, NOT the
  specific numbers.
- **L3 (red line, never)**: "improves sepsis treatment / safer policy / deployable."

Anchors that give it weight: operationalizes a caution from \emph{Guidelines for RL in
healthcare} (Gottesman et al., Nature Medicine 2019); provides a rare exact-evaluation
instance of the OOD-action problem the offline-RL literature (BCQ/CQL/pessimism) knows
matters but usually cannot measure cleanly.

Ready significance sentence (drop into Intro/Discussion):
> Offline medical RL inherently learns from logged data with uneven action coverage;
> how a pipeline handles data-unsupported actions is a consequential design choice that
> outcome metrics can hide. Using a known-dynamics medical benchmark as a controlled
> testbed, we make this failure visible and exactly measurable, localize its mechanism,
> and provide a support-aware diagnostic-and-remedy protocol for offline medical-RL
> practitioners — a methodological caution, not a clinical recommendation.

---

## 1. The three-layer claim stack (the spine)

### Claim 1 — FAILURE (hardened with the Q17 rebuttal — do NOT state it bare)
Under the default `mean` strategy, vanilla Q-learning deploys inadmissible
(data-unsupported) actions in ~87% of non-terminal states **and this carries a
real value cost, not just a labeling artifact**: J(π)=0.785 ≈ Random 0.780 ≈
Expert 0.782, while admissibility control reaches 0.806 (J*=0.875). The agent
"learns" a policy no better than random action selection, and survival rate
hides it (the benchmark paper reports only return/length/convergence).

> Pre-empt immediately: the benchmark *defines* inadmissible transition = mean of
> admissible (§4.3) and calls it "equivalent to a random admissible action." That
> equivalence is exactly why it costs value (random-admissible < best-admissible)
> and is a closed-world artifact (off-benchmark, unsupported actions do not behave
> like the average). → cite Q17.

### Claim 2 — MECHANISM (the centerpiece; makes it "mechanism discovery", not "masking helps")
Component ablation localizes the failure to **behavior-level sampling**.
Masking behavior alone is necessary AND sufficient; target-only and policy-only
do not fix it; Q-value leakage gives the mechanistic picture.

| Variant | dist-V* | deploy-unsupp | Q-leakage | reading |
|---|---:|---:|---:|---|
| vanilla | 0.0896 | 0.871 | +0.459 | unsupported Q-values become competitive |
| target-only | 0.0850 | 0.769 | +0.070 | cleaning the backup alone barely helps |
| policy-only (deploy) | 0.0834 | 0.000 | +0.459 | band-aid; Q-table still corrupted |
| CQL κ=1 | 0.0801 | 0.000 | −2.95 | best *soft* remedy, still trails |
| **behavior-only** | **0.0693** | 0.000 | −0.795 | necessary & sufficient |
| full mask | 0.0693 | 0.000 | −0.795 | identical to behavior-only |

> Wording: "Unsupported actions become harmful because they are *sampled and
> updated* under mean-imputed dynamics. Once behavior is restricted to supported
> actions, target and final-policy masks add no further gain."

### Claim 3 — REMEDY SPECTRUM (online + offline)
Support penalties trace a support–value trade-off but are Pareto-dominated by
hard masking; CQL-style value conservatism is the best soft remedy but still
trails. In the **finite-data offline** regime (empirical MDP from N expert
transitions), naive mean-imputation **overestimates** its own value (+0.21) and
its realized policy **stagnates** (~0.093) with more data, while pessimistic
VI-LCB is calibrated (~0) and improves (→0.069) and admissibility-masking removes
unsupported actions (0) and reaches 0.065. Exact V* is what makes overestimation
measurable.

---

## 2. Section-by-section outline (→ which result feeds it)

| Section | Content | Source |
|---|---|---|
| Abstract | problem → mean-imputation hides OOD actions → exact-V* testbed → diagnosis+mechanism+remedy spectrum → benchmark-internal disclaimer | — |
| 1. Introduction | medical RL benchmarks → ICU-Sepsis → the hidden OOD-action failure → contributions (3-layer stack) | §1 here |
| 2. Related Work | offline RL OOD (BCQ/BEAR/CQL/PEVI), invalid-action masking, sepsis RL, dead-ends, eval pitfalls (Gottesman) | `12`, `11` |
| 3. Background | ICU-Sepsis MDP; admissibility (τ=20); **§4.3 mean imputation (quote)**; γ=1 ⇒ V*=survival prob; exact eval | `11` §4.3, Q9/Q12 |
| 4. Method | OOD reframing; remedy spectrum (penalty / CQL-conservatism / behavior+target+policy masks); metrics (dist-V*, deploy-unsupp, Q-leakage, overestimation, agreement) | `submission/README`, `src/` |
| 5. Experiments | baselines (Tbl1); **Claim1 failure; Claim2 component ablation+leakage; Claim3 penalty sweep + offline sweep**; supplements (expert, robustness, dead-end) | results/* |
| 6. Discussion | why survival hides it; why exact-V* (measurement instrument, Q16); benchmark guidance (report inadmissible handling) | Q16 |
| 7. Limitations | tabular/known-dynamics scope & transfer; 5 seeds; data-support≠clinical; expert not fully admissible | honest gaps |
| 8. Conclusion | concise takeaway | — |

---

## 3. Main vs supplement (state this hierarchy explicitly)

**Main results**
1. Failure diagnosis (Claim 1) — `run_penalty_sweep.py` (vanilla endpoint) + baselines.
2. Component ablation + Q-leakage (Claim 2) — `run_component_ablation.py`. ← centerpiece.
3. Remedy spectrum online + **offline dataset-size sweep** (Claim 3) — `run_penalty_sweep.py`, `run_offline_datasize.py`.

**Supplements**
4. Expert prior + admissible projection — `run_expert_prior.py` (frame as *projection*, not imitation).
5. Robustness across algos & strategies — `run_robustness.py` (not Q-learning-only; `mean`-specific).
6. Dead-end / harm structure — `run_deadend_analysis.py` (honest negative: no dead-ends; calibration).

---

## 4. Overview Figure 1 (schematic — build this)

```
data-support threshold τ=20  →  admissible set Adm(s)
        ↓
ICU-Sepsis default mean imputation:  P(s'|s, a∉Adm) = mean_{a∈Adm} P(s'|s,a)   [§4.3]
        ↓
vanilla Q-learning samples & updates unsupported actions  →  Q-leakage > 0
        ↓
observed failure: ~87% deployed unsupported actions, J(π)≈Random, but survival "looks normal"
        ↓
remedy spectrum: penalty → CQL conservatism → (behavior/target/policy) masking
        ↓
exact evaluation: distance-to-V*, unsupported rate, Q-leakage, overestimation
```
Caption: "Mean imputation makes unsupported actions learnable without penalty; we
diagnose where this enters TD learning and compare support-aware remedies under
exact value evaluation."

---

## 5. Key numbers (verified; pull from here when writing)

- Baselines: Random 0.780 / Expert 0.782 / Optimal J*=0.875.
- Vanilla (mean): J=0.7855, dist-V*=0.0896, deploy-unsupp≈0.87, leak +0.459, agree 0.041.
- Hard/behavior mask: dist-V*=0.0693, J=0.806, unsupp 0, leak −0.795, agree 0.528.
- Penalty λ=0.1: dist 0.0831, unsupp 0.345; λ=1.0: dist 0.0865, unsupp 0.000.
- CQL κ=1: dist 0.0801, leak −2.95; κ=2: dist 0.0893 (over-conservative).
- Expert: inadmissible mass 0.156; raw 0.0736/unsupp 0.079/agree 0.605; projected 0.0731/unsupp 0.005/agree 0.647.
- Dead-end: min V*=0.198; 0 dead-ends; 427/713 secured (V*>0.9); SOFA mean V* 0.916→0.823; one-step death adm 0.0226 vs inadm 0.0323.
- Robustness (mean→mask): q 0.0896→0.0693, sarsa 0.0906→0.0720, dyna 0.0875→0.0696; terminate vanilla deploy-unsupp ≈0.03–0.04.
- Offline N=100k: naive overest +0.208 / dist 0.0935 / unsupp 0.857; pess +0.049 / 0.0688 / 0.403; masked +0.104 / 0.0645 / 0.000.

---

## 6. Defenses to inline in main text (not just rebuttal)

- **Q17 (≡ random admissible ⇒ harmless?)** → fold into Claim 1 (cost is real: J≈Random; closed-world artifact). Cite §4.3.
- **Q16 (known-dynamics toy?)** → one Discussion paragraph: measurement instrument, not optimization claim; generality from offline-RL literature, cleanliness from ICU-Sepsis; exact eval sidesteps OPE (Gottesman).
- **Cite Appendix B.3** (their perturbation/robustness check) and differentiate: it measures return robustness (insensitive by construction); we measure selection rate / dist-V* / mechanism / remedies.

---

## 7. Language rules (binding)

- Use: "data-support", "unsupported / inadmissible action", "benchmark-internal", "admissibility-respecting", "policy value / distance-to-V*".
- Avoid: "clinically safer", "improves survival", "inadmissible = medically wrong", "should be deployed".
- Per-seed: report mean ± 95% CI for primary metrics; appendix per-seed scatter; never lean on small survival-rate differences — lean on large-support diagnostics (87%→0, leak +0.46→−0.80).
- Dead-end: honest calibration, not a headline. Expert: *projection*, not imitation.

---

## 8. Writing checklist (from `14`, retained)
- [ ] Overview schematic early.
- [ ] Component ablation = mechanism centerpiece.
- [ ] Exact V* = measurement instrument framing.
- [ ] Explicit main vs supplement labels.
- [ ] Uncertainty / per-seed scatter on main figures.
- [ ] Q17 + Q16 inlined; §4.3 + B.3 cited.
- [ ] Benchmark-internal language throughout.
