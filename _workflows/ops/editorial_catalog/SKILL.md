---
name: editorial_catalog
description: >-
  Detect AI-tell patterns and mechanical/house-style issues in a manuscript in one
  pass and write a single combined catalog. Contains the full shared rule lists.
  Report findings only; does not rewrite. Use from generate_article before
  editorial_replace.
"last updated": 2026-10-26
"last run": 
---

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

# Editorial catalog

Detect only. The manuscript stays as is. The catalog feeds [editorial_replace](../editorial_replace/SKILL.md).

Run every list below against the same manuscript in one pass. Do not stop at the first match, and do not dedupe across lists: a line that breaks two rules gets one row per rule. Skip matches inside URLs, code, and quoted examples.

## Style guide permissions win

The workspace's style guide lives in its style catalog and style update steps (`_workflows/ops/style_catalog/SKILL.md` and `_workflows/ops/style_update/SKILL.md`). If that guide explicitly allows, requires, or defines something that a rule below would flag (a punctuation mark, heading case, a bold or italic rule, second person, a required string, a term), do not catalog it. The style guide's own rules are the style catalog's job, not this one. Do not invent permissions the guide does not state.

## AI patterns

Source label: `AI pattern`.

- Binary contrasts (`It's not X. It's Y.` / `not just X but Y.` / `stops being X and starts being Y.` / `The question isn't X, it's Y.`)
- Negative listing (`Not a X. Not a Y. A Z.`)
- Throat-clearing openers (`Here's the thing,` `Here's what...` `That's what...` `Let me be clear,` `It turns out`)
- Faux-insight setups (`What most people get wrong` / `Here's what nobody tells you`)
- Colon reveals (noun phrase + colon + dramatic lowercase reveal)
- Superficial `-ing` analysis (`highlighting,` `underscoring,` `showcasing,` `reflecting`)
- Importance puffery (`stands as a testament` / `plays a vital role` / `marks a pivotal moment`)
- Interpretive metadiscourse (`the key point is` / `as you can see` / `this distinction matters`)
- Vague declaratives (`the reasons are structural` / `the stakes are high`)
- Says nothing about (`says nothing about`)
- Weasel attribution (`experts agree` / `studies show` / `industry reports suggest`)
- Fake-strong verbs (`serves as a centralized hub for`)
- Synonym cycling (rotating terms instead of repeating the clear word)
- Dramatic fragmentation (`X. And Y. And Z.` / `That's it. That's the whole thing.`)
- Rhetorical setups (`What if I told you` / `Think about it:` / self-answered Q&A)
- Fake-profound kickers and summary-recap endings (`In conclusion,` `Ultimately,` `Overall,` `To summarize`)
- Robotic rhythm (repeated sentence shapes, stacked punchy fragments)
- Narrator from a distance (`nobody` / `people` where `you` fits an intro, how-to step, or CTA)
- Formatting slop (emoji headings, mid-sentence bold, headers over two-sentence sections)
- Banned words: delve, foster, leverage, utilize, facilitate, empower, streamline, robust, cutting-edge, paradigm, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness, ever-evolving, best-in-class, seamless, powerful, unlock (as metaphor), stays, meters, shapes
- Empty jargon: navigate, unpack, lean into, landscape, deep dive, double down, circle back, let's dive in, at its core
- Empty adverbs and phrases: just, really, actually, it's worth noting, in today's world/landscape/environment, at the end of the day, this is particularly important because, `Whether you're an X or a Y`, `this allows teams to` (delete "this allows" and restructure)
- Stacked adjectives before a noun (`scalable, reliable, high-performance streaming pipeline`), multiple abstract nouns in one sentence, and empty transition phrases
- Portable filler (a sentence that could move unchanged to another company)
- Clock-time scenes (`At 2 a.m., an analyst sees an alert that points to a credential misused months ago.` / `At 3 a.m.,` and the same shape with any hour)
- Nominal relatives and clausal objects. A nominal relative is a wh-clause with no noun head that fills a noun slot (`what remains queryable`, `who runs the platform`, `how they are priced`, `whatever denominator finance uses`, `what to track`). A clausal object is a finite clause used as a verb's object: an embedded question after ask, confirm, show, decide, or test (`ask whether older data feeds the same dashboards`, `ask what gets sampled`), or a that-clause, including a dropped that (`says every unique combination creates a new series`, `means an agent can spend`). Replace the clause with a noun phrase that names the thing (`the evidence that remains queryable`, `the pre-storage drop list`). One catalog row per clause. Leave direct questions alone (inversion, FAQ headings, numbered question lists), ordinary relatives with a noun head (`a field you didn't index`), adverbial whether (`whether it's the console or an agent`), and infinitives (`ask the vendor to answer`).
- Tricola: three parallel beats used as a slogan. Rewrite as a plain statement or a non-parallel construction.
- Software personification: software, a product, or a feature as the subject of a human verb. Rewrite so a person, a team, or the mechanism is the subject.

## Mechanical and house style

Source label: `Mechanical`.

- Headings use `#` through `######` with a space after the hashes. Turn bold-only lines that are clearly section titles into real headings.
- Body headings (H2 and below) are sentence case except proper nouns, acronyms, and product names. H1 case follows the style guide.
- Headings are 3 to 12 words, carry no trademark symbols (™, ®, ©), and have no inline bold. Standard component headings (Key takeaways, TL;DR, FAQs, Next steps, Related Reading) may be shorter.
- Replace image tags and Markdown image syntax with the literal token `[image]` on its own line.
- No em dashes (`—`), en dashes (`–`), or double hyphens (`--`) in prose. Replace with a comma, period, colon, parentheses, or a hyphen.
- No inline `**bold**` in body prose, list items, or FAQ answers. Headings stay headings.
- No horizontal rules (`---`) in the body.
- Rewrite these words and constructions, keeping the meaning:
  - "actual", "actually" (including "in actual practice")
  - "quiet", "quietly", "silent", "silently"
  - "gap", "gaps" (including "the real gaps")
  - "structural", "structurally"
  - "architecture", "shift", "realities"
  - "bar" as a metaphor (`the bar`, `uniqueness bar`; leave the UI "search bar")
  - metaphor "break", "breaks", "breaking", "broke" (`breaks at scale`); keep literal uses such as a line break or protocol break
  - "not just" and "do this, not that" constructions
  - *name* tics: imperative "Name the…", "is named", "a product called", "namely" (keep ordinary nouns such as domain name, metric name, file name, and product names)
  - adverb forms of the words above
- No `etc.` in body copy (be specific or use "and more"). No "click here" or "read more".
- Serial comma. US English (color, analyze, organization).
- No first-person singular ("I").
- Quote a new technical term on first use, then use it plainly. Spell out an acronym on first use unless it is a house abbreviation the style guide lists.
- Links:
  - Every required first-party URL from the crosslinks or sidecar file stays in running prose with its destination unchanged. Treat sidecar anchor text as a suggestion.
  - Link text is words the sentence would still say if the link were deleted. Flag a page title, a product name used as a citation, a source label (`according to`, `cited in`, `per`, `via`, `see [destination]`, `from X`, `outlined at`), or a raw URL as link text. Flag a link that starts a sentence and a sentence that exists only to hold a link. Move the URL onto words the sentence already needs.
  - Descriptive link text only: name the destination's topic. No raw URLs in prose.
  - No competitor links, including competitor content on third-party domains.

## Input

The manuscript: `{RUN_DIR}/{id-or-slug}.md` during generate_article, otherwise the path the caller names.

## Output

Write one combined catalog and paste the same table in chat:

- During generate_article: `{RUN_DIR}/{id-or-slug}-editorial-catalog.md`.
- Otherwise: `{stem}-editorial-catalog.md` next to the manuscript.

Columns: `Pattern` | `Instance` | `Suggested fix` | `Source`.

- One row per instance.
- Quote the exact line in `Instance`.
- Put a short rewrite in `Suggested fix`.
- `Source` is `AI pattern` or `Mechanical`.

If nothing matches, write `Findings: none`.

Log: `[run-debug] workflow=_workflows/ops/editorial_catalog | CATALOG | path=… rows=n`

## Related

- [editorial_replace](../editorial_replace/SKILL.md)
