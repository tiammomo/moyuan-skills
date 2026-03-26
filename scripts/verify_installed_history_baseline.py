#!/usr/bin/env python3
"""Verify a live installed-state target against an archived baseline history entry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import restore_installed_market_baseline
import verify_installed_market_baseline
from market_utils import ROOT, load_json


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare a live installed-state target against an archived installed baseline history entry."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("entry", help="History entry sequence number or 'latest'.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--output-dir", type=Path, help="Optional directory for current snapshot and diff artifacts.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when drift is detected.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def resolve_archived_baseline(history_path: Path, entry_token: str) -> tuple[dict, dict, Path]:
    resolved_history = resolve_repo_path(history_path)
    history_payload = load_json(resolved_history)
    try:
        entry = restore_installed_market_baseline.resolve_history_entry(history_payload, entry_token)
    except ValueError as exc:
        raise SystemExit(str(exc))
    archived_baseline_path = restore_installed_market_baseline.resolve_optional_repo_path(entry.get("archived_baseline_path"))
    if archived_baseline_path is None or not archived_baseline_path.is_file():
        raise SystemExit(f"archived baseline is missing: {archived_baseline_path}")
    return history_payload, entry, archived_baseline_path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    resolved_history, entry, archived_baseline_path = resolve_archived_baseline(args.history, args.entry)
    payload, current_payload = verify_installed_market_baseline.build_verification_payload(archived_baseline_path, args.target_root)
    payload["history_path"] = str(resolve_repo_path(args.history))
    payload["history_entry"] = entry.get("sequence")
    payload["requested_entry"] = args.entry
    payload["history_summary"] = entry.get("summary", {})
    payload["history_next_sequence"] = resolved_history.get("next_sequence")

    output_dir: Path | None = None
    if args.output_dir:
        output_dir = resolve_repo_path(args.output_dir)
        verify_installed_market_baseline.write_verification_artifacts(output_dir, current_payload, payload["diff"])

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed market history baseline verification:")
        print(f"- History: {payload['history_path']}")
        print(f"- Requested entry: {payload['requested_entry']}")
        print(f"- Resolved entry: {payload['history_entry']}")
        print(f"- Archived baseline: {payload['baseline_path']}")
        print(f"- Target root: {payload['target_root']}")
        print(f"- Matches baseline: {'yes' if payload['matches'] else 'no'}")
        print(f"- Added skills: {len(payload['diff']['skills']['added'])}")
        print(f"- Removed skills: {len(payload['diff']['skills']['removed'])}")
        print(f"- Changed skills: {len(payload['diff']['skills']['changed'])}")
        print(f"- Added bundles: {len(payload['diff']['bundles']['added'])}")
        print(f"- Removed bundles: {len(payload['diff']['bundles']['removed'])}")
        print(f"- Changed bundles: {len(payload['diff']['bundles']['changed'])}")
        if output_dir:
            print(f"- Verification artifacts: {output_dir}")

    if args.strict and not payload["matches"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
