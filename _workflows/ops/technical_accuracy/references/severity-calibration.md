# Severity calibration — worked examples

The six severity tiers (see SKILL.md step 5) each have a yes/no test, but the tests alone leave room for two independent reviewers (or two subagents with no shared context) to land on different tiers for a genuinely borderline claim. This file exists to anchor those calls with concrete examples, especially for the pairs most likely to get confused. When a real review surfaces a new confusable pair, add a worked example for it here rather than just re-explaining the abstract test better — this file is meant to grow.

**Severe** — *"TCP uses UDP as its transport layer."* Backwards in a way anyone can catch without networking background — no domain knowledge required to notice these are two different named things being confused.

**Incorrect** — *"IETF RFC 7336 defines a structure for cross-CDN log exchange."* Needs domain knowledge to catch (you have to know RFC 7336 is the general framework doc, not the logging spec) — a general reader has no way to independently notice this. But it's not "medium wrong": a primary source directly contradicts it (RFC 7336 itself defers logging specifics elsewhere; RFC 7937 is the document that actually defines the exchange format). Incorrect = needs expertise to catch, but a source flatly contradicts it.

**Outdated vs. Incorrect** — the pair most likely to get confused, so a worked comparison:
Claim: *"Purging a CDN cache takes seconds to minutes, propagation isn't uniform across regions."*
- Not Incorrect — it's still true for some providers today (Akamai's VOD purge can run up to 120 minutes).
- Is Outdated — Cloudflare and Fastly's own engineering blogs document a real before/after: purge times for the market leaders dropped to sub-150ms as a documented achievement. The claim was accurate as a general statement and has since been superseded for part of the market.
- **The test:** was there a point when this was accurate, and can you find a source marking when/how it changed? Yes → Outdated. Never true at all → Incorrect.

**Outdated vs. Imprecise** — second pair worth anchoring:
Claim: *"A hit rate above 85% is reasonable; below 50% points to a problem."*
- Looks like it could be Imprecise (nothing about what a hit ratio *is* is wrong) — but that's the wrong call here.
- Is Outdated — current vendor guidance (Akamai's own offload docs, 2026 industry benchmarks) shows the accepted "good" and "problem" thresholds have moved: 90%+ is now standard, and the "something's wrong" line sits well above 50%. The number was once a reasonable approximation and has drifted out of step with current norms.
- **The test:** does the fix mean adding back an omitted detail (Imprecise), or swapping a stale calibration point for a current one (Outdated)? Here, the latter.

**Imprecise** — *"The atmosphere is made up of the exosphere and the troposphere."* Both named layers are real and correctly described — nothing stated is false. But omitting the other layers (mesosphere, stratosphere, thermosphere) changes the reader's picture of how the atmosphere is actually structured. **The test:** if you added back what's omitted, would the takeaway change? Yes → Imprecise.

**Imprecise vs. Vague** — worked comparison:
Claim: *"CDNs generally offer good performance."*
- Is Vague, not Imprecise — there's no nameable fact being omitted, it's just stated too loosely to be informative.
- Contrast with the atmosphere example: that one omits specific, nameable content that would change the picture. This one isn't omitting anything specific — it's just underspecified.
- **The test:** is there a nameable fact missing that would change the takeaway (Imprecise), or does this just not say much (Vague)?

**Unverified** — *"These providers together account for roughly 80% of global CDN traffic."* After fetching multiple market-share sources (by site count, by revenue, by measured traffic), no source confirms this figure for this specific combination — the underlying methodologies disagree too much for a clean answer to exist. Unverified because fetches were actually attempted and came back inconclusive, not because nobody looked.
