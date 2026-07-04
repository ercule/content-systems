---
name: publish_wp_04_publish
description: >-
  Step 3: POST the assembled payload to the WordPress REST API and report
  the post ID, edit URL, and public URL.
"last updated": 2026-06-28T23:30:00+00:00
"last run": never
---

# Publish WordPress from Google Doc — 03 Publish

Read [setup/run_workflow/SKILL.md](../../../../setup/run_workflow/SKILL.md) before running this step.

Log line prefix: `[run-debug] workflow=publish-wordpress-from-google-doc | <PHASE> | <facts>`

## Inputs

- `POST_PAYLOAD` from step 2
- `config.json` — read `wordpress.site_url`, `wordpress.username`, `wordpress.app_password`, `wordpress.post_type`

## Build request

WP_API = `{site_url}/wp-json/wp/v2`
Endpoint = `{WP_API}/{post_type}`
Auth = Basic `base64("{username}:{app_password}")`

## POST

POST `{Endpoint}` with Basic auth, `Content-Type: application/json`, body = `POST_PAYLOAD`.

Log: `WP_REQ | endpoint={Endpoint} slug={SLUG} status_field={status}`

Expect HTTP 200 or 201. On any other status, log the full response body and stop.

## Report

From the response extract: `id`, `link` (public URL), `guid.rendered` if available.

Log: `WP_OK | post_id={id} status={status}`

Print:
- Post ID: `{id}`
- Edit URL: `{site_url}/wp-admin/post.php?post={id}&action=edit`
- Public URL: `{link}` (only meaningful if status is `publish`)
