---
name: generate_topic_ideas_04_write_sheet
description: >-
  Step 04 for generate_topic_ideas: create topicIdeas if missing, clear it,
  and write Topic, Tag, Rel rows.
"last updated": 2026-08-16T00:00:00+00:00
"last run": 2026-08-16
---

# Generate topic ideas — 04 Write sheet

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

This step replaces the whole `topicIdeas` tab. [write_google_sheet](../../../ops/write_google_sheet/SKILL.md) is match/append; use the Sheets API calls below instead.

## Inputs

From [../01_preflight/SKILL.md](../01_preflight/SKILL.md):

- `spreadsheet_id`
- Google access token from the start-of-run refresh

From [../03_draft_and_score/SKILL.md](../03_draft_and_score/SKILL.md):

- `{workspace_root}/tmp/generate_topic_ideas/topics.json`

## Credentials

- Google OAuth: `{workspace_root}/credentials.json` at `google.oauth_token_unified`

## 1. Resolve or create the tab

```http
GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields=sheets(properties(sheetId,title))
Authorization: Bearer {access_token}
```

If no sheet titled `topicIdeas` exists:

```http
POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "requests": [
    { "addSheet": { "properties": { "title": "topicIdeas" } } }
  ]
}
```

If that call returns an error because the tab already exists, continue. Other 4xx/5xx stop the step.

## 2. Clear the tab

```http
POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/topicIdeas:clear
Authorization: Bearer {access_token}
Content-Type: application/json

{}
```

Expect 2xx.

## 3. Write header and rows

Build values as `[header, ...rows]` where header is `["Topic", "Tag", "Rel"]` and each data row is `[topic, tag, relevance]`.

```http
PUT https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/topicIdeas?valueInputOption=USER_ENTERED
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "range": "topicIdeas",
  "majorDimension": "ROWS",
  "values": [["Topic", "Tag", "Rel"], ["remote debugging", "dev tools", 5]]
}
```

Expect 2xx. Log method, host, path, status, and content-length.

Leave every other tab unchanged.

## 4. Cleanup

Wipe `{workspace_root}/tmp/generate_topic_ideas/` after a successful write.

Log:

```text
[run-debug] workflow=_workflows/generate_topic_ideas | SHEET | tab=topicIdeas created={true|false} rows=N
[run-debug] workflow=_workflows/generate_topic_ideas | DONE | rows=N sheet={spreadsheet_id}
```

End of run: [run_workflow](../../../../setup/run_workflow/SKILL.md) § End of run. Update `"last run"` on every executed `SKILL.md` in this workflow to today's ISO date.
