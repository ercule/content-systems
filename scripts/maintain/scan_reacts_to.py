#!/usr/bin/env python3
"""List workflow skills with reacts-to metadata and flag likely-due time triggers."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workspace import library_root  # noqa: E402

REPO_ROOT = library_root(__file__)
SKIP_DIR_NAMES = {".git", ".claude", "node_modules", "chrome"}
SUBMODULE_PREP_PREFIX = "_submodule_prep"
STEP_DIR_RE = re.compile(r"^[0-9]{2}_")
FM_BLOCK = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)
REACTS_TO_KEY = re.compile(
    r'^(?:"reacts to"|reacts-to|reacts_to)\s*:(?:[ \t]*([^\n]+))?$',
    re.MULTILINE | re.IGNORECASE,
)
LAST_RUN_KEY = re.compile(
    r'^(?:"last run"|last_run)\s*:\s*(.+)$',
    re.MULTILINE | re.IGNORECASE,
)
LIST_ITEM = re.compile(r"^\s*-\s+(.+)$")
WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "fourteen": 14,
    "twenty": 20,
    "thirty": 30,
    "sixty": 60,
    "ninety": 90,
}
DAYS_IN_TEXT = re.compile(
    r"((?:\d+|[a-z]+))\s+or\s+more\s+(day|week|month)s?\b|"
    r"((?:\d+|[a-z]+))\s+(day|week|month)s?\b|"
    r"\b(daily|weekly|monthly|biweekly|fortnight)\b",
    re.IGNORECASE,
)


@dataclass
class TriggerAssessment:
    text: str
    kind: str  # time | external | unknown
    due: bool | None  # None = needs agent judgment
    reason: str = ""
    issue: str = ""  # manual-run | vague-source | empty when valid


MANUAL_RUN_RE = re.compile(
    r"\b("
    r"ask(?:s|ed|ing)?|request(?:s|ed|ing)?|stakeholder|editorial|"
    r"manual(?:ly)?|ad[- ]?hoc|when asked|user provides|shares a|gives a|"
    r"someone asks|on demand|on-demand"
    r")\b",
    re.IGNORECASE,
)
SOURCE_DETAIL_RE = re.compile(
    r"https?://|docs\.google\.com|spreadsheets/d/[A-Za-z0-9_-]+|"
    r"@[A-Za-z0-9_]+|youtube\.com|sc-domain:|gid=\d+|"
    r"\bUC[A-Za-z0-9_-]{10,}\b",
    re.IGNORECASE,
)


@dataclass
class WorkflowTriggers:
    path: Path
    name: str
    last_run: str
    last_run_dt: datetime | None
    triggers: list[TriggerAssessment] = field(default_factory=list)

    @property
    def likely_due(self) -> bool:
        return any(t.due is True for t in self.triggers)


def should_skip(path: Path) -> bool:
    return any(
        p in SKIP_DIR_NAMES or p.startswith(SUBMODULE_PREP_PREFIX) for p in path.parts
    )


def is_step_skill(path: Path) -> bool:
    return bool(STEP_DIR_RE.match(path.parent.name))


def parse_frontmatter(text: str) -> str | None:
    m = FM_BLOCK.match(text)
    return m.group(1) if m else None


def parse_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    return value


def parse_last_run(fm: str) -> tuple[str, datetime | None]:
    m = LAST_RUN_KEY.search(fm)
    if not m:
        return "missing", None
    raw = parse_scalar(m.group(1))
    if raw.lower() == "never":
        return raw, None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(raw.replace("+00:00", "+0000"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return raw, dt
        except ValueError:
            continue
    return raw, None


def parse_reacts_to_list(fm: str) -> list[str]:
    m = REACTS_TO_KEY.search(fm)
    if not m:
        return []
    rest = (m.group(1) or "").strip()
    if rest.startswith("- "):
        rest = rest[2:].strip()
    if rest.startswith("[") and rest.endswith("]"):
        inner = rest[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",") if part.strip()]
    if rest:
        return [parse_scalar(rest)]

    lines = fm[m.end() :].splitlines()
    items: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_\"'].+\s*:", line) and not line.lstrip().startswith("-"):
            break
        lm = LIST_ITEM.match(line)
        if lm:
            items.append(parse_scalar(lm.group(1)))
    return items


def parse_name(fm: str) -> str:
    m = re.search(r"^name\s*:\s*(.+)$", fm, re.MULTILINE)
    return parse_scalar(m.group(1)) if m else ""


def parse_count(raw: str | None) -> int | None:
    if not raw:
        return None
    raw = raw.lower()
    if raw.isdigit():
        return int(raw)
    return WORD_NUMBERS.get(raw)


def days_threshold(text: str) -> int | None:
    lower = text.lower()
    m = DAYS_IN_TEXT.search(lower)
    if not m:
        return None
    or_more_count, or_more_unit, count, unit, word = m.groups()
    if word:
        mapping = {
            "daily": 1,
            "weekly": 7,
            "biweekly": 14,
            "fortnight": 14,
            "monthly": 30,
        }
        return mapping.get(word.lower())
    n = parse_count(or_more_count or count)
    if n is None:
        return None
    u = (or_more_unit or unit or "").lower()
    if u.startswith("day"):
        return n
    if u.startswith("week"):
        return n * 7
    if u.startswith("month"):
        return n * 30
    return None


def looks_external(text: str) -> bool:
    lower = text.lower()
    external_markers = (
        "sheet",
        "row",
        "column",
        "video",
        "youtube",
        "posted",
        "published",
        "incident",
        "breach",
        "report",
        "pane",
        "queue",
        "approved",
        "entry",
        "entries",
        "new ",
        "appears",
        "added",
        "not covered",
        "not yet",
    )
    return any(w in lower for w in external_markers)


def validate_trigger(text: str) -> str:
    if MANUAL_RUN_RE.search(text):
        return "manual-run wording — remove (on-demand runs are not reacts-to triggers)"
    if looks_external(text) and not SOURCE_DETAIL_RE.search(text):
        return "external source not specific enough — add URL, spreadsheet ID, channel, or property"
    return ""


def classify_trigger(text: str, last_run_dt: datetime | None, last_run_raw: str) -> TriggerAssessment:
    issue = validate_trigger(text)
    lower = text.lower()
    time_markers = (
        "day",
        "week",
        "month",
        "hour",
        "schedule",
        "interval",
        "cadence",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "quarter",
        "annual",
        "year",
    )

    threshold = days_threshold(text)
    looks_time = threshold is not None or any(w in lower for w in time_markers)
    external = looks_external(text)

    if issue:
        kind = "invalid"
        return TriggerAssessment(text, kind, None, issue, issue)

    if looks_time and threshold is not None:
        if last_run_raw.lower() == "never" or last_run_dt is None:
            return TriggerAssessment(text, "time", True, "last run is never or unparsed")
        age_days = (datetime.now(timezone.utc) - last_run_dt).total_seconds() / 86400
        if age_days >= threshold:
            return TriggerAssessment(
                text,
                "time",
                True,
                f"last run {age_days:.0f}d ago (threshold {threshold}d)",
            )
        return TriggerAssessment(
            text,
            "time",
            False,
            f"last run {age_days:.0f}d ago (threshold {threshold}d)",
        )

    if looks_time and (last_run_raw.lower() == "never" or last_run_dt is None):
        return TriggerAssessment(text, "time", True, "time-like trigger and last run is never")

    if external:
        return TriggerAssessment(text, "external", None, "fetch named source and compare to last run")

    if looks_time:
        return TriggerAssessment(text, "time", None, "time-like trigger; parse interval manually")

    return TriggerAssessment(text, "unknown", None, "needs manual judgment")


def collect_workflows() -> list[WorkflowTriggers]:
    found: list[WorkflowTriggers] = []
    for sp in sorted(REPO_ROOT.rglob("SKILL.md")):
        if should_skip(sp) or is_step_skill(sp):
            continue
        text = sp.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm:
            continue
        items = parse_reacts_to_list(fm)
        if not items:
            continue
        last_run_raw, last_run_dt = parse_last_run(fm)
        wf = WorkflowTriggers(
            path=sp,
            name=parse_name(fm),
            last_run=last_run_raw,
            last_run_dt=last_run_dt,
        )
        for item in items:
            wf.triggers.append(classify_trigger(item, last_run_dt, last_run_raw))
        found.append(wf)
    return found


def main() -> int:
    workflows = collect_workflows()
    invalid = [
        (w, t)
        for w in workflows
        for t in w.triggers
        if t.issue
    ]
    due = [w for w in workflows if w.likely_due]
    needs_check = [
        w
        for w in workflows
        if not w.likely_due and any(t.due is None and not t.issue for t in w.triggers)
    ]

    print(f"Workflow skills with reacts-to metadata: {len(workflows)}")
    print(f"Invalid reacts-to items: {len(invalid)}")
    print(f"Likely due (time-based): {len(due)}")
    print(f"Need external check: {len(needs_check)}")
    print()

    if invalid:
        print("=== INVALID REACTS TO (fix or remove) ===")
        current = None
        for w, t in invalid:
            rel = w.path.relative_to(REPO_ROOT)
            if rel != current:
                print(f"{rel} ({w.name or 'unnamed'})")
                current = rel
            print(f"  - {t.text}")
            print(f"    -> {t.issue}")
        print()

    if due:
        print("=== LIKELY DUE ===")
        for w in due:
            rel = w.path.relative_to(REPO_ROOT)
            print(f"{rel} ({w.name or 'unnamed'}) | last run: {w.last_run}")
            for t in w.triggers:
                if t.due:
                    print(f"  - {t.text}")
                    print(f"    -> {t.reason}")
        print()

    if needs_check:
        print("=== CHECK EXTERNAL SIGNALS ===")
        for w in needs_check:
            rel = w.path.relative_to(REPO_ROOT)
            print(f"{rel} ({w.name or 'unnamed'}) | last run: {w.last_run}")
            for t in w.triggers:
                if t.due is None and not t.issue:
                    print(f"  - [{t.kind}] {t.text}")
                    print(f"    -> {t.reason}")
        print()

    if workflows and not due and not needs_check and not invalid:
        print("All reacts-to workflows appear up to date on time-based triggers.")

    return 1 if invalid else 0


if __name__ == "__main__":
    sys.exit(main())
