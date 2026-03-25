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

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed market baseline promotion:")
    print(f"- Target root: {payload['target_root']}")
    print(f"- Baseline JSON: {payload['baseline_path']}")
    print(f"- Baseline Markdown: {payload['baseline_markdown_path']}")
    print(f"- Replaced existing baseline: {'yes' if payload['replaced_existing_baseline'] else 'no'}")
    print(f"- Transition diff written: {'yes' if payload['transition_diff_present'] else 'no'}")
    if payload["transition_diff_path"]:
        print(f"- Transition diff JSON: {payload['transition_diff_path']}")
    if payload["transition_diff_markdown_path"]:
        print(f"- Transition diff Markdown: {payload['transition_diff_markdown_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
