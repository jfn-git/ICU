# 16. 給組員看的內部簡報

> 目標讀者：團隊成員  
> 目的：快速理解我們現在到底在做什麼、有哪些結果、paper 要怎麼寫、每個人可以認領什麼。  
> 注意：所有結果都是 **benchmark-internal**。`unsupported / inadmissible action` 指「資料支撐不足」，不是「醫學上錯誤」。  
> 主要來源：`core_docs/15_paper_story_spine.md`, `paper/main.tex`, `submission/README.md`, `results/*/summary.json`, `core_docs/reviewer_anticipated_questions.md`, `core_docs/11_literature_verified.md`

---

## 1. 30 秒總覽

**我們在做什麼？**  
我們研究 ICU-Sepsis benchmark 裡一個很容易被忽略的設定：當 agent 選到資料支撐不足的 action，也就是 `inadmissible / unsupported action`，環境預設的 `mean` strategy 會把它的 transition 補成「所有 admissible actions 的平均」。這讓 unsupported action 看起來像一個平均正常的選項，而不是一個需要被警惕的 OOD action。[來源: `core_docs/15_paper_story_spine.md`, `core_docs/06_project_plan_mean_imputation_hides_unsupported_actions.md`, `core_docs/11_literature_verified.md`]

**為什麼有趣？**  
Vanilla Q-learning 在這個預設下會大量部署 unsupported actions：大約 `87%` 的 non-terminal states 會選到 unsupported action；但 policy value `J=0.7855` 看起來又接近 Random `0.7801` / Expert `0.7818`，所以如果只看 survival-rate / return，很容易以為沒什麼問題。[來源: `results/penalty_sweep/summary.json`, `results/baselines/summary.json`, `core_docs/15_paper_story_spine.md`]

**一句話貢獻**  
我們把 ICU-Sepsis 的 inadmissible-action handling 重新詮釋成 offline RL 的 **OOD / low-support action problem**，利用 benchmark 的 exact V* 精準定位 failure 住在 behavior-level sampling，並比較 support penalty、CQL-style conservatism、hard mask 等一整條 remedy spectrum。[來源: `core_docs/15_paper_story_spine.md`, `submission/README.md`, `core_docs/11_literature_verified.md`]

---

## 2. 目前成果：Data + 圖

### 實驗總表

| 實驗 | 它回答什麼問題 | 關鍵數字 | 對應圖檔 | Main / Supplement |
|---|---|---|---|---|
| **Baseline** | 環境和 exact evaluation 有沒有對上原 paper？ | Random `0.7801`, Expert `0.7818`, Optimal `0.8751`，對齊 paper reference `0.78 / 0.78 / 0.88`。[來源: `results/baselines/summary.json`] | Table 1，目前沒有單獨圖。[來源: `submission/README.md`] | Main sanity check |
| **P1 Penalty sweep / OOD remedy spectrum** | support penalty 能不能替代 hard mask？ | Vanilla dist-V* `0.0896`, deploy unsupported `0.8707`; λ=0.1 dist `0.0831`, deploy unsupported `0.3871`; λ=1.0 deploy unsupported `0`, dist `0.0865`; hard mask dist `0.0693`, deploy unsupported `0`。[來源: `results/penalty_sweep/summary.json`] | `submission/figures/penalty_tradeoff.png` | **Main** |
| **T1 Component ablation + Q-leakage** | failure 到底住在哪裡？behavior、target、policy 哪個最重要？ | Behavior-only = full mask：dist `0.0693`, deploy unsupported `0`, Q-leakage `-0.7951`; vanilla Q-leakage `+0.4594`; target-only deploy unsupported `0.7691`; policy-only deploy unsupported `0` 但 Q-leakage 還是 `+0.4594`。[來源: `results/component_ablation/summary.json`] | `submission/figures/component_ablation.png` | **Main centerpiece** |
| **T2 Offline dataset-size sweep** | 如果模型不是已知，而是從 N 筆 expert transitions 估出來，naive mean-imputation 會怎樣？ | N=100k：naive overestimation `+0.2083`, dist `0.0935`, deploy unsupported `0.8569`; pessimistic dist `0.0688`, overest `+0.0488`; masked dist `0.0645`, deploy unsupported `0`。[來源: `results/offline_datasize/summary.json`] | `submission/figures/offline_datasize.png` | **Main / strong supplement** |
| **P2 Expert prior + admissible projection** | clinician/expert guidance 能不能幫忙？raw expert 是否也有 unsupported 問題？ | Expert inadmissible mass `0.1564`; raw expert prior dist `0.0736`, deploy unsupported `0.0788`, agreement `0.6048`; projected expert dist `0.0731`, deploy unsupported `0.0050`, agreement `0.6474`。[來源: `results/expert_prior/summary.json`] | `submission/figures/expert_prior_curve.png` | Supplement |
| **T3 Robustness** | 這是不是 Q-learning 單一怪癖？是不是只在 `mean` strategy 發生？ | Mean mask-off deploy unsupported：Q `0.8707`, SARSA `0.8606`, Dyna-Q `0.8443`; mean mask-on 都是 `0`; terminate mask-off 只剩約 `0.033–0.041`。[來源: `results/robustness/summary.json`] | `submission/figures/robustness.png` | Supplement |
| **P0 Dead-end / harm structure** | ICU-Sepsis 裡有沒有真正「怎麼做都會死」的 dead-end？ | hard dead-end `0`; min V* `0.1976`; secured states `427/713`; inadmissible one-step death risk `0.0323` > admissible `0.0226`; harmful actions 中 `58.6%` 是 inadmissible。[來源: `results/deadend/summary.json`] | `submission/figures/deadend_structure.png` | Supplement / honest calibration |

### 每個實驗一句白話

- **Baseline**：先證明我們的環境和 exact value 計算沒壞，數字對得上 benchmark。[來源: `results/baselines/summary.json`]
- **P1 Penalty sweep**：輕罰 unsupported actions 可以降低亂選，但硬性 behavior support control 才是 value 和 support trade-off 上最乾淨的解。[來源: `results/penalty_sweep/summary.json`, `submission/README.md`]
- **T1 Component ablation**：真正要修的是「訓練時不要讓 agent 去選 unsupported actions」；只修 target 或只修 final policy 都不夠。[來源: `results/component_ablation/summary.json`, `core_docs/15_paper_story_spine.md`]
- **T2 Offline sweep**：當 model 從有限資料估出來時，naive mean-imputation 會越來越高估自己；pessimism 和 masking 才比較可靠。[來源: `results/offline_datasize/summary.json`]
- **P2 Expert prior**：expert guidance 有幫助，但 raw expert 也不完全 support-respecting；投影到 admissible set 後比較乾淨。[來源: `results/expert_prior/summary.json`]
- **T3 Robustness**：換 SARSA / Dyna-Q 也看到同樣 failure；換成 `terminate` strategy 後 agent 會自然避開 unsupported actions，證明問題主要是 `mean` 的平均補值藏起來。[來源: `results/robustness/summary.json`]
- **P0 Dead-end**：原本想找 exact dead-end，但 ICU-Sepsis 沒有真正 dead-end；這是誠實負面結果，但仍揭示 inadmissible actions 有較高 one-step death risk。[來源: `results/deadend/summary.json`]

---

## 3. 對 Paper 的想像

### Working Title

**When Mean Imputation Hides Unsupported Actions: Diagnosing and Repairing an Out-of-Distribution Action Failure Mode in the ICU-Sepsis Benchmark**  
[來源: `core_docs/15_paper_story_spine.md`, `paper/main.tex`]

### 三層 Claim Stack

1. **Failure：`mean` strategy 藏起 unsupported-action failure**  
   Vanilla Q-learning 在 default `mean` strategy 下部署 unsupported actions 的比例約 `87%`，但 `J=0.7855` 接近 Random `0.7801` / Expert `0.7818`，所以單看 return 會錯過問題。[來源: `core_docs/15_paper_story_spine.md`, `results/penalty_sweep/summary.json`, `results/baselines/summary.json`]

2. **Mechanism：failure 住在 behavior-level sampling**  
   Component ablation 顯示 behavior-only mask 和 full mask 完全一樣好；target-only 幾乎沒解決 deploy unsupported，policy-only 只是最後部署時的繃帶，Q-table 仍被污染。[來源: `core_docs/15_paper_story_spine.md`, `results/component_ablation/summary.json`]

3. **Remedy：soft penalties / conservatism 有幫助，但 hard behavior support control 最乾淨**  
   Penalty λ 可以把 unsupported rate 壓低，但 distance-to-V* plateau；CQL-style conservatism 是最好的 soft remedy，但仍輸 hard mask。Offline sweep 進一步顯示 naive mean-imputation 會高估價值，pessimism/masking 比較穩。[來源: `results/penalty_sweep/summary.json`, `results/component_ablation/summary.json`, `results/offline_datasize/summary.json`]

### Paper 章節 Outline + 負責人

| Section | 要寫什麼 | 負責人 |
|---|---|---|
| Abstract | 問題 → exact V* testbed → failure / mechanism / remedy spectrum → benchmark-internal disclaimer。[來源: `paper/main.tex`, `core_docs/15_paper_story_spine.md`] | 負責人：____ |
| 1. Introduction | Medical RL benchmark 動機、ICU-Sepsis、mean-imputation hidden failure、三層 contributions。[來源: `paper/main.tex`, `core_docs/15_paper_story_spine.md`] | 負責人：____ |
| 2. Related Work | Sepsis RL、offline RL / OOD actions、invalid action masking、dead-end、evaluation pitfalls。[來源: `core_docs/12_related_work_draft.md`, `core_docs/11_literature_verified.md`] | 負責人：____ |
| 3. Background | ICU-Sepsis MDP、admissibility τ=20、`mean` strategy 公式、γ=1 ⇒ V*=survival probability。[來源: `paper/main.tex`, `core_docs/11_literature_verified.md`] | 負責人：____ |
| 4. Method | remedy spectrum：penalty、CQL-style conservatism、behavior/target/policy mask；metrics：dist-V*, deploy-unsupp, Q-leakage, overestimation。[來源: `paper/main.tex`, `submission/README.md`] | 負責人：____ |
| 5. Experiments | Baselines、Claim1 failure、Claim2 component ablation、Claim3 penalty + offline sweep、supplement results。[來源: `paper/main.tex`, `submission/README.md`, `results/*/summary.json`] | 負責人：____ |
| 6. Discussion | 為什麼 survival rate 會藏問題、Q16 known-dynamics 防守、Q17 random-admissible 防守、benchmark guidance。[來源: `core_docs/reviewer_anticipated_questions.md`, `core_docs/15_paper_story_spine.md`] | 負責人：____ |
| 7. Limitations | Tabular / known dynamics scope、5 seeds、data-support ≠ clinical correctness、no clinical recommendation。[來源: `paper/main.tex`, `core_docs/reviewer_anticipated_questions.md`] | 負責人：____ |
| 8. Conclusion | 一句話收束：inadmissible-action handling 應該被報告，不該留給 hidden default。[來源: `paper/main.tex`] | 負責人：____ |

### Deadline 時間線

| 時間 | 目標 |
|---|---|
| **05/22 晚上** | 確認 story spine、分工、figures 是否都能放進 paper。 |
| **05/23** | 完成 Introduction / Related Work / Method / Experiments 初稿；補 overview schematic 和 per-seed scatter。 |
| **05/24** | 全文 polish、縮頁數、檢查 citation、補 Discussion / Limitations 攻防。 |
| **05/25 23:59 前** | OpenReview submission deadline；不要拖到最後一小時。[來源: `core_docs/05_five_day_execution_schedule.md`, 課程規定脈絡] |

---

## 4. 潛在攻擊 vs 防守

| 攻擊一句 | 白話防守一句 |
|---|---|
| **(a) 這是 tabular，不是 deep RL，會不會不符合課程？** | ICU-Sepsis 本身就是 RLC/RLJ 2024 的 tabular RL benchmark；我們研究的是 offline RL 裡 OOD-action failure 的可測量版本，不是只跑玩具 Q-learning。[來源: `core_docs/reviewer_anticipated_questions.md`, `core_docs/11_literature_verified.md`] |
| **(b) Novelty 不就是 action masking 嗎？** | 不是。Masking 只是 remedy spectrum 的一端；我們真正做的是：指出 `mean` imputation 藏 failure、用 component ablation 定位 failure 住在 behavior sampling、用 Q-leakage 和 offline sweep 解釋 mechanism。[來源: `core_docs/15_paper_story_spine.md`, `results/component_ablation/summary.json`, `results/offline_datasize/summary.json`] |
| **(c) Q16：known dynamics / exact V* 會不會很 toy？** | Exact V* 是 measurement instrument，不是炫耀「我們最佳化 toy policy」。一般 healthcare RL 的問題是 OPE 很吵；這裡剛好能把 OOD-action failure 乾淨量出來。[來源: `core_docs/reviewer_anticipated_questions.md` Q16] |
| **(d) Q17：inadmissible action 等於 random admissible，所以不是無害嗎？** | 正因為它等於 random admissible，才有成本：random admissible 比 best admissible 差。Vanilla Q-learning 的 `J=0.7855` 幾乎等於 Random `0.7801`，而 hard mask 到 `0.8058`；這不是 label 問題，是 value cost。[來源: `core_docs/reviewer_anticipated_questions.md` Q17, `results/penalty_sweep/summary.json`, `results/baselines/summary.json`] |
| **(e) 只有 5 seeds 會不會太少？** | 我們不把結論壓在小 return 差異上，而是壓在大 support diagnostics：deploy unsupported `0.8707 → 0`，Q-leakage `+0.4594 → -0.7951`，這些效果很大；appendix 可放 per-seed scatter。[來源: `results/component_ablation/summary.json`, `core_docs/15_paper_story_spine.md`] |
| **(f) 會不會過度醫療宣稱？** | 我們全程只說 benchmark-internal；`unsupported` 是資料支撐不足，不是醫學錯誤；不說 clinically safer、不說 improved patient survival。[來源: `submission/README.md`, `core_docs/15_paper_story_spine.md`, `paper/main.tex`] |
| **(g) ICU-Sepsis 原 paper 不是做過 action-removal robustness 嗎？** | 有，但它看的是 return robustness；因為 `mean` 會把 inadmissible 補成平均，return 本來就不敏感。我們看的是 selection rate、dist-V*、Q-leakage、remedy spectrum，問題不同。[來源: `core_docs/11_literature_verified.md` Precise positioning vs ICU-Sepsis paper, `core_docs/reviewer_anticipated_questions.md` Q17] |

---

## 5. 還缺什麼 / 組員可認領任務

| 任務 | 要做什麼 | 為什麼重要 | 負責人 |
|---|---|---|---|
| **Introduction prose** | 把 `paper/main.tex` 的 TODO 寫成流暢故事：medical RL benchmark → ICU-Sepsis → `mean` hidden failure → OOD-action framing → contributions。[來源: `paper/main.tex`, `core_docs/15_paper_story_spine.md`] | 這是讀者第一眼理解我們是不是有貢獻的地方。 | 負責人：____ |
| **Related Work prose** | 從 `core_docs/12_related_work_draft.md` 搬進 paper，壓到 4–5 段，包含 BCQ/BEAR/CQL/PEVI、invalid masking、Fatemi dead-end、Gottesman evaluation。[來源: `core_docs/12_related_work_draft.md`, `core_docs/11_literature_verified.md`] | 防守 novelty：我們不是發明 OOD RL，而是在 ICU-Sepsis exact-V* testbed 上做新診斷。 | 負責人：____ |
| **Discussion prose** | 特別寫 Q16 / Q17：exact V* 是 measurement instrument；random admissible 不是無害而是成本；原 paper B.3 和我們不同。[來源: `core_docs/reviewer_anticipated_questions.md`, `core_docs/11_literature_verified.md`] | Reviewer 最可能打這裡，要先在 main text 擋住。 | 負責人：____ |
| **Overview 圖** | 做一張 schematic：τ=20 → Adm(s) → mean imputation → vanilla samples/updates unsupported actions → Q-leakage → remedy spectrum → exact metrics。[來源: `core_docs/15_paper_story_spine.md`] | 讓非作者一眼懂整篇，不然七組實驗會看起來散。 | 負責人：____ |
| **Per-seed scatter / uncertainty** | 為 main figures 補 per-seed scatter 或 mean±95% CI：penalty tradeoff、component ablation、offline sweep。[來源: `core_docs/15_paper_story_spine.md`, `results/*/summary.json`] | 擋 5 seeds 太少的攻擊。 | 負責人：____ |
| **Figure captions polish** | 每張圖 caption 都要寫「這張圖證明什麼」，不是只描述座標軸。[來源: `submission/README.md`, `paper/main.tex`] | 讓 reviewer 快速抓到 main/supplement hierarchy。 | 負責人：____ |
| **Language audit** | 全文搜尋並替換 risky wording：clinical safety、improves survival、medically wrong 等。[來源: `core_docs/15_paper_story_spine.md`, `submission/README.md`] | 避免過度醫療宣稱。 | 負責人：____ |
| **Anonymity / submission check** | 確認沒有作者姓名、學校、真實 GitHub；figures 和 README 連結不暴露身份。[來源: `paper/main.tex`, 課程 submission 規定] | double-blind 必要。 | 負責人：____ |

---

## 組內共識提醒

- Main results 是 **penalty sweep / component ablation / offline dataset-size sweep**；其他是 support，不要在口頭簡報時把七個實驗講成同等重要。[來源: `core_docs/15_paper_story_spine.md`, `submission/README.md`]
- 最重要的圖應該是 **component_ablation.png**，因為它把故事從「masking helps」提升成「failure mechanism 被定位」。[來源: `core_docs/15_paper_story_spine.md`, `results/component_ablation/summary.json`]
- 最重要的防守句：**Exact V* 是 measurement instrument；generality 來自 offline RL 文獻，cleanliness 來自 ICU-Sepsis。**[來源: `core_docs/reviewer_anticipated_questions.md` Q16]
- 最容易被誤解的地方：**random admissible equivalence 不是無害，而是 value cost 的來源。**[來源: `core_docs/reviewer_anticipated_questions.md` Q17]

