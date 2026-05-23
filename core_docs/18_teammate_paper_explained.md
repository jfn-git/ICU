# 18. 隊友 paper 白話解讀 — 「Admissibility-Aware RL Closes the Optimality Gap」

> 目的：用和 `16_team_briefing_claude.md` 一樣的白話風格，把**隊友那篇 paper 在說什麼**講清楚，讓你 5–10 分鐘就懂她的主張、方法、數據與強弱點。繁體中文，技術詞保留英文。
> 來源：**隊友的 PDF 草稿**（標題 *Admissibility-Aware Reinforcement Learning Closes the Optimality Gap on ICU-Sepsis*）。
> ⚠️ **重要前提**：經全 repo 搜尋，**她的程式碼、results、figures 都不在這個 repo 裡**（沒有 AA-MBRL/AA-PPO/SOFA/KL 的任何 code 或 JSON，也沒有 `e2_learning_curves.png`）。本檔所有數字都來自她 PDF 內文，**目前無法在我們 repo 重現**。詳見 §6、§7。

---

## 0. 30 秒總覽

她的論點一句話：**ICU-Sepsis 這個環境其實「附送」了 4 個 per-state 的提示（priors），但 5 個標準 RL 演算法在訓練時都把它們丟掉了；只要把這些提示放回訓練迴圈，距離最佳解的 gap 幾乎就補光了。**

她的收尾金句（PDF Conclusion）：

> 「The benchmark is hard for algorithms that ignore its structure, not for tabular RL.」
> （這個 benchmark 難，不是因為 tabular RL 弱，而是因為標準演算法忽略了它的結構。）

和你那篇的差別（一句話）：**你那篇是「診斷一個被藏起來的失敗 + 找根因」（批判/機制向）；她這篇是「把環境的結構放回去 → 把成績補到接近滿分」（建構/效能向）。** 兩篇用的是同一個環境、同一組 baseline 數字。

---

## 1. 她的核心論點（用具體情境理解）

**她觀察到的現象**：在 ICU-Sepsis 上，5 個標準演算法（Sarsa、Q-Learning、DQN、SAC、PPO）就算訓練到 5×10⁵（50 萬）episodes，成績仍離精確最佳解 0.88 有一段距離（optimality gap）。對一個只有 716 個 state 的小 tabular 環境來說，這「不太正常」——小環境照理應該學得到最佳。

**她的解釋**：這個 gap 是**結構性的（structural），不是演算法不夠強（algorithmic）**。原因是 ICU-Sepsis 每個 state 其實都帶了 4 個額外資訊，但標準 baseline 訓練時完全沒用：

> 想像病人狀況 `s`。環境其實「知道」：(1) 這個狀況下哪些處置有足夠資料（admissibility）、(2) 每個處置大概會把病人帶去哪（empirical transition model）、(3) 病人有多嚴重（SOFA 分數）、(4) 真實醫師在這個狀況通常怎麼做（clinician policy）。
>
> 標準 RL 把這些都當作不存在，只從 reward 慢慢試。她的主張是：**把這 4 個提示放回訓練，且完全不改網路結構、不改 hyperparameter，gap 就幾乎消失。**

**她的賣點（PDF 自述）**：因為「不改 representation、不改 hyperparameter」，所以**任何改善都能乾淨地歸因到「加了 prior」這件事**。

---

## 1.5 她研究的價值 — 對外要怎麼說它有意義

> 對齊 `16_team_briefing_claude.md` §1.5。注意：以下是**我幫她整理出「最站得住」的版本**；她 PDF 原稿偏向「我們補到 oracle / structure beats capacity」這種較高調、較易招打的講法，這份比原稿更保守、更可防守。

**一句話**：一個看起來「標準演算法都解不好」的 RL benchmark，其實不是演算法不夠強，而是**大家沒用環境本來就附的結構提示**；用回這些提示、完全不改模型，gap 幾乎消失。啟示是：**在帶 side-information 的環境上，先用好結構，往往比換更大的模型更划算。**

**為什麼這對別人有用（價值鏈，前 3 步是共識、第 4 步是她的貢獻）**
1. RL 研究常用 benchmark「跑一排演算法、比 final return / optimality gap」衡量進展（共識做法）
2. 看到 gap，直覺反應是「需要更強、更大容量的演算法」（常見假設）
3. 但很多環境（尤其從真實資料蒸餾來的）其實附帶 per-state side-information（事實）
4. **她的貢獻**：在 ICU-Sepsis 上乾淨證明——原 benchmark 留下的 gap，**大部分來自 baseline 沒用環境附的 4 個 prior，不是演算法弱**；放回訓練（不改 representation／hyperparameter）gap → 0.001
5. ⇒ 對做 benchmark RL 的人：遇到 gap 先問「是不是忽略了結構性 prior」，並把「有沒有用 prior」當成評估維度，而不是無腦加容量

**對外講價值的三個層次（看對象選用詞）**
- **保守版（最安全）**：在 ICU-Sepsis 上，光把被忽略的 admissibility prior 放回 baseline，就有穩定的 +0.026～+0.036 提升（配對檢定 p<0.001）；benchmark 報告應明說有沒有用 prior。
- **可推版（她的賣點）**：對「帶 per-state side-information 的 RL 環境」，先把結構放回訓練迴圈，常比換更大模型更划算——方法論建議。
- **🚫 不能講**：改善敗血症治療 / 臨床更安全 / 可部署。

**⚠️ 一定要同時說的誠實話**
- 真正可遷移的是「**結構優先於容量**」這個訊息，**不是**「AA-MBRL 是新方法」或「達到 SOTA」——在 716-state tabular MDP 上補到 oracle 本來就不難（她自己引的 UCRL/PSRL 就保證做得到）。論點若寫成「我們補到 0.874」會招打，寫成「**gap 主要來自忽略結構**」才站得住。
- 只限 ICU-Sepsis、tabular；deep/continuous 沒驗；5 seeds（vs benchmark 的 1000）；benchmark-internal，非臨床。

**兩個讓它有份量的引用**
- **Choudhary et al. 2024**（ICU-Sepsis 原 paper）：她的 gap 是相對它的 baseline，貢獻是「原 paper 留下的 gap 可被 prior 補上」。
- **Ng et al. 1999**（potential-based shaping）：給她 SOFA shaping 的理論正當性（不改最優策略）。
- （可選防守用）**Huang & Ontañón 2022 / UCRL / PSRL**：點明 masking 與 tabular model-based 都不是新技術 → 逼她把賣點放在「**診斷 gap 來源**」而非「方法新穎」。

### 關鍵差別：她的 §1.5 vs 你的 §1.5

| | 你的 §1.5 | 她的 §1.5 |
|---|---|---|
| 核心價值 | 把一個**被藏起來的 OOD 失敗**變得可量測 + 給診斷協議 | gap 是**結構性**的，**先用結構再加容量** |
| 語氣 | 警示 / 方法論 caution | 建構 / 方法論 lesson |
| claim 綁在哪 | 領域**已公認普遍**的現象（offline RL OOD）→ 借領域背書 | 這個 benchmark 的**特定 gap + 特定 prior** |
| 可遷移的是 | **機制洞見**（behavior 層、Q-leakage）| 一個關於單一環境的**分數事實** |
| 最強防守版 | 「offline 醫療 RL 該把 unsupported 處理當有後果的設計」 | 「遇到 gap 先查是否忽略 prior，而非加容量」 |
| 最大地雷 | 「masking 是常識」 | 「補到 oracle / structure beats capacity」（小 MDP 本來就可解）|

**為什麼她的賣點較弱（精準版）**：不是因為她「只跑一個環境」（你也只跑一個）；而是她的 novelty 與 generality 互相夾擊——**普遍成立的部分不新**（model-based 解小 MDP）、**算新的部分不普遍**（這 4 個 prior 綁死 ICU-Sepsis）。你那篇把 claim 掛在「offline RL 公認的 OOD 問題」上，等於借了整個領域的普遍性。**但她有你沒有的一種一般性：跨 Sarsa/Q/DQN/PPO（跨學習器，非跨環境）。** 兩個方向互補，正是 A-led 合併的理由。

---

## 2. 那 4 個 priors 是什麼（白話版）

她把環境附的 4 個 per-state 資訊命名為 P1–P4（PDF §2）：

| 代號 | 名稱 | 白話 | 技術細節 |
|---|---|---|---|
| **P1** | Admissibility map `A(s)` | 「這個狀況下，哪些處置有足夠病歷資料」 | 在該 state 被用過 ≥ τ=20 次的 action；平均每個 state 只有 **3.2 個** admissible（25 個裡） |
| **P2** | Empirical transition model `T̂` | 「每個處置大概會把病人帶去哪」 | AA-MBRL 邊互動邊用次數 `N(s,a,s')/N(s,a)` 線上估出來，reward 用 running mean |
| **P3** | SOFA severity `σ(s)` | 「病人有多嚴重」(器官衰竭指數 0–24) | 做成 reward shaping 的 potential `Φ(s) = −σ(s)/15` |
| **P4** | Clinician policy `π_expert` | 「真實醫師通常怎麼做」 | MIMIC-III 醫師的經驗動作分布，本身存活率 0.78；當成 KL 正則的 behavior prior |

> 注意：P1（admissibility）和 P4（clinician）你那篇也用到了（你做 masking、做 expert projection）；**P2（線上 model-based）和 P3（SOFA shaping）是她獨有、你沒做的**。

---

## 3. 她做了哪些方法（三組構造 C1/C2/C3）

她的方法就是「把 prior 一個一個加進不同演算法」，全部**不改 representation（one-hot tabular）、不改 hyperparameter（沿用原 paper Table 11）**（PDF §3, Table 1）：

### C1 — Admissibility-masked baselines（只加 P1）
對 4 個 baseline（Q-Learning、Sarsa、PPO、DQN），訓練時把可選 action 限制在 `A(s)`：
- Q-learning：bootstrap 的 `max` 只在 `A(s')` 上取，ε-greedy 也只在 `A(s)` 上選。
- PPO/DQN：把 inadmissible action 的 logits / Q 值在 softmax/argmax 前設成 −∞。
- 命名：AA-Q-Learning、AA-Sarsa、AA-PPO、AA-DQN。

### C2 — AA-MBRL（加 P1 + P2，這是她的招牌方法）
一個**線上 model-based** 方法：邊跑邊累積轉移次數、估出 empirical model，**每 K=1000 episodes 就在這個估出來的 model 上、只在 admissible action 集合內重新做一次 value iteration**（PDF Eq.2）。
- 技術細節：用 γ_vi=0.999 讓 VI 收斂（因為環境 γ=1 不收斂）；ε 從 0.5 線性降到 0.001。
- 三個變體（再加 P3/P4）：**AA-MBRL-Shaped**（+SOFA）、**AA-MBRL-KL**（fallback 改成從 expert 取樣）、**AA-MBRL-Full**（兩者都加）。

### C3 — 在 AA-PPO 上疊 P3/P4（reward shaping + KL）
- **AA-PPO-Shaped**：reward 改成 `r + γΦ(s') − Φ(s)`，`Φ=−σ/15`。她引 Ng et al. 1999 說 potential-based shaping **不會改變最優策略**（理論保證），回報時仍用原始 r。
- **AA-PPO-KL**：PPO loss 加一個會衰減的 KL 項，把策略往醫師 `π_expert` 拉，係數 β 從 0.10 降到 0。
- **AA-PPO-Full**：兩者同時。

---

## 4. 她的成果（數據 + 白話）

> 全部來自她 PDF 的 Table 2/3/4 與 Figure 1。預算是 **5×10⁵（50 萬）episodes、5 seeds**（比你的 5×10⁴ 多 10 倍）。

### 4.1 主結果（PDF Table 2，14 個方法 + 參考策略）

| 方法 | Final return | Gap to oracle | 白話 |
|---|---:|---:|---|
| Random / Expert / Optimal | 0.780 / 0.782 / **0.875** | 0.095 / 0.093 / 0 | 參考線（與你那篇完全一致）|
| Sarsa / Q / DQN / PPO（無 prior）| 0.789 / 0.785 / 0.787 / 0.833 | 0.086–0.042 | 標準 baseline，卡在 gap |
| **+P1 mask**：AA-Sarsa / AA-Q / AA-DQN / AA-PPO | 0.799 / 0.811 / 0.823 / **0.862** | 0.076→0.013 | 光加 mask 就明顯進步 |
| **AA-MBRL**（P1+P2）| **0.874 ± 0.003** | **0.001** | 她最好的訓練結果，幾乎貼到 oracle |
| AA-PPO-Shaped / -KL（+P3 或 P4）| 0.866 / 0.866 | 0.009 | 各再加一點點 |
| AA-PPO-Full（P3+P4）| 0.857 | 0.018 | 兩個一起加反而沒比較好 |
| AA-MBRL-Shaped / -KL / -Full | *in progress* | — | **PDF 自己標「還在跑」，沒有數字** |

### 4.2 三個她最強調的發現

1. **Mask 是最大的槓桿**（PDF Table 3，配對 t 檢定）：每個 baseline 加 mask 都變好，**效果隨 baseline 變強而變大**——Sarsa +0.010、Q +0.026、PPO +0.029、DQN +0.036（後三個 p<0.001）。
2. **加 model（P2）就補到 oracle**：AA-MBRL 0.874、gap 只剩 0.001。
3. **SOFA 和 KL 各加 +0.004，但「不疊加」**：兩個分開各到 0.866，合起來反而掉到 0.857。她的解釋是兩個 prior 資訊重疊（都來自同一份 MIMIC-III）。**副產品**：只要用 KL，seed 之間的 SE 縮小約 3 倍（變穩定）。

### 4.3 其他

- **Sample efficiency**（Figure 1，但**此圖檔不在 repo**）：AA-PPO 用約 105k episodes 就到 PPO 在 185k 才到的水準（約 1.8× 快）；AA-MBRL 收斂較慢（227k）但 plateau 更高。
- **無 mask 的 baseline 有 0.79–0.83 的訓練步在選 `A(s)` 以外的 action**，全被環境默默 remap 掉；加 mask 後這個比例 by construction = 0。（這點和你那篇的「85% unsupported」是同一個現象的不同講法。）

---

## 5. 她的 paper 故事線（一句話版）

> Medical RL 大多 offline → ICU-Sepsis 把它變成已知最佳解的 tabular benchmark → 但標準演算法留下一個不尋常的 optimality gap → 我們主張這 gap 是「沒用環境附的 4 個 prior」造成的結構性問題 → 把 prior（mask → model → SOFA/KL）放回訓練，gap 從 ~0.09 縮到 0.001 → 所以這個 benchmark 難在「忽略結構」，不是難在 tabular RL。

她明確聲明（PDF §1 末）：主張只限 ICU-Sepsis、且因為沒改任何設定，所有改善都可歸因到 prior。

---

## 6. 誠實的強弱點（幫你判斷，也關係到合併）

### 強項
- **組織清楚**：「環境附 4 個 prior、baseline 全丟掉」是很好懂的框架。
- **廣度好**：跨 Sarsa/Q/DQN/PPO 都驗，還有「效果隨 baseline 變強」這個漂亮的 pattern——這正好補你那篇「只有 Q-family、太窄」的弱點。
- **有建構性收尾**：AA-MBRL 補到 0.874，故事有「我們把它解決了」的爽感。
- **有 SOFA/KL 的組合分析**（2×2）+ 「KL 讓 variance 縮 3 倍」這個乾淨副產品，你那篇沒有。

### 要小心的弱點（重要）
1. **「補到 oracle」其實不令人意外**：在只有 716 個 state 的 tabular MDP 上，線上 model-based RL 本來就 trivially 解得掉——**她自己的 Related Work 就引了 UCRL（Auer 2008）和 PSRL（Osband 2013）並承認這點**。所以「AA-MBRL reaches 0.874」很可能被 reviewer 一句「小 tabular MDP 當然解得掉」消掉。
2. **只證明 mask 有效，沒解釋「為什麼」**：她沒有 component ablation（behavior/target/policy 拆解）、沒有 Q-value-leakage 診斷。**這正是你那篇的核心強項**——你的機制可以當她「mask 為何有效」的解釋。
3. **「structure beats capacity」太大話**：對這個規模的環境，這個宣稱招打。
4. **結果不完整**：3 個 AA-MBRL 變體 PDF 自標 *in progress*；SAC 在摘要列了卻沒做；DQN 是 tabular one-hot（不算真 deep）。
5. **全是 online，缺 offline 有限資料的分析**——而那是醫療 RL 最寫實的情境（你那篇有）。

### 一句話判斷
她的廣度與你的深度剛好互補；但她的 framing（closes the gap / structure beats capacity）overclaim 風險高。**這就是為什麼合併要以你的診斷/機制當主軸、把她的結果當證據而非戰績**（細節見 `core_docs/17_merged_paper_outline.md`）。

---

## 7. 你最該知道的三件事（實務）

1. **她的東西目前不在 repo**：沒有任何 AA-MBRL/AA-PPO/SOFA/KL 的 code、results、figure（連 `e2_learning_curves.png` 都沒有）。要合併進我們的 paper，這些數字**要嘛她交出可重現的 code/results，要嘛重跑**——這是 5/25 deadline 前的真實風險。
2. **數字其實對得上**：她的 Random/Expert/Optimal 和 vanilla Q（0.785）跟我們完全一致，代表是同一個環境、同一套 exact-V* 評估——**這是能合併的好兆頭**。唯一要對齊的是預算（她 500k vs 我們 50k）。
3. **她和你不是競爭，是兩半**：她答「跨演算法能不能普遍化、能不能補到 oracle」；你答「為什麼會發生、機制是什麼、有限資料下會怎樣」。拼起來是一篇更完整的 paper。

---

## 8. 名詞對照（讀她 paper 時用）

| 她的詞 | 意思 | 對應你那篇 |
|---|---|---|
| optimality gap | 距離精確最佳解 0.875 的差距 | = 你的 distance-to-V\* |
| admissibility mask / AA-* | 只在有資料根據的 action 裡學 | = 你的 hard masking |
| AA-MBRL | 線上估 model + 在 admissible 上做 VI | 你沒有（你有 offline 版的 empirical-MDP sweep）|
| SOFA shaping | 用病情嚴重度做 potential reward shaping | 你沒有 |
| KL-to-expert | 把策略往醫師拉的正則項 | ≈ 你的 expert prior（你用 projection，她用 KL）|
| four per-state priors (P1–P4) | 環境附的 4 個提示 | P1/P4 你也用；P2/P3 是她的 |
| structural not algorithmic | gap 是「沒用結構」造成，不是演算法弱 | 你的講法是「mean imputation 藏了 OOD failure」|

---

**一句話給你**：她的 paper 在說「ICU-Sepsis 附了 4 個提示、baseline 都沒用，放回去 gap 就補光（AA-MBRL 0.874）」。論點好懂、廣度夠，但缺機制、有 overclaim、且結果還不在 repo。它和你的診斷/機制剛好互補——這也是為什麼決定 A-led 合併。
