# 05. Five-Day Execution Schedule

> **時程錨點**：今天 = 2026-05-20。**Submission deadline = 2026-05-25 23:59**（5 天）。
> 後續還有 5/29 review、6/1 rebuttal、6/5 discussion、6/15 oral/poster——本文件只覆蓋 paper 截稿前的 5 天。
>
> 假設條件：團隊 3–5 人；至少 1 人能 full-time、其餘人 half-time。
> 假設硬體：每個組員一台筆電 CPU；至少 1 台有 GPU 是 nice-to-have（給 N1 DQN 用，可選）。
>
> 角色代號：
> - **M**：你（main owner，project lead）
> - **A**：teammate A（RL coding lead）
> - **B**：teammate B（experiments / plotting）
> - **C**：teammate C（paper writing / related work）
> - **D**：teammate D（reviewing + presentation prep + extra hands；若無此人，任務分散）
>
> Priority 標記：
> - **MUST**：必做，沒做就交不出 paper
> - **NICE**：時間夠就做，否則跳過
> - **RISKY**：值得試但可能失敗，要設 fallback

---

## Daily Standup 規範

每天 09:00 與 21:00 各一次 15 分鐘 sync：
- 我昨天做完什麼
- 我今天要做什麼
- 我卡在哪
- 是否需要把某個任務 reassign

任何 task **超過預估時間 50%** 一律先回報、討論 cut scope。

---

## Day 1 — 2026-05-20（Wed）：環境就緒 + Baseline 重現 + Skeleton

### 目標
1. **環境** install 成功 + repo paper 數字重現（B0）
2. **Code skeleton** 雛型完成（env_utils / evaluate / Q-learning）
3. **Paper skeleton** OverLeaf 開好
4. **Related Work** 草稿（從 [02](02_related_work_notes.md) 段落 E.1 移過去 + Day 1 內補完 Bib entries）

### Coding tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Install icu_sepsis + icu_sepsis_helpers，跑 quickstart | MUST | M | 30m | — | `setup_log.md` |
| 跑 `get_baselines.py -v 2`，與 README 數字比對 | MUST | M | 30m | install | Tbl 1 of paper |
| 建 `icu_sepsis_project/` 目錄結構（README, requirements, src/, scripts/, configs/） | MUST | A | 60m | — | repo skeleton commit |
| 寫 `src/env_utils.py`：`make_env(strategy, seed)`、`get_dynamics`、`compute_Vstar`、`compute_Vpi` | MUST | A | 2h | install | 模組能 import |
| 寫 `src/evaluate.py`：rollout n eps、計算 return / ep_len / unsafe_rate_deployed | MUST | A | 1.5h | env_utils | 模組能 import |
| 寫 `src/tabular_rl.py`（先 Q-learning + mask kwarg） | MUST | A | 2h | env_utils, evaluate | Q-learning 能跑 |
| 寫 `configs/default.yaml` + CLI loader | MUST | A | 30m | — | YAML schema |
| `tests/test_sanity.py`：env reset/step、VI 收斂、Q-learning ≥ 0.75 return | MUST | M | 1h | tabular_rl | pytest 通過 |

### Experiment tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| **B0 baseline reproduction** Random / Expert / Optimal（50k eps × 5 seeds） | MUST | M | 30m | env_utils | Tbl 1 raw JSON |
| **G1 cell 1**：Q-learning + mean + mask=off × 5 seeds × 50k eps | MUST | A | 1h | tabular_rl | results JSON |
| **G2 cell 1**：Q-learning + mean + mask=on × 5 seeds × 50k eps | MUST | A | 1h | tabular_rl | results JSON |

### Analysis / plotting tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 寫 `src/analysis.py`：distance_to_Vstar / agreement_with_expert / unsafe_rate_per_sofa_bucket | MUST | B | 2h | env_utils | 模組能 import |
| 畫 preliminary 學習曲線（mask-on vs mask-off 2 條線 + shaded CI） | MUST | B | 1h | analysis | `figures/preliminary.png` |
| 跑 `B0` 結果丟進 `make_tables.py`，產出 Tbl 1 raw | NICE | B | 30m | analysis | `tables/tbl1.tex` |

### Writing tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| OverLeaf 開 project，import NeurIPS 2026 template，line number on | MUST | C | 30m | — | OverLeaf URL（記 in core_docs/setup_log.md） |
| 把 paper outline §12 from [04](04_project_plan_icu_sepsis.md) 的 section 標題打進 `main.tex` | MUST | C | 30m | overleaf | main.tex skeleton |
| Related Work 段落從 [02 §E.1](02_related_work_notes.md) 移植進 `main.tex` | MUST | C | 1h | main.tex | Related Work v0 |
| `references.bib`：Day 1 內補完 7 個 main citation 的 full BibTeX | MUST | C | 1h | — | references.bib v0 |
| Verify [02 §A.2-§D] 中標 "未驗證" 的兩篇（sciltp CPQ-IQL、Springer 2025 offline-safe）真實 venue / year | MUST | C | 1h | — | Updated 02 file |

### Coordination tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 全員確認 OpenReview 帳號 active | MUST | M | 30m | — | screenshot 群組 |
| 把 [04 §16 第 9–12 小時] 的 preliminary curve 圖貼到群組 | MUST | M | 5m | preliminary fig | group msg |
| 設 anonymous GitHub 上傳 placeholder（anonymous.4open.science 或 anonymous-github.io） | MUST | M | 30m | — | URL |
| 確認 5 天執行表全員看過、沒人有衝突會議/考試 | MUST | M | 15m | — | group ack |

### End of Day 1 必達 milestone
- ✅ baseline numbers reproduced（Tbl 1 raw 完成）
- ✅ 1 張 preliminary learning curve（mask on vs off）
- ✅ paper skeleton + Related Work v0
- ✅ 全組 OpenReview ready

### Day 1 fallback
- 若 install 失敗 / 環境衝突：A 改用 conda env，記錄成功 setup steps；如果整天都掛在 install，當天結束改用 Docker / 在 Colab 上 setup。
- 若 baseline 重現結果偏離超過 5%（例如 Random < 0.7）：先檢查 seed / num_episodes；若仍偏，記錄並回報，使用我們自己的結果作 paper baseline 但 disclaim。

---

## Day 2 — 2026-05-21（Thu）：Tabular RL 全套 + Strategy / Mask 全 cell

### 目標
1. **G1 完整 6 cells** 跑完（{Q-learning, SARSA, Dyna-Q} × {mean, terminate}）
2. **G2 完整 6 cells** 跑完（{Q-learning, SARSA, Dyna-Q} × {mask on, mask off}, mean strategy 下）
3. **3 個演算法都能 reproduce 出合理數字**
4. **Method section** 完成草稿

### Coding tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 擴 `tabular_rl.py`：加 SARSA（masked / unmasked） | MUST | A | 1.5h | D1 q-learning | 能跑 |
| 擴 `tabular_rl.py`：加 Dyna-Q n=5（masked / unmasked） | MUST | A | 2h | D1 q-learning | 能跑 |
| `scripts/run_tabular_rl.py`：吃 YAML、輸出 JSON | MUST | A | 1h | tabular_rl | 一鍵跑 |
| `scripts/run_strategy_ablation.py`：sweep over `{mean, terminate}` | MUST | A | 30m | run_tabular_rl | sweep |
| `scripts/run_action_masking_ablation.py`：sweep over `{on, off}` | MUST | A | 30m | run_tabular_rl | sweep |
| **S0**：`raise_exception` edge case sanity（random + Q-learning short run，看 crash 行為） | MUST | M | 1h | env_utils | 1 段 Appendix 內容 |

### Experiment tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 平行跑 **G1**：3 algos × 2 strategies × 5 seeds × 50k eps = 30 runs | MUST | B | 3h wall-time | run_tabular_rl | 30 JSON |
| 平行跑 **G2**：3 algos × 2 masking × 5 seeds × 50k eps = 30 runs（mean strategy；與 G1 部分 cells 重疊，共需 ≈ 18 新 run） | MUST | B | 2h wall-time | run_tabular_rl | 18 新 JSON |
| 跑 `terminate + mask=on` 與 `terminate + mask=off` 共 6 cells × 5 seeds = 30 runs（補滿 2D matrix） | NICE | B | 2h wall-time | run_tabular_rl | 30 JSON |

> 平行：3 隊員每人 7–10 runs，用 `joblib` / `multiprocessing` per machine。

### Analysis / plotting tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 整理所有 runs → `results/master.csv`（一行一個 run） | MUST | B | 30m | runs | master.csv |
| 計算 distance-to-V*、agreement、unsafe rate（per run） | MUST | B | 1h | master.csv, analysis | 加列 |
| Draft **Fig 1**（3-panel learning curves，每 panel 4 條線） | MUST | B | 1.5h | master.csv | fig1.pdf |
| Draft **Fig 3**（training-time unsafe rate over episodes） | NICE | B | 1h | master.csv | fig3.pdf |

### Writing tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Method §4：Q-learning / SARSA / Dyna-Q pseudo + masked variant pseudo | MUST | C | 2h | — | Method v0 |
| §3 環境描述（716 state, 25 action, γ=1, 3 strategies, admissible set 統計） | MUST | C | 1.5h | repo understanding | §3 v0 |
| Define 4 個 metric 公式 in §3.x | MUST | C | 1h | — | metric subsection |
| Polish Related Work v0 → v1（加入 missing citations） | NICE | C | 1h | — | RW v1 |

### Coordination tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 09:00 standup：誰跑哪些 runs，避免衝突 | MUST | M | 15m | — | sync |
| 21:00 standup：Day 2 進度檢視，是否需要 cut scope | MUST | M | 15m | — | sync |
| 把 Fig 1 preliminary 貼群組 | MUST | M | 5m | fig1 draft | group msg |

### End of Day 2 必達 milestone
- ✅ 至少 G1 (6 cells) × 5 seeds + G2 (Q-learning 部分) × 5 seeds JSON 都在 `results/`
- ✅ 1 張 Fig 1 雛型（即使排版未調好）
- ✅ Method §4 + Env §3 草稿完成
- ✅ S0 raise_exception sanity 已記錄

### Day 2 fallback
- 若 SARSA 或 Dyna-Q 沒寫完：只跑 Q-learning（這已是 minimum viable）；SARSA / Dyna-Q 在 paper 中改寫成 "future work"。
- 若 30+ runs 超時：把 num_episodes 從 50k 降到 30k；paper 中明寫 budget。

---

## Day 3 — 2026-05-22（Fri）：Multi-seed 收尾 + Stretch + Experiments section

### 目標
1. **完整 ablation matrix**（terminate + mask 的 4 cells 完成）
2. **Sample efficiency curves**（5k/10k/25k/50k 切片）
3. **Tbl 2 主表完成**
4. **Experiments section §5** 完整初稿
5. **Stretch goals**：N3（SOFA-bucket）+ N4（policy agreement matrix）

### Coding tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 補 sample-efficiency snapshot logger（在 5k/10k/25k/50k 各做一次 50k-episode eval） | MUST | A | 1.5h | tabular_rl | per-run logs |
| 寫 `scripts/make_tables.py`：吃 master.csv → Tbl 1 / Tbl 2 LaTeX | MUST | A | 1.5h | master.csv | tbl1.tex, tbl2.tex |
| N3 stretch：`src/analysis.py` 加 SOFA-bucket 分析 function | NICE | A | 1h | analysis | function |
| N4 stretch：`src/analysis.py` 加 expert agreement matrix | NICE | A | 30m | analysis | function |
| N1 stretch（**RISKY**）：`src/dqn.py` 簡單 DQN with mask | RISKY | A or D | 4h | — | dqn.py |

### Experiment tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 補跑 terminate + masking on/off 4 cells × 5 seeds = 20 runs（如 Day 2 沒做完） | MUST | B | 2h | run scripts | 20 JSON |
| Sample efficiency 切片 evaluation（all cells, at 5k/10k/25k/50k） | MUST | B | 1.5h | logger | per-run snapshots |
| Aggregate 5-seed CI → master.csv 加 std_return / std_distance 等 column | MUST | B | 30m | analysis | master.csv v2 |
| **N1 RISKY**：跑 DQN with mask × 3 seeds × 50k eps 過夜 | RISKY | B or A | overnight | dqn.py | 3 JSON |

### Analysis / plotting tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 畫 **Fig 2**：bar chart distance-to-V*（12 條件） | MUST | B | 1.5h | master.csv | fig2.pdf |
| 畫 **Fig 3**：training-time unsafe-rate over episodes（4 條線） | MUST | B | 1.5h | master.csv | fig3.pdf |
| **Tbl 2** 主表：rows = (algo, strategy, mask), cols = (return, ep_len, dist-V*, unsafe-rate, agreement, episodes-to-0.85) | MUST | B | 1.5h | make_tables | tbl2.tex |
| **Fig 4** stretch：per-SOFA-bucket unsafe rate bar | NICE | B | 1h | N3 | fig4.pdf |
| **Tbl 3** stretch：policy agreement matrix | NICE | B | 30m | N4 | tbl3.tex |

### Writing tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Experiments §5：5.1 setup / 5.2 baseline reproduction / 5.3 strategy ablation / 5.4 masking ablation / 5.5 sample efficiency / 5.6 stability | MUST | C | 4h | Fig 1–3, Tbl 1–2 | §5 v0 |
| Introduction §1 v0：motivation 段、contribution bullet | MUST | C | 1.5h | RW v1 | §1 v0 |
| Discussion §6 草稿：3 RQ 的答案 + 觀察 | MUST | C | 1h | results | §6 v0 |

### Coordination tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 09:00 standup | MUST | M | 15m | — | sync |
| 中午 12:00 內部 cut-scope 決定：哪些 stretch goal 砍掉、哪些保留 | MUST | M | 30m | progress | written decision |
| 21:00 standup + 全 paper section 點名（誰寫哪段、進度）| MUST | M | 30m | — | sync |
| 把 Fig 2 + Tbl 2 雛型貼群組 | MUST | M | 5m | drafts | group msg |

### End of Day 3 必達 milestone
- ✅ 完整 G1 + G2 ablation matrix（≥ 60 runs，5 seeds 每 cell）
- ✅ Fig 1, 2, 3 + Tbl 1, 2 都有 v1
- ✅ §3, §4, §5 全有 v0
- ✅ Cut-scope 決定已下：哪些 nice-to-have 留、哪些砍

### Day 3 fallback
- 若 DQN (N1) 沒成功：Appendix 寫「We attempted a DQN baseline; converged but did not surpass tabular masked-Q-learning within our budget; full details in Appx」。然後集中火力在 main story。
- 若 Tbl 2 結果不顯著（差異 < 0.005）：paper 不要 claim "significant"，改用 "consistent" / "directionally" wording；加強 distance-to-V* 與 unsafe-rate metric（這兩個 effect size 較大）。

---

## Day 4 — 2026-05-23（Sat）：Figures Finalize + Paper 主體完成

### 目標
1. **所有 figure / table 排版到位**（出版品質）
2. **Paper main content 全 section** 至少有 v1
3. **Introduction / Related Work / Discussion / Limitations 寫完**
4. **anonymous GitHub** 把 code dump 上去（初版）

### Coding tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Code cleanup：remove dead code、加 docstring、檢查無作者名 / 機構 / 真實 GitHub URL | MUST | A | 2h | all | clean repo |
| Polish `README.md`：how to install, how to reproduce each figure | MUST | A | 1.5h | — | repo README |
| Upload code to anonymous.4open.science（或 anonymous-github.io），記 URL | MUST | A | 30m | clean repo | anon URL |
| 確認 `make reproduce-fig1`, `reproduce-fig2`, `reproduce-tbl2` 等 Makefile target 可用 | NICE | A | 1h | — | Makefile |

### Experiment tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 若 Day 3 DQN 過夜跑成功：產生 Tbl 4 row | NICE | B | 30m | DQN runs | tbl4.tex |
| 重跑任何 stats 失敗的 cell（補 missing seeds） | MUST | B | 1h | — | filled cells |
| 整理 5-seed 95% CI computation；放進每張 figure 與 table | MUST | B | 1.5h | — | corrected stats |

### Analysis / plotting tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Figure 美化：統一字體 size、color palette（colorblind-friendly）、tight_layout、legend 位置、CI shading | MUST | B | 3h | fig1–3 | publication-ready |
| Table 美化：booktabs、單位、CI 寫法、bold best cell | MUST | B | 1.5h | tbl1–2 | publication-ready |
| 確認所有 figure 有 caption、所有 table 有 caption | MUST | B | 30m | — | LaTeX in main.tex |
| Sanity check：每張 figure 在 paper 內被 ref 過至少一次 | MUST | B | 30m | main.tex | grep result |

### Writing tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Introduction §1 v1：定稿 motivation、contribution bullet、disclaimer | MUST | C | 2h | RW v1 | §1 v1 |
| Related Work §2 v1：補完所有 citation、確認 venue/year | MUST | C | 1.5h | refs.bib | §2 v1 |
| Discussion §6 v1：解讀結果、回答 3 RQ、對 ICU-Sepsis user 的具體建議 | MUST | C | 1.5h | results | §6 v1 |
| **Limitations §7**：明確 disclaim medical claim、tabular only、5 seeds、SOFA bucket 是 coarse | MUST | C | 1h | — | §7 v1 |
| Conclusion §8 + future work | MUST | C | 30m | §6 | §8 v1 |
| Abstract v1：濃縮成 4–6 句 | MUST | C | 1h | all sections | abstract v1 |
| **Anonymity audit**：grep paper for 任何 name / NTU / 真實 GitHub URL / email | MUST | C | 30m | main.tex | clean PDF |
| Page count check：main content 4–8 頁 | MUST | C | 15m | main.tex | length report |

### Coordination tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 09:00 standup | MUST | M | 15m | — | sync |
| 14:00 mid-day check：figure & table 狀態，是否需要砍 stretch | MUST | M | 30m | progress | decision |
| 22:00 內部 dry run：M / D 從頭讀一遍 paper，找重大 bug / 文字 | MUST | M, D | 1h | paper v1 | review notes |
| 把全 paper PDF compile 一次貼群組 | MUST | M | 5m | compile | group msg |

### End of Day 4 必達 milestone
- ✅ Paper main.tex 完整 v1（每個 section 都有內容）
- ✅ 所有 figures / tables 排版完成
- ✅ Anonymity 已 audit
- ✅ Anonymous code repo URL 已 ready
- ✅ Length 在 4–8 頁 main content

### Day 4 fallback
- 若 Paper 超 8 頁：先砍 nice-to-have 內容（DQN, SOFA-bucket, expert init）；section 5 收緊 prose；移 redundant table 到 Appendix。
- 若 Paper < 4 頁：補 Appendix 細節進 main、或補 1 個 ablation row。

---

## Day 5 — 2026-05-24（Sun）：Polish + Submit Buffer Day

### 目標
1. **Polish writing**：grammar / consistency / cross-ref / 圖表 ref 正確
2. **內部 review × 2 輪**
3. **最終 anonymity check**
4. **OpenReview 提交**（不要拖到 5/25 才提交，給自己一個 buffer day）
5. **準備 Day 6 開始的 review work**（每位組員會被分配一篇 review）

### Coding tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 最終 repo 整理：清空 `__pycache__`、`.DS_Store`、stale outputs；確保 fresh clone 能 reproduce | MUST | A | 1.5h | clean repo | final repo |
| 確認 anonymous repo URL 仍 valid（重點：URL 在 paper 中要 click 得到） | MUST | A | 15m | — | confirmed |
| 把所有 figure 的 source script 路徑寫進 figure caption（reviewer-friendly） | NICE | A | 30m | — | captions |
| 跑 `tests/test_sanity.py` 最終確認 | MUST | A | 15m | — | pytest pass |

### Experiment tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 跑任何最後 missing cell（補 seed 等） | MUST | B | 30m | — | filled |
| 把 final master.csv copy 到 `paper/data/` 供 reproducibility | NICE | B | 15m | — | data dump |

### Analysis / plotting tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Color / font / size 最終 unify（用同一個 `plot_style.py`） | MUST | B | 1h | figs | uniform |
| 確認 PDF 圖在 black-and-white 印刷時仍可讀（避免依賴顏色） | NICE | B | 30m | — | grayscale test |
| 在 Appendix 補 ablation matrix 的完整 raw table | MUST | B | 1h | master.csv | appx_tbl.tex |

### Writing tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| **Round 1 internal review**：M, D 各 1 人 25 分鐘 close-read，標 typo / unclear / 邏輯漏洞 | MUST | M, D | 30m | paper v1 | review comments |
| C 根據 R1 修 paper → v2 | MUST | C | 2h | R1 | paper v2 |
| **Round 2 internal review**：另外 2 人 close-read | MUST | A, B | 30m | paper v2 | R2 comments |
| C 根據 R2 修 paper → v3 (final) | MUST | C | 1.5h | R2 | paper v3 |
| 最終 Abstract polish | MUST | C | 30m | v3 | final abstract |
| **Anonymity final audit**：grep "NTU", 真實名, "@gmail", repository.com URLs | MUST | C | 30m | v3 | audited |
| **OpenReview metadata** 準備：title、authors（用 anonymous emails 加進去）、keywords（≤ 5 個）、TL;DR（1 句）、abstract | MUST | M | 1h | v3 | metadata text |

### Submission tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| OverLeaf → 編譯 final PDF；page count 再確認；line number on 確認 | MUST | C | 30m | v3 | final.pdf |
| 一名代表上 OpenReview，填 submission form，上傳 PDF | MUST | M | 30m | final.pdf, metadata | submission |
| **截圖** submission confirmation 並貼群組 | MUST | M | 5m | submit | screenshot |
| 全組 confirm 自己出現在 author list | MUST | all | 5m | submit | confirms |

### Presentation prep（Day 6+ 才正式做，但 Day 5 開始準備）

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| Skim slide template (Google Slides 或 Keynote)，預定 6/15 oral 5 min / poster 1 page 結構 | NICE | D | 30m | — | rough outline |

### Coordination tasks

| Task | Priority | Owner | Time | Dep | Output |
|---|---|---|---|---|---|
| 09:00 standup | MUST | M | 15m | — | sync |
| **14:00 全員 paper 朗讀會**：把 paper main content 由 C 唸出來，全員聽完一遍找邏輯漏洞 | MUST | all | 1h | v2 | comments |
| 21:00 submission 完成後慶祝 + 提醒 review 工作 5/29 截止 | MUST | M | 15m | submit | sync |

### End of Day 5 必達 milestone
- ✅ PDF 已 submit 在 OpenReview
- ✅ Anonymous code repo 已 final
- ✅ Submission confirmation screenshot in 群組
- ✅ 全組知道 5/29 是 review 截止

### Day 5 fallback（最重要）
- 若 Day 4 結束 paper 還沒 v1 完整：**Day 5 早上 7:00 開緊急會議**，決定砍掉的內容；C 全天集中寫；其他人協助 polish。
- 若 OpenReview submission 卡關（系統 bug、帳號問題）：**5/25 早上 10:00 前一定要 submit**，留 13+ hr buffer 處理意外。**絕對不要 5/25 晚上才上傳**。

---

## 跨日全表總覽（用於 daily standup 對齊）

```
Day      Coding-MUST                Experiment-MUST            Plot-MUST                Writing-MUST
-------  -------------------------- -------------------------- ------------------------ -------------------------
Day 1    env_utils/eval/Q-learning  B0 + G1 cell1 + G2 cell1   prelim curve             OL template + RW + bib
Day 2    SARSA/Dyna-Q + scripts     G1 6 cells + G2 6 cells    Fig1 v0                  Method §4 + Env §3
Day 3    snapshot logger + tables   terminate+mask 4 cells     Fig2/3 v0 + Tbl2         Experiments §5 + Intro v0
Day 4    code cleanup + anon repo   补 missing seeds + CI       finalize figs/tables     Intro/RW/Discuss/Limit v1
Day 5    final clean + sanity       backfill missing data      style unify + appx tbl    Abstract + 2 review rounds + SUBMIT
```

---

## 預警 thresholds（必要時 escalate）

| 觸發條件 | Action |
|---|---|
| Day 1 結束時 baseline 還沒重現 | 隔天早上立刻找 TA 問 install 問題；同時用 Colab fallback |
| Day 2 結束時 G1 < 4 cells 完成 | 砍 SARSA & Dyna-Q，只跑 Q-learning（最小可行 MVP） |
| Day 3 結束時 Method/§3/§4 都還沒寫 | 全員 Day 4 至少撥 4 hr 寫作（暫停 stretch goals） |
| Day 4 結束時 paper main 還 < 4 頁 | 砍 Discussion 篇幅、移 detail 到 Appendix；保 Intro/Method/Exp/Concl 完整 |
| Day 5 中午仍未進入 R2 review | OpenReview 上 22:00 前一定要 submit，不能 stage paper polishing |

---

## 截止日後 reminder（不在本表內，但要 mark in 行事曆）

- **2026-05-29 23:59**：Review submission deadline。每位學生會被分到一篇 paper，寫 summary / strengths / weaknesses / score (1–6) / confidence (1–5)。記得用 major/minor 區分、numbered list。
- **2026-06-01 23:59**：Rebuttal deadline。**全組要排班**，因為 reviewer comments 可能在 5/29–5/30 才出，rebuttal 只有 3 天。
- **2026-06-05 23:59**：Discussion deadline。reviewers 可加分。
- **2026-06-08 23:59**：Decision notification。決定 oral / poster。
- **2026-06-15**：課堂上 oral / poster 報告。**Day 5 完 submit 後就要開始準備 slides / poster**，不要等到 6/8 才開始。
