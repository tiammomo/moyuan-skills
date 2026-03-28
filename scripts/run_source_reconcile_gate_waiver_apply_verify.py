#!/usr/bin/env python3
"""Re-verify source-reconcile gate waiver apply artifacts and refresh the aggregate report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import report_source_reconcile_gate_waiver_apply
import verify_source_reconcile_gate_waiver_apply
from market_utils import ROOT


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Re-verify source-reconcile gate waiver apply artifacts and refresh the aggregate report."
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
        help="Named source-reconcile gate waiver id or JSON file path to verify. Defaults to all known gate waivers.",
    )
    parser.add_argument("--output-dir", type=Path, help="Directory containing apply and execution artifacts.")
    parser.add_argument("--target-root", type=Path, help="Installed target root used to verify staged targets.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument(
        "--source-reconcile-execute-summary-path",
        type=Path,
        help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.",
    )
    parser.add_argument(
        "--apply-execute-summary-path",
        type=Path,
        help="Optional source-reconcile gate waiver apply execution summary JSON path.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional refreshed report JSON output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional refreshed report Markdown output path.")
    parser.add_argument("--json", action="store_true", help="Print refreshed report JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else ROOT
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    source_reconcile_execute_summary_path = (
        resolve_repo_path(args.source_reconcile_execute_summary_path)
        if args.source_reconcile_execute_summary_path
        else None
    )
    apply_execute_summary_path = (
        resolve_repo_path(args.apply_execute_summary_path)
        if args.apply_execute_summary_path
        else (output_dir / "source-reconcile-gate-waiver-apply-execute-summary.json")
    )
    verify_summary_path = output_dir / "source-reconcile-gate-waiver-apply-verify-summary.json"
    verify_markdown_path = output_dir / "source-reconcile-gate-waiver-apply-verify-summary.md"

    verify_payload = verify_source_reconcile_gate_waiver_apply.build_verification_payload(
        args.history,
        args.waiver,
        args.gate_waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
    )
    verify_source_reconcile_gate_waiver_apply.write_text(
        verify_summary_path,
        verify_source_reconcile_gate_waiver_apply.render_json_payload(verify_payload),
    )
    verify_source_reconcile_gate_waiver_apply.write_text(
        verify_markdown_path,
        verify_source_reconcile_gate_waiver_apply.render_markdown(verify_payload),
    )

    report_payload = report_source_reconcile_gate_waiver_apply.build_report_payload(
        args.history,
        args.waiver,
        args.gate_waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
    )
    report_json_path = (
        resolve_repo_path(args.output_path)
        if args.output_path
        else (output_dir / "source-reconcile-gate-waiver-apply-report-summary.json")
    )
    report_markdown_path = (
        resolve_repo_path(args.markdown_path)
        if args.markdown_path
        else (output_dir / "source-reconcile-gate-waiver-apply-report-summary.md")
    )
    report_source_reconcile_gate_waiver_apply.write_text(
        report_json_path,
        report_source_reconcile_gate_waiver_apply.render_json_payload(report_payload),
    )
    report_source_reconcile_gate_waiver_apply.write_text(
        report_markdown_path,
        report_source_reconcile_gate_waiver_apply.render_markdown(report_payload),
    )

    if args.json:
        print(json.dumps(report_payload, indent=2, ensure_ascii=False))
    else:
        print("Source-reconcile gate waiver apply verification refreshed:")
        print(f"- History: {report_payload['history_path']}")
        print(f"- Report state: {report_payload['report_state']}")
        print(f"- Action count: {report_payload['action_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
