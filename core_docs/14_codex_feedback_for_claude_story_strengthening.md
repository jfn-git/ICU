# 14. Codex Feedback for Claude — Story Strengthening Priorities

> Purpose: 補充給 Claude 的 paper/story strengthening 建議。
>
> Context: 我根據 `06`, `09`, `submission/README.md`, `13`, `11/12`, `reviewer_anticipated_questions.md Q16`, 以及 `results/*/summary.json` 整理完研究故事流後，覺得目前故事已經很清楚，但還有幾個地方最值得補強，以避免 reviewer 覺得「只是 hard mask / ablation」或「tabular known-dynamics 太 toy」。

---

## 1. Current Story Is Strong, But the Weak Point Is Presentation

目前最強故事線是：

> `mean` imputation hides unsupported actions → vanilla Q-learning learns unsupported policies → support-aware remedies form a spectrum → behavior masking is the decisive fix → exact V* lets us measure value and overestimation precisely.

這條線很完整，尤其 `submission/README.md` 的結果已經足夠支持。

真正需要補強的不是「再多跑很多實驗」，而是 **把現有實驗呈現成 failure diagnosis + mechanism localization + remedy spectrum**，而不是一串 ablation。

---

## 2. Highest-Priority Weakness: Avoid Looking Like "Just Hard Masking"

Reviewer 可能的直覺反應：

> "If unsupported actions are bad, of course masking them helps. What is the research?"

建議 paper 一定要把主張從「masking helps」改成：

> The contribution is not that hard masking exists; the contribution is locating why ICU-Sepsis `mean` imputation hides unsupported-action behavior and showing, across remedy families, why behavior-level support control is the decisive intervention.

### What to emphasize

Use `run_component_ablation.py` as the centerpiece, not just `penalty_sweep`.

Key numbers:

| Variant | Distance-to-V* | Deploy unsupported | Q-leakage | Reading |
|---|---:|---:|---:|---|
| vanilla | 0.0896 | 0.8707 | +0.4594 | unsupported Q-values become competitive |
| target-only | 0.0850 | 0.7691 | +0.0699 | cleaning backup alone barely solves behavior |
| policy-only | 0.0834 | 0.0000 | +0.4594 | deployment band-aid; Q-table still corrupted |
| CQL κ=1 | 0.0801 | 0.0000 | -2.9513 | best soft remedy, still worse than hard support control |
| behavior-only | 0.0693 | 0.0000 | -0.7951 | necessary and sufficient |
| full mask | 0.0693 | 0.0000 | -0.7951 | same as behavior-only |

Suggested wording:

> Component ablation shows the failure is not primarily in the Bellman target or the final greedy extraction. Unsupported actions become harmful because they are sampled and updated under mean-imputed dynamics. Once behavior is restricted to supported actions, the target and final-policy masks add no additional gain.

This makes the paper feel like mechanism discovery, not just a wrapper trick.

---

## 3. Second Weakness: External Validity / "Known Dynamics Toy" Objection

Q16 already has the right defense. The paper should compress it into the main text, not leave it only for rebuttal.

Reviewer concern:

> "Exact V* from known dynamics is unusual; why should we care?"

Recommended main-text answer:

> ICU-Sepsis is not used here because it is clinically complete; it is used as a measurement instrument. Offline RL failures such as OOD-action overestimation are well known, but usually hard to evaluate exactly in healthcare because OPE is noisy. ICU-Sepsis gives a controlled tabular setting where support, dynamics, and V* are known, so we can isolate the failure mode cleanly.

Connect to:

- BCQ / BEAR / CQL / PEVI for generality of OOD-action problem.
- Gottesman healthcare RL warnings for why exact evaluation is valuable.
- ICU-Sepsis RLC/RLJ 2024 for benchmark legitimacy.

Suggested sentence:

> The generality of the phenomenon comes from offline-RL literature; the cleanliness of the measurement comes from ICU-Sepsis.

---

## 4. Third Weakness: Need One Overview Figure

Current results are rich, but a non-author reader needs one figure to orient them.

Recommended Figure 1 / overview schematic:

```text
Clinical data support threshold
        ↓
Admissible actions Adm(s)
        ↓
ICU-Sepsis default mean imputation:
P(s'|s,a_inadmissible) = average_{a∈Adm(s)} P(s'|s,a)
        ↓
Vanilla Q-learning:
samples unsupported actions → updates their Q-values → Q-leakage > 0
        ↓
Observed failure:
87% deployed unsupported actions, but return looks normal
        ↓
Remedy spectrum:
penalty → CQL-style conservatism → expert projection → hard mask
        ↓
Exact evaluation:
distance-to-V*, unsupported rate, Q-leakage
```

Caption idea:

> Mean imputation makes unsupported actions learnable without penalty. Our experiments diagnose where this enters TD learning and compare support-aware remedies under exact value evaluation.

This overview figure will help keep all experiments from feeling scattered.

---

## 5. Fourth Weakness: Clarify Main vs Supplement

Do not let all seven scripts appear equal. Suggested hierarchy:

### Main Results

1. **Penalty sweep / remedy spectrum**  
   Proves soft penalties trace a support-value trade-off, but hard mask is Pareto-best.

2. **Component ablation + Q-leakage**  
   Proves behavior-level sampling is the decisive mechanism.

3. **Offline dataset-size sweep**  
   Proves naive mean-imputation overestimates value under finite data; pessimism/masking are better calibrated.

### Supplement

4. **Expert prior**  
   Shows clinician guidance helps, but raw expert inherits unsupported mass; projection fixes it.

5. **Dead-end analysis**  
   Honest negative: no exact dead-ends, but harm/severity structure still informative.

6. **Robustness**  
   Shows the effect is not Q-learning-only and is specific to `mean` vs `terminate`.

This hierarchy should appear explicitly in the paper text or appendix organization.

---

## 6. Fifth Weakness: Uncertainty / Per-Seed Visibility

Most tables show 5-seed means. To preempt "five seeds is too few":

- In main text: report mean ± std or 95% CI for primary metrics.
- In appendix: add per-seed scatter for the three main figures.
- For large effects, explicitly say the conclusion does not depend on small survival-rate differences.

Priority figures for per-seed scatter:

1. Penalty trade-off: distance-to-V* vs deployed unsupported.
2. Component ablation: distance-to-V* and Q-leakage.
3. Offline data-size: overestimation and realized distance.

Suggested wording:

> We do not base our conclusion on small return differences alone. The headline effects are large-support diagnostics: vanilla deploys unsupported actions in 87% of states, whereas behavior masking and hard masking reduce this to zero; Q-leakage flips from +0.46 to -0.80.

---

## 7. Sixth Weakness: Be Careful With "Dead-End" Result

Dead-end analysis is useful, but it is not a positive main result.

Key result:

- no hard dead-ends: min V* = 0.1976
- no near-dead-ends under threshold 0.1
- 427/713 states are "secured" under V* > 0.9

Do not oversell dead-end contribution.

Recommended framing:

> We attempted an exact dead-end analysis motivated by clinical RL literature. ICU-Sepsis contains no true dead-ends under the benchmark dynamics, which is itself useful calibration. The analysis still reveals that inadmissible actions have higher one-step death risk (0.0323 vs 0.0226) while mean imputation compresses their long-run Q* gap.

This reads as honest scientific reporting rather than a failed main experiment.

---

## 8. Seventh Weakness: Expert Prior Should Be Framed as "Projection", Not "Imitation"

Expert-prior result is strong:

- raw expert prior: distance 0.0736, deploy unsupported 0.0788, agreement 0.6048
- projected expert: distance 0.0731, deploy unsupported 0.0050, agreement 0.6474
- expert inadmissible mass: 0.1564

Suggested framing:

> Expert guidance is useful, but raw clinician priors are not automatically support-respecting. Projecting expert exploration onto the benchmark's admissible set retains the value benefit while nearly eliminating deployed unsupported actions.

This avoids making it a separate imitation-learning paper.

---

## 9. Suggested Paper-Level Claim Stack

Use a three-layer claim structure:

### Claim 1: Failure

`mean` imputation hides unsupported action behavior: vanilla Q-learning deploys unsupported actions in about 87% of states.

### Claim 2: Mechanism

Unsupported actions are harmful because they are sampled and updated under mean-imputed dynamics; Q-leakage is +0.459 in vanilla and becomes -0.795 under behavior/full mask.

### Claim 3: Remedy Spectrum

Support penalties and CQL-style conservatism help, but hard behavior-level admissibility control gives the best value-support trade-off; offline finite-data experiments confirm naive mean-imputation overestimates value while pessimism/masking improve calibration.

This stack is stronger than saying "masking improves performance."

---

## 10. Quick Checklist for Claude While Writing

- [ ] Put an overview schematic early.
- [ ] Make component ablation the mechanism centerpiece.
- [ ] Use exact V* as "measurement instrument", not "optimization claim".
- [ ] Explicitly label main vs supplement results.
- [ ] Report uncertainty / per-seed scatter for main figures.
- [ ] Frame dead-end as honest calibration, not headline contribution.
- [ ] Frame expert prior as admissible projection, not full imitation learning.
- [ ] Avoid "clinically safer"; use "benchmark-internal", "data-support", "unsupported-action".

