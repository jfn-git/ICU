# Anticipated reviewer criticisms and our planned responses

> Drafted 2026-05-20 (autonomous overnight pass). Starting point: §13 of
> `04_project_plan_icu_sepsis.md`. The 15 entries below extend that risk
> table with concrete reviewer-style framings and longer responses, including
> the questions the user listed in the brief and several that arose from the
> dynamics analysis in `dynamics_stats.md`.
>
> The convention is: a NeurIPS-style reviewer comment, then a short response
> we can either inline in the paper or deploy in a rebuttal. We mark genuinely
> unresolved issues with "→ acknowledge in Limitations" so we don't pretend
> we have answers we do not.

---

## Q1. "Tabular Q-learning / SARSA / Dyna-Q on a 716-state MDP is not deep RL — this is not appropriate for a deep-RL venue."

The ICU-Sepsis benchmark (Choudhary et al., RLJ 2024) was itself published
at the Reinforcement Learning Conference and is a tabular benchmark by
construction: the source paper evaluates Q-learning, SARSA, DQN, SAC, and
PPO and reports that survival rate plateaus near 0.79 for the tabular
methods. Our contribution is not a new algorithm; it is a systematic
characterization of how the benchmark's own "inadmissible action handling"
modes interact with three canonical model-free / model-based tabular
algorithms. We additionally include a single DQN baseline (Appendix) with
one-hot state encoding and masked action sampling so reviewers can see the
same trends in a deep setting. The framing is "benchmark analysis" in the
NeurIPS Datasets & Benchmarks sense, not "new SOTA on a deep RL task."

## Q2. "Why not just run on MIMIC-III directly? That is the gold-standard sepsis-RL setting."

Three reasons. (1) MIMIC-III access requires CITI training and a credentialed
PhysioNet account, which is not available within a 5-day project window;
ICU-Sepsis was explicitly designed (per the authors' Abstract) so that
"researchers can use the benchmark without needing access to MIMIC-III."
(2) MIMIC-III sepsis evaluation is fundamentally an off-policy evaluation
problem; OPE on MIMIC has known bias and variance issues (Gottesman et al.,
Nature Medicine 2019), and any conclusion about the *effect of an
algorithmic ablation* on a MIMIC pipeline confounds the ablation with OPE
noise. ICU-Sepsis has a known model so we can compute the exact `V*` and
the exact `V^π` for any tabular policy — that lets the project's main
metric (distance-to-V*) be measured without OPE error at all. (3) The
project's contributions are about the *benchmark's* mechanisms
(`inadmissible_action_strategy`, action masking), which exist only in
ICU-Sepsis-v2; they have no analogue on raw MIMIC-III.

## Q3. "Why these three tabular algorithms (Q-learning, SARSA, Dyna-Q) and not e.g. CQL, IQL, BCQ?"

Q-learning, SARSA, and Dyna-Q span the canonical
off-policy / on-policy / model-based triad while sharing tabular
update structure. This is intentional: holding the function-approximator
class fixed (`Q: S × A → R`, no neural network) lets us attribute
differences to the algorithm's bootstrap target rather than to
approximation error. CQL/IQL/BCQ are *offline* algorithms — they require
a logged dataset, not the env's simulator, and they would conflate the
ablation with offline-RL pessimism hyperparameters. We discuss extending
to offline RL using the same ablation matrix as future work.

## Q4. "Five seeds is too few; show variance properly and demonstrate statistical significance."

We report mean ± 95 % CI (computed via percentile bootstrap with 10 000
resamples per cell) over 5 seeds in the main tables, and per-seed scatter
in the appendix so readers can see individual runs. Five seeds is on the
low end of recommended practice (e.g. Henderson et al. 2018 use ≥ 10), so
we flag this in Limitations and note that the most cost-sensitive comparisons
(masked vs unmasked, and `mean` vs `terminate`) have effect sizes that
exceed 5-seed CI under our metrics — masking reduces median episodes-to-
threshold by an order of magnitude, which is robust to seed variance.
For metrics where the effect is small (e.g. final survival rate, which
itself only spans 0.78–0.88 in the original paper) we explicitly do not
claim significance and instead pivot to the distance-to-V\* metric, which
is more sensitive.

## Q5. "Doesn't action masking trivially reduce the inadmissible-action rate to 0 by definition?"

Yes, for the **training-time** inadmissible-action rate of a masked agent
the metric is identically 0 — that is exactly the design intent of masking
and is not a claim we are testing. The interesting metric is
*evaluation-time* unsafe behaviour under a *masked-trained* policy when
deployed in the *unmasked* env. Concretely: we train with mask, then strip
the mask at evaluation and ask what fraction of greedy choices are inadmissible.
If the masked-trained Q-function has not learned to *prefer* admissible
actions (only to *pick from* admissible actions at training time), then its
deployment-time unsafe-action rate will be high. This is a real
generalization question and is the headline metric we will report.
The unmasked variants serve as the relevant baseline against which we
measure how much "what the agent is actually trained to prefer" deviates
from "what the agent is forced to do at training time."

## Q6. "How do you know your inadmissible-action-rate metric isn't gameable / cosmetic?"

We report inadmissible-action rate together with three other metrics
(survival, distance-to-V*, policy-agreement-with-expert). An agent that
games one metric by trivially memorising the admissible mask will show
this trade-off in the other three — in particular, masking that throws
away genuinely high-value but borderline-rare actions will move
distance-to-V\* up. We also report inadmissible rate *bucketed by SOFA-score
quintile*: a method that reduces inadmissible rate only in low-SOFA states
(where the patient is doing fine and any action is roughly equivalent) is
materially different from one that reduces it in high-SOFA states (where
inadmissibility is most consequential). This bucketed view makes the metric
hard to game by averaging.

## Q7. "What is the actual decision-theoretic difference between `mean` and `terminate`?"

They differ in how an inadmissible action `(s, a)` propagates the value
function: `mean` makes `(s, a)` behave dynamically identically to *taking
some admissible action sampled with the cohort-average distribution*, so
the inadmissible-action `Q(s, a)` converges toward `mean_{a' ∈ adm(s)}
Q(s, a')`. `terminate`, in contrast, transitions deterministically to the
DEATH state, so `Q(s, a) → 0` for any inadmissible `(s, a)`. The first
sends an *attractive* signal that inadmissible actions are roughly average,
which can mask exploration mistakes; the second sends a *punitive* signal
of −1 worth of survival probability per inadmissible decision, which
sharpens the learned policy toward admissible actions but at the cost of
training-time data corruption (some bona-fide-good trajectories get
truncated by a single inadmissible mistake). Our framing is that these
choices interpolate between "soft prior on admissibility" (`mean`) and
"hard penalty on admissibility" (`terminate`), and the project's purpose
is to *measure* where that interpolation lands on the safety-vs-efficiency
plane.

## Q8. "Are the admissible-action sets the same across seeds? Across `inadmissible_action_strategy` modes?"

Yes — and this is important to state explicitly. The admissible sets are
defined at *env construction time* from the source cohort's empirical
action counts (the `tau = 20` threshold) and are deterministic features
of the saved `dynamics` dict. They do not vary with the env seed and they
do not vary with the `inadmissible_action_strategy` setting. So all
within-cell comparisons (across 5 seeds) and all across-cell comparisons
(across 3 strategies × 2 mask settings × 3 algos) share an identical
admissibility partition, and any differences we report are due to
algorithm × strategy interactions, not to admissibility re-sampling.

## Q9. "Why γ = 1?"

The reward is +1 on transition into state 714 (survival) and 0 everywhere
else (we confirmed this directly by scanning `r_mat` — see
`dynamics_stats.md` §4). Episode length is bounded by `MAX_EPISODE_STEPS =
500`, so the undiscounted return is well-defined and is exactly the
survival probability. Discounting (γ < 1) would interpret a 10-step
survival as less valuable than a 1-step survival, which is the *opposite*
of clinical interest. The original paper sets γ = 1 for the same reason,
and our distance-to-V\* metric requires fixing the same γ as the V\*
computation. We include a γ = 0.99 sensitivity row in the Appendix to
satisfy the standard reviewer request, but the main tables use γ = 1.

## Q10. "What if `mean` is actually closer to clinical reality, because clinicians DO sometimes select under-supported actions?"

This is a real concern, and our dynamics analysis (§7 of
`dynamics_stats.md`) supports the reviewer's intuition directly: the env's
own *expert policy* places only ~84 % of its probability on admissible
actions, and in 0 of 713 non-terminal states is the expert fully
concentrated on admissibility. So clinicians in the source cohort
demonstrably do choose inadmissible actions about 16 % of the time. We
explicitly do **not** claim `terminate` is the "right" strategy; we
characterize the two *learnable* strategies, `mean` and `terminate`
(`raise_exception` is debug-only and excluded from the learning comparison
— see Q11). In Discussion we argue that `mean` is the most faithful to
clinical reality while `terminate` makes the inadmissibility signal explicit
but at a learning cost (vanilla Q-learning/SARSA reach a *worse*
distance-to-V* under `terminate` than under `mean`, ~0.107 vs ~0.090, because
death truncations corrupt model-free learning; see robustness results). The paper's recommendation will be **strategy choice is a
design knob the benchmark user should make explicit, not a hidden default
to ignore** — which is itself the contribution.

## Q11. "raise_exception isn't a learning strategy — why include it in the matrix at all?"

We do **not** include `raise_exception` in the learning matrix, and we are
explicit about why (so this is an honest scoping decision, not an omission).
By construction it raises an exception the moment any inadmissible action is
selected, so a vanilla (unmasked) agent crashes on its first exploratory
inadmissible step and cannot be trained. The only way to run under
`raise_exception` is to mask behavior so inadmissible actions are never
selected — but then the run is identical to masking under any other strategy
(the strategy branch is never reached), yielding no new learning information.
We therefore treat it as a debug/assertion mode (a guarantee that a masked
agent never violates admissibility), not as a learning condition. Our strategy
comparison is `mean` vs `terminate` (robustness experiment), where both are
genuinely learnable.

## Q12. "Your distance-to-V* assumes you have V* exactly. Are you sure the env's known dynamics let you compute it?"

Yes. `tx_mat` is a deterministic numpy array shipped with the package
(shape `(716, 25, 716)`, ≈ 25 MB in memory), and we can run value
iteration to floating-point convergence in seconds: see `src/env_utils.py`
`compute_Vstar()`. We checked the row-sum sanity (each admissible row of
`tx_mat` sums to 1.0 within 5e-16; see `dynamics_stats.md` §3) so no
projection / normalization step is needed. Distance-to-V\* under γ = 1 and
the bounded reward `r ∈ {0, 1}` is well-defined and lies in `[0, 1]`. We
also report agreement with the optimal greedy policy as a coarser but
intuition-friendly companion metric.

## Q13. "How is `expert_policy` constructed? Is it really clinician behaviour, or a clustered abstraction?"

It is the cohort-empirical clinician policy with low-count actions
(seen < τ = 20 times in the source MIMIC-III sepsis cluster) zeroed and
the remaining mass renormalized — per the package docstring on
`ICUSepsisEnv.expert_policy`. This is a smoothed statistical abstraction
of "what clinicians did," not a clean expert trajectory. We are careful
to call it *empirical clinician policy* in the paper text, not "expert
policy" in the imitation-learning sense, and we benchmark against it as a
behavioural baseline rather than as a normative target. The
*policy-agreement-with-expert* metric measures how often our learned
policy chose what clinicians chose **conditional on the same patient
state**, not whether our policy is "right."

## Q14. "Three of your tabular methods will converge to nearly identical asymptotic survival rates (~0.79). What is the substantive difference?"

We agree this is a known feature of the benchmark — the paper reports
0.79 for both Sarsa and Q-learning, and we expect Dyna-Q to lie in the
same neighbourhood. The substantive differences we expose are *not* in
asymptotic survival but in (a) *sample efficiency* (episodes to first
reach 90 % of asymptotic survival), (b) *distance-to-V\* trajectory shape
over training*, and (c) *training-time unsafe-action rate*. In particular,
Dyna-Q with planning steps reduces episodes-to-threshold by an
order-of-magnitude over Q-learning in our preliminary curves, even
though both reach the same asymptote. So the *learning dynamics* is where
the ablation is informative; we tone down survival-rate claims and centre
the figures on the dynamics.

## Q15. "Why bucket SOFA-wise rather than use SOFA as a continuous covariate in regression?"

Two reasons. (1) Our state space is already discrete (716 states), and the
SOFA score is averaged within each state cluster, so the granularity is
finite — 5 quantile buckets matches the natural resolution shown in
`dynamics_stats.md` §5. (2) Quantile buckets make the headline
visualisation (an unsafe-rate-vs-SOFA bar chart, ablation across
strategies) interpretable without a parametric assumption that a reviewer
could attack ("why log-linear?"). For appendix purposes we additionally
fit `Pearson(unsafe_rate_s, SOFA_s)` per cell so the linear association
is available to skeptics, but we keep the quantile bar chart as the main
figure.

## Q16. "Computing the exact V* from known dynamics is unusual — isn't this a non-standard / immature environment, so optimizing on it is meaningless?" (added 2026-05-22)

This is the most strategic version of the "tabular" objection and deserves a
direct answer. Three points.

(1) **Exact V* is not a sign of immaturity; it is textbook tabular RL.** Value
iteration on a known finite MDP to obtain V* is standard material (Sutton &
Barto; Puterman). It is "rare" only relative to *deep/applied* RL (Atari,
robotics, raw MIMIC), where V* is uncomputable and one must fall back on OPE.
ICU-Sepsis deliberately lives in the tabular regime where exact computation is
both possible and standard. Using it is not a loophole; it is using the tool as
designed.

(2) **The benchmark is legitimate and the known-dynamics property is its
intended design.** ICU-Sepsis was published at RLC 2024 / RLJ 2024 (Choudhary,
Gupta, Thomas — UMass). Its stated purpose is to give a small, fully-specified,
reproducible MDP so researchers can run controlled studies *without* MIMIC-III
access or OPE noise. We use it exactly as intended. The reward = survival
indicator with γ = 1 (so V*(s) = max survival probability) is a clean episodic
formulation, not a bug (see Q9, Q12).

(3) **Known dynamics is our measurement instrument, not our claim.** We are not
asserting "we optimized a policy on a toy and that is impressive." We run a
*diagnostic / methodological* study; exact V* is what lets us measure precisely.
The analogy we deploy in rebuttal: physics studies frictionless planes and
biology uses model organisms (Drosophila, C. elegans) precisely *because* the
simplified, controllable system isolates a phenomenon cleanly — nobody dismisses
a mechanistic finding in Drosophila because flies are simpler than humans. The
phenomena we study (OOD/unsupported actions, value overestimation) are
*well-documented general offline-RL problems* (BCQ, BEAR, CQL); we contribute a
clean, exactly-measurable diagnosis of *where* the failure lives plus a
benchmark-design lesson (mean imputation hides it), not a quirk of a toy. The
generality comes from the literature link; the cleanliness comes from the exact
environment. Finally, exact evaluation is a *strength* here: the healthcare-RL
literature explicitly warns that OPE is unreliable (Gottesman et al., Nature
Medicine 2019), so sidestepping OPE is a feature reviewers tend to reward.

→ The one legitimate residual is **external validity / transfer** to
function-approximation / continuous / deep settings — acknowledged in
Limitations (below). Our offline empirical-MDP dataset-size sweep
(`run_offline_datasize.py`) is a first step toward the realistic finite-data
regime: it shows the same naive-overestimation / pessimism / masking ordering
when the model must be *estimated from N transitions* rather than known.

## Q17. "The benchmark defines an inadmissible action's transition as the mean of the admissible actions, and the authors say this is *equivalent to choosing a random admissible action*. So selecting inadmissible actions is harmless by construction — your 85% 'unsupported-action rate' is a non-issue." (added 2026-05-22, after source/paper fact-check)

This is the most important objection to pre-empt, because it comes straight from
the ICU-Sepsis paper's own justification (§4.3: inadmissible transition =
`1/|A(s)| Σ_{a'∈A(s)} ζ(s,a',s')`; "equivalent to choosing one of the admissible
actions at random"). We verified the mean-imputation holds exactly in the shipped
dynamics (all 713 non-terminal states, inadmissible row == unweighted mean of
admissible rows to 7e-16). The premise is real and we do not dispute the authors'
construction. Our response has three parts.

(1) **"Equivalent to a random admissible action" is precisely the cost, not a
defense.** A random admissible action is worse than the *best* admissible action,
so a policy that selects mean-imputed actions earns random-admissible value, not
optimal value. Our numbers show exactly this: vanilla Q-learning under the default
`mean` strategy converges to J(π) = 0.785, essentially the Random (0.780) and
clinician/Expert (0.782) baselines, while admissibility masking reaches 0.806
(J* = 0.875). The default lets a model-free learner end up no better than random
action selection while *appearing* to have learned — and this is invisible in
survival rate, the only performance metric the original paper reports (return,
episode length, convergence; **no distance-to-V***). Our exact distance-to-V*
makes the cost visible.

(2) **The equivalence is a closed-world artifact.** "Inadmissible ≡ average
admissible" holds *only inside the benchmark*, by construction. In a real
deployment a data-unsupported action does **not** behave like the cohort average —
that is what "unsupported" means — so a policy that relies on inadmissible actions
is exactly the one that breaks under distribution shift. We keep this claim
benchmark-internal (we do **not** assert clinical danger), but it motivates why
support-aware learning is the right object of study.

(3) **Different from the paper's own robustness check (Appendix B.3).** The paper
does probe over-reliance on rare actions — but by randomly removing admissible
actions and measuring *return* robustness, concluding τ=20 is robust. That check
is insensitive to our phenomenon by construction: since inadmissible = average,
return is stable under such perturbations. We measure different things — the
*rate* at which default agents select inadmissible actions, the *exact* optimality
cost, the value-leakage mechanism, and a remedy spectrum. We cite §4.3 and B.3
explicitly and position our work as quantifying the cost of a documented,
author-justified design choice using metrics the paper does not use — not as
discovering an unknown bug.

---

## Honest gaps we will not paper over

- **N = 5 seeds is on the low end of community practice.** Acknowledged in
  Limitations; expanding to 10 seeds is the first thing we would do if
  granted compute.
- **No clinical validation.** Explicit, in Abstract and Discussion; we cite
  Gottesman et al. 2019 to anchor the "deliberately not a clinical
  recommendation" framing.
- **The env's `expert_policy` is not consistent with its own `admissible`
  definition** (only ~84 % of expert mass on admissible actions). This is
  a property of the benchmark we inherit, not something we can fix; we
  flag it in Discussion as a benchmark-level observation worth the
  community's attention.
- **No causal inference about which strategy is "best."** We characterize
  all three; we do not recommend one over another for production use.
  Addressed by changing claim verbs from "should use X" to "must be
  explicitly chosen and reported, because X moves metric Y by Z."
- **External validity / transfer beyond tabular.** All results are on a
  716-state tabular MDP with known dynamics. Whether the mean-imputation
  failure and the behavior-masking fix transfer to function approximation /
  continuous-state / deep-RL settings is untested and stated as scope in
  Limitations. The offline empirical-MDP sweep (`run_offline_datasize.py`)
  partially addresses this by moving from a *known* model to one *estimated
  from N transitions*, but it is still tabular. This is a scope limitation,
  not a validity flaw — exact V* on a tabular benchmark is a standard,
  intended capability (see Q16), used here as a measurement instrument.
