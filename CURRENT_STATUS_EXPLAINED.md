# 目前情況說明：ICU-Sepsis 期末專案

> 這份文件整理自：
> - `Final-Project-Introduction .pdf` 的課程規定
> - `core_docs/` 內的 Claude 評估、題目規劃、repo 理解、實驗紀錄與 reviewer 風險分析
> - 目前實際跑出的 `results/`、`figures/`、`tests/last_run.txt`
>
> 目的不是重複所有細節，而是用一份好讀的方式說清楚：我們現在在哪裡、這個題目是否穩、已經有什麼證據、還缺什麼。

---

## 一句話總結

目前專案方向是可行而且已經有初步成果的：我們把 ICU-Sepsis 這個 medical RL benchmark 當作一個可控的 tabular RL 實驗場，研究「inadmissible actions 要怎麼處理」以及「action masking 是否改善學習」。

目前已經完成環境安裝、baseline 重現、核心程式雛型、18 個 sanity tests，以及第一個關鍵 ablation：Q-learning 在 `mean` strategy 下，比較 mask off / mask on。初步結果顯示，action masking 讓 unsafe action rate 從約 85% 降到 0%，同時把 policy value 從 0.786 提升到 0.806，distance-to-V* 也明顯變小。這已經足夠支撐一篇最小可行的期末 paper，但若要讓 paper 更完整，還需要補上 strategy ablation、SARSA / Dyna-Q 或至少更完整的圖表與文字論述。

---

## 1. 課程到底要求什麼？

根據 `Final-Project-Introduction .pdf`，這門課的期末專案不是單純交 code，而是模擬一個 mini conference。

你們需要做的是：

1. 找一個有 novel contribution 的 RL-focused 題目。
2. 寫成英文 research paper。
3. 用 double-blind 的方式投稿到課程 OpenReview venue。
4. 之後還要參與 review、rebuttal、discussion。
5. 最後在 6/15 做 oral 或 poster presentation。

硬性格式要求：

| 項目 | 規定 |
|---|---|
| Paper 語言 | 英文 |
| 格式 | NeurIPS 2026 LaTeX template |
| 頁數 | main content 4-8 頁，不含 references 與 appendix |
| 匿名 | 必須 double-blind，不能出現姓名、學校、真實 GitHub 等會暴露身份的連結 |
| Line number | 必須開啟 |
| 內容 | Abstract、Introduction、Related Work、Methodology、Experiments、Conclusion、References；Member Workload 只放 camera-ready |

重要日期：

| 日期 | 事項 |
|---|---|
| 2026-05-25 23:59 | Paper submission deadline |
| 2026-05-29 23:59 | Review deadline |
| 2026-06-01 23:59 | Rebuttal deadline |
| 2026-06-05 23:59 | Discussion deadline |
| 2026-06-08 23:59 | Decision notification |
| 2026-06-15 | Oral / poster session |

評分方式：

| 部分 | 比重 |
|---|---|
| Author score | 25% |
| Reviewer score | 25% |
| Instructor score | 25% |
| Presentation | 25% |
| Oral paper bonus | +10% |

也就是說，專案本身、paper 品質、review 品質、最後報告都會影響分數。這份專案規劃中特別在意 reviewer 會問什麼，是合理的，因為 review/rebuttal 本身就是課程目標之一。

---

## 2. 目前選定的研究題目是什麼？

目前推薦且已經開始實作的題目是：

**Action Admissibility Matters: A Systematic Study of Inadmissible-Action Handling and Action Masking on the ICU-Sepsis Benchmark**

中文白話版：

> 在 ICU-Sepsis 這個 medical RL benchmark 裡，有些 state-action pair 因為原始臨床資料樣本太少，被環境標成 inadmissible action。這些 action 並不是物理上不能做，而是「資料支撐不足」。我們研究：RL agent 遇到這些 action 時，環境怎麼處理、訓練時是否把它們 mask 掉，會如何影響 performance、sample efficiency、unsafe-action proxy，以及與 clinician policy 的一致性。

這個題目有三個核心問題：

| RQ | 問題 |
|---|---|
| RQ1 | ICU-Sepsis-v2 的不同 `inadmissible_action_strategy` 會怎麼影響 RL 學習？ |
| RQ2 | 使用 `info["admissible_actions"]` 做 action masking，是否能降低 unsafe action rate 並改善 sample efficiency？ |
| RQ3 | 在 50k episodes 這種有限 budget 下，哪種 strategy + masking 組合最接近 optimal policy？ |

這裡的重點是：我們不是在說「哪個治療比較好」，而是在分析一個 benchmark 的設計選項會如何改變 RL 實驗結果。

Paper 裡一定要反覆清楚說明：

> This is a benchmark-level algorithmic analysis, not a clinical recommendation.

---

## 3. 為什麼這個題目適合五天期末專案？

`core_docs/03_candidate_project_directions.md` 比較了三個方向：

1. Action admissibility / action masking
2. Expert-guided learning / imitation initialization
3. SOFA-based reward shaping

最後推薦方向 1，理由很務實：

| 評估面向 | 方向 1 的狀態 |
|---|---|
| 五天可行性 | 最高，CPU 分鐘級可以跑 |
| Novelty | 原 ICU-Sepsis paper 沒有系統比較這些 ablation |
| Reviewer 風險 | 相對低，因為主張是 benchmark / algorithmic，不是 medical claim |
| 實作難度 | 低，環境直接提供 admissible action set |
| Paper 敘事 | 清楚，有 RQ、有 ablation、有 metric、有圖表 |

這個選擇的優點是很穩：ICU-Sepsis 是 tabular MDP，只有 716 states、25 actions，環境 dynamics 完全可見，所以可以直接用 value iteration 算 V*。這讓我們不需要碰真實 MIMIC-III 權限，也不用承擔 off-policy evaluation 的高風險。

換句話說，這不是那種「如果訓練不收斂就全毀」的題目。它比較像是一個 benchmark 設計分析：把已存在但未充分研究的 knobs 系統化測量出來。

---

## 4. ICU-Sepsis 環境目前理解到什麼程度？

根據 `core_docs/01_repo_understanding.md` 與 `core_docs/dynamics_stats.md`：

ICU-Sepsis 是一個 medical RL benchmark：

| 元素 | 數值 / 說明 |
|---|---|
| State | 716 個離散 state |
| Action | 25 個 action，來自 5 種 fluid level x 5 種 vasopressor level |
| Terminal states | death、survival、s_inf |
| Reward | 只有進入 survival state 時 +1，其餘為 0 |
| Return 意義 | episode return 等於 survival indicator，因此 average return 可解讀為 benchmark 內的 survival rate |
| Gamma | 1.0 |
| Horizon | 最多 500 steps，但實際 episode 平均約 9-11 steps |
| Dynamics | 完全可讀，可算 exact V* |

最重要的是 v2 有三種 `inadmissible_action_strategy`：

| Strategy | 行為 |
|---|---|
| `mean` | inadmissible action 會被替換成該 state 下 admissible actions 的平均 transition，是原 paper 預設 |
| `terminate` | 一選到 inadmissible action 就直接進入 death terminal state |
| `raise_exception` | 一選到就丟 exception，主要像 debug / instrumentation tool |

環境每一步也會在 `info` 裡給出：

```python
info["admissible_actions"]
```

這表示 action masking 實作成本很低：agent 在選 action 時只要限制在 admissible action set 裡即可。

---

## 5. Dynamics 分析發現了什麼？

`core_docs/dynamics_stats.md` 裡有幾個很重要、可以寫進 paper 的觀察。

第一，admissible action set 很小。

| 統計 | 非 terminal states |
|---|---|
| 最小 admissible action 數 | 1 |
| 中位數 | 4 |
| 最大值 | 13 |
| 平均 | 3.14 |
| admissible `(s,a)` 比例 | 約 12.56% |

這代表在 nominal 25 個 action 裡，多數 state 其實只有約 1-4 個 action 有足夠資料支撐。Action masking 不是小修小補，而是會移除大約 84%-87% 的 action space。這就是為什麼 masking 可能產生明顯效果。

第二，reward 很 sparse 但很乾淨：

| Transition target | Reward |
|---|---|
| survival state 714 | +1 |
| 其他 state，包括 death | 0 |

因此 `gamma=1` 很合理，因為 undiscounted return 就是 survival probability。如果用 `gamma<1`，反而會讓晚一點 survival 的 trajectory 被折價，這不符合此 benchmark 的定義。

第三，內建 expert policy 並不完全遵守 admissible action set。

| 指標 | 數值 |
|---|---|
| expert policy 在 admissible set 上的平均 probability mass | 約 84.4% |
| expert 完全只放 admissible action 的 non-terminal states | 0 個 |

這點非常適合寫進 Discussion：所謂 inadmissible 並不是「醫生絕對不會做」，而是「資料量不足以可靠估 transition」。因此 action masking 和 expert agreement 不是同一件事，也不能把 admissibility 簡化成 clinical correctness。

---

## 6. 目前實際完成了什麼？

根據 `core_docs/setup_log.md`、`tests/last_run.txt` 與實際檔案，目前已完成：

### 環境與 baseline

ICU-Sepsis 與 helper package 已安裝成功，quickstart 可跑。`get_baselines.py -v 2` 的 baseline reproduction 也通過：

| Policy | 目前重現結果 | 原 paper / README 數字 | 狀態 |
|---|---:|---:|---|
| Random | 0.78014 | 約 0.78 | match |
| Expert | 0.78132 | 約 0.78 | match |
| Optimal | 0.87624 | 約 0.88 | match |

這代表環境與 baseline 沒有明顯壞掉，後續實驗有可信起點。

### 程式架構

目前 repo 已有：

| 檔案 | 功能 |
|---|---|
| `src/env_utils.py` | 建 env、取 dynamics、算 V* / Vπ / distance-to-V* |
| `src/policies.py` | Random / Expert / Deterministic policy |
| `src/evaluate.py` | rollout evaluation |
| `src/tabular_rl.py` | Q-learning / SARSA / Dyna-Q，含 `use_mask` |
| `src/analysis.py` | SOFA bucket、admissible fraction 等分析 |
| `scripts/run_masking_ablation.py` | 目前主實驗腳本 |
| `scripts/compute_dynamics_stats.py` | dynamics 統計 |
| `configs/default.yaml` | 實驗設定 |

### 測試

`tests/test_sanity.py` 共 18 個測試全部通過：

```text
18 passed in 22.17s
```

測試涵蓋 env 載入、dynamics shape、transition normalization、value iteration、policy evaluation、Q-learning / SARSA / Dyna-Q 短跑、masking 相關行為等。這對期末專案而言已經是很不錯的工程底盤。

---

## 7. 目前跑出的初步實驗結果

目前完整跑完的是：

> Q-learning + `mean` strategy + 5 seeds + 50k episodes，比較 mask off / mask on。

結果存在：

| 檔案 / 目錄 | 內容 |
|---|---|
| `results/bundle_c_masking/*.json` | 10 個 per-seed run |
| `results/bundle_c_masking/summary.json` | 聚合統計 |
| `figures/preliminary_curve.png` | 初步圖 |

聚合結果如下：

| Metric | mask off | mask on | 差異 |
|---|---:|---:|---:|
| `J(π)`，即 d0-weighted policy value | 0.7855 ± 0.0029 | 0.8058 ± 0.0031 | +0.0203 |
| Distance to V* | 0.0896 ± 0.0029 | 0.0693 ± 0.0031 | -0.0203 |
| Training-time inadmissible-action rate | 0.854 ± 0.012 | 0.000 ± 0.000 | -0.854 |
| Agreement with expert | 0.041 ± 0.010 | 0.528 ± 0.005 | +0.487 |
| V* reference value | 0.8751 | 0.8751 | - |

直覺解讀：

1. **Masking 幾乎完全解決 training-time inadmissible action。**  
   這部分是 by construction，但數字非常乾淨，適合當 safety proxy 主結果。

2. **Masking 不只讓 unsafe rate 變 0，也讓 policy 更接近 V*。**  
   Distance-to-V* 從 0.0896 降到 0.0693，這是 paper 最好講的 performance improvement。

3. **Survival / return 只提升約 2 個百分點，但在這個 benchmark 中已經有意義。**  
   因為 Random / Expert 本來就在 0.78，Optimal 也只有 0.875，整個可改善空間約 0.10。從 0.786 到 0.806 等於吃掉了約 20% 的 optimality gap。

4. **Unmasked Q-learning 會大量選 inadmissible action，且沒有自己學會避開。**  
   原因是 `mean` strategy 會把 inadmissible action 的 transition 替換成 admissible actions 的平均，因此 agent 沒有得到明確懲罰信號。

5. **Expert agreement 的變化很大，但要小心解釋。**  
   Mask-on agreement 從 4% 跳到 53%，部分原因是 mask 把 action space 限縮到和 expert support 更接近的位置。這是有價值的 benchmark observation，但不能說「更像醫生所以更好」。

---

## 8. 目前最強的 paper 故事線

目前最順的故事可以這樣寫：

1. Medical RL benchmark 常被拿來比較演算法，但 benchmark 裡的 hidden design choices 可能大幅影響結果。
2. ICU-Sepsis-v2 提供 `inadmissible_action_strategy` 與 admissible action sets，但原始 benchmark paper 沒有系統分析這些 knobs。
3. 我們把這些 knobs 當成研究對象：比較 strategy、masking、algorithm，並且不只看 survival rate，也看 distance-to-V* 與 unsafe-action proxy。
4. 初步結果顯示，在 Q-learning + `mean` setting 下，action masking 使 inadmissible-action rate 從約 85% 變 0%，同時改善 distance-to-V* 與 policy value。
5. 因此，ICU-Sepsis 的使用者不應該只報告 default `mean` strategy 下的 survival rate，而應該明確報告 inadmissible-action handling 與 masking 設定。

這個故事的強項是很乾淨：不是硬拗 SOTA，而是把 benchmark 內部一個重要但容易被忽略的設計因素量化出來。

---

## 9. 目前還缺什麼？

如果以「最低限度能交」來看，目前還缺的是 paper 寫作與圖表整理，不是核心 feasibility。

但如果要讓 paper 更完整，建議補以下工作。

### 必補

| 項目 | 原因 |
|---|---|
| 把 preliminary result 整理成正式 Fig / Tbl | 現在有結果，但還不是 paper-ready |
| 寫 paper skeleton / Method / Experiments | 課程交的是 paper，不是只交 repo |
| 補清楚 anonymity audit | 投稿不能有真實姓名、學校、真實 GitHub |
| 建立 anonymous code link 或至少準備 submission-safe 說法 | PDF 不能暴露身份 |
| 把 claims 改成保守措辭 | 避免 medical overclaim |

### 強烈建議補

| 項目 | 原因 |
|---|---|
| `mean` vs `terminate` strategy ablation | 這是題目標題的一半；目前只完整跑了 `mean` |
| SARSA / Dyna-Q 至少跑其中一個 | 防止 reviewer 說只是一個 Q-learning 小實驗 |
| Sample efficiency at 5k / 10k / 25k / 50k | 很適合支撐「masking 改善學習效率」 |
| SOFA-bucket unsafe rate | 可讓 safety proxy 更細緻，但不是必要 |

### 可砍

| 項目 | 為什麼可砍 |
|---|---|
| DQN baseline | 可以防守「不是 deep RL」，但時間成本較高，不是 MVP 必需 |
| BC-init / imitation learning | 是另一篇 paper 的題目，不要讓主軸發散 |
| SOFA reward shaping | 有 medical claim 風險，且 effect size 不確定 |

---

## 10. Reviewer 可能會攻擊哪裡？

`core_docs/reviewer_anticipated_questions.md` 已經整理了 15 個問題。最重要的幾個如下。

### Q1：這不是 deep RL，只是 tabular RL，合適嗎？

回應方式：

這是 benchmark-level RL methodology analysis。ICU-Sepsis 本身就是 tabular benchmark，tabular setting 的好處是可以精確計算 V*，避免 OPE 噪音。我們不是提出新 deep RL 演算法，而是分析 benchmark design choices 如何影響 RL learning。

如果時間足夠，可以補一個 DQN baseline 放 appendix；但不應讓 DQN 成為主線。

### Q2：Action masking 不是很基本嗎？Novelty 在哪？

回應方式：

Novelty 不是發明 masking，而是在 ICU-Sepsis medical RL benchmark 上首次系統量化：

- masking 是否改變 distance-to-V*
- masking 是否改變 unsafe-action proxy
- masking 是否影響 expert agreement
- benchmark 預設 `mean` strategy 是否掩蓋 inadmissible action 問題

### Q3：Masking 把 unsafe rate 變 0 不是廢話嗎？

回應方式：

Training-time unsafe rate 對 masked agent 變 0 確實是設計結果，不該誇大。真正要強調的是：

- unmasked agent 在 `mean` strategy 下 unsafe rate 高達 85%
- 這個現象不只是安全 proxy，也對 distance-to-V* 與 return 有影響
- 若補 evaluation-time unmasked deployment unsafe rate，會更有說服力

### Q4：這能代表臨床安全嗎？

回應方式：

不能。Paper 要明確說這只是 benchmark-internal safety proxy，不是 clinical safety。Inadmissible action 代表資料覆蓋不足，不代表醫學上一定錯。

### Q5：五個 seed 太少嗎？

回應方式：

承認 5 seeds 是低標，但本專案時間有限；主要 effect size 很大，尤其 unsafe-action rate 85% 到 0%，distance-to-V* 也有清楚差距。對 survival rate 這種小差異，不做過度顯著性主張。

---

## 11. 最小可行 paper 可以長什麼樣？

如果時間很緊，MVP paper 可以只保留：

| Section | 內容 |
|---|---|
| Introduction | 說明 ICU-Sepsis、inadmissible action、為什麼 masking / strategy 是重要 benchmark knob |
| Related Work | Medical RL benchmark、ICU-Sepsis、action masking、safe / constrained RL |
| Method | 環境設定、Q-learning、action masking、metrics |
| Experiments | Baseline reproduction + Q-learning mask on/off |
| Discussion | 為什麼 survival rate 不夠、distance-to-V* 比較敏感、mean strategy 會讓 agent 不知道自己選到 inadmissible action |
| Limitations | Tabular only、5 seeds、不是 clinical recommendation、目前只跑部分 ablation |
| Conclusion | Benchmark users should explicitly report inadmissible-action handling and masking |

MVP 的主張要收斂一點：

> We provide an initial systematic study showing that action masking materially changes Q-learning behavior under the default ICU-Sepsis `mean` strategy.

不要寫成：

> We fully characterize all strategies and algorithms.

除非後續真的把完整 matrix 跑完。

---

## 12. 接下來最建議的行動順序

如果現在要把這個專案推向可交版本，我建議照這個順序：

1. **先固定 paper claim。**  
   決定是 MVP claim，還是要補完整 strategy / algorithm matrix。不要一邊寫完整 claim、一邊只有 partial result。

2. **把目前 Q-learning mask result 轉成正式表格與圖。**  
   目前數字已經足夠漂亮，要先讓它 paper-ready。

3. **補 `terminate` strategy 的 Q-learning mask on/off。**  
   這是最划算的下一步，因為能直接支撐 title 裡的 inadmissible-action handling。

4. **如果時間夠，再補 SARSA / Dyna-Q。**  
   這會讓 paper 更像「systematic study」，但不是最小可行版本的生死線。

5. **同步開始寫 paper，不要等所有實驗跑完。**  
   Introduction、Related Work、Method、Limitations 現在就能寫。Experiments 的數字可以最後填。

6. **最後做 anonymity audit。**  
   這點不能拖，因為課程明確要求 double-blind。

---

## 13. 我對目前狀況的判斷

目前這個專案不是空中樓閣，已經有可用結果，而且方向選得很聰明。

它的優勢是：

- 符合 RL-focused 與 novel contribution 的要求。
- 避開了 MIMIC-III 權限與 OPE 的大坑。
- 有 exact V*，metric 很乾淨。
- 已經重現 baseline，可信度高。
- 初步 masking ablation 效果明顯。
- Reviewer 風險可以用保守 framing 防住。

它的主要風險是：

- 目前完整實驗還偏少，只跑了 Q-learning + `mean` 的 masking ablation。
- 如果 paper 標題與摘要寫得像「完整系統研究」，但實驗只支撐 MVP，會被 reviewer 抓。
- 如果不斷強調 medical / clinical，會踩過度宣稱的雷。
- 如果最後沒有正式 paper-ready figure / table，再好的結果也不容易拿高分。

所以最核心的策略是：**用 benchmark analysis 的角度寫，claim 要貼緊已完成結果；能補多少 ablation 就補多少，但不要讓未完成的 stretch goal 綁架 paper。**

---

## 14. 給組員看的超短版

我們現在做的是 ICU-Sepsis benchmark 的 action admissibility / action masking 分析。課程要求 5/25 前交匿名英文 NeurIPS-format paper，4-8 頁。

目前已經：

- 裝好環境
- 重現 Random / Expert / Optimal baseline
- 寫好核心 RL code
- 18 個 tests 全過
- 跑完 Q-learning + `mean` strategy 下的 mask on/off ablation
- 初步結果很好：masking 讓 unsafe action rate 約 85% → 0%，policy value 0.786 → 0.806，distance-to-V* 0.0896 → 0.0693

接下來最重要：

1. 把結果變成正式圖表。
2. 補 `terminate` strategy，最好再補 SARSA / Dyna-Q。
3. 同步寫 paper，保持 claim 保守。
4. 全文避免 clinical recommendation，只說 benchmark-internal / safety proxy。
5. 投稿前做匿名檢查。

