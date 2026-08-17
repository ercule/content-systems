---
name: generate_article_07_mechanical_rewrite
description: >-
  Step 07: apply a fixed mechanical checklist to the manuscript (headings, dashes,
  images, AI-tells, crosslinks, word count). Overwrites the Markdown in place.
"last updated": 2026-08-17T00:40:00+00:00
"last run": never
---

# Generate article — 07 Mechanical rewrite

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../06_components/SKILL.md](../06_components/SKILL.md). Require `{id-or-slug}.md` and `{id-or-slug}-crosslinks.md` in `RUN_DIR`. If either is missing, list them and end the run.

## Input

- Manuscript: `{id-or-slug}.md` in `RUN_DIR`
- Crosslinks: `{id-or-slug}-crosslinks.md` in `RUN_DIR`
- Extra rules: Mechanical constraints in `prompt-pack.md`, plus phrase and heading rules in `RUN_DIR/context/`
- `target_word_count` from config in [../SKILL.md](../SKILL.md)

This step is a checklist. Voice already lives in the pack.

## Checklist (apply in order, then verify)

1. Headings use `#` through `######` with a space after the hashes. Turn lines that look like headings but use bold instead of `#` into real headings when they are clearly section titles.
2. H1 stays in title case. All other headings are sentence case except proper nouns, acronyms, and product names from the copied context files.
3. Replace every em dash (Unicode —) with a comma, period, colon, or parentheses.
4. Replace image tags and Markdown image syntax with the literal token `[image]` on its own line.
5. Rewrite any sentence that uses these tells, keeping the meaning: "actually"; "gaps" (including "the real gaps"); "not just"; "do this, not that".
6. Keep every required first-party URL from `{id-or-slug}-crosslinks.md` in running prose. Do not drop or swap destinations. Do not freeze sidecar `anchor_text`. If the visible link text is a page title, product name, or "see [destination]," rewrite it into a phrase already in the sentence.
7. Rewrite to remove: em dashes, "architecture", "shift", "structural" (replace with more plain spoken alternatives), "actual", "realities", "quiet", "silent", and adverb forms of those words

## Output

Overwrite `{id-or-slug}.md` in `RUN_DIR`.

Log: `[run-debug] workflow=_workflows/generate/generate_article | REWRITE | ok path={RUN_DIR}/{id-or-slug}.md`

Next: [../08_output/SKILL.md](../08_output/SKILL.md)
