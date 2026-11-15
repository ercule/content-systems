---
name: editorial_catalog
description: >-
  Detect AI-tell patterns and mechanical/house-style issues in a manuscript in one
  pass and write a single combined catalog. Contains the full shared rule lists.
  Report findings only; does not rewrite. Use from generate_article before
  editorial_replace.
"last updated": 2026-10-26
"last run": 2026-11-11
---

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

# Editorial catalog

Detect only. The manuscript stays as is. The catalog feeds [editorial_replace](../editorial_replace/SKILL.md).

Catalog occurrences of each of the patterns below. Be aggressive. Skip matches inside URLs, code, and quoted examples.

## AI patterns

Catalog each occurrence of the following patterns. Source label: `AI pattern`.

- Binary contrasts (`It's not X. It's Y.` / `not just X but Y.` / `stops being X and starts being Y.` / `The question isn't X, it's Y.`)
- Negative listing (`Not a X. Not a Y. A Z.`)
- Throat-clearing openers (`Here's the thing,` `Here's what...` `That's what...` `Let me be clear,` `It turns out`)
- Faux-insight setups (`What most people get wrong` / `Here's what nobody tells you`)
- Colon reveals (noun phrase + colon + dramatic lowercase reveal)
- Importance puffery (`stands as a testament` / `plays a vital role` / `marks a pivotal moment`)
- Interpretive language (`the key point is` / `as you can see` / `this distinction matters`)
- Vague declaratives (`the reasons are structural` / `the stakes are high`)
- Says nothing about (`says nothing about`)
- Weasel attribution (`experts agree` / `studies show` / `industry reports suggest`)
- Synonym cycling (rotating terms instead of repeating the clear word)
- Dramatic fragmentation (`X. And Y. And Z.` / `That's it. That's the whole thing.`)
- Rhetorical setups (`What if I told you` / `Think about it:` / self-answered Q&A)
- Narrator from a distance (`nobody` / `people` where `you` fits an intro, how-to step, or CTA)
- Absolute quantifiers and universals about the world: `always`, `never`, `every`, `all`, `none`, `everyone`, `nobody` / `no one` as a rhetorical subject (`Nobody wants to audit a shared drive.` / `No one reads the retention schedule.`), `any team`, `no team`, `the only way`, `the best`, `the single most important`. Skip literal technical uses (`every row`, `all columns`) and procedure steps (`Always back up before upgrading.`).
- Certainty adverbs and verbs: `clearly`, `obviously`, `undoubtedly`, `without question`, `of course`, `simply`, `guarantees`, `ensures`, `proves`, `eliminates`, `solves`, and `will` where `can` or `tends to` is accurate
- Unsupported superlatives and outcome absolutes: `fastest`, `most secure`, `100%`, `zero risk`, `completely`, `entirely`, with no number, source, or condition attached. Skip claims that the manuscript or crosslinks source.
- Categorical verdicts: a flat judgment on a whole category of tools or approaches (`X is dead.` / `X is broken.` / `X doesn't work.` / `X is the future.`)
- Unconditional prescriptions: `You must`, `You need to`, or `Never do X` with no condition and no reason
- Formatting slop (emoji headings, mid-sentence bold, headers over two-sentence sections)
- Stacked adjectives before a noun (`scalable, reliable, high-performance streaming pipeline`), multiple abstract nouns in one sentence, and empty transition phrases
- Clock-time scenes (`At 2 a.m., an analyst sees an alert that points to a credential misused months ago.` / `At 3 a.m.,` and the same shape with any hour)
- Nominal relative clause: a wh-clause with no noun head standing in for a noun (`what remains queryable`, `who runs the platform`, `how they are priced`, `what to track`)
- Embedded question clause: a wh- or whether-clause as the object of a verb (`ask whether older data feeds the same dashboards`, `ask what gets sampled`)
- That-clause object: a that-clause or dropped-that clause as the object of a verb (`says every unique combination creates a new series`, `means an agent can spend`)
- Three parallel clauses or phrases of similar length (`We scan it, index it, and secure it.` / `faster, cheaper, and safer`)
- Three-item lists whose items add nothing the sentence needs, or whose third item only completes the rhythm
- Three parallel sentences or fragments in a row, or a heading, bullet set, or CTA built on three beats
- Software personification: software, a product, or a feature as the subject of a human verb
- Complex noun phrases
- Short pairs and fragment openers: two short sentences in a row where one would do (`Logs pile up. Costs follow.`), or a paragraph that opens on a fragment (`Fast. Cheap. Reliable.` / `Less noise.`)
- Imperative closers and hypotheticals: a paragraph or section that ends on a command (`Start with the logs.` / `Audit your pipeline today.`) or a hypothetical (`Imagine if every query returned in seconds.` / `Picture a team that never pages at night.`) instead of a concrete statement
- Cold section openers: a section that opens with a one-line abstraction, a bare claim, or a question with no context, instead of grounding the reader in the topic of the section
- Duplicate point: a sentence or paragraph that restates a point already made in the same section or the one before it
- Gerund as the subject of a sentence or clause (`Sampling audit logs risks dropping the one event an investigation needs.` / `Writing to two zones keeps ingestion running.`). Skip lexicalized nouns such as logging, monitoring, billing, and pricing, and gerunds in headings.
- Missing transitions: consecutive sentences or paragraphs whose relationship (cause, contrast, sequence, example) is left unstated, so the reader has to infer the link (`Retention is set to 7 days. Reviews start two weeks after the alert.`). Skip pairs where the link is already obvious.

## Words and phrases to flag

Catalog each occurrence of the following words and phrases. Source label: `AI pattern`.

- Banned words: delve, foster, leverage, utilize, facilitate, empower, streamline, robust, cutting-edge, paradigm, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness, ever-evolving, best-in-class, seamless, powerful, unlock (as metaphor), stays, meters, shape, shapes, shaped, shaping
- Empty jargon: navigate, unpack, lean into, landscape, deep dive, double down, circle back, let's dive in, at its core
- Empty adverbs and phrases: just, really, actually, it's worth noting, in today's world/landscape/environment, at the end of the day, this is particularly important because, `Whether you're an X or a Y`, `this allows teams to`
- "actual", "actually" (including "in actual practice")
- "quiet", "quietly", "silent", "silently"
- "gap", "gaps" (including "the real gaps")
- "structural", "structurally"
- "architecture", "shift", "realities"
- "bar" as a metaphor (`the bar`, `uniqueness bar`), not the UI "search bar"
- Metaphor "break", "breaks", "breaking", "broke" (`breaks at scale`), not literal uses such as a line break or protocol break
- "not just" and "do this, not that" constructions
- *name* tics: imperative "Name the…", "is named", "a product called", "namely" (not ordinary nouns such as domain name, metric name, file name, and product names)
- Adverb forms of the words above

## Mechanical and house style

Catalog each occurrence of the following. Source label: `Mechanical`.

- Heading without `#` through `######` or without a space after the hashes
- Bold-only line that is clearly a section title
- Body heading (H2 and below) not in sentence case, except proper nouns, acronyms, and product names
- Heading shorter than 3 words or longer than 12 words, except standard component headings (Key takeaways, TL;DR, FAQs, Next steps, Related Reading)
- Heading with a trademark symbol (™, ®, ©)
- Heading with inline bold
- Image tag or Markdown image syntax
- Em dash (`—`), en dash (`–`), or double hyphen (`--`) in prose
- Inline `**bold**` in body prose, list items, or FAQ answers
- Horizontal rule (`---`) in the body
- `etc.` in body copy
- "click here" or "read more"
- Missing serial comma
- First-person singular ("I")
- Missing comma: after an introductory phrase or clause (`After the migration the team moved alerts.`), before a coordinating conjunction that joins two independent clauses (`The index is fast but storage costs climb.`), or around a nonessential clause or appositive
- Missing contraction: a spelled-out form where a contraction fits (`do not`, `does not`, `is not`, `it is`, `we are`, `you will`, `cannot`, `would not`). Skip quotes, code, legal or policy text, deliberate emphasis, and cases where the contraction is ambiguous (`Here it is.`).
- New technical term on first use without quotes
- Acronym on first use that is not spelled out, unless it is a house abbreviation the style guide lists
- Link text that is a page title, a product name used as a citation, a source label (`according to`, `cited in`, `per`, `via`, `see [destination]`, `from X`, `outlined at`), or a raw URL
- Link that starts a sentence
- Sentence that exists only to hold a link (`For more, see [X].` / `Learn more in [X].` / `[X] covers this in depth.`), including one that closes a paragraph or section
- Link text that does not name the destination's topic
- Raw URL in prose
- Competitor link, including competitor content on third-party domains

## Input

The manuscript: `{RUN_DIR}/{id-or-slug}.md` during generate_article, otherwise the path the caller names.

## Output

Write one combined catalog and paste the same table in chat:

- During generate_article: `{RUN_DIR}/{id-or-slug}-editorial-catalog.md`.
- Otherwise: `{stem}-editorial-catalog.md` next to the manuscript.

Columns: `Pattern` | `Instance` | `Source`.

- One row per instance.
- Quote the exact line in `Instance`.
- `Source` is `AI pattern` or `Mechanical`.

If nothing matches, write `Findings: none`.

Log: `[run-debug] workflow=_workflows/ops/editorial_catalog | CATALOG | path=… rows=n`

## Related

- [editorial_replace](../editorial_replace/SKILL.md)
