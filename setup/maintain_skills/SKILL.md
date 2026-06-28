---
name: utilities_maintain_skills
description: >-
  Audit, repair, and bring up to quality individual SKILL.md files in this repo.
  Covers structure, content quality, credentials/config, deduplication, cleanup,
  and reporting. For workflow orchestration standards, use maintain_workflows.
"last updated": 2026-06-28T12:00:00+00:00
"last run": 2026-06-24T12:00:00+00:00
---

Audit, repair, and report on individual skill files in this repo. Preserve intent, fix broken structure, and revise content quality to match the standards below.

By default, run this on the 10 least recently updated skills. Skip directories the user marks out of scope.

For workflow orchestrators, step sequences, preflight, produce vs stage, content_staging, and reacts-to due checks, also run [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

## Naming standard (repo-wide)

- Use `_` as the only word separator in workflow folder names, step folder names, and frontmatter `name:` values. Do not use `-`.
- Repo root holds `config.json`, `credentials.json`, `_context/`, and `_assets/`.
- `_context/` ships fictional example canon ([Gallivant](../../_context/README.md), [origin reference](../../_context/reference/gallivant-origin.md)) for demo; replace with real canon at `{workspace_root}/_context/` for production.
- Shipped skills live under `_workflows/{category}/{utility}/`. Publication-risk evaluation is `_workflows/edit/evaluate_content/`; rubric context lives in `{workspace_root}/_context/evaluate_content/`.
- Frontmatter `name:` mirrors the path with underscores.
- Claude plugin `{{PLUGIN_NAME}}` stays kebab-case; skill paths use underscores.

Workflow folder layout, step numbering, preflight, and orchestrator rules live in [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

## Say each instruction once

Each instruction, rule, or procedure must appear in exactly one place in the repo. Everywhere else that needs it must link to that canonical location — do not copy or paraphrase the same instruction into a second skill.

Where the canonical copy lives:

| Instruction type | Canonical home |
|------------------|----------------|
| Shared execution contract | [run_workflow/SKILL.md](../run_workflow/SKILL.md) |
| Workspace voice, brand, style | `{workspace_root}/_context/*` |
| Workflow-specific procedure | The one step skill that performs it, or the orchestrator if it is the only file |
| Cross-workflow utility | The `_workflows/{category}/{utility}/SKILL.md` that owns the behavior |
| Google Doc inline editorial markup | [show_edits_in_google_doc](../../_workflows/edit/show_edits_in_google_doc/SKILL.md) (paint plan in place), [accept_edits_google_doc](../../_workflows/edit/accept_edits_google_doc/SKILL.md) (finalize) |
| Workflow architecture | [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) |
| Browser automation (wp-admin fallback) | [_workflows/ops/browser_automation/SKILL.md](../../_workflows/ops/browser_automation/SKILL.md) — Browserbase when `config.browserbase.enabled`, else Chrome DevTools MCP |

Rules:

1. Orchestrator skills summarize and link to steps; they do not repeat step-level instructions (API shapes, column maps, cleanup file lists, etc.).
2. Step skills do not repeat the orchestrator run order or content already in an upstream step — link to the prior step output instead.
3. Reference files (`_context/*.md`, style guides, scorecards) hold editorial rules once. Pipeline skills link to them; they do not inline the same rules.
4. When consolidating duplicates during a maintain pass, keep the most specific canonical copy, replace duplicates with a Markdown link, and update callers.

Exception — eval workflows: skills whose job is to score, audit, or gate on quality (`content_eval`, `*-eval`, numbered eval steps such as `04-eval`) may restate criteria they check against. That restatement must point at the canonical reference (style guide, scorecard, brand doc) and must not introduce new requirements that are not in the source. Eval skills verify adherence; they do not become a second home for production instructions.

When auditing, flag the same instruction appearing in two or more skills or reference files unless one of them is an eval workflow exercising that exception.

## Google Doc skills — avoid duplication

- [show_edits_in_google_doc](../../_workflows/edit/show_edits_in_google_doc/SKILL.md) and [accept_edits_google_doc](../../_workflows/edit/accept_edits_google_doc/SKILL.md) paint and finalize Google Doc inline editorial markup. The caller or another workflow supplies `inline-markup-plan.json`; show does not invent edits. Runners live in [scripts/google_doc/](../../scripts/google_doc/). Do not fork plan schema or markup palette into new skills.
- [google-doc-to-markdown](../../_workflows/ops/google_doc_to_markdown/SKILL.md) and [fetch_url_html](../../_workflows/ops/fetch_url_html/SKILL.md) share Drive export mechanics — keep fetch docs in sync; do not fork OAuth refresh snippets into new skills.
- [markdown_to_google_doc](../../_workflows/edit/markdown_to_google_doc/SKILL.md) is the **only** upload recipe for new Docs from Markdown. Workspace output steps must link here and pass `doc_name`, `folder_id`, and `markdown` (or `html_fragment`) — never duplicate block rules, HTML shell, or multipart upload instructions.
- [_workflows/google_doc_to_wordpress](../../_workflows/ops/google_doc_to_wordpress/SKILL.md) is the generic WP publish template. Workspace `publish_wordpress_from_google_doc` skills should extend or replace it — do not maintain a third parallel copy.

## FAQ finder vs external linter

[faq_question_finder](../../_workflows/generate/faq_question_finder/SKILL.md) and [external_linter](../../_workflows/generate/external_linter/SKILL.md) share a similar shape (SerpAPI → extract → sheet append) but serve different outputs. Keep them separate unless extracting a documented shared base.

[faq-question-responder](../../_workflows/generate/faq_question_responder/SKILL.md) is intentionally a second pass — do not merge finder and responder.

## Repo hygiene — do not commit

- Ephemeral run data under any `tmp/` directory (repo convention). Each workflow or workspace may have its own `tmp/` folder. Use `.gitignore` (`tmp/` or `**/tmp/`). Keep `tmp/.gitkeep` only when the empty folder must exist in git.
- One-off research scripts and their scratch data unless promoted to a maintained skill.
- Vendored browser bundles (`chrome/` for Chrome for Testing) — use Playwright's bundled browser or download on demand; add `chrome/` to `.gitignore`.
- Legacy local venvs at repo root (`.venv-video`, `.venv-yt-dlp`) when a workflow-local venv exists under `scripts/`.
- Browser console mockup snippets and one-off HTML mockups after the deliverable ships.

Remove obsolete runner scripts once skill steps fully replace them (for example deleted `gslides-*` utilities).

## Credentials and config

See [README.md § Organization principles](../../README.md#organization-principles).

- `./credentials.json` at the repo root — single runtime entry point; gitignored; may use `@path#key` refs. Shape: [credentials.example.json](../credentials.example.json).
- `./config.json` — IDs, models, CMS maps, `repo.url`; no secrets.

Do not reference deleted utilities in example files. Point setup docs at the standard Google OAuth installed-app flow instead.

## Steps

### 1. Audit and fix structure

For each skill, check the following and fix any issues found:

- Frontmatter must include `name`, `description`, `"last updated"`, and `"last run"`. Add `"last run": never` to any missing it.
- Workflow skills must have a Step 0 pointing to [run_workflow/SKILL.md](../run_workflow/SKILL.md) at the correct relative depth. Shared utilities do not need one.
- Convert any bare path mentions to Markdown links. Verify `../` depth is correct and all paths are repo-relative.
- Any link pointing outside the skill's own folder or another documented repo path must be moved or removed.
- The skill must include: what it does, step-by-step instructions, locations of required config or credentials, where output is saved (if applicable), and a pointer to the next step if part of a sequence.
- Skills should always clean up after themselves. They should never leave intermediate or temporary files in places after they finish running.
- Say it once: each instruction appears in exactly one canonical skill or reference file; elsewhere link instead of copy. Eval workflows (`content_eval`, `*-eval`, eval steps) may restate criteria they check — see Say each instruction once above.

For workflow orchestrators and numbered step sequences, also apply [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md).

### 2. Audit and fix content quality

For each skill, check the following and revise any sections that don't meet them:

- All skills should be human readable. Aim for a tenth-grade reading level.
- Use "must" and "do not" for anything critical. Use plain language everywhere else.
- Instructions must be in execution order.
- Include examples where they prevent mistakes or rework — a sample API call, a Python snippet, or the exact shape of a request. Do not add examples for their own sake.
- Formatting must be plain text, headers, and flat bullets. No decorative separators, no bold or italic emphasis.
- No duplicated instructions: if this skill repeats prose that already exists elsewhere, replace the duplicate with a link to the canonical skill or reference (eval workflows excepted).

### 3. Split oversized skills

- Skills exceeding 200 lines should likely be split. Identify a logical division, create the new files, update any callers, and delete or truncate the original.

### 4. Audit and fix credentials and config

- Check that every referenced credential or config path actually exists. Remove any pointers to deleted files.
- `./credentials.json` holds only true credentials: API keys, tokens, secrets. Resolve `@ref` values per [run_workflow/SKILL.md](../run_workflow/SKILL.md). Non-secret metadata belongs in `config.json`.
- Delete empty `credentials.json` files.
- Check all model ID references against `./config.json`. Any model not listed must be replaced with one that is.

### 5. Clean up

- Delete obsolete runner scripts only once they are fully replaced by skill steps.
- Do not delete active prompts or assets without first checking what depends on them.
- Delete scratch files, empty stubs, and zero-byte placeholders created during this pass.
- Move any reference files that are not co-located with the skill that uses them.
- Ensure that all skills delete temporary files when they are done running.

### 6. Verify and report

- Run [scan_step_zero.py](../../scripts/maintain/scan_step_zero.py) and [scan_skill_links.py](../../scripts/maintain/scan_skill_links.py) from the repo root when available.
- Lint any files you touched.
- Confirm every `SKILL.md` touched now has both `"last updated"` and `"last run"` in ISO 8601 format (`YYYY-MM-DDTHH:MM:SS+00:00`). Update `"last updated"` for every file you changed.
- Run this file against itself and flag any updates needed.
- When any touched skill is part of a multi-step workflow, run [setup/maintain_workflows/SKILL.md](../maintain_workflows/SKILL.md) on that workflow.

Write a short summary covering:
1. How many skills and folders were scanned
2. What was fixed
3. What was removed
4. Anything that still needs a human decision
