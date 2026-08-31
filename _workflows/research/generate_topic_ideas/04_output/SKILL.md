---
name: generate_topic_ideas_04_output
description: >-
  Step 04 for generate_topic_ideas: write scored topics to markdown and JSON
  files.
"last updated": 2026-08-31T03:45:00+00:00
"last run": 2026-08-30
---

# Generate topic ideas — 04 Output

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

This step writes the scored topic list to disk and replaces any file already at `{output_path}`.

## Inputs

From [../01_preflight/SKILL.md](../01_preflight/SKILL.md):

- `brand_title`
- `brand_domain`
- `output_path`
- `{workspace_root}/tmp/generate_topic_ideas/research_notes.md` (category line at the top)

From [../03_draft_and_score/SKILL.md](../03_draft_and_score/SKILL.md):

- `{workspace_root}/tmp/generate_topic_ideas/topics.json`

## 1. Build the markdown

Read `topics.json`. Read the category string from the top of `research_notes.md`.

Write `{output_path}` as markdown:

```markdown
# Topic ideas — {brand_title}

Domain: {brand_domain}
Category: {category}

- {topic} — {tag} — {relevance}
```

One bullet per topic, in the same order as `topics.json`.

## 2. Write JSON beside it

Write the same array to a `.json` file with the same directory and stem as `{output_path}` (for `{workspace_root}/_context/topic-ideas.md`, write `{workspace_root}/_context/topic-ideas.json`).

Expect the parent directory to exist from preflight. Create it if it is missing.

## 3. Cleanup

Wipe `{workspace_root}/tmp/generate_topic_ideas/` after a successful write.

Log:

```text
[run-debug] workflow=_workflows/generate_topic_ideas | OUTPUT | path={output_path} rows=N
[run-debug] workflow=_workflows/generate_topic_ideas | DONE | rows=N path={output_path}
```

End of run: [run_workflow](../../../../setup/run_workflow/SKILL.md) § End of run. Update `"last run"` on every executed `SKILL.md` in this workflow to today's ISO date.
