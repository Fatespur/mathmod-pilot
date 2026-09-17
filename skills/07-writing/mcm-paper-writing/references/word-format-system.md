# CUMCM Word Format System

## Contents

- Page and section geometry
- Named styles
- Line-spacing policy
- Headings and numbering
- Figures
- Tables
- References and code
- Prohibited layout techniques

All values in this file are `RECOMMENDED-DEFAULT` unless a cited current rule promotes a value. Apply exact values through named Word styles; never describe them as national hard requirements.

## Page and section geometry

- A4: 210 mm × 297 mm, portrait, one column.
- Margins: 2.5 cm on every side; gutter 0 cm.
- Header/footer distance: 1.5 cm.
- Footer page number: centered Arabic number, starting at 1 on the abstract section.
- No header, watermark, decorative border, or background color by default.
- Use a next-page section break before the abstract so its numbering can restart without affecting official front matter.
- Use an isolated landscape section only after width optimization fails; restore portrait in the next section and preserve continuous page numbering.

## Named styles

Create or reuse all of these styles. Explicitly set East Asian font, Latin font, size, bold, alignment, line spacing, before/after spacing, first/left/right indent, widow/orphan control, keep-with-next, and keep-lines-together. Do not modify only `Normal` and rely on inheritance.

| Style | East Asian / Latin | Size | Alignment | Line spacing | Before / after | Indent and pagination |
|---|---|---:|---|---|---|---|
| `PaperTitle` | 黑体 / Times New Roman | 18 pt bold | center | single | 0 / 12 pt | no first indent; keep with next |
| `AbstractHeading` | 黑体 / Times New Roman | 16 pt bold | center | single | 0 / 6 pt | no first indent; keep with next |
| `AbstractBody` | 宋体 / Times New Roman | 12 pt | justified | multiple 1.15 | 0 / 0 | first line 2 chars; widow control |
| `Keywords` | 宋体 / Times New Roman | 12 pt | justified | multiple 1.15 | 6 / 0 | no first indent; bold only the “关键词” label |
| `Heading1` | 黑体 / Times New Roman | 16 pt bold | left | single | 12 / 6 pt | no first indent; keep with next/keep lines/widow |
| `Heading2` | 黑体 / Times New Roman | 14 pt bold | left | single | 8 / 4 pt | same pagination controls |
| `Heading3` | 黑体 / Times New Roman | 12 pt bold | left | single | 6 / 3 pt | same pagination controls |
| `BodyText` | 宋体 / Times New Roman | 12 pt | justified | multiple 1.15 | 0 / 0 | first line 2 chars; zero left/right; widow control |
| `ListText` | 宋体 / Times New Roman | 12 pt | justified | multiple 1.15 | 0 / 0 | real list numbering; hanging indent; no first indent |
| `FigureCaption` | 宋体 / Times New Roman | 10.5 pt | center | single | 3 / 6 pt | no indent; keep with prior figure |
| `TableCaption` | 宋体 / Times New Roman | 10.5 pt | center | single | 6 / 3 pt | no indent; keep with next table |
| `TableText` | 宋体 / Times New Roman | 10.5 pt | deliberate by column | single | 0 / 0 | no first indent; vertical center where appropriate |
| `EquationBlock` | compatible math / Times New Roman | 12 pt | center | single auto | 6 / 6 pt | no indent; keep lines; no fixed height |
| `Reference` | 宋体 / Times New Roman | 10.5 pt | left or justified | single | 0 / 0 | hanging indent 2 chars; keep item together when possible |
| `AppendixHeading` | 黑体 / Times New Roman | 16 pt bold | left | single | 12 / 6 pt | keep with next/keep lines |
| `CodeBlock` | 等线 or compatible CJK monospace / Consolas | 8-9 pt | left | single | 0 / 0 | preserve source indentation; no auto bullets |

Use 9 pt table text only when width optimization still requires it. If a requested font is unavailable, detect installed fonts, select a compatible replacement, and record the mapping in `formatting_report.md`; never substitute silently.

## Line-spacing policy

- Explicitly set every major style; never depend on Word defaults or “add space after paragraph”.
- Do not apply fixed 18/20 pt line spacing to the document. Fixed spacing can clip native equation structures, fractions, integrals, matrices, scripts, and large delimiters.
- Keep inline-equation paragraphs at body 1.15. If a specific native inline equation clips, adjust only that paragraph to multiple 1.2 or single automatic spacing.
- Keep display equations at single automatic spacing with 6 pt before/after. Never reduce formulas to an unreadable size.
- Use single spacing with 0 pt before/after in table cells, references, and code.
- Do not combine paragraph spacing with blank spacer paragraphs.

## Headings and numbering

Use the hierarchy `1`, `1.1`, `1.1.1` through real Word styles and a multilevel list. Do not type a long sequence of manual numbers, align with spaces/tabs, or copy stale numbering. Audit continuity, levels, duplicates, skipped numbers, keep-with-next, and headings stranded at the page bottom.

## Figures

- Insert inline with text, center horizontally, preserve aspect ratio, and keep within the body width.
- Use a default maximum width of 15.5 cm, reducing it when the source aspect ratio or page content requires.
- Place `图1  图题内容` below the figure, center it, keep it with the image, number continuously, and cite it before it appears.
- Prefer SVG/EMF for diagrams or high-resolution PNG when the renderer cannot preserve vector input.
- Target effective print resolution around 220-300 ppi for raster figures; this is a recommendation, not an official requirement.
- Ensure axes have names/units, legends are unambiguous, and line type/marker/shape remains distinguishable in grayscale. Do not rely only on color.
- Do not distort, overflow, or use a blurry screenshot when source data/code can render the figure.

## Tables

- Put `表1  表题内容` above the table, center it, keep it with the table, number continuously, and cite it first in the body.
- Use a native Word table, not an Excel screenshot. Prefer a three-line design without vertical rules.
- Compute explicit widths within the body area; do not use autofit as the final geometry.
- Use meaningful column widths, repeated header rows, expandable row heights, sufficient cell padding, and intentional alignment.
- Put units in column headers and use consistent decimal places within a column.
- Keep short tables on one page where practical. Allow long tables to break with repeated headers.
- For excessive width, simplify headings, rebalance widths, remove meaningless decimals, reduce only table type to 9 pt, split the table, then use an isolated landscape section. Do not shrink the whole paper's margins.

## References and code

Use sequential citations by first appearance and GB/T 7714 common formatting as a recommended default when no stricter supplied rule exists. Format body citations as `[1]` or `[2-4]`; use `Reference` style, real metadata, real DOI values, necessary access dates for web sources, and no placeholders or uncited decorative entries.

Use `CodeBlock` for complete appendix source. Preserve indentation and wrap or split long lines without altering semantics. Do not justify code, add Word bullets, omit key functions, or shrink below readable print size.

## Prohibited layout techniques

Do not use repeated spaces, consecutive tabs, repeated returns, spacer paragraphs, stacked text boxes, imaged text, imaged equations, manual page numbers, manually copied figure/table/equation numbers, full-width spaces for first-line indent, spreadsheet screenshots, stale Word fields, hidden identity text, or fixed line spacing that clips content.
