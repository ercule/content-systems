---
name: gdoc_to_wp_01_fetch_and_parse
description: >-
  Step 1: fetch the Google Doc and parse it into structured fields using the
  doc_schema defined in config.json. Produces title, slug, excerpt, body
  paragraphs, and FAQ pairs for step 2.
"last updated": 2026-06-01T00:57:13+00:00
"last run": 2026-06-01T00:57:13+00:00
---

# Google Doc to WordPress — 01 Fetch and Parse

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

Log line prefix: `[run-debug] workflow=google-doc-to-wordpress | <PHASE> | <facts>`

## Inputs

- Google Doc URL (provided by user for this run).
- `config.json` from step 00 — read `doc_schema.*`.

## Google credentials

Load `google.token_pickle_base64` from the workspace credentials file. Decode and unpickle.
If the token is expired, refresh it: `POST https://oauth2.googleapis.com/token` with `client_id`, `client_secret`, `refresh_token`, `grant_type=refresh_token`.
Use the returned `access_token` for all Google API calls.

(For the merged repo-level OAuth pattern, see [google_doc_to_markdown](../../google_doc_to_markdown/SKILL.md).)

## Fetch the doc

Extract doc ID from `https://docs.google.com/document/d/{DOC_ID}/edit`.
`GET https://docs.googleapis.com/v1/documents/{DOC_ID}` with `Authorization: Bearer {access_token}`.
Log: `DOC_FETCH | doc_id={DOC_ID} status=200`.

## Parse paragraphs

Walk `body.content`. For each element's `paragraph`, extract:

- `namedStyleType` from `paragraphStyle`.
- Full text: concatenate `content` from all `textRun` elements, strip trailing newlines.
- Runs: for each `textRun`, record `{ text, bold, italic, link_url }` from `textStyle`.

## Extract metadata

Use `doc_schema.meta_location` to locate the metadata block:

- `"heading"`: find the heading whose text is `Content info` (case-insensitive); collect `NORMAL_TEXT` paragraphs until the next heading.
- `"top"`: collect all `NORMAL_TEXT` paragraphs before the first heading.

For each line, match `Key: Value` using the keys in `doc_schema.meta_fields`. Map each configured field.

Derive slug: take the `slug` field value, strip any leading URL path (split on `/`, take the last segment).

## Extract body

Start collecting at the first paragraph whose style matches `doc_schema.body_start_style`.
If `doc_schema.exclude_title_from_body` is true, skip that first paragraph (it becomes the post title).

Stop collecting when a heading paragraph's text starts with any prefix in `doc_schema.stop_heading_prefixes` (case-insensitive).

Skip empty paragraphs.

## Extract FAQ

If `doc_schema.faq_handling` is `"omit"`, skip this section.

Find the heading whose text starts with `doc_schema.faq_heading_prefix` (case-insensitive).
Collect Q&A pairs: each `doc_schema.faq_question_style` paragraph is a question; all following `doc_schema.faq_answer_style` paragraphs until the next question or stop heading are the answer (join with space).
Stop at any heading that starts with a prefix in `stop_heading_prefixes` (excluding the FAQ prefix itself).

## Validate

- `title`, `slug` must be non-empty. Stop and report if missing.
- `slug` must match `^[a-z0-9-]+$`. Warn but do not stop if it does not — report and let the user decide.
- Body must contain at least one paragraph. Stop if empty.

## Output

Hold in memory for step 2:

- `TITLE`, `SLUG`, `EXCERPT`.
- Any additional meta fields from `doc_schema.meta_fields` (e.g. category, tags).
- `BODY_PARAGRAPHS` — list of `{ style, text, runs: [{ text, bold, italic, link_url }] }`.
- `FAQ_PAIRS` — list of `{ question, answer }` (empty list if `faq_handling` is omit).

Log: `PARSE_OK | title="{TITLE}" slug={SLUG} body_paragraphs={n} faq_count={n}`.

## Cleanup

This step holds parsed data in memory only. If you persisted any scratch JSON or HTML dumps during debugging, delete them before returning.

## Next

[../02-build-post/SKILL.md](../02_build_post/SKILL.md)
