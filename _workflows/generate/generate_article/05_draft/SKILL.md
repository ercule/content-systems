---
name: generate_article_05_draft
description: >-
  Step 05: write the article from the approved prompt pack. Requires
  prompt-pack.approved. Follows that pack as the only spec.
"last updated": 2026-08-16T05:30:00+00:00
"last run": never
---

# Generate article — 05 Draft

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../04_package_prompt/SKILL.md](../04_package_prompt/SKILL.md). Require `prompt-pack.md` and `prompt-pack.approved` in `RUN_DIR`. If either is missing, report `status=awaiting_prompt_approval` and end this run with no manuscript.

## Input

Read `prompt-pack.md` in `RUN_DIR`.

## Write `{id-or-slug}.md` in `RUN_DIR`

Write the article the pack asks for. Body length and H1 come from the pack. [../06_components/SKILL.md](../06_components/SKILL.md) adds FAQs, categories, and key takeaways unless Additional instructions already required takeaways in this draft.

Log: `[run-debug] workflow=_workflows/generate/generate_article | DRAFT | words≈{n} path={RUN_DIR}/{id-or-slug}.md`

Next: [../06_components/SKILL.md](../06_components/SKILL.md)
