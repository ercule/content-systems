#!/usr/bin/env python3
"""Apply inline red-strikethrough / blue-addition editorial markup to a Google Doc.

Reads a JSON plan (replaces, inserts, section blocks) and applies markup via
documents.batchUpdate. Palette matches show_edits_in_google_doc defaults.
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

RED = {"red": 0.77, "green": 0.13, "blue": 0.12}
BLUE = {"red": 0.0, "green": 0.4, "blue": 0.8}


def load_token() -> str:
    oauth = json.loads((workspace_root(__file__) / "credentials.json").read_text())[
        "google"
    ]["oauth_token_unified"]
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


def batch(doc_id: str, token: str, requests: list, label: str):
    chunk = 80
    for i in range(0, len(requests), chunk):
        api(
            "POST",
            f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
            token,
            {"requests": requests[i : i + chunk]},
        )
    print(f"[run-debug] inline_markup | pass={label} | requests={len(requests)}")


def fetch_body(doc_id: str, token: str) -> list:
    doc = api(
        "GET",
        f"https://docs.googleapis.com/v1/documents/{doc_id}?includeTabsContent=true",
        token,
    )
    tabs = doc.get("tabs") or []
    return tabs[0]["documentTab"]["body"]["content"] if tabs else doc["body"]["content"]


def build_index(body: list) -> tuple[str, list]:
    full, spans = "", []
    for el in body:
        if "paragraph" not in el:
            continue
        for pe in el["paragraph"].get("elements", []):
            if "textRun" not in pe:
                continue
            t = pe["textRun"].get("content", "")
            if not t:
                continue
            fs = len(full)
            full += t
            spans.append((fs, fs + len(t), pe["startIndex"], pe["endIndex"], t))
    return full, spans


def char_to_api(spans, pos: int) -> int:
    for fs, fe, s, e, _ in spans:
        if fs <= pos < fe:
            return s + (pos - fs)
    for fs, fe, s, e, _ in spans:
        if pos == fe:
            return e
    raise ValueError(f"unmap {pos}")


def find_range(full: str, spans, needle: str, occurrence: int = 1) -> tuple[int, int]:
    idx = -1
    for _ in range(occurrence):
        idx = full.find(needle, idx + 1)
    if idx < 0:
        raise ValueError(f"not found: {needle[:70]!r}")
    end = idx + len(needle)
    return char_to_api(spans, idx), char_to_api(spans, end)


def strike_style(s: int, e: int) -> dict:
    return {
        "updateTextStyle": {
            "range": {"startIndex": s, "endIndex": e},
            "textStyle": {
                "foregroundColor": {"color": {"rgbColor": RED}},
                "strikethrough": True,
            },
            "fields": "foregroundColor,strikethrough",
        }
    }


def blue_style(s: int, e: int) -> dict:
    return {
        "updateTextStyle": {
            "range": {"startIndex": s, "endIndex": e},
            "textStyle": {"foregroundColor": {"color": {"rgbColor": BLUE}}},
            "fields": "foregroundColor",
        }
    }


def para_style(s: int, e: int, named: str) -> dict:
    return {
        "updateParagraphStyle": {
            "range": {"startIndex": s, "endIndex": e},
            "paragraphStyle": {"namedStyleType": named},
            "fields": "namedStyleType",
        }
    }


def load_plan(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Plan JSON must be an object")
    return data


def pass_color_markup(doc_id: str, token: str, body: list, plan: dict):
    replaces = [tuple(pair) for pair in plan.get("replaces", [])]
    insert_after = [tuple(pair) for pair in plan.get("insert_after", [])]
    strike_only = list(plan.get("strike_only", []))

    full, spans = build_index(body)
    ops = []
    for old, new in replaces:
        s, e = find_range(full, spans, old)
        ops.append(("replace", s, e, new))
    for anchor, text in insert_after:
        _, e = find_range(full, spans, anchor)
        ops.append(("insert", e, e, text))
    for old in strike_only:
        s, e = find_range(full, spans, old)
        ops.append(("strike", s, e, ""))

    ops.sort(key=lambda o: o[1], reverse=True)
    requests = []
    for kind, s, e, text in ops:
        if kind == "replace":
            requests.append({"insertText": {"location": {"index": e}, "text": text}})
            requests.append(blue_style(e, e + len(text)))
            requests.append(strike_style(s, e))
        elif kind == "insert":
            requests.append({"insertText": {"location": {"index": e}, "text": text}})
            requests.append(blue_style(e, e + len(text)))
        elif kind == "strike":
            requests.append(strike_style(s, e))
    if requests:
        batch(doc_id, token, requests, "color")


def pass_insert_section(doc_id: str, token: str, body: list, plan: dict):
    section = plan.get("insert_section")
    if not section:
        return
    insert_before = section["insert_before"]
    blocks = [(b["style"], b["text"]) for b in section["blocks"]]
    full, spans = build_index(body)
    at, _ = find_range(full, spans, insert_before)
    text = "".join(t for _, t in blocks)
    requests = [{"insertText": {"location": {"index": at}, "text": text}}]
    requests.append(blue_style(at, at + len(text)))
    batch(doc_id, token, requests, "insert_section")


def pass_paragraph_styles(doc_id: str, token: str, body: list, plan: dict):
    section = plan.get("insert_section")
    if not section:
        return
    anchor = section.get("paragraph_style_anchor")
    blocks = [(b["style"], b["text"]) for b in section.get("blocks", [])]
    if not anchor or not blocks:
        return
    full, spans = build_index(body)
    start = full.find(anchor)
    if start < 0:
        print("[run-debug] inline_markup | pass=paragraph_styles | skipped (anchor not found)")
        return
    pos = start
    requests = []
    for named, chunk in blocks:
        s = char_to_api(spans, pos)
        pos += len(chunk)
        e = char_to_api(spans, pos)
        requests.append(para_style(s, e, named))
    batch(doc_id, token, requests, "paragraph_styles")


def pass_trim(doc_id: str, token: str, plan: dict):
    trim = plan.get("trim_replacements", [])
    if not trim:
        return
    requests = [
        {
            "replaceAllText": {
                "containsText": {"text": old, "matchCase": True},
                "replaceText": new,
            }
        }
        for old, new in trim
    ]
    batch(doc_id, token, requests, "trim_empty_paragraphs")


def doc_id_from_arg(value: str) -> str:
    m = re.search(r"document/d/([a-zA-Z0-9-_]+)", value)
    if m:
        return m.group(1)
    if re.fullmatch(r"[a-zA-Z0-9-_]+", value):
        return value
    raise SystemExit(f"Invalid doc id or URL: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc", help="Google Doc URL or document ID")
    parser.add_argument(
        "--plan",
        required=True,
        type=Path,
        help="JSON plan file (replaces, insert_after, strike_only, insert_section, trim_replacements)",
    )
    args = parser.parse_args()
    doc_id = doc_id_from_arg(args.doc)
    plan = load_plan(args.plan)
    if not any(
        plan.get(k)
        for k in ("replaces", "insert_after", "strike_only", "insert_section")
    ):
        raise SystemExit("Plan must include at least one of: replaces, insert_after, strike_only, insert_section")

    try:
        token = load_token()
        print(f"[run-debug] workflow=show_edits_in_google_doc | APPLY_INLINE | doc_id={doc_id}")
        body = fetch_body(doc_id, token)
        pass_color_markup(doc_id, token, body, plan)
        body = fetch_body(doc_id, token)
        pass_insert_section(doc_id, token, body, plan)
        body = fetch_body(doc_id, token)
        pass_paragraph_styles(doc_id, token, body, plan)
        pass_trim(doc_id, token, plan)
    except urllib.error.HTTPError as e:
        print(e.read().decode()[:500], file=sys.stderr)
        raise SystemExit(1) from e
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1) from e

    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
