# 07. RL Method Exploration Options

> 目的：整理「除了 ablation study 之外，ICU-Sepsis 還能做哪些更像 RL method / RL experiment 的方向」。
>
> 使用方式：這份文件可以拿來和 Claude 產出的方案互相比較，最後排序下午 / 晚上要優先實作哪些 probe。
>
> 背景：目前主題 **When Mean Imputation Hides Unsupported Actions: Admissibility-Aware Q-Learning for ICU-Sepsis** 已經有清楚研究縫隙，但它偏 benchmark diagnosis / ablation。下面的方向目標是讓專題更有「主動提出 RL 解法」的味道。

---

## 0. Executive Summary

我最推薦的探索順序：

| Priority | 方向 | 為什麼 |
|---:|---|---|
| 1 | **Admissibility-aware Conservative Q-learning** | 最貼合目前主題；把 masking 從 ablation 升級成 support-aware / conservative RL method |
| 2 | **SOFA-based Potential Reward Shaping** | 很有 RL 方法感；對應 sparse reward；ICU-Sepsis 直接提供 SOFA |
| 3 | **Expert-guided Q-learning / Expert-prior Exploration** | 醫療 RL 常見；可利用 env 內建 expert policy；能和 admissibility 結合 |
| 4 | Risk-sensitive / death-avoidant tabular RL | 有 safe RL 味道，但設計較容易過度臨床化 |
| 5 | Admissibility-aware Dyna / model-based planning | 很 tabular RL，但比較適合當 robustness / appendix |

最建議下午 quick probe：

1. **Penalty / conservative λ sweep**
2. **SOFA PBRS β sweep**
3. **Expert-prior exploration**

晚上根據哪個 probe 產生最漂亮的 trade-off / learning curve，再決定是否改主軸。

---

## 1. Why We Are Looking Beyond Ablation

目前的題目已經可以成立：

> ICU-Sepsis default `mean` strategy hides unsupported-action behavior; admissibility-aware Q-learning fixes it.

但這個故事可能被挑戰：

- 「這是不是只是 action masking ablation？」
- 「RL 主動性是否不足？」
- 「你們是否只是檢查 benchmark 設定，而不是提出方法？」

所以我們想探索更多 RL-method-like 的切入：

- Conservative / pessimistic learning
- Reward shaping
- Expert-guided RL
- Risk-sensitive RL
- Model-based planning

理想狀況是把 paper 從：

> We analyze a neglected benchmark knob.

升級成：

> We identify a hidden failure mode and evaluate a family of RL remedies.

---

## 2. What Medical RL Papers Commonly Try

從 sepsis / healthcare RL 文獻看，常見努力包括：

| 類型 | 醫療 RL paper 常做什麼 | 是否適合 ICU-Sepsis |
|---|---|---|
| Conservative / Offline RL | 避免選資料中很少見的 OOD treatment，例如 CQL、BCQ、IQL | **很適合**：inadmissible action 本質就是低資料支撐 |
| Safety constraints | clinical rule、runtime filter、constraint-aware policy | **適合簡化版**：admissibility constraint |
| Reward shaping | 用 APACHE / SOFA 等 severity score 補 terminal reward 太 sparse 的問題 | **很適合**：ICU-Sepsis 有 SOFA |
| Imitation / expert prior | 從 clinician policy warm-start，再用 RL fine-tune | **很適合**：env 有 expert policy |
| Uncertainty / pessimism | 對低 support 或不確定 action 降低 value estimate | **很適合**：可做 support-aware penalty |
| Deep representation | autoencoder、attention、notes、multimodal state | 不適合：五天太大，且 ICU-Sepsis 是 tabular cluster |
| OPE methodology | WIS / FQE / HCOPE | 不適合當主軸：ICU-Sepsis 可算 exact V* |

因此，最值得做的是把 **data support / safety / sparse reward / expert prior** 這些醫療 RL 問題轉成 ICU-Sepsis 上乾淨、快速的 tabular RL 實驗。

---

## 3. Option A — Admissibility-Aware Conservative Q-learning

### A.1 Core Idea

把目前的 action masking 從「ablation」升級成「conservative / pessimistic RL method」。

核心問題：

> 在 `mean` strategy 下，inadmissible actions 被填成 admissible transitions 的平均，所以 vanilla Q-learning 沒有負訊號。能不能用 conservative / support-aware update 讓 unsupported actions 自然變得不吸引人？

### A.2 Methods to Compare

| Method | 說明 |
|---|---|
| Vanilla Q-learning | 所有 actions 都可選，原始 baseline |
| Hard mask Q-learning | behavior + target + final policy 都限制在 admissible actions |
| Penalty Q-learning | 選 inadmissible action 時 reward -= λ |
| Conservative Q-learning style | 每次 update 後壓低 inadmissible action Q-values |
| Soft support regularization | 不禁止 unsupported actions，但給 support-aware penalty |

### A.3 Simple Implementation

最簡單 probe：

```text
r'(s,a,s') = r(s,a,s') - λ * 1[a notin Adm(s)]
λ ∈ {0.01, 0.05, 0.1, 0.5, 1.0}
```

再加一個 conservative variant：

```text
Q[s, a_inadmissible] ← Q[s, a_inadmissible] - η
```

或在 final action scoring 時：

```text
score(s,a) = Q(s,a) - λ * 1[a notin Adm(s)]
```

### A.4 Expected Figure

最漂亮的圖是 trade-off curve：

```text
x-axis: unsupported-action rate
y-axis: distance-to-V*
points: vanilla, λ penalties, hard mask
```

如果點形成合理 frontier，就非常像研究結果。

### A.5 Success Criteria

| 成功訊號 | 解讀 |
|---|---|
| penalty λ 能逐步降低 unsupported-action rate | support-aware penalty 有效果 |
| 某個 λ 接近 hard mask 的安全性但保留較高 value | 有 meaningful trade-off |
| distance-to-V* 不比 hard mask 差太多 | method 有競爭力 |
| hard mask 仍最強 | 也可接受，說明 hard constraint 是乾淨解 |

### A.6 Risks

| 風險 | 處理 |
|---|---|
| penalty 一加就 performance 崩 | 改成小 λ 或只 penalty final policy score |
| hard mask 明顯最好 | paper 仍可說 penalty baseline supports hard masking choice |
| 看起來像 reward hacking | 強調這是 benchmark support penalty，不是 clinical reward |

### A.7 Fit With Current Story

非常高。

目前題目可以從：

> admissibility-aware Q-learning

升級成：

> support-aware conservative Q-learning family

推薦程度：**★★★★★**

---

## 4. Option B — SOFA-Based Potential Reward Shaping

### B.1 Core Idea

ICU-Sepsis reward 很 sparse：只有 survival terminal reward 是 +1，中間都是 0。醫療 RL paper 常用 severity score 補中間 reward，例如 APACHE、SOFA。

ICU-Sepsis 直接提供每個 state 的 SOFA score，因此可以做 potential-based reward shaping：

```text
Φ(s) = -SOFA(s)
r'(s,a,s') = r(s,a,s') + β * (γΦ(s') - Φ(s))
```

這是 Ng et al. potential-based reward shaping，理論上不改 optimal policy。

### B.2 Methods to Compare

| Method | 說明 |
|---|---|
| Vanilla Q-learning | terminal reward only |
| PBRS-SOFA | potential-based shaping |
| Naive SOFA shaping | reward += SOFA decrease，不保證 policy invariant |
| PBRS + AA-Q | shaping + admissibility-aware Q-learning |

### B.3 Simple Implementation

```text
β ∈ {0.001, 0.005, 0.01, 0.05, 0.1}
```

每次 step 後替換 reward：

```text
shaped_reward = reward + β * (gamma * (-SOFA[next_s]) - (-SOFA[s]))
```

Terminal states 的 SOFA 是 0，這裡要小心處理，避免 terminal shaping 造成奇怪大獎懲。可以先做：

```text
if next_s is terminal:
    shaped_reward = reward
```

這樣比較保守，但會失去嚴格 PBRS 形式。另一種是保留公式，並在 limitations 說明 terminal potential 設定。

### B.4 Expected Figure

```text
learning curve:
x-axis = episodes
y-axis = distance-to-V*
lines = vanilla, PBRS β values, PBRS+AA-Q
```

或：

```text
episodes-to-threshold bar chart
```

### B.5 Success Criteria

| 成功訊號 | 解讀 |
|---|---|
| PBRS early learning 比 vanilla 快 | 解決 sparse reward / sample efficiency |
| final distance-to-V* 沒變差 | shaping 沒破壞 objective |
| PBRS + AA-Q 最穩 | 可以整合成 richer method |

### B.6 Risks

| 風險 | 處理 |
|---|---|
| episode 太短，shaping 效果不明顯 | 當 appendix / negative result |
| SOFA potential 反而傷 performance | 用作 cautionary result：clinical severity shaping is nontrivial |
| 被誤解成 clinical claim | 強調 benchmark-internal shaping，不是醫療目標 |

### B.7 Fit With Current Story

中高。

它和 admissibility 主題不是完全同一件事，但可以作為：

> additional RL remedy for sparse rewards

推薦程度：**★★★★☆**

---

## 5. Option C — Expert-Guided Q-learning / Expert-Prior Exploration

### C.1 Core Idea

醫療 RL 常見設定：不要從 random policy 開始，而是從 clinician policy warm-start。ICU-Sepsis 有 `expert_policy`，可以直接用。

更有趣的是，我們已經知道 expert policy 平均約 16% probability mass 在 inadmissible actions 上，所以可以研究：

> Raw expert guidance may inherit unsupported-action behavior; projecting expert policy onto admissible actions may give a better supported warm start.

### C.2 Methods to Compare

| Method | 說明 |
|---|---|
| Vanilla Q-learning | ε-greedy random exploration |
| Expert-prior exploration | exploration step 從 expert policy sample |
| Projected expert-prior exploration | expert policy renormalized over admissible actions |
| Expert Q-init | expert argmax actions initial Q higher |
| Expert + AA-Q | expert prior + admissibility-aware target/final policy |

### C.3 Simple Implementation

Expert-prior exploration：

```text
with probability ε:
    a ~ π_expert(s)
else:
    a = argmax Q(s,a)
```

Projected version：

```text
π_proj(a|s) ∝ π_expert(a|s) if a ∈ Adm(s), else 0
```

Q-init version：

```text
Q[s,a] = c * π_expert(s,a)
```

或：

```text
Q[s,argmax expert] = c
```

### C.4 Expected Figure

```text
learning curve:
vanilla vs expert-prior vs projected-expert-prior vs AA-Q
```

以及：

```text
bar chart:
unsupported-action rate / expert agreement / distance-to-V*
```

### C.5 Success Criteria

| 成功訊號 | 解讀 |
|---|---|
| expert prior 提升 early learning | clinician policy 有 sample-efficiency value |
| raw expert prior 有 unsupported actions | expert 不等於 admissible |
| projected expert prior 更穩 | 我們的 admissibility 主題得到延伸 |

### C.6 Risks

| 風險 | 處理 |
|---|---|
| Expert 和 Random return 幾乎一樣，效果可能小 | 看 early distance-to-V* / expert agreement，不只看 return |
| expert prior 把 policy 拉向次優 | 這本身是 finding |
| 看起來像 imitation learning 另一題 | 只放作 supporting experiment |

### C.7 Fit With Current Story

中高。

特別適合作為 Discussion：admissibility 不是簡單「follow expert」，因為 expert policy 自己也不完全 admissible。

推薦程度：**★★★★☆**

---

## 6. Option D — Risk-Sensitive / Death-Avoidant Tabular RL

### D.1 Core Idea

Safe RL 常不只 maximize expected return，也會控制 bad outcome risk。ICU-Sepsis 有 death state，因此可做簡化 risk-sensitive Q-learning。

### D.2 Possible Methods

| Method | 說明 |
|---|---|
| Death-penalty Q-learning | death transition 額外 penalty |
| CVaR-like evaluation | 看 low-tail performance |
| Death-risk constrained policy | avoid actions with high P(death | s,a) |
| Lagrangian supported-risk Q | reward - λ death_risk - η unsupported |

### D.3 Simple Implementation

利用 known dynamics 計算：

```text
death_risk(s,a) = P(s' = death | s,a)
```

學習時加 penalty：

```text
r' = r - λ * death_risk(s,a)
```

或 action selection 時：

```text
score(s,a) = Q(s,a) - λ * death_risk(s,a)
```

### D.4 Expected Figure

```text
x-axis: death-risk proxy
y-axis: distance-to-V*
points: λ sweep
```

### D.5 Risks

這個方向比較容易被問：

- 你是不是改了 clinical objective？
- death-risk penalty 的 λ 怎麼選？
- 用 model-known death probability 是否不公平？

因此我不建議當主軸。

推薦程度：**★★★☆☆**

---

## 7. Option E — Admissibility-Aware Dyna / Model-Based Planning

### E.1 Core Idea

ICU-Sepsis 是 tabular MDP，Dyna-Q / model-based planning 很自然。可以研究 planning updates 是否會浪費在 unsupported state-action pairs。

### E.2 Methods

| Method | 說明 |
|---|---|
| Q-learning | model-free baseline |
| Dyna-Q | learned model + planning |
| AA-Dyna-Q | planning only over admissible pairs |
| Oracle model planning | use true dynamics as upper bound |

### E.3 Research Question

> Does admissibility-aware planning improve sample efficiency by avoiding simulated updates over unsupported actions?

### E.4 Fit

這很 RL，但可能被視為「多跑一個 algorithm」。比較適合作為 robustness：

> our findings are not Q-learning-specific.

推薦程度：**★★★☆☆**

---

## 8. Recommended Afternoon Probe Plan

### Phase 1 — quick implementation / run

| Probe | Runs | Time | Decision signal |
|---|---|---:|---|
| A. Penalty / conservative | Q-learning, λ ∈ {0.01,0.05,0.1,0.5,1.0}, 1-3 seeds | 1-2 hr | trade-off curve exists? |
| B. SOFA PBRS | β ∈ {0.001,0.005,0.01,0.05}, 1-3 seeds | 1 hr | early learning improves? |
| C. Expert prior | raw vs projected expert exploration, 1-3 seeds | 1 hr | sample efficiency improves? |

### Phase 2 — choose one to expand

| Probe result | Expand into |
|---|---|
| Penalty / conservative works | Main method: support-aware conservative Q-learning |
| SOFA PBRS works | Secondary method: severity-shaped AA-Q |
| Expert prior works | Secondary method: admissible expert-guided Q-learning |
| None are strong | Keep current mean-imputation hidden-failure story; use negative probes as appendix / discussion |

### Phase 3 — 5-seed confirmation

只對最有希望的 1-2 個方向跑 full 5 seeds。不要三個都完整跑，除非時間很充裕。

---

## 9. How to Integrate With Current Paper

### If Option A works

New title:

> **Learning Supported Policies in ICU-Sepsis: Conservative and Admissibility-Aware Q-Learning under Mean-Imputed Transitions**

Story:

1. `mean` hides unsupported actions.
2. Hard mask fixes it.
3. Penalty / conservative variants reveal a value-support trade-off.
4. We recommend explicitly reporting this trade-off in ICU-Sepsis.

### If Option B works

Title:

> **Admissibility- and Severity-Aware Q-Learning for ICU-Sepsis**

Story:

1. `mean` hides unsupported actions.
2. terminal survival reward is sparse.
3. AA-Q handles unsupported actions; PBRS-SOFA improves sample efficiency.
4. Together they form a lightweight tabular RL improvement.

### If Option C works

Title:

> **Admissible Expert-Guided Q-Learning for ICU-Sepsis**

Story:

1. expert priors are useful but not perfectly admissible.
2. raw expert guidance may inherit unsupported-action behavior.
3. projecting expert prior onto admissible set improves supported learning.

### If no option works

Keep title:

> **When Mean Imputation Hides Unsupported Actions: Admissibility-Aware Q-Learning for ICU-Sepsis**

Story remains strong:

1. identify hidden failure mode
2. full AA-Q fixes it
3. broader probes show why this benchmark is tricky

---

## 10. Ranking Criteria for Comparing With Claude's Proposals

用這些標準給每個方案打分：

| Criterion | 問題 |
|---|---|
| Feasibility | 下午能不能先跑出 probe？ |
| Method feel | 是否像主動提出 RL 方法，而非只做分析？ |
| Fit with current results | 是否能接上已完成的 mask result？ |
| Figure quality | 是否能產生清楚 learning curve / trade-off plot？ |
| Novelty | 是否避開 ICU-Sepsis 原 paper 已做過的 baseline？ |
| Reviewer defensibility | 是否容易被質疑 medical overclaim / trivial？ |
| MVP fallback | 如果效果不強，是否仍能當 supporting result？ |

建議權重：

```text
Feasibility: 25%
Method feel: 20%
Fit with current story: 20%
Figure quality: 15%
Reviewer defensibility: 10%
Novelty: 10%
```

---

## 11. My Current Ranking

| Rank | Option | Score / 10 | Reason |
|---:|---|---:|---|
| 1 | Admissibility-aware Conservative Q-learning | 9.0 | 最貼目前主題，最容易變成 method story |
| 2 | SOFA-based Potential Reward Shaping | 8.0 | RL 味很強，但效果不一定明顯 |
| 3 | Expert-guided Q-learning | 7.8 | 醫療 RL 味強，和 expert inadmissibility finding 很搭 |
| 4 | Admissibility-aware Dyna / planning | 6.8 | tabular RL 很合理，但比較像 robustness |
| 5 | Risk-sensitive / death-avoidant Q | 6.3 | safe RL 感強，但 medical objective 風險較高 |

---

## 12. References / Anchors

Relevant anchors from current notes and search:

- ICU-Sepsis original benchmark: Choudhary et al., RLC/RLJ 2024.
- Healthcare RL caution / OPE limitations: Gottesman et al., Nature Medicine 2019.
- Sepsis treatment origin: Komorowski et al., Nature Medicine 2018.
- Continuous-state DDQN for sepsis: Raghu et al., MLHC 2017.
- Invalid action masking: Huang & Ontañón, FLAIRS 2022.
- Forbidden actions in Q-learning: Seurin, Preux, Pietquin, IJCNN 2020.
- Potential-based reward shaping: Ng, Harada, Russell, ICML 1999.
- Offline safe RL for sepsis with sparse rewards: Tu et al., Human-Centric Intelligent Systems 2025.
- CPQ-IQL / runtime safety filtering for sepsis: Zhang & Mi, Transactions on Artificial Intelligence 2026.

