# 02. Related Work Notes — ICU-Sepsis 與 Sepsis RL 文獻調查

> 範圍：ICU-Sepsis 原始 paper、Komorowski AI Clinician 系列、offline / safe RL for sepsis、OPE in medical RL、action masking 與 reward shaping 通用文獻、benchmark reproducibility 討論。
>
> **重要原則**：本文件區分三種來源層級：
> - **[Peer-reviewed]** Nature Medicine、RLC、PLOS One、npj Digital Medicine 等正式期刊/會議。
> - **[Preprint]** arXiv preprint，未必經過審查。
> - **[Other]** GitHub、blog post、未公開 venue 的 preprint。
>
> 沒有確定來源的工作會明確標示「未驗證」，不會憑空編造引用。

---

## A. ICU-Sepsis 原始環境

### A.1 原始 paper

| 項目 | 內容 |
|---|---|
| Title | ICU-Sepsis: A Benchmark MDP Built from Real Medical Data |
| Authors | Kartik Choudhary, Dhawal Gupta, Philip S. Thomas |
| Affiliation | UMass Amherst |
| Year / Venue | 2024 / Reinforcement Learning Conference (RLC) 2024，published in Reinforcement Learning Journal Vol. 4, pp. 1546–1566 |
| arXiv | [2406.05646](https://arxiv.org/abs/2406.05646)（v1: 2024-06-09, v2: 2024-10-14） |
| Status | **Peer-reviewed (RLC 2024)** |

**BibTeX**（取自 README）：
```bibtex
@inproceedings{choudhary2024icusepsis,
  title={{ICU-Sepsis}: A Benchmark {MDP} Built from Real Medical Data},
  author={Kartik Choudhary and Dhawal Gupta and Philip S. Thomas},
  booktitle={Reinforcement Learning Conference},
  year={2024},
  url={https://arxiv.org/abs/2406.05646}
}
```

### A.2 主要目的與 contribution

從 paper html（[arxiv html v1](https://arxiv.org/html/2406.05646v1)）抓到的重點：

1. **目的**：提供 lightweight, easy-to-setup, MIMIC-III credential 不必要 的 medical RL benchmark。
2. **基於** MIMIC-III 與 Komorowski 等 (2018) 的 sepsis cohort 處理流程。
3. **被設計成 benchmark 而非 clinical tool**：作者明寫 *"it should not be used to draw conclusions that guide medical practice"*。

### A.3 Paper 中報告的 baseline 數字

| Policy | Avg. Return（= survival rate） | Avg. Episode Length |
|---|---|---|
| Random | 0.78 | 9.45 |
| Expert | 0.78 | 9.22 |
| Optimal (VI) | 0.88 | 10.99 |
| Dataset reference | 0.77 | 13.27 |

### A.4 Paper 中已經跑過的 RL 演算法

paper html 顯示，作者在 benchmark 上跑了 **5 個** tabular-or-deep RL 演算法：

- **Sarsa** → 收斂在 0.79
- **Q-Learning** → 接近 0.79
- **DQN** → ≈ 0.86
- **SAC** → ≈ 0.86
- **PPO** → ≈ 0.86

> **重要**：「在 ICU-Sepsis 上跑 Q-learning / SARSA / DQN」這件事 **已經被原 paper 做過了**。如果我們只是「跑 Q-learning 看 learning curve」**沒有 novelty**。我們的 novelty 必須在 **inadmissible action 處理、action masking、ablation、metric 分析**等原 paper *沒做的維度*。

### A.5 Paper 中對 admissible / inadmissible action 的處理

- 定義：admissible = 在該 state 出現 ≥ τ = 20 次的 action。
- inadmissible action 的 transition 設成「隨機選一個 admissible action 並轉移」。
- **paper 只 evaluate 在 `'mean'` strategy 下**。`'terminate'` 與 `'raise_exception'` 是 v2 才加進來的選項，**沒有在 paper 中做 ablation**。

### A.6 Paper 的 limitations / future work

- 不可作為 clinical guidance。
- 沒有處理 gradual medication adjustment（臨床上 vasopressor 不應該突然大幅變動）。
- generalizability across patient sub-cohorts 未測試。
- Future work：continuous-state 版本、加上 clinical constraint 的版本。

### A.7 對我們的啟示

- **原 paper 已經幫我們做了「baseline reproduction」這一段**，我們可以直接 cite paper 數字並重現一遍，但不能宣稱是貢獻。
- **inadmissible_action_strategy 的系統比較**是原 paper 明確未做的事，是合法的 novelty。
- **action masking** 在原 paper 也沒做（它依賴 mean strategy 把 inadmissible 隱性吸收），是合法的 novelty。
- 「continuous-state / safer variant」是原 paper future work，但 5 天內不可能做到。
- 我們在 paper 中可以借原 paper 的「不可用於 clinical guidance」這句話，鞏固我們的 medical-claim 防守。

---

## B. 是否已有後續 paper 使用 ICU-Sepsis？

### B.1 搜尋結果摘要

**結論**：截至 2026-05-20 為止，**公開可追蹤、使用 `icu-sepsis` benchmark 為主要 evaluation 環境的 follow-up 工作數量仍有限**（少於 5 筆能明確驗證），且其中多半為 preprint 或近期論文。下方列出已找到的工作，剩餘可能存在的 follow-up 我們會在 paper 寫作前 24 小時再做一次 Google Scholar / arXiv listing 的 final pass，避免漏 cite。

#### 已找到的潛在 follow-up

1. **「Safe Offline Reinforcement Learning for Sepsis Treatment」**（CPQ-IQL framework）
   - 來源：sciltp PDF [media.sciltp.com/articles/2602003157/2602003157.pdf](https://media.sciltp.com/articles/2602003157/2602003157.pdf)
   - 在 search snippet 中明確提到 *"evaluated on the ICU-Sepsis benchmark"* 並使用 Surviving Sepsis Campaign 2021 guidelines 推出 clinical constraints。
   - Status：**未確認 venue**（網域 sciltp.com 看似 preprint / 小期刊；需要 Day 1 再 verify 是否 peer-reviewed）。
   - **與我們的關係**：他們做 "safety-filtered offline RL"，比我們野心大很多；但他們把 ICU-Sepsis 當 evaluation env，沒有系統做 admissible-action-handling 的 ablation。**我們可以 cite 並指出 differentiator: they propose a method, we systematically characterize the env's safety knobs.**

2. **「MIMIC-Sepsis: A Curated Benchmark for Modeling and Learning from Sepsis Trajectories in the ICU」**
   - arXiv: [2510.24500](https://arxiv.org/pdf/2510.24500)
   - 提出新的 sepsis benchmark（MIMIC-IV 上）並以 ICU-Sepsis 為比較對象。
   - **與我們的關係**：他們是 dataset/benchmark paper，定位與我們完全不同；可在 Related Work 中作為 "benchmark landscape" 的 cite，並用來證明「sepsis RL benchmark 標準化是 active research topic」。

> **誠實揭露**：除上述兩篇外，我們沒有在 web search 中找到其他明確以 ICU-Sepsis（Choudhary 2024）為主 evaluation env 的工作。**目前可找到的後續使用案例有限**，這對我們是好消息：題目空間還沒擁擠。但同時要注意：因為使用案例少，**reviewer 可能會挑戰我們「為什麼要用這個 benchmark 而不是 Komorowski 原版」**，需要在 Introduction 預先回答（→ 因為 ICU-Sepsis 不需要 MIMIC-III credential、可重現、tabular oracle V* 可得）。

---

## C. Broader Sepsis RL Literature

### C.1 Komorowski AI Clinician（祖宗 paper）

| 項目 | 內容 |
|---|---|
| Title | The Artificial Intelligence Clinician learns optimal treatment strategies for sepsis in intensive care |
| Authors | Komorowski M, Celi LA, Badawi O, Gordon AC, Faisal AA |
| Venue | **Nature Medicine** vol. 24, pp. 1716–1720 (2018) |
| Status | **Peer-reviewed** |
| URL | [nature.com/articles/s41591-018-0213-5](https://www.nature.com/articles/s41591-018-0213-5) |

**主要貢獻**：
- 提出 AI Clinician，第一個用 MIMIC-III + eICU 數據以 model-based RL（policy iteration on clustered state space）找 sepsis fluid + vasopressor 最佳策略。
- claim：在 validation cohort 中，clinician dose ≈ AI dose 的 patient 死亡率最低。
- **ICU-Sepsis benchmark 本身就是建立在 Komorowski 的 cohort 處理 pipeline 上**，所以引用是必須的。

### C.2 Raghu et al. — Continuous State-Space DDQN

| 項目 | 內容 |
|---|---|
| Title | Continuous State-Space Models for Optimal Sepsis Treatment: A Deep Reinforcement Learning Approach |
| Authors | A. Raghu, M. Komorowski, L. A. Celi, P. Szolovits, M. Ghassemi |
| Venue | **MLHC 2017** (Proceedings of the 2nd Machine Learning for Healthcare Conference, PMLR v68) |
| Status | **Peer-reviewed** |
| URL | [proceedings.mlr.press/v68/raghu17a.html](https://proceedings.mlr.press/v68/raghu17a.html) |

**重點**：把 Komorowski 的 discrete state 升級成 autoencoder + Dueling DDQN。對我們的意義：證明「continuous + deep RL」是 sepsis RL 的主流方向，而我們在 tabular ICU-Sepsis 上做 algorithmic analysis 是補互補空間（不是 compete）。

### C.3 Gottesman et al. — RL in Healthcare Guidelines

| 項目 | 內容 |
|---|---|
| Title | Guidelines for reinforcement learning in healthcare |
| Authors | Gottesman O, Johansson F, Komorowski M, Faisal A, Sontag D, Doshi-Velez F, Celi LA |
| Venue | **Nature Medicine** 25, 16–18 (2019) |
| Status | **Peer-reviewed** |
| URL | [nature.com/articles/s41591-018-0310-5](https://www.nature.com/articles/s41591-018-0310-5) |

**重點**：醫療 RL 從 cohort 到部署的指引；強調 OPE bias、distribution shift、reward 設計的限制。**對我們 Related Work 與 Limitations 段都是必引**——可以用來 defend「我們不做 clinical claim、只做 algorithmic analysis」。

### C.4 Safe RL / Constrained RL for Sepsis

| 項目 | 內容 |
|---|---|
| Title | Safe Reinforcement Learning for Sepsis Treatment |
| Authors | Jia et al.（具體 author list 待 Day 1 verify） |
| Venue / Year | 出現在搜尋結果中（[ACM DL 5555/AAI29281130](https://dl.acm.org/doi/10.5555/AAI29281130)），疑似 thesis / workshop |
| Status | **Unverified — 需在 Day 1 查清** |

| 項目 | 內容 |
|---|---|
| Title | Offline Safe Reinforcement Learning for Sepsis Treatment: Tackling Variable-Length Episodes with Sparse Rewards |
| Venue | Human-Centric Intelligent Systems, [Springer, 2025](https://link.springer.com/article/10.1007/s44230-025-00093-7) |
| Status | **Peer-reviewed** (Springer journal) |

**對我們的意義**：safe RL for sepsis 是 active topic；我們的 inadmissible action handling ablation 可以放在 "lightweight safety proxy" 的脈絡下 motivate，不需要打到 full constrained MDP 也能講出意義。

### C.5 Off-policy Evaluation in Medical RL

- **Towards more efficient and robust evaluation of sepsis treatment with deep RL**（[PMC9979564](https://pmc.ncbi.nlm.nih.gov/articles/PMC9979564/)）：強調 OPE 在 sepsis treatment 中的 reliability 問題。
- Weighted Importance Sampling / Effective Sample Size 在 MIMIC-III sepsis 中是常用 evaluation method。
- **對我們的意義**：在 ICU-Sepsis 中 OPE 不是問題（環境完全 model-known，可以直接做 ground-truth evaluation）。我們可以在 Discussion 段指出：*"this is one advantage of using a tabular benchmark over MIMIC-III-based offline studies — we can compute exact policy value, not just an OPE estimate."*

### C.6 Benchmark Reproducibility 問題

- **「Superhuman performance on sepsis MIMIC-III data by distributional RL」**（PLOS One 2022, [journals.plos.org/plosone/article?id=10.1371/journal.pone.0275358](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0275358)）— 此 claim 在 peer review 中被質疑「superhuman」字眼不適當。**這正是 ICU-Sepsis 想避免的問題**：標準化、可重現、不允許 OPE-based overclaim。
- **MIMIC-Sepsis (arXiv 2510.24500, 2025)**：批評過往工作 reliance on outdated datasets、ad-hoc curation。

對我們的意義：可以在 Introduction 用「reproducibility crisis in medical RL benchmarks」做 motivation 起手式。

### C.7 Survey / Imitation Learning（補充）

- Imitation learning for clinician policy modeling（behavior cloning 在 sepsis 上的應用）有零星工作，但沒有單一 canonical paper。我們可以在 Related Work 一段內 cover。
- 通用 imitation learning reference：Hester et al. 2018 "Deep Q-learning from Demonstrations" (AAAI) 是 expert-init Q-learning 的經典 cite；如果我們做 Direction 2（expert-init）會用到。

---

## D. Action Masking 與 Reward Shaping 的通用理論文獻

### D.1 Invalid Action Masking

| 項目 | 內容 |
|---|---|
| Title | A Closer Look at Invalid Action Masking in Policy Gradient Algorithms |
| Authors | Shengyi Huang, Santiago Ontañón |
| Venue / Year | FLAIRS-34, 2021；arXiv [2006.14171](https://arxiv.org/abs/2006.14171) |
| Status | **Peer-reviewed**（FLAIRS）+ arXiv |

**重點**：
- 對 PG 演算法（PPO 等）做 invalid action masking vs invalid action penalty 的對照實驗。
- masking 在大 invalid action 比例下顯著優於 penalty（差距 > 50%）。
- masking 等價於 PG with masked sampling distribution；gradient 結構正確。

**對我們的關係**：核心引用。雖然他們是 PG，我們是 Q-learning，但 masking 的 motivation（exploration 浪費、wrong gradient）對 Q-learning 也成立。我們的 paper 是 *把 masking 從 RTS games 帶到 medical RL benchmark*，並比較 "no mask + mean strategy"、"no mask + terminate strategy"、"action-masked Q-learning" 三者，這是原 paper 沒有的對照。

### D.2 Forbidden Action 的 Q-learning 處理

| 項目 | 內容 |
|---|---|
| Title | I'm sorry Dave, I'm afraid I can't do that: Deep Q-learning from forbidden actions |
| arXiv | [1910.02078](https://arxiv.org/abs/1910.02078) |
| Status | Preprint（被部分 follow-up 引用） |

**重點**：在 Q-learning 框架下處理 forbidden action 的方法。可作為 algorithmic baseline 比較。

### D.3 Potential-Based Reward Shaping

| 項目 | 內容 |
|---|---|
| Title | Policy invariance under reward transformations |
| Authors | Andrew Y. Ng, Daishi Harada, Stuart Russell |
| Venue | **ICML 1999** |
| Status | **Peer-reviewed**（經典） |

**重點**：F(s, s') = γΦ(s') - Φ(s) 保留 optimal policy。對我們 Direction 3 (SOFA-based reward shaping) 必引；保證 task objective 不被改變。

---

## D. 我們的定位（綜合判斷）

> 此段是給我們自己看的，回答你列的 D 部分問題。

### D.1 哪些事情已有人做？（不能做為主要 contribution）

1. **在 ICU-Sepsis 上跑 Q-learning / SARSA / DQN / SAC / PPO 的 learning curve** → 原 paper 已做。
2. **MIMIC-III 上的 offline RL for sepsis treatment** → AI Clinician、Raghu 等已做，且是 oversaturated 領域。
3. **claim「我們的 policy 比 clinician 好」** → 嚴重 medical claim，OPE 不可靠，已被廣泛 critique。
4. **在 tabular MDP 上 reproduce VI / Q-learning** → 教科書級內容，不算 novel。

### D.2 哪些題目對 5 天太大？

| 題目 | 為何太大 |
|---|---|
| 重新從 MIMIC-III 建環境並校準 | 需要 PhysioNet credential、MATLAB pipeline、數週 |
| Continuous-state ICU-Sepsis variant | 需要 redesign env，超出 5 天 |
| 完整 safe RL with constrained MDP solver | 需要實作 CMDP solver（CPO / RCPO），1 週起跳 |
| Offline RL (CQL / IQL / TD3+BC) on logged data | 沒有現成 logged dataset，自己 roll out 半天，調參另一天 |
| Off-policy evaluation methodology paper | 是另一個專題，與我們環境模型已知的優勢衝突 |
| 多代理 RL (MARL) 變體 | 環境是單病人單代理，沒有自然 MARL formulation |

### D.3 哪些角度仍然適合我們？

1. **inadmissible_action_strategy 的系統比較**（原 paper 未做）
2. **action masking ablation**（原 paper 未做，但理論上重要）
3. **學習穩定性 / sample efficiency / policy agreement with expert / state-wise unsafe action rate** 這些 metric 在原 paper 沒有完整報告
4. **多 seed × 多 algorithm × 多 strategy 的 ablation matrix**（dimension 雖小但組合分析新穎）
5. **lightweight reward shaping ablation**（SOFA-potential）但必須用 Ng-Russell 保證 invariance

### D.4 如何避免誇大 medical claim

- Abstract / Intro / Conclusion 不出現「improves patient survival」、「clinical recommendation」等字眼。
- 用 *survival rate* 時加上「(within this benchmark MDP)」。
- 用 *safety proxy* / *unsafe action rate (with respect to clinical-data-defined admissibility)* 而不是「safe」/「unsafe」。
- Limitations 段明寫「benchmark is a statistical abstraction; conclusions are about algorithmic behavior on the benchmark, not clinical recommendations」。
- 引用 Gottesman 2019 的 guideline 來合法化「we deliberately do not make clinical claims」的 stance。

### D.5 如何定位成 benchmark / algorithmic paper

paper 的 contribution bullets 寫成：

1. We provide the **first systematic comparison of the three inadmissible_action_strategy modes** offered by ICU-Sepsis-v2 (`mean` / `terminate` / `raise_exception`) and characterize how each affects RL training dynamics.
2. We show that **action masking using the env's per-state admissible action set** changes (a) sample efficiency, (b) inadmissible-action rate during training, (c) distance to V*, in ways not captured by survival rate alone.
3. We propose a **multi-metric evaluation protocol** for ICU-Sepsis (return, ep-length, distance-to-V*, policy-agreement-with-expert, inadmissible-action-rate-per-state-bucket) and release scripts to compute them.

這三點都是 **benchmark-level methodological contribution**，無需 clinical claim 即可成立。

### D.6 預先 defend：「這不是 deep RL / tabular MDP 太簡單」

可能的 reviewer 質疑：
> "The DRL course mini-conference asks for DRL-focused topics. Tabular Q-learning on a 716-state MDP is not deep RL."

我們的 defence（可放在 Section 1 introduction 末段 + appendix）：
1. **DRL course 的目的（PDF slide 5）是 "doing RL research / writing research paper / participating in review"**，不是限制只能用 deep networks。RL methodology 本身就是 final project scope 接受的主軸。
2. ICU-Sepsis 原 paper（RLC 2024）也是 tabular benchmark；它本身就是 RL research 領域接受的 contribution 形式。
3. 為了 **不留口實**，我們在 Section 4 加 **1 個 DQN baseline**（state 用 one-hot encoding 或 cluster centroid 連續向量），讓 reviewer 看到 "tabular and deep both supported and analyzed"。DQN 訓練在 ICU-Sepsis 上 paper 報告約幾十萬 episodes，雖然慢但仍在 5 天可承擔範圍（單 seed 過夜跑）。
4. 並非 method-level deep contribution，**focus is on benchmark analysis**——這在 NeurIPS / RLC 一直有 "Datasets & Benchmarks" track 接受空間，propre framing 即可。

---

## E. Related Work 段落草稿（直接放進 paper 用）

> 以下是英文段落的初稿，後續可調整。

### E.1 Related Work（≈ 0.75 頁）

**Sepsis treatment with reinforcement learning.**
Reinforcement learning for sepsis treatment has been studied extensively, beginning with Komorowski et al.'s AI Clinician [Komorowski2018Nature] which formulates the problem as a Markov decision process over clinical clusters derived from MIMIC-III. Follow-up work extends this with continuous-state representations and deep Q-networks [Raghu2017MLHC], distributional RL [PLOSone2022], and a range of offline / safe RL methods [Springer2025OfflineSafe; sciltp2024CPQIQL]. A persistent critique of this line of work is the difficulty of off-policy evaluation and the risk of overclaiming clinical relevance [Gottesman2019NatMed].

**Benchmarks for medical RL.**
To mitigate reproducibility issues caused by ad-hoc cohort processing, recent work has proposed standardized benchmarks: ICU-Sepsis [Choudhary2024RLC] is a 716-state, 25-action tabular MDP distilled from MIMIC-III via the Komorowski pipeline, designed so that researchers can evaluate RL algorithms without MIMIC-III access. MIMIC-Sepsis [arXiv2510.24500] proposes a complementary MIMIC-IV-based benchmark covering mortality, length-of-stay, and shock onset. Our work uses ICU-Sepsis as the evaluation environment but, unlike prior usage that focuses on training a single policy, we systematically analyze how the benchmark's *inadmissible action handling* and *action masking* affect RL training behavior.

**Action masking and invalid actions.**
The treatment of invalid or inadmissible actions has been studied in policy gradient methods, where action masking [Huang2021FLAIRS] is shown to outperform action penalties in environments with large invalid action sets. In Q-learning, similar techniques propose ignoring invalid actions during max [Boutilier1910Forbidden]. To our knowledge, these techniques have not been applied to medical RL benchmarks, where "inadmissibility" has a statistical-evidence origin rather than a hard physical constraint.

**Reward shaping.**
Potential-based reward shaping [Ng1999ICML] preserves the optimal policy under any potential function. We use this to motivate optional SOFA-score-based shaping experiments without altering the task objective.

> **References to verify on Day 1**（在 Day 1 Related Work 完善時逐一查 venue / year / 完整 author list）：
> - sciltp2024CPQIQL: venue 真實性、authors
> - Springer2025OfflineSafe: 完整 citation
> - PLOSone2022 distributional RL: 完整 citation
> - arXiv 2510.24500 MIMIC-Sepsis: 完整 citation
> - Boutilier1910Forbidden: 完整 citation (arXiv 1910.02078)

---

## F. Citation key list（給 LaTeX 用）

```
choudhary2024icusepsis    -> ICU-Sepsis RLC 2024
komorowski2018aiclinician -> AI Clinician Nature Medicine 2018
raghu2017continuous       -> Continuous state DDQN MLHC 2017
gottesman2019guidelines   -> Healthcare RL guidelines Nature Med 2019
ng1999reward              -> Ng Harada Russell ICML 1999
huang2021masking          -> Invalid action masking FLAIRS 2021 / arXiv 2006.14171
suttonbarto2018           -> Sutton & Barto textbook (Q-learning, SARSA, Dyna-Q)
```

> 寫 paper 時請務必確認所有 venue / year / 完整作者；preprint 在 final draft 前要再查一次有沒有 conference 接收。

---

## G. Citation verification log (2026-05-20 autonomous run)

> This section was added by an autonomous overnight verification pass on
> 2026-05-20. The body of sections A–F above is **unchanged**; this log
> records the verification status of every "未驗證 / Unverified" or
> deferred-to-Day-1 item flagged in those sections, plus any corrections
> we found along the way. All canonical BibTeX entries now live in
> `paper/references.bib` and each entry there carries its own
> `note = {verified via …}` field listing the authoritative source.

### G.1 Items the original notes explicitly flagged as needing verification

| Original-notes label | Section | Verification result |
|---|---|---|
| `sciltp2024CPQIQL` (CPQ-IQL safe offline RL) | B.1, E.1 | **VERIFIED with caveats.** Authors: Bailing Zhang and Yuwei Mi. Venue: *Transactions on Artificial Intelligence* (Scilight Press), vol. 2, no. 1, pp. 103–118, 2026. DOI 10.53941/tai.2026.100007. The journal is peer-reviewed and open-access per its editorial policy (Editor-in-Chief: Prof. Dapeng Oliver Wu, City University of Hong Kong) but is a *newly-launched, non-Scopus-indexed* venue. Cite as a peer-reviewed but lower-tier source; do not present as headline prior work. Saved as `cpqiql_safe_offline_sepsis` in references.bib. |
| `Springer2025OfflineSafe` (Offline Safe RL for Sepsis) | C.4, E.1 | **VERIFIED.** Full author list: Rui Tu, Zhipeng Luo, Chuanliang Pan, Zhong Wang, Jie Su, Yu Zhang, Yifan Wang. Venue: *Human-Centric Intelligent Systems* (Springer), vol. 5, no. 1, pp. 63–76, 2025. DOI 10.1007/s44230-025-00093-7. Verified via DBLP (`journals/hcisys/TuLPWSZW25`). Saved as `springer2025offlinesafe`. |
| `PLOSone2022` (distributional RL "superhuman") | C.6, E.1 | **VERIFIED.** Title: *Superhuman performance on sepsis MIMIC-III data by distributional reinforcement learning.* Authors: Markus Böck, Julien Malle, Daniel Pasterk, Hrvoje Kukina, Ramin Hasani, Clemens Heitzinger. *PLOS ONE* 17(11): e0275358, 2022. DOI 10.1371/journal.pone.0275358. Verified via the PLOS ONE landing page. Saved as `plosone2022superhuman`. |
| `arXiv2510.24500` (MIMIC-Sepsis) | B.1, C.6, E.1 | **VERIFIED as preprint.** Full author list: Yong Huang, Zhongqi Yang, Amir M. Rahmani. v1 posted 2025-10-28. **No peer-reviewed venue found as of 2026-05-20** (an OpenReview thread exists at `openreview.net/forum?id=iWvvpiA5ej` but no acceptance recorded). Recommend citing **as preprint** with `arXiv:2510.24500` and re-checking the day before submission in case a venue appears. Saved as `mimic_sepsis_arxiv2510_24500`. |
| `Boutilier1910Forbidden` (DQN-from-forbidden-actions) | D.2, E.1 | **VERIFIED — with a meaningful correction.** The original notes used `Boutilier` as the citation key. **This attribution was wrong.** The actual authors of arXiv 1910.02078 are **Mathieu Seurin, Philippe Preux, and Olivier Pietquin**. The paper appeared at **IJCNN 2020** in Glasgow, UK (not 2019). The arXiv preprint was first posted 2019-10-04, which presumably explains why the original notes used `2019` and a misremembered key. The references.bib entry has been re-keyed as `seurin2020forbidden`; the old `boutilier2019forbidden` key is preserved only as a comment alias for back-compatibility with any draft prose. **Action required:** any LaTeX prose still referencing `boutilier2019forbidden` or "Boutilier (2019)" must be updated. |
| `Safe RL for Sepsis Treatment` (Jia et al., AAI29281130) | C.4 | **STILL UNVERIFIED.** The ACM DL record `10.5555/AAI29281130` is a ProQuest-mirrored thesis, not a peer-reviewed paper, and the author list was uncertain in the original notes ("Jia et al., 具體 author list 待 Day 1 verify"). Recommend **dropping** unless explicit thesis citation is required; in any case do not use as a primary related-work anchor. **Not added to references.bib.** |

### G.2 Items the original notes already classified as "Peer-reviewed" — confirmed clean

| Key | Original-notes section | Verification source |
|---|---|---|
| `choudhary2024icusepsis` | A.1 | rlj.cs.umass.edu/2024/papers/Paper194.html (canonical RLJ vol. 4, pp. 1546–1566). arXiv 2406.05646 confirmed (v1 2024-06-09, v2 2024-10-14). |
| `komorowski2018aiclinician` | C.1 | PubMed 30349085 confirms: *Nature Medicine* 24(11):1716–1720, 2018. DOI 10.1038/s41591-018-0213-5. Full author list confirmed: Komorowski M, Celi LA, Badawi O, Gordon AC, Faisal AA. |
| `raghu2017continuous` | C.2 | proceedings.mlr.press/v68/raghu17a.html confirms: PMLR v68, pp. 147–163, MLHC 2017. Full author list confirmed: Raghu A, Komorowski M, Celi LA, Szolovits P, Ghassemi M. Editor list also recorded in the BibTeX `note`. |
| `gottesman2019guidelines` | C.3 | PubMed 30617332 confirms: *Nature Medicine* 25(1):16–18, January 2019. DOI 10.1038/s41591-018-0310-5. Full author list confirmed: Gottesman O, Johansson F, Komorowski M, Faisal A, Sontag D, Doshi-Velez F, Celi LA. |
| `ng1999reward` | D.3 | ACM DL 10.5555/645528.657613 confirms: ICML 1999, pp. 278–287, Morgan Kaufmann. Authors confirmed: Andrew Y. Ng, Daishi Harada, Stuart J. Russell. |
| `huang2021masking` | D.1 | **Correction to the original notes' venue:** the canonical publication is FLAIRS-**35** (vol. 35 of the FLAIRS proceedings), **2022**, DOI 10.32473/flairs.v35i.130584 — not FLAIRS-34 / 2021 as the original §D.1 stated. The arXiv preprint (2006.14171) is from June 2020, which presumably explains the date confusion. Citation key kept as `huang2021masking` to avoid breaking any pre-existing draft text, but the BibTeX entry now correctly states year 2022 and volume 35. **Action required:** any prose referring to "FLAIRS-34 (2021)" should be updated to "FLAIRS-35 (2022)." |
| `suttonbarto2018` | F (citation key list) | MIT Press 9780262039246. Verified via mitpress.mit.edu/9780262039246/reinforcement-learning/. |

### G.3 Summary

- **12 of 13** target citations verified against an authoritative source and
  written to `paper/references.bib` with explicit `note = {verified via …}`
  fields recording where the metadata came from.
- **1 entry** (the ACM DL "Safe RL for Sepsis Treatment" / `AAI29281130`
  thesis-like record) **was not added** because authorship and venue could
  not be established and it is not load-bearing for our Related Work.
- **Two corrections** in original notes that need carrying forward into the
  draft paper prose: (a) the "Boutilier" attribution for arXiv 1910.02078
  is wrong — actual authors are Seurin, Preux, Pietquin; (b) Huang &
  Ontañón's invalid-action-masking paper is FLAIRS-35 (2022), not
  FLAIRS-34 (2021).
- **One MIMIC-Sepsis caveat:** `arXiv:2510.24500` is still preprint-only;
  re-check the day before submission in case of formal publication.
- **One CPQ-IQL caveat:** the *Transactions on Artificial Intelligence*
  (Scilight Press) venue is peer-reviewed but very young and not in
  Scopus / Web of Science; we keep it in references.bib but should not
  use it as a load-bearing precedent in arguments about prior art.
