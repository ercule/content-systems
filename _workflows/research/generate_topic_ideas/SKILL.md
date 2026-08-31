---
name: generate_topic_ideas
description: >-
  Researches a brand, competitors, and category trends, then writes 30–45
  unbranded 1–4 word topics with one tag and a 0–5 relevance score to a
  markdown file. Use when the user asks to generate topic ideas or run
  topic research for a brand.
"last updated": 2026-08-31T03:45:00+00:00
"last run": 2026-08-30
---

# Generate topic ideas

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Keep helper code ephemeral for this run only and remove it before finishing.

Log line prefix:

```text
[run-debug] workflow=_workflows/generate_topic_ideas | <PHASE> | <facts>
```

## Inputs

- `workspace_root`: optional. Repo root used to merge `{workspace_root}/credentials.json` and to derive brand fields from `{workspace_root}/config.json`.
- `brand_title`: optional. Display name used in research. If omitted, resolve from `{workspace_root}/config.json` `workspace_name`, then confirm with the user.
- `brand_domain`: optional. Apex host. If omitted, resolve from `{workspace_root}/config.json` (`main_domain`, `domain`, or `workspace_domains`), then confirm with the user.
- `output_path`: optional. Markdown file to write. Default `{workspace_root}/_context/topic-ideas.md`.
- `research_model`: optional. Default `claude-sonnet-4-6` (root `config.json` at `anthropic.model_smart`). Must be a model on the permitted list in root `config.json`.

Take brand title and domain from chat or from a workspace wrapper skill. Resolve those values at run time.

## Credentials

Read credentials from `{workspace_root}/credentials.json` (resolve `@ref` per run_workflow). When a workspace wrapper calls this skill, merge wrapper credentials over the root values only for that run.

- SerpAPI key: `serpapi.api_key`.
- Anthropic key for draft and score: `anthropic.api_key`.

Log credential names and hosts only.

## Output contract

Each topic is one object:

- `topic`: unbranded conceptual hub, 1–4 words, lowercase
- `tag`: one of 4–7 topical tags defined for this brand, lowercase
- `relevance`: integer 0–5

Write 30–45 of those objects to `{output_path}` as markdown (heading, brand, domain, category, then one bullet per topic: `topic — tag — relevance`). Also write the same rows as JSON next to that file, same stem, `.json` suffix.

## Topic quality rules

These rules apply to every row before it is written, in step 03:

- Length: 1–4 words, preferably 1–2. Letters and numbers only, plus punctuation that is part of a technical term.
- Form: unbranded conceptual hubs. Each topic can host many long-tail queries. Use category language only.
- Case: Topic and Tag are lowercase.
- Tags: 4–7 short human-readable phrases (examples of tag style: `core data`, `analytics`, `supply chain`, `category & assortment`, `promotion & media`, `ai & agents`, `people & culture`). Each topic gets exactly one tag. Use each tag on multiple topics.
- Relevance: 5 = core to the brand's product and main narrative; 4 = very important, strong adjacency; 3 = relevant but supporting; 2 = tangential or niche; 1–0 = weak.
- Count: 30–45 rows after prune. Draft 50–70 candidates, then merge near-duplicates and drop topics that are too generic, too long-tail, or only weakly connected to the brand.

## Run order

Run these child skills in order:

1. [01_preflight/SKILL.md](01_preflight/SKILL.md) — verify credentials, brand inputs, and output path.
2. [02_research/SKILL.md](02_research/SKILL.md) — brand, competitor, and category-trend notes.
3. [03_draft_and_score/SKILL.md](03_draft_and_score/SKILL.md) — draft, prune, tag, and score topics.
4. [04_output/SKILL.md](04_output/SKILL.md) — write markdown and JSON.

Wipe `{workspace_root}/tmp/generate_topic_ideas/` at the start of the run. Write step intermediates there. Wipe that folder again after step 04 succeeds.

The end state is 30–45 scored topics on disk at `{output_path}`. No website pages are edited.

## Logging template

```text
[run-debug] workflow=_workflows/generate_topic_ideas | START | brand="{brand_title}" domain={brand_domain}
[run-debug] workflow=_workflows/generate_topic_ideas | PREFLIGHT | ok brand="{brand_title}" domain={brand_domain}
[run-debug] workflow=_workflows/generate_topic_ideas | RESEARCH | brand_pages=N competitors=N trend_queries=N
[run-debug] workflow=_workflows/generate_topic_ideas | DRAFT | candidates=N kept=N tags=N
[run-debug] workflow=_workflows/generate_topic_ideas | OUTPUT | path={output_path} rows=N
[run-debug] workflow=_workflows/generate_topic_ideas | DONE | rows=N path={output_path}
```

## Checklist

```text
Task Progress:
- [ ] brand_title and brand_domain confirmed
- [ ] output_path resolved
- [ ] [01_preflight/SKILL.md](01_preflight/SKILL.md) completed
- [ ] [02_research/SKILL.md](02_research/SKILL.md) completed
- [ ] [03_draft_and_score/SKILL.md](03_draft_and_score/SKILL.md) completed
- [ ] [04_output/SKILL.md](04_output/SKILL.md) completed
- [ ] Final summary includes row count, tag list, and output path
```
