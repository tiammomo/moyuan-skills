#!/usr/bin/env python3
"""Refresh the first frontend-facing installed governance summary pack."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import audit_installed_baseline_history_waivers
import check_installed_baseline_history_alerts
import check_installed_baseline_history_waiver_source_reconcile_gate
import check_source_reconcile_gate_waiver_apply_gate
import report_installed_baseline_history_waiver_source_reconcile
from market_utils import ROOT, repo_relative_path


DEFAULT_POLICY = "source-reconcile-review-handoff"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh the installed governance summary pack used by the frontend installed-state governance panel."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--target-root", type=Path, help="Installed target root associated with the history file.")
    parser.add_argument("--output-dir", type=Path, help="Directory receiving governance summary artifacts.")
    parser.add_argument(
        "--policy",
        default=DEFAULT_POLICY,
        help="Named source-reconcile gate policy id used for the first review summary.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional combined governance summary JSON path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional combined governance summary Markdown path.")
    parser.add_argument("--json", action="store_true", help="Print the combined governance summary as JSON.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def display_path(path: Path | None) -> str:
    if path is None:
        return ""
    return repo_relative_path(path) if path.is_relative_to(ROOT) else str(path)


def render_json_payload(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_valid_profiles() -> dict:
    history_policies, history_policy_errors = check_installed_baseline_history_alerts.load_policy_profiles()
    history_waivers, history_waiver_errors = check_installed_baseline_history_alerts.load_waiver_profiles()
    source_reconcile_policies, source_reconcile_policy_errors = (
        check_installed_baseline_history_waiver_source_reconcile_gate.load_policy_profiles()
    )
    source_reconcile_gate_waivers, source_reconcile_gate_waiver_errors = (
        check_installed_baseline_history_waiver_source_reconcile_gate.load_waiver_profiles()
    )
    apply_policies, apply_policy_errors = check_source_reconcile_gate_waiver_apply_gate.load_policy_profiles()
    apply_gate_waivers, apply_gate_waiver_errors = check_source_reconcile_gate_waiver_apply_gate.load_waiver_profiles()

    errors = (
        history_policy_errors
        + history_waiver_errors
        + source_reconcile_policy_errors
        + source_reconcile_gate_waiver_errors
        + apply_policy_errors
        + apply_gate_waiver_errors
    )
    if errors:
        raise SystemExit("\n".join(errors))

    return {
        "history_policies": history_policies,
        "history_waivers": history_waivers,
        "source_reconcile_policies": source_reconcile_policies,
        "source_reconcile_gate_waivers": source_reconcile_gate_waivers,
        "apply_policies": apply_policies,
        "apply_gate_waivers": apply_gate_waivers,
    }


def summarize_profile_counts(profiles: dict) -> dict:
    history_waivers = profiles["history_waivers"]
    source_reconcile_gate_waivers = profiles["source_reconcile_gate_waivers"]
    apply_gate_waivers = profiles["apply_gate_waivers"]

    return {
        "history_alert_policies": {
            "count": len(profiles["history_policies"]),
        },
        "history_alert_waivers": {
            "count": len(history_waivers),
            "active_count": sum(
                1 for waiver in history_waivers if check_installed_baseline_history_alerts.is_waiver_active(waiver)
            ),
        },
        "source_reconcile_policies": {
            "count": len(profiles["source_reconcile_policies"]),
        },
        "source_reconcile_gate_waivers": {
            "count": len(source_reconcile_gate_waivers),
            "active_count": sum(
                1
                for waiver in source_reconcile_gate_waivers
                if check_installed_baseline_history_waiver_source_reconcile_gate.is_waiver_active(waiver)
            ),
        },
        "source_reconcile_apply_policies": {
            "count": len(profiles["apply_policies"]),
        },
        "source_reconcile_apply_gate_waivers": {
            "count": len(apply_gate_waivers),
            "active_count": sum(
                1 for waiver in apply_gate_waivers if check_source_reconcile_gate_waiver_apply_gate.is_waiver_active(waiver)
            ),
        },
    }


def build_summary_payload(
    history_path: Path,
    *,
    target_root: Path,
    output_dir: Path,
    policy_id: str,
) -> dict:
    profiles = ensure_valid_profiles()
    profile_counts = summarize_profile_counts(profiles)
    policy_payload, policy_path = check_installed_baseline_history_waiver_source_reconcile_gate.resolve_policy_reference(
        policy_id
    )
    policy_defaults = check_installed_baseline_history_waiver_source_reconcile_gate.policy_defaults(policy_payload)
    allowed_states = check_installed_baseline_history_waiver_source_reconcile_gate.normalize_allowed_states(
        policy_defaults["allowed_states"]
    )

    audit_payload = audit_installed_baseline_history_waivers.build_audit_payload(history_path, [])
    gate_payload = check_installed_baseline_history_waiver_source_reconcile_gate.build_gate_payload(
        history_path,
        [],
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=None,
        execute_summary_path=None,
        policy_payload=policy_payload,
        policy_path=policy_path,
        gate_waiver_tokens=[],
        allowed_states=allowed_states,
    )

    audit_summary_path = output_dir / "history-waiver-audit-summary.json"
    audit_markdown_path = output_dir / "history-waiver-audit-summary.md"
    report_summary_path = output_dir / "source-reconcile-report-summary.json"
    report_markdown_path = output_dir / "source-reconcile-report-summary.md"
    gate_summary_path = output_dir / "source-reconcile-gate-summary.json"
    gate_markdown_path = output_dir / "source-reconcile-gate-summary.md"

    write_text(audit_summary_path, render_json_payload(audit_payload))
    write_text(audit_markdown_path, audit_installed_baseline_history_waivers.render_markdown(audit_payload))
    write_text(report_summary_path, render_json_payload(gate_payload["report"]))
    write_text(
        report_markdown_path,
        report_installed_baseline_history_waiver_source_reconcile.render_markdown(gate_payload["report"]),
    )
    write_text(gate_summary_path, render_json_payload(gate_payload))
    write_text(
        gate_markdown_path,
        check_installed_baseline_history_waiver_source_reconcile_gate.render_markdown(gate_payload),
    )

    recent_actions = [
        {
            "waiver_id": action.get("waiver_id", ""),
            "action_code": action.get("action_code", ""),
            "source_path": action.get("source_path", ""),
            "source_audit_state": action.get("source_audit_state", ""),
            "source_audit_message": action.get("source_audit_message", ""),
            "source_reconcile_mode": action.get("source_reconcile_mode", ""),
            "verification_state": action.get("verification_state", ""),
        }
        for action in gate_payload.get("report", {}).get("actions", [])[:5]
        if isinstance(action, dict)
    ]

    return {
        "generated_at": utc_now(),
        "history_path": str(resolve_repo_path(history_path)),
        "target_root": display_path(target_root),
        "output_dir": display_path(output_dir),
        "policy_profiles": profile_counts,
        "audit": {
            "summary_path": display_path(audit_summary_path),
            "markdown_path": display_path(audit_markdown_path),
            "waiver_count": audit_payload.get("waiver_count", 0),
            "finding_count": audit_payload.get("finding_count", 0),
            "expired_count": audit_payload.get("expired_count", 0),
            "unmatched_count": audit_payload.get("unmatched_count", 0),
            "stale_count": audit_payload.get("stale_count", 0),
            "passes": audit_payload.get("passes", False),
        },
        "gate": {
            "policy_id": gate_payload.get("policy_id"),
            "policy_title": gate_payload.get("policy_title"),
            "policy_path": display_path(policy_path),
            "summary_path": display_path(gate_summary_path),
            "markdown_path": display_path(gate_markdown_path),
            "report_summary_path": gate_payload.get("report_summary_path", ""),
            "report_state": gate_payload.get("report_state", ""),
            "report_complete": gate_payload.get("report_complete", False),
            "finding_count": gate_payload.get("finding_count", 0),
            "active_finding_count": gate_payload.get("active_finding_count", 0),
            "waived_finding_count": gate_payload.get("waived_finding_count", 0),
            "requested_gate_waiver_count": gate_payload.get("requested_gate_waiver_count", 0),
            "matched_gate_waiver_count": gate_payload.get("matched_gate_waiver_count", 0),
            "passes": gate_payload.get("passes", False),
        },
        "report": {
            "report_state": gate_payload.get("report", {}).get("report_state", ""),
            "report_complete": gate_payload.get("report", {}).get("report_complete", False),
            "action_count": gate_payload.get("report", {}).get("action_count", 0),
            "source_audit": gate_payload.get("report", {}).get("source_audit", {}),
            "source_reconcile": gate_payload.get("report", {}).get("source_reconcile", {}),
            "source_reconcile_execution": gate_payload.get("report", {}).get("source_reconcile_execution", {}),
            "source_reconcile_verification": gate_payload.get("report", {}).get("source_reconcile_verification", {}),
            "recent_actions": recent_actions,
        },
        "recommended_follow_ups": [
            {
                "label": "List source-reconcile gate policies",
                "command": "python scripts/skills_market.py list-installed-history-waiver-source-reconcile-policies --json",
                "description": "Review the reusable governance policy profiles behind the frontend summary.",
            },
            {
                "label": "List source-reconcile gate waivers",
                "command": "python scripts/skills_market.py list-installed-history-waiver-source-reconcile-waivers --json",
                "description": "Inspect reusable gate waivers before moving from review into approval work.",
            },
            {
                "label": "Run the review gate by hand",
                "command": f"python scripts/skills_market.py gate-installed-history-waiver-source-reconcile {display_path(history_path)} --policy {policy_id} --output-dir {display_path(output_dir)} --target-root {display_path(target_root)}",
                "description": "Re-run the review-oriented governance gate from the CLI when you want the full terminal summary.",
            },
        ],
    }


def render_markdown(payload: dict) -> str:
    audit = payload.get("audit", {})
    gate = payload.get("gate", {})
    report = payload.get("report", {})
    profile_counts = payload.get("policy_profiles", {})
    lines = [
        "# Installed Governance Summary",
        "",
        f"- Generated at: `{payload.get('generated_at', '')}`",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        "",
        "## Profile Counts",
        "",
        f"- History alert policies: `{profile_counts.get('history_alert_policies', {}).get('count', 0)}`",
        f"- History alert waivers: `{profile_counts.get('history_alert_waivers', {}).get('count', 0)}` active=`{profile_counts.get('history_alert_waivers', {}).get('active_count', 0)}`",
        f"- Source-reconcile policies: `{profile_counts.get('source_reconcile_policies', {}).get('count', 0)}`",
        f"- Source-reconcile gate waivers: `{profile_counts.get('source_reconcile_gate_waivers', {}).get('count', 0)}` active=`{profile_counts.get('source_reconcile_gate_waivers', {}).get('active_count', 0)}`",
        f"- Source-reconcile apply policies: `{profile_counts.get('source_reconcile_apply_policies', {}).get('count', 0)}`",
        f"- Source-reconcile apply gate waivers: `{profile_counts.get('source_reconcile_apply_gate_waivers', {}).get('count', 0)}` active=`{profile_counts.get('source_reconcile_apply_gate_waivers', {}).get('active_count', 0)}`",
        "",
        "## Review Status",
        "",
        f"- Audit findings: `{audit.get('finding_count', 0)}`",
        f"- Gate policy: `{gate.get('policy_title', '')}`",
        f"- Gate findings: `{gate.get('active_finding_count', 0)}` active, `{gate.get('waived_finding_count', 0)}` waived",
        f"- Report state: `{report.get('report_state', '')}`",
        f"- Review actions: `{report.get('action_count', 0)}`",
        "",
        "## Recent Actions",
        "",
    ]
    recent_actions = report.get("recent_actions", [])
    if not recent_actions:
        lines.append("- No review actions were captured in the latest governance summary.")
    else:
        for action in recent_actions:
            lines.append(
                f"- `{action.get('waiver_id', '')}` `{action.get('action_code', '')}` audit=`{action.get('source_audit_state', '')}` verify=`{action.get('verification_state', '')}`"
            )
            if action.get("source_path"):
                lines.append(f"  source: `{action.get('source_path', '')}`")
            if action.get("source_audit_message"):
                lines.append(f"  note: {action.get('source_audit_message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    history_path = resolve_repo_path(args.history)
    if not history_path.is_file():
        raise SystemExit(f"baseline history file not found: {history_path}")

    target_root = resolve_repo_path(args.target_root) if args.target_root else history_path.parent.parent
    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else (history_path.parent / "governance")
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = build_summary_payload(
        history_path,
        target_root=target_root,
        output_dir=output_dir,
        policy_id=args.policy,
    )

    summary_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "governance-summary.json")
    markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "governance-summary.md")
    write_text(summary_path, render_json_payload(payload))
    write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed governance summary refreshed:")
    print(f"- History: {payload['history_path']}")
    print(f"- Policy: {payload['gate']['policy_id']}")
    print(f"- Audit findings: {payload['audit']['finding_count']}")
    print(f"- Gate findings: {payload['gate']['active_finding_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
