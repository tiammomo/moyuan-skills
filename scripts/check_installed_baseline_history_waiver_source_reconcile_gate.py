#!/usr/bin/env python3
"""Evaluate source-reconcile report artifacts as a reusable CI/release gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import report_installed_baseline_history_waiver_source_reconcile
from market_utils import ROOT, repo_relative_path


DEFAULT_ALLOWED_STATES = ("verified", "no_reconcile_actions")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate source-reconcile report artifacts as a reusable gate."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to gate. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-reconcile artifacts and receiving gate summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source audits and verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument("--execute-summary-path", type=Path, help="Optional source-reconcile execution summary JSON path.")
    parser.add_argument(
        "--allow-state",
        action="append",
        default=[],
        help="Report state that should be treated as passing. Defaults to verified and no_reconcile_actions.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional JSON gate output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown gate output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when the gate fails.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_json_payload(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def display_path(path: Path) -> str:
    return repo_relative_path(path) if path.is_relative_to(ROOT) else str(path)


def normalize_allowed_states(values: list[str]) -> list[str]:
    normalized = [value.strip() for value in values if value.strip()]
    return normalized or list(DEFAULT_ALLOWED_STATES)


def build_gate_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
    allowed_states: list[str],
) -> dict:
    report_payload = report_installed_baseline_history_waiver_source_reconcile.build_report_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )

    findings: list[dict] = []
    if report_payload.get("report_complete") is not True:
        findings.append(
            {
                "code": "incomplete_report",
                "message": "source-reconcile handoff is incomplete because one or more workflow summaries are missing",
            }
        )

    report_state = str(report_payload.get("report_state", "")).strip()
    if report_state not in allowed_states:
        findings.append(
            {
                "code": "disallowed_report_state",
                "message": f"report_state={report_state or '(empty)'} is not allowed by this gate",
            }
        )

    execution_summary = report_payload.get("source_reconcile_execution", {})
    if execution_summary.get("blocked_action_count", 0) > 0:
        findings.append(
            {
                "code": "blocked_execution",
                "message": "source-reconcile execution contains blocked actions that must be resolved before promotion",
            }
        )

    verification_summary = report_payload.get("source_reconcile_verification", {})
    if verification_summary.get("pending_count", 0) > 0:
        findings.append(
            {
                "code": "pending_verification",
                "message": "source-reconcile verification still has pending actions and cannot be treated as complete",
            }
        )
    if verification_summary.get("blocked_count", 0) > 0:
        findings.append(
            {
                "code": "blocked_verification",
                "message": "source-reconcile verification contains blocked actions and requires follow-up",
            }
        )
    if verification_summary.get("drift_count", 0) > 0:
        findings.append(
            {
                "code": "verification_drift",
                "message": "source-reconcile verification detected drift after execution",
            }
        )

    passes = len(findings) == 0
    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "target_root": report_payload.get("target_root", ""),
        "stage_dir": report_payload.get("stage_dir", ""),
        "allowed_states": allowed_states,
        "report_state": report_state,
        "report_complete": report_payload.get("report_complete", False),
        "report_summary_path": display_path(output_dir / "source-reconcile-report-summary.json"),
        "source_reconcile_execution_summary_path": report_payload.get("source_reconcile_execute_summary_path", ""),
        "source_reconcile_verify_summary_path": report_payload.get("source_reconcile_verify_summary_path", ""),
        "passes": passes,
        "finding_count": len(findings),
        "findings": findings,
        "report": report_payload,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Reconcile Gate",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Allowed states: `{', '.join(payload.get('allowed_states', []))}`",
        f"- Report state: `{payload.get('report_state', '')}`",
        f"- Report complete: `{payload.get('report_complete', False)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Report summary: `{payload.get('report_summary_path', '')}`",
        "",
        "## Findings",
        "",
    ]
    findings = payload.get("findings", [])
    if not findings:
        lines.append("- Gate passed with no findings.")
    else:
        for finding in findings:
            lines.append(f"- `{finding.get('code', '')}` {finding.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else report_installed_baseline_history_waiver_source_reconcile.DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    execute_summary_path = resolve_repo_path(args.execute_summary_path) if args.execute_summary_path else None
    allowed_states = normalize_allowed_states(args.allow_state)

    payload = build_gate_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
        allowed_states=allowed_states,
    )

    report_summary_json_path = output_dir / "source-reconcile-report-summary.json"
    report_summary_markdown_path = output_dir / "source-reconcile-report-summary.md"
    write_text(
        report_summary_json_path,
        render_json_payload(payload["report"]),
    )
    write_text(
        report_summary_markdown_path,
        report_installed_baseline_history_waiver_source_reconcile.render_markdown(payload["report"]),
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "source-reconcile-gate-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "source-reconcile-gate-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source reconcile gate:")
        print(f"- History: {payload['history_path']}")
        print(f"- Report state: {payload['report_state']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")
        print(f"- Findings: {payload['finding_count']}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
