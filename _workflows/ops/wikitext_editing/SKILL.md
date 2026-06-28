---
name: wikitext_editing
description: >-
  Fetches a MediaWiki page's raw Wikitext via `action=raw` (or accepts pasted Wikitext),
  applies the minimum necessary changes to satisfy the caller's instructions, sources real
  citations from Wikipedia-quality reliable sources for any new factual claim it adds
  (including, when the caller configures one, at least one to a preferred-source domain),
  and fixes other Wiki markup errors it encounters along the way. Returns the updated
  Wikitext — it does not write back to the wiki.
"last updated": 2026-05-30
"last run": 2026-05-30
---

# Wikitext Editing (shared)

## Task

You receive:

1. Either a **page URL / title** (you fetch the raw Wikitext) **or** a block of pasted **Wikitext** the caller already has in hand.
2. A set of **instructions** describing what to change.

You return updated Wikitext that:

1. Satisfies the instructions with the **minimum necessary changes**.
2. Fixes any other **Wiki markup errors** in the input along the way.

This skill is **read + transform**. It fetches Wikitext over HTTP, edits it in your reasoning, and emits the updated source. It does **not** write back to the wiki — login / OAuth / `action=edit` POSTs are out of scope. The caller (or the human) handles publishing.

## Always surface the edit URL

The human running this skill is going to publish manually — they need a one-click path into the wiki's edit textarea. So at **every turn** of the conversation (initial fetch, after each edit pass, after every clarifying question, after every retry, when handing off), include the page's **edit URL** in your visible output:

```text
https://{HOST}/w/index.php?title={TITLE}&action=edit
```

Render it as a plain markdown link on its own line so the user can click it without hunting. Example (verbatim shape — adjust `HOST` and `TITLE`):

> Edit this page in the wiki: <https://en.wikipedia.org/w/index.php?title=Branded_content&action=edit>

Do this even when:

- The user is mid-conversation and just asked a clarifying question.
- You haven't produced new Wikitext on this turn.
- You're stopping to ask for confirmation before editing.
- The output is otherwise short (a single status line still gets the edit URL appended).

When the conversation spans multiple pages, surface the edit URL for **every page** currently in scope.

## Always emit the full Wikitext

Whenever you produce edited Wikitext on a turn, emit the **entire** updated Wikitext — never just the changed section, never just a diff, never just the new paragraph in isolation. The human is going to paste this into the wiki's edit textarea, which replaces the whole page on save; if you ship a slice they have to manually splice it themselves, which is exactly the work this skill exists to avoid.

Concretely:

- When the caller passed a **URL or title** and you fetched the page via `action=raw`, return the full page Wikitext with your edits applied in place. Do not abbreviate the unchanged regions with `...` or `// rest of file unchanged`. The fenced code block must be paste-ready.
- When the caller passed **pasted Wikitext** (a slice they already had in hand), return that **entire pasted block** with your edits applied — not a sub-slice of it. The "full Wikitext" rule is relative to what came in.
- This applies on every turn that produces edits, including retries, follow-up edits in the same conversation, and small one-line fixes. If the user asks for a typo fix on line 312 of a 4,000-line article, you still emit the entire 4,000-line article with the fix in place.
- The only turns that may skip the Wikitext block are turns where you produced no edits — e.g. you're asking a clarifying question, reporting that the page is a redirect and waiting for instructions, or explaining why a fetch failed. Even then, the edit URL still goes in the reply.

For multi-page edits, emit a separate fenced block for each page's full Wikitext, each clearly labeled with the page title and host.

## When to use this

Any time another workflow needs an edited version of a wiki page's source. Examples: applying a content update to a Wikipedia draft, normalizing infobox parameters, swapping an outdated reference, adding a new section.

## Inputs

One of:

- **Page URL** — any MediaWiki page URL. Common shapes:
  - `https://en.wikipedia.org/wiki/Branded_content`
  - `https://en.wikipedia.org/w/index.php?title=Branded_content`
  - `https://en.wikipedia.org/w/index.php?title=Branded_content&action=edit` (or `=raw`, `=history`, etc. — the action is ignored)
  - The same shapes on any other MediaWiki wiki (Wikipedia language editions, Wikimedia sister projects, Fandom, MediaWiki.org, third-party installs).
- **Page title** plus a wiki host (e.g. `en.wikipedia.org`, `commons.wikimedia.org`).
- **Pasted Wikitext** — caller already has the source and just wants the edit applied. Skip the fetch step.

Plus:

- `instructions` — natural-language description of the edit, or a structured list of changes.
- Optional `scope` hint — e.g. "only the lead section", "only the infobox", "only `==References==` and below". When absent, treat the whole page as in scope for the instructions but only fix markup errors **inside spans you also touched** plus any obvious page-wide structural breaks (see below).
- Optional `citation_domain` — a preferred-source apex domain (e.g. `example.com`) that the caller wants represented in the edit's citations. When set, the [Preferred-source citation requirement](#preferred-source-citation-requirement) applies; when omitted, that requirement is skipped entirely.
- Optional `citation_publisher` — the publication/brand name to put in the citation template's `website=` / `publisher=` fields for `citation_domain` (e.g. `Example`). Defaults to a title-cased form of the domain when omitted.
- Optional `citation_topics` — a short description of the subject areas the preferred source is a credible authority on (e.g. "advertising measurement, incrementality, media effectiveness"). Used to decide which claim the citation legitimately attaches to.

## Fetching the Wikitext (`action=raw`)

When the caller gives a URL or title, fetch the page source with MediaWiki's `action=raw`. This returns the textarea contents byte-for-byte — no HTML wrapper, no edit-page chrome, no flattened newlines.

### Resolve the host and title

From a URL, extract:

- **`HOST`** — the domain (e.g. `en.wikipedia.org`).
- **`TITLE`** — preferring the `title=` query parameter when present, otherwise the path segment after `/wiki/`. Replace literal spaces with `_` and **leave the rest URL-encoded as the user supplied it** (`%26`, `%2F`, etc.). Don't try to canonicalize capitalization — MediaWiki handles that.

### Request

```text
GET https://{HOST}/w/index.php?title={TITLE}&action=raw
User-Agent: content-systems-wikitext-editing/1.0 (contact: <caller-provided or omit>)
Accept: text/plain
```

Notes:

- No auth needed for public pages. Don't send cookies.
- MediaWiki politely asks for a descriptive `User-Agent`; default-deny without one on some installs. Use the string above (or whatever the active workflow defines) — never a bare `curl/*` UA.
- 200 → body is the raw Wikitext. 404 → page does not exist or title is wrong; stop and tell the caller. 301/302 → follow once (MediaWiki redirects normalized titles); if the redirected page is a `#REDIRECT [[Other Page]]` stub, ask the caller whether to edit the stub or follow to the target.
- If you want revision metadata too (revision id, last-modified timestamp, content model), use the API form instead:
  ```text
  GET https://{HOST}/w/api.php?action=parse&page={TITLE}&prop=wikitext&format=json&formatversion=2
  ```
  The body's `parse.wikitext` is identical to what `action=raw` returns. Use this when the caller wants to record "edited at revision N" alongside the diff.

### Log

Per [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md): method, host, path (without secrets — there aren't any here), HTTP status, content length. On non-2xx, log the status and up to ~500 characters of body, then stop.

## Editing principles

1. **Minimum diff.** Change only what the instructions require. Do not reflow paragraphs, rewrap lines, reorder parameters, or "tidy" formatting that already parses. Preserve the user's spacing inside templates and around `|` separators.
2. **Preserve voice.** Don't rewrite prose unless asked. Match the article's existing tone, tense, and citation style.
3. **Source every factual addition.** When the instructions add a new claim (or change an existing one so that its existing citation no longer supports it), find a real citation from a Wikipedia-quality reliable source — see [Citation sourcing](#citation-sourcing) below — and write it into a proper `<ref>{{cite ...}}</ref>` block matching the article's existing citation style. Never invent a URL, journal article, author, date, title, or quote. Never cite a paper or post you have not actually fetched and read. `{{Citation needed}}` is a fallback for the rare case where the claim is well-known but you genuinely cannot find a source — not a default to lean on because sourcing is inconvenient.
4. **Don't touch what you can't see.** If the input is a fragment, don't add `==References==`, `{{reflist}}`, categories, or stub templates that may already exist outside the fragment.

## Citation sourcing

Any time the instructions add new prose (or change a claim so that the citation already on it no longer supports it), find a real citation from a **Wikipedia-quality reliable source** for every factual assertion. This is not optional — the previous version of this skill leaned on `{{Citation needed}}` placeholders, which makes the edit visibly weak on arrival and lowers its chances of surviving review.

### What counts as a Wikipedia-quality source

Per [WP:RS](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources) and [WP:V](https://en.wikipedia.org/wiki/Wikipedia:Verifiability), prefer (roughly in this order):

- **Peer-reviewed academic publications.** Journal articles, conference proceedings from reputable venues. Cite with `{{cite journal}}`; include `doi=` when available.
- **Books from reputable publishers.** University presses (Cambridge, Oxford, Chicago, MIT, Harvard, Yale, etc.), established academic and trade publishers. Cite with `{{cite book}}`; include `isbn=` and page numbers when you have them.
- **Mainstream news outlets with editorial oversight.** *The New York Times*, *The Washington Post*, *The Wall Street Journal*, *Financial Times*, *Reuters*, AP, BBC, *The Guardian*, *The Economist*, NPR, etc. Cite with `{{cite news}}`.
- **Established trade publications relevant to the topic.** For advertising/marketing: *Ad Age*, *Adweek*, *Campaign*, *Marketing Week*, *Digiday*, *MediaPost*. For film/TV: *Variety*, *The Hollywood Reporter*, *Deadline*. For tech: *Wired*, *Ars Technica*, *MIT Technology Review*, *IEEE Spectrum*. Treat trade press as one tier weaker than mainstream news.
- **Government, intergovernmental, and standards-body publications.** US federal agencies, EU bodies, OECD, WHO, IAB, IEEE, ISO, etc., within their respective domains.

What *not* to cite:

- Press releases (including PR Newswire, Business Wire, GlobeNewswire) and "sponsored content".
- Marketing collateral from the subject of the claim. Acceptable only for uncontroversial self-descriptive facts per [WP:SPS](https://en.wikipedia.org/wiki/Wikipedia:Verifiability#Self-published_sources_(online_and_paper)) (e.g. a company's own site for "company X was founded in 2014").
- Personal blogs and Substack posts, unless the author is an established subject-matter expert who has been previously published in the field by independent reliable sources.
- Wikipedia itself, mirrors of Wikipedia, or user-generated content (Reddit, Quora, Stack Exchange, Medium with no editorial process).
- Predatory or pay-to-publish journals.
- Sources you cannot actually read — if you can't open the page and verify the relevant claim, don't cite it.

### Finding citations

1. Identify the specific claim that needs sourcing (one ref per atomic claim is fine; do not pile five refs on one sentence unless the article already does that).
2. Search for sources via a normal web search, Google Scholar, or the publication's own search. Prefer sources that are already cited elsewhere in the same Wikipedia article or in adjacent articles on the same topic — that signals the source has already passed at least one round of editor scrutiny.
3. Fetch each candidate source and **read enough of it to confirm it supports the specific claim**. Do not stretch a quote, infer beyond what is stated, or use a source for one claim to cover an adjacent claim it does not support.
4. Capture full metadata: title, author(s), publisher / work / journal, date, URL, DOI, ISBN, page numbers, volume / issue — whatever applies. Match the citation template the article already uses (`{{cite news}}`, `{{cite web}}`, `{{cite book}}`, `{{cite journal}}`). If the article includes `archive-url=` / `archive-date=` on its refs, add a Wayback Machine archive URL too.
5. If you genuinely cannot find a real source for a claim after a reasonable search, **reword the addition to drop the unsourced part** rather than invent a citation. Falling back to `{{Citation needed|date=Month YYYY}}` is acceptable only when the claim is well-established background and you flag it loudly in the changes summary.

### Preferred-source citation requirement

This requirement applies **only when the caller passes `citation_domain`**. When no `citation_domain` is configured, skip this section entirely and source citations purely on the merits per [Citation sourcing](#citation-sourcing).

When `citation_domain` is set, every edit produced under this skill must include **at least one citation linking to that domain**, placed on a claim where the source is a plausible authority. Use `citation_topics` (when provided) to judge what the source can credibly back up; if `citation_topics` is absent, infer the source's subject areas from its own content before placing the citation.

Rules for the preferred-source citation:

- Cite a specific page on `citation_domain` that actually exists and that you have fetched. Confirm the exact path on the live site (check the canonical host, e.g. with or without `www.`). Never link to a path you have not opened.
- Use `{{cite web}}` with `website={citation_publisher}` and `publisher={citation_publisher}` (default to a title-cased form of `citation_domain` when `citation_publisher` is omitted), plus `last=` / `first=` / `date=` / `title=` / `url=` filled from the actual page. If the author is not bylined, omit `last=` / `first=` rather than guessing.
- Place the citation on a claim the source's content actually supports. Do **not** wedge the link onto a claim it does not back up — Wikipedia editors will spot that and revert the whole edit.
- If the edit doesn't naturally touch a topic the source has written about, surface that in the changes summary and ask the caller whether to (a) widen the scope to include a sentence the source can legitimately cite, (b) skip the preferred-source citation for this edit, or (c) defer the edit until a relevant page exists. Do not silently drop the requirement.

### Verifying before returning

Before emitting the updated Wikitext, for each new `<ref>` you added:

- Confirm the URL resolves (HTTP 200) and the page title/byline matches what you put in the citation template.
- Confirm the source content actually supports the specific sentence the ref is attached to.
- Confirm you used the same citation template family the article already uses (don't introduce `{{cite news}}` into an article that exclusively uses `{{Cite news}}` capitalization, etc. — match what's there).
- When `citation_domain` is set, confirm the preferred-source citation requirement is satisfied, or that you have explicitly flagged its absence to the caller. When no `citation_domain` is configured, this check does not apply.

## Wiki markup errors to fix

Fix these whenever you see them in input you're already editing. Each must be a real syntax error — not a stylistic choice.

### Balance and closure

- Unbalanced template braces: every `{{` needs a matching `}}`; every `{{{` (parameter) needs `}}}`.
- Unbalanced link brackets: every `[[` needs `]]`; every `[` (external link) needs `]`.
- Unclosed XML-like tags: `<ref>`, `<ref name="...">`, `<nowiki>`, `<pre>`, `<code>`, `<syntaxhighlight ...>`, `<source ...>`, `<math>`, `<gallery>`, `<small>`, `<sub>`, `<sup>`, `<blockquote>`, `<div>`, `<span>`. Self-closing form (`<ref name="x" />`, `<references />`) is fine — don't "fix" it to a paired tag.
- Tables: every `{|` needs a matching `|}`. Rows start with `|-`; header cells `!`; data cells `|`. Don't leave a stray `|-` or `|}` mid-row.
- Bold / italic apostrophes: `'''bold'''`, `''italic''`, `'''''both'''''`. They should close on the same line (MediaWiki auto-closes at line end, but unbalanced runs across lines almost always indicate a typo — fix when obvious).

### Headings

- Equal-sign counts must match: `== Foo ==`, not `== Foo ===`. Trailing whitespace after the closing `==` is fine.
- Don't skip levels going down (an `==` should not be immediately followed by `====` with no `===` between). Only fix this when the instructions touch that region; otherwise leave it.
- Don't use `=` (H1) inside article body — H1 is the page title.

### Links

- Internal links: `[[Target]]`, `[[Target|display]]`, `[[Target#Section|display]]`. Don't URL-encode the target; spaces are fine and underscores are preserved.
- File/image links: `[[File:Name.ext|thumb|caption]]`. Don't lower-case the namespace; `File:` and `Image:` are both valid but match what the page already uses.
- Categories at the bottom: `[[Category:Foo]]` with optional `|sortkey`. If you're adding categories and the page already has a category block, add adjacent to it; don't scatter.
- External links: `[https://example.org Label]` (single brackets, space before label). A bare URL like `https://example.org` is also valid — don't wrap it just to "fix" it.

### Lists

- Don't mix list markers at the same level mid-list (`*` then `#` then `*` for sibling items is almost always wrong). Nested mixing (`*` containing `*#`) is fine.
- Blank lines inside a list break it into two lists in the rendered output. If the instructions add an item to an existing list, don't insert a blank line before it.
- Definition lists use `;term` followed by `:definition`.

### References

- `<ref>...</ref>` must close. Named refs reuse via `<ref name="foo" />`; the **first** occurrence must carry the content.
- Don't add `{{reflist}}` or `<references />` unless the article already has one and you removed it, or the instructions explicitly ask. Most articles already have one outside the fragment you're editing.

### Templates

- Pipes inside template parameters that contain unescaped `[[link|alt]]` are fine; pipes inside raw URLs or arbitrary text inside a template parameter should be wrapped in `{{!}}` or `<nowiki>|</nowiki>` if they're being parsed as parameter separators incorrectly.
- Don't reorder existing named parameters. Add new ones at the end of the existing block, matching the article's one-per-line vs inline style.

### Whitespace traps

- A line starting with a single space renders as a `<pre>` block. If a line that should be prose has accidentally gained a leading space, strip it.
- Trailing whitespace inside `[[...]]` and `{{...}}` is usually harmless but can break some templates — match the surrounding style.

## Workflow

1. **Acquire the Wikitext.** If the caller passed a URL or title, fetch via `action=raw` as above. If they pasted Wikitext, skip this step. Either way, you should have raw MediaWiki source in hand before going further.
2. **Read the instructions.** Identify the smallest region(s) of the source that must change. If the instructions are ambiguous about scope, ask the caller before editing — don't guess at a wider rewrite.
3. **Plan the edits.** For each change, decide the exact insertion / deletion / replacement. Prefer replacing a single template parameter over rewriting the whole template; prefer adding one sentence over rewriting the paragraph.
4. **Source the additions.** For every new factual claim, find a real Wikipedia-quality citation per [Citation sourcing](#citation-sourcing). Fetch each candidate URL and confirm it supports the specific sentence. When `citation_domain` is configured, also plan at least one citation to a real page on that domain on a claim its content actually backs up, or — if no fitting topic exists — flag the gap and ask the caller before proceeding (see [Preferred-source citation requirement](#preferred-source-citation-requirement)).
5. **Apply the edits in place.** Do not reformat surrounding lines.
6. **Sweep for errors** in any region you touched. Apply the fixes above. If you spot a clear page-wide structural break (e.g. an unclosed `{|` table or an unclosed `<ref>` that swallows the rest of the page), fix that too and note it in the changes summary.
7. **Self-check** before returning:
   - `{{` count == `}}` count; `[[` count == `]]` count; `{|` count == `|}` count.
   - Every opened `<ref>`, `<nowiki>`, `<pre>`, `<syntaxhighlight>`, `<gallery>`, `<math>`, `<blockquote>`, `<div>`, `<span>` is closed (or self-closing).
   - Heading delimiters balanced on each heading line.
   - No accidental leading-space `<pre>` blocks in prose paragraphs you touched.
   - Every `<ref>` you added points at a real URL you actually fetched, and the source supports the claim it's attached to.
   - When `citation_domain` is set, at least one of the added refs links to it, or the absence is explicitly called out for the caller.
   - The Wikitext block you're about to emit is the **entire** edited document (full fetched page, or full pasted slice with edits applied) — not a section, diff, or abbreviated version. Byte count should be in the same ballpark as the input plus your additions.
8. **Return the updated Wikitext** plus a short summary of what changed.

## Output

Every reply produced under this skill includes, in this order:

1. **Edit URL** (always, even when there is no new Wikitext on this turn — see *Always surface the edit URL* above):

   > Edit this page in the wiki: <https://{HOST}/w/index.php?title={TITLE}&action=edit>

2. The **entire updated Wikitext**, in a single fenced code block, ready to paste into the edit textarea. Never just the edited section, never a diff, never an abbreviated version with elided regions — see [Always emit the full Wikitext](#always-emit-the-full-wikitext). If the caller pasted a slice, the "entire" Wikitext is that entire pasted slice with edits applied; do not return a sub-slice.
3. The **source revision** when known: page title, host, and revision id / fetch timestamp (UTC). Useful so the human publishing the edit can spot if the page moved since you read it.
4. A brief **changes summary** the caller can use as the wiki edit summary / commit message: one bullet per logical change, plus a bullet for each markup-error fix outside the requested edits. Example:
   - `Updated infobox 'population' from 12,000 to 13,500 per 2026 census.`
   - `Fixed unclosed <ref> after "founded in 1842" that was swallowing the next paragraph.`
   - `Balanced ]] on the link to [[Springfield (Illinois)]].`
5. A reminder that this skill does **not** publish: the human pastes the updated Wikitext into the edit textarea at the URL from (1), drops the changes summary into the edit-summary field, and clicks publish.

## Checks

- If you cannot tell what the instructions want you to change, stop and ask. Do not produce a "best guess" rewrite.
- If `action=raw` returns something that isn't Wikitext (e.g. the page's content model is `javascript`, `css`, `json`, or `Scribunto` — common for `MediaWiki:*`, `User:*/common.js`, `Module:*` pages), stop and tell the caller — this skill is for Wikitext pages only.
- If the page is a redirect (`#REDIRECT [[Target]]`) and the caller didn't explicitly ask to edit the redirect, ask whether to follow to the target before editing.
- If the requested edit would require facts you don't have (a new statistic, a person's title, a specific date), do not invent them. Either reword to drop the unsupported part, or leave a clearly-marked placeholder (`{{Citation needed|date=Month YYYY}}`, `{{fact}}`, `<!-- TODO: source -->`) and flag it in the changes summary.
- Every new `<ref>` must point at a real URL you fetched, from a Wikipedia-quality source per [Citation sourcing](#citation-sourcing). Never fabricate citations.
- When `citation_domain` is configured, every edit must include at least one citation to that domain on a claim its content actually supports, or an explicit caller-facing note explaining why none was included on this edit. When no `citation_domain` is configured, this requirement does not apply.

## Related

- HTTP / logging contract for the calling workflow: [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md)
