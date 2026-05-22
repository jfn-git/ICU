# 10. Codex Research Tasks — Background & Literature for Paper Writing

> **指派者**：Claude（與使用者協調後）
> **對象**：Codex
> **日期**：2026-05-22
> **deadline 脈絡**：paper submission 2026-05-25 23:59，所以這些研究產出最好在 **05-23 內**回來，給寫作留時間。

---

## 0. 分工協議（重要，避免衝突）

- **Claude 負責**：所有實驗 code 與跑數據（P0 dead-end / P1 penalty-conservative sweep / P2 expert-prior），以及最後的 submission folder 整理。
- **Codex 負責（本文件）**：**background research + 文獻查證 + 可直接貼進 paper 的素材**。
- **請 Codex 不要改動** `src/`、`scripts/`、`results/`、`figures/`，避免和 Claude 正在跑的實驗衝突。Codex 的產出請寫到**新檔案**：
  - `core_docs/11_literature_verified.md`（查證後的文獻表 + BibTeX）
  - `core_docs/12_related_work_draft.md`（Related Work 英文草稿）
  - `paper/references.bib`（**只新增**，不要刪除既有條目；若修正既有條目請在 commit message 註明）

---

## 1. 已定案的專案方向（給 Codex 的 context）

經過 Claude×Codex 兩份方向文件對讀（見 `07_*`、`08_*`、`09_*`），已定案：

**主線（spine）**：把 ICU-Sepsis 的 inadmissible-action 問題重新詮釋為 **offline RL 的 out-of-distribution (OOD) / low-support action 問題**，並利用 benchmark 罕見的 **exact V***，精確比較一族 support-aware remedy：
`vanilla → support penalty(λ) → conservative/pessimistic → behavior-constraint → hard mask`。

**motivation**：沿用 "mean imputation hides unsupported actions" 的 hidden-failure-mode framing（既有 mask 結果是光譜上一點）。

**補充章節（選項甲，已採用）**：
1. **Exact dead-end analysis**：因 reward=survival indicator 且 γ=1，V*(s)=最大存活機率，可精確算死局 state / 通往死局的 action。
2. **Expert-guided + admissible projection**：env 內建 expert policy（約 16% mass 落在 inadmissible），比較 raw vs 投影到 admissible set。

**安全 framing**：全程 benchmark-internal / safety-proxy，**非臨床建議**。

---

## 2. Codex 的核心任務：把 paper 需要的文獻查證並整理成可用素材

對每一篇，請產出：**(a) 正確 venue + year**、**(b) 一句話 contribution**、**(c) 一句話「我們為何引用 / 如何定位我們的差異」**、**(d) 可編譯的 BibTeX**。
沿用團隊「未驗證」慣例：查不到正式 venue 的，標 `[未驗證]` 並註明來源性質（arXiv / workshop / blog）。

### 任務群 A — 主線 (offline RL / OOD action) 必備

1. **ICU-Sepsis benchmark 本體**：Choudhary et al.（RLC/RLJ 2024，arXiv:2406.05646）。確認正式 venue 名稱與作者全名、年份。
2. **Offline RL OOD-action 三大法**：
   - BCQ — Fujimoto et al. "Off-Policy Deep RL without Exploration"（ICML 2019）
   - CQL — Kumar et al. "Conservative Q-Learning for Offline RL"（NeurIPS 2020）
   - BEAR — Kumar et al. "Stabilizing Off-Policy Q-Learning via Bootstrapping Error Reduction"（NeurIPS 2019）
3. **Pessimism 理論**：Rashidinejad et al. "Bridging Offline RL and Imitation Learning: A Tale of Pessimism"（NeurIPS 2021）；如可，補一篇 tabular pessimistic VI / VI-LCB 的代表作（如 Jin et al. 2021 "Is Pessimism Provably Efficient for Offline RL?"）。
4. **Invalid / forbidden action masking**：
   - Huang & Ontañón "A Closer Look at Invalid Action Masking in PPO"（FLAIRS 2022）
   - （Codex 08 提到的）Seurin/Preux/Pietquin forbidden-action Q-learning（IJCNN 2020）— 查證。

### 任務群 B — 補充章節 (dead-end / expert) 必備

5. **Medical dead-ends**：Fatemi et al. "Medical Dead-ends and Learning to Identify High-risk States and Treatments"（NeurIPS 2021）。**重點**：找出他們是用「估計」survival/dead-end，好讓我們強調「我們用已知 dynamics 算 exact dead-ends」的差異。
6. **Sepsis RL 起源 / expert(clinician) policy**：
   - Komorowski et al. "The AI Clinician..."（Nature Medicine 2018）
   - Raghu et al. continuous-state DDQN for sepsis（MLHC 2017 或 arXiv 2017，查證）
7. **Healthcare RL 評估警示**（支撐我們 multi-metric / exact-V* 論述）：Gottesman et al. "Guidelines for RL in healthcare"（Nature Medicine 2019）及/或 Gottesman et al. 2018 評估方法那篇。
8. **Imitation / expert warm-start in RL**（給 expert-prior 章節）：找 1–2 篇代表性的 "expert-guided exploration / behavior-prior" 文獻（如 DQfD: Hester et al. AAAI 2018；或 healthcare 內的 imitation+RL）。

### 任務群 C — 加分 / 防守用（時間夠再做）

9. **Factored action spaces in healthcare RL**：Tang et al. "Leveraging Factored Action Spaces for Efficient Offline RL in Healthcare"（NeurIPS 2022）— 即使我們 factored 只當次要，也要有 citation 防守。
10. **Potential-based reward shaping**：Ng, Harada, Russell（ICML 1999）— 若最後納入 SOFA 章節才需要。
11. **Reproducibility / safe-RL in sepsis 近作**（Codex 08 列的 Tu et al. 2025、Zhang & Mi 2026）— 查證是否真實存在、是否 peer-reviewed；可疑就標 `[未驗證]`。

---

## 3. 具體產出格式（請 Codex 照這個寫 `11_literature_verified.md`）

每篇一個區塊：

```
### [key] Author et al., Venue Year
- Verified: ✅ / [未驗證: arXiv-only]
- Contribution (1 sentence):
- Why we cite / our difference (1 sentence):
- BibTeX:
  @inproceedings{key, ... }
```

並在檔尾附一段 **"Positioning paragraph"**：用 3–5 句話說明「我們的工作與上述文獻的關係」，可直接改寫進 Related Work。

---

## 4. Related Work 草稿（`12_related_work_draft.md`）

請 Codex 依下列結構寫 ~350–500 字英文草稿（雙盲、無身份資訊）：

1. **Medical RL benchmarks**（ICU-Sepsis、AI Clinician 一脈、為何要 reproducible tabular benchmark）。
2. **Offline RL & OOD actions**（BCQ/CQL/pessimism；點出 admissibility = data-support 約束）。
3. **Action masking / invalid actions**（masking 是 OOD 的 hard-constraint 端點）。
4. **Risk & dead-ends in clinical RL**（Fatemi；我們的 exact-dead-end 差異）。
5. **Evaluation pitfalls**（Gottesman；為何要 distance-to-V* 而非只看 survival rate）。

每段結尾用一句點出「**our work differs by …**」。

---

## 5. 兩個給 Codex 的明確問題（請在產出中回答）

1. **Novelty 防守**：在 offline RL 文獻中，是否已有人「在已知 dynamics 的 tabular medical benchmark 上，把 mean-imputation 造成的 OOD 隱藏問題明確化，並比較 penalty/pessimism/mask 光譜」？若有，請列出，讓我們調整 claim。
2. **Dead-end novelty 防守**：是否已有人用「已知 dynamics 算 exact dead-ends」（而非估計）？Fatemi 是估計版；若有 exact 版前例，請指出。

---

## 6. 交付與回報

- 產出檔：`core_docs/11_literature_verified.md`、`core_docs/12_related_work_draft.md`、（新增）`paper/references.bib` 條目。
- 完成後在本檔尾或群組回報「已完成任務群 A/B/C 之哪些」。
- 任何 `[未驗證]` 條目請集中列在 `11_*` 檔尾，方便 Claude/使用者最後人工核對。
