# 03. Candidate Project Directions（3 個五天可完成的題目）

> 本文件對應你列的「第四階段」要求。每個方向都有完整 12 點規格，並附上：
> - **Reviewer-risk analysis**（會被打的點）
> - **如何 defend**
> - **五天可行性評分**（★1–5；5=非常穩、1=極高風險）
>
> 結尾的「比較表」與「推薦」匯總到 [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md) 做為最終題目。

---

## Direction 1 — Action Admissibility & Inadmissible Action Handling

### 1. English title
**"Action Admissibility Matters: A Systematic Study of Inadmissible-Action Handling and Action Masking on the ICU-Sepsis Benchmark"**

### 2. 中文解釋
在 ICU-Sepsis 這個 medical RL benchmark 中，把「不允許動作的處理方式」與「是否使用 action masking」當作 ablation 變數，系統比較這些選擇對 RL 演算法的 performance / safety proxy / sample efficiency / 多 seed 穩定性的影響。**核心切入點**：原 ICU-Sepsis paper 只 report 預設的 `'mean'` strategy 結果，沒有比較 `'terminate'` / `'raise_exception'`，也沒有把 `info['admissible_actions']` 當 action mask 使用。

### 3. Core research question
- **RQ1**：在 ICU-Sepsis 上，三種 `inadmissible_action_strategy`（`mean` / `terminate` / `raise_exception`）會如何改變 model-free RL 的 learning dynamics、最終 performance、與 unsafe action rate？
- **RQ2**：使用 per-state admissible action set 做 action masking，能否在不改變 task objective 的前提下，顯著降低 unsafe action rate 並提高 sample efficiency？
- **RQ3**：在 limited training budget（例如 5 萬 episodes，原 paper 提到「hundreds of thousands」才收斂）下，masking + 適當 strategy 的組合能否比預設 baseline 更快接近 V*？

### 4. Main claim
**「在 ICU-Sepsis 上，inadmissible-action handling 與 action masking 是 first-order 變數：忽略它們會低估 RL 演算法的 sample efficiency 與 safety proxy 表現；採用 admissible-action masking + 適當 strategy 在 50k-episode budget 下可顯著縮短 distance to V*，並把訓練期 inadmissible-action rate 降到接近零。」**

### 5. Novelty / contribution
1. **首次系統比較** ICU-Sepsis-v2 三種 inadmissible action strategy（原 paper 只報告 `mean`）。
2. **首次把 `info['admissible_actions']` 拿來當 Q-learning / SARSA / Dyna-Q 的 action mask** 並做 ablation。
3. **新的 evaluation protocol**：除了 survival rate，引入 distance to V*、policy agreement with expert、state-bucket-wise unsafe action rate 三個 metric，並 release scripts。
4. **多 seed × multi-strategy × masking on/off 的 2D ablation table**，提供未來 user 選擇 strategy 的 reference。

### 6. Required experiments
| Experiment | Conditions | Seeds | 預估時間 |
|---|---|---|---|
| Baseline reproduction (Random / Expert / Optimal) | v2 mean | 5 | 15 min（CPU） |
| Tabular RL grid: Q-learning vs SARSA vs Dyna-Q | × {mean, terminate} × {mask on, mask off} = 12 cells | 5 | ~2 hr（CPU） |
| `raise_exception` strategy edge case | random + Q-learning 跑短期看 crash rate | 3 | 30 min |
| Sample efficiency at 5k/10k/25k/50k episodes | 取 above grid 子集 | 5 | 已含在 grid |
| Bonus: DQN on cluster-centroid state | mean × {mask on, off} | 3 | ~3 hr（CPU/GPU） |

### 7. Required implementation
- `src/env_utils.py`：包裝 `gym.make` + dynamics getter + V* via VI
- `src/policies.py`：Random / Expert / Optimal / Q-learning / SARSA / Dyna-Q（masked variants）
- `src/tabular_rl.py`：核心 Q-learning loop（共用 trainer，可選 masking）
- `src/evaluate.py`：50k-episode rollout evaluation + 各 metric
- `src/analysis.py`：distance to V*、policy agreement、unsafe action rate per SOFA-bucket
- `scripts/run_baselines.py`
- `scripts/run_tabular_rl.py`（吃 YAML config）
- `scripts/run_action_masking_ablation.py`
- `scripts/plot_results.py`
- `configs/`、`results/`、`figures/`
- 可選：`src/dqn.py` for the DQN bonus

### 8. Expected figures / tables

| # | 內容 |
|---|---|
| Fig 1 | learning curves: Q-learning ± mask, ± strategy（4 條線，shaded CI） |
| Fig 2 | bar chart: final return / survival rate / distance-to-V* across 12 conditions |
| Fig 3 | unsafe action rate over training（4 條線）+ per-SOFA-bucket bar |
| Tbl 1 | baseline reproduction（vs paper numbers）— sanity check |
| Tbl 2 | ablation matrix（rows = algorithm × strategy；cols = metric） |
| Tbl 3 | policy agreement with expert（matrix） |
| Tbl 4 (bonus) | DQN with masking |

### 9. Risk level
**Low to medium.** 主要 risk 是 *novelty 看起來太小*（我們的回答：原 paper 沒做這個 ablation，且 masking 在 medical RL 是 first time）。**Technical risk 幾乎為零**：環境穩定、訓練是 CPU 秒級到分鐘級、所有元件都在 repo 內。

### 10. 五天內可行性
**★★★★★（5/5）。** 環境 / metric / baseline 都有現成 code；50k-episode evaluation 在 CPU 上分鐘級；多 seed 用 `joblib` 平行可一晚跑完。

### 11. Reviewer 可能批評
1. *"Tabular RL on a tabular MDP is trivial."* → 已答辯（D.6 in [02](02_related_work_notes.md)）：加 1 個 DQN baseline；強調 benchmark-level analysis。
2. *"Action masking is well-known; what's novel?"* → 我們 novelty 在 *medical RL benchmark 上 first-time 系統比較* + 多 metric protocol，而不是發明 masking。
3. *"Why not deep RL?"* → 預先在 Intro & Limitations 預先 frame：tabular benchmark 允許 oracle V* 比較，這是 deep setting 失去的優勢。
4. *"Survival rate gap (0.78 vs 0.88) is small; results might not be significant."* → 用 5 seeds × 50k episodes 計 95% CI；同時用 distance to V*（更靈敏）做主 metric。
5. *"Inadmissible action rate is a weak safety proxy."* → 我們明寫「safety proxy」字眼，不 claim clinical safety。
6. *"Why not compare to AI Clinician baseline?"* → 我們的 Expert policy 就是 Komorowski-pipeline-estimated clinician policy，已經是 AI Clinician 風格的代表。

### 12. 如何 defend
- Introduction 第二段直接列三點 contribution（見 [02 §D.5](02_related_work_notes.md)）。
- Method section 用 algorithm pseudocode 顯示 masked Q-learning vs vanilla Q-learning，let reviewer 一眼看清差異。
- Limitations 段直接寫「we restrict to tabular methods to enable oracle comparisons; deep methods are explored only as one additional baseline (Appx)」。
- 在 Discussion 引用 Gottesman 2019 guideline，把 work 自我定位為「algorithmic characterization of a medical RL benchmark, not clinical guidance」。

---

## Direction 2 — Expert-Guided Learning / Imitation Initialization

### 1. English title
**"Warm-Starting Reinforcement Learning with the ICU-Sepsis Expert Policy: An Analysis of Imitation-Initialized Q-Learning"**

### 2. 中文解釋
ICU-Sepsis 提供 `expert_policy ∈ R^{716×25}`，是用 MIMIC-III 估計的 clinician policy。本方向研究：用 behavior cloning（fit Q to argmax 配 expert）或 expert prior（ε-greedy with expert prior、KL-regularized Q-learning）作為 warm start，能否在低 episode budget 下提升 sample efficiency 並降低 training-time unsafe action rate。

### 3. Core research question
- **RQ1**：把 Q-table 初始化為 BC-style（依 expert policy 加 soft Q-init）能否顯著加速 Q-learning？
- **RQ2**：在 ε-greedy 中用 expert-prior（取代 uniform random）做 exploration，能否降低 training-time inadmissible action rate？
- **RQ3**：當 expert policy 與 optimal policy 有 gap（已知 Expert=0.78, Optimal=0.88），warm-start 會把學到的 policy 拉向 expert（次優）還是仍能收斂到 optimal？這是 imitation→RL hand-off 的經典課題。

### 4. Main claim
**「Expert-prior initialization 可以在 ICU-Sepsis 上提供顯著的 early-training sample efficiency boost，但會增加 final policy 與 V* 的 gap；該 trade-off 可以被 KL-regularization coefficient 顯式 tune。」**

### 5. Novelty / contribution
1. 在 medical RL benchmark 上對比 (a) cold-start Q-learning、(b) BC-only baseline、(c) Q-init from BC、(d) ε-greedy with expert prior 四種 setting。
2. 用 ICU-Sepsis 的 oracle V* 做精確 evaluation：可以直接量「expert 偏移多遠」，避免 OPE 不可靠。
3. release imitation-initialized Q-learning 的乾淨 reproducible code。

### 6. Required experiments
- Baseline reproduction
- Cold-start Q-learning × 5 seeds
- BC-only（每個 (s,a)：Q[s,a] ← log π_expert(a|s) + 常數；roll-out 評估）
- Q-init = α · log π_expert + (1−α) · 0；掃 α ∈ {0, 0.5, 1.0}
- ε-greedy with expert prior（exploration step 用 π_expert sample，而非 uniform）
- KL-regularized Q-learning：每步 reward 減去 β · D_KL(π_t ‖ π_expert)，掃 β ∈ {0, 0.01, 0.1, 1}

### 7. Required implementation
- 大部分與 Direction 1 共用 base，加 `src/imitation.py`（BC + Q-init + prior-greedy + KL-reg）
- 不需 deep network

### 8. Expected figures / tables
- learning curve × 4 conditions
- final return vs β（KL coefficient）trade-off curve
- policy agreement with expert as function of β
- table：early-episode (≤5k) AUC 比較

### 9. Risk level
**Medium.** Imitation→RL 的 trade-off 有可能在 ICU-Sepsis 上太小（因為 Random=Expert=0.78），導致 effect size 不明顯。如果 expert policy 與 random 在 return 上等價，warm-start 的優勢可能不明顯在 survival rate 上。**緩解**：用 distance-to-V* 與 early-episode return 做主 metric，這對小 effect 更敏感。

### 10. 五天內可行性
**★★★★（4/5）。** Code 都是 tabular CPU，5 天綽綽有餘。但 effect size 風險使「結果是否值得寫 paper」有變數，是中等 risk。

### 11. Reviewer 可能批評
1. *"Why not deep imitation (DAgger / GAIL)?"* → 我們限定 tabular 為了 oracle 比較；deep imitation 在後續工作中。
2. *"BC + Q-init 已經在 Hester 2018 等做過。"* → 我們的 novelty 在 medical RL benchmark 上，且用 V* 做精確 evaluation。
3. *"Expert policy 本身已經是 reproduce 自 Komorowski，是不是 cheating？"* → 不算；研究問題就是「給定 expert，warm-start 有多有效」，這在臨床部署情境正是現實設定。

### 12. 如何 defend
- 在 Method 顯式寫 KL-regularized Bellman update 的公式。
- Discussion 強調 expert-init 是 medical RL deployment 的「最常見實際設定」，benchmark 上嚴格量化是有用的。

---

## Direction 3 — Reward Sparsity & SOFA-based Potential Shaping

### 1. English title
**"Potential-Based Reward Shaping with SOFA Scores on the ICU-Sepsis Benchmark: Sample Efficiency Without Sacrificing Policy Invariance"**

### 2. 中文解釋
ICU-Sepsis 是 terminal-reward MDP（只有死活兩個 reward），sample efficiency 低（原 paper 指出 hundreds of thousands of episodes）。本方向研究用 Ng-Russell potential-based reward shaping，把 SOFA score 當 potential 函數 Φ(s) = −SOFA(s)（SOFA 越低越好），在不改變 optimal policy 的前提下加速學習。

### 3. Core research question
- **RQ1**：以 SOFA 為 potential 的 PBRS 能否在 ICU-Sepsis 上 measurably 提高 Q-learning 的 sample efficiency？
- **RQ2**：因為 PBRS 對 optimal policy 有 invariance（Ng-Russell theorem），final policy 是否與無 shaping 收斂到同一個？我們可量化 distance-to-V*。
- **RQ3**：與「非 potential-based」naive shaping（單純 r += −Δ SOFA）對比，能否實證 invariance theorem 在 medical benchmark 上的重要性？（naive shaping 預期會偏到次優。）

### 4. Main claim
**「在 ICU-Sepsis 上，SOFA-based PBRS 能在 5k-episode budget 內把 Q-learning 的 distance-to-V* 顯著降低，且不改變 optimal policy；naive (non-potential) SOFA shaping 則會偏離 V*。」**

### 5. Novelty / contribution
1. 在 medical RL benchmark 第一次 explicit demonstrate Ng-Russell PBRS 與 naive shaping 的差別。
2. 用 SOFA（臨床 severity 指標）作為 potential，連結 medical domain knowledge 與 RL theory。
3. release PBRS-with-SOFA 的乾淨實作。

### 6. Required experiments
- Baseline + cold-start Q-learning
- PBRS with Φ(s) = −α · SOFA(s)，掃 α ∈ {0, 0.01, 0.1, 1}
- Naive shaping（每步 r += −α · Δ SOFA）
- 同時比較 mean / terminate strategy（次要 ablation）
- 最終 policy 與 V* 的逐 state Q-value 比較

### 7. Required implementation
- `src/reward_shaping.py`：兩種 shaper（PBRS / naive）
- 與 Direction 1 共用 RL loop；shaping 只是 reward override

### 8. Expected figures / tables
- learning curves: vanilla / PBRS / naive
- final distance-to-V*: PBRS ≈ vanilla < naive（驗證 invariance）
- per-SOFA-bucket policy agreement

### 9. Risk level
**Medium to high.** 主要 risk：
- ICU-Sepsis 的 reward 雖 sparse 但 episode 很短（avg 9–11 步），PBRS 加速 effect 可能不大。
- SOFA 是 noisy proxy，做為 potential 不一定 informative。
- **Medical claim 風險**：如果寫不好，reviewer 會覺得「你把 SOFA 拿來當 reward 是 implicit clinical claim」。

### 10. 五天內可行性
**★★★（3/5）。** Code 簡單，但 effect-size 風險與 medical-claim 風險使這方向最棘手。

### 11. Reviewer 可能批評
1. *"PBRS 是經典技術，沒 novelty。"* → 我們 novelty 在 medical RL benchmark 上 explicit 比較 PBRS vs naive，並把 SOFA 接入。
2. *"用 SOFA 當 potential 是 implicit clinical claim。"* → 我們在 Limitations 明確說「Φ 的選擇是 algorithmic, not clinical; we do not claim SOFA reduction is a treatment goal」。
3. *"Effect size 可能很小，這個結論有意義嗎？"* → 我們的 secondary claim「invariance 在 noisy potential 下仍 hold」本身就有教學意義。

### 12. 如何 defend
- Method 段引用 Ng 1999 並寫公式。
- 在 Discussion 明寫 PBRS 與 medical-claim 的 firewall。
- 把這個方向當「次要 RQ」放在 Direction 1 paper 的 Appendix，不要當主軸。

---

## 比較表

| 維度 | D1 Admissibility & Masking | D2 Expert-Init | D3 PBRS |
|---|---|---|---|
| 五天可行性 | ★★★★★ | ★★★★ | ★★★ |
| Novelty 強度 | 高（原 paper 明確未做） | 中（imitation→RL 經典問題） | 中（PBRS 經典） |
| Reviewer 風險 | 低 | 中（effect size 風險） | 中高（medical claim 易誤踩） |
| Code complexity | 低 | 中 | 低 |
| 訓練時間 | 分鐘級（CPU） | 分鐘級 | 分鐘級 |
| 預期 figure 數 | 3–4 | 3 | 2–3 |
| 主要 evaluation metric | survival rate, distance-to-V*, unsafe action rate, policy agreement | distance-to-V*, early-episode AUC | distance-to-V*, sample efficiency |
| 是否需要 deep RL baseline | 可選 1 個 DQN 強化 | 不需 | 不需 |
| Medical claim 風險 | 低 | 低 | 中 |
| 是否能寫出乾淨 paper logic | 是 | 是 | 是（但較窄） |

---

## 推薦

**推薦 Direction 1（Action Admissibility & Inadmissible Action Handling）為主軸**，理由（與你列的偏好一致）：

1. **五天可行性最高**（★★★★★）。
2. **Novelty 最強**：原 paper 明確未系統做的兩件事——三種 inadmissible_action_strategy 的比較、`info['admissible_actions']` 當 action mask 的 ablation。
3. **Reviewer 風險最低**：所有 claim 都是 algorithmic / benchmark-level，沒有 medical claim。
4. **可以 cleanly 寫 4–8 頁 NeurIPS paper**，且有清楚的 figures & ablation matrix。
5. **可以 graceful 把 D2、D3 部分內容收為 Appendix 加分**：例如把 expert-init 當 1 個 ablation 條件、把 PBRS 當 1 個 supplementary experiment，都能放進同一篇 paper 的 Appendix 而不破壞主軸。

詳細 project plan 進入 [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md)。
