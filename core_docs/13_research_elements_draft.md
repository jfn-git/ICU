# 13. Research Elements — Plain + Professional (DRAFT / 中間產出)

> ⚠️ **狀態：草稿 / 中間產出，表達尚未到位，待精修。**
> 目的：把目前研究的所有元素用「專業 + 白話」雙版本列出，方便寫 paper / 對齊組員 / 餵 codex。
> 用詞、結構、舉例之後會再打磨；數字以 `results/` 為準。
> T2 的數字目前來自 1-seed 冒煙，5-seed 全跑完成後需更新。

---

## 一、地基元素（為什麼這個研究做得成）

**1. 環境：ICU-Sepsis tabular benchmark**
- 專業：716-state、25-action tabular MDP，從 MIMIC-III 敗血症資料蒸餾；dynamics 完全已知。
- 白話：用真實 ICU 病歷做成的「小型棋盤遊戲」，小到每步機率都看得到。

**2. 殺手鐧：exact V***
- 專業：reward=survival indicator 且 γ=1 → value iteration 給精確 V*（最佳可達存活率）。
- 白話：能把「最完美玩法能拿幾分」算到精確，不像一般 RL 只能估。所有結論的可信根基。

**3. 重新框架：admissibility = offline RL 的 OOD 問題**
- 專業：inadmissible（資料支撐不足）action ＝ offline RL 的 out-of-distribution action problem。
- 白話：「沒資料根據的治療選項」就是 offline RL 那個著名難題換名字；我們把成熟工具箱搬來。

---

## 二、核心問題（發現的失敗）

**4. mean imputation 藏起 unsupported actions**
- 專業：`mean` strategy 把 inadmissible 的 transition 補成 admissible 平均，無負訊號；vanilla Q-learning 部署 ~85% 選 inadmissible，但 survival rate 看不出。
- 白話：benchmark 把「沒資料的選項」當「平均選項」，agent 亂選不被扣分，85% 用沒根據治療，成績單卻正常——失敗被藏住。

---

## 三、主線實驗（method 軸）

**5. Baseline 重現（Tbl 1）**
- 專業：exact J = Random 0.780 / Expert 0.782 / Optimal 0.875，吻合原 benchmark。
- 白話：先確認環境沒裝壞，數字對得上。

**6. P1：OOD-remedy 光譜（penalty sweep）**
- 專業：vanilla → support penalty(λ) → hard mask；penalty 可把部署 unsupported 壓到 0，但 distance-to-V* 卡 ~0.085，被 hard mask（0.069）Pareto-dominate。
- 白話：「輕罰」到「硬禁止」排成一條線比；輕罰能少選爛選項，但品質追不上硬禁止。

**7. T1：component ablation + Q-leakage + CQL**
- 專業：mask 拆 behavior/target/policy；behavior masking 必要且充分（behavior-only==full=0.069）；target-only 幾乎沒用（0.085）；policy-only 是部署繃帶（0.083，Q 仍腐化）；CQL-style 保守（κ=1）是最佳軟解（0.080）但仍輸硬約束；Q-leakage 給機制證據（vanilla +0.46 → full −0.80）。
- 白話：把「禁止」拆三處分別測，找出哪一步在起作用＝「訓練時別讓它選/學這些選項」最關鍵；事後補救只有半套。leakage 圖畫出「壞選項價值如何滲漏」。並做了正規 offline RL 保守法(CQL)。

**8. T2：offline 資料量 sweep（最有 RL 深度；數字待 5-seed 更新）**
- 專業：從真 MDP 用 expert 行為抽 N 筆建 empirical MDP，比較 naive(mean補值)/pessimistic(VI-LCB)/masked，全部用真 V* 精確評估。naive 嚴重高估(~+0.2)且 realized 卡在 ~0.096；pessimism 校準(~0)且隨 N 進步(~0.080)；masking unsupported→0。
- 白話：模擬「只有 N 筆病歷」的離線情境。naive 高估自己、給再多資料也學不好；pessimism 老實又越多資料越強；masking 清掉沒根據選項。能精確驗證這件事是我們環境獨有優勢。

---

## 四、補充實驗

**9. P2：expert-guided + admissible projection**
- 專業：expert prior 大勝 vanilla（dist 0.089→0.073、agreement 0.04→0.60）；raw expert 繼承 ~16% inadmissible mass；投影到 admissible 後 unsupported→0.005、value 不變、agreement→0.65。
- 白話：用醫師決策引導學得快很多；但醫師自己 16% 用沒根據選項，投影到有根據選項就乾淨——「照抄醫師」≠「有資料支撐」。

**10. P0：dead-end / harm 結構（含誠實負面結果）**
- 專業：V*(s)=最大存活機率；無 dead-end（min V*=0.198）；SOFA 與存活率負相關（0.916→0.823）；mean 也抹平 inadmissible 較高的即刻死亡風險（0.032 vs 0.023）。
- 白話：檢查有無「怎麼治都會死的絕境」——沒有（原計畫大章節誠實放棄）；但發現連「沒根據選項當下更危險」也被平均補值藏了。

**11. T3：robustness（演算法 × 策略）**
- 專業：失敗+masking 修法在 Q-learning/SARSA/Dyna-Q 都成立；`terminate` 下 vanilla 部署 unsupported 85%→~3–4%（選錯即死→自學避開），證明失敗是 `mean` 特有。
- 白話：換三種演算法都一樣→非演算法怪癖；換「選錯就死」設定 agent 自己避開→證明問題來自「平均補值」。

---

## 五、一句話貢獻

- 專業：We reframe ICU-Sepsis inadmissible-action handling as an offline-RL OOD problem and—uniquely able to evaluate against exact V*—diagnose the hidden failure, locate it mechanistically (behavior-level; component ablation + value-leakage), and map a remedy spectrum (penalty / CQL pessimism / masking) both online and in the finite-data offline regime.
- 白話：不是「跑了個 Q-learning」，而是：指出 benchmark 偷藏一個失敗 → 用拆解實驗精準定位它住在哪 → 拿一整排 offline RL 修法在「能精確打分」的環境裡比較。effort 在診斷、定位、精確量測，不在算力。

---

## TODO（精修方向，待辦）
- [ ] 重寫成更順、更有層次的敘事（目前是清單，paper 需要連貫故事線）。
- [ ] 統一術語中英對照表。
- [ ] T2 換上 5-seed 正式數字。
- [ ] 可能補一張「總覽圖」把所有元素串起來。
