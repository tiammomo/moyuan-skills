#!/usr/bin/env python3
"""Build a readable report for installed baseline history."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import diff_installed_history_baselines
from market_utils import ROOT, load_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a readable timeline/report for installed baseline history entries."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON report output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown report output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def summarize_transition(history_path: Path, before_entry: dict, after_entry: dict) -> dict:
    diff_payload = diff_installed_history_baselines.build_history_diff_payload(
        history_path,
        str(before_entry.get("sequence", "")),
        str(after_entry.get("sequence", "")),
    )
    return {
        "before_entry": diff_payload.get("before_entry"),
        "after_entry": diff_payload.get("after_entry"),
        "before_promoted_at": before_entry.get("promoted_at", ""),
        "after_promoted_at": after_entry.get("promoted_at", ""),
        "before_target_root": before_entry.get("target_root", ""),
        "after_target_root": after_entry.get("target_root", ""),
        "summary_delta": diff_payload.get("summary_delta", {}),
        "added_skill_ids": [item.get("skill_id") for item in diff_payload.get("skills", {}).get("added", []) if isinstance(item, dict)],
        "removed_skill_ids": [item.get("skill_id") for item in diff_payload.get("skills", {}).get("removed", []) if isinstance(item, dict)],
        "changed_skill_ids": [item.get("skill_id") for item in diff_payload.get("skills", {}).get("changed", []) if isinstance(item, dict)],
        "added_bundle_ids": [item.get("bundle_id") for item in diff_payload.get("bundles", {}).get("added", []) if isinstance(item, dict)],
        "removed_bundle_ids": [item.get("bundle_id") for item in diff_payload.get("bundles", {}).get("removed", []) if isinstance(item, dict)],
        "changed_bundle_ids": [item.get("bundle_id") for item in diff_payload.get("bundles", {}).get("changed", []) if isinstance(item, dict)],
        "diff": diff_payload,
    }


def build_report_payload(history_path: Path) -> dict:
    resolved_history = resolve_repo_path(history_path)
    history_payload = load_json(resolved_history)
    entries = history_payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []
        history_payload["entries"] = entries

    timeline = []
    normalized_entries: list[dict] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        normalized_entries.append(entry)
        summary = entry.get("summary", {})
        timeline.append(
            {
                "sequence": entry.get("sequence"),
                "promoted_at": entry.get("promoted_at", ""),
                "target_root": entry.get("target_root", ""),
                "installed_count": summary.get("installed_count", 0),
                "bundle_count": summary.get("bundle_count", 0),
                "replaced_existing_baseline": entry.get("replaced_existing_baseline", False),
                "archived_baseline_path": entry.get("archived_baseline_path", ""),
                "archived_transition_diff_path": entry.get("archived_transition_diff_path", ""),
            }
        )

    transitions = []
    for index in range(1, len(normalized_entries)):
        transitions.append(summarize_transition(resolved_history, normalized_entries[index - 1], normalized_entries[index]))

    return {
        "history_path": str(resolved_history),
        "baseline_path": history_payload.get("baseline_path", ""),
        "baseline_markdown_path": history_payload.get("baseline_markdown_path", ""),
        "archive_dir": history_payload.get("archive_dir", ""),
        "entries_count": len(normalized_entries),
        "next_sequence": history_payload.get("next_sequence"),
        "latest_entry": timeline[-1] if timeline else None,
        "timeline": timeline,
        "transitions": transitions,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Report",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Baseline path: `{payload.get('baseline_path', '')}`",
        f"- Archive dir: `{payload.get('archive_dir', '')}`",
        f"- Entries: `{payload.get('entries_count', 0)}`",
        f"- Next sequence: `{payload.get('next_sequence', '')}`",
        "",
        "## Timeline",
        "",
    ]

    timeline = payload.get("timeline", [])
    if not timeline:
        lines.append("- No retained baseline history entries.")
    else:
        for item in timeline:
            lines.append(
                f"- `#{item.get('sequence', '?')}` at `{item.get('promoted_at', '')}`"
                f" installed=`{item.get('installed_count', 0)}`"
                f" bundles=`{item.get('bundle_count', 0)}`"
            )
            lines.append(f"  target root: `{item.get('target_root', '')}`")
            lines.append(f"  archived baseline: `{item.get('archived_baseline_path', '')}`")

    lines.extend(["", "## Transition Summary", ""])
    transitions = payload.get("transitions", [])
    if not transitions:
        lines.append("- No history transitions yet.")
    else:
        for item in transitions:
            summary_delta = item.get("summary_delta", {})
            delta_chunks = [
                f"{key}={value.get('before')}->{value.get('after')}"
                for key, value in summary_delta.items()
                if isinstance(value, dict)
            ]
            if not delta_chunks:
                delta_chunks = ["no summary delta"]
            lines.append(
                f"- `#{item.get('before_entry', '?')}` -> `#{item.get('after_entry', '?')}`"
                f" ({', '.join(delta_chunks)})"
            )
            lines.append(
                f"  removed skills: `{', '.join(item.get('removed_skill_ids', [])) or '(none)'}`"
            )
            lines.append(
                f"  changed skills: `{', '.join(item.get('changed_skill_ids', [])) or '(none)'}`"
            )
            lines.append(
                f"  removed bundles: `{', '.join(item.get('removed_bundle_ids', [])) or '(none)'}`"
            )

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_report_payload(args.history)

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed baseline history report:")
    print(f"- History: {payload['history_path']}")
    print(f"- Entries: {payload['entries_count']}")
    print(f"- Next sequence: {payload['next_sequence']}")
    print(f"- Transition count: {len(payload.get('transitions', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
