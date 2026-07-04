---
name: publish_wp_01_preflight_discover_and_configure
description: >-
  One-time setup step. Discovers the WordPress site's available post types,
  taxonomies, and statuses via the REST API, then inspects a sample Google Doc
  to derive the doc template schema. Outputs config.json for use by steps 02–04.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-01T00:57:13+00:00
---

# Publish WordPress from Google Doc — 01 Preflight discover and Configure

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Run this step once per workspace. It produces a `config.json` that all publish runs will use.

Log line prefix: `[run-debug] workflow=publish-wordpress-from-google-doc | <PHASE> | <facts>`

## Part A: WordPress discovery

### Credentials

Ask the user for:

- WordPress site URL (e.g. `https://example.com`).
- WordPress username.
- WordPress Application Password.

Build Basic auth: `base64("{username}:{app_password}")`.
WP_API = `{site_url}/wp-json/wp/v2`.

### Verify access

`GET {WP_API}/users/me` with Basic auth.
On 401: stop and tell the user to generate an Application Password at `{site_url}/wp-admin/profile.php`.
Log: `WP_AUTH_OK | user={name} roles={roles}`.

### Discover post types

`GET {WP_API}/types` with Basic auth.
Filter to types where `rest_base` is set and `hierarchical` is false (i.e. post-like, not pages).
Present the list to the user: name, rest_base, description.
Ask: which post type should new posts be created under?
Store as `post_type` (the `rest_base` value, e.g. `posts`, `resources`).

### Discover taxonomies

`GET {WP_API}/taxonomies` with Basic auth.
Filter to taxonomies associated with the chosen `post_type`.
For each taxonomy, `GET {WP_API}/{taxonomy.rest_base}?per_page=50` to fetch available terms.
Present each taxonomy (label, slug) and its terms to the user.
Ask for each: do you want to assign `{taxonomy.label}` when publishing? If yes, which term(s) should be the default, or should it be left to the user at publish time?

Store decisions as `taxonomy_defaults`: a map of `taxonomy_slug → [term_id, ...]` or `null` (user sets per run).

### Discover post statuses

Ask: should posts be created as `draft` or `publish` directly?
Store as `default_status`.

### Content format

Ask: should body content be posted as plain HTML or Gutenberg blocks?
Recommend HTML for simplicity unless the user specifically needs block-level features.
Store as `content_format`: `"html"` or `"gutenberg"`.

Log: `WP_DISCOVERY_OK | post_type={post_type} status={default_status} format={content_format} taxonomies={n}`.

## Part B: Doc template discovery

### Google credentials

Use the merged OAuth bearer convention from [google_doc_to_markdown](../../google_doc_to_markdown/SKILL.md): read `oauth_token_unified` from `{workspace_root}/credentials.json`, refresh via `POST https://oauth2.googleapis.com/token` (`grant_type=refresh_token`) when needed.

### Sample doc

Ask the user for a sample Google Doc URL that represents the standard template all future input docs will follow.
Extract the doc ID from `https://docs.google.com/document/d/{DOC_ID}/edit`.

`GET https://docs.googleapis.com/v1/documents/{DOC_ID}` with `Authorization: Bearer {access_token}`.

Log: `SAMPLE_DOC_FETCH | doc_id={DOC_ID}`.

### Detect metadata block

Walk `body.content` paragraphs. Look for either:

- A heading paragraph whose text matches `Content info` (any heading level) — metadata follows as `NORMAL_TEXT` paragraphs until the next heading.
- Or `NORMAL_TEXT` paragraphs at the top of the document before the first heading.

In both cases, scan for `Key: Value` lines. Record every key found.

Present to the user: "Found these metadata fields: {list}. Are these correct, or are any missing or wrong?"

Confirm which field maps to:

- `title` — the post title.
- `slug` — the URL slug (may be a full URL; extract the final path segment).
- `excerpt` — short summary or meta description.
- Any additional fields to capture (e.g. `Category`, `Tags`).

Store as `doc_schema.meta_fields`: `{ "title": "Title", "slug": "Page url", "excerpt": "Description", ... }`.

Also record `doc_schema.meta_location`: `"heading"` if preceded by a `Content info` heading, else `"top"`.

### Detect content boundaries

Identify the heading that starts the article body (typically `HEADING_1`).
Identify all headings that signal content to exclude (e.g. `FAQs`, `Social post ideas`, `Sources`).
Present findings to the user and confirm: "The article body starts at the first {style} and stops before headings starting with: {list}. Is this correct?"

Store as:

- `doc_schema.body_start_style`: e.g. `"HEADING_1"`.
- `doc_schema.stop_heading_prefixes`: e.g. `["FAQs", "Social post ideas", "Sources"]`.
- `doc_schema.exclude_title_from_body`: `true` (the H1 title is the post title, not a body block).

### Detect FAQ section

Check whether any heading starts with `faq` (case-insensitive).
If found, present: "Found a FAQ section. Questions appear as {style} headings and answers as {style} paragraphs. Should FAQs be appended to the post body as HTML, or omitted?"

Store as:

- `doc_schema.faq_heading_prefix`: e.g. `"FAQs"`.
- `doc_schema.faq_question_style`: e.g. `"HEADING_3"`.
- `doc_schema.faq_answer_style`: e.g. `"NORMAL_TEXT"`.
- `doc_schema.faq_handling`: `"append_html"` or `"omit"`.

### Detect heading style mapping

Show the user the heading levels present in the body (e.g. `HEADING_2`, `HEADING_3`) and confirm the HTML tag mapping.

Default mapping:

- `HEADING_1` → `<h2>` (top-level article heading; H1 is reserved for the page title).
- `HEADING_2` → `<h2>`.
- `HEADING_3` → `<h3>`.
- `HEADING_4` → `<h4>`.
- `NORMAL_TEXT` → `<p>`.

Ask: does this mapping look right, or do you want to adjust any levels?
Store as `doc_schema.heading_map`.

Log: `DOC_SCHEMA_OK | meta_fields={n} stop_prefixes={list} faq={faq_handling}`.

## Output

Write `config.json` to the workspace workflow directory (e.g. `<workspace>/publish-wordpress-from-google-doc/config.json`). Non-secret values only.

```json
{
  "wordpress": {
    "site_url": "...",
    "username": "...",
    "app_password": "...",
    "post_type": "...",
    "default_status": "draft",
    "content_format": "html",
    "taxonomy_defaults": {}
  },
  "doc_schema": {
    "meta_location": "top",
    "meta_fields": {
      "title": "Title",
      "slug": "Page url",
      "excerpt": "Description"
    },
    "body_start_style": "HEADING_1",
    "exclude_title_from_body": true,
    "stop_heading_prefixes": ["FAQs", "Social post ideas", "Sources"],
    "heading_map": {
      "HEADING_1": "h2",
      "HEADING_2": "h2",
      "HEADING_3": "h3",
      "HEADING_4": "h4",
      "NORMAL_TEXT": "p"
    },
    "faq_heading_prefix": "FAQs",
    "faq_question_style": "HEADING_3",
    "faq_answer_style": "NORMAL_TEXT",
    "faq_handling": "append_html"
  }
}
```

Tell the user: setup complete. Run steps 02–04 with any doc that follows this template.

## Cleanup

If you wrote any scratch dumps of the sample doc (for example `{workspace_root}/tmp/google-doc-*.json`) during discovery, delete them before returning.

## Next

[../02_fetch_and_parse/SKILL.md](../02_fetch_and_parse/SKILL.md)
