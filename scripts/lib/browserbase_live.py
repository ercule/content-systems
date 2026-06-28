"""Conspicuous Browserbase live-session URLs for scripts and agent handoffs."""

from __future__ import annotations

import sys
import time


def replay_url(session_id: str) -> str:
    return f"https://browserbase.com/sessions/{session_id}"


def chat_block(session_id: str, live_url: str, *, reason: str = "", replay: str | None = None) -> str:
    """Markdown block agents should paste into chat (repeat while session is open)."""
    lines = [
        "## Browserbase live session",
        "",
        f"**Watch / interact:** {live_url}",
        "",
        f"Session: `{session_id}` · Replay after close: {replay or replay_url(session_id)}",
    ]
    if reason:
        lines.extend(["", reason])
    return "\n".join(lines)


def _banner(session_id: str, live_url: str, *, reason: str, replay: str | None) -> str:
    rule = "=" * 72
    parts = [
        "",
        rule,
        ">>> BROWSERBASE LIVE SESSION <<<",
        "",
        live_url,
        "",
        f"session={session_id}  replay={replay or replay_url(session_id)}",
    ]
    if reason:
        parts.extend(["", reason])
    parts.extend([rule, ""])
    return "\n".join(parts)


class LiveSessionReporter:
    """Print live URL loudly; repeat on waits and before any user-facing ask."""

    def __init__(self, session_id: str, live_url: str, replay: str | None = None) -> None:
        self.session_id = session_id
        self.live_url = live_url
        self.replay = replay or replay_url(session_id)
        self._last_print = 0.0

    def chat_block(self, reason: str = "") -> str:
        return chat_block(self.session_id, self.live_url, reason=reason, replay=self.replay)

    def print_open(self, reason: str = "Session started — open the live link to watch or help.") -> None:
        print(_banner(self.session_id, self.live_url, reason=reason, replay=self.replay), flush=True)
        self._last_print = time.time()

    def print_reminder(self, reason: str, *, min_interval_sec: float = 15.0, force: bool = False) -> None:
        now = time.time()
        if not force and now - self._last_print < min_interval_sec:
            return
        print(_banner(self.session_id, self.live_url, reason=reason, replay=self.replay), flush=True)
        self._last_print = now

    def print_before_ask(self, ask: str) -> None:
        self.print_reminder(ask, force=True)

    def run_debug(self) -> str:
        return (
            f"[run-debug] browser=browserbase | session_id={self.session_id} | "
            f"live={self.live_url} | replay={self.replay}"
        )


def add_lib_to_path(from_file: str) -> None:
    from workspace import library_root

    lib = library_root(from_file) / "scripts"
    path = str(lib)
    if path not in sys.path:
        sys.path.insert(0, path)
