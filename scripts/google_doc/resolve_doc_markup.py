#!/usr/bin/env python3
"""Accept or reject inline editorial markup in a Google Doc (red strike / blue add).

Accept: delete red strikethrough text; keep blue text and reset it to default body style.
Reject: delete blue text; keep red text and reset it to default body style.

Markup colors match show_edits_in_google_doc inline markup defaults.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workspace import workspace_root  # noqa: E402

DELETE_RGB = (0.77, 0.13, 0.12)
ADD_RGB = (0.0, 0.4, 0.8)
RGB_TOLERANCE = 0.08


def load_token() -> str:
    creds = json.loads((workspace_root(__file__) / "credentials.json").read_text())
    oauth = creds["google"]["oauth_token_unified"]
    body = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": oauth["refresh_token"],
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
        }
    ).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def api(method: str, url: str, token: str, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def doc_id_from_arg(value: str) -> str:
    m = re.search(r"document/d/([a-zA-Z0-9-_]+)", value)
    if m:
        return m.group(1)
    if re.fullmatch(r"[a-zA-Z0-9-_]+", value):
        return value
    raise SystemExit(f"Invalid doc id or URL: {value}")


def rgb_close(actual: dict | None, target: tuple[float, float, float]) -> bool:
    if not actual:
        return False
    r = actual.get("red", 0)
    g = actual.get("green", 0)
    b = actual.get("blue", 0)
    return all(abs(c - t) <= RGB_TOLERANCE for c, t in zip((r, g, b), target))


def walk_text_runs(content: list) -> list[dict]:
    runs = []
    for el in content:
        if "paragraph" in el:
            for pe in el["paragraph"].get("elements", []):
                if "textRun" not in pe:
                    continue
                tr = pe["textRun"]
                text = tr.get("content", "")
                if not text:
                    continue
                style = tr.get("textStyle", {})
                runs.append(
                    {
                        "start": pe["startIndex"],
                        "end": pe["endIndex"],
                        "text": text,
                        "strikethrough": bool(style.get("strikethrough")),
                        "rgb": style.get("foregroundColor", {})
                        .get("color", {})
                        .get("rgbColor"),
                    }
                )
        elif "table" in el:
            for row in el["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    runs.extend(walk_text_runs(cell.get("content", [])))
    return runs


def classify_runs(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    deletions, additions = [], []
    for run in runs:
        is_delete = run["strikethrough"] and rgb_close(run["rgb"], DELETE_RGB)
        is_add = (not run["strikethrough"]) and rgb_close(run["rgb"], ADD_RGB)
        if is_delete:
            deletions.append(run)
        elif is_add:
            additions.append(run)
    return deletions, additions


def merge_ranges(runs: list[dict]) -> list[tuple[int, int]]:
    if not runs:
        return []
    ordered = sorted(runs, key=lambda r: r["start"])
    merged: list[tuple[int, int]] = []
    cur_start, cur_end = ordered[0]["start"], ordered[0]["end"]
    for run in ordered[1:]:
        if run["start"] <= cur_end:
            cur_end = max(cur_end, run["end"])
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = run["start"], run["end"]
    merged.append((cur_start, cur_end))
    return merged


def delete_ranges(token: str, doc_id: str, ranges: list[tuple[int, int]]) -> int:
    if not ranges:
        return 0
    requests = [
        {"deleteContentRange": {"range": {"startIndex": s, "endIndex": e}}}
        for s, e in sorted(ranges, key=lambda r: r[0], reverse=True)
    ]
    api(
        "POST",
        f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
        token,
        {"requests": requests},
    )
    return len(ranges)


def reset_ranges(token: str, doc_id: str, ranges: list[tuple[int, int]]) -> int:
    if not ranges:
        return 0
    requests = []
    for s, e in ranges:
        requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": s, "endIndex": e},
                    "textStyle": {
                        "strikethrough": False,
                        "foregroundColor": {
                            "color": {"rgbColor": {"red": 0, "green": 0, "blue": 0}}
                        },
                    },
                    "fields": "strikethrough,foregroundColor",
                }
            }
        )
    chunk = 80
    for i in range(0, len(requests), chunk):
        api(
            "POST",
            f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
            token,
            {"requests": requests[i : i + chunk]},
        )
    return len(ranges)


def fetch_body(token: str, doc_id: str) -> list:
    doc = api(
        "GET",
        f"https://docs.googleapis.com/v1/documents/{doc_id}?includeTabsContent=true",
        token,
    )
    tabs = doc.get("tabs") or []
    if tabs:
        return tabs[0]["documentTab"]["body"]["content"]
    return doc["body"]["content"]


def resolve(token: str, doc_id: str, mode: str, dry_run: bool) -> dict:
    body = fetch_body(token, doc_id)
    deletions, additions = classify_runs(walk_text_runs(body))
    del_ranges = merge_ranges(deletions)
    add_ranges = merge_ranges(additions)

    stats = {
        "deletion_runs": len(deletions),
        "addition_runs": len(additions),
        "deletion_ranges": len(del_ranges),
        "addition_ranges": len(add_ranges),
    }

    if dry_run:
        stats["mode"] = mode
        stats["dry_run"] = True
        return stats

    if mode == "accept":
        stats["deleted_ranges"] = delete_ranges(token, doc_id, del_ranges)
        body = fetch_body(token, doc_id)
        _, additions_left = classify_runs(walk_text_runs(body))
        stats["normalized_ranges"] = reset_ranges(
            token, doc_id, merge_ranges(additions_left)
        )
    elif mode == "reject":
        stats["deleted_ranges"] = delete_ranges(token, doc_id, add_ranges)
        body = fetch_body(token, doc_id)
        deletions_left, _ = classify_runs(walk_text_runs(body))
        stats["normalized_ranges"] = reset_ranges(
            token, doc_id, merge_ranges(deletions_left)
        )
    else:
        raise SystemExit(f"Unknown mode: {mode}")

    stats["mode"] = mode
    stats["dry_run"] = False
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc", help="Google Doc URL or document ID")
    parser.add_argument(
        "mode",
        choices=["accept", "reject"],
        help="accept = keep blue, delete red; reject = delete blue, restore red",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report markup counts without mutating the Doc",
    )
    args = parser.parse_args()
    doc_id = doc_id_from_arg(args.doc)

    try:
        token = load_token()
        stats = resolve(token, doc_id, args.mode, args.dry_run)
    except urllib.error.HTTPError as e:
        print(e.read().decode()[:500], file=sys.stderr)
        raise SystemExit(1) from e

    print(
        f"[run-debug] workflow=accept_edits_google_doc | RESOLVE | "
        f"mode={stats['mode']} | dry_run={stats['dry_run']} | "
        f"deletion_ranges={stats['deletion_ranges']} | addition_ranges={stats['addition_ranges']}"
    )
    if not stats["dry_run"]:
        print(
            f"[run-debug] deleted_ranges={stats.get('deleted_ranges', 0)} | "
            f"normalized_ranges={stats.get('normalized_ranges', 0)}"
        )
    print(f"https://docs.google.com/document/d/{doc_id}/edit")

    if stats["deletion_ranges"] == 0 and stats["addition_ranges"] == 0:
        print("No red/blue editorial markup found.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
