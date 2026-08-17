---
name: utilities_maintain_skills
description: >-
  Audit, repair, and bring up to quality individual SKILL.md files — structure,
  content, links, frontmatter, deduplication, affirmative instructions,
  no text-replacement prompts, lists instead of tables, and cleanup. For
  workflow orchestration, use maintain_workflows.
"last updated": 2026-08-16T05:25:00+00:00
"last run": 2026-08-16
---

Audit, repair, and report on individual `SKILL.md` files. Preserve intent, fix broken structure, and revise content to match the standards below.

Architecture reference: [README.md § Documentation map](../../README.md#documentation-map). Runtime contract: [run_workflow/SKILL.md](../run_workflow/SKILL.md). Workflow rules: [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

## Architecture decisions (enforce on audit)

Skill-specific rules only. Workflow layout and preflight: [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md). Runtime paths, credentials, logging: [run_workflow/SKILL.md](../run_workflow/SKILL.md). Credential/config policy: [README.md § Credentials](../../README.md#credentials).

- Link style (this repo): use repo-relative links between skills in content-systems. Flag workspace skills that chain `../` into this repo.
- Shared skills: workspace skills link with `{content_systems_public_root}/…`.
- Deduplication: link to the canonical skill or `_context/` file.
- Preflight link: step 01 opens with a [run_workflow](../run_workflow/SKILL.md) link (not "Step 0" or `{00}_*` folders).
- Text replacement: name inputs in prose; the agent reads artifacts as context. Flag `{PLACEHOLDER}` templates, `.txt` fill-in files, and "substitute X into the template" instructions.

By default, run this on the 10 least recently updated skills in scope. Skip paths the user marks out of scope.

When the file is a workflow orchestrator or a numbered step in a pipeline, also run [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Output is a short summary (see step 6). No persistent artifacts — delete any scratch files created during this pass before finishing.

## Structure

Every skill file must have:

- Frontmatter — `name`, `description`, `"last updated"`, and `"last run"`. Add `"last run": never` when missing. Use ISO 8601 for timestamps (`YYYY-MM-DDTHH:MM:SS+00:00`).
- `name:` — underscores only; no hyphens. Should mirror the skill's path or role.
- Body — what the skill does; step-by-step instructions in execution order; where config and credentials live; where output is saved (if any); a pointer to the next step when part of a sequence.
- Links — skills in this repo use repo-relative Markdown links (`../run_workflow/SKILL.md`). Workspace skills outside this repo use `{content_systems_public_root}/…`. Remove or fix links that do not resolve.
- Cleanup — pipeline skills must say when and how to delete intermediates and `tmp/` scratch files. This maintain skill deletes its own scratch before finishing (see step 5).

Workflow layout, step numbering, run_workflow links, preflight, and orchestrator rules: [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

## Content quality

- Human readable; aim for a tenth-grade reading level.
- Use "must" for requirements; plain language elsewhere.
- State what to do. Every instruction names the required action or outcome. Prefer "Write X", "Use Y", "Keep Z" over "Do not write X", "Avoid Y", "Never Z".
- Include examples only when they prevent mistakes — a sample request shape, a snippet, or an API call. No decorative examples.
- Plain text, headers, and flat bullets. No decorative separators, bold, or italic for emphasis.
- Lists, not tables: replace every Markdown pipe table with a simple bulleted list. Put the key first, then a colon, then the rest. Apply this to skill bodies and to artifacts a skill tells the agent to write. JSON code samples may stay as fenced code.
- When a skill reads canon, point at [README.md § Troubleshooting](../../README.md#troubleshooting) (`_context/README.md` trust levels).

## Affirmative instructions

Skills prescribe actions. They omit prohibitions, anti-patterns, and "what not to do" lists.

When a draft or existing skill forbids something, rewrite it as the positive requirement that replaces it:

- Instead of "Do not copy instructions between skills": Link to the canonical skill
- Instead of "Avoid placeholder templates": Name inputs in prose; the agent reads artifacts as context
- Instead of "Never hard-code secrets in the skill body": Resolve secrets from `credentials.json`

When auditing, rewrite every "do not" / "don't" / "never" / "avoid" instruction into the action the agent should take. Keep these instead-of rewrite examples only in this maintain skill (and similar audit skills).

## No text replacement

Skills pass inputs as named context the agent reads. Requirements live in prose in the skill body.

Required pattern:

- Name inputs in prose and bullets; tell the agent what to read and apply
- Numbered step skills (for example `03_writer/SKILL.md`) state tone, structure, and constraints in the skill body — the agent reads run inputs and linked artifacts as context, not as tokens to splice into a template
- When a prior step produces an artifact, link to its path and describe how the next step uses it

When auditing, flag any skill that describes placeholder substitution (`{TOPIC}`, `{BRAND}`, and similar), hosts a replaceable template file, or depends on pre-call string merge. Refactor to a skill folder with requirements in `SKILL.md` body per [maintain_workflows — one folder per skill](../maintain_workflows/SKILL.md#workflow-layout).

## Deduplication

Each instruction must live in exactly one canonical place. Elsewhere, link to that source.

When consolidating during a maintain pass, keep the most specific canonical copy, replace duplicates with a Markdown link, and update callers.

Eval exception: skills that score or gate on quality (`content_eval`, `*-eval`, numbered eval steps) may restate criteria they check against, and must point at the canonical reference while matching its requirements exactly.

When auditing, flag the same instruction in two or more skills unless an eval skill is exercising that exception.

## Steps

### 1. Audit and fix structure

For each skill in scope:

- Complete frontmatter and required body sections (see Structure above).
- Fix links and path conventions (see [Architecture decisions](#architecture-decisions-enforce-on-audit)).
- Apply the deduplication rules above.

If the skill is part of a workflow, also apply [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

### 2. Audit and fix content quality

Revise sections that fail the content quality standards above, including [Affirmative instructions](#affirmative-instructions), [No text replacement](#no-text-replacement), and lists instead of tables. Convert every pipe table to a bulleted list.

### 3. Split oversized skills

Skills over 200 lines should likely be split. Create new files, update callers, then delete or truncate the original.

### 4. Audit references

- Every credential and config path the skill mentions must exist. Remove pointers to deleted files.
- Secrets belong in `credentials.json` (workspace root); non-secrets in `config.json`. Resolve `@ref` values per [run_workflow/SKILL.md](../run_workflow/SKILL.md). Policy: [README.md § Credentials](../../README.md#credentials). Config keys: [config.example.json](../config.example.json). Credential shapes: [credentials.example.json](../credentials.example.json).
- Model IDs must appear in `config.json` or be replaced with one that does.

### 5. Clean up

- Delete scratch files, empty stubs, and zero-byte placeholders created during this pass.
- Delete obsolete runner scripts only after skill steps fully replace them.
- Confirm dependents before deleting active prompts or assets.

### 6. Verify and report

- Manually check relative links in every SKILL.md you touched (or run a link checker in the workspace that owns these files).
- Confirm zero Markdown pipe tables remain in files you touched.
- Lint files you touched.
- Update `"last updated"` on every file you changed.
- Run this file against itself and flag any updates needed.
- When a touched skill belongs to a workflow, run [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Write a short summary covering:

1. How many skills were scanned
2. What was fixed
3. What was removed
4. Anything that still needs a human decision
