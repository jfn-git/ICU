# 16. 團隊簡報（Claude 版）— 我們做了什麼、paper 想像、攻防

> 給組員的內部簡報，5–10 分鐘讀完就能掌握全貌。繁體中文，技術詞保留英文。
> 數字皆以 `results/*/summary.json` 與 `submission/README.md` 為準（每項標了來源檔）。
> 與 codex 版（`16_team_briefing.md`）並排，可合併。

---

## 0. 30 秒總覽

我們在 **ICU-Sepsis**（一個用真實 ICU 病歷做成的小型 RL 環境）上，發現它**預設的設定會讓 AI 偷偷依賴「沒有資料根據的治療選項」，而且傳統成績單（存活率）完全看不出來**。我們把這件事**診斷清楚、定位到根因、並比較一整排修法**，全程用這個環境少見的「可以算出精確最佳解」的優勢來精確衡量。

一句話貢獻：**我們指出並量化了 ICU-Sepsis 一個被預設藏起來的 OOD-action 失敗，定位到它的根因（行為層），並用精確評估比較了一族 support-aware 修法。**

---

## 1. 我們解決的問題（用具體情境理解）

**先看一個情境**（這是幫助理解的直覺，**不是**我們 paper 的臨床主張）：

> 想像某個病人狀況 `s`。歷史病歷裡，醫師其實只在這個狀況下試過 **3 種**處置；剩下 **22 種**幾乎沒人用過，資料根本不足以判斷它們的效果。
>
> ICU-Sepsis 為了讓 25 種動作都能被 RL 使用，做了一個預設決定（叫 `mean` strategy）：**把那 22 種「沒人試過」的處置，假設它們的效果 = 那 3 種試過處置的平均。**
>
> 於是 AI 看到的世界是：「選一個沒根據的處置也不會出事，平均來說還行。」結果它**85% 的時間都在選這些沒根據的處置**，而**存活率看起來正常**——因為在這個模擬器裡，這些動作被定義成「等於隨機挑一個有根據的處置」。
>
> 代價是：AI **根本沒學會挑「最好」的處置**，只是在亂選一個平均值。它的成績（policy value 0.785）跟「隨機亂治」(0.780) 和「照抄醫師」(0.782) 幾乎一樣，離最佳 (0.875) 很遠。

**術語對照**（給之後讀 paper 的人）：
- 「沒資料根據的處置」= **inadmissible / unsupported / OOD action**
- 「用平均值填補」= **mean imputation**（原論文 §4.3 的預設）
- 「離最佳多遠」= **distance-to-V***（我們的主 metric；V* = 精確最佳存活率）

**為什麼這值得做**：這其實就是整個 **offline RL** 領域的核心難題（OOD action），但在真實醫療資料上你無法精確驗證（只能用有雜訊的 OPE）。ICU-Sepsis 因為 dynamics 完全已知，**能算出精確 V***，所以是難得能「乾淨量測」這個問題的環境。

---

## 1.5 我們研究的價值（對外要怎麼說它有意義）

**一句話**：醫療 RL 幾乎都是 **offline**（只能從歷史病歷學、不能拿病人試），而 offline 最大的坑就是「**資料不支撐的動作**」。我們在一個**能看到標準答案**的醫療環境裡，把這個坑「**看得見、量得準、找到根因**」，並給出一套可參考的診斷 + 修法。

**為什麼這對別人有用（價值鏈，前 3 步是領域共識、第 4 步是我們的貢獻）**：
1. 醫療 RL = offline（公認）
2. offline 的核心難題 = OOD / unsupported action（公認）
3. 「有些治療很少被試」是醫療資料的本質（公認）
4. **pipeline 怎麼處理這些沒資料的動作，會默默改變學到的策略，而存活率看不出來**（← 我們乾淨示範、定位、給協議）
5. ⇒ 做 offline 醫療 RL 的人應該：把「unsupported action 的處理」當成有後果的設計選擇；量 support 診斷而非只看 outcome；用 behavior-level support-aware 學習。

**對外講價值的三個層次（看對象選用詞）**：
- **保守版（最安全）**：ICU-Sepsis 使用者別只報存活率，要報 inadmissible 處理方式 + distance-to-V*／unsupported rate。
- **可推版（我們的賣點）**：因為 offline 醫療 RL 先天有資料覆蓋不均，我們提供的「**失敗診斷 + 量測協議 + support-aware 處方**」是給推動 offline 醫療 RL 的人參考的**方法論警示與工具**。
- **🚫 不能講**：改善敗血症治療 / policy 更安全 / 可部署。

**⚠️ 一定要同時說的誠實話**：可遷移的是**現象 + 協議 + practice**，**不是具體數字**；我們是 tabular、benchmark-internal 的受控示範，沒有在真實 ICU 資料 / deep RL 上驗證。

**兩個讓它有份量的引用**：Gottesman 2019《Guidelines for RL in healthcare》（我們把其中一條警告做成可量測案例）；offline RL 的 BCQ/CQL/pessimism（大家知道 OOD 重要，但平常量不乾淨，我們給出 exact-eval 實例）。

---

## 2. 目前成果（數據 + 圖）

### 2.0 實驗地圖（先看這個再看下面）

每個實驗都掛在「三層主線」或「防守」上。先掌握這張圖，就知道每個實驗為什麼存在：

```
核心問題：ICU-Sepsis 預設 mean imputation 有沒有代價？學習者該怎麼辦？
│
├─[基礎] Baseline + exact V*
│        建立「尺」(Random/Expert/Optimal + 精確最佳解)，並揭露 survival rate 區間很窄
│                         │
│                         ▼
├─[Claim 1｜失敗] 預設下 vanilla 會出問題嗎？
│        └ P1 的 vanilla 端點：85% 選 unsupported、成績≈隨機，survival 看不出
│                         │
│                         ▼
├─[Claim 2｜根因] 問題出在「哪一步」？  ← 機制核心
│        └ T1 component ablation + Q-leakage：定位到 behavior 層(訓練時被選取/更新)
│                         │
│                         ▼
├─[Claim 3｜修法] 怎麼修？哪種修法好？
│        ├ P1 penalty→mask 光譜：penalty < CQL < hard mask（線上、已知模型）
│        ├ T2 offline 資料量 sweep：有限病歷下 naive 高估、pessimism/masking 才可靠
│        └ P2 expert projection：support-aware 的醫師引導（實用變體）
│                         │
│                         ▼
└─[防守層] 結論穩嗎？泛用嗎？
         ├ T3 robustness：跨 Q/SARSA/Dyna 成立；且是 mean 特有(terminate 下 vanilla 自己會避開)
         └ P0 dead-end：排除「其實有絕境狀態」的另類解釋（誠實負面結果）
```

**一句話記法**：Baseline=給尺；P1=證明有病+開藥單比較；T1=找病根（核心）；
T2=真實情境(有限資料)再驗藥效；P2=實用加強藥；T3/P0=確認不是巧合也不是別的原因。

> 圖檔在 `submission/figures/`，數字在對應的 `results/*/summary.json`。
> 每個實驗一句白話「它證明了什麼」。

| 實驗 | 它回答什麼 | 關鍵數字 | 圖檔 | 等級 |
|---|---|---|---|---|
| **Baseline** | 環境有沒有裝壞？ | Random 0.780 / Expert 0.782 / Optimal **0.875**（精確，吻合原論文）| —（Tbl 1）| 基礎 |
| **P1 penalty sweep** | 「輕罰→硬禁止」哪個好？ | vanilla dist 0.090、unsupported 85%；hard mask dist **0.069**、unsupported 0%；penalty 壓得到 0% 但 dist 卡 0.085 | `penalty_tradeoff.png` | **main** |
| **T1 component ablation** | 失敗的根因在哪一步？ | **behavior masking 必要且充分**（=full mask，0.069）；只擋 target/只擋部署都不夠；Q-leakage +0.46→−0.80 | `component_ablation.png` | **main** |
| **T2 offline 資料量** | 只有 N 筆病歷時呢？ | naive **高估 +0.21 且永遠卡 0.094**；pessimism 校準(~0)且進步到 0.069；masking unsupported 歸 0、到 0.065 | `offline_datasize.png` | **main** |
| **P2 expert prior** | 用醫師決策引導有用嗎？ | 醫師自己 16% 沒根據；raw 殘留 8% unsupported；**投影到有根據集合→0.5%**，value 不變、agreement 0.65 | `expert_prior_curve.png` | supplement |
| **T3 robustness** | 只是 Q-learning 的怪癖嗎？ | Q/SARSA/Dyna 都一樣；`terminate` 設定下 vanilla unsupported 85%→**~4%** | `robustness.png` | supplement |
| **P0 dead-end** | 有「怎麼治都會死」的絕境嗎？ | **沒有**（min V*=0.198）；誠實負面結果；但 mean 也藏了 inadmissible 較高的即刻死亡風險 | `deadend_structure.png` | supplement |

### 敘事補充（每個實驗在解決什麼問題）

> 表格給數字與術語；以下用平實敘事說明每個實驗「想知道什麼 → 怎麼測 → 發現什麼」。

**Baseline**
- 想知道：環境與評估流程有沒有裝對？
- 怎麼測：用已知 dynamics 精確算 Random / Expert(臨床) / Optimal 三個策略的 policy value。
- 發現：0.780 / 0.782 / 0.875，與原論文一致。同時注意到：任何策略的存活率都落在 0.78–0.875 的窄區間（action 對存活的敏感度本來就低），這也是為何後續要改用較敏感的 distance-to-V*。

**P1｜penalty sweep**
- 想知道：要讓 AI 不再依賴 unsupported action，從最溫和（給一點懲罰）到最強硬（直接禁止），哪種較划算？
- 怎麼測：在 vanilla 與 hard mask 之間插入一排 support penalty λ（0.01→1.0），以 exact distance-to-V* 與部署 unsupported rate 衡量。
- 發現：penalty 越大、部署 unsupported 越低（λ=1.0 可達 0），但 distance-to-V* 卡在約 0.085，始終追不上 hard mask 的 0.069；hard mask 在「低 unsupported」與「低 distance」兩個目標上同時最佳。→ 軟性懲罰不足以完全取代硬約束。

**T1｜component ablation**
- 想知道：masking 有效，但效果來自哪一個環節？一個動作會在三處被處理——探索時是否「選取」、計算 TD target 時是否「納入」、輸出最終 policy 時是否「採用」。
- 怎麼測：逐一只開啟其中一個環節的 masking、其餘關閉，比較各自能否達到完整 masking 的效果。
- 發現：只在「探索選取」環節 masking 就足以達到完整 masking 的結果；只 mask TD target 改善有限；只 mask 最終輸出雖能讓部署不再選到 unsupported action，但 Q-table 內部仍高估它們（Q-leakage 未改善）。→ 失敗根源在於 unsupported action 在訓練時被選取並更新。

**T2｜offline 資料量 sweep**
- 想知道：真實情況是「只有有限歷史病歷」，而非已知完整模型；資料量變化時這些修法表現如何？
- 怎麼測：用臨床(expert)行為從真模型抽 N 筆 transition 建 empirical MDP，比較 naive（對未見動作用 mean 補值）/ pessimistic（對少見動作加 count-based 懲罰）/ masked（只用 admissible），再用真 V* 精確評估。
- 發現：naive 會高估自身價值（overestimation +0.21），且資料再多、實際表現仍卡在約 0.094 不進步；pessimism 估計校準（約 0）且隨資料進步到 0.069；masking 將 unsupported 歸 0、達 0.065。→ 有限資料情境下 naive(mean) 不可靠，pessimism/masking 才會隨資料變好。

**P2｜expert prior**
- 想知道：用臨床醫師決策引導學習是否有幫助？直接照抄醫師夠不夠？
- 怎麼測：將探索改為從 expert policy 取樣（raw），以及把 expert 先投影到 admissible 集合再取樣（projected），與 vanilla 比較。
- 發現：expert 引導明顯加快學習；但醫師策略本身有約 16% 落在 unsupported action 上，raw 會繼承（殘留約 8% 部署 unsupported）；投影到有資料根據的集合後，部署 unsupported 降至 0.5%、value 不變、與醫師一致度升至 0.65。→「照抄醫師」不等於「有資料根據」，需再投影一次。

**T3｜robustness（也是我們對「另外兩種 strategy」的分析）**
- 想知道：這個失敗只是 Q-learning 的偶然，還是普遍現象？是否只與 mean 設定有關？
- 怎麼測：將 vanilla vs full mask 跑在 Q-learning / SARSA / Dyna-Q 三種演算法，以及 mean / terminate 兩種 strategy（exact 評估，terminate 另建精確 dynamics）。
- 發現：
  - (1) 三種演算法在 mean 下都出現高 unsupported 與較差 distance，masking 皆能修正 → 非單一演算法的怪癖。
  - (2) 換成 `terminate`（選到 unsupported 即進入死亡）後，vanilla 自己便學會避開（部署 unsupported 85%→約 4%）→ 證明失敗確實由 mean 造成。
  - (3) **但 `terminate` 不是免費的**：對 Q-learning/SARSA，vanilla 的 distance-to-V* 反而**更差**（0.107/0.108 vs mean 的 0.090），因為探索時的死亡截斷讓 model-free 更難學（Dyna-Q 靠 planning 才沒事）；而 **masking 不論哪種 strategy 都最好且穩定（~0.069）**。
- 註：第三種設定 `raise_exception` 是 debug 模式（選到即中斷、vanilla 無法訓練；只有搭配 masking 才能跑，但那等同 mask＋任何 strategy），**非學習策略，故不分析**。

**P0｜dead-end 分析**
- 想知道：環境中是否存在「無論怎麼治都註定死」的絕境狀態（dead-end）？此概念在臨床 RL 文獻受重視。
- 怎麼測：因 V*(s) 即該狀態的最大存活機率，可直接精確找出存活機率趨近 0 的狀態。
- 發現：沒有任何 dead-end（最差狀態仍有 0.198 存活率；427/713 狀態存活率 >0.9）。這是誠實的負面結果，原計畫的 dead-end 章節因此放棄；但分析順帶發現 mean 補值也把 unsupported action 較高的即刻死亡風險（0.032 vs 0.023）抹平，反而支持主線。

**三句話總結成果**：
1. **失敗存在且有代價**：vanilla 85% 用沒根據動作，成績卻只到隨機/醫師水準（survival rate 看不出）。
2. **根因被定位**：問題在「訓練時被選到、被更新」（behavior 層），不是 bootstrap 或部署層。
3. **修法成譜**：penalty < CQL pessimism < hard masking；離線資料情境下 naive 會高估、pessimism/masking 才可靠。

---

## 3. 我們對 paper 的想像

**Working title**：*When Mean Imputation Hides Unsupported Actions: Diagnosing and Repairing an OOD-Action Failure Mode in ICU-Sepsis*（詳 `core_docs/15_paper_story_spine.md`）

**三層 claim stack（故事主軸）**：
- **Claim 1 — Failure**：mean imputation 讓 vanilla 85% 用沒根據動作，成績≈隨機，survival rate 藏住。
- **Claim 2 — Mechanism**：component ablation 證明根因在 behavior 層（這段是「不是只有 masking」的關鍵）。
- **Claim 3 — Remedy spectrum**：penalty / CQL / masking 線上比較 + 離線資料量 sweep。

**我們有/沒有提出什麼（誠實邊界，對外別講錯）**
- ✅ 處方（agent 層）：不要跑 vanilla，要 **behavior-level support-aware learning**——masking 最佳，CQL pessimism 是最佳「軟解」。
- ✅ 建議（benchmark 使用者）：明確報告 inadmissible 處理方式 + distance-to-V*／unsupported rate，別只看 survival rate。
- ❌ 我們**沒有**發明新 RL 演算法，也沒提出新補值法取代 mean。masking 本身不新；新的是「**證明它必須在 behavior 層、且軟解都被它 dominate**」+ 用 exact V* 精確比較。
- 「不用 mean 怎麼辦」：環境內建替代是 `terminate`（agent 會自己避開但更難學）/ `raise_exception`（debug 模式）；但更根本的解法是**讓 agent support-aware**（masking），這樣 mean 不必改。
- ⚠️ 被問「你們的新方法是什麼」時，正確答覆是：「我們的處方是 behavior-level support-aware learning，並用 exact V* 證明它優於軟性替代」——**不要說「我們發明了某演算法」**。

**章節 outline**：骨架已在 `paper/main.tex`，Method/Experiments 已寫實，其餘標了 `\todo`。

| 章節 | 狀態 | 負責人 |
|---|---|---|
| Abstract | 已草擬 | ____ |
| 1. Introduction | `\todo` 待寫 prose（contributions 已列）| ____ |
| 2. Related Work | `\todo`，可直接搬 `core_docs/12` | ____ |
| 3. Background | 已寫實（含 mean-imputation 公式）| ____ |
| 4. Method | 已寫實 | ____ |
| 5. Experiments | 已寫實（表格+圖已填）| ____ |
| 6. Discussion | `\todo`（Q16/Q17/B.3 重點已列）| ____ |
| 7. Limitations | 已草擬 | ____ |
| 8. Conclusion | 已草擬 | ____ |

**時間線**：5/25 投稿 → 5/29 review → 6/1 rebuttal → 6/5 discussion → 6/8 decision → 6/15 oral/poster。

---

## 4. 潛在攻擊 vs 我們的防守（review 時組員也能幫忙回）

> 完整版在 `core_docs/reviewer_anticipated_questions.md`（Q1–Q17）。以下是最該記住的 7 個。

1. **「tabular RL，不是 deep RL，不夠格。」**
   → 這是 benchmark-level 分析，不是新演算法；ICU-Sepsis 本來就是 tabular benchmark（RLC 2024），tabular 才能算精確 V*、避開 OPE 雜訊。

2. **「不就是 action masking？novelty 在哪？」**
   → 我們不是發明 masking；貢獻是**診斷+定位+修法光譜**。component ablation 證明「到底哪一步在起作用」，這是 mechanism discovery，不是包一層 wrapper。

3. **【最重要】「原作者說 inadmissible 動作 = 隨機合法動作，所以無害，你們的 85% 是假議題。」(Q17)**
   → 「等於隨機合法動作」**正是代價**：隨機合法 < 最佳合法，所以 vanilla 成績≈隨機(0.785 vs 0.780)。而且這只在模擬器裡成立；真實部署時沒根據的動作不會剛好等於平均，所以這種 policy 才危險。

4. **「用已知 dynamics 算 exact V* 很稀有，是不是 toy 環境，optimize 它沒意義？」(Q16)**
   → exact V* 是 tabular RL 的教科書工具；它是我們的**量尺，不是賣點**。就像物理用無摩擦平面、生物用果蠅——簡化才能乾淨地隔離現象。OOD/overestimation 是 offline RL 公認的普遍問題，我們只是能精確量它。

5. **「只有 5 seeds，太少。」**
   → 主結論靠的是**大效應的 support 診斷**（unsupported 85%→0、leakage +0.46→−0.80），不是靠微小的存活率差異；小差異我們不宣稱顯著。

6. **「這是不是在做臨床建議？」**
   → 不是。全文 benchmark-internal / data-support，明確不碰臨床安全；inadmissible = 資料不足，不是醫學上錯。

7. **「masking 讓 unsafe rate 變 0 不是廢話嗎？」(Q5)**
   → 訓練時變 0 是 by design，我們不誇大；真正重點是 unmasked vanilla 在預設下高達 85%、且 distance-to-V* 與部署行為都受影響。

---

## 5. 現在還缺什麼 / 組員可認領的任務

- [ ] **寫 prose**：Introduction、Related Work（搬 `12`）、Discussion（把 Q16/Q17/B.3 寫進主文）。
- [ ] **Overview Figure 1**：照 `core_docs/15` §4 的 schematic 做一張圖。
- [ ] **per-seed scatter**：三張主圖補上每個 seed 的散點（防「5 seeds 太少」）。
- [ ] **Overleaf 上線**：放 `neurips_2026.sty`、把 `submission/figures/` 六張圖複製進去、開 line numbers 編譯。
- [ ] **匿名稽核**：投稿前確認 PDF 無姓名/學校/真實 GitHub。
- [ ] **內部 review 演練**：每人挑 §4 一個攻擊，練習 30 秒回答。

---

**一句話給組員**：故事是「benchmark 偷藏一個失敗 → 我們診斷、定位根因、比較修法，全程精確量測」。實驗與防守都到位了，現在缺的是把 paper 的文字補完 + 上 Overleaf。
