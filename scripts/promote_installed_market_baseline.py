#!/usr/bin/env python3
"""Promote the current installed-state target into a refreshed baseline snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import diff_installed_market_snapshots
import snapshot_installed_market_state
from market_utils import ROOT, load_json, resolve_target_root


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Promote the current installed-state target into a baseline snapshot and optional transition diff."
    )
    parser.add_argument("baseline", type=Path, help="Destination baseline snapshot JSON file.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown baseline summary path.")
    parser.add_argument("--diff-output-path", type=Path, help="Optional JSON path for the transition diff.")
    parser.add_argument("--diff-markdown-path", type=Path, help="Optional Markdown path for the transition diff.")
    parser.add_argument("--history-path", type=Path, help="Optional JSON path for baseline promotion history.")
    parser.add_argument("--history-markdown-path", type=Path, help="Optional Markdown path for baseline promotion history.")
    parser.add_argument("--archive-dir", type=Path, help="Optional directory for archived promoted baselines.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def default_markdown_path(baseline_path: Path) -> Path:
    return baseline_path.with_suffix(".md")


def default_transition_diff_json_path(baseline_path: Path) -> Path:
    return baseline_path.with_name(f"{baseline_path.stem}-transition-diff.json")


def default_transition_diff_markdown_path(baseline_path: Path) -> Path:
    return baseline_path.with_name(f"{baseline_path.stem}-transition-diff.md")


def default_history_json_path(baseline_path: Path) -> Path:
    return baseline_path.with_name(f"{baseline_path.stem}-history.json")


def default_history_markdown_path(baseline_path: Path) -> Path:
    return baseline_path.with_name(f"{baseline_path.stem}-history.md")


def default_archive_dir(baseline_path: Path) -> Path:
    return baseline_path.with_name(f"{baseline_path.stem}-archive")


def entry_sequence(entry: object) -> int | None:
    if not isinstance(entry, dict):
        return None
    try:
        return int(entry.get("sequence"))
    except (TypeError, ValueError):
        return None


def next_history_sequence(payload: dict) -> int:
    next_sequence = payload.get("next_sequence")
    try:
        normalized = int(next_sequence)
    except (TypeError, ValueError):
        normalized = 1

    existing_sequences = [value for value in (entry_sequence(item) for item in payload.get("entries", [])) if value is not None]
    if existing_sequences:
        normalized = max(normalized, max(existing_sequences) + 1)
    return max(normalized, 1)


def load_history_payload(history_path: Path, baseline_path: Path) -> dict:
    if history_path.is_file():
        payload = load_json(history_path)
    else:
        payload = {
            "history_version": 1,
            "baseline_path": str(baseline_path),
            "entries": [],
        }
    if not isinstance(payload.get("entries"), list):
        payload["entries"] = []
    payload["baseline_path"] = str(baseline_path)
    payload["next_sequence"] = next_history_sequence(payload)
    return payload


def render_history_markdown(payload: dict) -> str:
    entries = payload.get("entries", [])
    lines = [
        "# Installed Baseline History",
        "",
        f"- Baseline path: `{payload.get('baseline_path', '')}`",
        f"- Baseline Markdown path: `{payload.get('baseline_markdown_path', '')}`",
        f"- Archive dir: `{payload.get('archive_dir', '')}`",
        f"- Entries: `{len(entries)}`",
        f"- Next sequence: `{payload.get('next_sequence', 1)}`",
        "",
    ]
    if not entries:
        lines.append("- No baseline promotions recorded.")
        return "\n".join(lines) + "\n"

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        summary = entry.get("summary", {})
        lines.extend(
            [
                f"- `#{entry.get('sequence', '?')}` promoted at `{entry.get('promoted_at', '?')}`",
                f"  target root: `{entry.get('target_root', '?')}`",
                f"  installed count: `{summary.get('installed_count', '?')}`",
                f"  bundle count: `{summary.get('bundle_count', '?')}`",
                f"  replaced existing baseline: `{entry.get('replaced_existing_baseline', False)}`",
                f"  archived baseline: `{entry.get('archived_baseline_path', '')}`",
            ]
        )
    return "\n".join(lines) + "\n"


def build_promotion_payload(baseline_path: Path, target_root: Path) -> tuple[dict, dict, dict | None]:
    resolved_baseline = resolve_repo_path(baseline_path)
    resolved_target_root = resolve_target_root(target_root)
    current_payload = snapshot_installed_market_state.build_snapshot_payload(resolved_target_root)

    previous_payload: dict | None = None
    transition_diff: dict | None = None
    replaced_existing = resolved_baseline.is_file()
    if replaced_existing:
        previous_payload = load_json(resolved_baseline)
        transition_diff = diff_installed_market_snapshots.build_diff_payload_from_snapshots(
            previous_payload,
            current_payload,
            before_snapshot={
                "path": str(resolved_baseline),
                "generated_at": previous_payload.get("generated_at", ""),
                "target_root": previous_payload.get("target_root", ""),
            },
            after_snapshot={
                "path": str(resolved_target_root),
                "generated_at": current_payload.get("generated_at", ""),
                "target_root": current_payload.get("target_root", ""),
            },
        )

    payload = {
        "baseline_path": str(resolved_baseline),
        "target_root": str(resolved_target_root),
        "replaced_existing_baseline": replaced_existing,
        "current_summary": current_payload.get("summary", {}),
        "transition_diff_present": transition_diff is not None,
        "transition_summary_delta": transition_diff.get("summary_delta", {}) if transition_diff else {},
    }
    return payload, current_payload, transition_diff


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    baseline_path = resolve_repo_path(args.baseline)
    markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else default_markdown_path(baseline_path)
    payload, current_payload, transition_diff = build_promotion_payload(baseline_path, args.target_root)

    write_text(baseline_path, json.dumps(current_payload, indent=2, ensure_ascii=False) + "\n")
    write_text(markdown_path, snapshot_installed_market_state.render_markdown(current_payload))

    payload = dict(payload)
    payload["baseline_markdown_path"] = str(markdown_path)

    if transition_diff is not None:
        diff_output_path = resolve_repo_path(args.diff_output_path) if args.diff_output_path else default_transition_diff_json_path(baseline_path)
        diff_markdown_path = (
            resolve_repo_path(args.diff_markdown_path)
            if args.diff_markdown_path
            else default_transition_diff_markdown_path(baseline_path)
        )
        write_text(diff_output_path, json.dumps(transition_diff, indent=2, ensure_ascii=False) + "\n")
        write_text(diff_markdown_path, diff_installed_market_snapshots.render_markdown(transition_diff))
        payload["transition_diff_path"] = str(diff_output_path)
        payload["transition_diff_markdown_path"] = str(diff_markdown_path)
    else:
        payload["transition_diff_path"] = None
        payload["transition_diff_markdown_path"] = None

    history_path = resolve_repo_path(args.history_path) if args.history_path else default_history_json_path(baseline_path)
    history_markdown_path = (
        resolve_repo_path(args.history_markdown_path)
        if args.history_markdown_path
        else default_history_markdown_path(baseline_path)
    )
    history_payload = load_history_payload(history_path, baseline_path)
    sequence = next_history_sequence(history_payload)
    archive_dir = resolve_repo_path(args.archive_dir) if args.archive_dir else default_archive_dir(baseline_path)
    archive_dir.mkdir(parents=True, exist_ok=True)
    history_payload["baseline_markdown_path"] = str(markdown_path)
    history_payload["archive_dir"] = str(archive_dir)
    archived_baseline_path = archive_dir / f"{sequence:04d}-baseline.json"
    archived_baseline_markdown_path = archive_dir / f"{sequence:04d}-baseline.md"
    write_text(archived_baseline_path, json.dumps(current_payload, indent=2, ensure_ascii=False) + "\n")
    write_text(archived_baseline_markdown_path, snapshot_installed_market_state.render_markdown(current_payload))

    archived_transition_diff_path: str | None = None
    archived_transition_diff_markdown_path: str | None = None
    if transition_diff is not None:
        archived_transition_json = archive_dir / f"{sequence:04d}-transition-diff.json"
        archived_transition_markdown = archive_dir / f"{sequence:04d}-transition-diff.md"
        write_text(archived_transition_json, json.dumps(transition_diff, indent=2, ensure_ascii=False) + "\n")
        write_text(archived_transition_markdown, diff_installed_market_snapshots.render_markdown(transition_diff))
        archived_transition_diff_path = str(archived_transition_json)
        archived_transition_diff_markdown_path = str(archived_transition_markdown)

    history_entry = {
        "sequence": sequence,
        "promoted_at": current_payload.get("generated_at", ""),
        "target_root": str(payload["target_root"]),
        "baseline_path": str(payload["baseline_path"]),
        "baseline_markdown_path": str(payload["baseline_markdown_path"]),
        "summary": current_payload.get("summary", {}),
        "replaced_existing_baseline": payload["replaced_existing_baseline"],
        "transition_diff_path": payload["transition_diff_path"],
        "transition_diff_markdown_path": payload["transition_diff_markdown_path"],
        "transition_summary_delta": payload["transition_summary_delta"],
        "archived_baseline_path": str(archived_baseline_path),
        "archived_baseline_markdown_path": str(archived_baseline_markdown_path),
        "archived_transition_diff_path": archived_transition_diff_path,
        "archived_transition_diff_markdown_path": archived_transition_diff_markdown_path,
    }
    history_payload["entries"].append(history_entry)
    history_payload["next_sequence"] = sequence + 1
    write_text(history_path, json.dumps(history_payload, indent=2, ensure_ascii=False) + "\n")
    write_text(history_markdown_path, render_history_markdown(history_payload))

    payload["history_path"] = str(history_path)
    payload["history_markdown_path"] = str(history_markdown_path)
    payload["history_entry_count"] = len(history_payload["entries"])
    payload["archive_dir"] = str(archive_dir)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed market baseline promotion:")
    print(f"- Target root: {payload['target_root']}")
    print(f"- Baseline JSON: {payload['baseline_path']}")
    print(f"- Baseline Markdown: {payload['baseline_markdown_path']}")
    print(f"- Replaced existing baseline: {'yes' if payload['replaced_existing_baseline'] else 'no'}")
    print(f"- Transition diff written: {'yes' if payload['transition_diff_present'] else 'no'}")
    print(f"- History JSON: {payload['history_path']}")
    print(f"- History Markdown: {payload['history_markdown_path']}")
    print(f"- Archive dir: {payload['archive_dir']}")
    if payload["transition_diff_path"]:
        print(f"- Transition diff JSON: {payload['transition_diff_path']}")
    if payload["transition_diff_markdown_path"]:
        print(f"- Transition diff Markdown: {payload['transition_diff_markdown_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
