# paper_final — submission package

Self-contained NeurIPS-2026 (anonymous) submission, synthesized from the teammate's
lean writing base (`main_teamates.tex`) + our figure management.

## Contents
- `main.tex` — the paper (main file to compile)
- `neurips_2026.sty` — official NeurIPS 2026 style file (included; do not edit)
- `references.bib` — bibliography (all cited keys verified present)
- `checklist.tex` — NeurIPS Paper Checklist, answers filled in (input at end of `main.tex`)
- `figures/` — the 8 PNGs used by `main.tex`:
  - main text: `component_ablation` (hero), `exact_dist_curve`, `offline_datasize`
  - appendix: `fig1_return_tiers`, `penalty_tradeoff`, `expert_prior_curve`,
    `robustness`, `deadend_structure`

## ⚠️ Before compiling on Overleaf
This folder is self-contained — upload it as-is. Submit in **anonymous mode**: do
**not** pass `[final]` to `\usepackage{neurips_2026}` (anonymous mode auto-prints
"Anonymous Author(s)" and turns on line numbers).

Then **Recompile ×2** (bibtex + label/figure-number settling).

## Notes on the synthesis (vs. main_teamates.tex)
- Brought the **exact learning-curve** figure back into the main text (§5.3, Fig 2);
  moved the **penalty-sweep** figure to the appendix to keep it page-neutral.
- Weakened the ablation-table and hero-figure captions (dropped the bare
  "necessary and sufficient" phrasing) and aligned §5.1 wording with the Discussion.
- Compressed the Reproducibility statement to a short paragraph; removed the empty
  `ack` block (anonymous submission).
- `checklist.tex` is **included and filled in** (16 answers + justifications), and
  `\input{checklist.tex}` is active at the end of `main.tex`. The checklist follows
  the references/appendix and does **not** count toward the page limit. The course
  does not strictly require it, but a filled checklist is included for completeness.

## ⚠️ Two checklist answers to verify before submitting
- **Q5 (Open access to data and code)** is set to `\answerYes` and states an
  anonymized code supplement is provided. If you will *not* upload an anonymized
  code zip, change it to `\answerNo` (and update the justification) — do not leave
  Yes without attaching code.
- **Q8 (Compute resources)** states "single commodity CPU, no GPU, tabular." If
  DQN/PPO were actually trained on a GPU, edit the justification.

## Page check
Target: main content through the Reproducibility statement ≤ 8 pages, so **References
start on page 9** (checklist + references + appendix are page-unlimited). If it
overflows, dial back in this order: exact-curve `0.60→0.55`, hero `0.95→0.90`.
(Appendix figure sizes are free.)
