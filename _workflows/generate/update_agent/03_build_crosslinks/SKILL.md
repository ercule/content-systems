---
name: update_agent_03_build_crosslinks
description: >-
  Shared update agent step 3: delegate to build_crosslinks for target keyword
  and crosslink list used during regeneration.
"last updated": 2026-06-21T00:00:00+00:00
"last run": never
---

# Update agent — 03 Build crosslinks

Step 0: Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md).

Run [../../build_crosslinks/SKILL.md](../../build_crosslinks/SKILL.md) with:

- `workspace_root`
- `source_html` or `source_markdown`
- `source_title`
- `source_url`
- `target_keyword` when supplied in step 01

Carry forward: `target_keyword`, `crosslinks`, `crosslinks_text`.

Next: [../04-regenerate/SKILL.md](../04_regenerate/SKILL.md)
