# 17 — Merged Paper Outline (A-led)

> 用途：把兩份草稿（Claude 主軸的「OOD-action 診斷/機制」+ 組員的「Admissibility-Aware RL closes the gap」）
> 融成**一隊一篇**。決策已定：**一隊一篇（必須合併）、以診斷/機制當主軸（A-led）**。
> Deadline 2026-05-25 23:59（本檔建立於 2026-05-22，剩 3 天）。NeurIPS 2026 format，main 4–8 頁。
>
> 兩份來源：
> - A（主軸）= `paper/main.tex` + `submission/`（exact V*、component ablation、penalty sweep、offline datasize、expert projection、robustness、dead-ends）
> - B（併入）= 組員草稿「Admissibility-Aware RL Closes the Optimality Gap」（C1 masked baselines、C2 AA-MBRL、C3 AA-PPO SOFA/KL、cross-algorithm、sample-efficiency、2×2 composition）

---

## 0. 為什麼 A-led 合併會「更好」而不是更糟（一句話備忘）

兩篇的致命弱點互為解藥：B 證明 mask 有效卻講不出**為什麼** → A 的機制就是 why；A 只有 Q-family 太窄 → B 的 PPO/DQN 廣度把它一般化。
**前提**：B 的結果從「主張」降級為「證據」，丟掉 overclaim（"structure beats capacity"、把 "reaches oracle" 當戰績）。
反過來 B-led 會同時繼承「masking 是常識」+「tabular MDP 本來就 trivially 解得掉」雙重攻擊面。

---

## 1. Unified thesis（全文唯一的一句話）

> ICU-Sepsis 的 default mean-imputation 製造了一個 **OOD-action pathology**，把 model-free RL 卡在 random/clinician baseline，而 survival rate 把它藏起來；
> 我們把失敗**定位到 behavior-level sampling**（機制），並證明**用 benchmark 自己出廠的結構**——從 soft support penalty → conservatism → admissibility masking → model-based planning——
> 能移除 pathology 並把 gap 補起來，且**跨演算法、online 與 offline 都成立**。

**Title 候選（A-led，但收進 "closing" 的弧線）：**
1. *When Mean Imputation Hides Unsupported Actions: Diagnosing and Closing an Out-of-Distribution Action Gap on ICU-Sepsis*（推薦）
2. *The Hidden Cost of Mean Imputation: An OOD-Action Failure and Its Structural Remedy on ICU-Sepsis*

---

## 2. Contributions（合併後 4 點）

1. **Failure diagnosis（被 survival rate 藏住）.** default `mean` 下 vanilla 在 ~87% 狀態部署 unsupported action、J≈random/clinician、dist-V*≈0.090；
   **且在 5×10⁵ episodes 仍不改善**（非 under-training）。 ← A 診斷 + B 的大預算確認
2. **Mechanism localization.** component ablation 證明 **behavior-level masking 必要且充分**（== full mask），target-only/policy-only 不足；Q-value-leakage +0.46→−0.80 給出機制。 ← A（**全文最強、不可砍**）
3. **Remedy spectrum, exactly evaluated, across algorithms, online & offline.** soft penalty(λ) → CQL conservatism → hard mask → **model-based AA-MBRL**；
   跨 Sarsa/Q/DQN/PPO 都成立且**效果隨 baseline 變強**；offline 有限資料下 naive 高估(+0.21)且停滯、pessimism/mask 校準並隨資料改善。 ← A+B 合併
4. **Benchmark guidance + release.** inadmissible-action handling 必須明確回報；釋出 one-command scripts。 ← A

> 註：組員的「4 priors the benchmark ships but baselines discard」是很好的**組織說法**，保留進 Intro 當鋪陳；
> 但 P1（admissibility）/P2（model）走主線，P3（SOFA）/P4（clinician）降為 supplement。**不要**把它升成 thesis。

---

## 3. Section-by-section（含資產對應與 owner）

| § | 內容 | 用哪邊的資產 | Owner |
|---|---|---|---|
| **Abstract** | 以 unified thesis 重寫；保留 A 的「survival rate hides it」+ B 的「closes the gap」收尾，但語氣是診斷不是 SOTA | 改寫 A 現有 abstract | 整合 |
| **1 Introduction** | medical RL 需可重現 benchmark → OPE 不可靠 → ICU-Sepsis 用 known-dynamics 解決 → 但要處理 data-unsupported actions，default mean 是 hidden choice → reframe 成 offline-RL OOD problem → known dynamics = exact V* 當量測工具。**鋪 B 的「benchmark 附 4 個 prior、baseline 丟掉」當引子** | A 大綱(core_docs/15 §2) + B intro 的 4-priors 句 | 待寫 |
| **2 Related Work** | (a) medical RL benchmarks (b) offline RL & OOD actions (c) action masking【併 B 的 deep-RL masking + sb3 MaskablePPO】 (d) tabular model-based: UCRL/PSRL【B 已寫，**用它來預先承認 "tabular 可解" 並轉守為攻**】 (e) reward shaping / behavior-constrained (f) eval pitfalls | A(core_docs/12) + **B 的 related work 三段直接併入** | Codex + 組員 |
| **3 Background** | ICU-Sepsis 設定、Eq.(mean)、admissibility τ=20、median\|A(s)\|=4(B 寫 3.2)。**統一一個數字** | A §background（已寫好） | 已完成 |
| **4 Method** | remedy spectrum：(i)vanilla (ii)support penalty λ (iii)CQL conservatism (iv)masking 拆 behavior/target/policy。**(v) AA-MBRL：online empirical model 上重解 admissibility-constrained Bellman**（併 B §3.2）。metrics: dist-V*, deploy-unsupp, Q-leakage, overestimation, expert-agreement | A §method（已寫）+ **B 的 AA-MBRL 段落併入為 spectrum 最右端** | 整合 |
| **5.1 The hidden failure (Claim 1)** | 87% / J≈baseline / dist 0.090；**強調在 5×10⁵ 仍不改善（引 B 的大預算 vanilla=0.785）** | A §failure + B Table 2 vanilla 列 | 整合 |
| **5.2 Mechanism (Claim 2)** | component ablation 表 + Q-leakage 曲線。**全文核心** | A Fig component_ablation + Table | 已完成 |
| **5.3 Remedy spectrum — online, cross-algorithm (Claim 3a)** | penalty Pareto 圖；**併入 B 的跨 Sarsa/Q/DQN/PPO 表 + 「效果隨 baseline 變強」+ paired-t**；AA-MBRL 補到 0.874 收尾（**framing：連最樸素地用結構都能補滿一個人為 gap**，不是「我們贏了」） | A penalty_tradeoff + **B Table 2/Table 3** | 整合 |
| **5.4 Remedy spectrum — offline finite-data (Claim 3b)** | naive 高估+停滯 vs pessimism/mask 校準+改善 | A offline_datasize | 已完成 |
| **5.5 Supplementary（壓縮成短段，圖進 appendix）** | expert projection 1 段；robustness「terminate 讓 vanilla 自然避開→failure 是 mean-specific」1 句（**很好的防守**）；no-dead-ends 1 句；SOFA×KL composition 1 句（+0.004、不疊加、KL 縮 SE 3×） | A expert/robustness/deadend + **B Table 4** | 整合 |
| **6 Discussion** | (1)為何 survival rate 藏住、需要 multi-metric+exact V* (2)為何用 known-dynamics benchmark：量測工具非 optimization claim〔Q16〕 (3)與 benchmark 自家 B.3 perturbation check 的差異〔Q17〕 (4)benchmark guidance (5)offline medical RL 意義（A 已有草稿段） | A §discussion 大綱 | 待寫 |
| **7 Limitations** | tabular、benchmark-internal、非臨床、5 seeds、clinician 本身不完全 admissible。**併 B：未做 SAC、deep/continuous 未測** | A §limitations（已寫）+ B 一句 | 微調 |
| **8 Conclusion** | A 現有結論 + 「the gap was an artifact of mean-imputation; the env ships the cure」 | A §conclusion | 微調 |

---

## 4. Figure / Table budget（8 頁紀律：main 約 4 圖 3 表）

**Main paper（保留）**
- Table 1 — baselines（tiny）
- Fig 1 — overview schematic（mean imputation 讓 unsupported 變 learnable）→ **還沒畫，要做**
- Table 2 — **merged main results**：baselines + C1 masked(Sarsa/Q/DQN/PPO) + AA-MBRL，欄位 final return / gap / deploy-unsupp（融 B Table2+Table3 精華）
- Fig 2 — component ablation + Q-leakage（A，**最大不可砍**）
- Fig 3 — remedy spectrum penalty Pareto（A），可把 B 的 learning-curve 做成小 inset
- Fig 4 — offline datasize（A）

**Appendix（降級）**
- B 的 learning curves（sample efficiency；注意她原稿 PNG 沒 render，要補圖）
- B 的 SOFA×KL 2×2（Table 4）
- A 的 expert_prior_curve、robustness、deadend_structure（各配一句正文）
- AA-MBRL-Shaped/KL/Full（**in progress → 跑完才放，否則不放**）

**砍掉**：B 的 "structure beats capacity" 大話；SAC 缺口的辯解（不提就不必辯）。

---

## 5. Protocol reconciliation（50k vs 500k）— 必做，否則表格自相矛盾

事實：A 跑 **5×10⁴ (50k)**，B 跑 **5×10⁵ (500k)**。好消息是 **vanilla Q 在兩個預算都是 0.785**（B Table 2 證實），所以 A 的失敗故事在 500k 仍成立、甚至更強（「非 under-training」）。

**方案（推薦，成本最低且最一致）：**
1. **凡是進「同一張表」的 cell，統一用 5×10⁵。** 直接沿用 B 已有的 cross-algorithm 數字；A 的 vanilla/masked 重跑 500k 對齊（scripts 已存在，改 config episode 數即可）。
2. **機制 sweep（component ablation / penalty λ / offline datasize）維持 5×10⁴** 以省算力，但**加一組 5×10⁵ 確認跑**（只跑 vanilla / behavior-mask / full-mask 三格），證明 leakage 與 dist 結論不變，放 appendix。正文寫一句「conclusions identical at 5×10⁵, App X」。
3. **統一雜項數字**：median \|A(s)\|（A 寫 4 / B 寫 3.2）、optimal（0.875 vs 0.88）、deploy-unsupp（A 0.87 / B 0.79–0.83）——挑一套來源，全文一致。

**驗證任務（合併前必跑一次確認）：** component-ablation 的 ordering 與 leakage 量級在 500k 是否仍成立（behavior-mask 必要且充分這點是結構性的，預期不變，但 leakage 數值會動，要更新表）。

---

## 6. Framing guardrails（避免合併變更糟的紅線）

- ✅ 保留 A：「benchmark-internal、非臨床、exact V* 是量測工具不是 optimization target」。
- ✅ 把 B 的 **AA-MBRL → 定位成「即使樸素地用 P2 也能補滿一個人為 gap」**，支撐結構論點。
- ❌ 不要寫 "structure beats capacity"、不要把 "0.874 / gap 0.001" 當 headline 戰績。
- ❌ 不要兩個聲音並存：全文只有一個 thesis（§1）。
- ⚠️ Related Work 用 UCRL/PSRL **主動承認** tabular MDP 可被 trivially 解，然後說「正因如此，我們的貢獻是診斷與機制，不是 regret/最優性」——把 reviewer 最可能的攻擊先講掉。

---

## 7. Division of labor（建議）+ 3 天時間軸

| 誰 | 負責 |
|---|---|
| jeff（你） | 合併整合、protocol 對齊、Method 把 AA-MBRL 接進 spectrum、確認 A 實驗 500k 重跑 |
| 組員 | 提供 AA-MBRL/PPO/DQN 原始結果、依統一 protocol 重跑、補 learning-curve PNG、Related Work 的 deep-RL masking/model-based 段 |
| Codex | Related Work 整合、references.bib 補 B 引用（Johnson MIMIC-III、Auer UCRL、Osband PSRL、Huang masking、Raffin sb3、Wu/Nair behavior-reg） |
| Claude | 草寫 Intro/Discussion/Conclusion prose、合併 Table 2、anonymity audit |

**時間軸（5/22→5/25）**
- **D1 (5/22)**：定 thesis/title/contributions（本檔）；啟動 A 的 500k 重跑（背景跑）；Codex 開始 Related Work 併入。
- **D2 (5/23)**：寫 Intro + Related Work + Method(含 AA-MBRL)；合併 Table 2；畫 Fig 1 overview。
- **D3 (5/24)**：寫 Discussion + Conclusion；補 appendix；確認跑回填數字；全文一致性（雜項數字）。
- **D4 上午 (5/25)**：Overleaf 編譯（放 neurips_2026.sty + 圖）、頁數壓到 ≤8、line numbers、**anonymity audit**、投稿。

---

## 8. Open risks / 待確認

- [ ] component-ablation 在 500k 的 leakage/ordering 確認（驗證跑）
- [ ] B 的 learning-curve PNG 實際存在且可重現（原稿是 placeholder）
- [ ] AA-MBRL-Shaped/KL/Full 是否跑得完；跑不完就只留 AA-MBRL 主格
- [ ] 8 頁是否塞得下——若超，先砍 sample-efficiency inset 與 SOFA×KL（已在 appendix）
- [ ] references.bib 是否含 B 所有引用（目前 21 筆，需補 UCRL/PSRL/MIMIC-III/sb3 等）
