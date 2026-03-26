#!/usr/bin/env python3
"""Prune installed-state baseline history entries and archived baseline files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import promote_installed_market_baseline
from market_utils import ROOT, load_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prune installed-state baseline history and archive artifacts.")
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--keep-last", type=int, required=True, help="Number of newest history entries to keep.")
    parser.add_argument("--history-markdown-path", type=Path, help="Optional Markdown history summary path.")
    parser.add_argument("--dry-run", action="store_true", help="Only print the planned prune result.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def resolve_optional_repo_path(value: object) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    return resolve_repo_path(Path(text))


def collect_archive_paths(entry: dict) -> list[Path]:
    keys = [
        "archived_baseline_path",
        "archived_baseline_markdown_path",
        "archived_transition_diff_path",
        "archived_transition_diff_markdown_path",
    ]
    paths: list[Path] = []
    for key in keys:
        path = resolve_optional_repo_path(entry.get(key))
        if path is not None:
            paths.append(path)
    return paths


def remove_archive_paths(paths: list[Path]) -> list[str]:
    removed: list[str] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        if path.exists():
            path.unlink()
            removed.append(str(path))
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.keep_last < 0:
        parser.error("--keep-last must be non-negative")

    history_path = resolve_repo_path(args.history)
    if not history_path.is_file():
        raise SystemExit(f"baseline history file does not exist: {history_path}")

    payload = load_json(history_path)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []
        payload["entries"] = entries

    previous_next_sequence = promote_installed_market_baseline.next_history_sequence(payload)
    keep_last = args.keep_last
    kept_entries = entries[-keep_last:] if keep_last > 0 else []
    pruned_entries = entries[:-keep_last] if keep_last > 0 else list(entries)
    pruned_sequences = [
        entry.get("sequence")
        for entry in pruned_entries
        if isinstance(entry, dict)
    ]
    retained_sequences = [
        entry.get("sequence")
        for entry in kept_entries
        if isinstance(entry, dict)
    ]

    archive_paths: list[Path] = []
    for entry in pruned_entries:
        if isinstance(entry, dict):
            archive_paths.extend(collect_archive_paths(entry))

    history_markdown_path = (
        resolve_repo_path(args.history_markdown_path)
        if args.history_markdown_path
        else history_path.with_suffix(".md")
    )

    removed_archive_paths: list[str] = []
    removed_archive_dir = False
    if not args.dry_run:
        removed_archive_paths = remove_archive_paths(archive_paths)
        payload["entries"] = kept_entries
        payload["next_sequence"] = previous_next_sequence
        payload["next_sequence"] = promote_installed_market_baseline.next_history_sequence(payload)
        promote_installed_market_baseline.write_text(
            history_path,
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        )
        promote_installed_market_baseline.write_text(
            history_markdown_path,
            promote_installed_market_baseline.render_history_markdown(payload),
        )
        archive_dir = resolve_optional_repo_path(payload.get("archive_dir"))
        if archive_dir is not None and archive_dir.is_dir() and not any(archive_dir.iterdir()):
            archive_dir.rmdir()
            removed_archive_dir = True

    result = {
        "history_path": str(history_path),
        "history_markdown_path": str(history_markdown_path),
        "keep_last": keep_last,
        "dry_run": args.dry_run,
        "before_count": len(entries),
        "after_count": len(kept_entries),
        "pruned_sequences": pruned_sequences,
        "retained_sequences": retained_sequences,
        "planned_archive_paths": [str(path) for path in archive_paths],
        "removed_archive_paths": removed_archive_paths,
        "removed_archive_dir": removed_archive_dir,
        "next_sequence": previous_next_sequence,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("Installed market baseline history prune:")
    print(f"- History JSON: {result['history_path']}")
    print(f"- History Markdown: {result['history_markdown_path']}")
    print(f"- Keep last: {result['keep_last']}")
    print(f"- Before count: {result['before_count']}")
    print(f"- After count: {result['after_count']}")
    print(f"- Pruned sequences: {', '.join(str(item) for item in pruned_sequences) if pruned_sequences else '(none)'}")
    print(f"- Retained sequences: {', '.join(str(item) for item in retained_sequences) if retained_sequences else '(none)'}")
    print(f"- Next sequence: {result['next_sequence']}")
    if args.dry_run:
        print(f"- Planned archive removals: {len(result['planned_archive_paths'])}")
    else:
        print(f"- Removed archive files: {len(result['removed_archive_paths'])}")
        print(f"- Removed empty archive dir: {'yes' if result['removed_archive_dir'] else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
