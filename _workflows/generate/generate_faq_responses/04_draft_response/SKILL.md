---
name: generate_faq_responses_04_draft_response
description: >-
  Step 04: draft ~50-word Draft Response from each Response Page.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Generate FAQ responses — 04 Draft response

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

When `Draft Response` column is present and `response_page_url` is set:

1. Fetch the page. On failure, leave draft blank and continue.
2. Call `finder_model` (default `claude-sonnet-4-6` from config):

```text
Write a single answer of about 50 words (45-55) to the question below, using only what the page says. Recapitulate the page's relevant content and add minimal new content of your own. No preamble, no markdown, no citations.

Question: {question}

Page text:
<<<
{page_text}
>>>
```

Trim to one paragraph. Retry once if under 30 or over 70 words.

Store `draft_response_text` per row (blank when no page or column absent).

Log: `[run-debug] workflow=_workflows/generate_faq_responses | RESPONSE | topic="..." response_page={url_or_none} draft_words=N`

Next: [../05_write_cells/SKILL.md](../05_write_cells/SKILL.md)
