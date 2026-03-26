#!/usr/bin/env python3
"""Suggest follow-up actions for source-reconcile gate waiver findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_installed_baseline_history_waiver_source_reconcile_waivers
import report_installed_baseline_history_waiver_source_reconcile
from market_utils import ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build remediation guidance for installed history waiver source-reconcile gate waiver findings."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to remediate. Defaults to all known gate waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-reconcile artifacts and receiving remediation summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source audits and verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument("--execute-summary-path", type=Path, help="Optional source-reconcile execution summary JSON path.")
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
    matched_policy_ids = [
        str(item).strip()
        for item in waiver.get("matched_policy_ids", [])
        if isinstance(item, str) and item.strip()
    ]
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
                    "summary": "Renew the approval window or remove the source-reconcile gate waiver if the exception is no longer needed.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Confirm the source-reconcile finding still represents an intentional, temporary exception.",
                        "If the exception is still valid, extend `expires_on` and refresh the approval note.",
                        "If the exception is no longer needed, delete the gate waiver from governance/source-reconcile-gate-waivers/.",
                    ],
                }
            )
        elif code == "unmatched":
            actions.append(
                {
                    "code": "retarget_or_remove",
                    "priority": "medium",
                    "summary": "Retarget the gate waiver selectors to the current source-reconcile report scope or remove the obsolete record.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Check whether target root, stage dir, report state, or action selectors drifted relative to the current source-reconcile report.",
                        "If the same approved exception still exists, update the selector fields under `match` to the current scope.",
                        "If the exception no longer exists, remove the stale gate waiver instead of keeping a dead match.",
                    ],
                }
            )
        elif code == "stale":
            actions.append(
                {
                    "code": "retire_or_replace",
                    "priority": "medium",
                    "summary": "Drop the stale gate waiver or replace it with selectors that match the active source-reconcile finding you still intend to approve.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Verify whether the original finding already disappeared from the source-reconcile gate output.",
                        "If no exception is still needed, delete the waiver record.",
                        "If approval should now cover a different gate finding, update `match.finding_codes` and related selectors to the new active finding.",
                    ],
                }
            )
        elif code == "policy_mismatch":
            actions.append(
                {
                    "code": "correct_policy_or_split",
                    "priority": "high",
                    "summary": "Point the gate waiver at the policy it actually matches, or split it into separate policy-scoped records if multiple workflows need coverage.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "candidate_policy_ids": matched_policy_ids,
                    "suggested_steps": [
                        "Compare `policy_id` with the policy profiles that still produce matching source-reconcile findings.",
                        "If the waiver belongs to another policy, update `policy_id` to the matching profile.",
                        "If different workflows need different approvals, split the waiver into multiple policy-scoped records instead of keeping one ambiguous exception.",
                    ],
                }
            )
        elif code == "policy_error":
            actions.append(
                {
                    "code": "fix_policy_reference",
                    "priority": "high",
                    "summary": "Repair the broken policy reference before this gate waiver can be used safely.",
                    "why": finding.get("message", ""),
                    "suggested_file": waiver_path,
                    "suggested_steps": [
                        "Compare `policy_id` with the available entries from `list-installed-history-waiver-source-reconcile-policies`.",
                        "Restore the missing policy or update the waiver to a valid policy id, then rerun audit.",
                    ],
                }
            )

    for action in actions:
        action["waiver_id"] = waiver_id
    return actions


def build_remediation_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
) -> dict:
    audit_payload = audit_installed_baseline_history_waiver_source_reconcile_waivers.build_audit_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )

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
        "output_dir": audit_payload.get("output_dir", ""),
        "target_root": audit_payload.get("target_root", ""),
        "stage_dir": audit_payload.get("stage_dir", ""),
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
        "# Installed Baseline History Waiver Source Reconcile Gate Waiver Remediation",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
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
        lines.append("- No source-reconcile gate waivers analyzed.")
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

    output_dir = (
        resolve_repo_path(args.output_dir)
        if args.output_dir
        else report_installed_baseline_history_waiver_source_reconcile.DEFAULT_OUTPUT_DIR
    )
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    execute_summary_path = resolve_repo_path(args.execute_summary_path) if args.execute_summary_path else None

    payload = build_remediation_payload(
        args.history,
        args.waiver,
        args.gate_waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source reconcile gate waiver remediation:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Remediation actions: {payload['remediation_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
