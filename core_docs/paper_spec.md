# paper_spec.md — 合併 paper 的逐章節寫作規格（executor 版）

> **這份文件是什麼**：把通用寫作規格 `spec.md` **套用到我們這篇合併 paper** 的逐章節施工圖。
> 目標：executor **不需要再讀原始 PDF、不需要再做判斷**，照本檔即可把每一節的 prose 寫出來。
>
> **與其他檔的關係**：
> - 硬性格式/NeurIPS 慣例 → 見 `spec.md`（template、4–8 頁、匿名、行號、claim–evidence 等，不在此重複）。
> - 本檔只管「**我們這篇要寫什麼、用哪些數字、踩哪些紅線**」。
> - 內容來源：`17_merged_paper_outline.md`（架構）、`16_team_briefing_claude.md`（我方）、`18_teammate_paper_explained.md`+`19_merged_team_briefing.md`（隊友）、`paper/main.tex`（現有骨架）、`results/*/summary.json`+`submission/README.md`（我方確切數字）。
>
> **數字標記規範（全檔通用，務必遵守）**：
> - 【repo ✅】= 我方數字，來自 `results/*/summary.json`，可重現。
> - 【PDF-only ★】= 隊友數字，目前只在她的 PDF、尚未在 repo 重現。**v1 決策（見頂部 🔒）：直接採用她 PDF 數字寫入，但每個 ★ 標 provisional 註記（`from teammate's draft, pending repo reproduction`），投稿前須重現或保留註記。** 她 PDF 標 *in progress* 而無數字者仍 omit。（此處取代舊規則「無法入庫就砍」。）
>
> **語言**：說明用繁中；寫進 paper 的句子與技術詞用英文。

---

## 🔒 v1 決策（已拍板 2026-05-23；executor 必須遵守，凌駕本檔其餘衝突描述）

1. **★ 隊友數字 — v1 直接採用她 PDF 的數字寫入 prose/表格**（不等 repo 重現）。但：
   - 每個 ★ 數字**必須標 provisional**：在該表/段加註腳或括註 `from teammate's draft, pending repo reproduction`。
   - 她 PDF 標 *in progress* 而**無數字**者（AA-MBRL-Shaped/KL/Full）仍無從寫 → 維持 omit。
   - 投稿前須把 ★ 重現入庫、或保留 provisional 註記。**此條凌駕 §0 標記規範「無法入庫就砍」與 §0.0 contribution 3「未入庫退回」的舊寫法。**
2. **Protocol — v1 不重跑對齊。** 同一張表內預算一致（Table 2 全 5×10⁵ 隊友列；我方機制表/圖全 5×10⁴），**每張表/數字明確標 episode 數**，並用「vanilla Q 在兩預算皆 0.785」橋接（§0.4）。不要把兩預算混在同一欄不註明。
3. **Title — 維持現有**（main.tex 的 "When Mean Imputation Hides Unsupported Actions: Diagnosing and Repairing…Failure Mode…"）。
4. **Contribution 3 — 保留**跨演算法 + AA-MBRL（因 ★ 會寫入），仍以 supporting evidence 語氣、AA-MBRL 為端點非戰績（§0.0/§0.2 護欄不變）。

---

## 0.0 Contribution framing（進攻型敘事 — 動筆前先內化，寫每節都回看）

> **三層分工，並存不衝突**：本節（§0.0）管「**賣相 / why-care**」（reviewer 一眼看出切角、特色、意義、實體貢獻）；§0.1 管「**單一 thesis（一個聲音）**」；§0.2 管「**護欄（紅線）**」。把 why-care 搬到**進攻位置**（Abstract / Introduction / Contributions / 主圖），同時嚴守 benchmark-internal / 非臨床 / AA-MBRL 非 SOTA / §9 誠實。§0.1 的 thesis 不變，本節只是指定它的**重心與露出順序**。
>
> **⚠️ 嚴格約束（全檔適用）：禁止 priority / bravado overclaim。** 不得出現 "the first / novel for the first time"；不得用 "offline RL can only theorize about / nobody can measure" 這類**抹掉既有實證文獻**的說法（offline RL 經常用 toy MDP 或 OPE 實證量 overestimation）。任何想寫 "first" 的地方，改成描述 **what is enabled**。賣點一律建立在**可驗證的對比**：`exact ground-truth + 真實蒸餾資料 + 免 OPE`，而非 claim priority。

### 主軸翻轉（one-line reframe）
- ❌ 舊（benchmark-first，reviewer 會歸成 incremental）：「我們診斷了某 benchmark 的一個失敗。」
- ✅ 新（instrument-first，最強 why-care）：「我們把一個**從真實醫療資料（MIMIC-III）蒸餾、且 dynamics 完全已知**的 benchmark，當成**能對 true $V^\star$ 精確量測 OOD-action 病理的量尺**。」
- 為何強：這是**罕見組合**——toy MDP 有 ground truth 但不真實；真實醫療資料真實但只能用吵雜 OPE；ICU-Sepsis 兩者兼得。切角（OOD reframing + exact $V^\star$ 當量尺）是**進攻賣點**，不再是 supporting。

### Abstract 第一句（英文，phenomenon-first，**直接採用、不得加 "first"/"only theorize"**）
> "ICU-Sepsis's known dynamics let us measure the cost of out-of-distribution (OOD) action handling exactly against the true optimal value $V^\star$, rather than through the noisy off-policy estimation that real-data medical RL must otherwise rely on."
>
> （umbrella 名詞全文統一為 "OOD / unsupported-action pathology"，與 §0.1 thesis 一致；"overestimation" 一詞**只保留給 offline empirical-MDP（§6.4）那段**，不要當全篇 umbrella，否則 reviewer 會以為整篇在講 value 高估而錯過 online 機制重心。）

### 唯一 punchline（reviewer 該記住的那**一件事**；§0.1 thesis 的子句全部服務它）
> The decisive remedy is **not** to mask unsupported actions at deployment—the obvious move, which still leaves the $Q$-table corrupted—but to keep them out of the **behavior** that is sampled and bootstrapped during training: a component ablation shows this behavior-level restriction is **necessary and sufficient**, and an exact, ground-truth **$Q$-value-leakage** diagnostic explains *why*.

中文：最反直覺的洞——直覺解「**部署時 mask**」不夠（Q-table 仍被污染），真正根因是「**訓練時別讓 OOD action 被取樣/更新**」（behavior 層 necessary & sufficient），且用 exact ground-truth Q-leakage 證出來。**跨演算法 / AA-MBRL / offline 一律降為「支撐它普遍成立的證據」，不是並列三 claim。**

### 3 個 surprising findings（Intro 開頭的鉤子；數字沿用 §0.3，**勿改勿增**）
- **(a)** benchmark 作者 *explicitly* 自述「無害」（"equivalent to choosing a random admissible action"）的 mean-imputation，讓學習**卡在 random baseline**（$J{=}0.785$ vs Random 0.780）。
- **(b)** **部署時 mask（最明顯的招）不夠**——deploy 歸 0，但 Q-table 仍被污染（leakage 不變，仍 $+0.46$）。
- **(c)** offline 下**資料越多、naive 反而高估越嚴重**（overestimation 升到 $+0.21$ 並停滯），與「多資料應更準」的直覺相反。

### 重寫後的 4 條 contributions（**取代** §2 舊版；把 ④反駁、⑤協議 納入。英文定稿用詞見此，§2 只放對照）
1. **A benign-design claim with a hidden, exactly-measurable cost.** ICU-Sepsis explicitly argues its default mean-imputation is harmless (*"equivalent to choosing a random admissible action"*); using the benchmark's known dynamics to evaluate against the true $V^\star$, we show it carries a measurable cost that survival rate hides—vanilla model-free agents deploy unsupported actions in $\sim$87\% of states and converge to $J{=}0.785$, no better than Random (0.780) / clinician (0.782) (\S\ref{sec:failure}).
2. **Mechanism, not merely a fix (our central result; the punchline).** A component ablation plus an exact $Q$-value-leakage diagnostic localize the failure to *behavior-level* sampling: **in our ablation**, restricting behavior to supported actions is both necessary *and* sufficient (it matches the full mask exactly), whereas masking only the Bellman target or the deployed policy does not suffice (deployment-masking leaves leakage at $+0.46$) (\S\ref{sec:mechanism}).
3. **Generality of the diagnosis and remedy, as supporting evidence.** The phenomenon and the support-aware remedy spectrum (support penalty $\to$ CQL conservatism $\to$ admissibility masking $\to$ model-based endpoint AA-MBRL) hold across Sarsa/Q/DQN/PPO and in a finite-data offline empirical-MDP regime, where naive imputation overestimates its own value ($+0.21$) and stagnates while pessimism and masking stay calibrated (\S\ref{sec:remedy}). *(★ 跨演算法 / AA-MBRL 採隊友 PDF 數字寫入並標 provisional，見頂部 🔒；保留為 supporting evidence、AA-MBRL 為端點非戰績。)*
4. **A reusable exact-$V^\star$ auditing protocol + release.** We package the study as an evaluation protocol for auditing OOD-action handling—three exactly-computable diagnostics (deployed-unsupported rate, $Q$-value leakage, value overestimation)—and release one-command scripts; ICU-Sepsis results should report inadmissible-action handling explicitly.

> 註：contribution 1 把「**反駁作者 explicit benign claim**」從防守（原 Q17/B.3）升成 headline novelty；contribution 4 把「**實體貢獻**」包成可遷移的 *protocol + 三診斷量 + scripts*，比「我診斷了一個 benchmark」具體得多。兩者皆只用 §0.3 既有數字，無 priority 字眼。

### 主圖指令（防稀釋 — 合併特有風險，⑥）
- **Fig 2（component ablation + $Q$-value leakage）= the hero figure。** 它承載 punchline（機制）；版面、解析度、正文討論篇幅**優先級最高，不可砍、不可縮**。
- **Table 2（跨演算法 + AA-MBRL）= 配角（supporting breadth）。** 它是「診斷普遍成立」的證據，**不得搶 Fig 2 版面**；版面緊張時**先壓 Table 2、不動 Fig 2**。
- 原因：跨演算法 / AA-MBRL 是**廣度證據不是洞**。Table 2 一旦搶版面，重心會漂回隊友的「在很多演算法上試很多 prior」，reviewer 會把全文歸成 empirical 比較而**錯過機制**。

---

## 0. 全域設定（動筆前先讀完這一節）

### 0.1 全文唯一 thesis（只能有一個聲音）
> ICU-Sepsis 的 default mean-imputation 製造了一個 **OOD-action pathology**：model-free RL 在約 87% 狀態部署 data-unsupported actions、卡在 random/clinician 水準，而 survival rate 把它藏起來。我們把失敗**定位到 behavior-level sampling**（機制），並證明**用 benchmark 自帶的結構**（support penalty → CQL conservatism → admissibility masking → model-based planning）能移除 pathology 並補上 gap，且**跨演算法、online 與 offline 都成立**。

**Title（已定，見 `paper/main.tex` 與 `17`）**：
*When Mean Imputation Hides Unsupported Actions: Diagnosing and Repairing an Out-of-Distribution Action Failure Mode in the ICU-Sepsis Benchmark*
（`17` 另列一個 "Diagnosing and Closing… Gap" 變體；目前 main.tex 用 "Repairing"，**以 main.tex 為準**，除非人類另行決定。）

### 0.2 Framing 護欄（紅線；每節寫完都要回頭對照）
- ✅ **A-led：診斷/機制是主軸。** Claim 2（component ablation + Q-leakage）是全文最強、不可砍、不可被稀釋。
- ✅ **benchmark-internal、非臨床。** "inadmissible/unsupported" = 資料不足，**不是**醫學上錯誤。全文不得出現臨床建議、可部署、更安全等字眼。
- ✅ **exact V\* 是量尺（measurement instrument），不是 optimization target。** 明講。
- ✅ **AA-MBRL 定位 = remedy 光譜的 model-based 端點**，用來支撐「gap 是 mean-imputation 製造的人為缺陷」，**不是 SOTA、不是賣點**。
- ✅ **納入 §9 external-validity 段落**（什麼能遷移、什麼不能；草稿已在 `17` §9，可直接貼進 Discussion）。
- ❌ **不要**寫 "structure beats capacity"、不要把 "0.874 / gap 0.001" 當 headline 戰績。
- ❌ **不要**兩個 thesis 並存（診斷 vs closes-the-gap）。隊友的廣度/AA-MBRL 一律降級為「證據」而非「主張」。
- ⚠️ Related Work 用 UCRL/PSRL **主動承認** small tabular MDP 本來就可被 model-based 解 → 把 reviewer 最可能的攻擊先講掉，再說「正因如此，我們的貢獻是診斷與機制，不是 regret/最優性」。

### 0.3 ★ Canonical numbers — 全文唯一數字真相表（避免各節打架）
> 凡是同一個量在多節出現，**一律用下表的值與寫法**。雜項數字（median |A(s)|、optimal、deploy-rate）的不一致已在此處一次解決。

**參考策略（exact，d0-weighted = survival rate）【repo ✅ `baselines/summary.json`】**
| 量 | 值 | 寫法 |
|---|---|---|
| Random | 0.780 | `J{=}0.780` |
| Clinician (Expert) | 0.782 | `J{=}0.782` |
| Optimal $V^\star$ | **0.875** | 全文 optimal 一律 **0.875**（不是 0.88；exact 0.8751） |

**環境常數（統一寫法，解決雜項不一致）**
| 量 | 統一值 | 說明 / 來源 |
|---|---|---|
| #states | 716（其中 713 non-terminal）| main.tex；deadend summary n_non_terminal=713 |
| #actions | 25（5 fluid × 5 vaso）| main.tex |
| admissibility threshold τ | 20 | main.tex / 隊友一致 |
| **admissible set 大小** | **median 4，mean 3.2**（of 25）| ⚠️ A 寫 median 4、隊友寫 mean 3.2 — **兩者皆對（不同統計量）**。全文一律寫 "median 4 (mean 3.2)"，不要二選一造成「矛盾」 |

**我方核心結果（5 seeds, 5×10⁴ episodes, J\*=0.875）【repo ✅】**
| 設定 | dist-V\* | deploy unsupp.(state) | Q-leakage | expert-agree | 來源 json |
|---|---:|---:|---:|---:|---|
| vanilla | **0.090** | **87%** (visit 85%) | **+0.46** | 0.04 | component_ablation / penalty_sweep |
| target-only mask | 0.085 | 77% | +0.07 | 0.08 | component_ablation |
| policy-only mask | 0.083 | 0% | +0.46 | 0.51 | component_ablation |
| CQL conservatism (κ=1) | 0.080 | 0% | −2.95 | 0.49 | component_ablation（best **soft** remedy）|
| CQL conservatism (κ=2) | 0.089 | 0% | −3.52 | 0.49 | component_ablation（over-conservative→更差）|
| **behavior-only mask** | **0.069** | 0% | **−0.80** | 0.53 | component_ablation（== full mask）|
| full mask | 0.069 | 0% | −0.80 | 0.53 | component_ablation |
| hard mask (penalty sweep 表) | 0.069 | 0% | — | 0.53 | penalty_sweep（J=0.806）|

> 註：full/behavior/hard mask 的 J = **0.806**【repo ✅】。deploy-unsupp 全文 headline 用 **87%（state-frac）**，並可加註 visitation-weighted 85%。**不要**把隊友的 "0.79–0.83"（她的 training-step 量測 @500k）混進我方這格。

**Penalty sweep（support–value trade-off）【repo ✅ `penalty_sweep/summary.json`】**
| λ | dist-V\* | deploy unsupp.(state) | expert-agree |
|---|---:|---:|---:|
| 0.01 | 0.089 | 82% | 0.07 |
| 0.1 | 0.083 | 39% | 0.23 |
| 0.5 | 0.085 | 1.3% | 0.51 |
| 1.0 | 0.087 | 0% | 0.52 |
| → 結論 | **plateau ≈0.085**，被 hard mask (0.069) **Pareto-dominated** | | |

**Offline empirical-MDP（N sweep, expert behavior, N 最大 =10⁵）【repo ✅ `offline_datasize/summary.json`】**
| method | overestimation @N=10⁵ | dist-V\* 隨 N | deploy unsupp. |
|---|---:|---|---:|
| naive (mean-impute) | **+0.21** | **stagnates ≈0.093**（N=10³→10⁵ 全程 0.093–0.096）| 升到 86% |
| pessimistic VI-LCB | ~0（+0.05；自 −0.51 校準上來）| **改善 0.092→0.069** | ~40% |
| masked | +0.10 | 改善 0.088→**0.065** | 0% |

**Supplementary【repo ✅】**
- Expert prior（`expert_prior/summary.json`；clinician inadmissible mass = **16%**）：raw → dist 0.074 / deploy **8%** / agree 0.60；**projected → dist 0.073 / deploy 0.5% / agree 0.65**（value 不變）。
- Robustness（`robustness/summary.json`）：
  - mean, maskoff：Q 0.090/87%、SARSA 0.091/86%、Dyna-Q 0.088/84%。
  - mean, maskon：Q 0.069、SARSA 0.072、Dyna-Q 0.070（deploy 全 0%）。
  - terminate, maskoff（vanilla 自己避開）：Q 0.107/3.8%、SARSA 0.108/4.1%、Dyna-Q 0.072/3.3% → **deploy 降到 3–4%，但 Q/SARSA 的 dist 反而更差**（model-free 因死亡截斷更難學；Dyna-Q 靠 planning 沒事）。
  - terminate, maskon：~0.069–0.072（masking 不論 strategy 都最好且穩）。
- Dead-ends（`deadend/summary.json`）：**無 dead-end**；min V\*=**0.198**、mean 0.883、median 0.909、**427/713 (60%) secured**（V\*>0.9）。one-step death：inadmissible **0.032** vs admissible **0.023**；harmful actions 中 **59%** 是 inadmissible。

**隊友結果（5 seeds, 5×10⁵ episodes）【PDF-only ★ — 入庫前不得寫死】**
| 項目 | 數字 | 備註 |
|---|---|---|
| baselines（no prior）| Sarsa 0.789 / Q **0.785** / DQN 0.787 / PPO 0.833 | Q 在兩預算都 0.785 → 與我方一致（protocol 接得起來的關鍵）|
| +P1 mask | AA-Sarsa 0.799 / AA-Q 0.811 / AA-DQN 0.823 / AA-PPO 0.862 | |
| mask gain（paired-t）| Sarsa +0.010 / Q +0.026 / PPO +0.029 / DQN +0.036 | 後三者 p<0.001；**效果隨 baseline 變強** |
| AA-MBRL (P1+P2) | **0.874 ± 0.003**, gap **0.001** | 光譜 model-based 端點，**非戰績** |
| AA-PPO-Shaped / -KL | 0.866 / 0.866 | 各 +0.004 |
| AA-PPO-Full | 0.857 | **不疊加**（兩 prior 資訊重疊）|
| AA-MBRL-Shaped/KL/Full | *in progress* | **無數字 → 跑完才放，否則不放** |
| sample efficiency | AA-PPO ~105k 達 PPO@185k（~1.8×）| learning-curve PNG 原稿是 placeholder，要補真圖 |
| KL 副產品 | seed 間 SE 縮 ~3× | |

### 0.4 Protocol 一致性備註（必寫進 paper，否則表格自相矛盾）
- 事實：我方跑 **5×10⁴ (50k)**，隊友跑 **5×10⁵ (500k)**。
- **救命事實**：vanilla Q 在兩個預算**都是 0.785** → 失敗故事在 500k 仍成立、甚至更強（**非 under-training**）。
- **規則**：
  1. 凡進「**同一張表**」的 cell，**統一單一預算**（建議統一 500k：沿用隊友 cross-algorithm，A 的 vanilla/masked 重跑 500k 對齊）。
  2. 機制 sweep（component ablation / penalty λ / offline datasize）**維持 50k** 省算力，但**加一組 500k 確認跑**（只跑 vanilla / behavior-mask / full-mask 三格）放 appendix，正文寫一句 "conclusions identical at $5{\times}10^5$ (App.~X)"。
  3. 正文凡引用跨預算數字，明確標 episode 數，**不要讓 50k 與 500k 的 cell 出現在同一欄而不註明**。

---

## 1. Abstract
- **唯一核心訊息**：mean-imputation 製造一個被 survival rate 藏住、可被 exact V\* 精確量測的 OOD-action failure；根因在 behavior 層；一族 support-aware remedies（含 model-based）能跨演算法、online/offline 修好它。
- **敘事 beats（phenomenon-first，對應 `spec.md` §2.1 公式 + §0.0 主軸翻轉）**：
  1. **Phenomenon / instrument-first hook（取代舊 "benchmark must decide…" 開法）**：OOD / unsupported-action 的處理是 offline RL 公認的核心難題（典型後果是 value overestimation），但在真實醫療資料上只能用吵雜 OPE 量；ICU-Sepsis 的 known dynamics 讓我們對 true $V^\star$ **精確量測**它。**直接採用 §0.0 的 Abstract 第一句**（"ICU-Sepsis's known dynamics let us measure the cost of out-of-distribution (OOD) action handling exactly against the true optimal value $V^\star$…"）。
  2. **Benign claim refuted（具體 why-care）**：benchmark 將 default `mean`（把 inadmissible action 設成 admissible 平均）自述為「equivalent to choosing a random admissible action、無害」；我們證明它有**被 survival rate 藏住的可量測代價**，並預告 punchline——根因在 behavior 層，部署時 mask 不夠。
  3. Finding（量化）：default 下 vanilla Q-learning 在 ~87% 狀態部署 unsupported actions、$J{=}0.785$ ≈ Random 0.780 / clinician 0.782，遠離 $J^\star{=}0.875$。
  4. Method + punchline：對 exact $V^\star$ 精確評估；component ablation 把失敗定位到 **behavior-level sampling（necessary & sufficient）**、Q-leakage 給機制（part of the hero result）；再比較 support penalty / CQL / masking（+ model-based 端點 AA-MBRL），跨演算法、online 與 finite-data offline 都做（**作為普遍成立的證據**）。
  5. Takeaway：benchmark-internal、非臨床；可遷移的是 phenomenon + protocol，不是數字；inadmissible-action handling 必須明確回報、不可留給隱藏 default。
- **Figure/Table**：無。
- **確切數字（baked-in）**：87% / 0.785 / 0.780 / 0.782 / 0.875【全 repo ✅】。offline：naive 高估 **+0.21** 並停滯、pessimism/masking 校準改善【repo ✅】。
- **護欄**：診斷語氣；可用一句 closing 弧線（"support-aware remedies remove the pathology"）但**不得**出現 SOTA / 0.874 / closes-the-gap-to-oracle / "first" / "only theorize"。**main.tex 現有 abstract 是 benchmark-first 開頭（"Medical reinforcement-learning benchmarks must decide how to handle…"）→ 要把開頭句換成 beat 1 的 phenomenon-first 句**，其餘大致保留、closing 半句語氣壓到診斷即可。

---

## 2. Introduction
- **唯一核心訊息（instrument-first，見 §0.0 主軸翻轉）**：OOD / unsupported-action 的處理是 offline RL 公認核心難題（典型後果是 value overestimation）、但在真實醫療上只能用吵雜 OPE 量；ICU-Sepsis 是「**真實蒸餾資料 + dynamics 已知**」的罕見組合，讓我們對 true $V^\star$ 精確量測這個 OOD-action 病理——並用它證明 benchmark 自述「無害」的 default mean-imputation 其實有可量測代價，根因在 behavior 層。
- **🪝 鉤子（Intro 開頭就拋；3 個 surprising findings，數字沿用 §0.3，勿改）**：
  - (a) 作者 *explicitly* 自述「無害」的 mean-imputation，讓學習**卡在 random baseline**（$J{=}0.785$ vs Random 0.780）。
  - (b) **部署時 mask（最明顯的招）不夠**——deploy 歸 0，Q-table 仍被污染（leakage 不變，仍 $+0.46$）。
  - (c) offline 下**資料越多、naive 反而高估越嚴重**（$+0.21$ 並停滯）。
  > 用法：開頭兩三句即可拋出 (a)~(c) 製造「咦？」的張力，再進漏斗解釋。
- **敘事 beats（漏斗，但 instrument-first；對應 `spec.md` §2.2）**：
  1. **Broad**：offline RL 的核心難題是 OOD / unsupported action，overestimation 是其公認後果〔fujimoto2019bcq, kumar2020cql〕；真實醫療（offline）只能用 noisy/biased OPE 量〔gottesman2019guidelines, gottesman2018evaluating〕。
  2. **主軸翻轉（instrument，進攻賣點）**：ICU-Sepsis〔choudhary2024icusepsis〕從真實 MIMIC-III 蒸餾、dynamics 完全已知 → 可對 true $V^\star$ **精確評估**，是把上述病理「乾淨量測」的罕見量尺（real-distilled + ground-truth + 免 OPE）。**用 §0.0 約束的可驗證對比語氣，不得寫 "first"/"only theorize"。**
  3. **反駁作為 novelty（headline，不再埋進 Discussion）**：benchmark 將 default mean-imputation 自述為「equivalent to choosing a random admissible action、無害」；我們證明它有可量測代價——乾淨、reviewer 一眼懂的具體貢獻。
  4. **Reframe**：把 inadmissible 當 offline-RL OOD-action problem；known dynamics = exact $V^\star$ = **量測工具**（非 optimization claim）。
  5. **Punchline 預告（見 §0.0）**：失敗根因在 **behavior 層**（訓練時被取樣/更新），部署 mask 不夠；跨演算法 / AA-MBRL / offline 是**支撐它普遍成立的證據**，不是並列 claim。
  6. **引子（降級，併隊友框架）**：benchmark「附帶」per-state 結構（admissibility、empirical model、severity、clinician），standard baselines 訓練時丟掉——引出「把結構放回去就能修」。**P1(admissibility)/P2(model) 走主線，P3(SOFA)/P4(clinician) 只當 supplement，不可升成 thesis。**
  7. Contributions bullet（見下方「Contributions 寫法」= §0.0 的 4 條）。
- **Figure/Table**：Fig 1 overview schematic（**待畫**，照 `15` §4：畫出 mean imputation 如何讓 unsupported action 變得 "learnable without penalty"）。它要證明：**直覺上**為何 mean 會讓 agent 採用 unsupported action。
- **確切數字（baked-in）**：結果預告句放最強數字 —— "deployed in ~87% of states yet scoring at the random/clinician level (0.785 vs 0.780/0.782)"【repo ✅】；以及鉤子 (a)~(c) 的 0.785 / +0.46 / +0.21【repo ✅】。
- **Contributions 寫法**：**直接採用 §0.0「重寫後的 4 條 contributions」的英文定稿**（① benign claim refuted & measured exactly；② mechanism = punchline；③ generality as supporting evidence；④ reusable exact-$V^\star$ auditing protocol + release）。對照舊版 main.tex 4 點需替換：原 "Failure diagnosis / Mechanism / Remedy spectrum / Benchmark guidance" → 新版把「反駁 benign claim」提到第 1、把「protocol+三診斷量」做成第 4。★ 跨演算法/AA-MBRL 入庫與否見 §12-3。
- **常見失敗模式**：背景鋪太長才講 gap（鉤子就是用來避免這點）；contributions 變「做了什麼」而非「得到什麼可驗證結論」；把隊友的 closes-the-gap 講成第二個 thesis；把切角（exact $V^\star$ 量尺）又退回 supporting。
- **護欄**：beat 2/4 把 known-dynamics 講成量尺；4-priors 只當引子；**全節禁止 priority/bravado（"first"/"only theorize"），一律改成 what is enabled**；instrument 野心要與 scope 誠實並存（可遷移的是現象+協議，不暗示可部署）。

---

## 3. Related Work
- **唯一核心訊息**：我們站在 offline-RL OOD / action-masking / tabular model-based 三條線之間，貢獻是「診斷+機制+exact 評估」，不是發明 masking 或 model-based。
- **敘事 beats（每段結尾都要 "our work differs by …"，對應 `spec.md` §2.3；可搬 `12`）**：
  1. Medical RL benchmarks〔choudhary2024icusepsis, komorowski2018aiclinician, raghu2017continuous〕。
  2. Offline RL & OOD actions / pessimism〔fujimoto2019bcq, kumar2019bear, kumar2020cql, rashidinejad2021pessimism, jin2021pessimism〕——我們把這個公認問題在 exact-eval 環境裡精確量測。
  3. Invalid/forbidden action masking〔huang2021masking, seurin2020forbidden〕+ 隊友的 deep-RL masking / sb3 MaskablePPO〔raffin sb3〕——我們不是發明 masking，而是用 component ablation 證明它**必須在 behavior 層**。
  4. **Tabular model-based: UCRL / PSRL**〔auer2008ucrl, osband2013psrl〕——**主動承認** small tabular MDP 可被 trivially 解，藉此把 AA-MBRL 的 0.874 框成「預期之內的端點」而非戰績。
  5. Reward shaping / behavior-constrained〔Ng et al. 1999 ng1999shaping；Wu/Nair behavior-reg〕——SOFA shaping 的理論正當性（supplement）。
  6. Evaluation pitfalls〔gottesman2019guidelines, gottesman2018evaluating〕。
- **Figure/Table**：無。
- **確切數字**：無（Related Work 不放數字）。
- **負責人**：Codex 整合 + 隊友提供 deep-RL masking / model-based 段（見 `19` §5）。
- **常見失敗模式**：流水帳、不講差異；漏掉 UCRL/PSRL 的「先承認再轉守為攻」這步（這步是護欄要求，**不可省**）。
- **references.bib 待補**：auer2008ucrl、osband2013psrl、johnson MIMIC-III、raffin sb3 MaskablePPO、Wu/Nair behavior-reg、ng1999shaping（確認是否已存在）。

---

## 4. Background: ICU-Sepsis and Mean Imputation
- **唯一核心訊息**：定義環境、admissibility、Eq.(mean)，並指出 default `mean` 把 inadmissible 設成 admissible 平均、自述「等同隨機合法動作」——正是代價來源。
- **敘事 beats**：
  1. Tabular MDP：716 states（713 non-terminal）、25 actions、survival-indicator reward、γ=1 → undiscounted return = survival prob → V\*(s) = 最大可達存活率。
  2. Full model shipped → 可用 value iteration 精確算 V\* 與任意 V^π，完全避開 OPE。
  3. Admissibility：τ=20 次以上才 admissible；admissible set 小（**median 4, mean 3.2** of 25）。
  4. Eq.(mean)：inadmissible action transition = admissible 的 unweighted average；我們驗證 shipped dynamics 完全成立（每列誤差 7×10⁻¹⁶）。
  5. 點出 benchmark 自述 "equivalent to choosing a random admissible action"，預告 §5.1 證明這就是代價所在。
- **Figure/Table**：無（或把 Eq.(mean) 編號）。
- **確切數字（baked-in）**：716 / 713 / 25 / τ=20 / median 4 (mean 3.2) / 7×10⁻¹⁶【repo ✅ + main.tex】。
- **狀態**：main.tex 已寫實，**幾乎不用動**；只需把 admissible-set 大小統一成 "median 4 (mean 3.2)"（目前寫 median 4，補上 mean 3.2 以與隊友一致）。

---

## 5. Method: Support-Aware Tabular RL
- **唯一核心訊息**：把 inadmissible action 當 OOD/low-support action，研究一族 remedy「在哪裡施加 support 約束」，全部共用 tabular Q update 以隔離「where」而非 function approximation 的影響；AA-MBRL 是這條光譜的 model-based 端點。
- **敘事 beats**：
  1. Framing：inadmissible = OOD/low-support，offline RL 的核心對象。
  2. Remedy spectrum：(i) vanilla → (ii) support penalty λ → (iii) CQL-style conservatism → (iv) admissibility masking（拆 behavior / target / policy 三個可獨立開關）→ **(v) AA-MBRL（online empirical model 上、僅在 admissible 集合重解 admissibility-constrained Bellman）★**。
  3. AA-MBRL 接法（併隊友 §3.2）：邊互動邊估 empirical model（N(s,a,s')/N(s,a)），**每 K=1000 episodes 在估出的 model 上、只在 A(s) 內重做一次 value iteration**；γ_vi=0.999（因 γ=1 不收斂）；ε 0.5→0.001。**明確定位成「光譜最右端：即使最樸素地用 P2 結構也能補滿一個人為 gap」。**
  4. Metrics（全 exact 除非註明）：dist-V\*、deployed unsupported-action rate、Q-value leakage、(offline) value overestimation、clinician agreement。給出每個 metric 的精確定義（main.tex 已有公式）。
- **Figure/Table**：無（方法圖併入 Fig 1 / 結果圖）。
- **確切數字**：無（Method 給定義，不給結果）。
- **狀態 / 合併動作**：main.tex 的 (i)–(iv) + metrics **已寫實**；**唯一要加的是 (v) AA-MBRL**，接在 spectrum 最右端，並把上面 beats 3 的設定寫進去。
- **護欄**：AA-MBRL 一定要用「光譜端點/支撐結構論點」的語氣引入，**不要**寫成「我們提出的新方法」。
- **常見失敗模式**：把 AA-MBRL 講成 contribution headline；metric 定義含糊（尤其 Q-leakage 與 overestimation 要無歧義）。

---

## 6. Experiments
> 共用 setup（main.tex 已寫）：5 seeds、α=0.1、γ=1、ε 1.0→0.05 over 10⁴；report mean±std，per-seed scatter 進 appendix；結論靠大效應 support 診斷而非微小存活率差。**注意 protocol §0.4：同表統一預算。**

### 6.0 Baselines（Table 1）
- **核心訊息**：環境與評估流程正確（exact 值吻合原論文）。
- **Table 1**：Random 0.780 / Clinician 0.782 / Optimal 0.875【repo ✅】。證明「尺」是準的，並順帶點出存活率落在 0.78–0.875 窄區間（為何要改用更敏感的 dist-V\*）。

### 6.1 The hidden failure（Claim 1）— §sec:failure
- **核心訊息**：default 下 vanilla 在 ~87% 狀態部署 unsupported actions、J≈baseline，survival rate 藏住；且跨演算法、500k 仍不改善。
- **敘事 beats**：
  1. vanilla：deploy **87%**、$J{=}0.785$、$dist{=}0.090$ ≈ Random/clinician【repo ✅】。
  2. 不是 labeling artifact：因 Eq.(mean)，選 inadmissible 賺到的是 random-admissible value 而非 best-admissible value，這個差**就是** gap to V\*。
  3. survival rate 看不出（benchmark 只報 return/length/convergence）；dist-V\* 才暴露。
  4. **普遍性 ★**：跨 Sarsa/Q/DQN/PPO 都失敗（隊友 C1）；vanilla Q 在 **5×10⁵ 仍 0.785**（非 under-training）。
  5. admissibility control 即可救回 $J{=}0.806$、$dist{=}0.069$【repo ✅】。
- **Figure/Table**：併入 Table 2（見下）；Fig 3 左 panel callout。
- **護欄**：500k / 跨演算法是 ★ 數字，入庫前可寫「we further confirm…（App）」但別寫死未重現的精確值。

### 6.2 Mechanism（Claim 2）— §sec:mechanism【全文核心，不可砍】
- **核心訊息**：失敗在 behavior-level sampling：masking behavior alone necessary & sufficient（== full mask）；只 mask target/policy 不夠；Q-leakage 給機制。
- **敘事 beats**：
  1. Component ablation（Table 3 = main.tex tab:ablation）：
     - vanilla：dist 0.090 / deploy 87% / leakage **+0.46**。
     - target-only：dist 0.085 / deploy 77% / leakage +0.07（backup alone 不夠）。
     - policy-only：dist 0.083 / deploy 0% / leakage **+0.46**（band-aid；Q 仍 corrupted）。
     - CQL κ=1：dist 0.080 / deploy 0% / leakage −2.95（best **soft** remedy，仍 trails）。
     - **behavior-only：dist 0.069 / deploy 0% / leakage −0.80（necessary & sufficient）**。
     - full mask：== behavior-only。
  2. Q-leakage 從 **+0.46（vanilla）→ −0.80（behavior/full）**：unsupported actions 變 competitive **只因為**它們在 mean-imputed dynamics 下被 sampled & updated。
- **Figure/Table**：Fig 2 = component ablation + Q-leakage（main.tex fig:ablation，**最大不可砍**），證明「根因在哪一步」。Table 3 = tab:ablation。
- **確切數字**：全 repo ✅（component_ablation/summary.json）。
- **常見失敗模式**：把 CQL 的 −2.95 leakage 誤讀成「比 mask 好」（它 dist 0.080 仍輸 mask 0.069；leakage 過負代表 over-suppression）。要解釋 leakage 的正負號意義。

### 6.3 Remedy spectrum — online, cross-algorithm（Claim 3a）— §sec:remedy
- **核心訊息**：從軟到硬到 model-based，hard mask Pareto-best；跨演算法都成立且效果隨 baseline 變強；AA-MBRL 補滿一個人為 gap。
- **敘事 beats**：
  1. Penalty trade-off：λ 越大 deploy→0（λ=1.0 達 0%），但 dist **plateau ≈0.085**，被 hard mask (0.069) **Pareto-dominated**【repo ✅】。
  2. CQL 是 best soft remedy（0.080）但仍 trails，有 κ sweet spot（κ=1 好、κ=2 過頭變 0.089）【repo ✅】。
  3. **跨演算法 ★**：mask 提升 Sarsa +0.010 / Q +0.026 / PPO +0.029 / DQN +0.036（後三 p<0.001），**效果隨 baseline 變強**（隊友 Table 3）。
  4. **AA-MBRL ★**：0.874、gap 0.001 —— **framing：連最樸素地用結構都能補滿一個人為 gap**，不是「我們贏了」。
- **Figure/Table**：
  - **Table 2 = merged main results**（融隊友 Table2+Table3 精華 + 我方 baseline/mask）：欄位 final return / gap / deploy-unsupp；列含 baselines + C1 masked(Sarsa/Q/DQN/PPO) + AA-MBRL。★ 部分入庫前不得定稿。
  - Fig 3 = penalty Pareto（main.tex fig:spectrum），可把隊友 learning-curve 做成小 inset（★，PNG 要補）。
- **護欄**：本節最容易 overclaim。AA-MBRL 與跨演算法都要用「證據支撐 thesis」語氣；gap 0.001 不得當 headline。

### 6.4 Remedy spectrum — offline finite-data（Claim 3b）— §sec:remedy（offline 段）
- **核心訊息**：有限病歷下 naive(mean) 高估自身價值且停滯，pessimism/masking 校準並隨資料改善——這是最寫實、最能遷移的一段。
- **敘事 beats**：
  1. 設定：clinician behavior 抽 N 筆 → certainty-equivalent empirical model → 比 naive / pessimistic VI-LCB〔jin2021pessimism, rashidinejad2021pessimism〕/ masked，全對 true V\* 精確評估。
  2. naive：overestimation **+0.21** @N=10⁵，realized policy **stagnates dist≈0.093**（與 N 無關）。
  3. pessimism：calibrated（~0）且 **改善→0.069**。
  4. masking：deploy 0%、**達 0.065**。
  5. exact V\* 才讓 overestimation pathology 可量（真實醫療不可能）〔gottesman2019guidelines〕。
- **Figure/Table**：Fig 4 = offline datasize（main.tex fig:offline），證明 naive 高估+停滯 vs pessimism/mask 校準+改善。
- **確切數字**：全 repo ✅（offline_datasize/summary.json）。
- **狀態**：main.tex 已寫實，幾乎不用動。

### 6.5 Supplementary analyses（壓成短段，圖進 appendix）
- **核心訊息**：一連串防守與穩健性檢查，證明結論不是巧合、不是別的原因、是 mean-specific。
- **逐項（各 1–2 句 + 圖入 appendix）**：
  1. **Expert projection**【repo ✅】：clinician 自己 **16%** 落在 inadmissible；raw 殘留 deploy **8%**；**projected → 0.5%**、value 不變、agreement 0.65。這是 support projection，不是 imitation learning。（可並列隊友 KL 變體 ★。）
  2. **Robustness**【repo ✅】：失敗+修法跨 Q/SARSA/Dyna-Q 成立；`terminate` 下 vanilla 自然避開（deploy 85%→3–4%）→ **失敗是 mean-specific**（很好的防守）。補一句：terminate 下 Q/SARSA 的 dist 反而更差（0.107/0.108），masking 不論 strategy 都最好且穩。
  3. **No dead-ends**【repo ✅】：min V\*=0.198、無 dead-end、427/713 secured；mean 也壓平了 inadmissible 較高的 one-step death（0.032 vs 0.023）——誠實負面結果，反而支持主線。
  4. **SOFA×KL composition ★**：各 +0.004、**不疊加**（0.866 單獨、0.857 合併）、KL 縮 SE ~3×（appendix Table）。
  5. **Sample efficiency ★**：AA-PPO ~1.8× 快達 plateau（appendix；learning-curve PNG 要補真圖）。
- **護欄**：★ 三項（KL、SOFA×KL、sample-eff）入庫前不得寫死；8 頁超頁時這些先砍（已在 appendix）。

---

## 7. Discussion
- **唯一核心訊息**：為何 survival rate 藏住、為何用 known-dynamics 量尺、與 benchmark 自家 perturbation check 的差異、benchmark guidance，以及「什麼能遷移到真實 offline 醫療 RL、什麼不能」。
- **敘事 beats（main.tex 註解已列 5 段；逐段對應 reviewer Q）**：
  1. 為何 survival rate 藏住 → 需要 multi-metric + exact V\*。
  2. **〔Q16〕** 為何用 known-dynamics benchmark：exact V\* 是**量測工具非 optimization claim**；OOD/overestimation 是 offline RL 公認普遍問題，我們只是能精確量它〔kumar2020cql, kumar2019bear〕。
  3. **〔Q17〕** 與 benchmark 自家 perturbation check（〔choudhary2024icusepsis〕Appendix B.3）的差異：它量 **return robustness**（by construction 不敏感）；我們量 **selection rate / dist-V\* / mechanism / remedies**。
  4. Benchmark guidance：明確回報 inadmissible-action handling。
  5. **〔§9 external validity，護欄要求〕**：什麼能遷移、什麼不能 —— **直接貼 `17` §9 的 LaTeX 草稿**（已寫好 paragraph，citation keys gottesman2019guidelines / fujimoto2019bcq / kumar2020cql 已在 bib；**需補 auer2008ucrl、osband2013psrl**）。重點三句：(a) 真實世界沒有 exact V\*，連 gap 都量不到，只能靠有偏 OPE；(b) 補滿 gap 的 AA-MBRL 是 online + 在 716-state 上 trivial（UCRL/PSRL），不可用在病人身上；(c) 4 個 prior 不是天上掉的，是同一份 logged 資料的統計。**可遷移的是 support-aware 原則，不是分數。**
- **Figure/Table**：無。
- **確切數字**：少量引用即可（如 716-state、AA-MBRL online 性質）。
- **狀態**：main.tex 的 "Significance for offline medical RL" 段已草擬且語氣正確，**保留**；其餘四段 + §9 段待寫（§9 可直接貼）。
- **常見失敗模式**：把 Discussion 寫成結果複述；漏掉 §9（這是合併 paper 最容易被打的洞，護欄明令要寫）。

---

## 8. Limitations
- **唯一核心訊息**：benchmark-internal、tabular、非臨床、有限 seeds、clinician 本身不完全 admissible、deep/continuous & SAC 未測。
- **敘事 beats**：
  1. "unsupported" = 資料不足，非醫學錯誤；無臨床主張。
  2. mean-imputation failure 與 behavior-masking fix 是否遷移到 function-approximation / continuous / deep **未測**（併隊友：**未做 SAC、deep/continuous 未驗** ★ 但這句是承認限制、不需數字，可直接寫）。
  3. offline empirical-MDP sweep 是往 realistic finite-data 的一步，但仍 tabular。
  4. 5 seeds（但 support 診斷效應大：87%→0%、leakage +0.46→−0.80）。
  5. clinician policy 本身不完全 admissibility-respecting（benchmark 繼承的性質）。
- **狀態**：main.tex 已寫實，**只需併入隊友的「未做 SAC、deep/continuous 未驗」一句**。
- **護欄**：誠實，不要行銷式 limitation。

---

## 9. Conclusion
- **唯一核心訊息**：gap 是 mean-imputation 製造的人為缺陷，env 自帶解藥；inadmissible handling 應被回報，不該留給隱藏 default。
- **敘事 beats**：
  1. default mean 讓 unsupported actions 看起來 average → model-free 採用、survival rate 藏住代價。
  2. 用 exact V\* 把失敗定位到 behavior 層、比較 online/offline support-aware remedies。
  3. 收尾：inadmissible-action handling should be reported, not left to a hidden default；"the gap was an artifact of mean-imputation; the env ships the cure"（語氣是診斷收束，不是 SOTA）。
- **狀態**：main.tex 已草擬，只需 tighten + 加上 closing 那句。
- **護欄**：不得冒出正文沒講過的新主張。

---

## 10. Figure / Table budget（8 頁紀律：main ≈ 4 圖 3 表）
**Main**
- Table 1 — baselines（tiny）【repo ✅】。
- Fig 1 — overview schematic（**待畫**，`15` §4）。
- **Fig 2 — component ablation + $Q$-value leakage = ⭐ THE HERO FIGURE【repo ✅】。** 承載 punchline（機制：behavior 層 necessary & sufficient、部署 mask 不夠）。**版面/解析度/正文討論篇幅最高優先；不可砍、不可縮、不可被 Table 2 擠位。**
- Table 2 — merged main results（baselines + C1 masked Sarsa/Q/DQN/PPO + AA-MBRL，融隊友 Table2+3）★ = **配角（supporting breadth）**。它證「診斷普遍成立」，**不得搶 Fig 2 版面**；**版面緊張時先壓 Table 2、不動 Fig 2**（見 §0.0 防稀釋指令）。
- Fig 3 — penalty Pareto【repo ✅】（可加隊友 learning-curve inset ★）。
- Fig 4 — offline datasize【repo ✅】。

**Appendix（降級）**：隊友 learning curves ★（PNG 要補）、SOFA×KL 2×2 ★、expert/robustness/dead-end【repo ✅，各配一句正文】、500k 確認跑、AA-MBRL-Shaped/KL/Full（**跑完才放**）。

**砍掉**：隊友 "structure beats capacity" 大話；SAC 缺口的辯解（不提就不必辯）。**超 8 頁時先砍**：sample-efficiency inset、SOFA×KL（都已在 appendix）。

---

## 11. ✅ 本檔自帶的逐節 checklist（接 `spec.md` §4，補本 paper 專屬項）

**進攻型敘事（§0.0，賣相軸）**
- [ ] Abstract 第一句是 **phenomenon/instrument-first**（採 §0.0 定稿句），非 benchmark-first（§0.0、§1）
- [ ] Intro 開頭就拋出 **3 個 surprising findings** 鉤子 (a)/(b)/(c)（§0.0、§2）
- [ ] **punchline**（behavior 層 necessary & sufficient + exact $Q$-leakage）在 Abstract 與 Intro **各出現一次**（§0.0）
- [ ] Contributions：第 1 條 = **反駁 benign claim 並精確量測**；第 4 條 = **reusable exact-$V^\star$ protocol + 三診斷量**；跨演算法/AA-MBRL 列為 supporting（§0.0、§2）
- [ ] **Fig 2 = hero**，未被 Table 2 擠位；版面緊張先壓 Table 2（§0.0、§10）
- [ ] **全文無 priority/bravado**："first" / "novel for the first time" / "only theorize" / "nobody can measure" 一律不出現；所有賣點都是可驗證對比（exact ground-truth + 真實蒸餾資料 + 免 OPE）（§0.0 嚴格約束）
- [ ] **umbrella 名詞一致**：全文用 "OOD / unsupported-action pathology"；"overestimation" 只出現在 offline §6.4（其餘處最多寫成 offline RL 的「典型後果」）；"necessary and sufficient" 一律掛在 "in our ablation"（§0.0、§6.2）

**單一聲音 / 數字 / 護欄（執行軸）**
- [ ] 全文只有一個 thesis（§0.1）；無第二聲音（closes-the-gap 未升成主張）
- [ ] optimal 一律 0.875、admissible set 一律 "median 4 (mean 3.2)"、deploy headline 一律 87%(state)（§0.3）
- [ ] 同一張表的 cell 預算一致；跨預算數字都標 episode 數（§0.4）
- [ ] 每一個 ★ 數字都已入庫/重跑；未入庫者已從 prose 移除（§0 標記規範）
- [ ] AA-MBRL 全文以「remedy 光譜 model-based 端點」出現，無 SOTA / headline 0.874（§0.2）
- [ ] Discussion 含 §9 external-validity 段（已貼 `17` §9）（§7）
- [ ] Related Work 用 UCRL/PSRL 主動承認 tabular 可解再轉守為攻（§3）
- [ ] Fig 2（component ablation + Q-leakage）在 main，且未被壓縮（§6.2）
- [ ] 全文 benchmark-internal / 非臨床，無 clinical overclaim（§0.2）
- [ ] references.bib 補齊 auer2008ucrl / osband2013psrl / MIMIC-III / sb3 / behavior-reg / ng1999shaping（§3、§7）

---

## 12. ✅ Executor 開工前的 3 個決策（已拍板 2026-05-23 — 完整版見頂部 🔒 block）

1. **隊友 ★ 數字** → ✅ **直接採用她 PDF 數字寫入 v1，每個 ★ 標 provisional 註記**（`pending repo reproduction`）；她標 *in progress* 而無數字者（AA-MBRL-Shaped/KL/Full）omit。
2. **Protocol** → ✅ **v1 不重跑對齊**；同一張表內預算一致（Table 2 全 5×10⁵ 隊友列、我方機制表/圖全 5×10⁴），每張表標 episode 數，用「vanilla Q 兩預算皆 0.785」橋接。
3. **Title / Contribution 3** → ✅ **Title 維持現有**；contribution 3 **保留**跨演算法 + AA-MBRL（supporting evidence 語氣、AA-MBRL 為端點）。

> ⚠️ 投稿前未了事項（**非 v1 阻擋**，但 camera-ready 前必清）：(a) 所有 ★ 數字最終重現入庫、或確認 provisional 註記；(b) learning-curve PNG 補真圖；(c) references.bib 補 `auer2008ucrl` / `osband2013psrl` / MIMIC-III / sb3 / behavior-reg / `ng1999shaping`；(d) overview Fig 1 待畫。
