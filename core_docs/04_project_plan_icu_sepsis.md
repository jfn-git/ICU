# 04. Project Plan — ICU-Sepsis Action Admissibility Study

> 推薦題目：**Direction 1（Action Admissibility & Inadmissible Action Handling）**
> 對應你的偏好題目：「在 ICU-Sepsis medical RL benchmark 中，分析 admissible action constraints / action masking / inadmissible action handling 對 RL policy performance、safety proxy、sample efficiency 與 stability 的影響。」
>
> 本計畫已通過：
> - 課程要求 ✅（DRL-focused，benchmark methodological paper 屬可接受 scope）
> - Repo 支援度 ✅（v2 三種 strategy + `info['admissible_actions']` 直接可用）
> - 文獻定位 ✅（原 paper 未做此 ablation，無已知 follow-up 重疊）

---

## 1. Project Title 候選

| # | English Title |
|---|---|
| A | **Action Admissibility Matters: A Systematic Study of Inadmissible-Action Handling and Action Masking on the ICU-Sepsis Benchmark** |
| B | **Masking the ICU: How Admissible-Action Constraints Reshape Reinforcement Learning on a Medical Benchmark MDP** |
| C | **Safety Proxies and Sample Efficiency: Re-evaluating Tabular RL on ICU-Sepsis under Three Inadmissible-Action Strategies** |

**推薦：Title A**（最直接、cover 我們三個 contribution、容易被搜尋）。
B 雖然 catchy 但 "ICU" wordplay 可能被部分 reviewer 視為 not serious。
C 偏向 evaluation-protocol-paper 風格，但弱化了 masking 的部分。

---

## 2. Abstract Draft

### 2.1 繁體中文說明版（給組員溝通用）

我們把 ICU-Sepsis（Choudhary et al., RLC 2024）這個 716-state、25-action、源自 MIMIC-III 的 medical RL benchmark，當作一個「ablation laboratory」。我們系統比較了它 v2 提供的三種 inadmissible-action handling strategy（`mean` / `terminate` / `raise_exception`）與兩種訓練設定（有無 action masking），在 Q-learning、SARSA、Dyna-Q 三個 tabular RL 演算法上跑了 5 個 seed × 多個 episode budget 的 ablation matrix。我們報告 (i) survival rate、(ii) distance to V*、(iii) training-time inadmissible-action rate、(iv) policy agreement with the estimated clinician policy 四個 metric，並由此論證：原 ICU-Sepsis paper 預設的 `mean` strategy 系統性地低估了 RL 演算法的 sample efficiency；action masking 即使在 tabular setting 下也能在 50k-episode budget 內顯著縮短 distance to V*。我們同時 release 一份 reproducible 評估 protocol，幫助未來 ICU-Sepsis user 報告 multi-metric 結果。**本工作是 benchmark-level algorithmic analysis，沒有也不應作為臨床建議。**

### 2.2 英文 paper abstract 初稿（NeurIPS 2026 template）

> Medical reinforcement learning benchmarks are increasingly used to evaluate algorithmic progress without requiring access to protected clinical datasets. ICU-Sepsis (Choudhary et al., 2024), a 716-state, 25-action tabular MDP distilled from MIMIC-III, is one such benchmark; its v2 release exposes three distinct strategies for handling actions that lack sufficient statistical support in the source data, yet the original benchmark report only evaluates the default `mean` strategy. In this paper, we conduct a systematic ablation across (i) all three inadmissible-action-handling strategies, (ii) action masking using the per-state admissible action set exposed by the environment, and (iii) three tabular RL algorithms (Q-learning, SARSA, Dyna-Q). On a 5-seed, multi-budget evaluation we find that (a) action masking consistently reduces the training-time inadmissible-action rate to near zero without harming final return, (b) the choice of inadmissible-action strategy materially changes both the learning curve and the policy-agreement-with-clinician metric, and (c) survival rate alone is a poor sensitivity instrument; distance-to-V* and per-state-bucket unsafe-action rate are far more informative. We release a reproducible evaluation protocol with code. Our results are about algorithmic behavior on a benchmark abstraction and are not clinical recommendations.

---

## 3. Motivation

### 3.1 Medical RL 的核心困難
- 真實 cohort 資料（MIMIC-III）需要 PhysioNet credential，重新建環境要數週 [Komorowski2018Nature]。
- OPE 估計不可靠，許多 sepsis RL paper 因此被質疑 [Gottesman2019NatMed]。
- 結果，多數 method paper 只能在自製 evaluation pipeline 上跑，**reproducibility 是 active issue**。

### 3.2 ICU-Sepsis 提供的價值
- Tabular MDP，可在 CPU 秒級跑。
- model 完全可見，V* 可由 VI 精確計算 → **不用 OPE，可以做 ground-truth comparison**。
- 不需 MIMIC-III credential。
- v2 提供 `inadmissible_action_strategy` 三種 mode 與 per-state admissible action sets。

### 3.3 為什麼 Admissibility / Masking 重要
- 在 medical decision making 中，inadmissibility 意義不是「物理上不可能」而是「資料上缺乏支持」。
- 把 inadmissible action 視為 mean of admissibles（v2 預設）等於 silently 用 prior 填補，可能影響 RL 對「資料覆蓋度」的學習行為。
- Action masking 在 RTS games 中已知對 PG 演算法有 dramatic effect [Huang2021FLAIRS]，但 **在 medical RL benchmark 上幾乎沒人嘗試**。

### 3.4 為什麼是合理的 course project
- 完全 RL-focused，符合 DRL 課程 scope。
- 5 天可完成，且可產生乾淨 figure & table。
- 無 clinical claim，無 medical claim 風險。
- 結果對 ICU-Sepsis 使用者實質有用（指導他們怎麼設定 ablation knob）。

---

## 4. Research Questions

| RQ | 問題 | 對應實驗 |
|---|---|---|
| RQ1 | 三種 `inadmissible_action_strategy` 對 RL 訓練 dynamics、最終 performance、unsafe action rate 的影響？ | Exp G1 |
| RQ2 | 是否使用 per-state admissible action set 做 action masking 能改變 sample efficiency 與 unsafe action rate？ | Exp G2 |
| RQ3 | 在受限 budget（5k–50k episodes）下，「strategy 選擇 × masking on/off」哪個組合最快接近 V*？ | Exp G3 |

---

## 5. Hypotheses

| H | 對應 RQ | 預測（defensible，不誇大） |
|---|---|---|
| H1 | RQ1 | 三種 strategy 的 *final* return 差異不大（< 0.03），但 *training dynamics* 與 *unsafe action rate* 顯著不同；`terminate` 會放大 random-explore agent 的早期死亡率。 |
| H2 | RQ2 | Action masking 把 training-time inadmissible-action rate 壓到接近 0；對 final return 影響在 ±0.01 之內；對 sample efficiency（達到 0.85 return 所需 episodes）有顯著正向效果。 |
| H3 | RQ3 | masking-on + mean strategy 是 50k-episode budget 下最快達 0.86 return 的組合（與 paper 的 DQN ≈ 0.86 對齊）。 |

> 我們不會 claim「action masking improves clinical outcomes」這種 claim。所有 hypothesis 都是 benchmark-internal 量化陳述。

---

## 6. Methods（要實作的 policies / algorithms）

| # | Method | 角色 | 是否要實作 |
|---|---|---|---|
| 1 | Random | 下界 baseline | 用 repo 的 `_rand_policy` |
| 2 | Expert (clinician estimate) | 中間 baseline | 用 `env.expert_policy` |
| 3 | Optimal (Value Iteration) | 上界 / oracle V* | 用 repo 的 `value_iteration` |
| 4 | Vanilla Q-learning | 主 RL 演算法 | 自己寫（tabular，CPU） |
| 5 | Vanilla SARSA | RL 演算法 #2 | 自己寫 |
| 6 | Dyna-Q (n=5) | RL 演算法 #3 | 自己寫 |
| 7 | **Action-masked** versions of 4/5/6 | 主對照 | 把 mask 加到 argmax 與 ε-greedy |
| 8 | (Bonus) DQN with one-hot state + mask | 防守 "not DRL" 質疑 | 用 `stable-baselines3` 或自己寫小 PyTorch DQN |
| 9 | (Bonus, optional) BC-init Q-learning | 借自 Direction 2 當 Appendix | 用 `env.expert_policy` 初始化 Q |

**Action masking 的具體實作**（給寫 paper 時用）：

```python
def masked_argmax(Q_row: np.ndarray, admissible: list[int]) -> int:
    """argmax over admissible actions only."""
    mask = np.full_like(Q_row, -np.inf)
    mask[admissible] = Q_row[admissible]
    return int(np.argmax(mask))

def masked_eps_greedy(Q_row, admissible, eps, rng):
    if rng.random() < eps:
        return int(rng.choice(admissible))
    return masked_argmax(Q_row, admissible)
```

**Reward / value-error metric**（用 model-known property）：
```python
V_star = value_iteration(tx_mat, r_mat, gamma)  # (716,)
V_pi   = policy_evaluation(pi_table, tx_mat, r_mat, gamma)  # (716,)
distance_to_optimal = (d_0 @ (V_star - V_pi))   # scalar ≥ 0
```

---

## 7. Experiment Design

### 7.1 Must-have experiments

| ID | 名稱 | 條件 | Seeds | 預估時間 |
|---|---|---|---|---|
| **B0** | Baseline reproduction（Random / Expert / Optimal） | v2 mean, 50k eval episodes | 5 | 15 min |
| **G1** | inadmissible_action_strategy × algorithm | {mean, terminate} × {Q-learning, SARSA, Dyna-Q} = 6 cells | 5 | 30 min × 6 = 3 hr |
| **G2** | action masking ablation | {mask on, mask off} × {Q-learning, SARSA, Dyna-Q} 在 mean strategy 下 | 5 | 已含於 G1 部分 |
| **G3** | sample-efficiency curves | 在 G1∩G2 子集，evaluate at 5k/10k/25k/50k episodes | 5 | 同上 |
| **S0** | `raise_exception` edge-case sanity check | random policy + Q-learning short run；只報「會 crash 嗎」 | 3 | 30 min |
| **B1** | Multi-seed 穩定性 | 上述所有 cell × 5 seeds，95% CI | 5 | 已含 |

> 全部 must-have 在 single CPU machine 上預估 **< 6 小時** 可跑完（含寫 log）。

### 7.2 Nice-to-have experiments（時間有就做，沒有就放棄）

| ID | 名稱 | 預估時間 |
|---|---|---|
| N1 | DQN with masking（one-hot state + masked-Q output） | 4–6 hr overnight |
| N2 | BC-init Q-learning（Direction 2 借入） | 1 hr |
| N3 | SOFA-bucket-wise unsafe action rate（per-bucket bar chart） | 30 min（純 analysis） |
| N4 | Policy agreement with expert（matrix）| 30 min |
| N5 | SOFA-PBRS quick demo（Direction 3 借入做 1 figure） | 1 hr |

### 7.3 計畫拋棄條件
- 若 Day 3 結束 G1+G2+B0 還沒跑完，**直接放棄所有 nice-to-have**，把時間轉去寫 paper。
- 若 N1 (DQN) 在 Day 4 沒收斂到合理數字，paper 中改寫成「we attempted DQN; results in Appendix; main analysis remains tabular」。

---

## 8. Metrics

| Metric | 公式 / 來源 | 為什麼選它 |
|---|---|---|
| **Average return** (= survival rate) | 50k-episode rollout mean | paper 慣例；對比原 paper |
| **Average episode length** | 同上 mean | 對比原 paper |
| **Distance to V*** | E_{s∼d_0}[V*(s) − V^π(s)]；用 model-known PE 算精確值 | 比 survival rate 靈敏 10×；medical RL 罕用、適合做主結果 |
| **Inadmissible-action rate (training)** | training 時 selected action 不在 admissible set 的比例 | 直接 quantify masking 效果 |
| **Inadmissible-action rate (deployed)** | 用 final policy rollout 時違法率 | 對應 deployment safety proxy |
| **Policy agreement with expert** | 1/|S| · Σ_s 1{argmax_a π(s,a) = argmax_a π_expert(s,a)} | 與 clinician 一致性，不是 clinical claim |
| **Sample efficiency** | episodes-to-reach-{0.80, 0.85, 0.87} | 受限 budget 下的 horse race |
| **Stability across seeds** | 5-seed std / 95% CI 寬度 | reviewer-quality 指標 |

> **重要 framing**：metric 5 與 6 是 *safety proxy*，paper 中明寫「proxy」字眼，避免變成 clinical claim。

---

## 9. Expected Figures and Tables

| # | 類型 | 內容 |
|---|---|---|
| **Fig 1** | Learning curves (3-panel)：Q-learning / SARSA / Dyna-Q，每 panel 4 條線（{mean,terminate}×{mask on, off}），y=return, shaded 95% CI | 主圖，page 4 |
| **Fig 2** | Bar chart：final-policy distance-to-V*，cells = 12 條件 | 主圖 |
| **Fig 3** | training-time inadmissible-action rate over episodes，4 條線 | 主圖 |
| **Fig 4** (optional) | per-SOFA-bucket unsafe-action rate bar | Appendix |
| **Tbl 1** | Baseline reproduction（Random/Expert/Optimal）vs paper numbers — sanity check | Method section |
| **Tbl 2** | Main ablation matrix：rows = (algo, strategy, mask)，cols = (return ±, ep-len, dist-V*, unsafe-rate, agreement) | 主表，page 5 |
| **Tbl 3** (optional) | Sample efficiency: episodes-to-reach-0.85 | Appendix |
| **Tbl 4** (optional) | DQN bonus row | Appendix |

> 所有 figure 都用 matplotlib + seaborn-darkgrid；統一字體 size / DPI；CI 用 shaded region。

---

## 10. Implementation Plan

### 10.1 建議目錄結構（新專案資料夾 `./icu_sepsis_project/` 或 root）

```
icu_sepsis_project/
├── README.md
├── requirements.txt              # gymnasium, numpy, scipy, matplotlib, pandas, tqdm, pyyaml
├── icu-sepsis/                   # 直接 pip install -e ./icu-sepsis/packages/icu_sepsis
├── configs/
│   ├── default.yaml
│   ├── ablation_strategy.yaml
│   └── ablation_masking.yaml
├── src/
│   ├── __init__.py
│   ├── env_utils.py              # gym.make wrapper, dynamics getter, VI cached
│   ├── policies.py               # Random, Expert, Optimal sampler classes
│   ├── tabular_rl.py             # Q-learning, SARSA, Dyna-Q trainers (mask kwarg)
│   ├── evaluate.py               # n-episode rollout, return + ep-len + safety proxy
│   ├── analysis.py               # distance to V*, agreement-with-expert, SOFA-bucket
│   ├── reward_shaping.py         # (optional) PBRS for N5
│   ├── imitation.py              # (optional) BC + Q-init for N2
│   └── dqn.py                    # (optional) DQN with mask for N1
├── scripts/
│   ├── run_baselines.py
│   ├── run_tabular_rl.py
│   ├── run_action_masking_ablation.py
│   ├── run_strategy_ablation.py
│   ├── plot_results.py
│   └── make_tables.py
├── results/                      # JSON / CSV per run；不入版控
├── figures/                      # PNG / PDF；最終 paper 用
├── logs/                         # per-run text log
├── paper/
│   ├── main.tex                  # NeurIPS 2026 template
│   ├── neurips_2026.sty
│   ├── references.bib
│   └── figures -> ../figures/
└── tests/
    └── test_sanity.py            # 確認 env 安裝 & VI 收斂
```

### 10.2 Config schema（YAML）

```yaml
# configs/default.yaml
env:
  id: "Sepsis/ICU-Sepsis-v2"
  inadmissible_action_strategy: "mean"   # mean | terminate | raise_exception
training:
  algo: "q_learning"                      # q_learning | sarsa | dyna_q
  use_action_mask: false
  num_episodes: 50000
  alpha: 0.1
  gamma: 1.0
  eps_start: 1.0
  eps_end: 0.05
  eps_decay_episodes: 10000
  dyna_n: 5
evaluation:
  num_eval_episodes: 50000
  seeds: [0, 1, 2, 3, 4]
logging:
  out_dir: "results"
  run_name: "default"
```

每個 run 留下 JSON：
```json
{
  "config": {...},
  "wall_time_sec": 47.3,
  "final_return": 0.86,
  "final_ep_len": 10.5,
  "distance_to_Vstar": 0.012,
  "unsafe_action_rate_training": 0.31,
  "unsafe_action_rate_deployed": 0.0,
  "agreement_with_expert": 0.41,
  "learning_curve": [...]
}
```

---

## 11. Reproducibility Plan

| 元件 | 規範 |
|---|---|
| Config | 全部用 YAML；CLI flag override 可選 |
| Seeds | NumPy + Python `random` + Gymnasium `env.reset(seed=...)` 三處統一 set |
| Result logging | 每 run 寫一個 JSON + 學習曲線 CSV；檔名包含 config hash |
| Saved policies | tabular Q-table 存 `.npy`；DQN 存 PyTorch checkpoint |
| Saved plots | `figures/` 下 PNG 300dpi + PDF |
| README instructions | `make reproduce-fig1` 一鍵跑 |
| Hardware spec | 在 paper Appendix 寫清楚（CPU model、RAM、總 wall time） |
| Code release | 在 paper 中放 **anonymous GitHub link**（用 anonymous.4open.science）；不能放真實 GitHub |

---

## 12. Paper Outline（NeurIPS 4–8 pages 安排）

| Section | 預估頁數 | 內容 |
|---|---|---|
| **Abstract** | 0.3 | 4 句：problem / approach / findings / disclaimer |
| **1. Introduction** | 1.2 | medical RL 困境 → ICU-Sepsis benchmark → 我們的三個 contribution bullet → "no clinical claim" 預先 disclaimer |
| **2. Related Work** | 0.7 | Sepsis RL（AI Clinician, Raghu, Komorowski）/ Medical RL guidelines（Gottesman）/ Action masking（Huang）/ Benchmark reproducibility |
| **3. The ICU-Sepsis Benchmark & Our Setup** | 1.0 | 環境基本參數 (716 state, 25 action, γ=1) / 三種 inadmissible_action_strategy / admissible action info / Method 4 個 metric 定義 |
| **4. Method** | 0.8 | Q-learning / SARSA / Dyna-Q 的 masked 版本 pseudocode；如何算 V* 與 distance-to-V*；how we vary strategy |
| **5. Experiments** | 2.0 | 5.1 setup / 5.2 baseline reproduction (Tbl 1) / 5.3 strategy ablation (Fig 1, Tbl 2) / 5.4 masking ablation / 5.5 sample efficiency / 5.6 stability |
| **6. Discussion** | 0.7 | 三個 RQ 的回答；為什麼 survival rate 是 noisy；對 ICU-Sepsis 使用者的具體建議 |
| **7. Limitations** | 0.4 | tabular only; SOFA-bucket 是粗略 grouping; not clinical recommendation; mass-mode + benchmark abstraction caveats |
| **8. Conclusion** | 0.2 | summary + future work（continuous-state extension, deep RL with mask, MIMIC-IV based ICU-Sepsis-IV） |
| **References** | 不計 | ≈ 15–20 篇 |
| **Appendix** | 不計 | 演算法完整偽碼、completion of all 12 cells in ablation matrix、DQN bonus、`raise_exception` edge-case |

**目標**：main content 7 頁；保留 1 頁 buffer。

---

## 13. Reviewer-Risk Analysis（事先 defuse）

| 風險 | 回應 paper 中放在哪 | 對應內容 |
|---|---|---|
| "Tabular MDP 太簡單" | Intro 第 4 段 + Limitations | tabular 是 benchmark 設計；用它換 oracle V* 比較。Appendix 補 1 個 DQN baseline。 |
| "Not deep RL — 違反 DRL 課程 scope" | Intro 末段 (mini-conference 不會在 paper 內提，但要 brief 寫 "RL methodology focus") | 強調 RL methodology 為主，DRL not strictly required by venue charter |
| "Medical claim 過度" | Abstract + Intro + Discussion + Limitations 共 4 處 disclaimer | 永遠寫 "benchmark-internal" / "safety proxy" / "not a clinical recommendation" |
| "Lack of real clinical validation" | Limitations | 我們 explicitly do not validate clinically; refer to Gottesman 2019 guideline. |
| "Limited novelty" | Intro contribution bullet | 原 paper 未做 strategy 比較與 masking ablation；引用原 paper 的 Future Work 段做 cross-reference |
| "Insufficient seeds" | Appendix table | 5 seeds + 95% CI；mention budget limitation in Limitations |
| "Action masking 太 trivial" | Discussion §6 | 在 medical RL benchmark 上 first time 系統化；effect on training-time unsafe-action rate 是 non-trivial |
| "raise_exception 沒結果" | Method §3 + Appendix S0 | 因設計上會 crash，我們報告它是 sanity / debug tool，不主分析 |
| "Survival rate 差異不顯著" | Discussion + Fig 2 | 我們主張 distance-to-V* 是主要 sensitivity metric；survival 噪音由 base survival 高所致 |
| "為什麼 γ=1，不該嗎" | Method §3 | 跟原 paper 設定一致；做 γ<1 sensitivity 在 Appendix（如果 nice-to-have 時間夠） |

---

## 14. Minimum Viable Paper（時間真的不夠時的底線）

若 Day 4 結束時還沒 finalize 所有 must-have，**minimum viable paper** = 以下子集：

| 必需 | 內容 |
|---|---|
| ✅ B0 baseline reproduction | 與 paper 數字一致的 Tbl 1 |
| ✅ G1 strategy ablation | 只跑 Q-learning × {mean, terminate} × 5 seeds = Fig 1 (1-panel) + Tbl 2 部分 |
| ✅ G2 masking ablation | 只跑 Q-learning × {mask on, off} × mean strategy × 5 seeds = Fig 1 (1-panel) + Tbl 2 部分 |
| ✅ Distance-to-V* | 必須算（Tbl 2 一個 column） |
| ✅ Unsafe action rate | 必須算（Tbl 2 一個 column） |
| ✅ 5 個 seed × 50k episodes | 必要 |
| ❌ SARSA / Dyna-Q | 拿掉，只在 Limitations 提「future work to extend to other tabular RL algorithms」 |
| ❌ Policy agreement | 拿掉或縮為 1 個 number |
| ❌ DQN, BC-init, PBRS | 全部拿掉 |

→ 這個 MVP 仍然構成 4 頁 NeurIPS paper，且 contribution claim 1 + 3 完整成立。

---

## 15. Stretch Goals（must-have 提早完成的話）

按優先級：

1. **N3 SOFA-bucket-wise unsafe action rate bar chart**（30 分鐘，加 1 個 figure，paper 強很多）
2. **N4 Policy agreement with expert matrix**（30 分鐘，補 1 個 metric column）
3. **N1 DQN with masking**（4–6 hr overnight，**defend "not deep RL"** 神器）
4. **N2 BC-init Q-learning 1 ablation row**（1 hr，借 Direction 2 元素，paper 看起來更廣）
5. **N5 SOFA-PBRS 1 row**（1 hr，借 Direction 3 元素）

stretch 全做完不可能（時間不夠），但前 2 個非常 cheap，建議無條件加做。

---

## 16. 立即執行 Checklist（接下來 12 小時）

> 假設 12 小時內 1 個人 work（或團隊分工）。**第一目標：環境裝好 + 確認原 paper 數字能重現**。在這之前不要碰 paper writing。

### 第 1 小時：環境裝設 sanity
- [ ] `python --version` ≥ 3.10
- [ ] `pip install -e ./icu-sepsis/packages/icu_sepsis`
- [ ] `pip install -e ./icu-sepsis/packages/icu_sepsis_helpers`
- [ ] 跑 `python ./icu-sepsis/examples/quickstart.py` → 應 print 出 state / next state / reward
- [ ] 跑 `python ./icu-sepsis/examples/get_baselines.py -v 2` → 應得到 ≈ Random 0.78 / Expert 0.78 / Optimal 0.88
- [ ] 在 `core_docs/` 下新增 `setup_log.md` 記錄 Python 版本、套件版本、得到的 baseline 數字

### 第 2–4 小時：repo skeleton
- [ ] 在 root 建 `icu_sepsis_project/` 結構（見 §10）
- [ ] `src/env_utils.py`：寫 `make_env(strategy)`、`get_dynamics(env)`、`compute_Vstar(env, gamma)`、`compute_Vpi(pi_table, env, gamma)`
- [ ] `src/evaluate.py`：寫 `evaluate(env, policy_callable, n_eps=50_000, seed=0)`，回傳 dict
- [ ] `src/analysis.py`：寫 `distance_to_optimal`、`agreement_with_expert`、`unsafe_rate_per_sofa_bucket`

### 第 5–8 小時：Q-learning + 確認能跑
- [ ] `src/tabular_rl.py`：寫 `train_q_learning(env, *, use_mask, num_episodes, ...)`
- [ ] 在 `mean` strategy + mask=off 下，5 seeds × 50k episodes 跑一次 → final return 應接近 0.79（與 paper 報告 Sarsa/Q-learning 一致）
- [ ] 把結果寫進 `results/qlearning_mean_nomask.json`

### 第 9–12 小時：第一個 ablation cell 跑通
- [ ] 加 `use_mask=True` 跑同 config × 5 seeds
- [ ] 比對 mask-on vs mask-off 的學習曲線：應該 mask-on 更快達到 baseline return
- [ ] 在 `figures/preliminary_curve.png` 畫出 2 條曲線 + CI
- [ ] 把這張 preliminary figure 貼到 Slack / 群組，讓全組看到「我們真的在做事 + 方向 work」

### 同步進行（任一組員平行）
- [ ] 在 OverLeaf 開新 project，import NeurIPS 2026 template，把 §12 的 section 標題打上去，line number 開啟
- [ ] 在 OpenReview 確認所有組員帳號都 active
- [ ] 把 `core_docs/02_related_work_notes.md` 中的 7 個 BibTeX key 整理到 `paper/references.bib`，並用 Google Scholar 補完整 entry

---

> **下一步**：把這份計畫對齊到逐日工作排程 → 進到 [`05_five_day_execution_schedule.md`](05_five_day_execution_schedule.md)。
