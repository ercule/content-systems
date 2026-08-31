---
name: generate_topic_ideas_03_draft_and_score
description: >-
  Step 03 for generate_topic_ideas: draft, prune, tag, and score 30–45
  unbranded topics from the research notes.
"last updated": 2026-08-31T03:45:00+00:00
"last run": 2026-08-30
---

# Generate topic ideas — 03 Draft and score

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Read `{workspace_root}/tmp/generate_topic_ideas/research_notes.md` from [../02_research/SKILL.md](../02_research/SKILL.md). Apply the topic quality rules on the [orchestrator](../SKILL.md#topic-quality-rules). Produce the topic rows here; writing files is [../04_output/SKILL.md](../04_output/SKILL.md).

## Inputs

- Research notes from step 02
- `brand_title`, `brand_domain` from preflight
- `research_model`: optional. Default `claude-sonnet-4-6` (`config.json` at `anthropic.model_smart`)

## Credentials

- Anthropic: `{workspace_root}/credentials.json` at `anthropic.api_key`

Call the model with the research notes as context. The running agent may perform this step directly when the notes already fit in context; use an isolated model call when the notes are long or the user passed `research_model`.

## STEP 4 — Draft topic candidates

Using the notes from Steps 1–3, generate 50–70 candidate topics:

- 1–4 words each, unbranded
- Broad enough to host multiple long-tail queries
- Clearly relevant to the brand's product, use cases, or audience
- Natural sounding, no longer than 4 words. Letters and numbers only, except punctuation that is part of a technical term
- Specific enough that they read as this category, not an unrelated field

Output as a flat list of topics, one per line.

## STEP 5 — Refine and prune

Refine the 50–70 candidates down to 30–45 strong topics by:

- Merging near-duplicates and choosing the clearest label
- Dropping topics that are too generic or too long-tail
- Keeping only topics where the brand has a clear, credible connection
- Keeping every topic at 1–4 words and unbranded

Output: the refined list of 30–45 topics, one per line.

## STEP 6 — Define tags and assign one tag per topic

Define 4–7 high-level topical tags that capture the main areas for this brand. Examples of tag styles: `core data`, `analytics`, `supply chain`, `category & assortment`, `promotion & media`, `ai & agents`, `people & culture`.

Tags:

- Short, human-readable phrases (no camelCase)
- Topic-based (category language only)

Assign exactly one of these tags to each topic. Use each tag on multiple topics.

Output Topic and Tag pairs, one per line.

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
- 1–4 words per topic; skip empty rows and branded names
- keep 30–45 rows; if the count is outside that range, prune or fill from leftover candidates once

Save `{workspace_root}/tmp/generate_topic_ideas/topics.json` as a JSON array:

```json
[
  { "topic": "remote debugging", "tag": "dev tools", "relevance": 5 }
]
```

Log: `[run-debug] workflow=_workflows/generate_topic_ideas | DRAFT | candidates=N kept=N tags=N`

Next: [../04_output/SKILL.md](../04_output/SKILL.md)
