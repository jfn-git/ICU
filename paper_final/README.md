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

## Checklist answers (finalized)
- **Q5 (Open access to data and code)** = `\answerYes`: an anonymized code archive
  (`supplementary_code.zip`, repo root) is attached as supplementary material; upload
  it alongside the PDF on OpenReview.
- **Q8 (Compute resources)** = `\answerYes`: tabular parts run on CPU; the deep
  baselines (DQN/PPO) were trained on a single consumer GPU.
- **Q16 (LLM usage)** = `\answerNA`: LLMs are not a core method component.
- All other answers are filled per the paper (see `checklist.tex`).

## Supplementary code archive
`supplementary_code.zip` (repo root) is the anonymized reproducibility supplement:
`src/`, `scripts/`, `configs/`, `tests/`, `requirements.txt`, and an English README.
It excludes caches, internal planning docs, outputs, and the third-party ICU-Sepsis
package (install from its public repo per the archive's README). Scanned for identity
leaks (no names/emails/personal repo URLs).

## Page check
Target: main content through the Reproducibility statement ≤ 8 pages, so **References
start on page 9** (checklist + references + appendix are page-unlimited). If it
overflows, dial back in this order: exact-curve `0.60→0.55`, hero `0.95→0.90`.
(Appendix figure sizes are free.)
