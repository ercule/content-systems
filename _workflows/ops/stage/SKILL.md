---
name: stage
description: >-
  Scan the client content Calendar for Approved rows and offer to stage matching
  Google Docs into the CMS as drafts. Use when the user says "stage", "stage
  approved", "what's approved on the calendar", or asks to push approved
  calendar items to the CMS. Client CMS recipes live in
  _clients/{client}/_workflows/ops/stage/SKILL.md.
"last updated": 2026-08-16T00:00:00+00:00
"last run": 2026-08-17
---

# Stage (shared)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=_workflows/ops/stage | <PHASE> | <facts>`

This is a staging workflow. The file you keep is a CMS draft. Never publish live unless the user explicitly asks in this conversation.

The client skill at `_workflows/ops/stage/SKILL.md` is the entry point. It links here for the scan-and-offer protocol, then names the CMS recipe. Do not invent a CMS path.

## Configuration

Read `config.json` → `calendar` at the workspace root:

```json
{
  "calendar": {
    "enabled": true,
    "spreadsheet_id": "",
    "url": "",
    "tab": "🗓️ Calendar",
    "header_row": 1,
    "status_column": "E",
    "status_value": "Approved",
    "title_column": "A",
    "doc_url_column": "G",
    "cms_url_column": "H",
    "ready_when_cms_empty": true
  }
}
```

- `enabled: false` — stop. Report that Calendar is not configured. Do not guess a sheet.
- Missing `calendar` — try `workflow_specific.update_agent.calendar`, then `workflow_specific.publish_google_doc_to_webflow.calendar`. If still missing, stop.
- Blank `spreadsheet_id` — stop.
- `status_value` may be a string or a list. Match case-insensitively after trim.
- Omit `status_column` when the queue has no Status column: a row is ready when `doc_url_column` is non-empty and (if `ready_when_cms_empty`) `cms_url_column` is empty.
- Omit column letters to discover them from the header row: `Status`, `Doc`, `Google Doc`, `Link`, `Webflow`, `WordPress`, `CMS`, `Test URL`. Confirm the mapping with the user before staging if you had to guess.

`spreadsheet_id` may also be taken from `topic_strategy_url` when `calendar.url` is set and `spreadsheet_id` is empty.

## Credentials

`google.oauth_token_unified` (Sheets read). Probe: refresh once (`POST {token_uri}`). Do not log tokens.

CMS credentials are named in the client skill. Load them only after the user confirms a row.

## Run order

1. Preflight — workspace `config.json`, `calendar` block, Google OAuth.
2. Read the Calendar tab.
3. Filter ready rows.
4. Offer. Stop here until the user confirms which rows to stage.
5. For each confirmed row, follow the **CMS** section in the client `ops/stage` skill. Then write the CMS editor or preview URL back to `cms_url_column` when that column is configured (see [write_google_sheet](../write_google_sheet/SKILL.md)).

## Read the Calendar

```http
GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{encoded_tab}
Authorization: Bearer {access_token}
```

Encode the tab name (including emoji). Range form: `'🗓️ Calendar'!A:Z`.

Log: `[run-debug] workflow=_workflows/ops/stage | SCAN | spreadsheet=… tab=… rows=… ready=…`

## Ready rows

Skip the header (`header_row`, default 1). A data row is ready when:

1. `doc_url_column` has a Google Doc URL (or the client skill names a different source column).
2. Status matches `status_value` when `status_column` is set.
3. `cms_url_column` is empty when `ready_when_cms_empty` is true (default).

If the tab is missing, stop and say so. Do not fall back to the Strategy tab.

## Offer

List ready rows in chat: title or item, status, Doc URL, row number, and whether a CMS URL is already present.

Ask which to stage (all, some, or none). Do not stage before that answer.

If there are no ready rows, say so and stop.

## After confirm

Run the client CMS recipe for that Doc. Default is draft:

- Webflow: `isDraft=true`. No `/items/live` or `/items/publish`.
- WordPress: `status=draft`.
- HubSpot: `is_draft=true` / `publish_immediately: false`.
- Prismic: Migration draft only. Publish in the Prismic UI.
- GitHub: local branch + preview. No `git push` / `gh pr create` unless the user asks.
- Sanity: prefer draft. HumanSignal's current publisher posts published — confirm before running.

On success, report the CMS editor URL and preview URL. Write the editor URL back to `cms_url_column` when configured. A sheet writeback failure must not roll back the CMS draft.

## Safety

- Never publish live unless the user explicitly asks in this conversation.
- Do not log CMS tokens, JWTs, or Google OAuth secrets.
- Do not stage a row with no Doc URL.
- Do not treat Strategy-tab topics as Calendar rows.

## End of run

Per [run_workflow](../../../setup/run_workflow/SKILL.md): update `last run` on this skill and on the client `ops/stage` skill that ran.
