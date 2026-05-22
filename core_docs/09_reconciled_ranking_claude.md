# 09. Reconciled Implementation Ranking (Claude, after reading Codex's 07 + 08)

> **作者**：Claude
> **日期**：2026-05-22
> **我讀過的輸入**：
> - Claude 探索：[`07_rl_active_directions_claude.md`](07_rl_active_directions_claude.md)
> - Codex 探索：[`07_rl_method_exploration_options.md`](07_rl_method_exploration_options.md)
> - Codex 合併排名（已含對 Claude 的反駁）：[`08_merged_implementation_ranking.md`](08_merged_implementation_ranking.md)
>
> 本文件是「互相讀完對方文件」後，Claude 這邊的最終實作順序排名。與 codex 的 08 並列，供使用者拍板。

---

## 1. 強共識（兩個 AI 獨立一致，可直接定案）

1. **#1 主線 = OOD-action / conservative Q-learning 光譜**（penalty → CQL-style pessimism → count-based pessimistic VI → BCQ-style behavior constraint → hard mask），用 exact distance-to-V* 評估。兩邊都給最高分。
2. **保留** mean-imputation hidden-failure-mode 當 **motivation**，不丟棄既有 mask 結果（它變成光譜上一點）。
3. **底層共識**：AA-Dyna / model-based 與 risk-sensitive / death-avoidant 都是 appendix / robustness 等級。
4. **probe 哲學**：fastest-signal-first，先跑最快能出圖的。

→ 這四點不需再爭論，直接採用。

---

## 2. 唯一實質分歧：Tier-2 補充章節的優先序

我和 codex 對 #1 完全同意。**真正的差異只在「主線之外，先補哪個」**：

| | Codex 08 的傾向 | Claude（本文件）的傾向 |
|---|---|---|
| 第二優先 | **Factored action space**（rank 2）| **Exact dead-end analysis** |
| 第三優先 | **SOFA PBRS**（rank 3）| **Expert-guided + admissible projection** |
| 對 Factored | 排很前、當第一個 probe | 同意「probe 快」，但**反對當 paper 主補充** |
| 對 Dead-end | rank 5、「可能變成另一篇 paper」| rank 高、**最便宜的 probe（零訓練）且 novelty 最高** |

### 2.1 我為何把 Factored 降級（相對 codex）

- **最正交**：factored 引入「action 結構 / sample efficiency」這條**和 admissibility 主軸無關的新軸**，在 4–8 頁裡和主線搶版面。codex 自己在 08 §6 與 Case B 也承認它「may become a separate story」。
- **方法風險真實**：ICU-Sepsis 的 fluid×vaso **交互作用可能很重要**，simple additive `Q≈Q_f+Q_v` 可能表現差或結果雜（codex 08 也列了這個風險）。當 probe 可，當主補充不穩。
- 我原 07 把 factored 放「probe 順序第一」**只因為快**，richness 排序我寫的是 A>B>C。codex 似乎把「probe 第一」誤讀成「重要性高」而抬高它。這裡澄清：**factored = 快但不重要的 probe**。

### 2.2 我為何把 Dead-end 升級（相對 codex）

- **最便宜的 probe**：dead-end 分析**完全不需訓練**，純用既有 V*（= 最大存活機率）算 state 死局度、per-action P(death)、policy 落在死局動作的 mass。~30 分鐘即可有訊號。
- **novelty 最高**：Fatemi 在真資料只能「估」dead-ends，我們能算 **exact**。
- codex 擔心「變成另一篇 paper」——但它**不需要成為完整 method**，可當一段緊湊 analysis：「benchmark 也藏了死局結構；admissibility-aware policy 較少踏入死局」，與 OOD 主線同源（都是「mean-imputation/benchmark 藏起來的東西」）。

### 2.3 我為何把 Expert-prior 升級（相對 codex）

- **fit 最好**：直接接既有發現「expert ~16% mass 落在 inadmissible」。「把 expert 投影到 admissible set」是 admissibility 主題的自然延伸，比 SOFA 更貼主線。
- 成本低（env 內建 expert_policy）。

### 2.4 我為何把 SOFA PBRS 降級（相對 codex）

- **最正交 + medical-claim 風險**（`CURRENT_STATUS` 已列「可砍」）。codex 用 potential-based（policy-invariant）防守合理，但**本環境 episode 僅 ~9–11 steps，shaping 的 sample-efficiency 上限有限**。當 probe 可，當主補充弱。

---

## 3. Claude 的最終實作順序排名

| Rank | 方向 | Tier | 來源 | 與 codex 08 差異 |
|---:|---|---|---|---|
| 1 | OOD-action / conservative Q-learning 光譜 | 主線 | Claude A + Codex A | 一致 |
| 2 | Exact dead-end analysis（零訓練、最高 novelty）| 補充 | Claude B | **我升、codex 降（其 rank 5）** |
| 3 | Expert-guided + admissible projection | 補充 | Codex C | **我升、codex 列 rank 4** |
| 4 | Factored action space | 視時間 | Claude C | **我降、codex 列 rank 2** |
| 5 | SOFA PBRS | 視時間 | Codex B | **我降、codex 列 rank 3** |
| 6 | AA-Dyna / model-based | appendix | Codex E | 一致 |
| 7 | Risk-sensitive / death-avoidant | appendix | Codex D | 一致 |

---

## 4. 合併後的下午 Probe 計畫（Claude 版）

| 順序 | Probe | 需訓練？ | 估時 | 為何這個位置 |
|---:|---|---|---:|---|
| P0 | Exact dead-end map（V* 已有，算死局度 / per-action P(death) / policy mass）| ❌ | ~30 min | **最便宜 + 最高 novelty**，先探一手 |
| P1 | Penalty / conservative λ sweep → trade-off 曲線（unsupported rate vs distance-to-V*）| ✅ 1–3 seeds | 1–2 hr | 兩 AI 共識主線骨幹，必跑 |
| P2 | Expert prior：raw vs 投影到 admissible | ✅ 1–3 seeds | ~1 hr | 便宜、fit 最好的補充 |

> 與 codex probe 順序的差異：codex 把 **factored** 當第一個 probe；我把**零訓練的 dead-end 分析**放第一（更快、更獨特），factored 留到「想要 method-y 第二軸」時再做。P1（λ sweep）兩邊都同意必跑。

**晚上**：哪個 probe 出最乾淨的圖就擴 5 seeds；conservative 家族（P1）無論如何留為骨幹。

---

## 5. 給使用者的拍板選項

主線（#1）與大策略**兩 AI 已一致**，可直接定。需要你決定的只有「補充章節走哪一邊」：

- **選項甲（Claude 傾向）**：補充先做 **dead-end + expert-prior**（貼主線、便宜、dead-end 最獨特）。
- **選項乙（Codex 傾向）**：補充先做 **factored + SOFA PBRS**（更 method-y、更多 RL 技巧展示，但較正交、風險較高）。
- **選項丙（折衷）**：probe 階段三個都各跑 1–3 seeds（dead-end 零成本 + λ sweep + 一個 method-y 的），晚上看哪個圖最漂亮再擴。

我的建議：**選項丙的 probe，但晚上擴充偏選項甲**——理由是 deadline 只剩 ~3 天，dead-end（零訓練）+ expert（接既有發現）風險最低、最快變成 paper 內容。
