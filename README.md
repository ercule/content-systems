# content-systems

Open-source **agent skills** for content operations — a foundation for **agentic marketing**: workflows that research, draft, edit, evaluate, and publish content with an AI agent doing the work, not just suggesting it.

Most marketing teams have tools (CMS, docs, sheets, analytics) and knowledge (messaging decks, brand guides, competitive intel) scattered across systems. Agents can connect those pieces — but only if you give them two things:

| Layer | What it is | Where it lives in this repo |
|-------|------------|-----------------------------|
| **Marketing brain** | What the agent *knows* — approved messaging, voice, proof, competitive context, content inventory | [`_context/`](_context/README.md), optional [`_assets/`](setup/sync_assets/SKILL.md), [`config.json`](setup/config.example.json) |
| **Marketing hands** | What the agent *does* — fetch pages, mine FAQs, draft copy, mark up edits, publish to CMS | [`_workflows/`](_workflows/README.md), [`setup/run_workflow/`](setup/run_workflow/SKILL.md) |

This repository ships: a demo brain ([Gallivant](_context/reference/gallivant-origin.md)) in an attempt to extend Janessa Lantz' [context builder](https://github.com/janessa-lantz/context-builder/) and production-ready hands (Google Doc markup, FAQ pipelines, page refresh, WordPress publish, and more).

Each skill is a `SKILL.md` file an agent reads and follows step by step.

Clone this repository and work from its **root** — the directory that contains `config.json`, `credentials.json`, `_context/`, `_workflows/`, and `setup/`.

**Agents (Claude Code, Claude, Cursor):** read this file end to end before the first skill run. Execute the [Agent checklist](#agent-checklist) in order. Ask the user for missing values. **Do not print, log, or commit secrets.**

---

## Why agentic marketing

Traditional marketing automation moves data between systems. **Agentic marketing** adds an agent that can reason over your canon, call APIs, run scripts, and complete multi-step pipelines — with human gates where judgment matters (editorial review in Google Docs, publish approval, etc.).

This repo is a starter kit for that model:

1. **Install a brain** — replace the Gallivant demo in `_context/` with your messaging canon ([context-builder](https://github.com/janessa-lantz/context-builder) shape), or use Gallivant to learn the system first.
2. **Wire up hands** — run shipped skills as-is, or compose custom pipelines in `_workflows/` that link to them.
3. **Connect credentials once** — `credentials.json` at repo root; skills resolve keys through a shared contract ([run_workflow](setup/run_workflow/SKILL.md)).
4. **Extend** — add your own orchestrators under `_workflows/`, swap in your canon, and fork or contribute back as your needs grow.

The brain feeds the hands: `_context/` and `_assets/` inform what skills produce; `_workflows/` executes against Google Docs, your CMS, search APIs, and LLMs.

---

## Quick start

```bash
git clone <repository-url> content-systems
cd content-systems
cp setup/config.example.json config.json
cp setup/credentials.example.json credentials.example.json
cp setup/credentials.example.json credentials.json   # then fill secrets
```

A [`.gitignore`](.gitignore) ignores `credentials.json`, `**/tmp/`, local `.venv/` trees, and transcription scratch output.

**Verify:** `./setup/run_workflow/SKILL.md` and `./_workflows/ops/show_edits_in_google_doc/` exist.

---

## I want to…

| I want to… | Start here | Needs |
|------------|------------|--------|
| Mark up edits in a Google Doc | [_workflows/show_edits_in_google_doc](_workflows/ops/show_edits_in_google_doc/SKILL.md) | Google OAuth, `inline-markup-plan.json` |
| Finalize markup after review | [_workflows/accept_edits_google_doc](_workflows/ops/accept_edits_google_doc/SKILL.md) | Google OAuth |
| Convert Doc → Markdown | [_workflows/google_doc_to_markdown](_workflows/ops/google_doc_to_markdown/SKILL.md) | Google OAuth |
| Create a Doc from Markdown | [_workflows/markdown_to_google_doc](_workflows/ops/markdown_to_google_doc/SKILL.md) | Google OAuth |
| Mine FAQ questions (sheet) | [_workflows/find_faq_questions](_workflows/research/find_faq_questions/SKILL.md) | Google OAuth, SerpAPI, GSC |
| Draft FAQ responses | [_workflows/generate_faq_responses](_workflows/generate/generate_faq_responses/SKILL.md) | Google OAuth, SerpAPI, Anthropic |
| Audit external brand mentions | [_workflows/evaluate_external_brand](_workflows/research/evaluate_external_brand/SKILL.md) | SerpAPI, Google OAuth, Playwright |
| Refresh an existing page | [_workflows/update_agent](_workflows/edit/update_agent/SKILL.md) | `workflow_specific.update_agent` in config |
| Publish Doc → WordPress | [_workflows/publish_wordpress_from_google_doc](_workflows/ops/publish_wordpress_from_google_doc/SKILL.md) | WP + Google OAuth |
| Browser fallback (CMS login) | [_workflows/browser_automation](_workflows/ops/browser_automation/SKILL.md) | Optional Browserbase |

---

## What's inside

### The marketing brain

| Path | Role |
|------|------|
| [_context/](_context/README.md) | **Messaging canon** — approved positioning, voice, proof, entities, content index. Ships with fictional [Gallivant](_context/reference/gallivant-origin.md) demo data; replace for production. |
| [_assets/](setup/sync_assets/SKILL.md) | **Materialized copy** — synced snapshots of live pages and external docs the agent can read without hitting URLs every run. Populated by [sync_assets](setup/sync_assets/SKILL.md) from `external_assets.md`. |
| `config.json` | **Operational config** — site URLs, sheet IDs, model names, workflow-specific blocks. Committed; no secrets. |
| `external_assets.md` | Optional registry of URLs/paths for asset sync. |

Skills that write or evaluate content should read the brain *before* generating — see [Context assembly](setup/run_workflow/SKILL.md) in the run contract.

### The marketing hands

| Path | Role |
|------|------|
| [_workflows/](_workflows/README.md) | **Skills by job type** — `research/`, `generate/`, `edit/`, `ops/`. Each folder has a `SKILL.md` the agent executes step by step. |
| [setup/run_workflow/](setup/run_workflow/SKILL.md) | **Step 0 contract** — credential resolution, context assembly, HTTP logging, Browserbase handoff. Every skill starts here. |

### Supporting infrastructure

| Layer | Path | Holds |
|-------|------|--------|
| **Asset sync** | [setup/sync_assets/](setup/sync_assets/SKILL.md) | Materialize `_assets/` from `external_assets.md` |
| **Hygiene** | [setup/maintain_skills/](setup/maintain_skills/SKILL.md), [setup/maintain_workflows/](setup/maintain_workflows/SKILL.md) | Author audits for skill quality and layout |
| **Setup templates** | [setup/](setup/) | Example `config.json` and `credentials.json` shapes |

Every skill run resolves **workspace root**: the directory that contains `config.json`. Walk up from the active `SKILL.md` until you find it (repo root in a normal setup).

### Skill categories at a glance

| Category | Typical use | Examples |
|----------|-------------|----------|
| **research/** | Discover opportunities, audit the market, build link maps | FAQ mining, external brand audit, crosslinks |
| **generate/** | Produce net-new drafts from research inputs | FAQ response drafting |
| **edit/** | Multi-step pipelines that refresh or reshape existing content | Page refresh (`update_agent`) |
| **ops/** | Atomic utilities — fetch, convert, markup, evaluate, publish | Doc ↔ Markdown, inline edits, WordPress publish, browser fallback |

---

## Agent checklist

Follow this in order on first setup. Ask the user for anything you cannot infer.

### 1. Clone and enter the repo

See [Quick start](#quick-start).

### 2. Ensure git ignores secrets

```bash
git check-ignore -v credentials.json
```

Must be ignored before writing secrets.

### 3. Create config.json

```bash
cp setup/config.example.json config.json
```

Edit `config.json`:

- `repo.url` — URL for this repository (blank until published is OK)
- Model names under `anthropic` / `gemini` if the user has preferences
- Service-specific IDs (sheet IDs, site URLs) as needed — **not secrets**
- `workflow_specific.*` blocks when running multi-step pipelines like [update_agent](_workflows/edit/update_agent/SKILL.md)

**Verify:** `jq . config.json` succeeds.

### 4. Create credentials.json

```bash
cp setup/credentials.example.json credentials.json
```

Fill inline values for each key the planned skills require. See [Credentials](#credentials).

Optional: split secrets using `@` references — see [Reference syntax](#reference-syntax).

**Verify:** `git check-ignore -v credentials.json` still passes after creating the file.

### 5. Set up the marketing brain

Skills read from **`{workspace_root}/_context/`**.

- **Learning / demo:** use shipped [Gallivant](_context/README.md) canon as-is. Run a generate or evaluate skill to see how canon shapes output.
- **Production:** replace `_context/` with real messaging canon ([context-builder](https://github.com/janessa-lantz/context-builder) shape). Keep the same file roles: `messaging-canon.md`, `canon-*.md`, `brand-writing-identity.md`, `content-index.md`, etc.

Optional asset layer:

1. Create `external_assets.md` (see [setup/sync_assets/external_assets.example.md](setup/sync_assets/external_assets.example.md)).
2. Run [setup/sync_assets/SKILL.md](setup/sync_assets/SKILL.md) to populate `{workspace_root}/_assets/`.

### 6. Register the repo with your agent environment

Point your agent at this README and the run contract so every session knows the rules.

**Cursor**

1. Open this repo as your project root.
2. Add a project rule or `@`-mention this README at the start of content workflow tasks.
3. Reference [setup/run_workflow/SKILL.md](setup/run_workflow/SKILL.md) as Step 0 for every skill.
4. Skills live under `_workflows/{category}/{name}/SKILL.md` — open or `@`-mention the target skill before running.
5. Browserbase sessions: follow [browser_automation](_workflows/ops/browser_automation/SKILL.md) — repeat the live session URL while the session is open.

**Claude Code**

1. Clone the repo and work from its root.
2. Create `CLAUDE.md` at repo root pointing here:

   ```markdown
   # Content systems

   Read ./README.md before any workflow.
   Step 0: setup/run_workflow/SKILL.md
   Skills: _workflows/{category}/{name}/SKILL.md
   Never commit credentials.json.
   ```

3. Register individual skills from `_workflows/` if your setup supports skill discovery.

**Claude (chat) / other agents**

Paste this README plus the target skill's `SKILL.md`. The user maintains `credentials.json` locally; the agent should ask for missing keys by name, never echo values.

### 7. Pull latest (ongoing)

```bash
git pull --ff-only
```

### 8. Smoke-test

1. Read [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).
2. Read the target skill's `SKILL.md` (see [Skill catalog](#skill-catalog)).
3. Run context assembly only if the skill reads `_context/` or `_assets/`.
4. Execute the skill steps; confirm `[run-debug]` lines appear when the skill asks for them.
5. Confirm `[run-debug]` lines appear — they are the agent's execution trace.

**Good first runs (low risk):**

- [fetch_url](_workflows/ops/fetch_url/SKILL.md) — no LLM, validates network + workspace root
- [google_doc_to_markdown](_workflows/ops/google_doc_to_markdown/SKILL.md) — validates Google OAuth
- [evaluate_content](_workflows/ops/evaluate_content/SKILL.md) — validates brain + LLM wiring

---

## Building on this repo

This is a standalone starter you own end to end. Typical paths:

| Goal | What to do |
|------|------------|
| **Run shipped skills** | Clone, configure, pick a skill from [I want to…](#i-want-to) |
| **Add your brand** | Replace `_context/` with your messaging canon; keep the same file roles |
| **Add a custom pipeline** | Create `_workflows/{edit\|generate\|ops}/{your_pipeline}/SKILL.md`; link to shipped skills — do not copy their steps |
| **Add a new atomic skill** | Add under `_workflows/ops/` (or the right category) |
| **Sync live site copy** | Maintain `external_assets.md` and run [sync_assets](setup/sync_assets/SKILL.md) |

Shipped skills in `_workflows/` are the canonical implementations. Your custom orchestrators should link down to them. If you improve a shared skill, contribute it back upstream so others benefit.

---

## Credentials

### Rules

- **Runtime lookups start at `{workspace_root}/credentials.json` only.**
- Do not commit populated credential files.
- Put non-secrets in `config.json`.

### Reference syntax

```text
@relative/path/to/credentials.json#dotted.key.path
```

Example: `@secrets/vendor-keys.json#google.oauth_token_unified`

Paths are relative to `workspace_root`. Inline values override references. Procedure: [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).

### Google OAuth

Most Google skills need `google.oauth_token_unified` with scopes in [setup/credentials.example.json](setup/credentials.example.json).

1. Create OAuth **Desktop** client in Google Cloud Console → `google.oauth_installed_client`.
2. Run installed-app flow → `google.oauth_token_unified`.

### Keys by skill (common)

| Skill area | Credential paths |
|------------|------------------|
| Google Docs / Sheets / Drive | `google.oauth_token_unified` |
| FAQ finder (GSC) | `google.oauth_token_unified` (+ optional `_2`) |
| FAQ finder (Reddit/LinkedIn) | `serpapi.api_key` |
| LLM steps | `anthropic.api_key`, `gemini.api_key` |
| Browser automation | `browserbase.api_key` when enabled in config |
| Webflow publish | `webflow.api_token` |

---

## Config vs credentials

| File | Committed? | Contents |
|------|------------|----------|
| `config.json` | Yes | IDs, URLs, models, `repo.url`, `browserbase.enabled` |
| `credentials.json` | No | API keys, tokens, OAuth bundles |
| `credentials.example.json` | Yes | Key shapes — no secrets |

Templates: [setup/config.example.json](setup/config.example.json), [setup/credentials.example.json](setup/credentials.example.json).

---

## How to run a skill

1. **Step 0** — [run_workflow/SKILL.md](setup/run_workflow/SKILL.md)
2. **Read the skill** — `_workflows/{category}/{name}/SKILL.md`
3. **Resolve workspace root** — directory containing `config.json`
4. **Context assembly** — when the skill reads canon, ensure `_context/` / `_assets/` are ready
5. **Execute** — small steps, `[run-debug]` logging
6. **End of run** — update `"last run"` in skill frontmatter (ISO date)

**Editorial markup pipeline:**

```
[your _workflows/ pipeline or plan JSON]
        ↓  inline-markup-plan.json
show_edits_in_google_doc  →  human review in Google Doc
        ↓
accept_edits_google_doc   →  finalized Doc
```

**Typical agentic content loop:**

```
research/find_faq_questions  →  sheet of questions
generate/generate_faq_responses  →  drafted answers
ops/evaluate_content  →  canon conformance check
ops/show_edits_in_google_doc  →  human review
ops/publish_wordpress_from_google_doc  →  live draft
```

Compose loops like this in `_workflows/` entry skills; link to shipped skills for each phase.

---

## Skill catalog

Grouped catalog: [_workflows/README.md](_workflows/README.md).

| Category | Skills |
|----------|--------|
| **edit** | [update_agent](_workflows/edit/update_agent/SKILL.md) — shared page-refresh pipeline |
| **research** | [find_faq_questions](_workflows/research/find_faq_questions/SKILL.md), [evaluate_external_brand](_workflows/research/evaluate_external_brand/SKILL.md), [build_crosslinks](_workflows/research/build_crosslinks/SKILL.md) |
| **generate** | [generate_faq_responses](_workflows/generate/generate_faq_responses/SKILL.md) |
| **ops** | [fetch_url](_workflows/ops/fetch_url/SKILL.md), [write_google_sheet](_workflows/ops/write_google_sheet/SKILL.md), [markdown_to_google_doc](_workflows/ops/markdown_to_google_doc/SKILL.md), [google_doc_to_markdown](_workflows/ops/google_doc_to_markdown/SKILL.md), [show_edits_in_google_doc](_workflows/ops/show_edits_in_google_doc/SKILL.md), [accept_edits_google_doc](_workflows/ops/accept_edits_google_doc/SKILL.md), [evaluate_content](_workflows/ops/evaluate_content/SKILL.md), [publish_wordpress_from_google_doc](_workflows/ops/publish_wordpress_from_google_doc/SKILL.md), [youtube_transcription](_workflows/ops/youtube_transcription/SKILL.md), [wikitext_editing](_workflows/ops/wikitext_editing/SKILL.md), [browser_automation](_workflows/ops/browser_automation/SKILL.md) |

### Roadmap (not shipped yet)

Documented in maintain docs but **no `SKILL.md` in this repo yet**:

- `_workflows/stage_content` — CMS publish router (add under `_workflows/` when you need it)
- Suggest/propose edit orchestrators, standalone `converters/` utility folder

Do not link agents to these until the skill files exist.

---

## Organization principles

### Folder layout

```
<repo-root>/
├── README.md
├── config.json
├── credentials.json              (gitignored)
├── _context/                     messaging canon (Gallivant demo → replace)
├── _assets/                      materialized copy (optional; see sync_assets)
├── external_assets.md            optional registry for sync_assets
├── _workflows/                   skills by category (see _workflows/README.md)
│   ├── edit/ research/ generate/ ops/
├── setup/                        config templates, run_workflow, maintain_*, sync_assets
│   ├── run_workflow/             Step 0 contract
│   ├── sync_assets/
│   ├── maintain_skills/
│   ├── maintain_workflows/
│   ├── config.example.json
│   └── credentials.example.json
```

### Ephemeral data

Scratch files **only** in directories named `tmp/`. Gitignore `**/tmp/` (see [`.gitignore`](.gitignore)).

### Skills and references

- **Shipped skills:** `_workflows/{category}/{name}/SKILL.md` — link from custom orchestrators; do not fork.
- **Custom pipelines:** add `_workflows/{edit|generate|ops}/{your_pipeline}/SKILL.md` and link to shipped skills below; do not copy their steps.
- Every step starts with Step 0: [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).
- Say each instruction once — link to canonical skills ([setup/maintain_skills/SKILL.md](setup/maintain_skills/SKILL.md)).

### sync_assets

Before skills read materialized copy, run [setup/sync_assets/SKILL.md](setup/sync_assets/SKILL.md) to populate `{workspace_root}/_assets/` from `external_assets.md` and local paths. See [run_workflow/SKILL.md § Context assembly](setup/run_workflow/SKILL.md).

### Repo hygiene

Do not commit:

- Populated `credentials.json`
- Anything under `**/tmp/`
- Local Python envs (`**/.venv/`)

---

## For Claude Code and Cursor

- Register skills under `_workflows/`.
- Point `CLAUDE.md` or a Cursor rule at this **README** and [run_workflow/SKILL.md](setup/run_workflow/SKILL.md).
- Browserbase: [_workflows/browser_automation](_workflows/ops/browser_automation/SKILL.md) — repeat the live session URL while the session is open.
- When starting a content task, tell the agent: workspace root path, target skill path, and which canon layer is active (demo Gallivant vs production `_context/`).

---

## Maintenance

See [setup/maintain_skills/SKILL.md](setup/maintain_skills/SKILL.md) and [setup/maintain_workflows/SKILL.md](setup/maintain_workflows/SKILL.md).

---

## Troubleshooting

| Symptom | Check |
|---------|--------|
| `credentials.json` not found | File at repo root next to `config.json` |
| Google 403 / invalid_grant | OAuth scopes; re-run token flow |
| Script cannot find workspace | Run from repo root |
| Skill not found | Look under `_workflows/{category}/{name}/` — see [_workflows/README.md](_workflows/README.md) |
| Canon ignored | Replace `_context/` at repo root for production |
| Agent output off-brand | Confirm context assembly ran; check `_context/` trust levels in [_context/README.md](_context/README.md) |

---

## Example context

[_context/](_context/README.md) ships **fictional Gallivant** messaging. Replace with real canon for production work.

Gallivant is an enterprise travel-and-expense company invented for demos. Use it to:

- See how canon files (`canon-*.md`, `brand-writing-identity.md`) constrain generation
- Run [evaluate_content](_workflows/ops/evaluate_content/SKILL.md) against known-good and known-bad samples
- Practice the editorial markup pipeline without touching a real CMS

When you are ready for production, swap `_context/` for your company's messaging brain and keep the same hands.
