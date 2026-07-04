---
name: publish_wp_03_build_post
description: >-
  Step 2: convert parsed paragraphs to HTML (or Gutenberg blocks), append FAQ
  if configured, and assemble the full WordPress post payload.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Publish WordPress from Google Doc — 02 Build Post

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=publish-wordpress-from-google-doc | <PHASE> | <facts>`

## Inputs

- Parsed fields from step 1: `TITLE`, `SLUG`, `EXCERPT`, `BODY_PARAGRAPHS`, `FAQ_PAIRS`
- `config.json` — read `wordpress.*` and `doc_schema.*`

## Convert body to HTML

Use `doc_schema.heading_map` to map each paragraph style to an HTML tag.

For each paragraph in `BODY_PARAGRAPHS`, build one HTML element:
- Heading styles → `<h2>`, `<h3>`, `<h4>` etc. per the map: `<h2>text</h2>`
- `NORMAL_TEXT` → `<p>text</p>`

Within each paragraph, render inline marks from runs:
- `bold: true` → wrap in `<strong>`
- `italic: true` → wrap in `<em>`
- `link_url` set → wrap in `<a href="{url}">`
- Marks compose: bold + link → `<strong><a href="...">text</a></strong>`

Concatenate all elements into `BODY_HTML`.

## Append FAQ as HTML

If `doc_schema.faq_handling` is `"append_html"` and `FAQ_PAIRS` is non-empty:

Build:
```html
<div class="faq-section">
  <h2>FAQs</h2>
  <div class="faq-item">
    <h3>{question}</h3>
    <p>{answer}</p>
  </div>
  ...
</div>
```

Append to `BODY_HTML`.

## Gutenberg format (if content_format is "gutenberg")

If `wordpress.content_format` is `"gutenberg"`, wrap each block in a Gutenberg comment:

- Paragraph: `<!-- wp:paragraph --><p>text</p><!-- /wp:paragraph -->`
- Heading h2: `<!-- wp:heading {"level":2} --><h2>text</h2><!-- /wp:heading -->`
- Heading h3: `<!-- wp:heading {"level":3} --><h3>text</h3><!-- /wp:heading -->`

Wrap the FAQ section: `<!-- wp:html -->{faq_html}<!-- /wp:html -->`

## Resolve taxonomies

For each taxonomy in `wordpress.taxonomy_defaults`:
- If the value is a list of term IDs, use it directly.
- If `null`, check whether any parsed meta field maps to this taxonomy (e.g. a `Category` field from the doc). If found, GET `{WP_API}/{taxonomy.rest_base}?slug={value}` to resolve the term ID. If not found, omit.

Store as `TAXONOMY_PAYLOAD`: `{ "categories": [id, ...], "tags": [id, ...], ... }`

## Assemble post payload

```json
{
  "title": "<TITLE>",
  "slug": "<SLUG>",
  "content": "<BODY_HTML>",
  "excerpt": "<EXCERPT>",
  "status": "<wordpress.default_status>",
  ...TAXONOMY_PAYLOAD
}
```

## Output

Hold `POST_PAYLOAD` in memory for step 3.

Log: `BUILD_OK | html_chars={n} faq_items={n} status={default_status}`

Next: [../04_publish/SKILL.md](../04_publish/SKILL.md)
