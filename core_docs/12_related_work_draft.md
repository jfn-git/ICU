# 12. Related Work Draft

> English draft for the paper. Length: approximately 500 words.
> This is written for an anonymous submission and avoids institutional or identity-revealing language.

## Related Work

**Medical RL benchmarks and sepsis treatment.**
Reinforcement learning has been widely studied for sepsis treatment, beginning with the AI Clinician line of work, which formulates treatment as a Markov decision process over patient state clusters and fluid / vasopressor actions. Subsequent work has explored continuous-state deep RL models for sepsis and other dynamic treatment regimes. A recurring difficulty in this literature is reproducibility: many studies require protected clinical data access, nontrivial cohort construction, and off-policy evaluation from observational trajectories. ICU-Sepsis addresses part of this problem by providing a lightweight 716-state, 25-action tabular benchmark derived from MIMIC-III, with known transition dynamics and exact value-iteration baselines. Our work uses this benchmark not to propose a clinical treatment policy, but to study how one of its modeling choices -- inadmissible-action handling -- changes learned RL behavior.

**Offline RL and out-of-distribution actions.**
Offline RL studies how to learn policies from fixed datasets without further environment interaction, where distribution shift and low-support actions can cause severe extrapolation or bootstrapping error. BCQ constrains learned policies toward actions likely under the dataset, BEAR constrains backup actions to reduce bootstrapping error, CQL learns conservative Q-values that lower-bound policy value, and pessimistic value-iteration methods subtract uncertainty penalties under insufficient coverage. ICU-Sepsis's inadmissible actions are a natural medical-benchmark instance of this same support problem: they are actions whose state-action counts were too low to estimate transitions reliably. Our work differs from standard offline RL by using a benchmark where the support partition is explicit and V\* is exactly computable, allowing direct comparison of support penalties, pessimism, behavior constraints, and hard masking.

**Invalid actions and action masking.**
Invalid-action masking has been studied in large discrete action spaces, especially in policy-gradient settings, where masking often outperforms penalties when invalid actions are common. Related work on forbidden actions in Q-learning adds losses that suppress Q-values of disallowed actions. These settings typically treat invalidity as a hard environmental rule. In ICU-Sepsis, inadmissibility has a different meaning: it indicates insufficient statistical support in the clinical source data, not medical impossibility. This distinction motivates evaluating hard masks alongside softer support-aware penalties and conservative updates rather than treating masking as the only reasonable remedy.

**Risk, dead-ends, and expert guidance in clinical RL.**
Medical RL work has also studied high-risk states and expert-guided learning. Fatemi et al. define medical dead-ends as states from which death is unavoidable regardless of future treatments and learn detectors from clinical data. ICU-Sepsis allows a complementary analysis: because reward is a survival indicator and the model is known, V\*(s) is the exact maximum survival probability under the benchmark, so dead-end-like states can be computed directly rather than estimated. Demonstration-based RL methods such as DQfD motivate clinician-guided initialization or exploration, but ICU-Sepsis also reveals that empirical clinician policies may place nonzero mass on inadmissible actions; therefore, expert guidance and admissibility constraints should be analyzed jointly.

**Evaluation pitfalls in healthcare RL.**
Healthcare RL guidelines emphasize that observational evaluation can be misleading because of confounding, representation choices, high-variance off-policy estimators, and overclaiming clinical relevance. ICU-Sepsis does not remove all abstraction concerns, but it does provide exact model-based evaluation, enabling distance-to-V\* and exact Vπ metrics in addition to rollout return. We therefore report benchmark-internal value, unsupported-action rate, and expert-agreement diagnostics, and avoid interpreting these quantities as clinical recommendations.

