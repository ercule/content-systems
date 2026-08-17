---
name: generate_article_06_components
description: >-
  Step 06: add configured extra components (key takeaways, FAQs, categories)
  from the draft and prompt pack. Categories go in a separate file unless the pack
  asks for them in the article.
"last updated": 2026-08-16T05:30:00+00:00
"last run": 2026-08-16
---

# Generate article — 06 Components

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../05_draft/SKILL.md](../05_draft/SKILL.md). Require `{id-or-slug}.md` and `prompt-pack.approved` in `RUN_DIR`. If either is missing, follow the missing-file stop in 05_draft.

## Inputs

- Manuscript: `{id-or-slug}.md` in `RUN_DIR`
- Pack: `prompt-pack.md` in `RUN_DIR` (Additional instructions, thesis bullets, Context)
- Config: `workflow_specific.generate_article.components` in [../SKILL.md](../SKILL.md)

Add each listed component. When the manuscript already has that section and it matches the draft, leave it as is.

## key_takeaways

Write or replace `## Key takeaways` (or `## TL;DR` when Additional instructions in the pack names that heading).

- 3–5 bullets that match the article as written, aligned with the pack's thesis bullets.
- Place the block where Additional instructions in the pack says (default: right after the H1, before the intro).
- Concrete takeaways: definition or answer, primary insight, actionable point.

## faqs

Append `## FAQs` at the end of the manuscript (before any CTA the pack required).

- 4–6 questions the article answers, using inventory FAQ seeds when they still fit.
- Each answer is a short paragraph in the same voice as the body.
- On-site links in answers must come from `{id-or-slug}-crosslinks.md`.

## categories

Write `{id-or-slug}-categories.md` in `RUN_DIR` as a short bullet list of category names that fit the article (from the copied context files or site sections).

When Additional instructions in the pack asks for an in-body Categories block, add those labels there. When it does not, the categories file is the full output for this component.

## Output

Overwrite `{id-or-slug}.md` in `RUN_DIR`.

Log: `[run-debug] workflow=_workflows/generate/generate_article | COMPONENTS | added={list}`

Next: [../07_mechanical_rewrite/SKILL.md](../07_mechanical_rewrite/SKILL.md)
