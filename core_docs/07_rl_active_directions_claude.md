# 07. RL-Active Direction Analysis (Claude)

> **作者**：Claude
> **日期**：2026-05-22
> **目的**：回應「目前 failure-mode / ablation 題目的 RL 主動性不夠」的顧慮，提出比 ablation 更有 RL 實驗性的方向。
> **使用方式**：本文件與 codex 版本 (`07_rl_active_directions_codex.md` 或同名 codex 檔) 互相對讀，最後合併出一份**實作順序排名**。
>
> 前置脈絡見：[`06_project_plan_mean_imputation_hides_unsupported_actions.md`](06_project_plan_mean_imputation_hides_unsupported_actions.md)、[`../CURRENT_STATUS_EXPLAINED.md`](../CURRENT_STATUS_EXPLAINED.md)。

---

## 0. 使用者的顧慮（被回應的問題）

- 現有題目（不論舊 ablation 還是 doc 06 的 "mean imputation 藏起 unsupported actions" failure-mode framing），**以研究角度講得出 contribution / research gap**，但 **RL 主動性不夠**。
- 它本質是「站在 RL 應用環境上，**被動審視** benchmark / 方法被忽視的問題」，而非「**主動**在 RL 上提出做法」。
- 使用者要的是：更有 RL 實驗性、更展現 RL 能動性的方向（method 型或 question 型皆可）。
- 約束：環境跑得極快（CPU 秒/分鐘級），可花一個下午探索；不一定要取代現有題目，**最在意最終結果的豐富度**；deadline 2026-05-25。

---

## 1. 核心洞察：admissibility ≡ offline RL 的 OOD-action 問題

「inadmissible / data-coverage 不足的動作」在 RL 文獻有正式名稱：**out-of-distribution (OOD) action / distributional shift**，這是**整個 offline RL 領域**的核心難題。

現有解法（hard action masking）只是這個問題**最粗暴的一個點**。Offline RL 已發展一整套「主動的 RL 方法」處理同一件事：

| 方法 | 處理 OOD action 的方式 | 與我們 admissibility 的關係 |
|---|---|---|
| BCQ (behavior-constrained) | 限制 policy 在資料中出現過的動作 | ≈ soft 版 admissibility masking |
| CQL (conservative Q-learning) | 對 OOD 動作的 Q 值加 pessimism penalty | 比 hard mask 更平滑 |
| Pessimistic VI (VI-LCB) | count-based lower-confidence-bound，count 越少懲罰越大 | admissibility = count 為 0 的極端情形 |

**為什麼這對我們極有利**：ICU-Sepsis 有**完整已知 dynamics → 可算 exact V***。Offline RL 方法平常**最大痛點是無法精確評估**（需 noisy OPE）。我們的環境天生繞過此痛點。

**升級後的題目敘事**：

> 「ICU-Sepsis 是一個有 ground-truth V* 的 testbed，讓我們能**精確比較 offline RL 處理 OOD-action 的各種方法**。」

→ 一步把專案從「被動診斷一個 benchmark 毛病」變成「主動方法比較」，而現有的 masking 結果直接成為這個 spectrum 上的一個 baseline point。**這是我認為投報率最高的單一改動。**

---

## 2. 同類醫療 RL 應用做了哪些「RL 努力」（可借鑑來源）

ICU-Sepsis 是 sepsis RL（Komorowski AI Clinician 一脈）的 tabular 抽象，同類工作高度可借鑑。
（年份/venue 為記憶所及，**投稿前需查證**，沿用團隊「未驗證」慣例。）

| 工作 | RL 上做了什麼 | 可移植性 |
|---|---|---|
| Komorowski et al. *AI Clinician* (Nature Med 2018) | sepsis 離散化成 MDP，offline policy iteration + OPE | ICU-Sepsis 為其 tabular 後裔，直接相關 |
| Raghu et al. (2017) sepsis Deep RL | 連續 state + Dueling Double DQN | 可做但偏 deep，非 tabular 強項 |
| **Fatemi et al. *Medical Dead-ends* (NeurIPS 2021)** | 辨識「死局狀態」(無論做什麼都近乎必死)，學獨立 value 標記高風險 state/action | ⭐ 我們有真 dynamics → 可算 **exact dead-ends** |
| **Tang et al. *Factored Action Spaces for Healthcare* (NeurIPS 2022)** | 利用 action 可分解 (fluid × vaso) 做 factored 學習，提升 sample efficiency | ⭐ 我們的 25 = 5×5 動作**天生 factored** |
| Gottesman et al. *Guidelines for RL in healthcare* (Nature Med 2019) | 非 method，是醫療 RL 評估陷阱的 warning paper | 支撐我們 multi-metric / exact V* 的論述 |
| 通用 offline RL：BCQ (2019) / CQL (2020) / BEAR (2019) / Rashidinejad pessimism (2021) | behavior-constraint / conservatism / pessimism | ⭐ 最契合，見 §1 |

**歸納**：同類工作的「RL 主動性」集中在三條線——**(a) offline RL / pessimism、(b) dead-end / risk-aware learning、(c) factored action space**。三者都能在我們 tabular 環境上做，且都有「真 dynamics → exact 評估」的加分。

---

## 3. 候選方向（每個都比 ablation 更 RL-active）

每個標註 **method 型 / question 型**、成本、與現有成果的關係。

### 候選 A — OOD-action 方法光譜（method 型；richness 最高）⭐⭐⭐

把 hard masking 放進一條光譜，與真正的 offline RL 方法比較，全部用 exact distance-to-V* 衡量：

```
vanilla(無約束) → penalty baseline → CQL-style pessimism
   → count-based pessimistic VI (LCB) → BCQ-style behavior constraint → hard masking
```

- **主圖**：x 軸 = 給定 dataset 大小 N（從真 MDP 抽 N 筆 transition 建 empirical MDP），y 軸 = distance-to-V*；每方法一條線。展示「資料越少，pessimism/constraint 越重要」。
- **強處**：吸收現有 masking 當 baseline、真正的 RL 方法實作、用上 exact V* 這個獨特優勢、連結熱門 offline RL 文獻。
- **成本**：中（一下午可先做 2–3 個方法 prototype）。
- **風險**：方法最多，但每個 tabular 版都不難。

### 候選 B — Ground-truth dead-ends（question 型；最獨特）⭐⭐⭐

因 reward = survival indicator 且 γ=1，**V*(s) 恰為 state s 的最大存活機率**。可**精確算出**：
- 哪些 state 是 dead-end（連 optimal policy 存活率都趨近 0）
- 哪些 action 把病人推進 dead-end
- expert / 學到的 policy 在 dead-end 附近浪費多少 mass

再做 **dead-end-aware learning**（對通往 dead-end 的動作加懲罰）看是否改善。

- **強處**：Fatemi 在真實 sepsis 上只能「估計」dead-ends，我們能算 **exact** → 清楚的新貢獻角度；實驗故事性強。
- **成本**：中。
- **風險**：framing 要小心，仍強調 benchmark-internal、非臨床判斷。

### 候選 C — Factored action space（method 型；最快最乾淨）⭐⭐

動作 = 5 fluid × 5 vasopressor。實作 factored Q-learning（Q 分解到兩子動作）對比 flat Q-learning，量 **sample efficiency**（episodes-to-threshold）。

- **強處**：factorization 環境內建、Tang et al. 已證明在 sepsis 有效、乾淨的「method + sample-efficiency」故事、RL 味十足。
- **成本**：低（最可能一下午跑出初步結果）。
- **風險**：低；但環境太小，effect size 可能偏小，需實測。

### 次要候選（先了解即可）

- **Pessimism 在 imitation↔RL 間插值**（Rashidinejad）：實為候選 A 的理論框架，可合併。
- **Model-based vs model-free sample efficiency**：已有 Dyna-Q 可順手做，但偏教科書。
- **Distributional / risk-sensitive RL**：return 是 Bernoulli，資訊量低，**不建議**。
- **Exploration bonus**：環境太小太好解，exploration 非瓶頸，**不建議**。

---

## 4. Claude 的建議主線

以「**最終結果豐富度**」為目標、且不一定取代現有題目：

> **主線升級為候選 A（OOD-action 方法光譜）**，把現有 masking 結果當光譜上一個點；若有餘力，**加候選 B（exact dead-ends）當獨立 analysis 章節**。

升級後 paper 從「我發現 mean imputation 的毛病」變成：

> 「ICU-Sepsis 是能 exact 評估 offline-RL OOD-action 處理的 testbed；我們系統比較 hard masking / pessimism / behavior-constraint，並（利用已知 dynamics）首次精確刻畫 dead-ends。」

→ 同時具 **method 主動性** 與 **獨特實驗**，遠比純 ablation 豐富，且**幾乎全部複用現有的 V* / Vπ / Q-learning 程式**。

---

## 5. Claude 的初步實作順序（待與 codex 合併）

| 排名 | 方向 | 理由 | 成本 |
|---|---|---|---|
| 1 | 候選 C（factored） | 最快驗證可行性、低風險、乾淨 method 故事 | 低 |
| 2 | 候選 A（OOD spectrum） | richness 最高、吸收現有成果、主線 | 中 |
| 3 | 候選 B（exact dead-ends） | 最獨特、加分章節 | 中 |

**先 prototype 順序建議**：C（驗證可行性）→ A（主線）→ B（加分）。

---

## 6. 與現有程式的銜接點

現有：`src/env_utils.py`(V*/Vπ/distance-to-V*)、`src/tabular_rl.py`(Q/SARSA/Dyna-Q + use_mask)、`src/policies.py`、`src/evaluate.py`、`src/analysis.py`。

- 候選 A：新增「從真 MDP 抽 N 筆建 empirical MDP」工具 + pessimistic VI / CQL-tabular / BCQ-tabular 更新；評估直接用既有 distance-to-V*。
- 候選 B：用既有 V*（= 最大存活機率）直接定義 dead-ends；新增 dead-end penalty 到 Q-update。
- 候選 C：在 `tabular_rl.py` 加 factored Q 表示與更新；評估用既有 episodes-to-threshold / distance-to-V*。

---

## 7. 待確認

1. 文獻年份/venue 投稿前需 web 查證（避免重造、拿正確 citation）。
2. 先 prototype 哪一個由使用者拍板（預設 C → A → B）。
