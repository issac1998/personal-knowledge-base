#!/usr/bin/env python3
"""Create a searchable metadata catalog from a ChatGPT data export ZIP or JSON."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def iso(value) -> str:
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return ""


def text_of(message: dict) -> str:
    content = message.get("content") or {}
    parts = content.get("parts") or []
    text = " ".join(part for part in parts if isinstance(part, str))
    return " ".join(text.split())[:180]


def rows_from(data, source: str):
    conversations = data if isinstance(data, list) else data.get("conversations", [])
    for conversation in conversations:
        if not isinstance(conversation, dict):
            continue
        mapping = conversation.get("mapping") or {}
        messages = []
        for node in mapping.values():
            if not isinstance(node, dict):
                continue
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            role = (message.get("author") or {}).get("role")
            if role in ("user", "assistant"):
                messages.append((message.get("create_time") or 0, role, message))
        messages.sort(key=lambda item: item[0])
        first_user = next((text_of(message) for _, role, message in messages if role == "user" and text_of(message)), "")
        yield {
            "conversation_id": conversation.get("id") or conversation.get("conversation_id") or "",
            "title": " ".join(str(conversation.get("title") or "").split())[:240],
            "created_at_utc": iso(conversation.get("create_time")),
            "updated_at_utc": iso(conversation.get("update_time")),
            "user_messages": sum(role == "user" for _, role, _ in messages),
            "assistant_messages": sum(role == "assistant" for _, role, _ in messages),
            "first_user_message": first_user,
            "source": source,
        }


def load_rows(path: Path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if re.search(r"(?:^|/)conversations(?:[-_]\d+)?\.json$", name)]
            for name in sorted(names):
                with archive.open(name) as stream:
                    yield from rows_from(json.load(stream), f"{path.name}:{name}")
    else:
        with path.open(encoding="utf-8") as stream:
            yield from rows_from(json.load(stream), path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="ChatGPT export ZIP or conversations JSON")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "sources/chatgpt_export_catalog.tsv")
    args = parser.parse_args()
    rows = list(load_rows(args.input))
    if not rows:
        parser.error("No conversations found in this export; no catalog was written")
    by_id = {row["conversation_id"]: row for row in rows if row["conversation_id"]}
    output_rows = sorted(by_id.values(), key=lambda row: row["updated_at_utc"], reverse=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["conversation_id", "title", "created_at_utc", "updated_at_utc", "user_messages", "assistant_messages", "first_user_message", "source"]
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Indexed {len(output_rows)} ChatGPT conversations: {args.output}")


if __name__ == "__main__":
    main()
