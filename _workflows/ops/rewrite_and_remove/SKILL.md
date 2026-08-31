---
name: rewrite_and_remove
description: >-
  Independent ops helper: catalog every AI-tell and filler hit in a Markdown
  draft, then rewrite each catalog row in place. Callers name the draft path.
"last updated": 2026-08-29T20:42:00+00:00
"last run": never
---

# Rewrite and remove

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=_workflows/ops/rewrite_and_remove | <PHASE> | <facts>`

This skill is a shared helper. Callers name the draft. It is not a step in generate_article or any other pipeline unless that pipeline links here.

## Input

- `draft_path` (required): Markdown file to scan and overwrite. The caller names this path. If it is missing, ask for it and stop.
- Extra pattern bullets (optional): the caller may append bullets to the list below. Treat those the same as the shared list.

## Output

- Catalog: write `{draft_stem}-rewrite-and-remove-catalog.md` in the same folder as `draft_path`. `{draft_stem}` is the filename without `.md`.
- Draft: after task 2, overwrite `draft_path`.

Run both tasks in order. Stop after task 1 only when the caller asks for catalog-only.

## Task 1 — Catalog

Search headings and body prose in `draft_path` for every bullet under **Patterns**. Leave fenced code, inline code, URL strings, and verbatim quoted passages as they are.

Write the catalog file. One bullet per hit:

- Pattern: the matching bullet from **Patterns** (or a caller extra)
- Quote: the sentence or phrase as it appears in the draft
- Where: nearby heading, or "H1" / "opening" when there is no heading yet

If there are zero hits, write a catalog that says `No hits.` and stop. Log `CATALOG | hits=0 path={catalog_path}`.

Log: `[run-debug] workflow=_workflows/ops/rewrite_and_remove | CATALOG | hits={n} path={catalog_path}`

## Task 2 — Rewrite

Rewrite every catalog row in `draft_path`. Keep the same fact. Replace the quoted span so that row's pattern is gone. Overwrite `draft_path`.

Confirm each catalog quote is gone from the draft. Hits that were not in this catalog wait for a later run.

Log: `[run-debug] workflow=_workflows/ops/rewrite_and_remove | REWRITE | ok path={draft_path} catalog={catalog_path}`

## Cleanup

Keep the catalog file. This skill writes nothing under `tmp/`.

## Patterns

Rewrite and remove all:

- "It's not X, it's Y."
- "It's not just X, it's Y."
- "This isn't about X — it's about Y."
- "Not X. Not Y. But Z."
- "That's not X. That's Y."
- "The problem isn't X. The problem is Y."
- "X, not Y."
- "X doesn't do that. Y does."
- "A won't save you. B will."
- "never A. B is."
- "do this, not that"
- "What [X] is/does is [Y]"
- "What is left is…"
- "X is how you Y"
- "stop thinking X, start thinking Y"
- "You're not doing this, you're doing that"
- Staccato one-line paragraphs used for fake emphasis
- Staccato sentence pairs used more than once per piece ("The tools got faster. The maintenance didn't shrink.")
- Rule-of-three wallpaper ("Faster. Cheaper. Smarter." / "efficiency, scalability, and innovation." / lazy groups of three)
- "The result?"
- "The problem?"
- "The best part?"
- "Here's the kicker."
- "Here's the thing."
- Colon-punch lines ("The answer: better AI.")
- Colon-stacked headlines ("Signal-Based Marketing: A New Era.")
- Colon as fake drama
- Rhetorical questions in body copy or as section openers
- Symmetrical A/B parallels ("the person who X… the person who Y." / "the ones who A… the ones who B.")
- Aphoristic parallel closers ("X is the multiplier. The tools are a commodity.")
- Uniform metronomic rhythm (every sentence the same length and weight)
- Uniform 3–4 sentence paragraphs throughout
- "In today's fast-paced…"
- "In today's landscape/world/environment"
- "In an era of"
- "In a world where"
- "In the realm/world of"
- "As we navigate/embark…"
- "As the landscape evolves"
- "Now more than ever"
- "It's no secret that…"
- "It's worth noting that"
- "It's important to note"
- "This is particularly important because"
- "Needless to say"
- "At the end of the day"
- "Make no mistake"
- "The reality is" / "The truth is"
- "In this article, we'll…"
- "Let's explore" / "Let's dive in" / "Let's unpack"
- "This is where X comes in"
- "Whether you're a … or a …" / "Whether you're an X or a Y"
- "At its core"
- "navigating the complexities of"
- Overly apologetic meta ("we should be honest about what we're selling" / "this is the company blog, so obviously we believe…")
- "In conclusion"
- "To summarize" / "In summary"
- "The good news is" / "The bad news is"
- "Rest assured"
- "Look no further"
- "Stay ahead of the curve"
- "The future of X is bright"
- Empty "Key takeaways" recap that only restates the headings
- Soft wrap-up that re-explains a point already landed
- delve
- dive deep
- harness
- leverage (as a verb)
- utilize
- empower
- unlock (as metaphor / "unlock the power of" / "unlock insights")
- elevate
- supercharge
- foster
- facilitate
- streamline (without saying how)
- spearhead
- unpack
- navigate
- revolutionize
- "This allows teams to"
- seamless / seamlessly
- robust
- powerful
- cutting-edge
- state-of-the-art
- next-generation / next-gen / next-level
- best-in-class
- world-class
- game-changer
- needle-mover
- transformative
- revolutionary
- paradigm shift
- holistic
- scalable / end-to-end without specifics
- blazing-fast
- quietly / silently / structural (as filler)
- "quietly fails" / "quietly breaks" / "quietly winning" / "silently powerful"
- landscape
- ecosystem
- journey
- synergy
- "testament to"
- "speaks volumes"
- gaps (including "the real gaps")
- architecture
- shift
- realities
- pivotal / crucial / vital / essential
- exciting / thrilled
- "align stakeholders"
- "drive value" with no mechanism
- stacked adjectives before a noun ("scalable, reliable, high-performance … pipeline")
- multiple abstract nouns per sentence
- unattributed superlatives and absolutes ("only," "best," "always," "guarantee," "the gold standard," "100%," "definitively") unless sourced
- actually
- actual (including "in actual practice")
- really
- simply
- just
- literally
- basically
- essentially
- ultimately
- clearly
- obviously
- of course
- in fact
- indeed
- that said
- truly
- incredibly
- "not just"
- imperative "Name the…"
- "is named"
- "a product called"
- "namely"
- metaphor break / breaks / breaking / broke ("breaks at scale," "breaks list-price intuition")
- "click here"
- "read more"
- em dashes (Unicode —)
- en dashes used as rhythm or fake drama
- "Furthermore," / "Moreover," / "Additionally" as paragraph openers
- emoji as a closer or bullet decoration in body copy
- `etc.`
- Markdown image syntax and HTML `<img>` tags
- software personification ("X lets you," "X thinks," "X knows," "X wants")
