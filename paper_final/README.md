# paper_final — submission package

Self-contained NeurIPS-2026 (anonymous) submission, synthesized from the teammate's
lean writing base (`main_teamates.tex`) + our figure management.

## Contents
- `main.tex` — the paper (main file to compile)
- `references.bib` — bibliography (all cited keys verified present)
- `figures/` — the 7 PNGs used by `main.tex` (main: component_ablation,
  exact_dist_curve, offline_datasize; appendix: penalty_tradeoff, expert_prior_curve,
  robustness, deadend_structure)

## ⚠️ Before compiling on Overleaf
Add **`neurips_2026.sty`** to this folder — it is NOT in this repo (get it from the
teammate's repo / NeurIPS 2026 style bundle). Without it the build fails.
Submit in anonymous mode: do **not** pass `[final]` to `\usepackage{neurips_2026}`
(anonymous mode auto-prints "Anonymous Author(s)" and turns on line numbers).

Then **Recompile ×2** (bibtex + label/figure-number settling).

## Notes on the synthesis (vs. main_teamates.tex)
- Brought the **exact learning-curve** figure back into the main text (§5.3, Fig 2);
  moved the **penalty-sweep** figure to the appendix to keep it page-neutral.
- Weakened the ablation-table and hero-figure captions (dropped the bare
  "necessary and sufficient" phrasing) and aligned §5.1 wording with the Discussion.
- Compressed the Reproducibility statement to a short paragraph; removed the empty
  `ack` block (anonymous submission).
- `\input{checklist.tex}` is commented out (the course does not require the NeurIPS
  checklist). Add `checklist.tex` here and uncomment if you want it.

## Page check
Target: main content through the Reproducibility statement ≤ 8 pages, so **References
start on page 9**. If it overflows, dial back in this order: exact-curve
`0.60→0.55`, hero `0.95→0.90`. (Appendix is unlimited; figure sizes there are free.)
