# Messaging issues (Gallivant example)

Structured findings from a fictional analyzer run — the job that compares canon, customer language, and published assets, then flags drift for humans to fix. Matches [context-builder](https://github.com/janessa-lantz/context-builder) issue themes.

**Not live findings.** Illustrates shape only.

## Issue kinds

| Kind | Meaning |
|------|---------|
| mismatched | Published copy contradicts canon |
| misaligned | Tone or emphasis drift; not wrong, but off-brand |
| missing | Canon component absent from a surface that should carry it |
| outdated | Canon or asset stale vs newer source |
| opportunity | Gap worth filling, not necessarily an error |

## Open issues (fictional)

### issue-2026-06-28-travel-companions-label

- **kind:** mismatched
- **confidence:** high
- **component:** icp, narrative
- **surface:** `gallivant-pricing` PDF one-pager (internal draft)
- **detail:** Draft uses "Customer Success onboarding included." Canon and [gallivant-origin](../reference/gallivant-origin.md) require **Travel Companions** — Alice will notice.
- **suggested action:** Replace label; link to [canon-who-its-for.md](../canon-who-its-for.md#travel-companions-not-customer-success)

### issue-2026-06-22-software-hero-copy

- **kind:** misaligned
- **confidence:** medium
- **component:** brand-writing-identity
- **surface:** blog-sunday-night-receipts (scheduled)
- **detail:** Meta description says "expense software." Becca prefers avoiding "software" in unprompted hero/meta copy; customer quote on homepage may keep the word when attributed.
- **suggested action:** Rephrase to "expense product" or "Gallivant"; see [brand-writing-identity.md](../brand-writing-identity.md)

### issue-2026-06-15-view-proof-gap

- **kind:** missing
- **confidence:** medium
- **component:** customer-proof
- **surface:** gallivant-view
- **detail:** View page explains finance features but has no customer proof. Homepage quotes are traveler-focused; finance buyers may need a View-specific proof point (on-site renewal story is internal-only in origin reference).
- **suggested action:** Interview finance champion from on-site visit (with permission) or add anonymized outcome metric per [canon-proof.md](../canon-proof.md)

### issue-2026-06-01-capture-keyword

- **kind:** opportunity
- **confidence:** low
- **component:** topics
- **surface:** content-index
- **detail:** GSC-style gap (fictional): "expense capture at point of sale" queries rising; [blog-sunday-night-receipts](../content-index.md) partially covers theme but doesn't target phrase.
- **suggested action:** Add topic row in [canon-themes.md](../canon-themes.md) or spin follow-up post

## Resolved (fictional)

### issue-2026-05-10-homepage-quotes

- **kind:** missing → **resolved**
- **detail:** Homepage lacked customer voice; Alice obtained two verbatim quotes now in [canon-proof.md](../canon-proof.md).
