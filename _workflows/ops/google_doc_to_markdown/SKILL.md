---
name: google_doc_to_markdown
description: >-
  Read a Google Doc via the Drive API export, then produce GitHub-flavored
  Markdown (no model API required for the HTML-to-Markdown step). OAuth Bearer
  from merged repo credentials.
"last updated": 2026-06-01T00:57:13+00:00
"last run": 2026-06-01T00:57:13+00:00
---

# Google Doc to Markdown (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

## Task

Given a Google Doc URL or document ID, fetch document content using the Google Drive API, then emit Markdown that preserves headings, lists, links, and emphasis as faithfully as practical.

This skill does not update the Doc. It does not create files in Drive.

## When to use this

Use before workflows that need Markdown source text (for example editorial passes, static site generators, or hand conversion into another CMS format). Some workspace workflows (e.g. CMS guide imports) run a workspace-specific extraction step after this shared utility, applying that step's own section boundaries (such as an H1 / "Social post ideas" split) before building the webhook payload.

## Inputs

- Google Doc URL in the usual form: `https://docs.google.com/document/d/{DOC_ID}/edit` (query strings may follow; ignore them for ID extraction).
- Or `{DOC_ID}` alone when the string matches `^[a-zA-Z0-9-_]+$` and the user confirms it is a Doc ID.

## Credentials

Merge later over earlier (caller may document a workspace credentials file):

1. [./credentials.json](./credentials.json)
2. Optional ``{workspace_root}/credentials.json`` when the active workflow names it.

You need an OAuth access token whose scopes include one of:

- `https://www.googleapis.com/auth/drive.readonly`
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`

The Drive `files.export` method is not satisfied by `documents.readonly` alone. If you only have a Docs-only scope, obtain a token that includes Drive read as above, or use a different workflow that calls the Docs API JSON and maps structure manually.

### Refreshing an access token (curl)

If you have `refresh_token`, `client_id`, `client_secret`, and `token_uri` (typically `https://oauth2.googleapis.com/token`) in JSON, obtain a new access token:

```bash
curl -sS -X POST 'https://oauth2.googleapis.com/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=refresh_token' \
  --data-urlencode "refresh_token=<REFRESH>" \
  --data-urlencode "client_id=<CLIENT_ID>" \
  --data-urlencode "client_secret=<CLIENT_SECRET>"
```

Parse `access_token` from the JSON response. Do not log refresh tokens or secrets.

If your repo only stores `google.oauth_token_unified`, refresh via `grant_type=refresh_token` using `client_id`, `client_secret`, and `refresh_token` from that object (see the curl snippet above). Ensure the granted scopes include Drive read (or Docs) as required for your export path.

## Run

### 1. Document ID

From a URL, extract `DOC_ID` with a regex on `document/d/([a-zA-Z0-9-_]+)`.

### 2. Optional title

```text
GET https://www.googleapis.com/drive/v3/files/{DOC_ID}?fields=name
Authorization: Bearer {access_token}
```

If `files.get` or export returns 404 (or unclear 403), retry the same URLs with `&supportsAllDrives=true` so files on shared drives behave like native Google Docs paths.

Use `name` as the suggested Markdown H1 or document title line if the export body does not carry an equivalent.

### 3. Export body

Primary export (preserves structure best for Markdown conversion):

```text
GET https://www.googleapis.com/drive/v3/files/{DOC_ID}/export?mimeType=text%2Fhtml
Authorization: Bearer {access_token}
```

(Same `supportsAllDrives=true` retry pattern as step 2 above when the Doc lives under a shared drive.)

Response body is HTML. Save to an ephemeral file if helpful, for example `{workspace_root}/tmp/google-doc-{DOC_ID}.html`.

Log: method, host, path without token, HTTP status, content length if present.

### 4. Fallback

If the HTML export fails with 403 or 404, try:

```text
GET https://www.googleapis.com/drive/v3/files/{DOC_ID}/export?mimeType=text%2Fplain
Authorization: Bearer {access_token}
```

If plain text is all you have, wrap the body in a Markdown fenced code block titled `Plain export (structure not preserved)` and tell the user structure was lost.

### 5. HTML to Markdown

Perform conversion in the agent (no `generateContent` or other model HTTP call for this step unless a different workflow explicitly adds one). Strip Drive or Docs boilerplate wrappers, `style` blocks, and scripts. Map semantic HTML to GitHub-flavored Markdown: headings, paragraphs, ordered and unordered lists, links, bold, italic, code where obvious. Tables: preserve as Markdown tables when column count is stable; otherwise keep a simplified list form and note the compromise.

If the HTML contains forbidden or unknown tags, flatten to text or Markdown equivalents and note what dropped.

## Output

- Markdown string (or path to a file you were asked to write, for example `{workspace_root}/tmp/google-doc-{DOC_ID}.md`).
- First line or YAML-free front-matter block may repeat doc `name` as `# Title` when that helps downstream steps.

## Cleanup

If you wrote `{workspace_root}/tmp/google-doc-{DOC_ID}.html` (or `.md`) during this run, delete it before returning unless the caller asked to keep the file.

## Checks

- If you cannot obtain a Bearer token with Drive export scope, stop and say which scope is missing.
- If export returns non-2xx, log status and up to about 500 characters of body, then stop.

## Related

- Reverse direction (Markdown to new Doc): [../../edit/markdown_to_google_doc/SKILL.md](../../edit/markdown_to_google_doc/SKILL.md)
- Structured field parsing (not export Markdown): use `GET https://docs.googleapis.com/v1/documents/{DOC_ID}` and walk `body.content` and `paragraph` elements when the caller needs labeled blocks (metadata, FAQ sections, etc.) instead of a single export body.

## Next

This is a leaf shared skill. The calling workflow defines the next step after Markdown exists.
