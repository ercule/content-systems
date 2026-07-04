---
name: generate_faq_responses_05_write_cells
description: >-
  Step 05: write Response Page and Draft Response cells; report run totals.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Generate FAQ responses — 05 Write cells

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Write each optional column to its mapped cell (not a widened range):

```http
PUT https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{encodedCell}?valueInputOption=RAW
Authorization: Bearer {access_token}
```

Example: `'FAQ Coverage'!F124` for Response Page, `'FAQ Coverage'!E124` for Draft Response. Skip blank values. Never write `LLM Response` or unmapped columns.

On write failure, log and add row to `failed_response_writes`; continue.

Report:

- `response_pages_written`
- `draft_responses_written`
- `failed_response_writes`

Log: `[run-debug] workflow=_workflows/generate_faq_responses | DONE | response_pages_written=N draft_responses_written=N failed_response_writes=N`
