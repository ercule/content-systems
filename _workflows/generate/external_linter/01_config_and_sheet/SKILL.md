---
name: external_linter_01_config_and_sheet
description: >-
  Step 01 for the shared external linter: resolve the workspace display name, the workspace's
  own domains (to exclude from results), and the destination Drive folder, then
  create a brand-new Google Sheet with a Site | Mention header row inside that
  folder.
"last updated": 2026-06-07
"last run": 2026-06-09
---

# External Linter - 01 Config And Sheet

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md).

## Inputs

From chat or caller:

- `workspace_root` — required. Path to the repo root.
- `workspace_name` — optional. Confirmed brand string for the SERP queries.
- `workspace_domains` — optional. Apex hosts to exclude from results.
- `drive_folder_id` — optional. Destination folder.

## Credentials

- Google OAuth for Drive + Sheets: `./credentials.json` at `google.oauth_token_unified`. Scopes: `drive` and `spreadsheets`.

Refresh the Google access token once at the start of the workflow. Reuse it for every Drive and Sheets call. Do not log tokens.

## 1. Read workspace config

Read ``{workspace_root}/config.json``. From it you will derive the workspace domains and the Drive folder; missing values fall back to the caller-supplied inputs.

## 2. Resolve workspace display name

Resolve `workspace_name` per [Resolve workspace display name](../SKILL.md#resolve-workspace-display-name): caller input → ``{workspace_root}/config.json`` `workspace_name` → inferred from domain/folder. If it was inferred, show the user the resolved name and the exact two queries and confirm before any search happens in step 02.

## 3. Resolve workspace domains (exclusion set)

These are the hosts that count as "the workspace's own domain" and are dropped from the SERP in step 02.

1. If the caller passed `workspace_domains`, use them.
2. Else collect candidates from ``{workspace_root}/config.json``:
   - `site_url`, `site`, `main_domain_host`, or `gsc_site_url` (strip scheme and `sc-domain:` prefix).
   - `webflow.domains[*]`.
   - The host of any `*_url` field that is clearly the workspace site (not `docs.google.com`, `drive.google.com`, or `sheets.googleapis.com`).
3. Normalize every candidate to its apex host: lowercase, strip scheme, strip path, strip a leading `www.`.
4. Build `workspace_hosts` = the deduped apex host set. Treat both the apex and any `www.` subdomain as the workspace when matching in step 02 (match on apex so subdomains like `blog.`, `docs.`, `www.` are all excluded).

If no domain can be determined, ask the user for the workspace's primary domain before continuing — the exclusion set is the whole point of an *external* linter.

Log:

```text
[run-debug] workflow=_workflows/external_linter | DOMAINS | workspace_hosts=[...]
```

## 4. Resolve Drive folder

1. If the caller passed `drive_folder_id`, use it.
2. Else read `google_drive_url` from ``{workspace_root}/config.json`` and extract the folder id from the `/folders/{id}` segment (ignore any `?usp=...` query and `/u/0/` user prefix).
3. If the resolved `google_drive_url` is empty (some workspaces have `""`), stop and ask the user for a destination folder id.

## 5. Create the new Google Sheet in the folder

Create the spreadsheet directly inside the Drive folder using Drive `files.create` so it lands in the right place in one call:

```http
POST https://www.googleapis.com/drive/v3/files?supportsAllDrives=true&fields=id,name,webViewLink,parents
Authorization: Bearer {access_token}
Content-Type: application/json
```

Body:

```json
{
  "name": "External Linter — {workspace_name} — {YYYY-MM-DD}",
  "mimeType": "application/vnd.google-apps.spreadsheet",
  "parents": ["{drive_folder_id}"]
}
```

Capture `spreadsheet_id` from the response `id` and the sheet URL from `webViewLink` (form: `https://docs.google.com/spreadsheets/d/{id}/edit`).

Then resolve the first tab's title (a new spreadsheet has one tab, usually `Sheet1`):

```http
GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields=properties(title),sheets(properties(sheetId,title))
Authorization: Bearer {access_token}
```

Set `tab_title` to the first sheet's title.

## 6. Write the header row

Write the header row to the first tab:

```http
PUT https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{encodedRange}?valueInputOption=RAW
Authorization: Bearer {access_token}
Content-Type: application/json
```

Where `{encodedRange}` covers `'{tab_title}'!A1:B1` and the body is:

```json
{ "values": [["Site", "Mention"]] }
```

Log:

```text
[run-debug] workflow=_workflows/external_linter | SHEET | created spreadsheet_id={id} folder={drive_folder_id} tab="{tab_title}"
```

## Outputs for next step

Carry these values forward:

- `workspace_name` — confirmed brand string.
- `workspace_hosts` — apex host exclusion set.
- `spreadsheet_id`
- `tab_title`
- `sheet_url`
- `drive_folder_id`

## Checks

- [ ] Google access token refreshed (drive + spreadsheets scopes).
- [ ] `workspace_name` resolved and confirmed.
- [ ] `workspace_hosts` exclusion set built (non-empty, apex hosts).
- [ ] Drive folder id resolved.
- [ ] New spreadsheet created inside the folder.
- [ ] `Site | Mention` header row written to the first tab.
