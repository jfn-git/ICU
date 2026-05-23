# 19. 團隊簡報（合併版）— 合併後的 paper 我們在說什麼、怎麼防守、誰做什麼

> 給組員的內部簡報，5–10 分鐘讀完掌握**合併後**的全貌。繁體中文，技術詞保留英文。
> 這是 `16_team_briefing_claude.md`（你那篇）與 `18_teammate_paper_explained.md`（隊友那篇）合併後的版本，架構依 `17_merged_paper_outline.md`（A-led 決策）。
> 決策已定：**一隊一篇（必須合併）、以你的「診斷/機制」當主軸、隊友的「跨演算法廣度 + AA-MBRL + SOFA/KL」當證據。**
> ⚠️ **資料狀態**：你那邊的數字都來自 repo（`results/*/summary.json`、`submission/`，可重現）；**隊友的數字目前只在她 PDF，code/results 都還不在 repo**（見 §5 的合併卡點）。表格已標來源。

---

## 0. 30 秒總覽

我們在 **ICU-Sepsis**（用真實 ICU 病歷做成的小型 tabular RL 環境）上發現：**預設設定會讓 AI 偷偷依賴「沒有資料根據的治療選項」，而傳統成績單（存活率）完全看不出來**。我們把這件事**診斷清楚、定位到根因（行為層）、比較一整排修法**，並證明**用環境自己附的結構**（從輕罰 → 保守 → 硬性禁止 → 線上 model-based）能把問題移除、把離最佳解的差距補起來——而且**跨多種演算法、線上與離線都成立**。全程靠這個環境少見的「可算出精確最佳解 V\*」乾淨量測。

**一句話貢獻**：我們在一個有「標準答案」的醫療 benchmark 上，**指出並量化了一個被預設藏起來的 OOD-action 失敗、定位到它的根因、並用一整族 support-aware 修法（含 model-based）跨演算法、線上/離線地把它補上**。

**和合併前兩篇的關係**：你那篇給「**為什麼會失敗 + 根因 + 為何超出本環境也重要**」（深度、普遍性）；隊友那篇給「**跨 Sarsa/Q/DQN/PPO 都成立 + 用結構能補到 oracle**」（廣度、建構收尾）。兩個一般性方向（跨現象 vs 跨學習器）互補。

---

## 1. 我們解決的問題（用具體情境理解）

> 幫助理解的直覺，**不是**臨床主張。

> 病人狀況 `s`：歷史病歷裡醫師只在這狀況試過 **3 種**處置，剩下 **22 種**幾乎沒人用，資料不足以判斷效果。
>
> ICU-Sepsis 為了讓 25 種 action 都能用，做了預設決定（`mean` strategy）：**把那 22 種「沒人試過」的處置，假設效果＝那 3 種試過處置的平均。**
>
> 於是 AI 看到的世界是「選沒根據的處置也不會出事，平均還行」，結果它 **85% 的時間都在選沒根據的處置**，而**存活率看起來正常**（因為在模擬器裡這些動作被定義成「等於隨機挑一個有根據的」）。
>
> 代價：AI **根本沒學會挑「最好」的處置**，成績（J=0.785）跟「隨機亂治」(0.780)、「照抄醫師」(0.782) 幾乎一樣，離最佳 (0.875) 很遠。

**術語對照**：「沒資料根據的處置」=inadmissible/unsupported/**OOD action**；「用平均值填補」=**mean imputation**；「離最佳多遠」=**distance-to-V\***（主 metric，V\*=精確最佳存活率）。

**為什麼值得做**：這正是整個 **offline RL** 的核心難題（OOD action），但真實醫療資料無法精確驗證（只能用有雜訊的 OPE）。ICU-Sepsis 因 dynamics 完全已知、**能算精確 V\***，是難得能「乾淨量測」這問題的環境。

---

## 1.5 我們研究的價值 — 對外要怎麼說它有意義（合併版）

**一句話**：醫療 RL 幾乎都是 **offline**，最大的坑是「**資料不支撐的動作**」。我們在一個**能看到標準答案**的環境裡把這個坑「**看得見、量得準、找到根因**」，再證明**用環境自己附的結構**就能修好——而且**換演算法、換到離線有限資料都成立**。

**價值鏈（前 3 步領域共識、第 4–5 步我們的貢獻）**
1. 醫療 RL = offline（公認）
2. offline 的核心難題 = OOD / unsupported action（公認）
3. 「有些治療很少被試」是醫療資料的本質（公認）
4. **pipeline 怎麼處理沒資料的動作，會默默改變學到的策略，而存活率看不出來**（← 我們乾淨示範 + 定位根因 + 給協議）
5. **而修法不必發明新東西——用環境本來就附的結構（support-aware 行為層學習），跨多種演算法都能把差距補上**（← 合併後新增的建構面）

**對外講價值的三個層次（看對象選用詞）**
- **保守版（最安全）**：ICU-Sepsis 使用者別只報存活率，要報 inadmissible 處理方式 + distance-to-V\* / unsupported rate；光把被忽略的 admissibility 放回 baseline 就有穩定 +0.026~+0.036（跨演算法、p<0.001）。
- **可推版（賣點）**：offline 醫療 RL 先天資料覆蓋不均，我們提供「**失敗診斷 + 量測協議 + support-aware 處方**」，並示範**結構優先於容量**——給推動 offline 醫療 RL 的人參考的方法論。
- **🚫 不能講**：改善敗血症治療 / 更安全 / 可部署。

**⚠️ 一定要同時說的誠實話**
- 可遷移的是**現象 + 機制 + 協議 + practice**，**不是具體數字**；tabular、benchmark-internal 受控示範，沒在真實 ICU/deep RL 上驗。
- **AA-MBRL 補到 oracle（0.874）不是賣點也不令人意外**——716-state tabular MDP 本來就 trivially 可解（UCRL/PSRL）。它是 remedy 光譜的「model-based 端點」，用來支撐「**gap 是 mean-imputation 製造的人為缺陷**」這個論點，**不要寫成「我們達到 SOTA」**。

**撐場引用**：Gottesman 2019《Guidelines for RL in healthcare》（把其中一條警告做成可量測案例）；offline RL 的 BCQ/CQL/pessimism（OOD 重要但平常量不乾淨，我們給 exact-eval 實例）；Ng et al. 1999（SOFA shaping 的理論正當性）；ICU-Sepsis 原 paper Choudhary 2024（gap 相對它，我們證明可被結構補上）。

---

## 2. 目前成果（數據 + 圖）

### 2.0 實驗地圖（先看這個）

```
核心問題：ICU-Sepsis 預設 mean imputation 有沒有代價？學習者該怎麼辦？怎麼修最好？
│
├─[基礎] Baseline + exact V*
│        建立「尺」(Random/Expert/Optimal + 精確最佳解)，揭露 survival rate 區間很窄
│                         │ ▼
├─[Claim 1｜失敗] 預設下 vanilla 會出問題嗎？普遍嗎？
│        ├ 你：P1 vanilla 端點 — 85% 選 unsupported、成績≈隨機、survival 看不出
│        └ 隊友：跨 Sarsa/Q/DQN/PPO 都失敗，且 5×10⁵ 仍不改善（非 under-training）★
│                         │ ▼
├─[Claim 2｜根因] 問題出在「哪一步」？  ← 機制核心（全文最強、不可砍）
│        └ 你：T1 component ablation + Q-leakage — 定位到 behavior 層
│                         │ ▼
├─[Claim 3｜修法光譜] 怎麼修？從軟到硬到 model-based，哪種好？
│        ├ 你：penalty → CQL → hard mask（線上、已知模型）
│        ├ 隊友：跨演算法 mask 都有效、效果隨 baseline 變強 ★
│        ├ 隊友：AA-MBRL（線上 model-based）補到 oracle 0.874 ＝ 光譜 model-based 端點 ★
│        ├ 你：T2 offline 資料量 sweep — 有限病歷下 naive 高估、pessimism/masking 才可靠
│        └ 你：P2 expert projection（＋隊友的 KL 變體並列）
│                         │ ▼
└─[防守層] 結論穩嗎？泛用嗎？
         ├ 你：T3 robustness — 跨 Q/SARSA/Dyna 成立；mean 特有(terminate 下 vanilla 自己會避開)
         ├ 隊友：sample efficiency — AA-PPO ~1.8× 快達 plateau ★
         └ 你：P0 dead-end — 排除「有絕境狀態」的另類解釋（誠實負面結果）

★ = 隊友貢獻，目前只在她 PDF、尚未進 repo（見 §5）
```

**一句話記法**：Baseline=給尺；Claim1=證明有病（你定點 + 隊友證跨演算法普遍）；Claim2=找病根（核心）；Claim3=開藥單比較（你軟硬光譜 + 隊友 model-based 端點 + 跨演算法 + 離線）；T3/P0=確認不是巧合也不是別的原因。

### 2.1 合併成果表

> 圖在 `submission/figures/`，數字在 `results/*/summary.json`（你的部分）。隊友部分標「PDF-only」。

| 實驗 | 它回答什麼 | 關鍵數字 | 來源/可重現? | 等級 |
|---|---|---|---|---|
| **Baseline** | 環境有沒有裝壞？ | Random 0.780 / Expert 0.782 / Optimal **0.875** | repo ✅ | 基礎 |
| **P1 penalty sweep** | 輕罰→硬禁止哪個好？ | vanilla dist 0.090、unsupp 85%；hard mask dist **0.069**、unsupp 0；penalty 壓得到 0% 但 dist 卡 0.085 | repo ✅ | **main** |
| **T1 component ablation** | 失敗根因在哪一步？ | **behavior masking 必要且充分**(=full,0.069)；只擋 target/只擋部署都不夠；Q-leakage **+0.46→−0.80** | repo ✅ | **main 核心** |
| **跨演算法 mask（C1）** | 只是 Q 的怪癖嗎？ | mask 提升 Sarsa +0.010 / Q +0.026 / PPO +0.029 / DQN +0.036（後三 p<0.001）；效果隨 baseline 變強 | **PDF-only ★** | **main**(廣度) |
| **AA-MBRL（C2）** | 用環境的 model 能補多少？ | **0.874**，gap **0.001**（光譜 model-based 端點）| **PDF-only ★** | main(端點) |
| **T2 offline 資料量** | 只有 N 筆病歷時呢？ | naive **高估 +0.21 且卡 0.094**；pessimism 校準(~0)到 0.069；masking unsupp 0、到 0.065 | repo ✅ | **main** |
| **P2 expert（＋KL）** | 醫師引導有用嗎？ | 醫師自己 16% 沒根據；raw 殘留 8%；**投影→0.5%**，value 不變、agreement 0.65。隊友 KL 變體並列 | repo ✅（KL 部分 PDF ★）| supplement |
| **SOFA×KL composition（C3）** | 嚴重度/醫師 prior 疊得起來嗎？ | 各 +0.004 但**不疊加**（0.866 單獨、0.857 合併）；KL 讓 SE 縮 ~3× | **PDF-only ★** | supplement(appendix) |
| **T3 robustness** | 只是 mean 特有嗎？ | Q/SARSA/Dyna 都一樣；`terminate` 下 vanilla unsupp 85%→~4% | repo ✅ | supplement |
| **sample efficiency** | masking 也更省資料嗎？ | AA-PPO ~105k 達 PPO 在 185k 的水準（~1.8×）| **PDF-only ★** | supplement |
| **P0 dead-end** | 有絕境狀態嗎？ | **沒有**(min V\*=0.198)；誠實負面；mean 也藏了 inadmissible 較高即刻死亡風險 | repo ✅ | supplement |

**三句話總結**：
1. **失敗存在且有代價，且普遍**：vanilla 85% 用沒根據動作、成績只到隨機/醫師水準，survival 看不出；跨 Sarsa/Q/DQN/PPO 都這樣，且 5×10⁵ 仍不改善。
2. **根因被定位**：問題在「訓練時被選到、被更新」（behavior 層），不是 bootstrap 或部署層。
3. **修法成譜**：penalty < CQL pessimism < hard masking < model-based(補滿)；離線有限資料下 naive 會高估、pessimism/masking 才可靠。

---

## 3. 我們對 paper 的想像（合併版）

**Working title**：*When Mean Imputation Hides Unsupported Actions: Diagnosing and Closing an Out-of-Distribution Action Gap on ICU-Sepsis*（詳 `17_merged_paper_outline.md`）

**統一 thesis（全文唯一主張）**：mean-imputation 製造 OOD-action pathology → survival rate 藏住 → 機制定位在 behavior-level sampling → 用 benchmark 自帶的結構（penalty → conservatism → mask → model-based）把問題移除並補上 gap，**跨演算法、online/offline 都成立**。

**三層 claim stack**
- **Claim 1 — Failure**：mean imputation 讓 vanilla 85% 用沒根據動作、成績≈隨機，survival 藏住；**跨演算法 + 5×10⁵ 仍不改善**（你 + 隊友）。
- **Claim 2 — Mechanism**：component ablation 證根因在 behavior 層 + Q-leakage（你，核心）。
- **Claim 3 — Remedy spectrum**：soft penalty → CQL → hard mask → **model-based AA-MBRL**；跨 Sarsa/Q/DQN/PPO；online + offline（你 + 隊友合併）。

**我們有/沒有提出什麼（誠實邊界）**
- ✅ 處方（agent 層）：別跑 vanilla，要 **behavior-level support-aware learning**；masking 最佳，CQL pessimism 是最佳軟解，model-based 用環境結構可補滿。
- ✅ 建議（benchmark 使用者）：明確報告 inadmissible 處理 + distance-to-V\* / unsupported rate。
- ❌ **沒有**發明新 RL 演算法、沒提新補值法。masking/model-based 都不新；新的是「**證明失敗必須在 behavior 層修、軟解都被它 dominate、且 gap 是 mean 製造的人為缺陷**」+ exact V\* 精確比較 + 跨演算法驗證。
- ⚠️ 被問「你們的新方法是什麼」→ 答「我們的**處方**是 behavior-level support-aware learning，並用 exact V\* + 跨演算法證明它優於軟性替代」，**不要說「發明了某演算法」**，**也不要把 AA-MBRL 0.874 講成戰績**。

**章節 outline + 負責人**（細節在 `17_merged_paper_outline.md` §3）

| 章節 | 狀態 | 合併動作 | 負責人 |
|---|---|---|---|
| Abstract | 改寫 | 統一 thesis；診斷語氣 + closing 弧線 | ____ |
| 1. Introduction | `\todo` | A 大綱 + 隊友「4 priors」當引子 | ____ |
| 2. Related Work | `\todo` | 搬 `12` + 併隊友的 deep-RL masking / UCRL-PSRL 段 | Codex |
| 3. Background | ✅ 已寫 | 統一 median\|A(s)\| 等雜項數字 | ____ |
| 4. Method | ✅ 已寫 | 把 **AA-MBRL** 接進 spectrum 最右端 | ____ |
| 5. Experiments | ✅ 已寫 | 併 Table 2（跨演算法 + AA-MBRL）、加 Claim1 跨演算法 | ____ |
| 6. Discussion | `\todo` | Q16/Q17/B.3 + 「gap 是人為缺陷」 | ____ |
| 7. Limitations | ✅ 草擬 | 併隊友：未做 SAC、deep/continuous 未驗 | ____ |
| 8. Conclusion | ✅ 草擬 | 收「gap 是 mean 製造、env 自帶解藥」 | ____ |

**Figure budget（8 頁紀律，main 約 4 圖 3 表）**：main = Table1 baselines、Fig1 overview(待畫)、Table2 跨演算法+AA-MBRL、Fig2 component ablation(核心)、Fig3 penalty Pareto、Fig4 offline；appendix = sample efficiency、SOFA×KL、expert/robustness/dead-end。

**時間線**：5/25 投稿 → 5/29 review → 6/1 rebuttal → 6/5 discussion → 6/8 decision → 6/15 oral/poster。

---

## 4. 潛在攻擊 vs 我們的防守

> 完整在 `reviewer_anticipated_questions.md`(Q1–Q17)。合併後最該記住的：

1. **「tabular，不是 deep RL。」** → benchmark-level 分析，不是新演算法；tabular 才能算精確 V\*、避開 OPE 雜訊。**而且我們現在有 PPO/DQN 廣度**（隊友 C1）。
2. **「不就是 masking？novelty?」** → 不是發明 masking；貢獻是**診斷 + 定位（component ablation）+ 修法光譜（含 model-based）+ 跨演算法驗證**。
3. **【最重要 Q17】「inadmissible = 隨機合法動作，所以無害。」** → 「等於隨機合法」**正是代價**：隨機合法 < 最佳合法，所以 vanilla≈隨機(0.785 vs 0.780)；真實部署不會剛好等於平均，才危險。
4. **【Q16】「exact V\* 是 toy？」** → exact V\* 是**量尺不是賣點**；OOD/overestimation 是 offline RL 公認普遍問題，我們只是能精確量它。
5. **「只有 5 seeds。」** → 主結論靠**大效應 support 診斷**（85%→0、leakage +0.46→−0.80），不靠微小存活率差。
6. **「臨床建議？」** → 不是。全文 benchmark-internal / data-support。
7. **【合併新增】「AA-MBRL 補到 oracle 不意外，小 tabular MDP 本來就可解。」** → **同意**，所以我們把它定位成 remedy 光譜的 **model-based 端點**，用來證明「gap 是 mean 製造的人為缺陷」，**不是 SOTA claim**；UCRL/PSRL 我們在 Related Work 已主動承認。
8. **【合併新增】「兩種預算（50k vs 500k）？」** → vanilla Q 在兩個預算**都是 0.785**，失敗持續、非 under-training；同表的 cell 統一在單一預算。
9. **【合併新增・最該準備】「如果要做真正可部署的 offline 醫療 RL，這種『用結構補 gap』成立嗎？」**
   → **大半不成立，而且我們明說它 benchmark-internal。** 三個理由：(a) 真實世界沒有 exact V\*，**連 gap 都量不到**，只能靠有偏的 OPE（Gottesman 2019）；(b) 補滿 gap 的 AA-MBRL 是 **online**（需重新互動），**不能用在病人身上**，且在 716-state 上補滿本來就 trivial（UCRL/PSRL）；(c) 那 4 個 prior 不是天上掉的，是**從同一份 logged 資料算出來的統計**。**真正可遷移的不是分數，是 support-aware 原則**（對沒資料根據的動作保持悲觀，BCQ/CQL），那正是我們的診斷/機制 + T2 offline sweep。→ 完整 Discussion 草稿見 `17_merged_paper_outline.md` §9。

---

## 5. 現在還缺什麼 / 組員可認領的任務

**🔴 合併最大卡點（最優先）**
- [ ] **把隊友的 code/results 拿進 repo 或重跑**：目前 AA-MBRL / 跨演算法 / SOFA-KL / sample-efficiency 全不在 repo，且 AA-MBRL-Shaped/KL/Full 她自標「in progress」。**這些數字進不了可重現的 paper，就只能砍或重跑。**（負責人：隊友 + jeff）
- [ ] **Protocol 對齊**：同表 cell 統一 5×10⁵；機制 sweep 維持 5×10⁴ + 一組 500k 確認跑放 appendix。

**必補**
- [ ] **寫 prose**：Introduction、Related Work（搬 `12` + 隊友段）、Discussion（Q16/Q17/B.3 + AA-MBRL 定位）。
- [ ] **合併 Table 2**：baselines + 跨演算法 mask + AA-MBRL。
- [ ] **Overview Figure 1**：照 `15` §4 schematic 畫。
- [ ] **隊友 learning-curve PNG**：她原稿是 placeholder，要補真圖。
- [ ] **references.bib**：補 UCRL(Auer)、PSRL(Osband)、MIMIC-III(Johnson)、sb3 MaskablePPO、Wu/Nair behavior-reg。
- [ ] **統一雜項數字**：median\|A(s)\|(4 vs 3.2)、optimal(0.875 vs 0.88)、deploy-unsupp。

**收尾**
- [ ] per-seed scatter（防「5 seeds 太少」）；figure captions 寫「證明什麼」。
- [ ] language audit（移除 clinical overclaim）；**anonymity audit**（無姓名/學校/真實 GitHub）。
- [ ] 8 頁紀律：超頁先砍 sample-efficiency inset 與 SOFA×KL（已在 appendix）。

**分工建議**：jeff＝合併整合 + protocol 對齊 + Method 接 AA-MBRL；隊友＝交可重現 code/results + 重跑 + learning-curve + Related Work deep-RL/model-based 段；Codex＝Related Work 整合 + references.bib；Claude＝Intro/Discussion/Conclusion prose + 合併 Table 2 + anonymity audit。

---

**一句話給組員**：合併後的故事是「**benchmark 偷藏一個失敗 → 我們診斷、定位根因、用環境自帶的結構從軟到硬到 model-based 把它補上，跨演算法、線上/離線都成立，全程精確量測**」。你的深度 + 隊友的廣度互補，比兩篇單獨都強。**現在最關鍵的卡點是把隊友的結果變成 repo 內可重現的數字**，其次才是補 prose 與上 Overleaf。
