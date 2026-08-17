---
name: generate_topic_ideas_03_draft_and_score
description: >-
  Step 03 for generate_topic_ideas: draft, prune, tag, and score 30–45
  unbranded topics from the research notes.
"last updated": 2026-08-16T00:00:00+00:00
"last run": 2026-08-16
---

# Generate topic ideas — 03 Draft and score

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Read `{workspace_root}/tmp/generate_topic_ideas/research_notes.md` from [../02_research/SKILL.md](../02_research/SKILL.md). Apply the topic quality rules on the [orchestrator](../SKILL.md#topic-quality-rules). Produce the sheet rows here; writing the tab is [../04_write_sheet/SKILL.md](../04_write_sheet/SKILL.md).

## Inputs

- Research notes from step 02
- `brand_title`, `brand_domain` from preflight
- `research_model` — optional. Default `claude-sonnet-4-6` (`config.json` at `anthropic.model_smart`)

## Credentials

- Anthropic: `{workspace_root}/credentials.json` at `anthropic.api_key`

Call the model with the research notes as context. The running agent may perform this step directly when the notes already fit in context; use an isolated model call when the notes are long or the user passed `research_model`.

## STEP 4 — Draft topic candidates

Using the notes from Steps 1–3, generate 50–70 candidate topics:

- 1–4 words each, unbranded
- Broad enough to host multiple long-tail queries
- Clearly relevant to the brand's product, use cases, or audience
- Marketing slogans and ultra-generic terms stay off the list
- Natural sounding, no longer than 4 words. Characters other than letters and numbers stay off the list, except punctuation that is directly relevant to a technical topic
- Topics feel natural rather than stilted or compacted
- Relevant to the brand and industry, specific enough that they are not misconstrued as something unrelated

Output as a flat list of topics, one per line.

## STEP 5 — Refine and prune

Refine the 50–70 candidates down to 30–45 strong topics by:

- Merging near-duplicates and choosing the clearest label
- Removing topics that are too generic or too long-tail
- Keeping only topics where the brand has a clear, credible connection
- Ensuring all topics are 1–4 words and unbranded

Output: the refined list of 30–45 topics, one per line.

## STEP 6 — Define tags and assign one tag per topic

Define 4–7 high-level topical tags that capture the main areas for this brand. Examples of tag styles: `core data`, `analytics`, `supply chain`, `category & assortment`, `promotion & media`, `ai & agents`, `people & culture`.

Tags:

- Short, human-readable phrases (no camelCase)
- Topic-based (brand names stay off tags)

Assign exactly one of these tags to each topic. Use each tag on multiple topics when possible.

Output a two-column table: Topic, Tag.

## STEP 7 — Score topic relevance (0–5)

For each topic, assign a Relevance score:

- 5 = Core to the brand's product and main narrative
- 4 = Very important, strong adjacency
- 3 = Relevant but more supporting
- 2 = Tangential / niche
- 1–0 = Very weak or irrelevant (only if needed)

Consider both current positioning and strategic areas the brand should own in SEO/AEO/GEO.

## Parse and validate

Normalize every row:

- `topic` and `tag` lowercase, trimmed
- `relevance` integer 0–5
- drop empty topics, branded names, and rows outside 1–4 words
- keep 30–45 rows; if the count is outside that range, prune or fill from leftover candidates once

Save `{workspace_root}/tmp/generate_topic_ideas/topics.json` as a JSON array:

```json
[
  { "topic": "remote debugging", "tag": "dev tools", "relevance": 5 }
]
```

Log: `[run-debug] workflow=_workflows/generate_topic_ideas | DRAFT | candidates=N kept=N tags=N`

Next: [../04_write_sheet/SKILL.md](../04_write_sheet/SKILL.md)
