---
name: editorial_replace
description: >-
  Apply a combined editorial catalog (AI-tell patterns plus mechanical/house-style
  issues) to a manuscript. Overwrites the manuscript in place. Use from
  generate_article after editorial_catalog.
"last updated": 2026-11-08
"last run": 2026-11-11
---

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

# Editorial replace

Edit mode. Fix every row in the catalog written by [editorial_catalog](../editorial_catalog/SKILL.md). The rule lists live in that skill. The catalog says what is wrong. You decide the rewrite.

## Input

- The manuscript: `{RUN_DIR}/{id-or-slug}.md` during generate_article, otherwise the path the caller names.
- The catalog: `{RUN_DIR}/{id-or-slug}-editorial-catalog.md`, or `{stem}-editorial-catalog.md` next to the manuscript. If the catalog is missing, run [editorial_catalog](../editorial_catalog/SKILL.md) once, then continue.

## Steps

1) For each catalog row, rewrite the quoted `Instance`. Make the replacement thoughtful, not opinionated. Make it informative, and easy to read. Find the row's pattern in the guide below and follow its Explanation and example of a better version. Keep the meaning and every fact.

2) Overwrite the manuscript with the full document, from the H1 through the last section. Return the complete file. Save the reply only when it keeps every heading, every required first-party URL the caller names, and every close section already in the manuscript (FAQs, related reading, or the CTA). If anything is missing, leave the saved manuscript unchanged and ask for the whole manuscript again.

3) Report a short **What changed** section.

Preserve every required first-party URL the caller names, with its destination unchanged. Spell product names exactly as the workspace's context files do.

Log: `[run-debug] workflow=_workflows/ops/editorial_replace | REPLACE | path=… applied=n`

# Replacement guide

One section per pattern from the catalog. The examples are illustrations. Rewrite the real instance, not the example.

## Binary contrasts

### Explanation
A sentence defines a point by denying something nobody claimed. State the point directly. Keep the "not X" half only when the reader really holds that belief.

### Example to replace:
It's not a logging problem. It's a retention problem.
### Example of a better version:
Your retention policy decides what you can still query in a year.

## Negative listing

### Explanation
A run of "Not a X. Not a Y." fragments before the reveal. Say what the thing is in one sentence.

### Example to replace:
Not a dashboard. Not a data lake. A query engine.
### Example of a better version:
Acme Logs is a query engine for high-volume log data.

## Throat-clearing openers

### Explanation
A lead-in that announces a point instead of making it. Delete it and start with the claim.

### Example to replace:
Here's the thing: most teams never test their restore process.
### Example of a better version:
Most teams skip testing their restore process.

## Faux-insight and rhetorical setups

### Explanation
Teasers (`What most people get wrong`, `What if I told you`, `Think about it:`) and self-answered questions. Skip the setup and give the answer with its evidence.

### Example to replace:
What if I told you your alerts are the problem? They are.
### Example of a better version:
Your alert rules fire on 40 conditions, and nine of them account for most pages.

## Colon reveals

### Explanation
A noun phrase, a colon, and a dramatic lowercase payoff. Join them into one plain sentence where the verb does the work.

### Example to replace:
The result: a pipeline that nobody trusts.
### Example of a better version:
The result is a pipeline that the team no longer trusts.

## Importance puffery and vague declaratives

### Explanation
Sentences that claim significance without a fact (`plays a vital role`, `the stakes are high`, `the reasons are structural`). Replace with the specific fact, number, or consequence. If none exists, cut the sentence.

### Example to replace:
Observability plays a vital role in modern operations.
### Example of a better version:
Without traces, a slow checkout can take hours to trace to a single service.

## Interpretive language and "says nothing about"

### Explanation
The author narrates how to read the text (`the key point is`, `as you can see`, `this distinction matters`, `says nothing about`). Delete the narration and state the content.

### Example to replace:
The key point is that the free tier says nothing about retention.
### Example of a better version:
The free tier doesn't list a retention period, so ask support before relying on it.

## Weasel attribution

### Explanation
A claim credited to nobody (`experts agree`, `studies show`). Name the source and link it, or cut the claim.

### Example to replace:
Studies show that most outages start with a config change.
### Example of a better version:
Google's SRE book reports that [roughly 70% of outages follow a change to a live system](https://example.com/sre-book).

## Synonym cycling

### Explanation
One thing called by several names in a row. Pick the clearest term and repeat it.

### Example to replace:
The agent reads the file. The tool then parses the document, and the utility writes the output.
### Example of a better version:
The agent reads the file, and then writes the parsed output.

## Dramatic fragmentation and short pairs

### Explanation
Short fragments stacked for effect (`X. And Y. And Z.`, `Logs pile up. Costs follow.`) or a paragraph that opens on a fragment. Merge into one full sentence with a subject and a verb.

### Example to replace:
Logs pile up. Costs follow. Nobody notices.
### Example of a better version:
As logs pile up, storage costs climb.

## Narrator from a distance and "nobody" subjects

### Explanation
`people`, `nobody`, or `no one` where the reader is the actor. Address the reader with "you", or name the real actor.

### Example to replace:
Nobody wants to audit a shared drive by hand.
### Example of a better version:
You shouldn't have to audit a shared drive by hand.

## Formatting slop

### Explanation
Emoji headings, mid-sentence bold, and headers over two-sentence sections. Remove the emoji and bold. Merge a thin section into the section above it.

### Example to replace:
## 🚀 Why it **matters**
### Example of a better version:
## Why it matters

## Stacked adjectives and complex noun phrases

### Explanation
Several modifiers or abstract nouns before one noun. Keep the one that carries meaning and split the rest into a short clause.

### Example to replace:
A scalable, reliable, high-performance streaming data ingestion pipeline.
### Example of a better version:
A streaming pipeline that ingests 2 million events per second.

## Clock-time scenes

### Explanation
Openers built on a time stamp (`At 2 a.m., an analyst…`). Replace with a concrete scenario without the hour, or cut.

### Example to replace:
At 3 a.m., an engineer sees an alert for a credential misused months ago.
### Example of a better version:
Remove altogether.

## Clause-as-noun (nominal relative, embedded question, that-clause object)

### Explanation
A clause stands in for a noun (`what remains queryable`, `ask whether…`, `says every combination creates a new series`). Replace the clause with a noun phrase that names the thing.

### Example to replace:
Ask what gets sampled before you buy.
### Example of a better version:
Ask for the sampling rules before you buy.

## Three parallel beats

### Explanation
Three clauses, list items, sentences, or CTA beats of similar length. Keep the items that carry information. Cut the filler item or vary the structure. Two or four items is fine.

### Example to replace:
We scan it, index it, and secure it.
### Example of a better version:
We scan and index each file, and then we restrict access by team.

## Software personification

### Explanation
A product or feature as the subject of a human verb. Make a person the subject, or use a plain verb.

### Example to replace:
The dashboard tells you when a job is struggling.
### Example of a better version:
The dashboard shows job latency, and you can alert on it.

## Imperative closers and hypotheticals

### Explanation
A paragraph or section that ends on a command or an `imagine` framing. End on a concrete statement of what the section showed.

### Example to replace:
Imagine if every query returned in seconds. Start with your logs.
### Example of a better version:
After the change, the median query returned in 1.8 seconds on 90 days of logs.
### Alternative example of a better version:
Remove altogether.

## Cold section openers

### Explanation
A section that opens with a bare abstraction or context-free question. Open with one sentence that names the topic and why it matters to this reader.

### Example to replace:
## Retention
What is the right number?
### Example of a better version:
## Retention
Retention sets how far back you can investigate an incident, and how much storage you pay for.

## Duplicate point

### Explanation
A sentence or paragraph that restates what the section already said. Keep the stronger version and delete the other, or replace it with a new fact.

### Example to replace:
Storage costs grow with volume. As volume increases, you pay more to store it.
### Example of a better version:
Storage costs grow with volume.

## Absolute quantifiers and universals

### Explanation
A claim about the world stated as true for everyone, always, or never. Narrow it to the cases the evidence covers. Name the condition, the scale, or the proportion. Leave literal technical uses and procedure steps alone.

### Example to replace:
Every team needs a retention policy.
### Example of a better version:
Teams that investigate incidents older than 30 days need a retention policy that covers that window.

## Certainty words and unsupported superlatives

### Explanation
Intensifiers and outcome absolutes (`clearly`, `simply`, `guarantees`, `fastest`, `100%`) with no support. Delete the intensifier. Replace the superlative with a number, a source, or a condition. Use `can` or `typically` when the outcome varies. Keep a confident claim only when the manuscript or crosslinks supply a source.

### Example to replace:
This guarantees you will never lose a log line.
### Example of a better version:
If you write each log line to two zones, ingestion can continue through a single zone failure.

## Categorical verdicts and unconditional prescriptions

### Explanation
A flat verdict on a whole category (`X doesn't work`) or a command with no condition (`You must`, `Never do X`). Say what fails, for whom, and under what conditions, or give the reason behind the rule. Keep a firm statement only when you can cite or measure it.

### Example to replace:
Sampling doesn't work for security. Never sample audit logs.
### Example of a better version:
Sampling can drop the one event an investigation needs, so security teams often keep full-fidelity logs for audit sources.

## Banned words, jargon, empty adverbs, and flagged words

### Explanation
Covers `leverage`, `robust`, `seamless`, `landscape`, `just`, `really`, `actually`, `quiet`, `gap`, `structural`, `shape` (`shapes`, `shaped`, `shaping`), `bar` and `break` used as metaphors, and the `name` tics. Use the plain word and delete empty adverbs. For metaphors, say the literal thing.

### Example to replace:
You can just leverage our robust API to close the gap.
### Example of a better version:
You can use our API to import the missing records.

### Examples for each banned word

| Word | Example to replace | Better version |
| --- | --- | --- |
| delve | Let's delve into how retention works. | This section explains how retention works. |
| foster | Shared dashboards foster collaboration. | Shared dashboards let teams work from the same numbers. |
| leverage | Leverage the index to speed up queries. | Use the index to speed up queries. |
| utilize | Utilize the CLI to export logs. | Use the CLI to export logs. |
| facilitate | The connector facilitates ingestion. | The connector loads data from S3. |
| empower | The console empowers analysts. | Analysts can run their own queries in the console. |
| streamline | We streamline onboarding. | Onboarding takes three steps. |
| robust | A robust alerting system. | An alerting system that retries failed notifications. |
| cutting-edge | Cutting-edge compression. | Compression that cuts storage by 80%. |
| paradigm | A new paradigm for log storage. | A different way to store logs. |
| tapestry | A tapestry of data sources. | Many data sources, including S3, Kafka, and Postgres. |
| realm | In the realm of observability, cost matters. | In observability, cost matters. |
| beacon | The dashboard is a beacon of clarity. | The dashboard shows each service's error rate. |
| multifaceted | A multifaceted problem. | A problem with three causes. |
| meticulous | Meticulous audit trails. | Audit trails that record every change. |
| intricate | Intricate retention rules. | Retention rules that vary by table. |
| paramount | Security is paramount. | Security is the top requirement for this team. |
| transformative | A transformative release. | A release that cuts query time in half. |
| elevate | Elevate your monitoring. | Add per-service latency alerts to your monitoring. |
| embark | Embark on a migration. | Start the migration. |
| supercharge | Supercharge your queries. | Speed up your queries. |
| harness | Harness your log data. | Use your log data. |
| ever-evolving | An ever-evolving threat model. | A threat model that changes with each release. |
| best-in-class | Best-in-class performance. | Queries return in under 2 seconds. |
| seamless | A seamless upgrade. | An upgrade with no downtime. |
| powerful | A powerful query engine. | A query engine that scans 1 TB in seconds. |
| unlock (metaphor) | Unlock insights from your logs. | Find slow endpoints in your logs. |
| stay / stays | The data stays in your account. | The data remains in your account. |
| meters | The plan meters ingest. | The plan bills by gigabytes ingested. |
| shape / shapes / shaped / shaping | Retention shapes cost. | Longer retention raises cost. |

## Dashes, bold, rules, `etc.`, and images

### Explanation
Replace em dashes, en dashes, and `--` with a comma, period, or parentheses. Remove inline bold and horizontal rules. List the items instead of writing `etc.`. Replace images with `[image]` on its own line.

### Example to replace:
The index is fast — **very** fast — for logs, metrics, etc.
### Example of a better version:
The index returns log and metric queries in under 2 seconds.

## Heading issues

### Explanation
Headings need a `#` prefix with a space, sentence case, 3 to 12 words, no trademark symbol, and no inline bold. Standard component headings (Key takeaways, TL;DR, FAQs, Next steps, Related Reading) are exempt from the length rule.

### Example to replace:
## How To Configure **Retention** Rules™
### Example of a better version:
## How to configure retention rules

## Gerund as the subject of a sentence

### Explanation
A verb ending in `-ing` opens the sentence and acts as its subject, which hides who does the action and makes the sentence abstract. Name the actor (`you`, `we`, or a specific team) and use a finite verb, or turn the gerund into an `if` or `when` clause. Leave lexicalized nouns (logging, monitoring, billing, pricing) and headings alone.

### Example to replace:
Sampling audit logs risks dropping the one event an investigation needs.
### Example of a better version:
If you sample audit logs, you can drop the one event an investigation needs.

## Missing transitions

### Explanation
Neighboring sentences or paragraphs sit side by side with no stated relationship, so the reader has to guess the link. Add a plain connective that names it: `but` or `however` for contrast, `so` or `because` for cause, `then` or `after that` for sequence, `for example` for an instance. Don't use filler transitions (`it's worth noting`, `at the end of the day`). Fold two short sentences into one when that reads better. Leave pairs alone when the link is already obvious.

### Example to replace:
Retention is set to 7 days. Incident reviews often start two weeks after the alert. Analysts can't see the original logs.
### Example of a better version:
Retention is set to 7 days, but incident reviews often start two weeks after the alert. By then, analysts can't see the original logs.

## Missing commas

### Explanation
Add a comma after an introductory phrase or clause, before a coordinating conjunction (`and`, `but`, `so`, `or`) that joins two independent clauses, and around a nonessential clause or appositive. Don't add a comma between a subject and its verb, or before a conjunction that joins two verbs with one subject. Use a comma, not a dash, for an aside.

### Example to replace:
After the migration the team moved alerts to the new pipeline but the old dashboards kept firing.
### Example of a better version:
After the migration, the team moved alerts to the new pipeline, but the old dashboards kept firing.

## Missing contractions

### Explanation
Spelled-out forms read stiff and formal. Use a contraction wherever one fits (`do not` to `don't`, `it is` to `it's`, `cannot` to `can't`, `we are` to `we're`, `you will` to `you'll`). Leave the form spelled out when the contraction would be ambiguous (`Here it is.`), when you want deliberate emphasis, inside quotes, code, and legal or policy text, and in headings that already read cleanly.

### Example to replace:
We do not recommend sampling audit logs because it is easy to lose events that you cannot recover.
### Example of a better version:
We don't recommend sampling audit logs, because it's easy to lose events you can't recover.

## Serial comma, first person, new terms, and acronyms

### Explanation
Add the serial comma. Rewrite "I" as "we" or the reader's voice. Quote a new technical term on first use. Spell out an acronym on first use unless the style guide lists it.

### Example to replace:
I tracked logs, metrics and traces with SIEM.
### Example of a better version:
We tracked logs, metrics, and traces with a security information and event management (SIEM) tool.

## Link-holder sentences and sentence-leading links

### Explanation
A sentence that exists only to hold a link, or a sentence that starts with one. Delete the holder sentence and put the link inside the sentence that makes the claim.

### Example to replace:
Retention affects cost. For more, see [our pricing page](https://example.com/pricing).
### Example of a better version:
Retention affects cost, and [per-gigabyte storage rates](https://example.com/pricing) show by how much.

## Link text and raw URLs

### Explanation
Link text must name the destination's topic. Do not use a page title, a source label (`according to`, `via`, `per`), `click here`, or a raw URL. Remove competitor links.

### Example to replace:
According to https://example.com/guide, you can tune retention.
### Example of a better version:
You can tune retention with [per-table retention settings](https://example.com/guide).

## Related

- [editorial_catalog](../editorial_catalog/SKILL.md)
