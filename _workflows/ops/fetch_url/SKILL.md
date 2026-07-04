---
name: fetch_url
description: >-
  Shared HTML fetch for update_agent and similar workflows. Given a URL or Google Doc,
  return canonical main-body HTML, plain-text title, and the resolved source URL.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-01T00:57:13+00:00
---

# Fetch URL HTML (shared)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

## Inputs

- `input` — required. One of:
  - A web URL (`https?://…`).
  - A Google Doc URL (`https://docs.google.com/document/d/{id}/…`).
  - A bare Google Doc id (matches `^[a-zA-Z0-9-_]{20,}$`).
- `content_selector` (optional) — CSS selectors to try in order before falling back to `body`.
- `timeout_sec` (optional, default `60`).

## Outputs (carry forward to caller)

- `source_url` — canonical resolved URL (web URL, or `https://docs.google.com/document/d/{id}/edit` for Docs).
- `source_title` — string. Web: first `h1` text → `og:title` → `<title>`. Doc: file `name`.
- `content_html` — main-body HTML fragment (no surrounding `<html>` or `<body>`).
- `is_google_doc` — boolean.

## Web URL path

1. Normalize: ensure `https`, strip URL fragments. Follow at most one redirect.
2. `GET` the URL with timeout `timeout_sec`, browser-like User-Agent.
3. Title:
   - First substantive `<h1>` text.
   - Else `<meta property="og:title">`.
   - Else `<title>`.
4. Pick the main subtree using the first matching selector from `content_selector` (when supplied), otherwise try in order: `main`, `article`, `[role='main']`, the largest article-like container, then `body`.
5. Strip `script`, `style`, `noscript`, `iframe`, `nav`, `header`, `footer`, `aside`, and elements with `role="complementary"` from the chosen subtree.
6. Serialize the subtree to HTML and cap the result at ~55,000 characters before passing to downstream steps.

## Google Doc path

Detect a Doc input when:

- The string contains `docs.google.com/document/d/`, or
- The whole string matches the Doc id regex above and the caller asked for Doc resolution.

Extract the doc id with regex `/document/d/([a-zA-Z0-9-_]+)`.

1. `GET https://www.googleapis.com/drive/v3/files/{doc_id}?fields=name` → `source_title`.
2. `GET https://www.googleapis.com/drive/v3/files/{doc_id}/export?mimeType=text%2Fhtml` → `content_html`.
3. If HTML export fails, retry with `mimeType=text/plain` and wrap the body in a single `<pre>` block before returning.

OAuth bearer comes from `{workspace_root}/credentials.json` at `oauth_token_unified` (or the same token used elsewhere in this repo). Drive scope is required.

## Logging

Per step, log:

- `fetch_kind=web|google_doc`
- `source_url` (no secrets)
- `status` (HTTP status)
- `content_length`
- `title_source=h1|og|title|drive_name`

## Failure handling

- On non-2xx response, log status and the first ~500 chars of the body, then stop. Callers must treat empty `content_html` as a hard failure.
