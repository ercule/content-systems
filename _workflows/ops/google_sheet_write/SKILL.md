---
name: google_sheet_write
description: >-
  Shared Google Sheets write utility. Match a row and update cell(s), or append a
  row. Used for notify/catalog steps (content calendar, Output tab, Delivery tab).
  Skips cleanly when spreadsheet config is blank.
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Google Sheet write (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

## Operations

| Mode | When to use |
|------|-------------|
| `match_update` | Find a row where a column equals a lookup value; write one or more cells on that row. |
| `append` | Add a new row (notify/catalog). |
| `match_update_or_append` | Try `match_update`; if no row matches and `append_if_missing` is true, `append`. |

OAuth bearer: Google token from [./credentials.json](./credentials.json) at `oauth_token_unified` (or `google.oauth_token_unified` — same token, either path in repo). Spreadsheets scope required.

## Common inputs

- `spreadsheet_id` — required unless config block supplies it.
- `tab` — sheet tab name.
- `values` — map of runtime fields the caller passes (e.g. `source_url`, `doc_url`, `post_name`, `source_title`).
- `workspace_config` — optional; used by presets below.

If `spreadsheet_id` is empty or missing, log `sheet=skip reason=not-configured` and return — no error.

## `match_update`

Config:

```json
{
  "match_column": "A",
  "match_value_from": "source_url",
  "normalize_url": true,
  "writes": [{ "column": "G", "value_from": "doc_url" }]
}
```

Procedure:

1. `GET …/values/{tab}!{match_column}:{match_column}` — read the match column.
2. Find the first row (1-based) where the cell equals the lookup value. When `normalize_url` is true: lowercase host, strip trailing slash, strip query and fragment.
3. On match: for each entry in `writes`, `PUT …/values/{tab}!{column}{row}?valueInputOption=USER_ENTERED` with body `{ "values": [[cell_value]] }`.
4. On no match: log `sheet=no-match` and return (unless caller uses `match_update_or_append`).

## `append`

Config:

```json
{
  "range": "A:F",
  "row_from_values": ["Topic", "doc_url", "slug", "title", "meta", ""],
  "fixed_cells": { "B": "Acme" },
  "cell_templates": {
    "D": { "kind": "hyperlink", "url_from": "doc_url", "display_template": "Acme - Update: {post_name}" }
  }
}
```

Procedure:

1. Build the row array: map `row_from_values` entries — literal strings pass through; names that exist in `values` resolve from runtime fields.
2. Apply `fixed_cells` to named columns on the appended row.
3. When `cell_templates` includes `kind: hyperlink`, write `=HYPERLINK("{url}","{display}")` where `display` comes from `display_template` with `{post_name}`, `{source_title}`, `{source_url}` placeholders.
4. `POST …/values/{tab}!{range}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS`.

## Preset: update_agent calendar notify

Callers pass `workspace_config`, `source_url`, `doc_url`, and optional `post_name` / `source_title`.

Reads `workspace_config.workflow_specific.update_agent.calendar`:

```json
{
  "spreadsheet_id": "",
  "tab": "",
  "url_match_column": "",
  "doc_url_column": "",
  "create_row_if_missing": false,
  "row_decorators": null
}
```

Maps to `match_update_or_append`:

- `match_column` = `url_match_column`
- `match_value_from` = `source_url` (with URL normalization)
- `writes` = one cell: `doc_url_column` ← `doc_url`
- `append_if_missing` = `create_row_if_missing`
- On append, apply legacy `row_decorators`:
  - `item_prefix` — prepended to URL in `url_match_column`
  - `fixed_cells` — `{ COLUMN_LETTER: VALUE }` on the new row
  - `doc_cell.kind: hyperlink` — render `=HYPERLINK("doc_url","display")` in `doc_url_column` using `display_template`

When `row_decorators` is null, append uses bare `source_url` + `doc_url` in the configured columns.

## Logging

```text
[run-debug] workflow=<caller> | sheet | spreadsheet=<id> tab=<name> op=<match_update|append|match_update_or_append> result=<updated|appended|skip|no-match>
```

## Failure handling

A 4xx from Sheets must not roll back a prior Doc or CMS write. Surface the failure with the response body; treat as soft failure when the primary deliverable (Doc, etc.) already succeeded.
