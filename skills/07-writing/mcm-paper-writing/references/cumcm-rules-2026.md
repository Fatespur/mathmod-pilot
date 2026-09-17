# CUMCM 2026 Baseline Rule Registry

## Contents

- Scope and provenance
- Rule precedence
- OFFICIAL-MANDATORY rules
- CONSERVATIVE-SAFETY rules
- RECOMMENDED-DEFAULT rules
- Conflict handling

## Scope and provenance

Use this file only as the bundled “全国大学生数学建模竞赛论文格式规范（2026年修订稿）” baseline described by the skill update request. It is not proof that a current rule was checked online. When the user supplies a national, regional, school, template, or submission-system file, read it and record its filename, date, issuer, checksum, and applicable clauses in the rule manifest.

Each applied rule must have:

- `rule_id`
- `classification`: `OFFICIAL-MANDATORY`, `CONSERVATIVE-SAFETY`, or `RECOMMENDED-DEFAULT`
- `source`
- `source_date`
- `value`
- `scope`
- `conflicts`
- `decision`
- `reason`

## Rule precedence

1. Official files, regional notices, or school notices supplied for this task.
2. The current national official rules actually read and verified.
3. `CONSERVATIVE-SAFETY` rules below.
4. `RECOMMENDED-DEFAULT` rules below.
5. Microsoft Word defaults.

If a regional or school instruction conflicts with a national hard requirement, do not choose silently. Identify both clauses, normally preserve the national hard requirement, and record the decision and reason in `formatting_report.md`.

## OFFICIAL-MANDATORY rules

### O-01 Paper and margins

- Use white A4 paper; one-sided or two-sided printing is allowed.
- Every margin must be at least 2.5 cm.
- Bind the printed paper on the left.
- A default of exactly 2.5 cm is one conforming implementation, not the only allowed value.

### O-02 Printed-paper order

Use this order:

1. commitment page;
2. numbering page;
3. abstract page;
4. body beginning on the fourth physical page;
5. references;
6. appendix.

The commitment and numbering pages display no paper page number. Prefer the authentic current official DOCX/PDF pages. Do not programmatically imitate them, redraw them from screenshots, change fixed text/borders/fields/instructions, or fill anything other than officially permitted fields.

### O-03 Abstract page

- Include the paper title, Chinese abstract, and keywords.
- Do not generate an English abstract.
- The abstract should not exceed one page.
- Start Arabic page numbering at 1 on the abstract page, centered in the footer, and continue it afterward.
- Do not include school, participant, advisor, college, or regional identity information.

### O-04 Body, references, and appendix

- Do not create a Word TOC field, a manual TOC, a “目录” heading, or a page-number list.
- The body is limited to 30 pages under the applicable official wording.
- Place the appendix after the body; appendix pages are unlimited.
- Print and bind the appendix with the printed paper.

### O-05 Appendix and programs

Include:

- a supporting-material file list;
- every complete runnable source program used for modeling;
- Excel, SPSS, or comparable interaction commands;
- necessary supplementary explanations.

The code must match the model, results, and figures and must include preprocessing, training, solving, output, and plotting steps. Do not substitute pseudocode, omit key functions, or write “代码过长，略”. If no program was used, use exactly:

> 本论文没有用到程序

Do not paraphrase this fixed statement.

### O-06 Anonymity

Do not expose participant identity in the abstract, body, post-reference statements, appendix, code, images, tables, supporting materials, filenames, local paths, Word/PDF properties, comments, or revision history.

Scan at least participant/advisor names, student numbers, school/college/laboratory names and abbreviations, school English names, region, email, phone, local usernames, Windows/macOS/Linux home paths, Git identity, image watermarks, document author/last editor/comment author, and revision authors.

Classify findings. Preserve legitimate reference authors, institutions quoted by the problem, data-source institutions, and public dataset names. Do not indiscriminately delete names from references.

### O-07 Citations

- Mark every use of public or web material in the body and list it in the references.
- Do not copy long passages or fabricate sources, authors, journals, metadata, or DOI values.
- Verify body-to-list and list-to-body correspondence, continuous numbering, figure/table data sources, external data provenance, and required AI-tool citations.

### O-08 Electronic paper

- Keep body, references, and appendix consistent with the printed paper.
- Exclude the commitment and numbering pages.
- Make the first page the abstract page.
- Submit one independent Word or PDF file; prefer PDF when allowed.
- Keep each electronic paper file at or below 20 MB.
- Do not compress the electronic paper file itself.

Generate at least `paper_submission.docx` and `paper_submission.pdf`. Generate `paper_print.docx` only when authentic official front matter is available to preserve.

### O-09 Supporting materials

Include all runnable source programs, independently sourced data, long intermediate results, model-supporting files, and the AI-use detail file when AI was used. The original problem-provided data need not be duplicated.

Package supporting materials as one ZIP or RAR file at or below 20 MB. Keep its file list consistent with the appendix; exclude commitment/numbering pages and identity information. If no supporting materials exist, use exactly:

> 本论文没有支撑材料

Do not paraphrase this fixed statement.

### O-10 AI use

AI tools include language/generative models, code assistants, Codex, intelligent mathematical software, and other tools that generate text, code, models, or analysis.

Only after the team explicitly confirms no AI was used during the competition may the paper state:

> 本参赛队未使用任何AI工具

Never create that statement automatically. When AI was used, record the tool name and version/model, developer, dates, tasks/stages, key interactions, adoption decision, human modifications, and whether it affected modeling, code, paper text, or only document operations. Include the required body/reference disclosure and `AI工具使用详情.pdf` in supporting materials when the applicable rules require it. Codex used only for Word styles, LaTeX cleanup, equation numbering, document scripts, validation, PDF rendering, or anonymity scanning still counts as actual AI use and must not be hidden.

## CONSERVATIVE-SAFETY rules

### C-01 Thirty-page boundary

Because the treatment of reference pages can be ambiguous, count from the first body page through the last reference page and keep that range at or below 30 pages; start the appendix on the next page. Do not claim the national committee explicitly said references are included. Put this sentence in the report:

> 为避免正文页数边界产生争议，本文件按照正文起始页至参考文献末页不超过30页的保守规则执行。

### C-02 Abstract length

Treat “原则上不超过一页” as a strict one-page generation gate. If it overflows, remove background filler and repeated method prose first; preserve each subproblem's core model, algorithm, main numerical result, validation, and robustness evidence. Do not shrink margins below 2.5 cm, use unreadable fonts/line spacing, stack text boxes, convert the abstract to an image, or delete key methods/results as the first remedy.

### C-03 Official template priority

Search the work directory for commitment, numbering, abstract, regional/school templates, and official format files. Reuse them before any blank-document generator. Copy rather than overwrite. Preserve page geometry, sections, official headers/footers, fixed text, and fixed pages. Do not propagate body styles into official fixed pages.

### C-04 Supplemental rules

Before every build, ask whether the user supplied national, regional, school, abstract, commitment, numbering, or submission-system files. Apply their specific non-conflicting clauses before skill defaults and record all changes.

### C-05 Unknown verification state

Use `WARNING` or `FAIL`, never `PASS`, when a current official file, official template, native OMML conversion, AI disclosure, code run, PDF export, or page inspection was not actually available or performed.

## RECOMMENDED-DEFAULT rules

The following are professional defaults, not national hard requirements:

- Chinese font choices, Times New Roman for Latin text, exact title/body sizes, and all style spacing.
- 1.15 multiple line spacing for body and abstract.
- Three-line tables.
- GB/T 7714 sequential citation formatting.
- Image effective resolution targets and maximum image width.
- Equation font and vector/matrix typography.
- Paragraph before/after spacing.

Default page implementation:

- A4 portrait, single column;
- margins 2.5 cm on all sides, gutter 0 cm;
- header and footer distance 1.5 cm;
- no header, watermark, decorative border, or colored page background;
- black body text and centered footer page number.

Use a separate landscape section only for a genuinely wide table. Insert a section break before it, restore portrait afterward, continue page numbering, preserve all other margins, and avoid blank pages.

See [word-format-system.md](word-format-system.md) for all exact styles, line spacing, figures, tables, and references. See [equation-workflow.md](equation-workflow.md) for formulas. See [submission-validation.md](submission-validation.md) for automated and visual gates.

## Conflict handling

For every conflict, report:

1. the two source clauses;
2. their classifications and scopes;
3. whether either is a national hard requirement;
4. the selected rule;
5. the reason;
6. any residual submission risk;
7. the manual action needed, if any.
