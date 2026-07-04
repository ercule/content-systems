---
name: update_agent_04_build_crosslinks
description: >-
  Shared update agent step 4: delegate to build_crosslinks for target keyword
  and crosslink list used during regeneration.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Update agent — 04 Build crosslinks

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Run [../../../research/build_crosslinks/SKILL.md](../../../research/build_crosslinks/SKILL.md) with:

- `workspace_root`
- `source_html` or `source_markdown`
- `source_title`
- `source_url`
- `target_keyword` when supplied in step 02

Carry forward: `target_keyword`, `crosslinks`, `crosslinks_text`.

Next: [../05_regenerate/SKILL.md](../05_regenerate/SKILL.md)
