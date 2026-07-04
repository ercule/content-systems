---
name: browser_automation
description: >-
  Preferred browser path when REST or Google API cannot complete a step. Check
  config.json for Browserbase availability; use Browserbase + Playwright when
  enabled and credentialed; fall back to Chrome DevTools MCP otherwise. Link from
  any skill that marks Browser (wp-admin) or Browser Fallback in its routing table.
  REQUIRED: post Browserbase live view URL to the user immediately after session
  create (see Live session link section); never only in run-debug logs.
"last updated": 2026-06-28T23:30:00+00:00
"last run": 2026-06-28
---

# Browser automation (shared)

Read [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md) before running this step.

Log prefix: `[run-debug] browser=… | …`

## When to use

Any skill that routes an operation to **Browser (wp-admin)**, **Fallback**, or **Browser fallback** links here for how to drive the browser. The caller skill owns what to do in wp-admin; this skill owns which browser path to use and how to connect.

Prefer REST or HTTP APIs when they work. Switch to a browser path as soon as an API path is blocked — do not report the run complete with missing CMS fields.

## Path preference

1. **Browserbase + Playwright** — preferred when available (see availability check below)
2. **Chrome DevTools MCP** (`user-chrome-devtools`) — when Browserbase is not configured or session creation fails

Do not ask the user which path to use. Pick automatically from the check below.

## Availability check (required before Browserbase)

Read `{workspace_root}/config.json` and resolve `{workspace_root}/credentials.json` per [setup/run_workflow/SKILL.md](../../../setup/run_workflow/SKILL.md).

Browserbase is **available** only when all of the following are true:

- `config.browserbase.enabled` is exactly `true`
- Resolved `browserbase.api_key` is a non-empty string

Optional but recommended: `config.browserbase.project_id` (non-secret; Browserbase can infer project from the API key when omitted).

```text
[run-debug] browser=browserbase | available=true|false | enabled=… | api_key=set|missing | project_id=…
```

If `available=false`, skip Browserbase and use Chrome DevTools MCP immediately. Do not stop the run or ask the user unless both paths fail login.

## Browserbase session

Dependencies (install once per environment when missing):

```bash
pip install browserbase playwright
playwright install chromium
```

### Live session link (required — repeat while session is open)

Every time you create a Browserbase session, fetch the Live View URL and **keep repeating it in user-facing replies until the session closes**.

User-facing format (paste at the top of every message while BB is running; repeat again immediately before any ask):

```markdown
## Browserbase live session

**Watch / interact:** {debugger_fullscreen_url}

Session: `{session_id}` · Replay after close: https://browserbase.com/sessions/{session_id}
```

1. `session = bb.sessions.create(...)`
2. `live = bb.sessions.debug(session.id)` — while the session is still running
3. Post the block above in chat **before** long automation. **Repeat it**:
   - at the start of every subsequent message while the session is open
   - immediately above any login/handoff instruction or question to the user
   - after launching BB scripts (read `live=` from terminal output and paste the block)
4. URLs:
   - **Live (interactive):** `live.debugger_fullscreen_url`
   - **Replay (after close):** `https://browserbase.com/sessions/{session.id}`

Repeat the live session URL block in terminal output every ~15s during waits (not only once at session start):

```text
[run-debug] browser=browserbase | session_id={id} | live={debugger_fullscreen_url} | replay=https://browserbase.com/sessions/{id}
```

Do not wait until the end of the run to surface the live link — the session may close first. Fetch `debug` right after `create`, before long automation steps.

If the user may need to intervene (login, MFA, cookie banner, upload), pause automation, **repeat the live URL block**, then tell them what to do. Resume Playwright/CDP control after they finish.

Use `keep_alive=True` on `sessions.create` when a human handoff may take more than a minute.

### Saved contexts (reuse auth)

When `config.browserbase.contexts.<name>.id` is set (non-secret), create sessions with that context so login persists across runs. Read the id from `{workspace_root}/config.json`.

| Context key | Use |
|-------------|-----|
| `asana` | Saved login for a third-party web app (configure per workspace in `config.json`) |

```python
context_id = config["browserbase"]["contexts"]["asana"]["id"]
session = bb.sessions.create(
    project_id=project_id,
    keep_alive=True,
    browser_settings={"context": {"id": context_id, "persist": True}},
)
```

- **`persist: false`** — read-only; use when auth is already saved and you must not overwrite cookies.
- **`persist: true`** — write changes back to the context when the session is released (`sessions.update(id, status="REQUEST_RELEASE")`). Use after a fresh login handoff to save new auth.

First-time login handoff: create session without a context (or with `persist: true` on a new context), give the user the live link, wait for login, then release the session and store the context id in `config.json`.

Re-auth: if a saved context stops working (Asana forced logout), repeat the handoff and update `contexts.asana.id` or create a new context.

### Connect pattern

```python
from playwright.sync_api import sync_playwright
from browserbase import Browserbase

bb = Browserbase(api_key=api_key)
session = bb.sessions.create(project_id=project_id, keep_alive=True)
live = bb.sessions.debug(session.id)
live_url = live.debugger_fullscreen_url
replay_url = f"https://browserbase.com/sessions/{session.id}"
print(f"[run-debug] browser=browserbase | session_id={session.id} | live={live_url} | replay={replay_url}")
# Always include live_url in the user-facing reply when starting a BB session.

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    # caller-specific automation (login, upload, save draft, etc.)
```

REST equivalent when not using the SDK:

```text
GET https://api.browserbase.com/v1/sessions/{session_id}/debug
X-BB-API-Key: {api_key}
```

Response field: `debuggerFullscreenUrl`.

Credentials:

| Key | File | Notes |
|-----|------|-------|
| `browserbase.api_key` | `credentials.json` | Secret. May use `@credentials.json#browserbase.api_key`. |
| `browserbase.enabled` | `config.json` | Must be `true` to attempt Browserbase. |
| `browserbase.project_id` | `config.json` | Non-secret project UUID. |

Do not log the API key. Echo session id, live URL, and replay URL only.

On session or CDP connect failure after one retry, log the error and fall back to Chrome DevTools MCP for the same operation.

## Playwright + CDP pitfalls (wp-admin)

Learned on wp-admin ACF repeater fills; apply to any long `page.evaluate()` against wp-admin:

| Pitfall | Fix |
|---------|-----|
| **`TargetClosedError` mid-fill** | BB session or tab closed (save reload, timeout, user). Use `keep_alive=True`; save **outside** evaluate; resume with `sessions.retrieve(id)` + CDP reconnect, or start a new session. |
| **`page.evaluate(..., timeout=N)`** | Sync Playwright API does **not** accept `timeout` on `evaluate`. Use `page.set_default_timeout(ms)` before long scripts. |
| **Infinite repeater loops** | ACF `add-row` is async. Never `while (rows < n) click()` — use delayed `ensureRows($rep, n, done)` instead. |
| **Save during evaluate** | `#save-post` inside JS can navigate and kill the evaluation context. Fill in JS; `page.click('#save-post')` from Python after evaluate returns. |
| **Relative admin URLs** | Duplicate-plugin links like `admin.php?action=dt_duplicate_post_as_draft&post=…` need `urljoin(f"{base}/wp-admin/", href)` before `page.goto`. |
| **wp-login vs REST creds** | Application passwords work for REST/GraphQL only. Browser login on `wp-login.php` uses `credentials.json` → `wordpress` (human password field), not `workflow_specific.update_agent.wordpress.app_password`. |
| **Import `browserbase_live`** | Add `{workspace_root}/scripts` to `sys.path` before `from lib.browserbase_live import LiveSessionReporter`. |

### Resume an open session

When the user is already logged in via the live BB view, reconnect without creating a new session:

```python
session = bb.sessions.retrieve(session_id)
live = bb.sessions.debug(session_id)
# share live.debugger_fullscreen_url with user (repeat while open)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.contexts[0].pages[0] or browser.contexts[0].new_page()
    # poll until "wp-admin" in page.url and "wp-login" not in page.url
```

Caller example: `{workspace_root}/_workflows/{name}/resume_browserbase_session.py {session_id}`.

Release when done: `bb.sessions.update(session_id, status="REQUEST_RELEASE")`.

### One page per session (debugging)

For fragile multi-step wp-admin work, run **one page/mock per BB session** so a failed fill does not poison the browser context for the next duplicate. Re-login is cheap once auto-fill or saved context works.

## Chrome DevTools MCP fallback

When Browserbase is unavailable or fails, use `user-chrome-devtools`:

| Tool | Use |
|------|-----|
| `navigate_page` | Open login or editor URLs |
| `click`, `fill` | Form interaction |
| `upload_file` | Media / featured image upload |
| `take_snapshot` | Confirm page state before and after edits |

Log: `[run-debug] browser=chrome-devtools-mcp | reason=browserbase_unavailable|session_failed|…`

Typical WordPress login: navigate to `{base_url}/wp-login.php`, sign in with workspace WordPress credentials (`credentials.json` → `wordpress`, not REST app password unless confirmed working on login form), confirm with `take_snapshot` before editing.

## Do not stop early

Complete the browser step unless login is impossible on both paths. Do not ask the user to finish by hand when either automation path can still run.
