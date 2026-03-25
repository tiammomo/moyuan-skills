#!/usr/bin/env python3
"""Verify a live installed-state target against a baseline snapshot."""

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
        description="Compare a live installed-state target against a baseline snapshot."
    )
    parser.add_argument("baseline", type=Path, help="Baseline installed-state snapshot JSON file.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--output-dir", type=Path, help="Optional directory for current snapshot and diff artifacts.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when drift is detected.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diff_has_changes(diff_payload: dict) -> bool:
    if diff_payload.get("summary_delta"):
        return True
    count_deltas = diff_payload.get("count_deltas", {})
    if any(count_deltas.get(section) for section in ["channels", "lifecycle_statuses", "source_kinds", "finding_severities"]):
        return True
    skills = diff_payload.get("skills", {})
    bundles = diff_payload.get("bundles", {})
    return any(skills.get(section) for section in ["added", "removed", "changed"]) or any(
        bundles.get(section) for section in ["added", "removed", "changed"]
    )


def build_verification_payload(baseline_path: Path, target_root: Path) -> tuple[dict, dict]:
    resolved_baseline = resolve_repo_path(baseline_path)
    resolved_target_root = resolve_target_root(target_root)
    baseline_payload = load_json(resolved_baseline)
    current_payload = snapshot_installed_market_state.build_snapshot_payload(resolved_target_root)
    diff_payload = diff_installed_market_snapshots.build_diff_payload_from_snapshots(
        baseline_payload,
        current_payload,
        before_snapshot={
            "path": str(resolved_baseline),
            "generated_at": baseline_payload.get("generated_at", ""),
            "target_root": baseline_payload.get("target_root", ""),
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
        "matches": not diff_has_changes(diff_payload),
        "baseline_summary": baseline_payload.get("summary", {}),
        "current_summary": current_payload.get("summary", {}),
        "diff": diff_payload,
    }
    return payload, current_payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload, current_payload = build_verification_payload(args.baseline, args.target_root)

    output_dir: Path | None = None
    if args.output_dir:
        output_dir = resolve_repo_path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        write_text(output_dir / "current-snapshot.json", json.dumps(current_payload, indent=2, ensure_ascii=False) + "\n")
        write_text(output_dir / "current-snapshot.md", snapshot_installed_market_state.render_markdown(current_payload))
        write_text(output_dir / "diff.json", json.dumps(payload["diff"], indent=2, ensure_ascii=False) + "\n")
        write_text(output_dir / "diff.md", diff_installed_market_snapshots.render_markdown(payload["diff"]))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed market baseline verification:")
        print(f"- Baseline: {payload['baseline_path']}")
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
