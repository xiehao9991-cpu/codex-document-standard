---
name: codex-document-standard
description: Apply Lan an's unified visual and structural standard when Codex creates or reformats professional work documents, especially DingTalk documents and document tables. Use for reports, plans, reviews, meeting notes, summaries, proposals, and similar business documents. Preserve a user-provided template when it conflicts with this default.
---

# Codex Document Standard

Use this skill to make Codex-authored work documents visually consistent across tasks.

## Required workflow

1. Read [references/style-standard.md](references/style-standard.md) before creating or restyling a document.
2. Determine whether the user supplied an existing template.
   - If yes, preserve its structure and use the standard only for unspecified details.
   - If no, use the standard as the visual and structural default.
3. Adapt table column count and width to the content while keeping the standard colors, typography, spacing, and hierarchy.
4. Use verified facts and real links. Never fabricate evidence, metrics, dates, owners, or URLs.
5. Inventory every table in the authorized scope recursively, including nested subtables and tables inside containers. Count data tables, supporting note/code blocks, and layout containers separately; do not select tables by header color or stop after the first table. For ambiguous one-cell tables, preserve them as supporting blocks unless their data role is explicit.
6. For full-standard DOCX formatting, run `python scripts/normalize_docx_tables.py input.docx --output checked.docx --expected-tables N` (requires `python-docx`). This preserves the source, recursively normalizes data tables, and checks the saved output. Choose a font installed on the target platform with `--font`; Chinese and numeric body text must use the same family. The default uses the DOCX Normal East Asian font, falling back to Microsoft YaHei. Do not run this whole-document helper for a narrower user-authorized edit; apply and verify only that scope.
7. For authorized DingTalk online documents created by converting a DOCX, run `python scripts/apply_dingtalk_heading_styles.py <node-id> --expected-tables N --font "Microsoft YaHei"` after conversion, using the independently counted source total. Requires the authenticated `dws` CLI. DingTalk strips title formatting during import; compare imported counts before updates and stop if any source table is lost. Preserve existing documents and use a test copy for experiments.
8. Decide alignment independently for every data-table cell: one displayed line is centered; two or more displayed lines make the entire cell's own text left-aligned. Count explicit breaks, multiple non-empty paragraphs and automatic wrapping. This applies to headers, section rows and every subtable, not to the second and subsequent table rows. Do not count nested-table text or required empty terminal paragraphs as extra lines in a parent cell. Preserve values and leading zeros. Outside body text, supporting blocks and layout containers keep their separate alignment.
9. Verify the rendered or native document before completion. Check every leaf/run, including digits, split runs and hyperlinks, and reconcile all table counts. Retain the accepted 10.5 pt local / 10 pt DingTalk table sizes; supporting blocks keep their own typography. Verify headings, spacing, links, merges and unchanged fixed content. DingTalk must have no empty spacer paragraphs outside table cells. Run `python -m unittest discover -s tests -v` when changing these helpers. The helpers estimate soft wrapping from available width and font metrics (Pillow when available); missing widths/fonts, custom padding, list indents, viewer font substitution and resized columns require rendered review. Inspect actual wrapping and correct only affected cell alignment; never change font size or width just to satisfy alignment. Recheck after content or column-width changes. Structural checks alone do not establish visual equivalence; disclose unavailable rendering.

### DingTalk nested-table import boundary

DOCX import can flatten nested tables even though native JSONML supports them. A 21-table test imported as 16 tables, while explicit native creation retained both two-level subtables and supporting blocks. Do not lower the expected count to make a failed import pass. For newly authorized documents, create or restore the nested sections through `dws` native JSONML from the source structure; reconcile text, table roles, counts and nesting before styling and again after reading back. Do not automatically flatten, delete, or replace existing user document sections. This Skill's style script detects import loss but does not reconstruct lost source tables by itself.

## Boundaries

- This standard applies to professional work documents, not source code, README files, slide decks, spreadsheets, or marketing artwork unless the user explicitly requests the same visual language.
- User instructions, company templates, and existing document styles take precedence.
- When editing an existing document, make the smallest possible change and avoid whole-document replacement.
