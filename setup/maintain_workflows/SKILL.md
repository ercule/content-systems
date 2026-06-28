---
name: utilities_maintain_workflows
description: >-
  Audit, repair, and bring up to quality multi-step workflow orchestrators and
  step sequences. Covers run order, preflight, produce vs stage, content_staging,
  update_agent wrappers, reacts-to metadata, and workflow due checks.
"last updated": 2026-06-28T12:00:00+00:00
"last run": never
---

Audit, repair, and report on workflow orchestrators and their numbered step skills. Preserve workflow intent, fix broken run order, and align architecture with the standards below.

Run this when authoring a new workflow, after a major workflow refactor, or as part of a repo hygiene pass. Pair with [maintain_skills/SKILL.md](../maintain_skills/SKILL.md) for per-file structure and content quality.

By default, scan every main workflow orchestrator under `_workflows/`. Skip directories the user marks out of scope.

Always run the reacts-to due check (step 5) across every main workflow skill in scope, not only workflows touched in steps 1–4.

## Workflow layout

- Main orchestrator: `_workflows/{category}/{workflow_name}/SKILL.md`
- Numbered steps: `_workflows/{category}/{workflow_name}/{NN}_{slug}/SKILL.md` — only when a workflow has two or more distinct steps
- Single-step utilities: one `SKILL.md` at the workflow root (no `{NN}_*` folder). Python runners live in `scripts/` — see [scripts/README.md](../../scripts/README.md).
- Step folders use `{NN}_{slug}` with zero-padded numbers. No letter-suffix steps.
- Final produce step: `{NN}_output` (Google Doc, Markdown file, or thin wrapper over [_workflows/update_doc_handoff](../../_workflows/generate/update_doc_handoff/SKILL.md)).
- Use `_` as the only word separator in workflow folder names, step folder names, and frontmatter `name:` values. Do not use `-`.
- Do not use `{workspace_root}/workflows/`; use `{workspace_root}/_workflows/` (or `_workflows/` from repo root).
- Every step skill starts with Step 0: [run_workflow/SKILL.md](../run_workflow/SKILL.md) at the correct relative depth.

Orchestrator skills summarize run order and link to steps. They do not repeat step-level instructions (API shapes, column maps, cleanup file lists, etc.). Step skills link to prior-step outputs instead of repeating upstream content.

## Preflight step (workflows with more than 3 steps)

Any workflow with more than three numbered step skills must include a dedicated preflight step as step 01 (`01_preflight` or `01_preflight_*`). It runs immediately after Step 0 ([run_workflow/SKILL.md](../run_workflow/SKILL.md)) and before every other step.

The preflight step must:

1. Scan remaining workflow steps — read each downstream step skill and list what it will need (APIs, files, paths, prior-step outputs).
2. Ensure that all credentials, API access, connections, and paths are working — resolve credential refs, probe endpoints or filesystem paths, and stop with a clear error before expensive work begins.

Rules:

- Do not merge preflight checks into config, fetch, or transform steps; keep them in step 01.
- Preflight verifies access only; it does not perform the workflow's main work.
- Workflows with three steps or fewer may fold lightweight checks into step 01 when a separate preflight step would be overhead.

When auditing, flag multi-step workflows that lack a dedicated step-01 preflight or that defer all access checks to a later step.

## Add content_staging when you publish to a CMS

This repo should include `_workflows/content_staging/SKILL.md` when you publish to a CMS. The master skill should:

1. Define the default staging destination (CMS draft, Google Doc handoff, or both).
2. Route by source type in a routing table.
3. Name the correct publish sub-skill for each row — never embed publish logic in the master skill itself.

Publish sub-skills are workspace-specific and named by source → destination, for example:

- `publish_wordpress_from_google_doc` / `google-doc-to-wordpress`
- `google_doc_to_webflow`
- Prismic migration PUT (via `content_staging` + workspace publish step)
- `publish_from_google_doc` (HubSpot, Sanity, etc.)

The content_staging master only dispatches; it does not call CMS APIs directly except through those sub-skills.

When `content_staging` is missing, add one using the examples in this doc as a template. When a publish sub-skill is missing for a row in the table, add the row only after the publish skill exists, or mark the row as "Doc handoff only" until it does.

## Produce vs stage (hard boundary)

Every workspace content workflow falls on one side of this line — never both in the same skill tree:

| Side | Role | Typical outputs |
|------|------|-----------------|
| Produce | Create or refresh editorial content | Google Doc, Markdown, sheet row, local `RUN_DIR` artifact |
| Stage | Push an approved artifact into the CMS (draft by default) | WordPress `status=draft`, Webflow `isDraft=true`, Prismic Migration PUT, HubSpot `is_draft=true`, Sanity mutation, CMS webhook preview URL |

Rules:

1. A single workflow must not both produce and stage. Production pipelines end at Doc/Markdown/sheet. CMS writes live only in `_workflows/content_staging` dispatch targets or dedicated publish sub-skills (`publish_wordpress_from_google_doc`, `google_doc_to_webflow`, `publish_from_google_doc`, `stage-blog-from-doc`, `publish_webhook_from_google_doc`, etc.).
2. Staging is always the responsibility of `_workflows/content_staging/SKILL.md`. The master skill routes to the correct publish sub-skill; it does not embed generation logic.
3. Human approval is not a required workflow step. Review happens between runs: a human reviews the produce output, then separately invokes content_staging (or asks the agent to run the staging sub-skill). Do not add mandatory in-workflow gates unless the workspace explicitly requires one — treat review as the boundary between workflow (1) and workflow (2), not as automation inside either skill.
4. Each produce workflow has one primary output destination (Google Doc, Markdown file, etc.). An optional notify step may catalog that output (calendar row, Output sheet, Delivery tab) — notify is not staging and does not call CMS APIs.
5. When auditing, flag any produce workflow whose final step calls a CMS create/update API, and any content_staging row whose sub-skill both generates net-new body copy and POSTs/PATCHes the CMS in one run.

Good examples of produce vs stage (all under `_workflows/`):

- `_workflows/video_article_pipeline` → Google Doc only; staging via `content_staging` → publish sub-skill.
- `_workflows/llm_article_writer` → Google Doc only; staging via `content_staging`.
- `_workflows/update_agent` → Google Doc + optional sheet notify; CMS publish via `content_staging`.
- `_workflows/publish_webhook_from_google_doc` → Doc → webhook draft only (staging-only skill).

## One shared update agent

Page refresh (crosslinks, optional FAQ, dated-year freshness) lives in [_workflows/generate/update_agent/SKILL.md](../../_workflows/generate/update_agent/SKILL.md). Configure it via `{workspace_root}/config.json` → `workflow_specific.update_agent`. Optional thin entry skills under `_workflows/{category}/{name}/` may link here; do not duplicate shared steps 03–06.

Update agent invariants:

- Full regenerate only — the model returns a complete replacement article. Do not patch CMS structures in place (no Prismic span indices, no partial HTML DOM edits, no slice-level surgery).
- End state is a Google Doc for human review, not a live CMS publish.
- Publishing runs through `_workflows/content_staging` → the appropriate publish sub-skill after the reviewer runs staging separately.
- Do not include a mandatory human gate step — review is the process boundary between this produce workflow and a later staging run (see Produce vs stage above).

Wire these shared utilities into the update_agent path; do not leave them orphaned:

- [build_crosslinks](../../_workflows/generate/build_crosslinks/SKILL.md) + [init_crosslinks_json](../../_workflows/generate/init_crosslinks_json/SKILL.md)
- [update_doc_handoff](../../_workflows/generate/update_doc_handoff/SKILL.md)
- [google_sheet_write](../../_workflows/ops/google_sheet_write/SKILL.md) when the workspace has a sheet notify block configured (e.g. update_agent `calendar` preset)

Deprecate or remove workspace steps that only performed in-place CMS edits when a shared regenerate path exists.

## Reacts to (workflow metadata)

Main workflow `SKILL.md` files (orchestrators at `_workflows/{category}/{workflow}/SKILL.md`, not numbered step folders) may declare when they are expected to run using a frontmatter list called `"reacts to"`. Step skills and shared utilities do not use this field.

Format (YAML frontmatter, quoted key because of the space):

```yaml
"reacts to":
  - Plain text description of one trigger
  - Another trigger when relevant
```

Each list item is a short plain-text sentence describing an observable event or condition the agent can verify on its own.

Good examples (patterns — use each workspace's own URLs and IDs in workspace skills, not in `_workflows/`):

- A new video is published on https://www.youtube.com/@ExampleChannel after the last run date
- Seven or more days have passed since the last run
- The FAQ Coverage tab (https://docs.google.com/spreadsheets/d/EXAMPLE_SHEET_ID/edit?gid=0) has rows with status `approved` in column F and empty output in column G
- A new MCP incident on https://vulnerablemcp.info is not yet covered in https://example.com/blog/example-post

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

List every `_workflows/{category}/{name}/SKILL.md` orchestrator and its numbered step folders. Note step count, whether step 01 is preflight, and whether the workflow is produce, stage, or utility.

### 2. Audit workflow structure

For each workflow, check the following and fix any issues found:

- Orchestrator run order matches existing step folders and `Next:` links between steps.
- Step numbering is contiguous and zero-padded (`01`, `02`, …). No letter-suffix steps.
- Preflight: workflows with more than three numbered step skills must have a dedicated step 01 (`01_preflight` or `01_preflight_*`) that scans downstream steps and verifies credentials, API access, connections, and paths before any other step runs. See Preflight step above.
- Produce vs stage: no workflow both generates net-new body content and writes to a CMS in the same skill tree. Produce ends at Doc/Markdown; staging goes through `_workflows/content_staging`.
- Markdown → Google Doc: workspace output steps must delegate to [markdown_to_google_doc](../../_workflows/edit/markdown_to_google_doc/SKILL.md). Flag duplicated block rules, HTML shells, or multipart upload recipes in workspace skills.
- Add `content_staging` when it publishes to a CMS. Publish sub-skills exist for every row in the routing table, or the row is marked "Doc handoff only".
- Workspace `update_agent` entry skills are thin and point at the shared update agent; no duplicated shared steps 03–06.
- On main workflow skills, audit `"reacts to"`: remove manual-run items; rewrite external triggers so the source is concrete (URL, ID, channel, property). See Reacts to above.

For per-file structure, links, frontmatter, and content quality on individual step skills, apply [maintain_skills/SKILL.md](../maintain_skills/SKILL.md).

### 3. Repair orchestrators

- Ensure the orchestrator lists every step in execution order with Markdown links.
- Move step-level instructions out of the orchestrator into the step skill that performs them.
- Renumber steps when adding `01_preflight` requires shifting existing steps (update folder names, `Next:` links, and orchestrator references together).

### 4. Verify and report

- Run [scan_step_zero.py](../../scripts/maintain/scan_step_zero.py) and [scan_skill_links.py](../../scripts/maintain/scan_skill_links.py) from the repo root when available.
- Confirm every orchestrator and step skill touched now has both `"last updated"` and `"last run"` in ISO 8601 format (`YYYY-MM-DDTHH:MM:SS+00:00`). Update `"last updated"` for every file you changed.
- Run this file against itself and flag any updates needed.

### 5. Check reacts-to triggers

Run [scan_reacts_to.py](../../scripts/maintain/scan_reacts_to.py) from the repo root when available. It lists every main workflow skill that declares `"reacts to"`, flags invalid items (manual-run wording or vague external sources), compares `"last run"` against time-like triggers, and prints groups:

0. Invalid reacts-to — fix or remove in the skill frontmatter before treating the workflow as schedulable; re-run the scanner until this group is empty
1. Likely due — time-based triggers where the interval has elapsed or `"last run"` is `never`
2. Check external signals — concrete external triggers to verify with HTTP or named integrations

For every item in group 2, fetch the named source and compare against `"last run"` or the workflow's own output state. Flag the workflow if the condition is true now.

In the final summary, include a reacts-to section:

| Workflow | Trigger | Status |
|----------|---------|--------|
| path | trigger text | due / not due / needs human |

Offer to run any workflow flagged due unless the user opts out.

Write a short summary covering:
1. How many workflows were scanned
2. What was fixed (preflight, run order, produce vs stage, content_staging, update_agent wrappers)
3. Reacts-to: which workflows look due and why
4. Anything that still needs a human decision
