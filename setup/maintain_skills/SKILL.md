---
name: utilities_maintain_skills
description: >-
  Audit, repair, and bring up to quality individual SKILL.md files — structure,
  content, links, frontmatter, deduplication, and cleanup. For workflow
  orchestration, use maintain_workflows.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-28
---

Audit, repair, and report on individual `SKILL.md` files. Preserve intent, fix broken structure, and revise content to match the standards below.

By default, run this on the 10 least recently updated skills in scope. Skip paths the user marks out of scope.

When the file is a workflow orchestrator or a numbered step in a pipeline, also run [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Output is a short summary (see step 6). No persistent artifacts — delete any scratch files created during the pass before finishing.

## Structure

Every skill file must have:

- Frontmatter — `name`, `description`, `"last updated"`, and `"last run"`. Add `"last run": never` when missing. Use ISO 8601 for timestamps (`YYYY-MM-DDTHH:MM:SS+00:00`).
- `name:` — underscores only; no hyphens. Should mirror the skill's path or role.
- Body — what the skill does; step-by-step instructions in execution order; where config and credentials live; where output is saved (if any); a pointer to the next step when part of a sequence.
- Links — repo-relative Markdown links with correct `../` depth. Convert bare path mentions to links. Remove or fix links that do not resolve.
- Cleanup — pipeline skills must say when and how to delete intermediates and `tmp/` scratch files. This maintain skill deletes its own scratch before finishing (see step 5).

Workflow layout, step numbering, run_workflow links, preflight, and orchestrator rules: [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

## Content quality

- Human readable; aim for a tenth-grade reading level.
- Use "must" and "do not" for requirements; plain language elsewhere.
- Include examples only when they prevent mistakes — a sample request shape, a snippet, or an API call. No decorative examples.
- Plain text, headers, and flat bullets. No decorative separators, bold, or italic for emphasis.

## Deduplication

Each instruction must live in exactly one canonical place. Elsewhere, link — do not copy or paraphrase.

When consolidating during a maintain pass, keep the most specific canonical copy, replace duplicates with a Markdown link, and update callers.

Eval exception: skills that score or gate on quality (`content_eval`, `*-eval`, numbered eval steps) may restate criteria they check against, but must point at the canonical reference and must not add requirements beyond it.

When auditing, flag the same instruction in two or more skills unless an eval skill is exercising that exception.

## Steps

### 1. Audit and fix structure

For each skill in scope:

- Complete frontmatter and required body sections (see Structure above).
- Fix links and relative path depth.
- Apply the deduplication rules above.

If the skill is part of a workflow, also apply [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

### 2. Audit and fix content quality

Revise sections that fail the content quality standards above.

### 3. Split oversized skills

Skills over 200 lines should likely be split. Create new files, update callers, then delete or truncate the original.

### 4. Audit references

- Every credential and config path the skill mentions must exist. Remove pointers to deleted files.
- Secrets belong in `credentials.json`; non-secrets in `config.json`. Resolve `@ref` values per [run_workflow/SKILL.md](../run_workflow/SKILL.md). See [README.md § Organization principles](../../README.md#organization-principles).
- Model IDs must appear in `config.json` or be replaced with one that does.

### 5. Clean up

- Delete scratch files, empty stubs, and zero-byte placeholders created during this pass.
- Delete obsolete runner scripts only after skill steps fully replace them.
- Do not delete active prompts or assets without checking dependents.

### 6. Verify and report

- Manually check relative links in every SKILL.md you touched (or run a link checker in the workspace that owns these files).
- Lint files you touched.
- Update `"last updated"` on every file you changed.
- Run this file against itself and flag any updates needed.
- When a touched skill belongs to a workflow, run [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Write a short summary covering:

1. How many skills were scanned
2. What was fixed
3. What was removed
4. Anything that still needs a human decision
