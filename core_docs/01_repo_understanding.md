# 01. ICU-Sepsis Repo 理解

> 來源：`./icu-sepsis/` 整個 repo（含 `packages/icu_sepsis/`、`packages/icu_sepsis_helpers/`、`examples/`、`README.md`）
> 對應原 paper：Choudhary, Gupta, Thomas, *"ICU-Sepsis: A Benchmark MDP Built from Real Medical Data"*, RLC 2024 ([arXiv:2406.05646](https://arxiv.org/abs/2406.05646))

本文件目的：把 repo 行為 **完整、可實作層級** 整理清楚，後續所有 design choice 都從這裡推。

---

## 1. ICU-Sepsis 是什麼？

- 一個 **離散、tabular、有限 MDP**，模擬一位 sepsis 病人在 ICU 中的治療歷程。
- 用 MIMIC-III 真實病人資料、以 Komorowski et al. (2018) 的 sepsis cohort 為基礎，經 clustering + 統計估計 transition / reward 後封裝成的 RL benchmark。
- 透過 `gymnasium` / `gym` 介面提供 (`Sepsis/ICU-Sepsis-v1`、`Sepsis/ICU-Sepsis-v2`)。
- **核心定位**（原作者立場）：可重現、輕量、無需 MIMIC-III 授權即可使用的 medical RL benchmark；**不是** clinical decision support tool。

---

## 2. RL Problem Formulation

| 元素 | 定義 |
|---|---|
| State space `S` | 716 個離散 state（id 0–715） |
| 終止 state | `STATE_DEATH = 713`、`STATE_SURVIVAL = 714`、`STATE_S_INF = 715`（三者構成 `STATES_TERMINAL`） |
| Action space `A` | `MultiDiscrete([5, 5])` = 25 個離散組合（fluids × vasopressors，各 5 個 level）；預設 `FlattenActionWrapper` 會 flatten 成 `Discrete(25)` |
| Reward `R` | 進入 `STATE_SURVIVAL` 時 +1；進入 `STATE_DEATH` 時 0；其它 transition 0。Reward 是 deterministic function of `s_next`，存在 `_r_mat[s, a, s_next]`。 |
| Transition `P` | `tx_mat[s, a, s_next]` ∈ R^{716×25×716}，每 row sum to 1。 |
| 初始分布 `d_0` | `d_0 ∈ R^{716}`；由 `env.reset()` 從中 sample。終止 state 機率為 0。 |
| Discount `γ` | 預設 **1.0**（無折扣 finite-horizon）。可在 `gym.make(..., gamma=...)` 改。 |
| Horizon | `MAX_EPISODE_STEPS = 500`；論文 baseline 平均 episode length ≈ 9–11，所以 truncation 幾乎不發生。 |

**回報範圍**：episode return ∈ {0, 1}（survive=1, die=0），所以 average return 直接等於 **survival rate**。這是接下來實驗設計的關鍵點。

### 2.1 Repo 等級的重要 source 引用

- 終止 state 與終止集合：[icu_sepsis/utils/constants/\_\_init\_\_.py:1-11](icu-sepsis/packages/icu_sepsis/icu_sepsis/utils/constants/__init__.py#L1-L11)
- Step / transition 邏輯：[icu_sepsis/envs/sepsis.py:174-188](icu-sepsis/packages/icu_sepsis/icu_sepsis/envs/sepsis.py#L174-L188)
- Reset 與初始分布：[icu_sepsis/envs/sepsis.py:162-172](icu-sepsis/packages/icu_sepsis/icu_sepsis/envs/sepsis.py#L162-L172)
- Action flattening wrapper：[icu_sepsis/wrappers/two_d_actions.py:11-26](icu-sepsis/packages/icu_sepsis/icu_sepsis/wrappers/two_d_actions.py#L11-L26)

---

## 3. Model-Free 還是 Model-Based？

**兩者都可以**，由我們選擇要不要用 `env.dynamics`：

1. **Model-free**：把 `env` 當黑盒，呼叫 `reset / step`，可實作 Q-learning / SARSA / Dyna-Q / 任何 deep RL。
2. **Model-based**：`env.unwrapped.dynamics` 會回傳 `{'tx_mat', 'r_mat', 'd_0', 'admissible_actions'}`，可直接做 value iteration / policy iteration / 任何 model-based 分析（這也是 baseline `Optimal` 計算方式）。

→ 這對我們很有利：可以同時跑 model-free 學習曲線 vs. model-based optimal V*，做出乾淨的「距離 optimal 多遠」分析。

---

## 4. 現成 Baselines

repo 提供 3 個內建 baselines（[icu_sepsis_helpers/baselines.py:8-43](icu-sepsis/packages/icu_sepsis_helpers/icu_sepsis_helpers/baselines.py#L8-L43)）：

| Baseline | 來源 | 計算方式 | 用途 |
|---|---|---|---|
| **Random** | `np.random.randint(0, 25)` | 完全均勻隨機 | 下界 reference |
| **Expert** | 估計的 clinician policy `env.expert_policy ∈ R^{716×25}` | 從 MIMIC-III 拍照得到的 stochastic policy，τ-cleaned | 模擬臨床醫師 |
| **Optimal / π*** | `value_iteration(tx_mat, r_mat, γ)` | 用 `dynamics` 跑 VI | 上界 / oracle |

**README 報告數字**（reference）：

| | Random | Expert | Optimal |
|---|---|---|---|
| Avg. return (= survival rate) | 0.78 | 0.78 | 0.88 |
| Avg. episode length | 9.45 | 9.22 | 10.99 |

**有趣現象（我們可以拿來寫 paper）**：Random 與 Expert 的 average return 幾乎一樣高（0.78 vs 0.78）；Optimal 也只多 10 個百分點。這暗示：
1. 環境的 base survival rate 偏高（很多 patient 不論做什麼都 survive）。
2. 「擊敗 random」門檻很低、但「貼近 expert」門檻也很低；**真正困難的是貼近 optimal**。
3. **survival rate 在這個 benchmark 中是個 noisy metric**——所以我們的 paper 必須報告其他 metric（例如 distance to V*、policy agreement with expert、unsafe action rate），不能只看 survival rate。

**Value iteration tolerance**：`max_steps=50000`, `delta=1e-6`（[utils/mdp.py:10-28](icu-sepsis/packages/icu_sepsis_helpers/icu_sepsis_helpers/utils/mdp.py#L10-L28)）。

---

## 5. 重要設定

### 5.1 Admissible / Inadmissible Actions

- 來源：MIMIC-III 中，在某些 state 下某些 action 樣本太少 → 不可信 → 標為 **inadmissible**。
- `env._admissible_actions: list[list[int]]` → 每個 state 都有自己的 admissible action 子集。
- 統計（從 `admissible_actions.txt` 第一行可得）：
  - 716 個 state，admissible action 數量呈現高度不均（從 1 到 12 都有）。
  - 經人工估算，**約 1/4 的 state 只有 1 個 admissible action**（這些 state 任何 RL exploration 都會大量觸發 inadmissible action）。
- `_admissible_action_sets[s]: set[int]` 提供 O(1) 查詢（[envs/sepsis.py:67-69](icu-sepsis/packages/icu_sepsis/icu_sepsis/envs/sepsis.py#L67-L69)）。

### 5.2 `inadmissible_action_strategy`（v2 新增）

由 `gym.make('Sepsis/ICU-Sepsis-v2', inadmissible_action_strategy=...)` 控制：

| Strategy | 行為 |
|---|---|
| `'mean'` (預設，與 v1 同) | inadmissible action 的 transition 用「該 state 下所有 admissible action 的 transition 平均」 |
| `'terminate'` | 立即把病人送到 `STATE_DEATH`，當回合結束 |
| `'raise_exception'` | 直接拋 `InadmissibleActionError` |

→ **這是我們題目最直接的 ablation knob**：同一個 agent，三種 strategy 跑出來會有不同學習曲線與最終 performance。原 ICU-Sepsis paper 只報告 `'mean'` 結果。

實作參考：[envs/sepsis.py:117-141](icu-sepsis/packages/icu_sepsis/icu_sepsis/envs/sepsis.py#L117-L141)。

### 5.3 環境版本

| 版本 | 行為 |
|---|---|
| `Sepsis/ICU-Sepsis-v1` | 永遠 `mean` strategy；改 strategy 會 warning 並 reset。 |
| `Sepsis/ICU-Sepsis-v2` | 預設 `mean`；可改 `terminate` / `raise_exception`。 |

→ 我們應該全程用 **v2**，這樣才能拿 strategy 當 ablation 變數。

### 5.4 Gym / Gymnasium API

- 預設用 `gymnasium`；同時 register 一個 legacy `gym` 版本。
- Step return：`(obs, reward, terminated, truncated, info)`（5-tuple，符合 gymnasium）。
- Action 是 `Discrete(25)`（FlattenActionWrapper 已包好）。

### 5.5 `MAX_EPISODE_STEPS = 500`

由 `gym.envs.registration.register(..., max_episode_steps=500)` 套用（[icu_sepsis/__init__.py:53-71](icu-sepsis/packages/icu_sepsis/icu_sepsis/__init__.py#L53-L71)）。Truncation 在 baseline 上幾乎不會觸發，但若使用 random exploration + `terminate` strategy，可能會大量 early termination。

---

## 6. 可拿來做分析的物件

`env.unwrapped` 直接給出（[envs/sepsis.py:197-244](icu-sepsis/packages/icu_sepsis/icu_sepsis/envs/sepsis.py#L197-L244)）：

| Property | Shape | 內容 |
|---|---|---|
| `num_states` | scalar | 716 |
| `num_actions` | scalar | 25 |
| `gamma` | scalar | 1.0 |
| `expert_policy` | (716, 25) | clinician 估計 policy（已 τ-cleaned，每 row sum to 1） |
| `state_cluster_centers` | (716, D) | 每個 state 在連續 feature space 上的 centroid（可拿來做 t-SNE / state similarity 分析） |
| `sofa_scores` | (716,) | 每個 state 的平均 SOFA score（醫療 severity 指標） |
| `env_metadata` | dict | n_states / n_actions / r_survive=1.0 / r_death=0.0 / threshold=20 / seed / action_map_method |
| `dynamics` | dict | `tx_mat (716,25,716)`, `r_mat (716,25,716)`, `d_0 (716,)`, `admissible_actions` |

從 `info` 每步可拿：
- `info['admissible_actions']`：當前 state 的合法 action list（可直接拿來做 action masking）
- `info['state_vector']`：當前 state 的 cluster centroid（連續特徵向量，若想做 deep RL 可用）
- `info['sofa_score']`：當前 state 的平均 SOFA（可用來做 reward shaping 或 unsafe-action metric）

→ **重要**：`info` 直接給 admissible action list，我們不需要自己解析 `admissible_actions.txt`，**這讓 action masking 變得幾乎 0 成本**。

### 6.1 SOFA score 為什麼有用

SOFA = Sequential Organ Failure Assessment，是 ICU 中標準的 severity 量表。
- 在 paper 中可拿來：
  - 把 state 依 SOFA 分桶，看不同 severity bucket 下 policy 的 performance / unsafe action rate。
  - 做為 reward shaping 的 potential（Δ SOFA 降低時給小獎勵）—— **要小心 medical claim**。
  - 拿來定義 "unsafe action proxy"（在高 SOFA state 上選 admissible action 之外的動作）。

---

## 7. 我們可能的切入點（從 repo 反推）

| 切入點 | 為何 repo 支援 | 五天可行性 |
|---|---|---|
| **三種 inadmissible_action_strategy 系統比較** | v2 直接提供 3 種 strategy；切換成本 = 一個 kwarg | ★★★★★ |
| **Action masking vs. no masking** | `info['admissible_actions']` 每步可取得；mask 實作只需 5 行 | ★★★★★ |
| **Tabular RL (Q-learning / SARSA / Dyna-Q)** | 716×25 = 17900 entries，Q-table 完全裝得下；CPU 訓練秒級 | ★★★★★ |
| **Optimal V* 為 reference 的 sample efficiency 曲線** | `value_iteration` 直接給 V*；可算 ‖V^π − V*‖ | ★★★★★ |
| **Policy agreement with expert** | `env.expert_policy` 直接可拿 | ★★★★★ |
| **SOFA-based reward shaping** | `sofa_scores` 直接可拿；要小心改寫 reward 後 task 變了 | ★★★★（小心 overclaim） |
| **Behavior cloning / expert-init Q-learning** | `expert_policy` 直接 ready | ★★★★ |
| **Offline RL (FQI / CQL on logged trajectories)** | 沒有現成 logged dataset，但可用 expert policy roll out 自己造 | ★★★（要多花半天） |
| **Off-policy evaluation (FQE / IS / WIS)** | 完全 model-known，可直接做；新題目主軸不必擴大 | ★★★ |
| **Deep RL (DQN)** | 用 `info['state_vector']` 或 one-hot；訓練時間可能 1–2 小時 | ★★（在 5 天內可加做 1 個 deep baseline 防守 reviewer） |
| **重新 build 環境（要 MIMIC-III）** | 需要 PhysioNet credential + MATLAB 處理；**5 天內不可能** | ★ |

---

## 8. 用法快速 cheat sheet（給組員）

```python
import gymnasium as gym
import icu_sepsis

# 預設 v2 + 'mean' strategy（與原 paper baseline 一致）
env = gym.make("Sepsis/ICU-Sepsis-v2")

# 切換 inadmissible action strategy
env_term = gym.make("Sepsis/ICU-Sepsis-v2",
                    inadmissible_action_strategy="terminate")

# 取出 model（拿來做 VI / 算 distance to V*）
dyn = env.unwrapped.dynamics             # tx_mat, r_mat, d_0, admissible_actions
expert = env.unwrapped.expert_policy     # (716, 25), per-row sum to 1
sofa   = env.unwrapped.sofa_scores       # (716,)

# Step + info（含 admissible action）
s, info = env.reset(seed=0)
admissible = info["admissible_actions"]  # list[int]
a = some_policy(s, admissible)
s_next, r, terminated, truncated, info = env.step(a)
```

**5 天可立即沿用的觀察**：
1. 環境完全是 CPU、tabular、秒級。**沒有任何 GPU 需求**。
2. 50k episodes 的 baseline evaluation（repo 預設）大約幾分鐘內可跑完，可以放心 multi-seed × multi-config。
3. `dynamics` 完全可見 → 我們有 oracle V*，任何 RL 演算法都有「距離 optimal 多遠」的精確 metric。
4. Reward 是 ∈ {0,1}，evaluation noise 主要來自 episode 數；50k episodes 足以讓 95% CI 收得很窄。

---

## 9. 已知小坑

- `metadata.json` 的 `n_states=750` 是 build 階段的 clustering K，不是最終 state 數；最終 state 數是 716（750 - inactive clusters + 3 terminal states）。**Paper 寫作時要用 716。**
- `state_cluster_centers` 的維度 D 從 `dynamics.npz` 可讀；我們需要 `load_dynamics_and_print_shapes.py` 驗證一次（Day 1 task）。
- `gym` 與 `gymnasium` 雙 register；混用會 warning。**全 project 統一用 `gymnasium`**。
- README 提到的 csv tables 與 `icu-sepsis-csv-tables.tar.gz` 跟 `dynamics.npz` 是冗餘的；**直接用 `dynamics.npz` 就好**。
- VI 預設 `gamma=1.0`，episode 必然終止（716 個 state 中 3 個 absorbing），所以 VI 收斂；但若我們改 `gamma<1` 做 ablation 要確認 VI 仍收斂。
