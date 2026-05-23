# NeurIPS 投稿寫作規格（通用、可重用版）

> **這份文件是什麼**：一份「與任何特定題目無關」的 NeurIPS 風格論文寫作規格（writing spec）。
> 它把「課程的硬性規定」與「NeurIPS 強論文的敘事慣例」整理成可逐項執行、可逐項打勾的標準。
>
> **這份文件不是什麼**：它**不包含**我們專案的任何研究內容、結論、實驗或主張。
> 任何讀者（即使完全沒看過我們的專案）只要讀完這份 spec，就能知道「一篇合格的 NeurIPS 投稿長什麼樣」。
>
> **語言慣例**：說明用繁體中文；技術詞（technical terms）與範例句（example sentences）用英文，因為論文本體必須是英文。
>
> **來源標記**：第 1 節每一條規定都標「來源：PDF〈投影片標題〉p.N 第 X 點」，N 為該投影片右下角頁碼，方便回查課程 PDF（`Final-Project-Introduction .pdf`）。第 2–4 節為 NeurIPS 一般寫作慣例（非課程硬規定），標為「慣例」。

---

## 0. 使用方式（給 executor 的三步驟）

1. **動筆前**：先讀第 1 節（硬規定）+ 第 4 節 checklist，確認 template、頁數、匿名、章節骨架都對。
2. **寫每一節時**：對照第 3 節的「該節必須達成 / 常見失敗模式 / 好壞範例」逐節檢查。
3. **投稿前**：用第 4 節 checklist 從頭到尾打勾，全部 ✅ 才提交。

**優先順序**：硬規定（第 1 節）> 敘事慣例（第 2–3 節）。
任何衝突一律以「硬規定」為準；硬規定本身有衝突時，以**專門投影片**為準（見 §1.9）。

---

## 1. 硬性格式需求（從課程 PDF 抓，必須 100% 滿足）

> 違反任一條都可能直接扣分或被 desk-reject。這些不是建議，是門檻。

### 1.1 Template 與語言
- **必須使用 NeurIPS 2026 template，以 LaTeX 撰寫，全文英文。**
  - 來源：PDF〈Submission Requirements (Format of PDF)〉p.16 第 1.a 點；〈What do we want…（Submission format 縮圖）〉p.5。
- **必須一併繳交 LaTeX source files**（不是只交 PDF）。
  - 來源：PDF〈… Submission format 縮圖〉p.5：「using LaTeX (LaTeX source files should be submitted)」。
- 建議用 **Overleaf** 匯入官方 template（可一鍵切換匿名/非匿名）；用 Word 也可，但必須自行確保格式完全正確。
  - 來源：PDF〈Submission Requirements〉p.16 第 1.c 點。
- 實務提醒（慣例）：NeurIPS template 透過 `\usepackage{neurips_2026}` 載入。
  - **投稿（匿名）版**：**不要**加 `[final]` 選項 → 這會自動顯示 line numbers 並印出 "Anonymous Author(s)"。
  - `[final]` / `[preprint]` 等選項是 camera-ready 或 arXiv 才用，投稿階段不要用。

### 1.2 頁數上限
- **正文（main content）4～8 頁**。
  - 來源：PDF〈Submission Requirements〉p.16 第 1.b 點；〈… Submission format 縮圖〉p.5：「4~8 pages」。
- **References 不算入頁數；Appendix 不算入且頁數不限**（unlimited appendices）。
  - 來源：PDF〈Submission Requirements〉p.16 第 1.b 點：「4~8 pages for main content (excluding references and unlimited appendices)」。
- 注意：課程的 4–8 頁**覆蓋** NeurIPS 官方預設頁數（NeurIPS 主會通常為 9 頁）。以課程的 4–8 頁為準。
- 解讀：8 頁是**上限不是目標**；但低於 4 頁不符規定。內容應撐滿到「該講的都講清楚」，不要灌水也不要為了湊頁數塞冗言。

### 1.3 Double-blind 匿名（最容易被忽略而出包）
- **全文不得出現任何作者姓名 / 任何可辨識身分的資訊**（雙盲審查）。
  - 來源：PDF〈Submission Requirements〉p.16 第 2.a 點；〈Other than you get to visit…〉p.4（double-blind paper review process）。
- **不得包含任何會洩漏身分的外部連結（external links）**（例如個人 GitHub、個人網站、學號、機構帳號）。
  - 來源：PDF〈Submission Requirements〉p.16 第 2.c 點。
- 慣例補充（避免去匿名化）：
  - 引用自己過去的工作要用第三人稱（"Prior work [X] shows…"），不要寫 "our previous paper"。
  - 致謝（acknowledgements）、資助單位資訊在投稿版**移除**，camera-ready 再加。
  - 若要釋出程式碼，投稿階段用**匿名連結**（如 anonymous.4open.science）而非個人 repo。

### 1.4 Line numbers（行號）
- **行號必須可見（visible）。**
  - 來源：PDF〈Submission Requirements〉p.16 第 2.b 點。
- 慣例：NeurIPS template 在「非 final」模式下會自動加上行號（見 §1.1）；務必檢查最終 PDF 左側每行都有號碼。行號是 reviewer 引用位置用的，缺了會被扣印象分。

### 1.5 必備章節清單（建議骨架，順序如下）
課程提供的 reference 結構（"example paper structure for reference"）：
1. **Abstract**
2. **Introduction** — 高層次概覽（motivation、observation、contribution）；說明 what problem & why important。
3. **Related Work** — 討論相關研究，說明你與它們的 similarity / difference。
4. **Methodology** — 詳述你如何解題 / 進行研究；遇到的挑戰與如何解決。
5. **Experiments** — main experiments、ablation studies、討論，證明方法有效。
6. **Conclusion**
7. **Member Workload** — **僅 camera-ready 版需要**（投稿版不放）。
8. **References**
9. **Appendices** — optional，需要才放。
- 來源：PDF〈What do you need to contain in your paper?〉p.17 第 1–9 點。
- 注意：這是「reference 結構」，非逐字強制；但 **Abstract / Introduction / Related Work / Method / Experiments / Conclusion / References 視為實質必備**。Limitations 雖未在課程清單明列，屬 NeurIPS 強烈期待（見 §2.7、§3.7），建議務必加。

### 1.6 References / Appendix 規則
- **References**：不計入 4–8 頁正文頁數（§1.2）。慣例：用一致的 bib style，每筆要可被查證（作者、標題、會議/期刊、年份）。
- **Appendix**：不計頁數、頁數不限；放完整證明、超參數表、額外實驗、資料細節等。
  - 原則（慣例）：正文必須**自足（self-contained）**——reviewer 不讀 appendix 也能判斷主張成立；appendix 只承載「支持性、可選的」細節，不可把核心論證藏進 appendix。
  - 來源（頁數規則）：PDF〈Submission Requirements〉p.16 第 1.b 點。

### 1.7 Deadline 與審查流程（時間軸）
- **05/15**：分組註冊截止；每組 3～5 人；每位成員需註冊 OpenReview 帳號（用 NTU 機構信箱可自動啟用，非機構信箱可能要 2 週）。
- **05/25 23:59**：**論文投稿截止**（在 venue page 上傳）。
- **05/29 23:59**：Review 截止（每人需 review 並評分一篇；每篇收到 3 份 review）。
- **06/01 23:59**：Rebuttal 截止（作者回應 reviewer）。
- **06/05 23:59**：Discussion 截止（作者與 reviewer 討論；reviewer 可調分）。
- **06/08 23:59**：Decision notification（Area Chair/TA 裁決；假設全數錄取，僅 top N% 為 oral，其餘 poster）。
- **06/15**：in-class presentation（oral）+ poster session。
  - 來源：PDF〈Important Dates for Paper Submissions〉p.10；〈Important Dates for Double-Blind Peer Review〉p.11;〈Scoring〉p.13。
- 對寫作的意涵：投稿版**不要**放 Member Workload；要預留時間做 rebuttal，因此寫作時就應把「可被質疑的點」想清楚（見 §2.7、`reviewer_anticipated_questions` 類文件）。

### 1.8 其他課程硬規定（影響能不能過關）
- **Scope**：題目必須與 DRL（深度強化學習）相關，且 **DRL 必須是專案的主要焦點與貢獻**，不可以 CV / NLP / 其他領域為主。
  - 來源：PDF〈… Scope 縮圖〉p.5。
- **Novelty**：必須是有新貢獻的 RL 題目；**禁止**既有工作的複製（existing work replication）與 survey paper。
  - 來源：PDF〈Topic Limitation〉p.9 第 1–3 點。
- **明確陳述 motivation / novelty / main contributions**（這是評分與審查的核心）。
  - 來源：PDF〈… Submission format 縮圖〉p.5；〈What do you need…〉p.17。
- **Source code 必須可重現（reproducible）**，遵循 paperswithcode 的 "releasing-research-code" 規範。
  - 來源：PDF〈… Submission format 縮圖〉p.5。
- 評分結構（提醒寫作該討好誰）：Author 25% / Reviewer 25% / Instructor 25% / Presentation 25%；Oral 額外 +10% bonus；另有 Best Paper Award。
  - 來源：PDF〈Scoring〉p.13。

### 1.9 ⚠️ PDF 內部不一致之處（以專門投影片為準）
PDF 有兩處數字打架，executor 須知道並採用「專門投影片」版本：
- **評分權重**：〈Scoring〉專門投影片 p.13 寫 **25%/25%/25%/25%**；但 p.5 的「Lecture 1 縮圖」小字寫 Author 30% / Reviewer 10% / Instructor 30% / Presentation 30%。
  - **採用 p.13 的 25% 四等分**（專門投影片較新且為正式版）。
- 其餘日期、頁數、template 兩處一致，無爭議。
- 處理原則：本 spec 一律以「專門投影片」覆蓋「縮圖小字」。

---

## 2. NeurIPS 強論文的敘事慣例（慣例，非課程硬規定，但決定 accept/reject）

> reviewer 評的四個維度：**quality（紮實度）、clarity（清楚度）、originality（原創性）、significance（重要性）**。
> 來源：PDF〈What does a reviewer need to do?〉p.19。下列慣例都是為了在這四軸上拿分。

### 2.1 Abstract 結構公式（6 句骨架）
強 abstract 幾乎都能拆成這 6 個功能句（可合併，但功能不可缺）：
1. **Context / 領域背景**：這個問題屬於什麼、為何存在。
2. **Gap / problem**：現有方法缺什麼、哪裡失敗（"However, …"）。
3. **This paper / approach**：我們做了什麼（一句話的方法定位）。
4. **How / key idea**：核心機制或洞見是什麼（一句話）。
5. **Results / evidence**：量化結果（數字、相對改進、在什麼設定下）。
6. **Implication / takeaway**：所以這代表什麼、為什麼重要。
- 慣例：Abstract 不放引用、不放未定義縮寫、不賣關子；**結果要有數字**。
- 長度：約 150–250 字。

### 2.2 Introduction 的漏斗（funnel）與 contributions 寫法
**漏斗結構**（從寬到窄）：
1. 大背景 → 為何這領域/問題重要（broad，1 段）。
2. 收斂到具體 gap → 現有方法在「某個具體情境」失敗或不足（"Despite …, it remains unclear / fails when …"）。
3. 你的洞見/方法一句話總結（"In this paper, we …"）。
4. 你怎麼驗證（資料/環境/實驗一句話）。
5. **結果預告**（一句最強的量化結果）。
6. **明列 contributions**（bullet 條列）。
- **Contributions 寫法**：每點動詞開頭、可驗證、對應後文章節。
  - 慣例：3–4 點為佳；避免「我們做了實驗」這種空話，要寫「做了什麼、得到什麼可檢驗的結論」。
- 慣例：Introduction 結尾的 contribution list 是 reviewer 找「貢獻」最快的地方，務必對得上 abstract 與後文。

### 2.3 Related Work 的 positioning（定位，而非流水帳）
- **目的不是列舉，是定位**：說明每群相關工作與你的 **similarity / difference**，並指出它們的不足正是你補上的。
  - 來源（要點）：PDF〈What do you need…〉p.17 第 3 點。
- 慣例寫法：依「主題群（theme）」分段，不要一篇一段流水帳；每段結尾收束到「→ 因此本文不同於它們之處在於 …」。
- 禁忌：把 related work 寫成「中性摘要」卻不講差異 → reviewer 會質疑 originality。

### 2.4 Claim–Evidence 紀律（NeurIPS 的命脈）
- **每一個 claim 都要有對應 evidence**（實驗、理論、引用三選一），且 evidence 必須**支持得起 claim 的強度**。
- 慣例守則：
  - 不要 over-claim：寫 "improves" 就不要說 "solves"；普適性沒測過就不要說 "in general"。
  - 量詞要精確：用 "+3.1 points on X" 取代 "significantly better"（除非真的做了顯著性檢定）。
  - 因果要謹慎：相關不等於因果；沒做 ablation 就不要宣稱「是某設計帶來增益」。
- 這是 reviewer 抓 major flaw 最常見的點（PDF〈How to write clear review〉p.20 把「incorrect equation」「experiments not robust」列為 major flaws）。

### 2.5 Figure / Table 慣例
- **每張圖表都要能獨立看懂**：caption 要能脫離正文說明「在看什麼、軸是什麼、結論是什麼」。
- 慣例：
  - 圖在頂部（`[t]`）、字體不小於內文、軸標與單位齊全、線條/顏色色盲友善。
  - **報告變異性**：多次 run 要給 mean ± std 或 CI、標明 seeds 數；RL 尤其需要（高變異）。
  - 表的最佳值 **bold**，並在 caption 說明 bold 的判準。
  - 正文必須**引用並解讀**每張圖表（"Figure 2 shows that …"），不可只放圖不講。
  - 圖表編號、引用一致；不要有 "Figure ??"。

### 2.6 Reproducibility（課程硬規定 + NeurIPS 慣例的交集）
- 課程要求 source code 可重現（§1.8）。論文側的慣例配套：
  - 寫清楚 environment / dataset 版本、state-action 定義、reward、評估協定、train/val/test 切分。
  - 完整超參數、訓練細節、硬體、隨機種子放 Appendix。
  - 評估指標的定義與計算方式要無歧義（特別是自訂指標）。
- 慣例：附「Reproducibility Statement」或在 Appendix 開一節，指向（匿名）程式碼。

### 2.7 限制與誠實度（Limitations & honesty）
- NeurIPS 期待**主動寫 Limitations**：誠實列出方法/實驗的邊界與威脅效度（threats to validity）。
- 慣例：
  - 自己先講限制，比被 reviewer 抓到好；這會**提高**而非降低可信度。
  - 負面/未達預期的結果如實報告；不要藏。
  - 不要把核心論證藏進 appendix 規避檢查（見 §1.6）。
- 對應審查：誠實的 limitations 讓 rebuttal 階段更好守（你已預先承認的點，reviewer 較難當成致命傷）。

---

## 3. 逐章節規格（必須達成 / 常見失敗模式 / 好範例 vs 壞範例）

> 每節三件事：①這節**必須達成什麼**；②**常見失敗模式**；③一句 **good vs bad** 範例（英文）。範例皆為通用示意，與任何題目無關。

### 3.1 Abstract
- **必須達成**：用 §2.1 的 6 句骨架，讓讀者 30 秒內知道「問題、做法、結果、意義」，且結果有數字。
- **常見失敗模式**：
  - 只有背景與動機，沒有結果數字；
  - 出現未定義縮寫或引用；
  - 賣關子（"we propose a novel method"卻不說是什麼）。
- **範例**：
  - ✅ Good: *"We find that method X reduces error by 18% over the strongest baseline on benchmark Y, suggesting that Z is the key bottleneck."*
  - ❌ Bad: *"We propose a novel approach that achieves promising results on several tasks."*

### 3.2 Introduction
- **必須達成**：完成 §2.2 漏斗，結尾有可對照後文的 contributions bullet；讓 reviewer 清楚 "what problem & why important"（PDF p.17 第 2 點）。
- **常見失敗模式**：
  - 背景鋪太長、遲遲不講 gap；
  - contributions 寫成「做了哪些事」而非「得到哪些可檢驗結論」；
  - 預告的結果與 abstract / experiments 不一致。
- **範例**：
  - ✅ Good: *"Despite strong average returns, existing agents fail under distribution shift at deployment; we show why and propose a remedy that recovers 90% of the gap."*
  - ❌ Bad: *"Reinforcement learning is a popular and important field with many applications."*

### 3.3 Related Work
- **必須達成**：依主題分群、每群明確對比 similarity/difference，收束到「你補上的缺口」（§2.3、PDF p.17 第 3 點）。
- **常見失敗模式**：
  - 流水帳式「一篇一段、無對比」；
  - 不講差異，讀完不知你和它們差在哪 → 傷 originality；
  - 漏掉最直接的競品 baseline。
- **範例**：
  - ✅ Good: *"Unlike [12, 15] which assume full observability, our setting removes that assumption, which is precisely where their guarantees break."*
  - ❌ Bad: *"[12] proposed A. [15] proposed B. [20] proposed C."*

### 3.4 Methodology
- **必須達成**：詳述你怎麼解題，符號定義清楚、可重現；說明遇到的挑戰與如何解決（PDF p.17 第 4 點）。一個沒看過你專案的人能照著重建方法。
- **常見失敗模式**：
  - 符號未定義 / 前後不一致；
  - 只給直覺不給精確定義（或反之，只堆公式不給直覺）；
  - 把關鍵設計藏進 appendix，正文不自足（違反 §1.6）。
- **範例**：
  - ✅ Good: *"We define the admissible action set A(s) = {a : p(a|s) > τ}, and replace the policy's output by projecting onto A(s); τ is chosen by … (Appendix B)."*
  - ❌ Bad: *"We filter out bad actions using a threshold and then train as usual."*

### 3.5 Experiments
- **必須達成**：main experiments + ablation studies + 討論，逐一支持 contributions（PDF p.17 第 5 點）；報告變異性（§2.5）；每個 claim 有對應實驗（§2.4）。
- **常見失敗模式**：
  - 沒有 ablation → 無法歸因增益來源；
  - 單一 seed / 無誤差棒 → reviewer 視為 "not robust"（major flaw, PDF p.20）；
  - baseline 太弱或設定不公平；
  - 放了圖表卻不解讀。
- **範例**：
  - ✅ Good: *"Removing component C drops performance from 0.82 to 0.71 (5 seeds, ±0.02), isolating C as the source of the gain."*
  - ❌ Bad: *"Our method got the best score in the table."*

### 3.6 Conclusion
- **必須達成**：一段收束「我們發現了什麼、為何重要、可能的後續」；呼應 introduction 的承諾。
- **常見失敗模式**：
  - 只是 abstract 的複製貼上；
  - 突然冒出正文沒講過的新主張；
  - 灌入 limitations 卻沒在別處交代。
- **範例**：
  - ✅ Good: *"Our results indicate that X, not Y, governs deployment robustness, opening a path toward …"*
  - ❌ Bad: *"In conclusion, we did experiments and they worked well."*

### 3.7 Limitations（強烈建議獨立成節或併入 Conclusion 前）
- **必須達成**：誠實列出方法/實驗邊界與 threats to validity（§2.7）。
- **常見失敗模式**：完全不寫；或寫成行銷（"the only limitation is that it is too general"）。
- **範例**：
  - ✅ Good: *"Our evaluation is limited to a single simulator; transfer to real deployment is untested and may be affected by …"*
  - ❌ Bad: *"There are no significant limitations to our approach."*

### 3.8 References
- **必須達成**：每筆可查證、style 一致、被正文實際引用；不計頁數（§1.6）。
- **常見失敗模式**：bib 欄位殘缺（缺年份/會議）、arXiv 與正式版混亂、引用了正文沒提到的條目。
- **範例**：
  - ✅ Good: 完整 `author, title, venue, year`，正式版優先於 arXiv。
  - ❌ Bad: 只有標題與一個壞掉的連結。

### 3.9 Appendix（optional）
- **必須達成**：承載支持性細節（完整證明、超參數、額外實驗、資料細節），讓正文自足（§1.6）。
- **常見失敗模式**：把核心論證/關鍵結果藏進 appendix；appendix 與正文符號不一致。
- **範例**：
  - ✅ Good: *"Full hyperparameter grids and per-seed curves are in Appendix C."*
  - ❌ Bad: 把「方法是否有效」的唯一證據放在 appendix。

---

## 4. Executor 可逐項打勾的 Checklist

> 投稿前從頭走一遍，全部 ✅ 才提交。分三段：硬規定門檻 / 敘事品質 / 投稿前最後檢查。

### 4.1 硬規定門檻（缺一不可，對應第 1 節）
- [ ] 使用 **NeurIPS 2026 template**、**LaTeX**、**全文英文**（§1.1）
- [ ] 一併準備 **LaTeX source files** 供繳交（§1.1）
- [ ] 投稿版**未**使用 `[final]`，確認套件為匿名模式（§1.1）
- [ ] 正文 **4–8 頁**（不含 references / appendix）（§1.2）
- [ ] References **不計頁**、Appendix **不計頁且不限**（§1.2、§1.6）
- [ ] **全文無作者姓名 / 機構 / 任何可辨識身分資訊**（§1.3）
- [ ] **無任何會洩漏身分的外部連結**；自引用用第三人稱；致謝/資助已移除（§1.3）
- [ ] **行號（line numbers）在最終 PDF 可見**（§1.4）
- [ ] 章節骨架齊全：Abstract / Introduction / Related Work / Methodology / Experiments / Conclusion / References（§1.5）
- [ ] **投稿版未放 Member Workload**（camera-ready 才加）（§1.5）
- [ ] 題目 **以 DRL 為主要焦點與貢獻**，非 CV/NLP/其他（§1.8）
- [ ] **非既有工作複製、非 survey**，有明確 novelty（§1.8）
- [ ] 正文明確陳述 **motivation / novelty / main contributions**（§1.8）
- [ ] Source code **可重現**，遵循 paperswithcode releasing-research-code（§1.8）
- [ ] 趕得上 **05/25 23:59 投稿截止**；OpenReview 帳號全員就緒（§1.7）

### 4.2 敘事品質（對應第 2–3 節）
- [ ] Abstract 含 6 句功能（context→gap→approach→idea→results(含數字)→implication），無引用/未定義縮寫（§2.1、§3.1）
- [ ] Introduction 成漏斗、有結果預告、結尾 contributions bullet 且對得上 abstract 與後文（§2.2、§3.2）
- [ ] Related Work 按主題分群、明講 similarity/difference、收束到你補的缺口（§2.3、§3.3）
- [ ] Methodology 符號定義完整一致、可重現、正文自足（§3.4、§1.6）
- [ ] **每個 claim 都有對應 evidence**，無 over-claim、量詞精確、因果謹慎（§2.4）
- [ ] Experiments 含 **ablation**、報告 **mean±std / 多 seeds**、baseline 公平、每圖表都被解讀（§2.5、§3.5）
- [ ] 有 **Limitations** 且誠實（§2.7、§3.7）
- [ ] Conclusion 呼應 introduction、無新主張（§3.6）

### 4.3 投稿前最後檢查（格式與一致性）
- [ ] 無 `Figure ??` / `Table ??` / 壞掉的 `\ref` `\cite`
- [ ] 所有圖表都有 caption 且能獨立看懂；最佳值 bold 並說明判準（§2.5）
- [ ] 數字一致：abstract、intro 預告、experiments 表格三處數字相符
- [ ] References 每筆欄位完整、style 一致、皆被正文引用（§3.8）
- [ ] 重新編譯 PDF：頁數合規、行號可見、無匿名外洩、字體與邊界未被竄改
- [ ] 預想 reviewer 會問的 major/minor 問題並已在文中預先回應（為 rebuttal 鋪路，§1.7、§2.7）

---

### 附：本 spec 來源對照表（PDF）
| 規定 | 來源（PDF 投影片 / 頁碼） |
|---|---|
| Template / LaTeX / 英文 / 交 source | 〈Submission Requirements〉p.16 第1點；〈Submission format 縮圖〉p.5 |
| 4–8 頁、refs/appendix 規則 | 〈Submission Requirements〉p.16 第1.b 點 |
| 雙盲匿名 / 無洩漏連結 / 行號 | 〈Submission Requirements〉p.16 第2.a–c 點 |
| 必備章節 / Member Workload 時機 | 〈What do you need to contain…〉p.17 第1–9點 |
| 時間軸 / deadline | 〈Important Dates…〉p.10、p.11；〈Scoring〉p.13 |
| Scope（DRL 為主）/ Novelty | 〈Scope 縮圖〉p.5；〈Topic Limitation〉p.9 |
| Reproducibility | 〈Submission format 縮圖〉p.5 |
| 評分權重（25%×4，採專門投影片） | 〈Scoring〉p.13（注意 §1.9 不一致說明） |
| Reviewer 四評分軸（quality/clarity/originality/significance） | 〈What does a reviewer need to do?〉p.19 |
| Major/Minor 區分（影響寫作防守） | 〈How to write clear review〉p.20 |
