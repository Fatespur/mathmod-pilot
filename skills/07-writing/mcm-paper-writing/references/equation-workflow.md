# Word-native equation compatibility contract

CANONICAL_SOURCE = MARKDOWN
FORMULA_AUTHORING = WORD_NATIVE_COMPATIBLE_LATEX
DOCX_FORMULA_TARGET = OMML
MANUAL_MATHTYPE_CONVERSION = NOT_REQUIRED

Final formal text is `PAPER_FINAL.md`; `paper.md` remains the pipeline working
artifact. At handoff copy verified content and record both hashes/path aliases;
do not break existing manifest consumers. DOCX/PDF are derived exports only.
Keep standard LaTeX source, readable Git diffs and no Word XML in Markdown.

Use Pandoc math: inline `$E=mc^2$` (no delimiter-adjacent spaces), display `$$`
on separate lines. Prefer \frac, \sqrt, \sum, \prod, \int, \sin, \cos, \exp,
\ln, \log, \min, \max, \left, \right, aligned, cases, standard matrices,
\mathbf, \boldsymbol, \mathrm, \operatorname, Greek letters, relations,
subscripts and superscripts. Validate braces, paired delimiters and environments.
These are preferred candidates, not a promise that every converter/version
supports every construction. Unknown macros require a real conversion test.

Avoid custom macros/\newcommand, packages, TikZ, raw TeX primitives, unsupported
environments, presentation-only macros and manual spacing hacks. Never embed
raw `<m:oMath>` XML or replace standard formulas with images/SVG/screenshots,
plain text or OLE objects. A truly graphical mathematical object needs a documented
exception and semantic review; a normal fraction is never such an exception.

Run `scripts/formula_compatibility_validator.py PAPER_FINAL.md` and the integrated
Markdown validator. Static lint cannot prove conversion or detect unlabeled formula
images: visually inspect all figures. Review FORMULA_SYNTAX_VALID,
PANDOC_MATH_COMPATIBLE, UNSUPPORTED_LATEX_MACROS, RAW_OMML_IN_MARKDOWN and
FORMULA_AS_IMAGE (CRITICAL unless a justified graphical exception).

## Export and smoke test

Use an actually installed Pandoc-compatible converter, e.g.
`pandoc fixture.md --from=markdown+tex_math_dollars --to=docx -o fixture.docx`.
Do not use the legacy plain-text Word generator for mathematical papers.
If no native converter exists, report WORD_NATIVE_EXPORT_PIPELINE = NOT_PRESENT
and WORD_NATIVE_EQUATION_SMOKE_TEST = NOT_AVAILABLE. Keep Markdown plus lint;
do not require a manual conversion workflow or claim native editability.

Use the synthetic fixture in `assets/word-native-smoke.md`: inline math, fraction,
root, scripts, sum, integral, aligned, cases, matrix, Greek, operatorname and nested
delimiters. Inspect DOCX ZIP XML for m:oMath and real m:f, m:rad, script, nary,
matrix and equation-array structures; no formula images/OLE/plain-text fallbacks.
Record converter version, command, exit/stderr and source/output SHA256.
In Word verify Equation Editor entry, editable numerator/denominator/scripts,
matrix cells and aligned/cases layout; record WORD_UI_EDITABILITY separately.
Only claim WORD_NATIVE_EQUATION = PASS when applicable checks actually ran;
XML proof alone is structural evidence, not proof of a Word interaction.

Test `\tag{1}` separately through the exact conversion chain, checking number
retention and native structure. If unstable or untested, defer numbering to the
pipeline's verified numbering mechanism or formatting stage. Never silently drop
references or preserve tags as noneditable objects. NATIVE_EDITABILITY >
MANUAL_VISUAL_HACK. Do not stretch equations to satisfy page budgets.
