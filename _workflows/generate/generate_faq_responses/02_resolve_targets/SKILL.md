---
name: generate_faq_responses_02_resolve_targets
description: >-
  Step 02: resolve FAQ Coverage tab, header map, and rows to fill.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Generate FAQ responses — 02 Resolve targets

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Resolve the spreadsheet and `FAQ Coverage` tab by title (exact match, fallback to title containing `FAQ Coverage`). Read row 1 and build `header_map`: `{ header -> { index, column_letter } }`.

Check optional columns independently:

- If neither `Response Page` nor `Draft Response` exists, stop — nothing to fill.
- When `Draft Response` exists without `Response Page`, still resolve pages in memory for drafting but do not write Response Page cells.

Build target rows:

- Use `appended_rows_detail` when handed off from [find_faq_questions](../../../research/find_faq_questions/SKILL.md) step 05.
- Otherwise select rows with non-empty `Topic`, `Question`, and `Source` but missing at least one present optional column. Skip fully filled rows.

Parse source type and URL from each `source` value (`Reddit {url}`, `LinkedIn {url}`, `GSC {page_url}`).

Resolve `main_domain_host` from input, `gsc_site_url`, or `{workspace_root}/config.json`; null skips Reddit/LinkedIn SerpAPI lookups.

Log: `[run-debug] workflow=_workflows/generate_faq_responses | TARGETS | rows=N response_page={present|absent} draft_response={present|absent}`

Next: [../03_response_page/SKILL.md](../03_response_page/SKILL.md)
