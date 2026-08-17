---
name: generate_article_04_package_prompt
description: >-
  Step 04: write one prompt in four parts (two-sentence brief, seven voice
  bullets, extra instructions, then all copied context verbatim). End this run
  until the user accepts the pack.
"last updated": 2026-08-17T00:40:00+00:00
"last run": never
---

# Generate article — 04 Package prompt

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../03_research/SKILL.md](../03_research/SKILL.md). Require `RUN_DIR/context/`, `{id-or-slug}-inventory.md`, `{id-or-slug}-relevant-articles.md`, and `{id-or-slug}-crosslinks.md`. If any are missing, list them and end the run.

When `prompt-pack.md` and `prompt-pack.approved` already exist in `RUN_DIR`, leave the pack and go to [../05_draft/SKILL.md](../05_draft/SKILL.md).

When `prompt-pack.md` exists and `prompt-pack.approved` is missing, return the existing pack and follow **End this run**. Do not rewrite the pack.

## Inputs

- Copied context files in `RUN_DIR/context/` from [../02_context_pack/SKILL.md](../02_context_pack/SKILL.md) (every file under `context/`, path-sorted)
- `{id-or-slug}-inventory.md`, `{id-or-slug}-relevant-articles.md`, and `{id-or-slug}-crosslinks.md` from [../03_research/SKILL.md](../03_research/SKILL.md)

Read the company or product name from the copied context files (who-we-are, brand writing identity, or messaging canon). Use the name those files use in running prose.

## Write `prompt-pack.md` in `RUN_DIR`

Write one prompt that [../05_draft/SKILL.md](../05_draft/SKILL.md) can follow as its only spec. Use these four parts, in this order, with these headings:

`## General prompt`

`## Voice and tone`

`## Additional instructions`

`## Context`

### General prompt

Exactly two sentences.

Sentence 1 must follow this shape: Write an article with the title [title] for [company], [N] words.

Example: Write an article with the title What is an expense report for Gallivant, 1200 words.

Use the run `title`, the company name from context, and `target_word_count` for N.

Sentence 2 states who the article is for and what it must answer, using the inventory thesis and audience.

### Voice and tone

Exactly seven bullets. Each bullet is one voice or tone rule taken from the copied context files (brand writing identity, voice, style). Keep the wording close to those files.

### Additional instructions

Everything else the draft must follow, including:

- H1 is the run `title`
- Outline and thesis bullets from the inventory
- `specific_context` when present
- The checklist in [../07_mechanical_rewrite/SKILL.md](../07_mechanical_rewrite/SKILL.md)
- Which of `key_takeaways`, `faqs`, `categories` [../06_components/SKILL.md](../06_components/SKILL.md) will add after this draft
- Write the body in this draft. Step 06 adds FAQs, categories, and key takeaways. When the copied context already requires key takeaways first, write that `##` block now from the thesis bullets, then the intro, then the body

Then paste these two research files in full, each under its own heading:

- `### Relevant articles` — body of `{id-or-slug}-relevant-articles.md`
- `### Crosslinks` — body of `{id-or-slug}-crosslinks.md`. Required URLs must appear as in-sentence Markdown links. Sidecar `anchor_text` is a hint, not required. If the visible words are a page title or product name, rewrite them into the sentence.

### Context

Paste every copied context file in full, in path-sorted order under `RUN_DIR/context/`. Each source file starts with a heading that is the file's path inside `RUN_DIR/context/`. Then the file body, unchanged.

## Write `run-status.md` in `RUN_DIR`

Lines:

- `status: awaiting_prompt_approval`
- `run_dir:` plus the `RUN_DIR` path
- `title:` plus the article title

## End this run

Return a pointer to `prompt-pack.md` to the user.

If a person is in this chat: wait until they accept the pack (`yes`, `approved`, or equivalent). Then write an empty file `prompt-pack.approved` in `RUN_DIR`, set `run-status.md` to `status: prompt_approved`, and go to [../05_draft/SKILL.md](../05_draft/SKILL.md).

If no person is watching: end here. A later job starts at [../01_preflight/SKILL.md](../01_preflight/SKILL.md). That job continues through 02, 03, and 04 (reuse) into 05 only after `prompt-pack.approved` exists.

Log: `[run-debug] workflow=_workflows/generate/generate_article | PACK | status=awaiting_prompt_approval path={RUN_DIR}/prompt-pack.md`
