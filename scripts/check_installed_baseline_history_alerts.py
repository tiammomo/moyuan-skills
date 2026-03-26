#!/usr/bin/env python3
"""Flag unusually large installed baseline history transitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import report_installed_baseline_history
from market_utils import ROOT


DEFAULT_MAX_ADDED_SKILLS = 1
DEFAULT_MAX_REMOVED_SKILLS = 1
DEFAULT_MAX_CHANGED_SKILLS = 2
DEFAULT_MAX_ADDED_BUNDLES = 0
DEFAULT_MAX_REMOVED_BUNDLES = 0
DEFAULT_MAX_CHANGED_BUNDLES = 1
DEFAULT_MAX_INSTALLED_DELTA = 1
DEFAULT_MAX_BUNDLE_DELTA = 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate installed baseline history transitions against alert thresholds."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--latest-only", action="store_true", help="Only evaluate the latest retained transition.")
    parser.add_argument("--max-added-skills", type=int, default=DEFAULT_MAX_ADDED_SKILLS, help="Maximum allowed added skills per transition.")
    parser.add_argument("--max-removed-skills", type=int, default=DEFAULT_MAX_REMOVED_SKILLS, help="Maximum allowed removed skills per transition.")
    parser.add_argument("--max-changed-skills", type=int, default=DEFAULT_MAX_CHANGED_SKILLS, help="Maximum allowed changed skills per transition.")
    parser.add_argument("--max-added-bundles", type=int, default=DEFAULT_MAX_ADDED_BUNDLES, help="Maximum allowed added bundles per transition.")
    parser.add_argument("--max-removed-bundles", type=int, default=DEFAULT_MAX_REMOVED_BUNDLES, help="Maximum allowed removed bundles per transition.")
    parser.add_argument("--max-changed-bundles", type=int, default=DEFAULT_MAX_CHANGED_BUNDLES, help="Maximum allowed changed bundles per transition.")
    parser.add_argument("--max-installed-delta", type=int, default=DEFAULT_MAX_INSTALLED_DELTA, help="Maximum allowed absolute installed-count delta per transition.")
    parser.add_argument("--max-bundle-delta", type=int, default=DEFAULT_MAX_BUNDLE_DELTA, help="Maximum allowed absolute bundle-count delta per transition.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON alert report output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown alert report output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when alerts are present.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def threshold_payload(args: argparse.Namespace) -> dict:
    return {
        "max_added_skills": args.max_added_skills,
        "max_removed_skills": args.max_removed_skills,
        "max_changed_skills": args.max_changed_skills,
        "max_added_bundles": args.max_added_bundles,
        "max_removed_bundles": args.max_removed_bundles,
        "max_changed_bundles": args.max_changed_bundles,
        "max_installed_delta": args.max_installed_delta,
        "max_bundle_delta": args.max_bundle_delta,
    }


def check_count(metric: str, actual: int, threshold: int, *, before_entry: object, after_entry: object) -> dict | None:
    if actual <= threshold:
        return None
    return {
        "metric": metric,
        "actual": actual,
        "threshold": threshold,
        "message": f"transition #{before_entry}->{after_entry} exceeds {metric}: {actual} > {threshold}",
    }


def evaluate_transition(transition: dict, thresholds: dict) -> dict:
    summary_delta = transition.get("summary_delta", {})
    installed_delta = summary_delta.get("installed_count", {})
    bundle_delta = summary_delta.get("bundle_count", {})
    before_entry = transition.get("before_entry")
    after_entry = transition.get("after_entry")

    alerts = [
        check_count("added_skills", len(transition.get("added_skill_ids", [])), thresholds["max_added_skills"], before_entry=before_entry, after_entry=after_entry),
        check_count("removed_skills", len(transition.get("removed_skill_ids", [])), thresholds["max_removed_skills"], before_entry=before_entry, after_entry=after_entry),
        check_count("changed_skills", len(transition.get("changed_skill_ids", [])), thresholds["max_changed_skills"], before_entry=before_entry, after_entry=after_entry),
        check_count("added_bundles", len(transition.get("added_bundle_ids", [])), thresholds["max_added_bundles"], before_entry=before_entry, after_entry=after_entry),
        check_count("removed_bundles", len(transition.get("removed_bundle_ids", [])), thresholds["max_removed_bundles"], before_entry=before_entry, after_entry=after_entry),
        check_count("changed_bundles", len(transition.get("changed_bundle_ids", [])), thresholds["max_changed_bundles"], before_entry=before_entry, after_entry=after_entry),
        check_count(
            "installed_delta",
            abs(int(installed_delta.get("delta", 0))) if isinstance(installed_delta, dict) else 0,
            thresholds["max_installed_delta"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "bundle_delta",
            abs(int(bundle_delta.get("delta", 0))) if isinstance(bundle_delta, dict) else 0,
            thresholds["max_bundle_delta"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
    ]
    normalized_alerts = [item for item in alerts if item is not None]
    return {
        "before_entry": before_entry,
        "after_entry": after_entry,
        "before_promoted_at": transition.get("before_promoted_at", ""),
        "after_promoted_at": transition.get("after_promoted_at", ""),
        "alerts": normalized_alerts,
        "alert_count": len(normalized_alerts),
        "summary_delta": summary_delta,
        "removed_skill_ids": transition.get("removed_skill_ids", []),
        "changed_skill_ids": transition.get("changed_skill_ids", []),
        "removed_bundle_ids": transition.get("removed_bundle_ids", []),
    }


def build_alert_payload(history_path: Path, args: argparse.Namespace) -> dict:
    report_payload = report_installed_baseline_history.build_report_payload(history_path)
    thresholds = threshold_payload(args)
    transitions = report_payload.get("transitions", [])
    if args.latest_only and transitions:
        transitions = [transitions[-1]]
    evaluated = [evaluate_transition(item, thresholds) for item in transitions if isinstance(item, dict)]
    alert_count = sum(item.get("alert_count", 0) for item in evaluated)
    return {
        "history_path": report_payload.get("history_path", ""),
        "latest_only": args.latest_only,
        "thresholds": thresholds,
        "entries_count": report_payload.get("entries_count", 0),
        "evaluated_transition_count": len(evaluated),
        "alert_count": alert_count,
        "passes": alert_count == 0,
        "transitions": evaluated,
        "latest_entry": report_payload.get("latest_entry"),
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Alerts",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Latest only: `{payload.get('latest_only', False)}`",
        f"- Evaluated transitions: `{payload.get('evaluated_transition_count', 0)}`",
        f"- Alert count: `{payload.get('alert_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Thresholds",
        "",
    ]
    for key, value in payload.get("thresholds", {}).items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Transition Alerts", ""])
    transitions = payload.get("transitions", [])
    if not transitions:
        lines.append("- No retained transitions to evaluate.")
    else:
        for item in transitions:
            lines.append(
                f"- `#{item.get('before_entry', '?')}` -> `#{item.get('after_entry', '?')}`"
                f" alerts=`{item.get('alert_count', 0)}`"
            )
            alerts = item.get("alerts", [])
            if not alerts:
                lines.append("  no alerts")
                continue
            for alert in alerts:
                lines.append(
                    f"  - `{alert.get('metric', '')}` actual=`{alert.get('actual', '')}` threshold=`{alert.get('threshold', '')}`"
                )

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_alert_payload(args.history, args)

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history alert check:")
        print(f"- History: {payload['history_path']}")
        print(f"- Latest only: {payload['latest_only']}")
        print(f"- Evaluated transitions: {payload['evaluated_transition_count']}")
        print(f"- Alert count: {payload['alert_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
