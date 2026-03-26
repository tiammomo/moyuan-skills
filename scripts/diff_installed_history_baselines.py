#!/usr/bin/env python3
"""Diff two archived installed baseline history entries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import diff_installed_market_snapshots
import verify_installed_history_baseline
from market_utils import ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two archived installed baseline history entries and report their changes."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("before_entry", help="Older history entry sequence number or 'latest'.")
    parser.add_argument("after_entry", help="Newer history entry sequence number or 'latest'.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON diff output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown diff output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_history_diff_payload(history_path: Path, before_entry_token: str, after_entry_token: str) -> dict:
    _, before_entry, before_baseline_path = verify_installed_history_baseline.resolve_archived_baseline(history_path, before_entry_token)
    _, after_entry, after_baseline_path = verify_installed_history_baseline.resolve_archived_baseline(history_path, after_entry_token)
    payload = diff_installed_market_snapshots.build_diff_payload(before_baseline_path, after_baseline_path)
    payload["history_path"] = str(resolve_repo_path(history_path))
    payload["before_entry"] = before_entry.get("sequence")
    payload["before_requested_entry"] = before_entry_token
    payload["after_entry"] = after_entry.get("sequence")
    payload["after_requested_entry"] = after_entry_token
    payload["before_history_summary"] = before_entry.get("summary", {})
    payload["after_history_summary"] = after_entry.get("summary", {})
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_history_diff_payload(args.history, args.before_entry, args.after_entry)

    output_path: Path | None = None
    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    markdown_path: Path | None = None
    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, diff_installed_market_snapshots.render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed market history baseline diff:")
    print(f"- History: {payload['history_path']}")
    print(f"- Before entry: {payload['before_entry']}")
    print(f"- After entry: {payload['after_entry']}")
    print(f"- Added skills: {len(payload['skills']['added'])}")
    print(f"- Removed skills: {len(payload['skills']['removed'])}")
    print(f"- Changed skills: {len(payload['skills']['changed'])}")
    print(f"- Added bundles: {len(payload['bundles']['added'])}")
    print(f"- Removed bundles: {len(payload['bundles']['removed'])}")
    print(f"- Changed bundles: {len(payload['bundles']['changed'])}")
    if output_path:
        print(f"- JSON diff: {output_path}")
    if markdown_path:
        print(f"- Markdown diff: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
