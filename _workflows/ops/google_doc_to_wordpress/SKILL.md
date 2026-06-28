---
name: google_doc_to_wordpress
description: >-
  Generic skill for publishing Google Doc drafts as WordPress posts.
  Step 00 runs once to discover the WordPress environment, inspect a sample doc,
  and produce a config.json. Steps 01–03 repeat for every subsequent publish run.
"last updated": 2026-06-01T00:58:47+00:00
"last run": 2026-06-01T00:58:47+00:00
---

# Google Doc to WordPress

Step 0: Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) (workflow standards: runtime HTTP, logging, ephemeral rules).

Log line prefix:

`[run-debug] workflow=google-doc-to-wordpress | <PHASE> | <facts>`

## First-time setup

Run step 00 once per workspace/site. It produces a `config.json` that drives all subsequent runs.

1. [00-discover-and-configure/SKILL.md](00_discover_and_configure/SKILL.md)

## Publish a doc (repeating)

Run steps 01–03 for each doc. Requires a completed `config.json` from step 00.

2. [01-fetch-and-parse/SKILL.md](01_fetch_and_parse/SKILL.md)
3. [02-build-post/SKILL.md](02_build_post/SKILL.md)
4. [03-publish/SKILL.md](03_publish/SKILL.md)

## Credentials

Store per-workspace credentials separately from this shared skill. Expected shape:

```json
{
  "wordpress": {
    "site_url": "https://example.com",
    "username": "your-username",
    "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
  },
  "google": {
    "token_pickle_base64": "<base64-encoded pickle>"
  }
}
```

WordPress requires an Application Password, not the account login password.
Generate one at: `{site_url}/wp-admin/profile.php` → Application Passwords.
