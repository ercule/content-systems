---
name: generate_article_08_mechanical_rewrites
description: >-
  Step 08: apply the mechanical catalog and overwrite the manuscript.
"last updated": 2026-09-20
"last run": 2026-09-20
---

# Generate article — 08 Mechanical rewrites

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Start this step after [../07_mechanical_catalog/SKILL.md](../07_mechanical_catalog/SKILL.md). Require `{id-or-slug}.md` and `{id-or-slug}-mechanical-catalog.md` in `RUN_DIR`. If either is missing, list them and end the run.

This skill is **Edit**. Apply every **Suggested fix** row in the catalog. If the catalog is `Findings: none`, leave the manuscript unchanged. Grep-verify leftover checklist hits from [../07_mechanical_catalog/SKILL.md](../07_mechanical_catalog/SKILL.md) (skip URLs, code, and quoted examples).

Overwrite `{id-or-slug}.md` in `RUN_DIR`.

Log: `[run-debug] workflow=_workflows/generate/generate_article | REWRITE | ok path={RUN_DIR}/{id-or-slug}.md`

Next: [../09_output/SKILL.md](../09_output/SKILL.md)
