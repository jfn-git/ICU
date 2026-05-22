# 08. Merged Implementation Ranking — Claude × Codex

> 來源：
> - Claude: `core_docs/07_rl_active_directions_claude.md`
> - Codex: `core_docs/07_rl_method_exploration_options.md`
>
> 目的：把兩份「更 RL-active 的方向」合併，排序下午/晚上最值得 prototype 的實作順序。

---

## 0. Executive Decision

我建議最終採用這個策略：

> **主線仍保留「mean imputation hides unsupported actions」這個 failure-mode framing，但把解法升級成 offline-RL / OOD-action handling spectrum。**

也就是：

1. ICU-Sepsis 的 inadmissible action 可以重新詮釋成 offline RL 裡的 **OOD / low-support action**。
2. `mean` strategy 的問題是它把 OOD action 用 average supported transition 補起來，讓 vanilla Q-learning 沒有 pessimism。
3. 我們比較一系列 RL remedy：vanilla、penalty、conservative/pessimistic、behavior constraint、hard mask。
4. 再用 factored action 或 exact dead-end analysis 做加分章節。

這會比純 ablation 更像 RL project：

> We identify a hidden benchmark failure mode and evaluate a family of RL remedies for OOD / unsupported actions under exact value evaluation.

---

## 1. Final Ranking

| Rank | Direction | Source | Score | Verdict |
|---:|---|---|---:|---|
| 1 | **OOD-action / Conservative Q-learning spectrum** | Claude + Codex overlap | 9.5 | 最值得做，應成為主線升級 |
| 2 | **Factored action-space Q-learning** | Claude | 8.4 | 快速、RL 味強，適合下午先試 |
| 3 | **SOFA-based potential reward shaping** | Codex | 8.0 | RL 方法感強，若有效可成第二貢獻 |
| 4 | **Expert-guided / projected expert prior Q-learning** | Codex | 7.8 | 和醫療 RL 很搭，適合 supporting experiment |
| 5 | **Exact dead-end analysis / dead-end-aware learning** | Claude | 7.6 | 很獨特，但 framing 要小心 |
| 6 | **Admissibility-aware Dyna / planning** | Codex | 6.8 | 好做，但像 robustness 而非主線 |
| 7 | **Risk-sensitive / death-avoidant Q-learning** | Codex | 6.2 | safe RL 味強，但 medical objective 風險高 |

---

## 2. Why Rank #1 Is the Best Main Upgrade

Claude 最重要的洞察是：

> inadmissible action ≈ offline RL 的 OOD-action / distribution shift 問題。

這點非常有用，因為它把我們的題目從：

> action masking ablation

升級成：

> controlled testbed for OOD-action remedies in medical RL.

而 ICU-Sepsis 的特殊優勢是：

- 它是 tabular MDP。
- dynamics 完全可見。
- 可以算 exact V* / exact Vπ。
- 因此可以精確比較方法，而不用依賴 noisy OPE。

這讓我們有一個更像 paper 的主張：

> ICU-Sepsis provides a rare setting where OOD-action handling methods from offline RL can be evaluated exactly. We show that the default mean-imputation strategy hides unsupported-action behavior, and compare hard masking, penalties, and conservative pessimism as remedies.

---

## 3. Recommended Afternoon Prototype Order

雖然 rank #1 是主線，但下午實作順序不一定等於最終重要性。要先跑「最快驗證是否有圖」的。

### Step 1 — Factored Q-learning quick probe

Claude 建議先做 factored，這點我同意，因為它可能最便宜：

```text
Q(s, fluid, vaso) ≈ Q_f(s, fluid) + Q_v(s, vaso)
```

或更簡單：

```text
score(s, a) = Q_fluid[s, fluid(a)] + Q_vaso[s, vaso(a)]
```

比較：

- flat Q-learning
- factored Q-learning
- factored + admissibility mask

成功訊號：

- early learning 更快
- fewer parameters / better sample efficiency
- 和 action factorization literature 能接上

風險：

- ICU-Sepsis 的 action interaction 可能很重要，簡單 additive factorization 表現可能差。

建議：**先 1-2 seeds、10k/25k episodes 試水溫。**

### Step 2 — OOD / conservative λ sweep

這是最重要的主線 prototype。

先做最簡單版本：

```text
r'(s,a,s') = r(s,a,s') - λ * 1[a notin Adm(s)]
λ ∈ {0.01, 0.05, 0.1, 0.5, 1.0}
```

比較：

- vanilla
- penalty λ sweep
- hard mask

畫：

```text
x-axis = unsupported-action rate
y-axis = distance-to-V*
```

成功訊號：

- λ 增大時 unsupported-action rate 下降。
- distance-to-V* 不要完全崩。
- hard mask 或某個 penalty 點形成 trade-off frontier。

建議：**這個一定要做。**

### Step 3 — SOFA PBRS quick probe

如果前兩個跑完還有時間，做 SOFA reward shaping：

```text
Φ(s) = -SOFA(s)
r' = r + β(γΦ(s') - Φ(s))
β ∈ {0.001, 0.005, 0.01, 0.05}
```

成功訊號：

- early distance-to-V* 改善。
- final value 不變差。

若有效，它可以變成第二貢獻：

> AA-Q handles unsupported actions; SOFA PBRS addresses sparse reward.

### Step 4 — Expert prior / exact dead-end 二選一

若時間剩不多，我建議二選一：

| 選項 | 何時選 |
|---|---|
| Expert prior | 想要更醫療 RL、clinician-guided flavor |
| Exact dead-end | 想要更獨特、analysis-heavy flavor |

我的傾向：如果主線已經是 OOD/conservative，**expert prior 比 dead-end 更容易接上**；dead-end 雖然很酷，但可能變成另一篇 paper。

---

## 4. Consolidated Experiment Matrix

### Must Run

| ID | Experiment | Cells | Seeds | Why |
|---|---|---|---:|---|
| M0 | Existing baseline | vanilla vs hard mask | 5 | 已有結果，保底 |
| M1 | Penalty sweep | λ = 0.01, 0.05, 0.1, 0.5, 1.0 | 1-3 first, then 5 | 主線升級 |
| M2 | Factored quick probe | flat vs factored vs factored+mask | 1-3 | 快速驗證 RL method feel |

### Should Run

| ID | Experiment | Cells | Seeds | Why |
|---|---|---|---:|---|
| S1 | Component mask ablation | behavior / target / final / full | 3-5 | 防止 hard mask 被說 trivial |
| S2 | `terminate` comparison | vanilla / AA-Q under terminate | 3-5 | 證明 failure mode tied to mean |
| S3 | SOFA PBRS | β sweep | 1-3 | Sparse reward method probe |

### Nice to Have

| ID | Experiment | Cells | Seeds | Why |
|---|---|---|---:|---|
| N1 | Expert prior | raw / projected / projected+AA | 1-3 | 醫療 RL flavor |
| N2 | Exact dead-end analysis | V* threshold + policy visitation | analysis only first | 獨特 analysis |
| N3 | SARSA / Dyna robustness | vanilla / AA-Q | 3-5 | Robustness |

---

## 5. How to Decide Tonight

跑完 quick probes 後，用以下決策樹：

### Case A — Penalty / conservative works

Final title:

> **Learning Supported Policies in ICU-Sepsis: Conservative and Admissibility-Aware Q-Learning under Mean-Imputed Transitions**

Main story:

1. `mean` hides unsupported actions.
2. This is an OOD-action problem.
3. We compare vanilla, penalty, conservative, hard mask.
4. Hard mask / conservative remedy improves support-value trade-off.

### Case B — Factored Q works strongly

Possible title:

> **Factored and Admissibility-Aware Q-Learning for ICU-Sepsis**

Main story:

1. ICU-Sepsis action space is naturally factorized: fluid × vasopressor.
2. Flat Q-learning ignores this structure.
3. Factored Q improves sample efficiency.
4. Admissibility constraints prevent unsupported treatment combinations.

Note: this is more method-like, but less directly connected to current mask result.

### Case C — SOFA PBRS works strongly

Possible title:

> **Admissibility- and Severity-Aware Q-Learning for ICU-Sepsis**

Main story:

1. ICU-Sepsis has two issues: unsupported actions and sparse terminal reward.
2. AA-Q solves unsupported actions.
3. SOFA PBRS improves sample efficiency.
4. Combined method gives best early learning.

### Case D — None work beyond mask

Keep current title:

> **When Mean Imputation Hides Unsupported Actions: Admissibility-Aware Q-Learning for ICU-Sepsis**

Use all probes as:

- negative / robustness experiments
- limitations
- appendix

This is still acceptable.

---

## 6. My Disagreement With Claude

Claude ranks factored Q first for prototype because it is fastest. I agree for **probe order**, but not for **paper mainline**.

Reason:

- Factored Q is RL-active and clean, but it may become a separate story from mean imputation / unsupported actions.
- OOD / conservative learning directly absorbs our existing results and related work.
- We already have strong mask data; abandoning that as mainline would waste evidence.

So my recommendation:

```text
Implementation probe order:
1. Factored quick probe
2. OOD penalty / conservative sweep
3. SOFA PBRS
4. Expert prior or dead-end

Paper mainline priority:
1. OOD / conservative admissibility-aware learning
2. Mean-imputation hidden failure mode
3. Factored / SOFA / expert as supporting experiments if they work
```

---

## 7. Final Recommended Working Story

Best final story if things go reasonably well:

> ICU-Sepsis contains a statistically defined action-support structure that makes it a natural testbed for OOD-action handling in medical RL. We show that the default mean-imputation strategy hides unsupported-action behavior in vanilla Q-learning. We then compare several tabular remedies: hard admissibility masking, support penalties, conservative Q-value pessimism, and optionally factored action learning. Across exact value metrics, admissibility-aware methods reduce unsupported-action use and improve distance-to-V*, while survival rate alone fails to reveal the issue.

This gives:

- one clear failure mode
- one RL-active method family
- one exact-evaluation advantage
- several experiments, not just ablation
- a safe non-clinical claim

