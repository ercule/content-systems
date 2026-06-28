---
name: update_agent_04_regenerate
description: >-
  Shared update agent step 4: call the enhancement model to produce a full
  replacement article with crosslinks woven in and optional FAQ section.
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Update agent — 04 Regenerate

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md).

## Rule: full document only

The model must return a complete replacement article suitable for overwriting the CMS body field. Do not return:

- JSON patches, span indices, or slice-level edits
- A list of insertions without the full surrounding prose
- Partial HTML fragments

When `include_faq` is true, append an `## FAQ` (or workspace-equivalent heading) with question/answer pairs at the end. When false, omit FAQ entirely.

## Prompt assembly

1. Load `enhance_prompt_path` when set; otherwise use the default contract below.
2. Substitute placeholders without `str.format` on HTML/Markdown (curly braces break). Use literal string replacement for:
   - `{title}` / `{source_title}`
   - `{source_url}`
   - `{source_body}` — full original HTML or Markdown
   - `{crosslinks_context}` — prefix with `CROSSLINK OPPORTUNITIES:` then `crosslinks_text`
   - `{current_year}` — four-digit year from runtime clock
   - `{include_faq}` — `yes` or `no`

### Default contract (when no workspace prompt file)

```text
You are refreshing an existing marketing page. Return the FULL updated article only.

Requirements:
- Regenerate the entire body from scratch while preserving topic, intent, and brand voice.
- Weave internal links from CROSSLINK OPPORTUNITIES into existing prose where natural.
- FAQ section: {include_faq} — when yes, append ## FAQ with 3–5 Q&A pairs grounded in the page.
- Replace stale "now" year phrases with {current_year}; do not change historical or citation years.
- Output format: {output_format}. No commentary outside the article.

Original URL: {source_url}
Title: {source_title}

CROSSLINK OPPORTUNITIES:
{crosslinks_context}

Original body:
{source_body}
```

## Model call

Use `gemini.model_smart` or `anthropic.model_smart` from `{workspace_root}/config.json` unless the workspace wrapper specifies otherwise. Credentials from `{workspace_root}/credentials.json`.

Parse the response to a single string: `enhanced_markdown` or `enhanced_html` matching `output_format`.

## Change summary (for step 05)

Build a bullet list of what changed: crosslinks added (URL + anchor text), FAQ count when applicable, dated-year substitutions, and any structural notes. Store as `change_summary_markdown`.

Next: [../05-human-gate/SKILL.md](../05_human_gate/SKILL.md)
