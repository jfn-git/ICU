# 06. Project Plan — When Mean Imputation Hides Unsupported Actions

> Working title: **When Mean Imputation Hides Unsupported Actions: Admissibility-Aware Q-Learning for ICU-Sepsis**
>
> 本計畫把原本「ICU-Sepsis action admissibility / masking ablation」重新包裝成更有問題意識的研究：
>
> **核心問題**：ICU-Sepsis 預設的 `mean` strategy 會把 inadmissible action 的 transition 填成 admissible actions 的平均，因此 vanilla RL agent 可以大量選擇「資料不支撐」的 action，卻不會受到明確懲罰。這會讓 benchmark performance 看起來正常，但 learned policy 其實依賴 unsupported actions。
>
> **核心解法**：提出並評估 **admissibility-aware TD learning**：把 admissible-action constraint 放進 exploration、Bellman backup、final policy extraction 與 evaluation protocol 中。

---

## 1. One-Sentence Pitch

ICU-Sepsis 的 default `mean` imputation strategy hides unsupported-action behavior: vanilla Q-learning selects inadmissible actions at very high rates while receiving no penalty signal, and a simple admissibility-aware TD variant fixes this failure mode by constraining action selection and Bellman backups to statistically supported actions.

中文：

> ICU-Sepsis 預設的 `mean` 補值方式會把「選到資料不支撐 action」這件事藏起來；我們指出這個 benchmark failure mode，並用 admissibility-aware Q-learning 修正它。

---

## 2. Why This Is Better Than a Plain Ablation Study

原本題目是：

> 比較 action masking / strategy / metrics。

這是可行的，但 reviewer 可能覺得像是 implementation detail ablation。

新的題目是：

> Benchmark default hides a failure mode; we identify it, explain why it happens, and propose a constrained TD-learning fix.

這樣會有更清楚的 problem-solution structure：

| Paper component | 原本 ablation framing | 新 framing |
|---|---|---|
| Problem | 不同 strategy / mask 會影響結果 | `mean` strategy hides unsupported-action behavior |
| Failure mode | mask-off unsafe rate 高 | vanilla Q-learning learns unsupported policies without penalty |
| Method | mask on/off ablation | admissibility-aware TD learning |
| Evidence | 多 metric 對照 | failure diagnosis + fix + robustness ablations |
| Takeaway | benchmark users should report knobs | benchmark default can be misleading unless admissibility is modeled |

這樣比較像 NeurIPS-style paper：有 clear finding、有 method、有 evaluation protocol、有 broader benchmark lesson。

---

## 3. Research Questions

| RQ | 問題 | 對應實驗 |
|---|---|---|
| RQ1 | Does ICU-Sepsis's default `mean` strategy hide unsupported-action behavior? | Vanilla Q-learning under `mean`, measure inadmissible-action rate, return, distance-to-V* |
| RQ2 | Which part of admissibility-aware learning matters: behavior masking, target masking, or final policy masking? | Component ablation: behavior-only / target-only / full |
| RQ3 | Does admissibility awareness improve policy value, sample efficiency, and robustness across algorithms? | Q-learning main; SARSA / Dyna-Q as robustness |
| RQ4 | Are survival-rate improvements sufficient to reveal this issue? | Compare return vs distance-to-V* / unsafe-action rate / expert agreement |
| RQ5 | Does the issue become worse in clinically severe states? | SOFA-bucket unsafe-action analysis |

---

## 4. Main Claim

Recommended main claim:

> Under ICU-Sepsis's default `mean` strategy, vanilla Q-learning learns policies that select statistically unsupported actions at high rates because inadmissible actions receive average admissible transitions rather than a negative signal. Admissibility-aware TD learning removes this hidden failure mode and improves distance-to-V* without requiring a new environment or clinical assumptions.

保守版 claim：

> We identify and quantify a hidden unsupported-action failure mode in ICU-Sepsis and show that a simple admissibility-aware Q-learning variant substantially reduces unsupported-action use while improving benchmark-internal value metrics.

不要寫：

> Our policy is clinically safer.

應該寫：

> Our policy is better supported under the benchmark's data-coverage-defined admissibility criterion.

---

## 5. Proposed Method: Admissibility-Aware Q-Learning

### 5.1 Baseline: vanilla Q-learning

Vanilla Q-learning 在 state `s` 會從所有 25 個 actions 中 epsilon-greedy 選擇：

```text
a_t ~ eps-greedy(Q(s_t, ·), A_all)
Q(s_t,a_t) ← Q(s_t,a_t) + α [r + γ max_a Q(s_{t+1},a) - Q(s_t,a_t)]
π(s) = argmax_a Q(s,a)
```

問題：在 `mean` strategy 下，inadmissible action 不會被處罰，只會得到該 state 下 admissible transitions 的平均，因此 Q-learning 沒有明確訊號知道「這個 action 資料不支撐」。

### 5.2 Full admissibility-aware Q-learning

Full variant 在三個地方都使用 admissible action set `Adm(s)`：

```text
a_t ~ eps-greedy(Q(s_t, ·), Adm(s_t))
Q(s_t,a_t) ← Q(s_t,a_t) + α [r + γ max_{a ∈ Adm(s_{t+1})} Q(s_{t+1},a) - Q(s_t,a_t)]
π(s) = argmax_{a ∈ Adm(s)} Q(s,a)
```

這不是換 reward，也不是 clinical rule injection；它只是要求 agent 在 benchmark 自己定義的 statistically supported action set 裡學習與評估。

### 5.3 Component variants

為了讓 method 看起來不是「單純 mask 一下」，建議拆成 component ablation：

| Variant | Behavior selection | Bellman target | Final policy |
|---|---|---|---|
| Vanilla | all actions | all actions | all actions |
| Behavior-mask only | admissible only | all actions | all actions or admissible |
| Target-mask only | all actions | admissible only | all actions |
| Policy-mask only | all actions | all actions | admissible only |
| Full AA-Q | admissible only | admissible only | admissible only |

最重要的是 Full AA-Q；其他變體幫忙回答「到底是哪一段在工作」。

---

## 6. Experiment Menu

因為 ICU-Sepsis 很快，可以把實驗分成三層：MVP、Strong、NeurIPS-style Stretch。

### 6.1 MVP: 保底可交故事線

這是最少也要完成的版本。

| ID | 實驗 | 條件 | Seeds | Output |
|---|---|---|---|---|
| B0 | Baseline reproduction | Random / Expert / Optimal | 5 or original helper | Tbl 1 |
| E1 | Hidden failure mode | Vanilla Q-learning, `mean`, no mask | 5 | unsafe rate, return, distance-to-V* |
| E2 | Fix | Full AA-Q, `mean` | 5 | same metrics |
| E3 | Metric diagnosis | Return vs distance-to-V* vs unsafe rate | from E1/E2 | Fig 1 + Tbl 2 |

MVP story:

1. ICU-Sepsis default `mean` allows all actions by replacing unsupported actions with average supported transitions.
2. Vanilla Q-learning under this default selects unsupported actions roughly 85% of the time.
3. Full admissibility-aware Q-learning reduces unsupported-action rate to 0 and improves distance-to-V*.
4. Survival rate alone understates the issue; multi-metric evaluation is necessary.

目前已經完成的結果已經覆蓋 MVP 的核心 E1/E2：

| Metric | Vanilla / mask off | Full mask on |
|---|---:|---:|
| J(π) | 0.7855 | 0.8058 |
| Distance-to-V* | 0.0896 | 0.0693 |
| Training inadmissible rate | 0.854 | 0.000 |
| Expert agreement | 0.041 | 0.528 |

### 6.2 Strong version: 讓內容豐富、有系統性

這是建議目標。

| ID | 實驗 | 條件 | 為什麼重要 |
|---|---|---|---|
| E4 | Component ablation | behavior-only / target-only / policy-only / full | 證明不是 trivial masking |
| E5 | Strategy comparison | `mean` vs `terminate` vs `raise_exception` sanity | 說明 failure mode 來自 `mean` |
| E6 | Algorithm robustness | Q-learning / SARSA / Dyna-Q | 避免只是一個 algorithm artifact |
| E7 | Sample efficiency | 5k / 10k / 25k / 50k episodes | 支撐 "faster learning" |
| E8 | Deployment diagnostic | train with mask, evaluate greedy with and without mask | 判斷 Q-table 是否真的 internalize admissibility |
| E9 | SOFA-bucket unsafe rate | SOFA quintiles | 讓 safety proxy 更有內容 |

Strong story:

1. Diagnosis: `mean` hides unsupported actions.
2. Mechanism: inadmissible action values become average-like under `mean`.
3. Fix: admissibility-aware Q-learning.
4. Component ablation: behavior masking and target masking serve different roles.
5. Robustness: effect persists across tabular TD algorithms and budgets.
6. Severity analysis: unsupported-action behavior can be reported by SOFA bucket.

### 6.3 NeurIPS-style stretch: 讓 paper 更像 benchmark/method submission

NeurIPS-style 並不是一定要「很大模型」，而是要有：

- clear problem with broader relevance
- method or protocol that others can reuse
- rigorous ablations
- robust evaluation
- careful limitations

在我們環境下可以加這些：

| Stretch | 內容 | 成本 | 價值 |
|---|---|---:|---|
| S1 | DQN with admissibility-aware masking | 中高 | 防守 "not deep RL" |
| S2 | Penalty baseline | inadmissible action penalty λ ∈ {-0.01, -0.05, -0.1, -1} | 低 | 和 masking 比較，呼應 invalid-action literature |
| S3 | Soft admissibility prior | add log support / admissible bonus to Q target | 中 | 比 hard mask 更像 method |
| S4 | Action-support threshold sensitivity | 模擬不同 admissible set strictness | 中 | 變成 benchmark analysis |
| S5 | Expert-policy inconsistency analysis | expert mass on inadmissibles by SOFA bucket | 低 | 很有 discussion value |
| S6 | Calibration of learned Q-values | compare Q(s,a) for admissible vs inadmissible under mean | 中 | 解釋 why failure happens |
| S7 | Full reproducibility package | one-command scripts + table/figure generation | 中 | NeurIPS benchmark style 加分 |

最推薦的 stretch 是 S2、S5、S6：便宜而且和主 claim 高度相關。

---

## 7. Metrics

主 metric 不應只放 return，因為 ICU-Sepsis 的 return range 本來就窄。

| Metric | 定義 | 角色 |
|---|---|---|
| Return / J(π) | d0-weighted Vπ or rollout survival rate | 與原 paper 對齊 |
| Distance-to-V* | E_{s~d0}[V*(s)-Vπ(s)] | 主 performance metric |
| Training unsupported-action rate | training 中 action ∉ Adm(s) 的比例 | failure-mode diagnostic |
| Deployment unsupported-action rate | final policy 在 evaluation 中 action ∉ Adm(s) 的比例 | policy diagnostic |
| Supported policy ratio | fraction of states where π(s) ∈ Adm(s) | final-policy support |
| Expert agreement | argmax π vs argmax expert | behavioral reference |
| SOFA-bucket unsupported rate | unsafe rate split by severity bucket | richer analysis |
| Episodes-to-threshold | episodes to reach J ≥ 0.80 / dist-V* ≤ threshold | sample efficiency |
| Q-value leakage | max inadmissible Q minus max admissible Q | explains mean-imputation failure |

建議主文只放 4-5 個，其他放 appendix：

主文：

1. J(π)
2. Distance-to-V*
3. Training unsupported-action rate
4. Deployment unsupported-action rate or supported policy ratio
5. Expert agreement

Appendix：

- SOFA bucket
- Q-value leakage
- per-seed scatter
- hyperparameter sensitivity

---

## 8. Figures and Tables

### Main paper figures

| Figure | 內容 | 用途 |
|---|---|---|
| Fig 1 | Hidden failure mode diagram: mean imputation makes inadmissible action transition equal average supported transition | 讓 reviewer 立刻懂問題 |
| Fig 2 | Learning curves: Vanilla vs Full AA-Q, y = distance-to-V* and/or J(π) | 主結果 |
| Fig 3 | Unsupported-action rate over training: Vanilla vs variants | failure + fix |
| Fig 4 | Component ablation bar chart | 展示 method 細節 |
| Fig 5 optional | SOFA-bucket unsupported action rate | 內容豐富度 |

### Tables

| Table | 內容 |
|---|---|
| Tbl 1 | Baseline reproduction: Random / Expert / Optimal vs ICU-Sepsis paper |
| Tbl 2 | Main method comparison: Vanilla / component variants / Full AA-Q |
| Tbl 3 | Strategy comparison: mean / terminate / raise_exception sanity |
| Tbl 4 appendix | Algorithm robustness: Q-learning / SARSA / Dyna-Q |

---

## 9. Paper Outline

目標是 6-7 頁 main content，符合 4-8 頁限制。

| Section | 頁數 | 內容 |
|---|---:|---|
| Abstract | 0.25 | Problem, method, findings, non-clinical disclaimer |
| 1. Introduction | 1.0 | Medical RL benchmark motivation → ICU-Sepsis → hidden unsupported-action failure mode → contributions |
| 2. Related Work | 0.75 | ICU-Sepsis, sepsis RL, invalid action masking, healthcare RL evaluation |
| 3. Background: ICU-Sepsis and Mean Imputation | 1.0 | state/action, admissibility, `mean` strategy, why it hides unsupported actions |
| 4. Method: Admissibility-Aware TD Learning | 1.0 | vanilla Q-learning, AA-Q, component variants, metrics |
| 5. Experiments | 2.0 | setup, baseline reproduction, failure diagnosis, fix, ablations, robustness |
| 6. Discussion | 0.6 | what this means for benchmark users, why survival rate is insufficient |
| 7. Limitations | 0.4 | tabular, not clinical, 5 seeds, admissibility is data support not medical correctness |
| 8. Conclusion | 0.2 | concise takeaway |

---

## 10. Contribution Bullets

Recommended:

1. **Failure-mode diagnosis.** We show that ICU-Sepsis's default `mean` strategy hides statistically unsupported action choices: vanilla Q-learning can select inadmissible actions at high rates while receiving average admissible transitions.
2. **Admissibility-aware TD learning.** We introduce a simple constrained Q-learning variant that applies admissible-action sets during behavior selection, Bellman backups, and final policy extraction.
3. **Multi-metric evaluation.** We demonstrate that survival rate alone misses this failure mode, and report distance-to-V*, unsupported-action rate, supported-policy ratio, and expert agreement.
4. **Benchmark guidance.** We provide scripts and ablations showing that ICU-Sepsis results should explicitly report inadmissible-action handling and admissibility constraints.

如果有補完 SARSA / Dyna-Q：

5. **Robustness across TD algorithms.** We show the same admissibility issue appears across Q-learning, SARSA, and Dyna-Q.

---

## 11. Claims We Can and Cannot Make

### Safe claims

- "unsupported action" means insufficient data support under ICU-Sepsis's threshold, not medically impossible.
- `mean` imputation can hide unsupported-action behavior from RL updates.
- admissibility-aware Q-learning improves benchmark-internal metrics under the ICU-Sepsis MDP.
- distance-to-V* reveals differences that survival rate alone can miss.

### Risky claims to avoid

- "our policy is clinically safer"
- "our policy improves patient survival"
- "inadmissible action means medically wrong action"
- "this should be deployed"
- "we solve sepsis treatment"

Preferred wording:

| Avoid | Use instead |
|---|---|
| unsafe clinical action | statistically unsupported action |
| safe policy | admissibility-respecting policy |
| improves survival | improves benchmark-internal return / policy value |
| clinical recommendation | benchmark-level algorithmic finding |

---

## 12. Experimental Priority Plan

### If only 12 hours remain

Do:

1. Freeze MVP claim.
2. Polish existing Q-learning mask off/on result.
3. Create Fig 1/2/3 and Tbl 1/2.
4. Write paper with honest limitation: "we focus on Q-learning under the default mean strategy."

### If 24 hours remain

Add:

1. Component ablation.
2. `terminate` strategy Q-learning comparison.
3. SOFA-bucket unsupported rate.

### If 48+ hours remain

Add:

1. SARSA and Dyna-Q robustness.
2. Sample-efficiency budgets.
3. Penalty baseline.
4. DQN if compute/time allows.

---

## 13. Concrete Experiment Matrix

### Core matrix

| Algo | Strategy | Variant | Episodes | Seeds |
|---|---|---|---:|---:|
| Q-learning | mean | Vanilla | 50k | 5 |
| Q-learning | mean | Behavior-mask only | 50k | 5 |
| Q-learning | mean | Target-mask only | 50k | 5 |
| Q-learning | mean | Policy-mask only | 50k | 5 |
| Q-learning | mean | Full AA-Q | 50k | 5 |
| Q-learning | terminate | Vanilla | 50k | 5 |
| Q-learning | terminate | Full AA-Q | 50k | 5 |

### Robustness matrix

| Algo | Strategy | Variant | Episodes | Seeds |
|---|---|---|---:|---:|
| SARSA | mean | Vanilla / Full AA | 50k | 5 |
| Dyna-Q | mean | Vanilla / Full AA | 50k | 5 |
| SARSA | terminate | Vanilla / Full AA | 50k | 5 |
| Dyna-Q | terminate | Vanilla / Full AA | 50k | 5 |

### Sample efficiency

For selected cells:

```text
episodes = [1k, 2.5k, 5k, 10k, 25k, 50k]
```

Log:

- J(π)
- distance-to-V*
- training unsupported rate
- supported-policy ratio

---

## 14. Method Details Needed in Code

目前 `use_mask=True/False` 可能已經同時影響 behavior selection 與 bootstrap target。為了 component ablation，需要把 mask 拆成 flags：

```python
train_q_learning(
    env,
    mask_behavior: bool,
    mask_target: bool,
    mask_policy_eval: bool,
    ...
)
```

或至少在 script 層做：

| Flag | 用途 |
|---|---|
| `mask_behavior` | epsilon-greedy random / greedy 是否只從 admissible actions 選 |
| `mask_target` | TD target 的 max 是否只看 next state's admissible actions |
| `mask_final_policy` | Q-table 轉 greedy policy 時是否只在 admissible actions 中 argmax |

新增 diagnostic：

```text
q_leakage(s) = max_{a notin Adm(s)} Q(s,a) - max_{a in Adm(s)} Q(s,a)
```

如果 q_leakage 很高，代表 inadmissible actions 在 Q-table 中真的被高估，不只是 behavior selection 的問題。

---

## 15. What NeurIPS-Style Presentation Would Need

雖然這是課程 mini-conf，不是真的 NeurIPS，但如果以 NeurIPS-style 標準看，需要補強：

### 15.1 More than a trick

不要呈現成「我加了 action mask」。要呈現成：

> We diagnose a benchmark-level failure mode caused by the interaction between mean imputation and unconstrained TD learning.

### 15.2 Mechanistic evidence

要有 evidence 解釋為什麼發生：

- mean-imputed inadmissible transitions exactly equal average admissible transitions
- vanilla Q-values for inadmissible actions become competitive or higher
- epsilon-greedy exploration repeatedly selects unsupported actions
- no negative reward signal exists to correct this

### 15.3 Ablations

至少 component ablation：

- behavior masking
- target masking
- final policy masking
- full AA-Q

這會讓 method 看起來更像研究，不只是 wrapper。

### 15.4 Robustness

至少一個：

- SARSA / Dyna-Q
- `terminate` strategy
- penalty baseline
- episode-budget sweep

### 15.5 Strong limitations

NeurIPS-style reviewer 會喜歡誠實的 limitations：

- tabular benchmark only
- data-support admissibility is not medical validity
- no external clinical validation
- 5 seeds due to course budget
- expert policy itself assigns nonzero mass to inadmissible actions

### 15.6 Reproducibility

要有：

- config files
- seeds
- result JSON
- plotting scripts
- exact package version
- command to reproduce figures

---

## 16. Draft Abstract

> Medical reinforcement-learning benchmarks often replace missing or poorly supported transitions with default modeling choices. In ICU-Sepsis, actions with insufficient state-action support are handled by a default `mean` strategy that assigns each inadmissible action the average transition dynamics of admissible actions in the same state. We show that this design can hide unsupported-action behavior: vanilla Q-learning under the default setting selects inadmissible actions at high rates while receiving no explicit penalty signal. We propose admissibility-aware Q-learning, a simple TD-learning variant that restricts behavior selection, Bellman backups, and final policy extraction to the benchmark's statistically supported action set. On ICU-Sepsis, this reduces unsupported-action use from approximately 85% to 0% and improves distance-to-V* under the default benchmark setting. Our results are benchmark-internal and should not be interpreted as clinical recommendations; rather, they show that admissibility handling should be explicitly reported when using ICU-Sepsis.

---

## 17. Draft Introduction Logic

1. Medical RL needs reproducible benchmarks, but real clinical data pipelines are hard to reproduce.
2. ICU-Sepsis solves this by giving a lightweight tabular MDP built from MIMIC-III.
3. However, because many state-action pairs have insufficient data support, the benchmark must decide how to handle inadmissible actions.
4. The default `mean` strategy makes the environment usable with all actions, but it also hides when an RL agent selects unsupported actions.
5. We show this is not cosmetic: vanilla Q-learning selects inadmissible actions at high rates, and survival rate alone does not reveal the issue.
6. We propose admissibility-aware TD learning and a multi-metric evaluation protocol.

---

## 18. Recommended Next Actions

1. Rename the project framing in README / paper outline to this new title.
2. Add component-ablation flags in `src/tabular_rl.py`.
3. Run Q-learning component matrix under `mean`.
4. Run Q-learning `terminate` comparison.
5. Generate Fig 2/3 and Tbl 2.
6. Write Method + Experiments around this new story.
7. Add SARSA / Dyna-Q only after MVP figures exist.

