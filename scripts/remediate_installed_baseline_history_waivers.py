#!/usr/bin/env python3
"""Suggest follow-up actions for installed baseline history waiver findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_installed_baseline_history_waivers
from market_utils import ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build remediation guidance for installed baseline history waiver findings."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to remediate. Defaults to all known waivers.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional JSON remediation output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown remediation output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when remediations are required.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_actions(waiver: dict) -> list[dict]:
    waiver_id = str(waiver.get("id", "")).strip()
    waiver_path = str(waiver.get("path", "")).strip()
    actions: list[dict] = []
    for finding in waiver.get("findings", []):
        if not isinstance(finding, dict):
            continue
        code = str(finding.get("code", "")).strip()
        if code == "expired":
            actions.append(
                {
                    "code": "renew_or_remove",
                    "priority": "high",
                    "summary": "Renew the approval window or delete the waiver if the exception is no longer needed.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Review whether the approved exception is still expected for the current history transition.",
                        "If it is still valid, extend `expires_on` and refresh the approval note.",
                        "If it is no longer needed, remove the waiver record from governance/history-alert-waivers/.",
                    ],
                }
            )
        elif code == "unmatched":
            actions.append(
                {
                    "code": "rescope_or_remove",
                    "priority": "medium",
                    "summary": "Update the waiver selectors to the current retained transition or remove the obsolete record.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Check whether the expected transition was pruned or whether the waiver selectors drifted.",
                        "If the same approved exception still exists, update the selector fields in `match` to the current retained transition.",
                        "If the exception no longer exists, delete the waiver record instead of keeping a dead match in governance.",
                    ],
                }
            )
        elif code == "stale":
            actions.append(
                {
                    "code": "retire_or_replace",
                    "priority": "medium",
                    "summary": "Drop the stale waiver or replace it with selectors that match the still-active alert you intend to approve.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Confirm whether the old alert has already disappeared from the retained history.",
                        "If the exception is no longer necessary, remove the waiver record.",
                        "If approval should now cover a different metric, update `match.metrics` and related selectors to the new active alert.",
                    ],
                }
            )
        elif code == "policy_error":
            actions.append(
                {
                    "code": "fix_policy_reference",
                    "priority": "high",
                    "summary": "Update the waiver to reference a valid policy profile before it can be used safely.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Compare `policy_id` with the available entries from `list-installed-history-policies`.",
                        "Fix the reference or restore the missing policy profile before re-running audit.",
                    ],
                }
            )
    if not actions:
        return []
    for action in actions:
        action["waiver_id"] = waiver_id
    return actions


def build_remediation_payload(history_path: Path, waiver_tokens: list[str]) -> dict:
    audit_payload = audit_installed_baseline_history_waivers.build_audit_payload(history_path, waiver_tokens)
    waivers: list[dict] = []
    remediation_count = 0
    high_priority_count = 0
    medium_priority_count = 0

    for waiver in audit_payload.get("waivers", []):
        if not isinstance(waiver, dict):
            continue
        actions = build_actions(waiver)
        remediation_count += len(actions)
        high_priority_count += sum(1 for action in actions if action.get("priority") == "high")
        medium_priority_count += sum(1 for action in actions if action.get("priority") == "medium")
        waiver_result = dict(waiver)
        waiver_result["actions"] = actions
        waiver_result["needs_remediation"] = bool(actions)
        waivers.append(waiver_result)

    return {
        "history_path": audit_payload.get("history_path", ""),
        "waiver_count": audit_payload.get("waiver_count", 0),
        "finding_count": audit_payload.get("finding_count", 0),
        "remediation_count": remediation_count,
        "high_priority_count": high_priority_count,
        "medium_priority_count": medium_priority_count,
        "passes": remediation_count == 0,
        "waivers": waivers,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Remediation",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Remediation actions: `{payload.get('remediation_count', 0)}`",
        f"- High priority: `{payload.get('high_priority_count', 0)}`",
        f"- Medium priority: `{payload.get('medium_priority_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Waiver Actions",
        "",
    ]

    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No waivers analyzed.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` needs_remediation=`{waiver.get('needs_remediation', False)}`"
            )
            actions = waiver.get("actions", [])
            if not actions:
                lines.append("  - no remediation needed")
                continue
            for action in actions:
                lines.append(
                    f"  - `{action.get('code', '')}` priority=`{action.get('priority', '')}`: {action.get('summary', '')}"
                )

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_remediation_payload(args.history, args.waiver)

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver remediation:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Remediation actions: {payload['remediation_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
