---
name: update_agent_05_regenerate
description: >-
  Shared update agent step 5: call the enhancement model for an agent_editor
  markup plan (crosslinks, optional FAQ, dated-year freshness). Not a
  replacement article.
"last updated": 2026-09-20
P26-09-20
---

# Update agent — 05 Markup plan

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

## Rule: markup plan only

The model must return a single JSON object for [agent_editor](../../../ops/agent_editor/SKILL.md). Do not return:

- A full replacement article (Markdown or HTML)
- JSON CMS patches, span indices, or slice-level edits
- A List of changes / change summary for the Doc
- Commentary or markdown fences

When `include_faq` is true, plan an FAQ via `insert_sections` (new section) or `insert_after` (extra questions on an existing FAQ). When false, omit FAQ edits.

Prefer wrap and insert over rewrite. `old`, `insert_before`, and `insert_after` anchors must be verbatim substrings of the original body as it will appear in the Google Doc (visible text — not Markdown link syntax).

## Prompt assembly

1. Load `enhance_prompt_path` when set; otherwise use the default contract below. If a workspace prompt still asks for a full article or CMS JSON, ignore that output shape and still require the markup-plan schema here.
2. Substitute placeholders without `str.format` on HTML/Markdown (curly braces break). Use literal string replacement for:
   - `{title}` / `{source_title}`
   - `{source_url}`
   - `{source_body}` — full original HTML or Markdown
   - `{crosslinks_context}` — prefix with `CROSSLINK OPPORTUNITIES:` then `crosslinks_text`
   - `{current_year}` — four-digit year from runtime clock
   - `{include_faq}` — `yes` or `no`

### Default contract (when no workspace prompt file)

```text
You are planning inline editorial markup for an existing marketing page.
Return ONLY a JSON object matching the schema below. No markdown fences, no commentary, no replacement article.

The review Google Doc will contain the ORIGINAL article. Paint edits as red strikethrough / blue additions.

Prefer:
- replaces: wrap an existing verbatim phrase as a crosslink, or swap a stale "now" year
- insert_after: short additive text when wrapping is not possible
- insert_sections: FAQ (and similar missing sections) only
Never rewrite paragraphs. Never invent a List of changes.

`old` / insert anchors MUST be verbatim visible text from Original body.

Crosslink `new` text: keep the same visible words as `old`, then a space and the absolute URL in parentheses.
Example: ["records management", "records management (https://www.example.com/records/)"]
Do not use Markdown [text](url) in `new` — insertText cannot create hyperlinks.

Schema (omit empty keys or use empty arrays):
{
  "replaces": [["old verbatim", "new"]],
  "styled_replaces": [],
  "insert_after": [["anchor substring", " text to insert"]],
  "strike_only": [],
  "insert_sections": [
    {
      "insert_before": "anchor heading or phrase at the insert point",
      "paragraph_style_anchor": "FAQ\n",
      "blocks": [
        {"style": "HEADING_2", "text": "FAQ\n"},
        {"style": "HEADING_3", "text": "Question?\n"},
        {"style": "NORMAL_TEXT", "text": "Answer.\n"}
      ]
    }
  ],
  "trim_replacements": []
}

Requirements:
- Weave internal links from CROSSLINK OPPORTUNITIES into existing phrases (typically 5–7 unless the workspace prompt says otherwise). Do not invent URLs.
- FAQ section: {include_faq} — when yes and none exists, append via insert_sections with 3–5 Q&A pairs grounded in the page. When no, do not add FAQ.
- Replace stale "now" year phrases with {current_year}; do not change historical or citation years.

Original URL: {source_url}
Title: {source_title}

CROSSLINK OPPORTUNITIES:
{crosslinks_context}

Original body:
{source_body}
```

## Model call

Use `gemini.model_smart` or `anthropic.model_smart` from `{workspace_root}/config.json` unless the workspace wrapper specifies otherwise. Credentials from `{workspace_root}/credentials.json`.

Parse the response to one object: `markup_plan`. Strip markdown fences if present. Stop if it is not an object, if it looks like a full article, or if every of `replaces`, `styled_replaces`, `insert_after`, `strike_only`, `insert_section`, `insert_sections` is empty.

Write `{workspace_root}/tmp/inline-markup-plan.json` (create `tmp/` if needed).

Carry forward: `markup_plan`, `source_markdown` or `source_html` (unchanged original), `source_title`, `source_url`. Do not set `enhanced_markdown` to a replacement body. Do not build `change_summary_markdown` for the Doc.

When this step's only output is one blob, emit the markup plan JSON only.

Next: [../06_human_gate/SKILL.md](../06_human_gate/SKILL.md) (optional — skip unless the user asks to preview the plan before Doc upload)
