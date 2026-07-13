---
name: find_faq_questions_01_preflight
description: >-
  Step 01 for find_faq_questions: verify sheet access, credentials, and inputs
  before topic queue or SERP work.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-07-08
---

# Find FAQ questions — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Stop with a clear error listing anything missing or broken. Do not continue to step 02 until preflight passes.

## Downstream inventory

| Step | Needs |
|------|--------|
| 02_sheet_and_topics | Google Sheets read/write; `sheet_url_or_id` |
| 03_source_collection | SerpAPI; Reddit/LinkedIn source fetches |
| 04_gsc_questions | GSC OAuth with `webmasters.readonly`; SerpAPI optional |
| 05_extract_and_append | Anthropic for question extraction; Sheets append |

## Validate inputs

- `sheet_url_or_id` — required from chat or wrapper; extract spreadsheet id.
- `workspace_root` — when set, confirm `config.json` exists for GSC property derivation.

## Probe credentials

Load `{workspace_root}/credentials.json` when `workspace_root` is set; resolve `@ref` per run_workflow.

| Secret | Probe |
|--------|-------|
| `google.oauth_token_unified` | Refresh once; scopes must include Sheets and `webmasters.readonly` for GSC |
| `serpapi.api_key` | Present and non-empty |
| `anthropic.api_key` | Present and non-empty |

## Probe sheet access

`GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields=properties(title)` — must return 2xx. Confirm Strategy and FAQ Coverage tabs exist (exact resolution happens in step 02).

Log: `[run-debug] workflow=_workflows/find_faq_questions | PREFLIGHT | ok sheet={spreadsheet_id}`

Next: [../02_sheet_and_topics/SKILL.md](../02_sheet_and_topics/SKILL.md)
