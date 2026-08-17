---
name: generate_topic_ideas_01_preflight
description: >-
  Step 01 for generate_topic_ideas: verify sheet access, credentials, and
  brand inputs before research or sheet writes.
"last updated": 2026-08-16T00:00:00+00:00
"last run": 2026-08-16
---

# Generate topic ideas — 01 Preflight

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Stop with a clear error listing anything missing or broken. Stay on this step until preflight passes.

## Downstream inventory

- 02_research: SerpAPI; [fetch_url](../../../ops/fetch_url/SKILL.md); `brand_title`; `brand_domain`
- 03_draft_and_score: Anthropic; research notes from step 02
- 04_write_sheet: Google Sheets read/write; `spreadsheet_id`; topic rows from step 03

## Validate inputs

- `sheet_url_or_id` — required from chat or wrapper; extract `spreadsheet_id` from `/spreadsheets/d/{id}`.
- `workspace_root` — when set, confirm `config.json` exists.
- `brand_title` — required before step 02. Caller value, else `{workspace_root}/config.json` `workspace_name`. Confirm inferred names with the user.
- `brand_domain` — required before step 02. Caller value, else `{workspace_root}/config.json` `main_domain`, `domain`, or first `workspace_domains` host. Normalize to an apex host (lowercase, strip scheme, path, and a leading `www.`).

Wipe `{workspace_root}/tmp/generate_topic_ideas/` at the start of this step, then create that folder for this run.

## Probe credentials

Load `{workspace_root}/credentials.json` when `workspace_root` is set; resolve `@ref` per run_workflow.

- `google.oauth_token_unified`: refresh once with `POST {token_uri}`; scope includes Sheets
- `serpapi.api_key`: present and non-empty
- `anthropic.api_key`: present and non-empty

## Probe sheet access

```http
GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields=properties(title),sheets(properties(sheetId,title))
Authorization: Bearer {access_token}
```

Expect 2xx. Log the spreadsheet title and the current tab titles. A missing `topicIdeas` tab is fine; step 04 creates it.

Log: `[run-debug] workflow=_workflows/generate_topic_ideas | PREFLIGHT | ok sheet={spreadsheet_id} brand="{brand_title}" domain={brand_domain}`

Next: [../02_research/SKILL.md](../02_research/SKILL.md)
