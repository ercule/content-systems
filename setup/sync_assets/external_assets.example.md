Copy to `external_assets.md` at the workspace root and edit.

One asset per non-empty line. `#` starts an end-of-line comment.

```
[<output-filename>] <source>
```

Examples:

```markdown
# Approved positioning (repo copy)
positioning.md | _context/positioning.md

# Google Doc — requires Drive OAuth in credentials.json
approved-positioning.md | https://docs.google.com/document/d/EXAMPLE_DOC_ID/edit

# Web snapshot for drift analysis only — not canon
homepage.txt | https://example.com/
```
