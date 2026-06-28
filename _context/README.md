# Example context layer (Gallivant)

Fictional messaging context for demo and learning. **Not a real company** — replace with your own canon for production.

The company is **Gallivant** — enterprise travel and expense management, shaped by founders Alice and Becca. The raw character and product reference lives in [reference/gallivant-origin.md](reference/gallivant-origin.md). Everything else in this folder is structured messaging derived from that source, following the [context-builder](https://github.com/janessa-lantz/context-builder) model.

`_context/` lives at the **repo root** (next to `config.json` and `_workflows/`). Skills read from `{workspace_root}/_context/`.

| File / folder | Role |
|---------------|------|
| [reference/gallivant-origin.md](reference/gallivant-origin.md) | Canonical narrative reference (founders, voice, product in their words) |
| [messaging-canon.md](messaging-canon.md) | Index of approved messaging by component group |
| `canon-*.md` | One approved statement per messaging component |
| [brand-writing-identity.md](brand-writing-identity.md) | Voice, guardrails, lexicon |
| [brand-visual-identity.md](brand-visual-identity.md) | Observable design facts |
| [content-index.md](content-index.md) | Registry of published assets and which components they carry |
| [entities/](entities/) | Raw intelligence on outside actors — not vetted for publication |
| [issues/](issues/) | Example analyzer findings (drift, gaps) for humans to act on |

For production, replace Gallivant files with your company's messaging canon.

## Messaging components

Stable kebab-case IDs group everything. There are 24 components across six groups — see the component list in context-builder's [context README](https://github.com/janessa-lantz/context-builder/blob/main/context/README.md).

## Trust levels

| Layer | Safe to ship? |
|-------|----------------|
| Canon, brand identity, content index | Yes — human-validated |
| Entity profiles and feeds | No — raw intelligence; build battlecards separately |
| Origin reference | Internal — character truth; cite, do not paste wholesale into ads |
| Issues folder | Internal workflow — analyzer output, not customer-facing |
