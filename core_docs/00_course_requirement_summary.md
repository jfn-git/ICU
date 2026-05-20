# 00. 課程 Final Project 要求整理

> 來源：`./Final-Project-Introduction .pdf`（NTU-DRL-MiniConf 2026，2026/05/11 公布）
> 本文件閱讀時間：5 分鐘。請所有組員在開始工作前先讀完。

---

## 0. TL;DR（最關鍵 5 件事）

1. **題目必須以 DRL / RL 為主**，且需有 **novel contribution**；禁止 existing work replication 與 survey paper。
2. **格式**：NeurIPS 2026 LaTeX template、英文、main content **4–8 頁**（references 與 appendix 不計頁數）、**雙盲匿名**、**保留 line number**、**禁止外部連結洩漏身份**。
3. **時程**：
   - 2026-05-25 23:59 提交（**從今天 2026-05-20 算起，剩 5 天**）
   - 2026-05-29 23:59 review 截止
   - 2026-06-01 23:59 rebuttal 截止
   - 2026-06-05 23:59 discussion 截止
   - 2026-06-08 23:59 decision notification
   - 2026-06-15 課堂上 Oral / Poster Session
4. **評分**：Author 25% + Reviewer 25% + Instructor 25% + Presentation 25%，再加 Oral bonus 10%、Best Paper 加分。
5. **必含章節**：Abstract / Introduction / Related Work / Methodology / Experiments / Conclusion / References；Member Workload 只在 camera-ready 時加上。

---

## 1. Final Project 的目的

slide 4–8 明確指出，這門課的 final project **不是純 implementation 練習**，而是讓學生熟悉「做 RL research 的完整流程」：

| 階段 | 學生要學會 |
|---|---|
| 找題目 | 找一個 **novel** 的 RL research topic（不是 existing work 重做） |
| 寫 paper | 寫一篇符合 conference 水準的論文 |
| 投稿 | 在 OpenReview 上送出匿名 paper |
| 同儕審查 | 每位學生都要 review 一篇論文，並參與 rebuttal / discussion |
| 出席會議 | 在 2026-06-15 進行 Oral / Poster |

**重點解讀**：
- 「RL research」是主軸 → 不能是 CV / NLP / 純應用，DRL 必須是 primary focus。
- 「novel contribution」門檻並非「打敗 SOTA」，但必須能說清楚：「我做了什麼前人沒做過或沒系統做過的事？」
- mini-conference 採 **double-blind review**，所以 paper 內容必須能說服「不認識作者」的 reviewer。

---

## 2. Submission Requirements

### 2.1 PDF 格式（slide 16）

| 項目 | 要求 |
|---|---|
| Template | **NeurIPS 2026 LaTeX template**（OverLeaf 上可直接 import） |
| 語言 | **英文** |
| 頁數 | **4–8 頁** main content；references 不計；appendix 不限頁數 |
| 匿名 | 必須移除作者姓名、機構；不可放會洩漏身份的外部連結（含 GitHub repo URL，除非用匿名 GitHub） |
| Line number | 必須開啟（為 reviewer 引用方便） |
| 工具建議 | OverLeaf（推薦）或 Word（要自己對格式） |

### 2.2 提交方式（slide 15）

- 每隊推一位代表在 OpenReview venue page 點 "Add submission"。
- Title / Authors（用 email 加入隊員）/ Keywords / TL;DR / Abstract / PDF / License = CC BY 4.0。
- 所有隊員必須先有 OpenReview 帳號（建議用 NTU email，否則最久兩週才能啟用）。

### 2.3 Source Code 要求（slide 5）

- 程式碼必須能 **reproduce 結果**。
- 跟著 `papers-with-code/releasing-research-code` 規範整理。
- 雖然這項要求被歸在「scope」說明，camera-ready 與 review 期間實質上會被檢視 reproducibility。

---

## 3. Paper 應該包含的內容（slide 17）

官方建議結構，**這就是我們最終 paper 的目錄**：

1. **Abstract**：高度濃縮，包含 motivation / problem / method / 主要結果。
2. **Introduction**
   - High-level 介紹整篇 paper（motivation, observation, contribution）
   - What problem do you address? Why is it interesting / important?
3. **Related Work**
   - 與我們工作相關的研究
   - 說明「相似」與「差異」
4. **Methodology**
   - 我們如何解決問題 / 如何進行研究
   - 遇到什麼 challenge，怎麼解決
5. **Experiments**
   - main experiments + ablation studies + discussion
   - 用來證明方法有效（或 claim 成立）
6. **Conclusion**
7. **Member Workload**（**只在 camera-ready** 加上，匿名投稿版本不要放）
8. **References**
9. **Appendices**（optional）

> **我們 paper 的必備內容（與 PDF 對齊）**：明確的 motivation、清楚的 novelty 宣告、可驗證的 main contribution、reasonable ablation、limitations 段落（雖然 slide 沒明列但 NeurIPS 慣例會放在 Discussion / Conclusion 之前）。

**Limitations 段落雖然官方沒列**，但 NeurIPS 2026 template 慣例與 reviewer 期待都需要 explicitly 提到 limitations；我們應主動寫，避免 reviewer 自己挖出更糟的批評。

---

## 4. Reviewer 怎麼看這個 Project（slide 19–21）

每篇 paper 會被 **3 位** 學生 reviewer 評分：

| 項目 | 內容 |
|---|---|
| Summary | 用自己的話摘要本論文 |
| Strengths / Weaknesses | 從 **quality / clarity / originality / significance** 四個面向評論 |
| Score | 1 (strong reject) – 6 (strong accept) |
| Confidence | 1 (educated guess) – 5 (absolute certain) |

撰寫 reviewer 評論時：
- 區分 **major / minor** issue
- 多個問題用 **numbered list**

### 4.1 我們 paper 必須對應四個 review 維度

| 維度 | 我們可以做什麼 |
|---|---|
| **Quality** | 實驗要 **multi-seed**（≥ 3 seeds 較安全）、metric 要清楚定義、claim 要有對應實驗、有 ablation。 |
| **Clarity** | 結構清楚、figure 有 caption、用語精確、避免 jargon 但 RL 術語要用對。 |
| **Originality** | 在 Related Work 明確指出「我們和 X / Y 的差異是 ___」。即使是 small delta，也要 explicit 說出來。 |
| **Significance** | 不需要 medical-level claim，但要說明「為什麼這個發現對 medical RL benchmark 使用者有意義」。 |

### 4.2 Reviewer 可能會挑的點（針對我們 ICU-Sepsis 題目）

事先記下來，避免被打臉：

- 「為什麼是 tabular MDP？這不像 deep RL final project」 → 我們要在 Introduction 明確說明「DRL 課程目的是 RL research 訓練，而 medical RL benchmark 的 algorithmic / safety analysis 本身就是 RL 主題」。並可在 paper 加 1 個 deep RL baseline（例如 DQN with action masking on tabular state representation）來防守。
- 「Novelty 在哪？只是 reproduce ICU-Sepsis 嗎？」 → 必須在 Introduction 段落直接列 contribution bullet list；ablation / multi-seed / 對 inadmissible_action_strategy 三種模式的系統比較，是 ICU-Sepsis paper 本身沒做的（原 paper 只報告 mean 模式的 baseline）。
- 「Medical claim 有無 overclaim？」 → 我們在 Abstract、Introduction、Limitations 都要明寫「this is not a clinical recommendation; results are about benchmark behavior under controlled RL settings」。
- 「實驗 robustness 不夠？」 → 至少 5 個 seed，error bar 或 95% CI；evaluation 用 50k episodes（與原 ICU-Sepsis 一致）。

---

## 5. 評分結構（slide 13）

| 項目 | 比例 | 我們怎麼準備 |
|---|---|---|
| Author Score | 25% | paper quality + rebuttal 品質。**rebuttal 期 06-01 ~ 06-05 不能掛**，組員要排班。 |
| Reviewer Score | 25% | 每位隊員都會被分配 review；review 寫得專業、有條理、major/minor 分開，TA 才會給高分。 |
| Instructor Score | 25% | 助教 / 老師對技術內容的評分。寫清楚 method、ablation、實驗設定。 |
| Presentation | 25% | 06-15 oral / poster。**要在 5 天內就先準備 slide / poster 雛型**，否則交完 paper 又要趕 slide。 |
| **Bonus** | | |
| Oral | +10% | 取 top N%（N 未公佈） |
| Best Paper | +N% | 一篇 |

> **重要**：Reviewer score 與 Author score 同等比重（各 25%）。**寫好 review 跟寫好 paper 一樣重要**——這常被忽略。

---

## 6. 對我們 ICU-Sepsis 題目的 implication

把上述要求對齊到我們現在這 5 天的決策：

1. **題目必須 RL-focused，不能是 medical claim 為主**
   → 把 paper 定位成 *benchmark / algorithmic analysis*，不是 clinical recommendation。
2. **要 novelty**
   → 不能只重做 ICU-Sepsis paper 的 baseline；至少要做原 paper 沒系統做過的 ablation（例如三種 `inadmissible_action_strategy` 的系統比較、不同 RL 演算法在 admissible action constraint 下的行為差異）。
3. **要英文 NeurIPS 4–8 頁**
   → 5 天內 paper 不可能很長；目標 **6 頁 main content** 比較合理（4 頁太薄、8 頁太累）。
4. **要 reproducible**
   → 從 Day 1 開始就用 config file + seed 管理實驗，最後打包成 reproducible repo（建議用匿名 GitHub repo 或 zip 附上）。
5. **要雙盲**
   → 不能在 paper 內寫 NTU、寫真實姓名、寫公開個人 GitHub。
6. **要先預期 reviewer 批評**
   → 第一份 plan 就把可能批評列出來，並在 paper 對應段落預先 defuse。

---

## 7. Checklist：提交前 24 小時要全部勾選

- [ ] NeurIPS 2026 template，line number 開啟
- [ ] **無作者名、無機構、無 NTU 字樣、無公開 GitHub 連結**（OK 用 anonymous.4open.science 之類匿名 repo）
- [ ] 4–8 頁 main content
- [ ] Abstract / Intro / Related Work / Method / Experiments / Conclusion 完整
- [ ] **Limitations 段落明確存在**
- [ ] 所有 figure / table 有 caption；至少 1 張 main result figure 在 page 1–2 出現
- [ ] 至少 1 個 ablation / 比較表
- [ ] Multi-seed 結果（≥ 3 seeds，建議 5）含 error bar
- [ ] 所有 reward / metric / setup 在 Method 或 Appendix 完整定義
- [ ] **無 medical / clinical claim**；Limitations 中明寫「not a clinical recommendation」
- [ ] Source code 整理成可一鍵 reproduce
- [ ] OpenReview submission form 填好 keywords / TL;DR / abstract
- [ ] 三位以上組員確認過最終 PDF
