---
name: publish_wordpress_from_google_doc
description: >-
  Generic skill for publishing Google Doc drafts as WordPress posts.
  Step 01 runs once to discover the WordPress environment, inspect a sample doc,
  and produce a config.json. Steps 02–04 repeat for every subsequent publish run.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-01T00:58:47+00:00
---

# Publish WordPress from Google Doc

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix:

`[run-debug] workflow=publish-wordpress-from-google-doc | <PHASE> | <facts>`

## First-time setup

Run step 01 once per workspace/site. It produces a `config.json` that drives all subsequent runs.

1. [01_preflight_discover/SKILL.md](01_preflight_discover/SKILL.md)

## Publish a doc (repeating)

Run steps 02–04 for each doc. Requires a completed `config.json` from step 01.

2. [02_fetch_and_parse/SKILL.md](02_fetch_and_parse/SKILL.md)
3. [03_build_post/SKILL.md](03_build_post/SKILL.md)
4. [04_publish/SKILL.md](04_publish/SKILL.md)

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
