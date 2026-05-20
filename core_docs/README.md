# DRL Final Project — ICU-Sepsis 新題目 Project Hub

> **更新日期**：2026-05-20（題目轉向當日）
> **Submission deadline**：2026-05-25 23:59（**剩 5 天**）
> **目標 paper**：4–8 頁 NeurIPS 2026 template，雙盲匿名，英文，可重現 source code
>
> 本目錄是組員的 single source of truth。讀完本 README + 一份指定 detail 文件就能開工。

---

## 1. 現在新題目是什麼？

**Action Admissibility Matters: A Systematic Study of Inadmissible-Action Handling and Action Masking on the ICU-Sepsis Benchmark**

一句話總結：把 [ICU-Sepsis (Choudhary et al., RLC 2024)](https://arxiv.org/abs/2406.05646) 當成 medical RL benchmark，系統比較它 v2 提供的三種 `inadmissible_action_strategy` 與 *是否使用 action masking* 對 tabular RL 演算法（Q-learning / SARSA / Dyna-Q）的 performance、safety proxy、sample efficiency、stability 的影響，並提出一個 multi-metric evaluation protocol。

**這不是臨床建議，是 benchmark-level algorithmic analysis。** 所有 paper 中的 metric 都會明標 "benchmark-internal" / "safety proxy"。

---

## 2. 為什麼放棄原本的衛星題目？

原本 MARL on LEO satellite topology 題目被放棄，因為：

- 太多 topology / traffic / reward / communication constraint / baseline fairness 設定需要前置測量
- 我們低估了建立 + 校準實驗環境的成本
- 5 天內無法產生 reviewer 會買單的穩定實驗結果

---

## 3. 為什麼 ICU-Sepsis 比較適合 5 天 project？

| 痛點 | LEO MARL | ICU-Sepsis |
|---|---|---|
| 環境是否現成 | ❌ 要自建 | ✅ 一個 `pip install` 就 ready |
| 訓練時間 | GPU × hours/days | CPU × seconds/minutes |
| baseline 有沒有 | 要自己 tune | ✅ Random / Expert / Optimal 已內建 |
| oracle 比較 | ❌ 沒有 | ✅ Value Iteration 給精確 V* |
| Action constraint knob 是否現成 | ❌ | ✅ `inadmissible_action_strategy` 三種 mode + `info['admissible_actions']` |
| 原 paper 已做的 ablation | 不適用 | 原 paper **只 evaluate `mean` strategy** — 我們的 novelty 空間 |
| Reviewer-friendly | 多 setting 要 defend | 全部 ablation cell 都 well-defined |
| Medical claim 風險 | 沒（無關 medical） | 需要主動 disclaim（已預先規劃 disclaimer） |

**最關鍵**：我們的 contribution 不需要靠「打敗 SOTA」或「重新建環境」，只需要做原 paper 沒做的 ablation。這在 5 天 budget 下 sufficient。

---

## 4. 推薦的 paper direction

**Direction 1：Action Admissibility & Inadmissible Action Handling**（詳 [`03_candidate_project_directions.md`](03_candidate_project_directions.md)）

主要 contribution（已在 [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md) §5 寫好）：

1. **首次系統比較** ICU-Sepsis-v2 三種 `inadmissible_action_strategy`（mean / terminate / raise_exception）。
2. **首次** 把 `info['admissible_actions']` 拿來當 Q-learning / SARSA / Dyna-Q 的 action mask 並做 ablation。
3. **Multi-metric evaluation protocol**：除了 survival rate，引入 distance-to-V* / inadmissible-action rate / policy-agreement-with-expert 三個 metric 並 release scripts。

**為什麼選這個**：novelty 強、reviewer 風險低、實驗在 CPU 秒級、5 天有極大 buffer。詳見 [`03_candidate_project_directions.md`](03_candidate_project_directions.md) §「推薦」段。

---

## 5. 目前要先讀哪些文件（順序）

| 順序 | 文件 | 對象 | 預估閱讀時間 |
|---|---|---|---|
| 1 | **本 README** | 全員 | 5 min |
| 2 | [`00_course_requirement_summary.md`](00_course_requirement_summary.md) | 全員（每人必讀） | 10 min |
| 3 | [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md) | 全員 | 20 min |
| 4 | [`05_five_day_execution_schedule.md`](05_five_day_execution_schedule.md) | 全員（找到自己被分配的 task） | 15 min |
| 5 | [`01_repo_understanding.md`](01_repo_understanding.md) | coding lead (A) + experiments lead (B) | 30 min |
| 6 | [`02_related_work_notes.md`](02_related_work_notes.md) | paper-writing lead (C) | 30 min |
| 7 | [`03_candidate_project_directions.md`](03_candidate_project_directions.md) | 想了解為什麼選 Direction 1 的人 | 15 min |

> 不要直接跳去寫 code 前，至少先讀 1、2、3。

---

## 6. 接下來 12 小時誰該做什麼

對應 [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md) §16 與 [`05_five_day_execution_schedule.md`](05_five_day_execution_schedule.md) Day 1。

| 角色 | 接下來 12 小時要做的事 |
|---|---|
| **M（你 / project lead）** | (1) Install `icu_sepsis` + `icu_sepsis_helpers`，跑 `quickstart.py` 與 `get_baselines.py -v 2`，比對 README 數字；(2) 在 `core_docs/setup_log.md` 記錄 Python 版本與得到的數字；(3) 確認全組 OpenReview 帳號 active；(4) 把 preliminary curve（A 跑出來的）貼群組；(5) 預訂 anonymous GitHub URL（anonymous.4open.science）。 |
| **A（RL coding lead）** | (1) 建 `icu_sepsis_project/` 目錄（README、requirements、src/、scripts/、configs/）；(2) 寫 `src/env_utils.py`、`src/evaluate.py`、`src/tabular_rl.py`（先把 Q-learning 寫好，有 `use_mask` kwarg）；(3) 寫 `configs/default.yaml`；(4) 跑 Q-learning + mean + mask=off / mask=on 各 5 seeds × 50k eps。 |
| **B（experiments / plotting）** | (1) 寫 `src/analysis.py`：`distance_to_Vstar`、`agreement_with_expert`、`unsafe_rate_per_sofa_bucket`；(2) 把 A 跑出的 JSON 整理成 preliminary 學習曲線（mask-on vs mask-off）；(3) 把 figure 存 `figures/preliminary.png`。 |
| **C（paper writing）** | (1) OverLeaf 開新 project import [NeurIPS 2026 template](https://neurips.cc)，line number 開啟；(2) 把 [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md) §12 的 paper outline section 標題打進 `main.tex`；(3) 把 [`02_related_work_notes.md`](02_related_work_notes.md) §E.1 的 Related Work 草稿移到 `main.tex`；(4) 把 7 個 main citation 的 full BibTeX 補進 `references.bib`；(5) 在 Day 1 內 verify [`02`](02_related_work_notes.md) 中標 "未驗證" 的兩篇真實 venue。 |
| **D（reviewing + extra hands）** | (1) 跟 C 對齊 paper skeleton；(2) 幫忙 A / B 任何 stuck 的環節；(3) Day 5 內部 review 時擔任 R1 reviewer 角色。若團隊只有 4 人沒有 D，這些 task 分散給 M。 |

---

## 7. Minimum Viable Paper（時間真的不夠的底線）

詳見 [`04_project_plan_icu_sepsis.md`](04_project_plan_icu_sepsis.md) §14。**MVP 必有的結果**：

- ✅ **B0**：Baseline reproduction（Random / Expert / Optimal）vs paper 數字一致 → Tbl 1
- ✅ **G1 (partial)**：Q-learning × {mean, terminate} × 5 seeds × 50k eps → 部分 Tbl 2 + 半 Fig 1
- ✅ **G2 (partial)**：Q-learning × {mask on, off} × mean strategy × 5 seeds × 50k eps → 部分 Tbl 2 + 半 Fig 1
- ✅ **Distance-to-V*** 與 **unsafe-action rate** 兩個 metric column
- ✅ Paper 4 頁、含 Intro / Related Work / Method / Experiments / Discussion / Limitations / Conclusion

→ 這個 MVP 仍然構成完整 NeurIPS paper，contribution 1 + 3 完整成立。SARSA / Dyna-Q / DQN / 任何 stretch goal 都可以拿掉。

---

## 8. 重要日期

| 日期 | 事件 | 對應 doc 段 |
|---|---|---|
| **2026-05-20**（今天） | 題目轉向；Day 1 開始 | [05 Day 1](05_five_day_execution_schedule.md) |
| 2026-05-25 23:59 | **Paper submission deadline** | [05 Day 5](05_five_day_execution_schedule.md) |
| 2026-05-29 23:59 | Review submission deadline（每人 review 一篇） | [00 §1](00_course_requirement_summary.md) |
| 2026-06-01 23:59 | Rebuttal deadline | [05 截止日後 reminder](05_five_day_execution_schedule.md) |
| 2026-06-05 23:59 | Discussion deadline | 同上 |
| 2026-06-08 23:59 | Decision notification（accept oral / poster） | 同上 |
| 2026-06-15 | 課堂 oral / poster session | 同上 |

---

## 9. 重要原則（給未來的自己看）

1. **不要誇大醫療意義**。我們是 benchmark-level algorithmic analysis，不是 clinical recommendation。
2. **不要設計太大的題目**。剩 5 天，優先 tabular RL + ablation + analysis。
3. **所有 claim 要有 evidence**。沒實驗就標 speculation；要更多實驗就明確列出。
4. **所有文獻要查證**。preprint / GitHub / blog 要清楚標示來源性質。詳見 [02](02_related_work_notes.md) 的「未驗證」記號。
5. **所有文件以繁體中文為主**；paper 是英文；技術詞保留英文。
6. **submit 不要拖到 5/25 晚上**。Day 5（5/24）就要把 PDF 上 OpenReview，留一天 buffer。

---

## 10. 待辦：本 doc 之外還要追加的小檔案（隨開工自然產生）

- `core_docs/setup_log.md`：Python 版本、套件版本、install steps、得到的 baseline 數字。Day 1 內由 M 建立。
- `core_docs/scope_decisions.md`：每天 21:00 standup 後，把當天 cut-scope 的決定記下來（哪些 task 砍了、為什麼、預期影響）。Day 1 開始累積。
- `core_docs/reviewer_anticipated_questions.md`：寫 paper 期間，把預想的 reviewer 質疑與我們的 defense 寫下來；Day 5 寫 rebuttal 時很有用。

---

## 11. 一句話開工指令

> **「現在 6 個 detail document 已經 ready，task assignment 已分配。15 分鐘讀完本 README、`00_course_requirement_summary.md`、`04_project_plan_icu_sepsis.md`，看到自己的角色就動手。Day 1 的目標是 baseline 重現 + 1 張 preliminary curve；不要管 SARSA / Dyna-Q / DQN。」**
