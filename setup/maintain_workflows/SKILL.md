---
name: utilities_maintain_workflows
description: >-
  Audit, repair, and bring up to quality multi-step workflow orchestrators and
  step sequences. Covers run order, preflight, produce vs stage, stage_content,
  update_agent wrappers, reacts-to metadata, verb-first naming, one-folder-per-skill layout,
  and workflow due checks.
"last updated": 2026-07-10T06:45:00+00:00
"last run": 2026-07-04
---

Audit, repair, and report on workflow orchestrators and their numbered step skills. Preserve workflow intent, fix broken run order, and align architecture with the standards below.

Design principles: [README.md § Design principles](../../README.md#design-principles). Per-skill audits: [maintain_skills/SKILL.md](../maintain_skills/SKILL.md). Runtime contract: [run_workflow/SKILL.md](../run_workflow/SKILL.md).

## Architecture decisions (enforce on audit)

Workflow-specific rules only. Runtime paths, credentials, logging: [run_workflow/SKILL.md](../run_workflow/SKILL.md). Per-skill text and frontmatter: [maintain_skills/SKILL.md](../maintain_skills/SKILL.md). Design principles: [README.md § Design principles](../../README.md#design-principles).

| Decision | Rule |
|----------|------|
| Repo boundary | Shared produce/ops skills live in `@content_systems_public`; local repos hold thin orchestrators and CMS-specific publish steps. Do not fork shared skill steps. |
| Preflight | Step `01_preflight` (or `01_preflight_*`) links [run_workflow](../run_workflow/SKILL.md) first; full checklist in [Preflight step](#preflight-step-required) below. |
| Produce vs stage | Produce pipelines end at Doc/Markdown/sheet; CMS API writes only in `stage_content` → publish sub-skills — never both in one workflow tree. |
| Naming | Verb-first workflow folder names (`generate_*`, `publish_*`, `stage_*`); `_` separator only. |
| Categories | Produce in `generate/`, `edit/`, `research/`; staging/publish/evaluate in `ops/`. |
| One folder per skill | Every skill — orchestrator, numbered step, or auxiliary helper — lives in its own folder with exactly one `SKILL.md`. One folder, one skill; one skill, one folder. |
| update_agent | One shared [update_agent](../../_workflows/edit/update_agent/SKILL.md); workspace wrappers link in after preflight — no duplicated downstream steps. |

---

Run this when authoring a new workflow, after a major workflow refactor, or as part of a repo hygiene pass. Pair with [maintain_skills/SKILL.md](../maintain_skills/SKILL.md) for per-file structure, frontmatter, links, and content quality on individual skills.

By default, scan every workflow orchestrator in scope — a root `SKILL.md` that names a pipeline under `_workflows/`. Skip directories the user marks out of scope.

Always run the reacts-to due check (step 5) across every main workflow skill in scope, not only workflows touched in steps 1–4.

## Workflow layout

Find the workspace root per [run_workflow/SKILL.md](../run_workflow/SKILL.md). Workflow skills live under `_workflows/`.

- Orchestrator — one root `SKILL.md` per workflow (the folder that names the pipeline).
- One folder per skill — every skill in a workflow tree gets its own folder containing exactly one `SKILL.md`. Do not put two skills in one folder, two `SKILL.md` files in one folder, or loose prompt/template files beside a skill instead of in a dedicated skill folder.
- Numbered steps — each pipeline step is a subfolder `{NN}_{slug}/SKILL.md` under that workflow folder. Step 01 is always preflight (see below). Most workflows have two or more numbered steps after preflight. Multi-step produce and stage pipelines must use this shape — do not ship them as a single root `SKILL.md` without numbered step folders.
- Step folders use `{NN}_{slug}` with zero-padded numbers starting at `01` (`01`, `02`, …). No letter-suffix steps. No `{00}_*` folders.
- Final produce step: `{NN}_output` (Google Doc, Markdown file, or thin wrapper over [markdown_to_google_doc](../../_workflows/ops/markdown_to_google_doc/SKILL.md)).
- Use `_` as the only word separator in workflow and step folder names. Do not use `-`.
- Category placement — every workflow lives under `_workflows/{category}/`:
  - Produce pipelines (`generate_*`, `edit_*`, `update_*`, `research_*`) live in `edit/`, `generate/`, or `research/` — never in `ops/`.
  - Staging and publish pipelines (`stage_*`, `publish_*`, `evaluate_content`, and other CMS or ops skills) live in `ops/` only — never in `edit/`, `generate/`, or `research/`. 

Per-skill frontmatter and link conventions: [maintain_skills/SKILL.md](../maintain_skills/SKILL.md). Prompt and template rules: [maintain_skills — No text replacement](../maintain_skills/SKILL.md#no-text-replacement).

## Workflow naming (verb-first)

The workflow folder name must start with a verb that describes what the pipeline does. Use `{verb}_{object}` or `{verb}_{object}_{qualifier}` — not bare nouns or role names alone.

Common verb prefixes:

| Prefix | Use for |
|--------|---------|
| `edit_` | Revise, polish, or transform existing content |
| `generate_` | Create net-new editorial content |
| `build_` | Assemble structured output (crosslinks, posts, payloads) |
| `find_` / `research_` | Discover questions, sources, SERP data, queue rows |
| `update_` | Refresh an existing live page or record |
| `publish_` | Push an approved artifact to a CMS or webhook |
| `stage_` | Route artifacts into CMS drafts (dispatch orchestrators) |
| `evaluate_` | Score, lint, or gate content quality |

Good examples: `generate_video_article`, `generate_article`, `find_faq_questions`, `update_agent`, `publish_wordpress_from_google_doc`, `stage_content`, `evaluate_content`.

Bad examples: `video_article_pipeline`, `llm_article_writer`, `content_staging`, `blog_tile`, `whitepaper` — rename to a verb-first form when you touch the workflow (for example `generate_video_article`, `generate_article`, `stage_content`, `build_blog_tile`).

Rules:

- The workflow folder name and orchestrator frontmatter `name:` must share the same verb-first stem (optional workspace-specific prefixes in `name:` are fine — e.g. `generate_video_article`).
- Net-new article pipelines use `generate_article`, not `generate_llm_article` — rename legacy `generate_llm_article` folders when you touch them.
- Numbered step folders describe their slice of the work (`01_preflight`, `02_fetch_source`); they do not need a verb prefix when the step role is already clear.
- Shared library skills under the content-systems repo follow the same rule when added or renamed.

When auditing, flag workflow folders that do not start with a recognized verb prefix, legacy `generate_llm_article` names, workflows in the wrong category folder (produce outside `ops/`, staging/publish inside `ops/` only), folders with more than one skill, or skills not in their own folder. Rename folder, orchestrator links, and frontmatter `name:` together — do not leave a mismatched folder and `name:`.

## Step numbering (no zero-indexing)

- The first step is step 01, not step 0. Numbered steps start at `01` and count up contiguously.
- Step 01 is always preflight (`01_preflight` or `01_preflight_*`). It opens with a link to [run_workflow/SKILL.md](../run_workflow/SKILL.md), then verifies the run can succeed before any downstream step runs.
- Do not use `{00}_*` step folders or prose like "step 00", "Step 0", or zero-indexed sub-step lists.
- Zero-padding in folder names (`01`, `02`) is for sort order only — it is not zero-indexing of step identity.

When auditing, flag and fix any workflow using step 0 / step 00 labeling, `{00}_*` folders, gaps before `01`, or a first step that is not preflight.

## Orchestrator vs step skills

Orchestrator skills summarize run order and link to steps. They do not repeat step-level instructions (API shapes, column maps, cleanup file lists, etc.).

Step skills do not repeat the orchestrator run order or content already in an upstream step — link to the prior step output instead.

When auditing, flag orchestrators that embed step procedures and step skills that duplicate upstream content or the orchestrator run order.

## Preflight step (required)

Every workflow must start with step 01 preflight (`01_preflight` or `01_preflight_*`). Preflight proves the rest of the pipeline can run before any expensive or mutating work begins.

The preflight step must:

1. Link to [run_workflow/SKILL.md](../run_workflow/SKILL.md) at the top of the skill body.
2. Resolve `{content_systems_public_root}` from `config.json` → `content_systems_public.path`.
3. Read the orchestrator and every downstream step skill — list what each step needs (APIs, files, paths, inputs, prior-step outputs, models, sheet tabs, CMS endpoints).
4. Resolve and validate configuration — required keys in `config.json`, `workflow_specific.*` blocks, env-style variables, folder IDs, and spreadsheet IDs referenced anywhere in the workflow.
5. Resolve and probe credentials — load workspace-root `credentials.json`, resolve `more_credentials` and `@…#…` refs, and verify each secret/API the workflow needs (auth handshake, read-only fetch, or HEAD request — not full pipeline work).
6. Probe filesystem and network paths — confirm URLs, Drive folders, sheet tabs, `{content_systems_public_root}`, and local paths exist and are reachable.
7. Stop with a clear error listing what is missing or broken. Do not continue to step 02 until preflight passes.

Rules:

- Do not merge preflight checks into config, fetch, transform, or output steps — keep them in step 01.
- Preflight verifies readiness only; it must not perform the workflow's editorial or CMS work.
- Standalone pipelines that are still a single root `SKILL.md` must be split: add `01_preflight`, move the existing procedure to `02_*` (or more steps), and update the orchestrator run order.

When auditing, flag any workflow whose step 01 is not preflight or that defers access/config checks to a later step.

## Add stage_content when you publish to a CMS

The workspace should include a `stage_content` orchestrator when you publish to a CMS. The master skill should:

1. Define the default staging destination (CMS draft, Google Doc handoff, or both).
2. Route by source type in a routing table.
3. Name the correct publish sub-skill for each row — never embed publish logic in the master skill itself.

Publish sub-skills are workspace-specific and named by source → destination, for example:

- `publish_wordpress_from_google_doc` / `google-doc-to-wordpress`
- `google_doc_to_webflow`
- Prismic migration PUT (via `stage_content` + workspace publish step)
- `publish_from_google_doc` (HubSpot, Sanity, etc.)

The `stage_content` master only dispatches; it does not call CMS APIs directly except through those sub-skills.

When `stage_content` is missing, add one using the examples in this doc as a template. When a publish sub-skill is missing for a row in the table, add the row only after the publish skill exists, or mark the row as "Doc handoff only" until it does.

## Produce vs stage (hard boundary)

Every workspace content workflow falls on one side of this line — never both in the same skill tree:

| Side | Role | Typical outputs |
|------|------|-----------------|
| Produce | Create or refresh editorial content | Google Doc, Markdown, sheet row, local `RUN_DIR` artifact |
| Stage | Push an approved artifact into the CMS (draft by default) | WordPress `status=draft`, Webflow `isDraft=true`, Prismic Migration PUT, HubSpot `is_draft=true`, Sanity mutation, CMS webhook preview URL |

Rules:

1. A single workflow must not both produce and stage. Production pipelines end at Doc/Markdown/sheet. CMS writes live only in the workspace `stage_content` dispatch targets or dedicated publish sub-skills (`publish_wordpress_from_google_doc`, `google_doc_to_webflow`, `publish_from_google_doc`, `stage-blog-from-doc`, `publish_webhook_from_google_doc`, etc.).
2. Staging is always the responsibility of the workspace `stage_content` orchestrator (legacy folder name: `content_staging`). The master skill routes to the correct publish sub-skill; it does not embed generation logic.
3. Human approval is not a required workflow step. Review happens between runs: a human reviews the produce output, then separately invokes `stage_content` (or asks the agent to run the staging sub-skill). Do not add mandatory in-workflow gates unless the workspace explicitly requires one — treat review as the boundary between workflow (1) and workflow (2), not as automation inside either skill. See [README § Design principles](../../README.md#design-principles).
4. Each produce workflow has one primary output destination (Google Doc, Markdown file, etc.). An optional notify step may catalog that output (calendar row, Output sheet, Delivery tab) — notify is not staging and does not call CMS APIs.
5. When auditing, flag any produce workflow whose final step calls a CMS create/update API, and any `stage_content` routing row whose sub-skill both generates net-new body copy and POSTs/PATCHes the CMS in one run.

Good examples of produce vs stage:

- `generate_video_article` → Google Doc only; staging via `stage_content` → publish sub-skill.
- `generate_article` → Google Doc only; staging via `stage_content`.
- `update_agent` → Google Doc + optional sheet notify; CMS publish via `stage_content`.
- `publish_webhook_from_google_doc` → Doc → webhook draft only (staging-only skill).

## One shared update agent

Page refresh (crosslinks, optional FAQ, dated-year freshness) lives in the shared [update_agent](../../_workflows/edit/update_agent/SKILL.md) skill. Configure it via `config.json` → `workflow_specific.update_agent`. Optional thin entry skills in your workspace may link here; do not duplicate shared steps after preflight.

When maintaining the shared update_agent or any workspace wrapper, step 01 must be `01_preflight`; renumber existing steps (legacy `01_config` → `02_config`, etc.) and move config resolution into preflight or step 02 as appropriate.

Update agent invariants:

- Full regenerate only — the model returns a complete replacement article. Do not patch CMS structures in place (no Prismic span indices, no partial HTML DOM edits, no slice-level surgery).
- End state is a Google Doc for human review, not a live CMS publish.
- Publishing runs through the workspace `stage_content` orchestrator → the appropriate publish sub-skill after the reviewer runs staging separately.
- Do not include a mandatory human gate step — review is the process boundary between this produce workflow and a later staging run (see Produce vs stage above).

Wire these shared utilities into the update_agent path; do not leave them orphaned:

- [build_crosslinks](../../_workflows/research/build_crosslinks/SKILL.md)
- [markdown_to_google_doc](../../_workflows/ops/markdown_to_google_doc/SKILL.md)
- [write_google_sheet](../../_workflows/ops/write_google_sheet/SKILL.md) when the workspace has a sheet notify block configured (e.g. update_agent `calendar` preset)

Deprecate or remove workspace steps that only performed in-place CMS edits when a shared regenerate path exists.

## Reacts to (workflow metadata)

Main workflow orchestrator `SKILL.md` files — not numbered step folders — may declare when they are expected to run using a frontmatter list called `"reacts to"`. Step skills and shared utilities do not use this field.

Format (YAML frontmatter, quoted key because of the space):

```yaml
"reacts to":
  - Plain text description of one trigger
  - Another trigger when relevant
```

Each list item is a short plain-text sentence describing an observable event or condition the agent can verify on its own.

Good examples (patterns — use each workspace's own URLs and IDs in workspace skills, not in shipped library skills):

- A new video is published on https://www.youtube.com/@ExampleChannel after the last run date
- Seven or more days have passed since the last run
- The FAQ Coverage tab (https://docs.google.com/spreadsheets/d/EXAMPLE_SHEET_ID/edit?gid=0) has rows with status `approved` in column F and empty output in column G
- A new item appears on https://example.com/feed.xml that is not yet covered in https://example.com/blog/example-post

Bad examples (do not use):

- A stakeholder shares a YouTube URL and asks for a blog draft — manual request, not an observable trigger
- Editorial asks to clear approved FAQ rows — manual request
- A new YouTube video is published on a channel the team tracks — source not specified; use the channel URL or handle
- A new MCP security breach is reported in primary sources — source not specified; name the sites or feeds to check

Rules:

- Do not list manual-run triggers. Omit anything that depends on a person asking, sharing a link, or requesting a run. Those are normal on-demand runs, not reacts-to conditions.
- Time and schedule triggers are fine (daily, weekly, N days since last run, each Monday after data is ready).
- External triggers must name the source concretely enough that the agent can detect the condition on its own: full URL, spreadsheet link, YouTube channel URL or handle, GSC property (`sc-domain:…`), analytics pane path, queue tab and column, or another fetchable endpoint. The agent must not have to guess which feed, sheet, or channel to check.
- Multiple items mean any one of them may warrant a run (OR semantics).

When authoring or repairing a main workflow skill, add or fix `"reacts to"` during this pass. Remove invalid items and tighten vague external sources.

## Steps

### 1. Inventory workflows

List every workflow orchestrator in scope (root `SKILL.md` for a pipeline) and its numbered step subfolders. Note step count, whether step 01 is preflight, whether the folder name is verb-first, and whether the workflow is produce, stage, or utility.

### 2. Audit workflow structure

For each workflow, apply [Architecture decisions](#architecture-decisions-enforce-on-audit), [Workflow layout](#workflow-layout), [Workflow naming](#workflow-naming-verb-first), [Step numbering](#step-numbering-no-zero-indexing), [Preflight step](#preflight-step-required), [Orchestrator vs step skills](#orchestrator-vs-step-skills), [Produce vs stage](#produce-vs-stage-hard-boundary), [Add stage_content](#add-stage_content-when-you-publish-to-a-cms), [One shared update agent](#one-shared-update-agent), and [Reacts to](#reacts-to-workflow-metadata). Path and credential checks: [run_workflow/SKILL.md](../run_workflow/SKILL.md). Logging: [run_workflow/SKILL.md](../run_workflow/SKILL.md) § Execution rules.

For per-skill structure, frontmatter, links, and content quality, apply [maintain_skills/SKILL.md](../maintain_skills/SKILL.md) to every orchestrator and step skill in the workflow — including [one folder per skill](#workflow-layout) and [no text replacement](../maintain_skills/SKILL.md#no-text-replacement).

### 3. Repair orchestrators

- Ensure the orchestrator lists every step in execution order with Markdown links.
- Move step-level instructions out of the orchestrator into the step skill that performs them.
- Renumber steps when adding `01_preflight` requires shifting existing steps (rename `01_config` → `02_config`, etc.; update folder names, `Next:` links, and orchestrator references together).
- Split single-file standalone pipelines into `01_preflight` plus downstream numbered steps.
- Replace "Step 0" labels with a run_workflow link at the top of step 01 (or the first numbered step). Rename `{00}_*` folders to start at `01` and renumber downstream steps.
- Rename non-verb-first workflow folders to verb-first names; update orchestrator `name:`, links, and config references in the same change.

### 4. Verify and report

- Manually verify step 01 preflight links and run order on every orchestrator touched in this pass (step 5 covers reacts-to separately).
- Run [maintain_skills/SKILL.md](../maintain_skills/SKILL.md) verify steps on every orchestrator and step skill touched in this pass.
- Run this file against itself and flag any updates needed.

### 5. Check reacts-to triggers

Review every main workflow skill that declares `"reacts to"`. Flag invalid items (manual-run wording or vague external sources), compare `"last run"` against time-like triggers, and group findings as:

1. Invalid reacts-to — fix or remove in the skill frontmatter before treating the workflow as schedulable; re-run the scanner until this group is empty
2. Likely due — time-based triggers where the interval has elapsed or `"last run"` is `never`
3. Check external signals — concrete external triggers to verify with HTTP or named integrations

For every item in group 3, fetch the named source and compare against `"last run"` or the workflow's own output state. Flag the workflow if the condition is true now.

In the final summary, include a reacts-to section:

| Workflow | Trigger | Status |
|----------|---------|--------|
| path | trigger text | due / not due / needs human |

Offer to run any workflow flagged due unless the user opts out.

Write a short summary covering:
1. How many workflows were scanned
2. What was fixed (naming, preflight, run order, produce vs stage, stage_content, update_agent wrappers)
3. Reacts-to: which workflows look due and why
4. Anything that still needs a human decision
