# 11. Literature Verified — Offline RL / OOD Actions / Dead-Ends / Expert Priors

> Prepared for the ICU-Sepsis paper direction:
> **mean imputation hides unsupported actions; support-aware remedies can be evaluated exactly via V\*.**
>
> Verification date: 2026-05-22.
>
> Scope: this file verifies the papers requested in `10_codex_research_tasks.md` and gives paper-ready positioning notes. BibTeX entries for papers already present in `paper/references.bib` are repeated here for convenience; only missing entries were appended to the `.bib` file.

---

## A. Main Spine: ICU-Sepsis, Offline RL, OOD Actions

### [choudhary2024icusepsis] Choudhary et al., Reinforcement Learning Journal / RLC 2024

- Verified: ✅ Peer-reviewed. Published in *Reinforcement Learning Journal*, volume 4, pages 1546-1566; presented at RLC 2024.
- Contribution (1 sentence): Introduces ICU-Sepsis, a 716-state, 25-action tabular MDP benchmark distilled from MIMIC-III sepsis trajectories, with exact model access and standard RL baselines.
- Why we cite / our difference (1 sentence): We use ICU-Sepsis as the testbed, but unlike the original paper's default `mean` handling and standard algorithm comparisons, we study unsupported-action handling as an OOD-action problem.
- BibTeX:

```bibtex
@article{choudhary2024icusepsis,
  author       = {Choudhary, Kartik and Gupta, Dhawal and Thomas, Philip S.},
  title        = {{ICU-Sepsis}: {A} Benchmark {MDP} Built from Real Medical Data},
  journal      = {Reinforcement Learning Journal},
  volume       = {4},
  pages        = {1546--1566},
  year         = {2024},
  url          = {https://rlj.cs.umass.edu/2024/papers/Paper194.html},
  eprint       = {2406.05646},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG}
}
```

### [fujimoto2019bcq] Fujimoto et al., ICML 2019

- Verified: ✅ Peer-reviewed. PMLR volume 97, pages 2052-2062.
- Contribution (1 sentence): Proposes Batch-Constrained Q-learning (BCQ), which constrains learned policies toward actions likely under the fixed batch dataset to reduce extrapolation error in offline RL.
- Why we cite / our difference (1 sentence): BCQ provides the canonical behavior-constraint endpoint of our support-aware spectrum; ICU-Sepsis gives us an explicit per-state support set and exact V\* evaluation instead of learned generative action support and OPE.
- BibTeX:

```bibtex
@inproceedings{fujimoto2019bcq,
  title        = {Off-Policy Deep Reinforcement Learning without Exploration},
  author       = {Fujimoto, Scott and Meger, David and Precup, Doina},
  booktitle    = {Proceedings of the 36th International Conference on Machine Learning},
  pages        = {2052--2062},
  year         = {2019},
  volume       = {97},
  series       = {Proceedings of Machine Learning Research},
  publisher    = {PMLR},
  url          = {https://proceedings.mlr.press/v97/fujimoto19a.html}
}
```

### [kumar2020cql] Kumar et al., NeurIPS 2020

- Verified: ✅ Peer-reviewed. NeurIPS 2020, Advances in Neural Information Processing Systems 33.
- Contribution (1 sentence): Introduces Conservative Q-Learning (CQL), which learns lower-bounded Q-values by penalizing overestimated actions under offline distribution shift.
- Why we cite / our difference (1 sentence): CQL motivates our pessimistic / conservative treatment of unsupported ICU-Sepsis actions; our implementation is tabular and benchmark-specific rather than a deep offline RL algorithm.
- BibTeX:

```bibtex
@inproceedings{kumar2020cql,
  author       = {Kumar, Aviral and Zhou, Aurick and Tucker, George and Levine, Sergey},
  title        = {Conservative {Q}-Learning for Offline Reinforcement Learning},
  booktitle    = {Advances in Neural Information Processing Systems},
  volume       = {33},
  year         = {2020},
  url          = {https://proceedings.neurips.cc/paper/2020/hash/0d2b2061826a5df3221116a5085a6052-Abstract.html}
}
```

### [kumar2019bear] Kumar et al., NeurIPS 2019

- Verified: ✅ Peer-reviewed. NeurIPS 2019, Advances in Neural Information Processing Systems 32.
- Contribution (1 sentence): Identifies bootstrapping error from out-of-distribution actions in offline Q-learning and proposes BEAR to constrain backup actions using distributional support.
- Why we cite / our difference (1 sentence): BEAR is the clearest conceptual precedent for our claim that backups over unsupported actions can corrupt TD learning; ICU-Sepsis lets us observe the support partition directly.
- BibTeX:

```bibtex
@inproceedings{kumar2019bear,
  author       = {Kumar, Aviral and Fu, Justin and Soh, Matthew and Tucker, George and Levine, Sergey},
  title        = {Stabilizing Off-Policy {Q}-Learning via Bootstrapping Error Reduction},
  booktitle    = {Advances in Neural Information Processing Systems},
  volume       = {32},
  year         = {2019},
  url          = {https://papers.neurips.cc/paper/9349-stabilizing-off-policy-q-learning-via-bootstrapping-error-reduction}
}
```

### [rashidinejad2021pessimism] Rashidinejad et al., NeurIPS 2021

- Verified: ✅ Peer-reviewed. NeurIPS 2021, Advances in Neural Information Processing Systems 34.
- Contribution (1 sentence): Frames offline RL and imitation learning as endpoints of a data-composition spectrum and studies lower-confidence-bound pessimism that adapts across regimes.
- Why we cite / our difference (1 sentence): This supports our spectrum framing from behavior-constrained learning to pessimistic support-aware learning; our expert-prior analysis is an ICU-Sepsis-specific instance with exact model evaluation.
- BibTeX:

```bibtex
@inproceedings{rashidinejad2021pessimism,
  author       = {Rashidinejad, Paria and Zhu, Banghua and Ma, Cong and Jiao, Jiantao and Russell, Stuart J.},
  title        = {Bridging Offline Reinforcement Learning and Imitation Learning: {A} Tale of Pessimism},
  booktitle    = {Advances in Neural Information Processing Systems},
  volume       = {34},
  year         = {2021},
  url          = {https://proceedings.neurips.cc/paper/2021/hash/60ce36723c17bbac504f2ef4c8a46995-Abstract.html}
}
```

### [jin2021pessimism] Jin et al., ICML 2021

- Verified: ✅ Peer-reviewed. PMLR volume 139, pages 5084-5096.
- Contribution (1 sentence): Proposes PEVI, a pessimistic value-iteration method that subtracts uncertainty penalties to handle insufficient coverage in offline RL.
- Why we cite / our difference (1 sentence): PEVI is a principled tabular/linear pessimism reference; our simpler support penalties are a lightweight empirical analogue for the known ICU-Sepsis admissibility partition.
- BibTeX:

```bibtex
@inproceedings{jin2021pessimism,
  title        = {Is Pessimism Provably Efficient for Offline {RL}?},
  author       = {Jin, Ying and Yang, Zhuoran and Wang, Zhaoran},
  booktitle    = {Proceedings of the 38th International Conference on Machine Learning},
  pages        = {5084--5096},
  year         = {2021},
  volume       = {139},
  series       = {Proceedings of Machine Learning Research},
  publisher    = {PMLR},
  url          = {https://proceedings.mlr.press/v139/jin21e.html}
}
```

### [huang2021masking] Huang and Ontanon, FLAIRS 2022

- Verified: ✅ Peer-reviewed. FLAIRS-35, 2022. Note: older project notes incorrectly called this FLAIRS-34 / 2021.
- Contribution (1 sentence): Studies invalid-action masking in policy-gradient algorithms and shows masking can outperform invalid-action penalties when invalid actions are common.
- Why we cite / our difference (1 sentence): This is the core invalid-action-masking reference; our setting differs because ICU-Sepsis inadmissibility is statistical data support, not hard game legality.
- BibTeX:

```bibtex
@inproceedings{huang2021masking,
  author       = {Huang, Shengyi and Onta\~{n}\'{o}n, Santiago},
  title        = {A Closer Look at Invalid Action Masking in Policy Gradient Algorithms},
  booktitle    = {The International {FLAIRS} Conference Proceedings},
  volume       = {35},
  year         = {2022},
  doi          = {10.32473/flairs.v35i.130584},
  url          = {https://journals.flvc.org/FLAIRS/article/view/130584}
}
```

### [seurin2020forbidden] Seurin et al., IJCNN 2020

- Verified: ✅ Peer-reviewed. IJCNN 2020. The earlier "Boutilier" attribution in old notes was wrong.
- Contribution (1 sentence): Studies deep Q-learning with forbidden actions and introduces losses that push Q-values of forbidden actions below those of admissible actions.
- Why we cite / our difference (1 sentence): This is the closest Q-learning-specific invalid-action precedent; our work studies statistically unsupported actions in a medical benchmark and compares support penalties, pessimism, and masks under exact V\*.
- BibTeX:

```bibtex
@inproceedings{seurin2020forbidden,
  author       = {Seurin, Mathieu and Preux, Philippe and Pietquin, Olivier},
  title        = {``{I'm} sorry {D}ave, {I'm} afraid {I} can't do that'' {D}eep {Q}-Learning from Forbidden Actions},
  booktitle    = {2020 International Joint Conference on Neural Networks ({IJCNN})},
  year         = {2020},
  publisher    = {IEEE},
  eprint       = {1910.02078},
  archivePrefix = {arXiv}
}
```

---

## B. Dead-Ends and Expert / Healthcare RL Context

### [fatemi2021deadends] Fatemi et al., NeurIPS 2021

- Verified: ✅ Peer-reviewed. NeurIPS 2021, Advances in Neural Information Processing Systems 34.
- Contribution (1 sentence): Introduces "medical dead-ends" as ICU states from which death is unavoidable under all future treatments, and learns neural models for state construction, dead-end discovery, and confirmation from clinical data.
- Why we cite / our difference (1 sentence): Fatemi et al. estimate dead-ends from data; ICU-Sepsis provides a known tabular model, so we can compute V\*(s) exactly and define benchmark-internal dead-end states without learning a detector.
- BibTeX:

```bibtex
@inproceedings{fatemi2021deadends,
  author       = {Fatemi, Mehdi and Killian, Taylor W. and Subramanian, Jayakumar and Ghassemi, Marzyeh},
  title        = {Medical Dead-ends and Learning to Identify High-Risk States and Treatments},
  booktitle    = {Advances in Neural Information Processing Systems},
  volume       = {34},
  year         = {2021},
  url          = {https://papers.nips.cc/paper_files/paper/2021/hash/26405399c51ad7b13b504e74eb7c696c-Abstract.html}
}
```

### [komorowski2018aiclinician] Komorowski et al., Nature Medicine 2018

- Verified: ✅ Peer-reviewed. *Nature Medicine* 24(11):1716-1720.
- Contribution (1 sentence): Introduces the AI Clinician, a model-based RL approach for sepsis treatment using discrete clinical state clusters and fluid / vasopressor actions from MIMIC-III and eICU data.
- Why we cite / our difference (1 sentence): ICU-Sepsis builds on this sepsis-RL lineage, but we avoid clinical policy claims and use the benchmark to study algorithmic support handling.
- BibTeX:

```bibtex
@article{komorowski2018aiclinician,
  author       = {Komorowski, Matthieu and Celi, Leo A. and Badawi, Omar and Gordon, Anthony C. and Faisal, A. Aldo},
  title        = {The Artificial Intelligence Clinician learns optimal treatment strategies for sepsis in intensive care},
  journal      = {Nature Medicine},
  volume       = {24},
  number       = {11},
  pages        = {1716--1720},
  year         = {2018},
  doi          = {10.1038/s41591-018-0213-5}
}
```

### [raghu2017continuous] Raghu et al., MLHC 2017

- Verified: ✅ Peer-reviewed. PMLR volume 68, pages 147-163.
- Contribution (1 sentence): Applies continuous-state deep RL / Dueling DDQN-style methods to sepsis treatment using learned patient representations.
- Why we cite / our difference (1 sentence): This anchors deep sepsis RL as prior work; we intentionally use a tabular benchmark to enable exact V\* and fine-grained support diagnostics.
- BibTeX:

```bibtex
@inproceedings{raghu2017continuous,
  author       = {Raghu, Aniruddh and Komorowski, Matthieu and Celi, Leo Anthony and Szolovits, Peter and Ghassemi, Marzyeh},
  title        = {Continuous State-Space Models for Optimal Sepsis Treatment: A Deep Reinforcement Learning Approach},
  booktitle    = {Proceedings of the 2nd Machine Learning for Healthcare Conference},
  series       = {Proceedings of Machine Learning Research},
  volume       = {68},
  pages        = {147--163},
  year         = {2017},
  publisher    = {PMLR},
  url          = {https://proceedings.mlr.press/v68/raghu17a.html}
}
```

### [gottesman2019guidelines] Gottesman et al., Nature Medicine 2019

- Verified: ✅ Peer-reviewed. *Nature Medicine* 25(1):16-18.
- Contribution (1 sentence): Gives practical guidelines for RL in healthcare, emphasizing careful evaluation, off-policy pitfalls, and risk-conscious interpretation.
- Why we cite / our difference (1 sentence): We cite it to justify non-clinical framing and multi-metric evaluation; our exact model setting reduces the OPE uncertainty that motivates many of these cautions.
- BibTeX:

```bibtex
@article{gottesman2019guidelines,
  author       = {Gottesman, Omer and Johansson, Fredrik and Komorowski, Matthieu and Faisal, Aldo and Sontag, David and Doshi-Velez, Finale and Celi, Leo Anthony},
  title        = {Guidelines for reinforcement learning in healthcare},
  journal      = {Nature Medicine},
  volume       = {25},
  number       = {1},
  pages        = {16--18},
  year         = {2019},
  doi          = {10.1038/s41591-018-0310-5}
}
```

### [gottesman2018evaluating] Gottesman et al., arXiv 2018

- Verified: [未驗證: arXiv-only / preprint]. Listed by DBLP as CoRR abs/1805.12298, "Informal or Other Publication"; Nature Medicine 2019 cites it as a preprint.
- Contribution (1 sentence): Discusses why evaluating RL policies from observational healthcare data can be misleading because of representation, confounding, and off-policy-estimator variance issues.
- Why we cite / our difference (1 sentence): This strengthens our argument that survival-rate-only and OPE-style evaluation are inadequate; ICU-Sepsis gives exact Vπ and V\* for benchmark-internal evaluation.
- BibTeX:

```bibtex
@misc{gottesman2018evaluating,
  author       = {Gottesman, Omer and Johansson, Fredrik D. and Meier, Joshua and Dent, Jack and Lee, Donghun and Srinivasan, Srivatsan and Zhang, Linying and Ding, Yi and Wihl, David and Peng, Xuefeng and Yao, Jiayu and Lage, Isaac and Mosch, Christopher and Lehman, Li-wei H. and Komorowski, Matthieu and Faisal, Aldo and Celi, Leo Anthony and Sontag, David and Doshi-Velez, Finale},
  title        = {Evaluating Reinforcement Learning Algorithms in Observational Health Settings},
  year         = {2018},
  howpublished = {arXiv preprint arXiv:1805.12298},
  eprint       = {1805.12298},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  url          = {https://arxiv.org/abs/1805.12298}
}
```

### [hester2018dqfd] Hester et al., AAAI 2018

- Verified: ✅ Peer-reviewed. AAAI 2018, Proceedings of the AAAI Conference on Artificial Intelligence 32(1); DOI 10.1609/aaai.v32i1.11757.
- Contribution (1 sentence): Proposes Deep Q-learning from Demonstrations (DQfD), combining TD updates with supervised demonstration losses to improve early learning from demonstrations.
- Why we cite / our difference (1 sentence): DQfD supports expert-guided RL motivation; our expert-prior variant is much lighter and highlights that raw clinician priors may include unsupported actions.
- BibTeX:

```bibtex
@inproceedings{hester2018dqfd,
  author       = {Hester, Todd and Vecerik, Matej and Pietquin, Olivier and Lanctot, Marc and Schaul, Tom and Piot, Bilal and Horgan, Dan and Quan, John and Sendonaris, Andrew and Osband, Ian and Dulac-Arnold, Gabriel and Agapiou, John and Leibo, Joel Z. and Gruslys, Audrunas},
  title        = {Deep {Q}-Learning from Demonstrations},
  booktitle    = {Proceedings of the Thirty-Second {AAAI} Conference on Artificial Intelligence},
  pages        = {3223--3230},
  year         = {2018},
  doi          = {10.1609/aaai.v32i1.11757},
  url          = {https://ojs.aaai.org/index.php/AAAI/article/view/11757}
}
```

---

## C. Add-On / Defense Citations

### [tang2022factored] Tang et al., NeurIPS 2022

- Verified: ✅ Peer-reviewed. NeurIPS 2022, Advances in Neural Information Processing Systems 35, Main Conference Track.
- Contribution (1 sentence): Shows that exploiting factored action spaces in offline RL can improve sample efficiency and inference over underexplored action combinations in healthcare-motivated settings.
- Why we cite / our difference (1 sentence): ICU-Sepsis actions are naturally factored as fluid × vasopressor; if we include factored Q-learning, this is the main supporting citation.
- BibTeX:

```bibtex
@inproceedings{tang2022factored,
  author       = {Tang, Shengpu and Makar, Maggie and Sjoding, Michael and Doshi-Velez, Finale and Wiens, Jenna},
  title        = {Leveraging Factored Action Spaces for Efficient Offline Reinforcement Learning in Healthcare},
  booktitle    = {Advances in Neural Information Processing Systems},
  volume       = {35},
  year         = {2022},
  url          = {https://proceedings.neurips.cc/paper_files/paper/2022/hash/dda7f9378a210c25e470e19304cce85d-Abstract-Conference.html}
}
```

### [ng1999reward] Ng et al., ICML 1999

- Verified: ✅ Peer-reviewed. ICML 1999, pages 278-287.
- Contribution (1 sentence): Proves that potential-based reward shaping preserves optimal policies under transformations of the form γΦ(s') - Φ(s).
- Why we cite / our difference (1 sentence): Only needed if SOFA-based shaping is included; it lets us frame severity shaping as algorithmic sample-efficiency shaping rather than changing the clinical objective.
- BibTeX:

```bibtex
@inproceedings{ng1999reward,
  author       = {Ng, Andrew Y. and Harada, Daishi and Russell, Stuart J.},
  title        = {Policy Invariance under Reward Transformations: {T}heory and Application to Reward Shaping},
  booktitle    = {Proceedings of the Sixteenth International Conference on Machine Learning},
  pages        = {278--287},
  year         = {1999},
  publisher    = {Morgan Kaufmann}
}
```

### [springer2025offlinesafe] Tu et al., Human-Centric Intelligent Systems 2025

- Verified: ✅ Peer-reviewed journal. Springer *Human-Centric Intelligent Systems* 5(1):63-76; DOI 10.1007/s44230-025-00093-7.
- Contribution (1 sentence): Studies offline safe RL for sepsis with variable-length episodes and sparse rewards.
- Why we cite / our difference (1 sentence): This supports that safe/offline sepsis RL is active, but our work is narrower and cleaner: benchmark-internal support handling with exact V\* rather than full clinical safety claims.
- BibTeX:

```bibtex
@article{springer2025offlinesafe,
  author       = {Tu, Rui and Luo, Zhipeng and Pan, Chuanliang and Wang, Zhong and Su, Jie and Zhang, Yu and Wang, Yifan},
  title        = {Offline Safe Reinforcement Learning for Sepsis Treatment: {T}ackling Variable-Length Episodes with Sparse Rewards},
  journal      = {Human-Centric Intelligent Systems},
  volume       = {5},
  number       = {1},
  pages        = {63--76},
  year         = {2025},
  doi          = {10.1007/s44230-025-00093-7}
}
```

### [cpqiql_safe_offline_sepsis] Zhang and Mi, Transactions on Artificial Intelligence 2026

- Verified: ✅ with caveat. Appears as peer-reviewed article in *Transactions on Artificial Intelligence* 2(1):103-118, Scilight Press; DOI 10.53941/tai.2026.100007. Venue is new / lower visibility, so do not use as load-bearing prior art.
- Contribution (1 sentence): Proposes a safe offline RL method for sepsis and reports evaluation on ICU-Sepsis.
- Why we cite / our difference (1 sentence): This is a nearby ICU-Sepsis usage, but it proposes a safety-filtered offline RL algorithm rather than diagnosing ICU-Sepsis's default inadmissible-action handling.
- BibTeX:

```bibtex
@article{cpqiql_safe_offline_sepsis,
  author       = {Zhang, Bailing and Mi, Yuwei},
  title        = {Safe Offline Reinforcement Learning for Sepsis Treatment},
  journal      = {Transactions on Artificial Intelligence},
  volume       = {2},
  number       = {1},
  pages        = {103--118},
  year         = {2026},
  doi          = {10.53941/tai.2026.100007}
}
```

---

## Positioning Paragraph

Prior sepsis RL work has largely focused on learning treatment policies from observational clinical data, beginning with AI Clinician-style tabular abstractions and later continuous-state deep RL models. ICU-Sepsis was introduced to make this line of work reproducible by providing a lightweight tabular benchmark with known dynamics and exact value computation. Offline RL methods such as BCQ, BEAR, CQL, and pessimistic value iteration show that low-support or out-of-distribution actions can corrupt Q-learning through extrapolation and bootstrapping error; however, these methods are usually evaluated where true policy value is unavailable. Our work uses ICU-Sepsis as a controlled medical-RL testbed where the support partition is explicit and V\* is exactly computable, allowing us to diagnose how `mean` imputation hides unsupported-action behavior and to compare support-aware remedies under exact benchmark-internal metrics.

---

## Explicit Questions from `10_codex_research_tasks.md`

### Q1. Novelty defense: has prior offline RL work already done this exact study?

I did **not** find a prior work that explicitly studies "mean-imputation hiding OOD / unsupported actions" on a known-dynamics tabular medical benchmark while comparing penalty / pessimism / mask remedies under exact V\*. The closest prior art is:

- BCQ / BEAR / CQL / PEVI: general offline RL methods for extrapolation error, bootstrapping error, and pessimism.
- Huang & Ontanon and Seurin et al.: invalid / forbidden action masking in games or generic Q-learning settings.
- ICU-Sepsis original paper: builds the benchmark and reports standard algorithm baselines, but does not frame `mean` handling as an OOD-action failure mode or compare the remedy spectrum.
- CPQ-IQL / offline safe sepsis work: nearby medical RL safety work, but not this benchmark-internal mean-imputation diagnosis.

Recommended claim wording:

> To our knowledge, this is the first benchmark-internal study of ICU-Sepsis that reframes inadmissible actions as an offline-RL support problem and compares support penalties, pessimistic/conservative updates, behavior constraints, and hard masking using exact V\*.

### Q2. Dead-end novelty defense: has prior work used known dynamics to compute exact medical dead-ends?

I found no medical-RL paper that uses a known-dynamics tabular sepsis benchmark to compute exact dead-ends directly from V\*. Fatemi et al. (NeurIPS 2021) is the closest and strongest precedent: it defines medical dead-ends and learns / estimates dead-end discovery and confirmation models from clinical data. General planning / MDP literature studies dead ends when models are known, but that is not the same as a medical RL benchmark analysis.

Recommended claim wording:

> Unlike prior medical dead-end work, which estimates high-risk states from observational data, ICU-Sepsis permits an exact benchmark-internal dead-end analysis because γ=1 and reward is a survival indicator, so V\*(s) is the maximum survival probability under the model.

---

## Precise positioning vs the ICU-Sepsis paper (source + paper fact-check, 2026-05-22)

Verified directly against the shipped package source and the arXiv HTML
(`arXiv:2406.05646v1`). Use these exact points when writing Method / Related Work
so we cannot be accused of misreading the benchmark.

- **Mean imputation is real, documented, and the default.** §4.3 defines the
  inadmissible-action transition as `1/|A(s)| Σ_{a'∈A(s)} ζ(s,a',s')` (the
  unweighted mean of admissible transitions). Confirmed in code
  (`envs/sepsis.py::_take_action`, default `MEAN`) and empirically (all 713
  non-terminal states: inadmissible row == admissible mean to 7e-16;
  `metadata.json: action_map_method = "uniform_unweighted"`, `threshold = 20`).
- **The authors frame it as benign**, not as a failure: "equivalent to choosing
  one of the admissible actions at random." → We must engage this directly; see
  `reviewer_anticipated_questions.md` Q17. Our line: that equivalence is exactly
  the *cost* (random-admissible < best-admissible) and is a closed-world artifact.
- **Metrics they report:** average return (= survival prob), average episode
  length, convergence episodes/steps, post-convergence return. **No
  distance-to-V\*, no inadmissible-selection rate.** → our exact-V* metrics are
  genuinely additive and are what make the hidden cost visible.
- **They do NOT** compare inadmissible-action strategies (mean/terminate/raise)
  and do NOT study action masking on/off. → those comparisons are ours.
- **Closest existing experiment — Appendix B.3 (action-removal perturbation).**
  Randomly makes admissible actions inadmissible w.p. σ (32 runs/policy), measures
  *return* robustness; concludes τ=20 ICU-Sepsis is robust whereas the τ=5 variant
  exploited rare actions. This is adjacent (over-reliance on under-supported
  actions) but (a) measures return robustness, which is insensitive to our
  phenomenon by construction (inadmissible = average ⇒ return is stable), and
  (b) does not study selection rate, distance-to-V*, mechanism, or remedies.
  **Cite B.3 and differentiate; do not ignore it.**

---

## Unverified / Caveat List

- `gottesman2018evaluating`: arXiv / CoRR preprint; useful and widely cited, but not a peer-reviewed venue.
- `cpqiql_safe_offline_sepsis`: peer-reviewed according to the journal page and DOI metadata, but the journal is young and lower visibility; cite only as nearby recent work, not as a cornerstone.
- `mimic_sepsis_arxiv2510_24500` from previous notes remains arXiv-only as of the last check; not central to this paper.

