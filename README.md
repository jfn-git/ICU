# Action Admissibility Matters — ICU-Sepsis Benchmark Study

> 系統比較 **inadmissible-action handling** 與 **action masking** 對 tabular RL
> （Q-learning / SARSA / Dyna-Q）在 [ICU-Sepsis (Choudhary et al., RLC 2024)](https://arxiv.org/abs/2406.05646)
> benchmark 上的 performance / safety-proxy / sample-efficiency / stability 影響。

> ⚠️ **這是 benchmark-level algorithmic analysis，不是臨床建議。** Paper 中所有 metric
> 皆標示為 "benchmark-internal" / "safety proxy"，不可解讀為醫療決策依據。

DRL 課程期末專案。完整題目背景、實驗計畫與時程見 [`core_docs/README.md`](core_docs/README.md)。

---

## 專案結構

```
.
├── src/                # 核心程式碼
│   ├── env_utils.py    #   建立 ICU-Sepsis env、取得 dynamics / V*
│   ├── tabular_rl.py   #   Q-learning / SARSA / Dyna-Q（含 use_mask 開關）
│   ├── policies.py     #   Random / Expert / Deterministic policy
│   ├── evaluate.py     #   rollout evaluation
│   └── analysis.py     #   distance-to-V*、agreement-with-expert 等 metric
├── scripts/            # 可執行實驗腳本
│   ├── run_masking_ablation.py   # 主實驗：mask on/off ablation
│   └── compute_dynamics_stats.py
├── configs/default.yaml
├── tests/              # pytest sanity checks
├── results/            # 實驗輸出 (JSON)
├── figures/            # 圖
├── paper/              # references.bib 等
└── core_docs/          # 內部規劃文件（繁中）：題目、計畫、時程、reviewer Q&A
```

> 注意：第三方環境套件 `icu-sepsis/`（公開 repo 的 clone，含大型二進位檔）**未**納入本 repo，
> 請依下方 Setup 自行安裝。

---

## Setup

需要 **Python 3.13**（開發環境為 Anaconda / miniconda）。

```bash
# 1. 安裝 ICU-Sepsis 環境（第三方公開套件，editable install）
git clone https://github.com/icu-sepsis/icu-sepsis.git
python -m pip install -e ./icu-sepsis/packages/icu_sepsis
python -m pip install -e ./icu-sepsis/packages/icu_sepsis_helpers

# 2. 安裝本專案其餘相依套件
python -m pip install -r requirements.txt
```

---

## 執行方式

所有指令請在 **專案根目錄** 下執行（腳本會自行把根目錄加進 `sys.path`）。

```bash
# 主實驗：Q-learning × {mask off, mask on} × mean strategy × 5 seeds × 50k eps
# 輸出 → results/bundle_c_masking/*.json，圖 → figures/preliminary_curve.png
python scripts/run_masking_ablation.py

# 環境 dynamics 統計
python scripts/compute_dynamics_stats.py

# 測試
python -m pytest -q
```

主要設定（env id、strategy、演算法、超參數、seeds）見 [`configs/default.yaml`](configs/default.yaml)。

---

## 評估 metric

| metric | 意義 |
|---|---|
| `distance_to_Vstar` | 學到的 policy 與 value-iteration oracle V* 的差距 |
| `J(π)` (d0-weighted) | 初始分布加權的 policy value |
| inadmissible-action rate | safety proxy：選到不可行動作的比率 |
| agreement-with-expert | 與內建 expert policy 的一致度 |
