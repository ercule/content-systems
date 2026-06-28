---
name: markdown_to_google_doc
description: >-
  Canonical shared skill: convert Markdown (or a pre-built HTML fragment) to a
  native Google Doc via Drive multipart upload. All workflows that create Docs from
  Markdown must delegate here — do not duplicate conversion rules, HTML shell, or
  upload recipe in workspace skills.
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Markdown → Google Doc (shared)

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

Log line prefix: `[run-debug] workflow=<caller> | markdown_to_google_doc | <facts>`

## When to use

Any workflow step whose primary output is a **new Google Doc** created from Markdown (or from an HTML fragment produced upstream). Callers own prompt generation, link checks, sheet notify, and CMS staging — this skill owns HTML conversion, shell wrapping, Drive upload, and post-upload verification.

Do not copy the block rules, inline escaping procedure, DOCTYPE shell, or multipart recipe into workspace `SKILL.md` files. Link here and pass the inputs below.

Related wrappers:

- [update_doc_handoff](../../generate/update_doc_handoff/SKILL.md) — builds update_agent Markdown body, then calls this skill.
- [google-doc-to-markdown](../../ops/google_doc_to_markdown/SKILL.md) — inverse (read Doc → Markdown).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| `markdown` | Yes*, | Full Markdown body to convert. *Omit when `html_fragment` is set. |
| `html_fragment` | No | Pre-built inner HTML (no `<html>`). Skips Markdown conversion; caller must HTML-escape correctly. |
| `doc_name` | Yes | Drive file `name` field. |
| `folder_id` | Yes | Drive parent folder ID (`parents: [folder_id]`). |
| `preset` | No | Shorthand for metadata + shell (see table below). Default `standalone_article`. |
| `metadata_items` | No | Override preset metadata: list of `{label, value, href?}` rendered as `<li>` before optional `<hr />`. |
| `include_hr_before_body` | No | When true, insert `<hr />` between metadata and body. Presets set this; callers may override. |
| `shell` | No | `standard` (default) or `minimal`. |
| `verify_export` | No | Default true — run post-upload export check. |

OAuth: refresh token from [`./credentials.json`]](./credentials.json) → `oauth_token_unified` or `google.oauth_token_unified`. Drive file-create scope required.

## Outputs

- `doc_id` — from `files.create` response
- `doc_url` — `https://docs.google.com/document/d/{doc_id}/edit` (or response `webViewLink`)
- `webViewLink` — when returned by Drive

## Presets

| Preset | Metadata `<ul>` | `<hr />` before body | Shell | Typical callers |
|--------|-----------------|----------------------|-------|-----------------|
| `standalone_article` | None | No | standard | llm_article_writer produce steps (body only before template extras) |
| `no_metadata` | None | No | standard | buyers_guide, solutions_page, and similar long-form outputs |
| `update_agent_default` | Original URL, Generated, Changes made | Yes | standard | Generic update_agent via [update_doc_handoff](../../generate/update_doc_handoff/SKILL.md) |
| `video_article` | Caller-supplied items (source video, video ID, generated, pipeline) | Yes | standard | video_article_pipeline output steps |
| `custom_metadata` | Caller `metadata_items` | Usually yes | standard | update_agent (post id, slug, etc.), competitive_pages (HTML comment headers) |

When a caller skill specifies stricter layout rules than a preset (for example a blog-article-template metadata block in workspace references), build the final Markdown first, then call this skill with `preset: standalone_article` or `no_metadata` as appropriate.

## Procedure (always run in order)

1. **Convert** — If `markdown` is set, walk it top to bottom using [Block rules](#block-rules) and [Inline rules](#inline-rules). Emit one HTML fragment (no outer `<html>` / `<body>`).
2. **Metadata** — When the preset or `metadata_items` requires it, prepend the metadata `<ul>`, then optional `<hr />`, then the article fragment. When preset is `standalone_article` or `no_metadata`, the body is the fragment only.
3. **Shell** — Wrap in [HTML shell](#html-shell) (`standard` or `minimal`).
4. **Upload** — [Drive multipart create](#drive-upload).
5. **Verify** — [Post-upload check](#post-upload-check) when `verify_export` is true.

## Block rules

Drive's HTML → Google Doc import breaks when `<ul>` / `<li>` / `<p>` boundaries are wrong. Walk the source top to bottom:

1. Headings: `# title` → one `<h1>`; `## title` → one `<h2>`; `###` → `<h3>`. Close any open `<ul>` before emitting a heading.
2. Horizontal rule: a line that is only `---` → `<hr />`. Close open `<ul>` first.
3. Bullet lists: lines starting with `- ` share one `<ul>`. First `- ` after non-list context opens `<ul>`. Each `- ` → `<li>…</li>`.
4. Paragraphs: other non-empty lines → `<p>…</p>`. Close `<ul>` before `<p>`, headings, or `<hr />`.
5. Sanity check: count `<ul>` and `</ul>` — must match. No `<li>` outside lists.

Allowed tags: `h1`–`h4`, `p`, `ul`, `ol`, `li`, `a`, `strong`, `em`, `code`, `pre`, `blockquote`, `br`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `hr`.

Forbidden: `script`, `iframe`, `img`, `svg`, `style`, `video`, `object`, `embed`, `input`, `form`. Link schemes: `http`, `https`, `mailto` only.

## Inline rules

**Escape first, then insert tags — never the reverse.** Building `<a href="…">` then running `html.escape` on the whole segment produces literal `&lt;a href=…` in the Doc.

Procedure:

1. Replace each `[text](url)` and `**bold**` with ASCII placeholders containing no `<` or `>`.
2. Run `html.escape` on the tag-free segment.
3. Substitute real `<a href="…" rel="noopener noreferrer">…</a>` and `<strong>` tags back in; escape `href` and anchor text individually.

### Mandatory pre-upload self-check

Fail and fix before upload if the fragment contains:

- `&lt;a `, `&lt;/a&gt;`, `&lt;strong`, or other escaped structural tags
- Unconverted `](http` or bare `**` in body copy

Link count in HTML must match Markdown source.

## Video transcript appendix

When the Markdown contains `## Video transcript (source)` (exact heading):

- Treat everything under that heading as body copy, not `<pre>`.
- Collapse whitespace within each paragraph; wrap in one or more `<p>` blocks.
- Do not change words compared to the source file.

## Default metadata block (update_agent preset)

When preset is `update_agent_default` or caller uses equivalent items:

```html
<ul>
  <li><strong>Original URL:</strong> <a href="{url}">{url}</a></li>
  <li><strong>Generated:</strong> {YYYY-MM-DD HH:MM:SS} UTC</li>
  <li><strong>Changes made:</strong> Crosslinks added: N; FAQ section: Yes|No</li>
</ul>
<hr />
```

[update_doc_handoff](../../generate/update_doc_handoff/SKILL.md) builds richer Markdown (change summary sections); convert that Markdown with preset `standalone_article` or pass through as a single `markdown` input — the handoff skill documents the exact body shape.

## HTML shell

### Standard (`shell: standard`)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    p, ul, ol, table, h1, h2, h3, h4, h5, h6 { margin-bottom: 10pt; }
    h2 { margin-top: 20pt; }
    li { margin-bottom: 2pt; }
  </style>
</head>
<body>
  … inner HTML …
</body>
</html>
```

### Minimal (`shell: minimal`)

```html
<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head><body>… inner HTML …</body></html>
```

## Drive upload

Single recipe for all callers:

```http
POST https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true&fields=id,name,webViewLink,parents
Authorization: Bearer {access_token}
Content-Type: multipart/related; boundary={boundary}
```

Part 1 — JSON metadata:

```json
{ "name": "{doc_name}", "mimeType": "application/vnd.google-apps.document", "parents": ["{folder_id}"] }
```

Part 2 — `Content-Type: text/html; charset=UTF-8` with the full shell document.

Use a hand-built `multipart/related` body with CRLF line endings (`\r\n`). Generic MIME helpers have returned `400` from Drive while the same payload succeeded with explicit boundaries.

On success: log `doc_id`, return `doc_url`.

To replace body in place on retry: `PATCH …/upload/drive/v3/files/{id}?uploadType=media&supportsAllDrives=true` with `Content-Type: text/html`.

## Post-upload check

When `verify_export` is true:

1. `GET https://www.googleapis.com/drive/v3/files/{id}/export?mimeType=text/plain&supportsAllDrives=true`
2. Export must contain **zero** literal `<a href`, `</a>`, `<strong>`, or `**` sequences.
3. Spot-check that at least one known body link exported as a real hyperlink.

## Failure handling

A 4xx from Drive must not roll back upstream work (research, CMS draft, etc.). Surface the response body; the caller decides whether to retry.

## Logging

```text
[run-debug] workflow=<caller> | markdown_to_google_doc | folder=<id> doc_id=<id> preset=<name>
```

## Caller checklist

- [ ] Linked to this skill from the workspace step — no duplicated conversion or upload instructions.
- [ ] Passed `doc_name`, `folder_id`, and `markdown` or `html_fragment`.
- [ ] Chose the correct preset (or documented override).
- [ ] Ran post-upload verify unless explicitly skipped.
