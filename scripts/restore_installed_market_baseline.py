#!/usr/bin/env python3
"""Restore a promoted installed-state baseline from baseline history."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from market_utils import ROOT, load_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Restore a promoted installed-state baseline from baseline history.")
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("entry", help="History entry sequence number or 'latest'.")
    parser.add_argument("--baseline-path", type=Path, help="Optional restore destination for the baseline JSON.")
    parser.add_argument("--markdown-path", type=Path, help="Optional restore destination for the baseline Markdown summary.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def resolve_optional_repo_path(value: object) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    return resolve_repo_path(Path(text))


def resolve_history_entry(history_payload: dict, token: str) -> dict:
    entries = history_payload.get("entries", [])
    if not isinstance(entries, list) or not entries:
        raise ValueError("baseline history does not contain any entries")
    normalized = token.strip().lower()
    if normalized == "latest":
        entry = entries[-1]
        if not isinstance(entry, dict):
            raise ValueError("latest history entry is invalid")
        return entry
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("sequence", "")).strip() == token.strip():
            return entry
    raise ValueError(f"baseline history entry not found: {token}")


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    history_path = resolve_repo_path(args.history)
    history_payload = load_json(history_path)
    try:
        entry = resolve_history_entry(history_payload, args.entry)
    except ValueError as exc:
        raise SystemExit(str(exc))

    archived_baseline_path = resolve_repo_path(Path(str(entry.get("archived_baseline_path", ""))))
    if not archived_baseline_path.is_file():
        raise SystemExit(f"archived baseline is missing: {archived_baseline_path}")
    archived_markdown_path = resolve_optional_repo_path(entry.get("archived_baseline_markdown_path"))
    if archived_markdown_path and not archived_markdown_path.is_file():
        archived_markdown_path = None

    baseline_path = resolve_repo_path(args.baseline_path) if args.baseline_path else resolve_optional_repo_path(entry.get("baseline_path"))
    if baseline_path is None:
        raise SystemExit("baseline restore destination is missing from the history entry")
    markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else resolve_optional_repo_path(entry.get("baseline_markdown_path"))
    if archived_markdown_path and markdown_path is None:
        markdown_path = baseline_path.with_suffix(".md")

    copy_file(archived_baseline_path, baseline_path)
    if archived_markdown_path and markdown_path is not None:
        copy_file(archived_markdown_path, markdown_path)

    payload = {
        "history_path": str(history_path),
        "restored_sequence": entry.get("sequence"),
        "baseline_path": str(baseline_path),
        "baseline_markdown_path": str(markdown_path) if archived_markdown_path and markdown_path is not None else None,
        "archived_baseline_path": str(archived_baseline_path),
        "archived_baseline_markdown_path": str(archived_markdown_path) if archived_markdown_path else None,
        "summary": entry.get("summary", {}),
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed market baseline restore:")
    print(f"- History: {payload['history_path']}")
    print(f"- Restored sequence: {payload['restored_sequence']}")
    print(f"- Baseline JSON: {payload['baseline_path']}")
    if payload["baseline_markdown_path"]:
        print(f"- Baseline Markdown: {payload['baseline_markdown_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
