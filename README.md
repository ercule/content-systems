# content-systems

Open-source agent skills for content operations, a foundation for agentic marketing: workflows that research, draft, edit, evaluate, and publish content with an AI agent doing the work, not just suggesting it.

Most marketing teams have tools (CMS, docs, sheets, analytics) and knowledge (messaging decks, brand guides, competitive intel) scattered across systems. Agents can connect those pieces, but only if you give them two things: something to know and something to follow. This repo provides the "follow" part (shared, reusable skills) and a shape for the "know" part (your messaging canon).

This repository includes a demo brain called [Gallivant](_context/reference/gallivant-origin.md), a fictional enterprise travel-and-expense company used to try the system before you plug in a real brand, built on an extension of Janessa Lantz's [context builder](https://github.com/janessa-lantz/context-builder/). It also includes production-ready hands: Google Doc markup, FAQ pipelines, page refresh, WordPress publish, and more.

## Getting started

The simplest way to start working with this repo is to point an agent, such as Claude Code, Claude, or Cursor, at this file and let it take things from there. Open the repo in your agent of choice and reference this README directly; the agent will read it, along with the skill files it links to, and can guide you through cloning the repo, setting up a workspace, and running your first skill.

## A few terms, in plain language

A repository, or "repo," is just a folder of files that's stored online and tracked over time, so changes can be reviewed and undone. This document you're reading lives in a repo called `content-systems`.

To clone a repo means to download a working copy of it onto your own computer, so you have the actual files rather than just viewing them in a browser. Cloning content-systems gets you a folder full of the skill instructions described below.

A skill, in this repo, is a single instruction file (called a `SKILL.md`) that tells an AI agent exactly how to do one job, like refreshing a page or drafting FAQ answers. You don't need to write or edit these yourself to use them, though you're welcome to.

You won't need to touch any of this directly for day-to-day content work. Someone on the technical side sets up the repo and connects it to an agent; from there, you work through normal tools like Google Docs. The sections below explain how the pieces fit together, and the later sections (Quick start, Credentials, Folder layout) are the technical setup details for whoever does that connecting.

## Design principles

These ideas shape every skill and pipeline in this repo. They exist because agents behave better with clear structure than with open-ended instructions.

Separate writing from publishing. Production workflows create or revise content and stop at something a human can review, usually a Google Doc. Staging and publish workflows take an already-approved piece of content and push it to a CMS (the content management system a website runs on, like WordPress). 

Combined pipelines make it too easy to skip human review. But agents require a human in the loop, meaning a person needs to check the work before it goes live. If "write the article" and "push to production" are one pipeline, the agent, or a rushed human, can skip review and go live with unapproved copy. The system assumes editorial judgment happens in a Doc first; publishing to the CMS is a deliberate, separate second step.

Review is a process boundary between two runs (produce, then later stage/publish), not a numbered step inside either pipeline unless your workspace explicitly requires one.

Always preflight before starting. Every pipeline begins with step `01_preflight`, which proves the run can succeed before expensive work. Spec: [maintain_workflows](setup/maintain_workflows/SKILL.md) (checklist) and [run_workflow](setup/run_workflow/SKILL.md) (runtime).

One path, no fallbacks. Each skill describes exactly one way to do the job, not "try A, and if that fails try B." Multiple paths invite an agent to pick randomly or skip steps silently. If the one path can't succeed, the skill should fail with a clear message. Failure is fine; ambiguity isn't.

Never repeat instructions. This is sometimes called the DRY principle, short for "don't repeat yourself." If the same instruction would need to appear in two skills, it belongs in one canonical place, and every other skill links to it instead of restating it. Copying instructions creates drift: the copy stops getting fixes made to the original. See [Documentation map](#documentation-map).

Leave a visible trail. Every run should log what it did: which file or URL it touched, what it wrote, and where. Not secret values, but enough that a person can see what happened instead of guessing. Logging format: [run_workflow](setup/run_workflow/SKILL.md).

## Architecture

### Brain and hands

The brain is what an agent should know before writing: positioning, voice, proof, competitive context, what pages already exist. It lives in a folder called `_context/`, which is markdown your team maintains, and optionally in a second folder called `_assets/`, which holds synced snapshots so the agent reads a local copy instead of fetching live URLs every time.

The hands are what an agent does: research a question, draft copy, mark up a Google Doc, refresh a page, publish to WordPress. Each procedure is a skill, meaning a `SKILL.md` file that describes the job step by step. Shared skills live in this repo under a folder called `_workflows/`; your own workspace (explained just below) adds pipelines that link to them rather than forking, or copying and diverging from, them.

Two files carry the settings a skill needs to run. `config.json` holds non-secret settings, like URLs, sheet IDs, and model names, and is safe to commit (saved into the repo's history for anyone to see). `credentials.json` holds API keys and tokens and stays in your workspace, never in this repo.

### Your workspace and the shared library

You run production work from a workspace, which is one folder per company or content operation. It holds your canon (your team's approved messaging and voice), your secrets, your CMS connection details, and any custom pipelines you've built. It also points at a checkout of this shared skills repo; the folder path is `config.json` → `content_systems_public.path` (relative to the workspace root), not a fixed directory name.

Shared skills improve once and benefit everyone, so they live in the shared repo. Brand voice and credentials differ per company, so they live in the workspace instead. A workspace pipeline resolves the shared library through that one config setting, rather than a chain of folder references that would break if anything moved.

Runtime path rules and shared-library resolution: [run_workflow](setup/run_workflow/SKILL.md). Workflow layout and conventions: [maintain_workflows](setup/maintain_workflows/SKILL.md).

### Workflows and skills

Workflows live under `_workflows/` as numbered pipelines or single-file utilities. Layout, naming, metadata, produce/stage boundaries, and staging conventions: [maintain_workflows](setup/maintain_workflows/SKILL.md). Individual skill text, frontmatter, and formatting: [maintain_skills](setup/maintain_skills/SKILL.md).

## Documentation map

Each architectural or layout rule lives in one canonical file. This README orients readers, states design principles, and links to the owning doc. When you add or change a rule, edit the owner only — everywhere else, link instead of restating.

| File | Job |
|------|-----|
| **This README** | Onboarding, design principles, brain/hands model, workspace vs shared-library concept, folder layout, credential *policy* (where secrets live, never in this repo), quick start, troubleshooting, and agent entry checklist. |
| [`setup/run_workflow/SKILL.md`](setup/run_workflow/SKILL.md) | Runtime execution rules: workspace root resolution, `{content_systems_public_root}`, cross-repo link style, context-assembly trigger (`sync_assets`), HTTP/logging/`[run-debug]` rules, `tmp/` hygiene, credential resolution procedure (`more_credentials`, `@…#…` refs), model credential checks, end-of-run `"last run"` updates. |
| [`setup/maintain_workflows/SKILL.md`](setup/maintain_workflows/SKILL.md) | Workflow audits: Rules for layout and organization of skills within workflows, workflow metadata and naming, and workflow conventions. |
| [`setup/maintain_skills/SKILL.md`](setup/maintain_skills/SKILL.md) | Skill audits: Rules for the text of individual skills, skill metadata and naming, and skill conventions. |
| [`setup/config.example.json`](setup/config.example.json) | Non-secret configuration options and pointers to files. |
| [`setup/credentials.example.json`](setup/credentials.example.json) | Credential key shapes — catalog of service blocks and JSON paths skills may require (placeholders only); copy needed shapes into workspace `credentials.json`. Which skill needs which key is noted in `_comment` fields where applicable. |

## Example context: Gallivant

The `_context/` folder includes fictional Gallivant messaging so you can see the system work before touching a real brand. Gallivant is an invented enterprise travel-and-expense company. Use it to see how canon files, such as `canon-*.md` and `brand-writing-identity.md`, constrain what an agent generates; to run the `evaluate_content` skill against known-good and known-bad samples; and to practice the editorial markup pipeline without touching a real CMS.

When you're ready for production, swap `_context/` for your company's messaging brain and keep the same hands.

## Credentials

### Rules

A few rules govern how credentials are handled. The shared skills checkout (this repo) never stores credentials; it holds skills only. Runtime lookups (meaning, when a skill runs and needs a key) start at `credentials.json` in the workspace root. Never commit a populated credentials file to version control. Anything that isn't a secret belongs in `config.json` instead.

### Referencing credentials stored elsewhere

Workspaces may split secrets across files using `more_credentials` and `@alias#dotted.path` references. Resolution procedure: [run_workflow](setup/run_workflow/SKILL.md).

### Google OAuth

Setup shapes and required scopes: [`setup/credentials.example.json`](setup/credentials.example.json) → `google` block.

### Which credentials which skills need

Key shapes and skill mappings: [`setup/credentials.example.json`](setup/credentials.example.json).

### Config versus credentials, at a glance

`config.json` lives at the workspace root, is safe to commit, and holds non-secret settings. Key list: [`setup/config.example.json`](setup/config.example.json). `credentials.json` also lives at the workspace root but is never committed; copy needed shapes from [`setup/credentials.example.json`](setup/credentials.example.json).

## Folder layout

### Your workspace

At the root of your workspace sits `config.json`, which is committed and includes `content_systems_public.path` (where the shared skills checkout lives), alongside a `README.md` for your own team. Next to it sit `credentials.json`, which is not committed and holds your actual secrets, and `credentials.example.json`, a safe-to-commit template of the same shape. The shared library checkout itself holds skills only and no credentials — its location is whatever path you set in config, often a submodule beside the workspace root (for example `@content_systems_public` in [`setup/config.example.json`](setup/config.example.json)). Your messaging canon lives in `_context/`, and, optionally, a synced snapshot of reference material lives in `_assets/`, populated according to an optional registry file called `external_assets.md`. Finally, `_workflows/` holds your own custom pipelines, organized into the same four categories used in the shared repo: `edit/`, `generate/`, `research/`, and `ops/`.

### This repo

This repo's own root looks similar but smaller: a `README.md`, a demo `config.json` (omit `content_systems_public` when skills are local), the Gallivant demo canon in `_context/`, the shipped shared skills in `_workflows/`, and a `setup/` folder. See [Documentation map](#documentation-map) for what each file under `setup/` owns.

### Repo hygiene

Never commit: a populated `credentials.json`, anything under `tmp/` (see [run_workflow](setup/run_workflow/SKILL.md)), or local Python virtual environments.

## Troubleshooting

If `credentials.json` can't be found, check that it's at the workspace root rather than inside the shared skills checkout (`content_systems_public.path`). A Google 403 error or an `invalid_grant` message usually means an OAuth scope problem; re-run the token flow. If a shared skill can't be found, check the `content_systems_public.path` setting in `config.json`. Older workspaces may use a `content_systems` key instead — rename to `content_systems_public` to match skills. If any skill can't be found at all, look under `_workflows/` in either your workspace or the shared repo. If the agent seems to be ignoring your canon, confirm `_context/` is at the workspace root and populated with real content. If output feels off-brand despite that, check the trust levels described in `_context/README.md`, since not all canon files are treated as equally authoritative.

## Maintenance

Run [maintain_skills](setup/maintain_skills/SKILL.md) and [maintain_workflows](setup/maintain_workflows/SKILL.md) under `setup/` when you want to audit the skill library. Each file's scope is defined in [Documentation map](#documentation-map).

## Instructions for agents

Read this file, then follow [run_workflow](setup/run_workflow/SKILL.md) for every workflow run.

1. Find the workspace root (folder containing `config.json`). Confirm `credentials.json` is there, not inside the shared skills checkout (`content_systems_public.path`).
2. When the workflow reads canon or reference material, run context assembly per [run_workflow](setup/run_workflow/SKILL.md) → [sync_assets](setup/sync_assets/SKILL.md).
3. Open the target skill at `_workflows/{category}/{name}/SKILL.md` (workspace or shared repo). Run step `01_preflight`, then remaining steps in order.
4. Stop for human review after a produce skill outputs a Doc, sheet, or file. Run publish/stage skills only after review.
5. End of run: [run_workflow](setup/run_workflow/SKILL.md) § End of run. If skills look stale, offer [maintain_skills](setup/maintain_skills/SKILL.md) and [maintain_workflows](setup/maintain_workflows/SKILL.md).

Workflow layout, skill formatting, config keys, and credential shapes: [Documentation map](#documentation-map).