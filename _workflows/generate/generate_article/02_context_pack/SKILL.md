---
name: generate_article_02_context_pack
description: >-
  Step 02: create a run folder and copy workspace context into it verbatim.
  Keep an existing folder that already has a prompt pack.
"last updated": 2026-08-16T05:30:00+00:00
"last run": never
---

# Generate article — 02 Context pack

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../01_preflight/SKILL.md](../01_preflight/SKILL.md) has passed in this run. `title` and `id-or-slug` must be set.

## Reuse an existing pack folder

When `RUN_DIR` already contains `context/` and `prompt-pack.md`, keep that folder. Leave the copies as they are. Do not delete `tmp/generate_article/{id-or-slug}/`. Go to [../03_research/SKILL.md](../03_research/SKILL.md).

## New folder

When there is no pack folder, create one.

## 1. Sync assets

Run [sync_assets](../../../../setup/sync_assets/SKILL.md) from the workspace root (context assembly in run_workflow).

## 2. Remove leftover tmp for this slug

Under `tmp/generate_article/{id-or-slug}/`, delete timestamp folders that contain neither `prompt-pack.md` nor `prompt-pack.approved`. Never delete a folder that contains either of those files.

## 3. Create a new run folder

Create `tmp/generate_article/{id-or-slug}/{YYYYMMDD-HHMMSSZ}/` under the workspace root. Call that path `RUN_DIR`. Create `RUN_DIR/context/` inside it.

## 4. Copy relevant context, verbatim

Copy files as-is (same bytes, same filenames). Keep relative links working by preserving each source folder's layout.

From `_context/`, copy into `RUN_DIR/context/`:

- `README.md`
- `messaging-canon.md`
- every `canon-*.md`
- `brand-writing-identity.md`, `brand-visual-identity.md`
- `content-index.md`
- `reference/` when it exists
- any other files at the `_context/` top level (voice, style, writing rules, brand, article template, and similar)

From `_assets/`, copy into `RUN_DIR/context/assets/`:

- `asset-manifest.md` when it exists
- every synced text file the manifest lists (voice, naming, structure, and other approved reference copy)

Log: `[run-debug] workflow=_workflows/generate/generate_article | CONTEXT | files={count} run_dir={RUN_DIR}`

Next: [../03_research/SKILL.md](../03_research/SKILL.md)
