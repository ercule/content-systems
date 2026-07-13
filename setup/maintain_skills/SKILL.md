---
name: utilities_maintain_skills
description: >-
  Audit, repair, and bring up to quality individual SKILL.md files — structure,
  content, links, frontmatter, deduplication, no text-replacement prompts, and cleanup.
  For workflow orchestration, use maintain_workflows.
"last updated": 2026-07-10T06:45:00+00:00
"last run": 2026-07-04
---

Audit, repair, and report on individual `SKILL.md` files. Preserve intent, fix broken structure, and revise content to match the standards below.

Architecture reference: [README.md § Documentation map](../../README.md#documentation-map). Runtime contract: [run_workflow/SKILL.md](../run_workflow/SKILL.md). Workflow rules: [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

## Architecture decisions (enforce on audit)

Skill-specific rules only. Workflow layout and preflight: [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md). Runtime paths, credentials, logging: [run_workflow/SKILL.md](../run_workflow/SKILL.md). Credential/config policy: [README.md § Credentials](../../README.md#credentials).

| Area | Correct | Wrong |
|------|---------|-------|
| Link style (this repo) | Repo-relative between skills in content-systems | Cross-repo `../` depth chains in workspace skills |
| Shared skills | `{content_systems_public_root}/…` in workspace skills | Hard-coded relative depth chains into this repo from outside |
| Deduplication | Link to canonical skill or `_context/` file | Copy run_workflow or shared ops instructions inline |
| Preflight link | Step 01 opens with [run_workflow](../run_workflow/SKILL.md) link (not "Step 0") | Missing preflight link; `{00}_*` folders |
| Text replacement | Inputs passed as named context the agent reads; prompt skills state requirements in prose | `{PLACEHOLDER}` templates, `.txt` fill-in files, or "substitute X into the template" instructions |

---

By default, run this on the 10 least recently updated skills in scope. Skip paths the user marks out of scope.

When the file is a workflow orchestrator or a numbered step in a pipeline, also run [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Output is a short summary (see step 6). No persistent artifacts — delete any scratch files created during the pass before finishing.

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
- Use "must" and "do not" for requirements; plain language elsewhere.
- Include examples only when they prevent mistakes — a sample request shape, a snippet, or an API call. No decorative examples.
- Plain text, headers, and flat bullets. No decorative separators, bold, or italic for emphasis.
- When a skill reads canon, point at [README.md § Troubleshooting](../../README.md#troubleshooting) (`_context/README.md` trust levels).

## No text replacement

Do not use text replacement anywhere in a skill.

Wrong:

- Prompt templates with `{TOPIC}`, `{BRAND}`, `{RESEARCH_OUTPUT}`, or other placeholders filled via string substitution
- Instructions like "substitute `{X}` into the template" or "literal string replacement"
- `.txt`, `.md`, or other sidecar files treated as fill-in-the-blank templates
- Scripts that merge variables into a prompt file before calling a model

Right:

- Name inputs in prose and tables; tell the agent what to read and apply
- Numbered step skills (for example `03_writer/SKILL.md`) state tone, structure, and constraints in the skill body — the agent reads run inputs and linked artifacts as context, not as tokens to splice into a template
- When a prior step produces an artifact, link to its path and describe how the next step uses it

When auditing, flag any skill that describes placeholder substitution, hosts a replaceable template file, or depends on pre-call string merge. Refactor to a skill folder with requirements in `SKILL.md` body per [maintain_workflows — one folder per skill](../maintain_workflows/SKILL.md#workflow-layout).

## Deduplication

Each instruction must live in exactly one canonical place. Elsewhere, link — do not copy or paraphrase.

When consolidating during a maintain pass, keep the most specific canonical copy, replace duplicates with a Markdown link, and update callers.

Eval exception: skills that score or gate on quality (`content_eval`, `*-eval`, numbered eval steps) may restate criteria they check against, but must point at the canonical reference and must not add requirements beyond it.

When auditing, flag the same instruction in two or more skills unless an eval skill is exercising that exception.

## Steps

### 1. Audit and fix structure

For each skill in scope:

- Complete frontmatter and required body sections (see Structure above).
- Fix links and path conventions (see [Architecture decisions](#architecture-decisions-enforce-on-audit)).
- Apply the deduplication rules above.

If the skill is part of a workflow, also apply [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

### 2. Audit and fix content quality

Revise sections that fail the content quality standards above, including [No text replacement](#no-text-replacement).

### 3. Split oversized skills

Skills over 200 lines should likely be split. Create new files, update callers, then delete or truncate the original.

### 4. Audit references

- Every credential and config path the skill mentions must exist. Remove pointers to deleted files.
- Secrets belong in `credentials.json` (workspace root); non-secrets in `config.json`. Resolve `@ref` values per [run_workflow/SKILL.md](../run_workflow/SKILL.md). Policy: [README.md § Credentials](../../README.md#credentials). Config keys: [config.example.json](../config.example.json). Credential shapes: [credentials.example.json](../credentials.example.json).
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
- When a touched skill belongs to a workflow, run [maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Write a short summary covering:

1. How many skills were scanned
2. What was fixed
3. What was removed
4. Anything that still needs a human decision
