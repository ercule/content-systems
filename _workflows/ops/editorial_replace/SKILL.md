---
name: editorial_replace
description: >-
  Apply a combined editorial catalog (AI-tell patterns plus mechanical/house-style
  issues) to a manuscript. Overwrites the manuscript in place. Use from
  generate_article after editorial_catalog.
"last updated": 2026-10-26
"last run": 
---

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

# Editorial replace

Edit mode. Apply the catalog written by [editorial_catalog](../editorial_catalog/SKILL.md). The rule lists live in that skill.

## Style guide permissions win

If the workspace's style guide (`_workflows/ops/style_catalog/SKILL.md` and `_workflows/ops/style_update/SKILL.md`) explicitly allows or requires something a catalog row asks you to change, leave it as is and say so in **What changed**. Do not invent permissions the guide does not state.

## Input

- The manuscript: `{RUN_DIR}/{id-or-slug}.md` during generate_article, otherwise the path the caller names.
- The catalog: `{RUN_DIR}/{id-or-slug}-editorial-catalog.md`, or `{stem}-editorial-catalog.md` next to the manuscript. If the catalog is missing, run [editorial_catalog](../editorial_catalog/SKILL.md) once, then continue.

## Steps

1. If the catalog is `Findings: none`, leave the manuscript unchanged and report that.
2. Apply every **Suggested fix** row with the minimum effective edit. Leave strong human sentences alone.
3. Keep the writer's meaning. Use only claims, stats, quotes, and links already in the manuscript, the context pack, or the research notes.
4. Grep-verify leftover hits against the "Mechanical and house style" list in editorial_catalog. Skip URLs, code, and quoted examples. Fix any remaining hit before returning.
5. Overwrite the manuscript with the full document, from the H1 through the last section. Return the complete file. Save the reply only when it keeps every heading, every required first-party URL the caller names, and every close section already in the manuscript (FAQs, related reading, or the CTA). If anything is missing, leave the saved manuscript unchanged and ask for the whole manuscript again.
6. Report a short **What changed** section, with findings as labeled severities.

Preserve every required first-party URL the caller names, with its destination unchanged. Spell product names exactly as the workspace's context files do.

Log: `[run-debug] workflow=_workflows/ops/editorial_replace | REPLACE | path=… applied=n`

## Related

- [editorial_catalog](../editorial_catalog/SKILL.md)
