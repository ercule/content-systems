---
name: generate_article_07_mechanical_catalog
description: >-
  Step 07: detect mechanical checklist hits; write the catalog. Do not rewrite.
"last updated": 2026-08-31T00:00:00+00:00
"last run": 2026-08-31
---

# Generate article — 07 Mechanical catalog

Look for these patterns in the manuscript. Do not rewrite it.

- Headings use `#` through `######` with a space after the hashes. Turn lines that look like headings but use bold instead of `#` into real headings when they are clearly section titles.
- H1 stays in title case. All other headings are sentence case except proper nouns, acronyms, and product names from the copied context files.
- Replace every em dash (Unicode —) with a comma, period, colon, or parentheses.
- Replace image tags and Markdown image syntax with the literal token `[image]` on its own line.
- Rewrite any sentence that uses these tells, keeping the meaning: "actually"; "gap"; "gaps" (including "the real gaps"); "not just"; "do this, not that"; "is how you"; "is what you"; "is how we"; "is what keeps"; "tells you how"; "tells you what" (the definitional "X is how you Y" family).
- Keep every required first-party URL from `{id-or-slug}-crosslinks.md` in running prose. Do not drop or swap destinations. Do not freeze sidecar `anchor_text`. If the visible link text is a page title, product name, or "see [destination]," rewrite it into a phrase already in the sentence.
- Rewrite to remove: em dashes, "architecture", "shift", "structural" and "structurally" (replace with more plain spoken alternatives), "actual", "realities", "quiet", "silent", "shaped", "bar" (metaphor: "the bar", "uniqueness bar"; leave UI "search bar"), and adverb forms of those words

Return a catalog of every match. One row per instance, columns `Pattern` | `Instance` | `Suggested fix`. Quote the exact line. Put a short rewrite in Suggested fix. Write `{RUN_DIR}/{id-or-slug}-mechanical-catalog.md`. Paste the same table in chat. If nothing matches, write `Findings: none`.

Log: `[run-debug] workflow=_workflows/generate/generate_article | CATALOG | ok path={RUN_DIR}/{id-or-slug}.md`

Next: [../08_mechanical_rewrites/SKILL.md](../08_mechanical_rewrites/SKILL.md)
