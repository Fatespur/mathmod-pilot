# Acknowledgements & Credits

MathMod-Pilot is an open-source project that builds upon and integrates work from
multiple sources. This file provides transparent attribution for every skill
shipped in the library, in accordance with their respective licenses.

## Skill Attribution Table

| # | Skill | Directory | Original Source / Author | License | Modification Notes |
|---|-------|-----------|--------------------------|---------|--------------------|
| 1 | brainstorming | `brainstorming/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 2 | problem-analyzer | `problem-analyzer/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 3 | data-processing | `data-processing/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 4 | mle-solver | `mle-solver/` | MathMod-Pilot Project (original work) | MIT | **Original Python implementation.** The Generate-Verify-Revise iterative architecture, `extensions/heuristic_algorithms.py` (GA/PSO/SA/DE), and the three-layer assertion-checking mechanism are all independent original developments based on national-level mathematical modelling competition experience. |
| 5 | model-validation | `model-validation/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 6 | scipilot-figure | `scipilot-figure/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 7 | **scipilot-figure-skill** | `scipilot-figure-skill/` | **Haojae** — [scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill) | **MIT** (Copyright (c) 2026 Haojae) | Third-party skill. The `scripts/` directory ships the original unmodified Python modules. A `skill.py` wrapper and attribution headers were added. |
| 8 | mcm-paper-writing | `mcm-paper-writing/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 9 | paper-review | `paper-review/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 10 | diagram-generator | `diagram-generator/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 11 | matlab-figure | `matlab-figure/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 12 | nature-figure | `nature-figure/` | MathMod-Pilot Project (references [figures4papers](https://github.com/ChenLiu-1996/figures4papers) by Chen Liu, Yale) | MIT | Original `skill.py`, `nature_figure_backend.py` and `generate_openrouter_schematic.py`. The `assets/figures4papers/` directory contains **original demo scripts from the upstream repo** for pattern-level reference. **Upstream has no explicit license** — redistribute at your own risk or seek author permission. |
| 13 | winning-paper-analysis | `winning-paper-analysis/` | MathMod-Pilot Project (references [Math_Model](https://github.com/personqianduixue/Math_Model) by personqianduixue) | MIT | Original `skill.py` and `SKILL.md`. The prompt cites the Math_Model repository (6.3k+ stars) as a **data source** for award-winning CUMCM/MCM papers. **No code from the upstream repo is included.** Upstream has no explicit license. |
| 14 | reference-manager | `reference-manager/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |
| 15 | systematic-debugging | `systematic-debugging/` | MathMod-Pilot Project (native Trae skill) | MIT | Original work, unmodified prompt |

## Third-Party Dependencies

MathMod-Pilot skills rely on the following open-source Python libraries at runtime
(declared as optional extras in `pyproject.toml`):

| Library | License | Used By |
|---------|---------|---------|
| NumPy | BSD-3-Clause | mle-solver, model-validation |
| SciPy | BSD-3-Clause | mle-solver, model-validation |
| scikit-learn | BSD-3-Clause | model-validation |
| matplotlib | PSF-based | scipilot-figure-skill, scipilot-figure, nature-figure, diagram-generator |
| seaborn | BSD-3-Clause | scipilot-figure-skill |
| plotly | MIT | scipilot-figure-skill |
| pandas | BSD-3-Clause | data-processing, scipilot-figure-skill |
| Pillow | HPND | scipilot-figure-skill |
| SALib | MIT | model-validation |
| statsmodels | BSD-3-Clause | model-validation |
| SciencePlots | MIT | scipilot-figure-skill (optional) |
| PyYAML | MIT | core (SKILL.md front-matter parsing) |
| Requests | Apache-2.0 | nature-figure (OpenRouter API) |

## License

The MathMod-Pilot library is distributed under the **MIT License**. All bundled
third-party skills retain their original copyright notices and license terms.

## Compliance Notes

The following upstream projects were referenced during development but carry
licensing constraints that require attention:

| Upstream Project | License | How It Is Used | Compliance Status |
|------------------|---------|----------------|-------------------|
| [figures4papers](https://github.com/ChenLiu-1996/figures4papers) (Chen Liu) | No explicit license | `assets/figures4papers/` contains original demo scripts for pattern reference. | **Risk** — upstream has no license. Consider removing scripts or obtaining written permission before commercial use. |
| [Math_Model](https://github.com/personqianduixue/Math_Model) (personqianduixue) | No explicit license | Cited as a reference data source in `winning-paper-analysis` SKILL.md. No code included. | Low risk — citation only, no redistribution. |
