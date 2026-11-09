#!/usr/bin/env python3
"""Index Codex sessions without a parent-thread marker, without full transcripts."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


def records(path: Path):
    if path.suffix == ".zst":
        proc = subprocess.Popen(
            ["zstd", "-dc", "-q", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            errors="replace",
        )
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
        finally:
            proc.kill()
            proc.wait()
    else:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def user_snippet(payload: dict) -> str:
    if payload.get("type") != "message" or payload.get("role") != "user":
        return ""
    parts = [part.get("text", "") for part in payload.get("content", []) if isinstance(part, dict)]
    text = " ".join(parts).strip()
    if "## My request:" in text:
        text = text.split("## My request:", 1)[1].strip()
    if not text or text.startswith(("<environment_context>", "<external_codex_apps_", "<recommended_plugins>", "# AGENTS.md instructions")):
        return ""
    return " ".join(text.split())[:180]


def inspect(path: Path) -> dict | None:
    stream = records(path)
    try:
        first = next(stream, None)
        if not first or first.get("type") != "session_meta":
            return None
        meta = first.get("payload", {})
        if meta.get("parent_thread_id"):
            return None
        snippet = ""
        for index, record in enumerate(stream):
            if index >= 500:
                break
            if record.get("type") == "response_item":
                snippet = user_snippet(record.get("payload", {}))
                if snippet:
                    break
        return {
            "date": str(meta.get("timestamp", ""))[:10],
            "thread_id": meta.get("id") or meta.get("session_id") or "",
            "cwd": meta.get("cwd") or "",
            "first_user_message": snippet,
            "archive_file": str(path),
        }
    finally:
        stream.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-root", type=Path, default=Path.home() / ".codex/sessions")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "sources/codex_root_sessions.tsv")
    args = parser.parse_args()
    paths = sorted([*args.sessions_root.rglob("*.jsonl"), *args.sessions_root.rglob("*.jsonl.zst")])
    rows = []
    for path in paths:
        row = inspect(path)
        if row:
            rows.append(row)
    # A long Codex thread can have several rollout archive files. Keep one
    # catalog row per thread, preferring its earliest useful opening message.
    rows.sort(key=lambda row: (row["date"], row["archive_file"]))
    by_id = {}
    for row in rows:
        prior = by_id.get(row["thread_id"])
        if prior is None or (not prior["first_user_message"] and row["first_user_message"]):
            by_id[row["thread_id"]] = row
    rows = sorted(by_id.values(), key=lambda row: (row["date"], row["thread_id"]), reverse=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["date", "thread_id", "cwd", "first_user_message", "archive_file"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Indexed {len(rows)} root sessions from {len(paths)} local archives: {args.output}")


if __name__ == "__main__":
    main()
