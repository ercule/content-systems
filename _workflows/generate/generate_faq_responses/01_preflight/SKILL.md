---
name: generate_faq_responses_01_preflight
description: >-
  Step 01: verify sheet id, Google OAuth, SerpAPI, and Anthropic before row work.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Generate FAQ responses — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Stop with a clear error listing anything missing. Do not continue to step 02 until preflight passes.

## Validate inputs

- `sheet_url_or_id` — required; extract spreadsheet id.

## Probe credentials

Load `{workspace_root}/credentials.json` when set; resolve `@ref` per run_workflow.

| Secret | Probe |
|--------|-------|
| `google.oauth_token_unified` | Refresh once for Sheets |
| `serpapi.api_key` | Present (Reddit/LinkedIn Response Page lookups) |
| `anthropic.api_key` | Present (Draft Response) |

## Probe sheet

`GET spreadsheets/{id}?fields=properties(title)` — must return 2xx.

Log: `[run-debug] workflow=_workflows/generate_faq_responses | PREFLIGHT | ok sheet={spreadsheet_id}`

Next: [../02_resolve_targets/SKILL.md](../02_resolve_targets/SKILL.md)
