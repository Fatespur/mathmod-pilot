# CUMCM Submission, Anonymity, and Visual Validation

## Contents

- Output set
- Structural and page checks
- Style, equation, figure, table, and citation checks
- Anonymity checks
- AI disclosure checks
- File and supporting-material checks
- PDF visual review
- Report schema

## Output set

Generate only applicable artifacts:

- `paper_print.docx`
- `paper_submission.docx`
- `paper_submission.pdf`
- `equations.tex`
- `equation_mapping.json`
- `supporting_materials.zip` or `.rar`
- `AI工具使用详情.pdf` only when AI was used
- `formatting_report.md`
- `validation_report.json`
- exact Word-generation and format-validation scripts

If an artifact is inapplicable or blocked, explain why in the reports. Do not create a fake placeholder.

## Structural and page checks

Check:

- A4 geometry and no Letter sections;
- every margin at least 2.5 cm;
- correct portrait/landscape sections and restoration after wide tables;
- no abnormal blank pages;
- print order: commitment, numbering, abstract, body, references, appendix;
- no paper page number on the first two print pages;
- electronic paper excludes the first two official pages and starts with the abstract;
- no table of contents;
- abstract occupies exactly one page;
- Arabic page number 1 starts on the abstract, centered in the footer, then remains continuous;
- body start through reference end is at most 30 pages under the conservative rule;
- appendix begins after the counted range and contains complete code and the supporting-material list.

When an automatic tool cannot confirm a page-number field or section boundary, mark it `WARNING` and verify in Microsoft Word; do not infer a `PASS` from extracted text alone.

## Style and content checks

Audit every required named style for East Asian/Latin font, size, bold, alignment, line-spacing rule/value, before/after spacing, first/hanging/left/right indents, and pagination controls.

Specifically confirm:

- body and abstract: multiple 1.15;
- headings, formula blocks, tables, captions, references, and code: single automatic spacing;
- no fixed spacing that clips formulas;
- no undefined default paragraph spacing;
- real multilevel heading numbering with no gaps/duplicates;
- no fake lists or indentation made from spaces/tabs;
- images preserve aspect ratio, body width, caption pairing, numbering, citation, and adequate effective resolution;
- tables use native Word geometry, repeat headers when needed, stay within width, and have continuous cited numbering;
- references are bidirectionally cited, sequential, real, and free of placeholder DOI/metadata;
- external data and figure/table sources are identified.

Equation checks are defined in [equation-workflow.md](equation-workflow.md).

## Anonymity checks

Scan:

- DOCX body, headers, footers, footnotes/endnotes, comments, revisions, hidden text, core/custom properties, embedded filenames, and relationships;
- filenames, directory names, code, logs, configuration, absolute paths, Git identity strings, and supporting-material inventory;
- PDF metadata and extractable text;
- visible text and watermarks in images (OCR or manual visual review when available).

Ask the user/team for known participant, advisor, student-number, school, college, laboratory, regional, email, and phone terms. Also detect Windows/macOS/Linux home paths and common contact patterns.

Classify every finding as:

- `participant_identity` — blocking;
- `reference_author` — allowed when it belongs to a real citation;
- `problem_institution` — allowed when supplied by the problem;
- `data_source_institution` — allowed with provenance;
- `public_dataset` — allowed;
- `uncertain` — requires manual classification.

Never mass-delete names. Strip Word/PDF author and last-editor metadata, comments, and revision identities only after preserving any review information the user still needs in a separate working copy.

## AI disclosure checks

Use one explicit state:

- `used`
- `not_used_confirmed`
- `unknown`

`unknown` cannot pass. `not_used_confirmed` requires explicit team confirmation before inserting the fixed non-use statement. `used` requires the applicable body/reference disclosure and an AI-use detail artifact containing tool/version, developer, dates, purpose/stage, key interactions, adoption, human modifications, and impact. Include Codex formatting/validation use.

## File and supporting-material checks

- Open and parse every DOCX/PDF/ZIP artifact.
- Keep each electronic paper and supporting archive at or below 20 MB.
- Require ZIP or RAR for supporting materials; do not compress the paper itself.
- Compare archive inventory with the appendix list.
- Exclude official front matter and identity information from supporting materials.
- Run the programs or their applicable tests; a file's presence is not proof of runnability.
- Preserve independently sourced data and long intermediate/model-supporting files; do not duplicate problem-provided raw data unnecessarily.

## PDF visual review

DOCX XML inspection never replaces visual review.

1. Export `paper_submission.docx` to PDF.
2. Render every PDF page to PNG with `scripts/render_pdf_pages.py` or the installed PDF/document renderer.
3. Inspect every page at 100%, not a sample.
4. Check title stranding, heading/body separation, image/caption and table-title/table separation, formula clipping/number alignment, unconverted LaTeX, overflow, abnormal whitespace, blank pages, table/code width, footer obstruction, font substitution, Chinese corruption, and blurry figures.
5. Repair the DOCX and regenerate all dependent outputs.
6. Repeat export, rendering, and full-page inspection.

Complete at least two generation-export-render-review cycles. Record each cycle, reviewed page count, defects, fixes, reviewer, and timestamp. If LibreOffice/Word/native-equation is unavailable, record that the gate did not run and do not claim final compliance.

## Report schema

`validation_report.json` must contain machine-readable checks with:

- `id`
- `category`
- `status`: `PASS`, `WARNING`, `FAIL`, or `NOT APPLICABLE`
- `message_zh`
- `evidence`
- `rule_class`
- `rule_source`
- `automatic`
- `manual_action`

`formatting_report.md` must summarize at least:

1. official baseline/version and supplied supplemental rules;
2. precedence and conflict decisions;
3. page geometry and margins;
4. fonts and substitutions;
5. line spacing for every required style;
6. abstract, body-to-reference, appendix, and total page counts;
7. PDF and supporting-material sizes;
8. image resolution findings;
9. figure/table numbering and citations;
10. equation count, numbers, native OMML status, and unconverted LaTeX count;
11. citation consistency;
12. anonymity findings;
13. AI disclosure state;
14. supporting-material consistency and code-run status;
15. automatic fixes;
16. remaining manual Word/native-equation checks;
17. both visual-review cycles.

Do not report a `PASS` for any test that was skipped, inferred, or performed against an obsolete artifact.
