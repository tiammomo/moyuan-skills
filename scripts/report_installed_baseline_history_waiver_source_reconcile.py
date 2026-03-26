#!/usr/bin/env python3
"""Aggregate source-reconcile artifacts into a single reviewable report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_installed_baseline_history_waiver_sources
import reconcile_installed_baseline_history_waiver_sources
import verify_installed_baseline_history_waiver_source_reconcile
from market_utils import ROOT, load_json, repo_relative_path


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate source-audit, source-reconcile, execution, and verification artifacts into one report."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to report. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-reconcile artifacts and receiving report summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source audits and verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument("--execute-summary-path", type=Path, help="Optional source-reconcile execution summary JSON path.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON report output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown report output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_json_payload(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def display_path(path: Path | None) -> str:
    if path is None:
        return ""
    return repo_relative_path(path) if path.is_relative_to(ROOT) else str(path)


def ensure_source_audit_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path,
) -> tuple[dict, str]:
    summary_path = output_dir / "source-audit-summary.json"
    payload = audit_installed_baseline_history_waiver_sources.build_source_audit_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
    )
    write_text(summary_path, render_json_payload(payload))
    write_text(output_dir / "source-audit-summary.md", audit_installed_baseline_history_waiver_sources.render_markdown(payload))
    return payload, display_path(summary_path)


def ensure_source_reconcile_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path,
) -> tuple[dict, str]:
    summary_path = output_dir / "source-reconcile-summary.json"
    if summary_path.is_file():
        return load_json(summary_path), display_path(summary_path)

    payload = reconcile_installed_baseline_history_waiver_sources.build_reconcile_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
    )
    write_text(summary_path, render_json_payload(payload))
    write_text(output_dir / "source-reconcile-summary.md", reconcile_installed_baseline_history_waiver_sources.render_markdown(payload))
    return payload, display_path(summary_path)


def load_source_reconcile_execute_payload(output_dir: Path, execute_summary_path: Path | None) -> tuple[dict, str]:
    summary_path = execute_summary_path if execute_summary_path is not None else (output_dir / "source-reconcile-execute-summary.json")
    if not summary_path.is_file():
        return {"actions": []}, ""
    return load_json(summary_path), display_path(summary_path)


def ensure_source_reconcile_verify_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
) -> tuple[dict, str]:
    summary_path = output_dir / "source-reconcile-verify-summary.json"
    if execute_summary_path is None and summary_path.is_file():
        return load_json(summary_path), display_path(summary_path)

    payload = verify_installed_baseline_history_waiver_source_reconcile.build_verification_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )
    write_text(summary_path, render_json_payload(payload))
    write_text(summary_path.with_suffix(".md"), verify_installed_baseline_history_waiver_source_reconcile.render_markdown(payload))
    return payload, display_path(summary_path)


def build_action_map(items: list[dict]) -> dict[tuple[str, str], dict]:
    action_map: dict[tuple[str, str], dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        waiver_id = str(item.get("waiver_id", "")).strip()
        action_code = str(item.get("action_code", "")).strip()
        if waiver_id and action_code:
            action_map[(waiver_id, action_code)] = item
    return action_map


def append_action_keys(ordered_keys: list[tuple[str, str]], items: list[dict]) -> None:
    seen = set(ordered_keys)
    for item in items:
        if not isinstance(item, dict):
            continue
        key = (
            str(item.get("waiver_id", "")).strip(),
            str(item.get("action_code", "")).strip(),
        )
        if key[0] and key[1] and key not in seen:
            ordered_keys.append(key)
            seen.add(key)


def summarize_source_audit(payload: dict, summary_path: str) -> dict:
    return {
        "summary_path": summary_path,
        "apply_execute_summary_path": payload.get("execute_summary_path", ""),
        "waiver_count": payload.get("waiver_count", 0),
        "action_count": payload.get("action_count", 0),
        "pending_count": payload.get("pending_count", 0),
        "applied_count": payload.get("applied_count", 0),
        "manual_review_count": payload.get("manual_review_count", 0),
        "drift_count": payload.get("drift_count", 0),
        "write_record_count": payload.get("write_record_count", 0),
        "staged_record_count": payload.get("staged_record_count", 0),
        "passes": payload.get("passes", False),
    }


def summarize_source_reconcile(payload: dict, summary_path: str) -> dict:
    return {
        "summary_path": summary_path,
        "waiver_count": payload.get("waiver_count", 0),
        "drift_count": payload.get("drift_count", 0),
        "action_count": payload.get("action_count", 0),
        "restore_target_count": payload.get("restore_target_count", 0),
        "restore_delete_count": payload.get("restore_delete_count", 0),
        "review_action_count": payload.get("review_action_count", 0),
        "passes": payload.get("passes", False),
    }


def summarize_source_reconcile_execution(payload: dict, summary_path: str) -> dict:
    return {
        "summary_path": summary_path,
        "available": bool(summary_path),
        "write_mode": payload.get("write_mode", False),
        "stage_dir": payload.get("stage_dir", ""),
        "target_root": payload.get("target_root", ""),
        "action_count": payload.get("action_count", 0),
        "staged_update_count": payload.get("staged_update_count", 0),
        "staged_delete_count": payload.get("staged_delete_count", 0),
        "written_update_count": payload.get("written_update_count", 0),
        "written_delete_count": payload.get("written_delete_count", 0),
        "blocked_action_count": payload.get("blocked_action_count", 0),
        "source_mismatch_count": payload.get("source_mismatch_count", 0),
        "passes": payload.get("passes", False),
    }


def summarize_source_reconcile_verification(payload: dict, summary_path: str) -> dict:
    return {
        "summary_path": summary_path,
        "target_root": payload.get("target_root", ""),
        "stage_dir": payload.get("stage_dir", ""),
        "action_count": payload.get("action_count", 0),
        "verified_count": payload.get("verified_count", 0),
        "staged_target_match_count": payload.get("staged_target_match_count", 0),
        "staged_delete_match_count": payload.get("staged_delete_match_count", 0),
        "written_target_match_count": payload.get("written_target_match_count", 0),
        "written_delete_match_count": payload.get("written_delete_match_count", 0),
        "manual_review_count": payload.get("manual_review_count", 0),
        "pending_count": payload.get("pending_count", 0),
        "blocked_count": payload.get("blocked_count", 0),
        "drift_count": payload.get("drift_count", 0),
        "passes": payload.get("passes", False),
    }


def derive_report_state(
    source_audit_summary: dict,
    source_reconcile_summary: dict,
    execute_summary: dict,
    verify_summary: dict,
) -> str:
    if not execute_summary.get("available", False) and source_reconcile_summary.get("action_count", 0) > 0:
        return "needs_execution"
    if verify_summary.get("drift_count", 0) > 0 or source_audit_summary.get("drift_count", 0) > 0:
        return "drifted"
    if verify_summary.get("pending_count", 0) > 0 or verify_summary.get("blocked_count", 0) > 0:
        return "needs_verification_followup"
    if verify_summary.get("passes", False):
        return "verified"
    if source_reconcile_summary.get("action_count", 0) == 0:
        return "no_reconcile_actions"
    return "review_required"


def build_action_report(
    key: tuple[str, str],
    *,
    audit_map: dict[tuple[str, str], dict],
    reconcile_map: dict[tuple[str, str], dict],
    execute_map: dict[tuple[str, str], dict],
    verify_map: dict[tuple[str, str], dict],
) -> dict:
    audit_item = audit_map.get(key, {})
    reconcile_item = reconcile_map.get(key, {})
    execute_item = execute_map.get(key, {})
    verify_item = verify_map.get(key, {})

    return {
        "waiver_id": key[0],
        "action_code": key[1],
        "source_path": audit_item.get("source_path")
        or reconcile_item.get("source_path")
        or execute_item.get("source_path")
        or "",
        "source_audit_state": audit_item.get("state", ""),
        "source_audit_execute_status": audit_item.get("execute_status", ""),
        "source_audit_message": audit_item.get("message", ""),
        "source_audit_passes": audit_item.get("passes"),
        "source_reconcile_mode": reconcile_item.get("mode", ""),
        "source_reconcile_message": reconcile_item.get("message", ""),
        "source_reconcile_patch_path": reconcile_item.get("patch_path", ""),
        "source_reconcile_target_artifact_path": reconcile_item.get("target_artifact_path", ""),
        "source_reconcile_review_artifact_path": reconcile_item.get("review_artifact_path", ""),
        "source_reconcile_execute_status": execute_item.get("status", ""),
        "source_reconcile_execute_message": execute_item.get("message", ""),
        "source_reconcile_execute_stage_path": execute_item.get("stage_path", ""),
        "source_reconcile_execute_write_path": execute_item.get("write_path", ""),
        "verification_state": verify_item.get("state", ""),
        "verification_execute_status": verify_item.get("execute_status", ""),
        "verification_expected_state": verify_item.get("expected_state", ""),
        "verification_path": verify_item.get("verification_path", ""),
        "verification_message": verify_item.get("message", ""),
        "verification_passes": verify_item.get("passes"),
    }


def build_report_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    effective_target_root = target_root if target_root is not None else ROOT

    source_audit_payload, source_audit_summary_path = ensure_source_audit_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=effective_target_root,
    )
    source_reconcile_payload, source_reconcile_summary_path = ensure_source_reconcile_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=effective_target_root,
    )
    source_reconcile_execute_payload, source_reconcile_execute_summary_path = load_source_reconcile_execute_payload(
        output_dir,
        execute_summary_path,
    )

    resolved_target_root = effective_target_root
    execute_target_root_value = str(source_reconcile_execute_payload.get("target_root", "")).strip()
    if target_root is None and execute_target_root_value:
        resolved_target_root = resolve_repo_path(Path(execute_target_root_value))

    resolved_stage_dir = stage_dir
    execute_stage_dir_value = str(source_reconcile_execute_payload.get("stage_dir", "")).strip()
    if resolved_stage_dir is None and execute_stage_dir_value:
        resolved_stage_dir = resolve_repo_path(Path(execute_stage_dir_value))

    source_reconcile_verify_payload, source_reconcile_verify_summary_path = ensure_source_reconcile_verify_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=resolved_target_root,
        stage_dir=resolved_stage_dir,
        execute_summary_path=execute_summary_path,
    )

    source_audit_summary = summarize_source_audit(source_audit_payload, source_audit_summary_path)
    source_reconcile_summary = summarize_source_reconcile(source_reconcile_payload, source_reconcile_summary_path)
    source_reconcile_execute_summary = summarize_source_reconcile_execution(
        source_reconcile_execute_payload,
        source_reconcile_execute_summary_path,
    )
    source_reconcile_verify_summary = summarize_source_reconcile_verification(
        source_reconcile_verify_payload,
        source_reconcile_verify_summary_path,
    )

    ordered_keys: list[tuple[str, str]] = []
    append_action_keys(ordered_keys, source_audit_payload.get("results", []))
    append_action_keys(ordered_keys, source_reconcile_payload.get("actions", []))
    append_action_keys(ordered_keys, source_reconcile_execute_payload.get("actions", []))
    append_action_keys(ordered_keys, source_reconcile_verify_payload.get("results", []))

    audit_map = build_action_map(source_audit_payload.get("results", []))
    reconcile_map = build_action_map(source_reconcile_payload.get("actions", []))
    execute_map = build_action_map(source_reconcile_execute_payload.get("actions", []))
    verify_map = build_action_map(source_reconcile_verify_payload.get("results", []))

    actions = [
        build_action_report(
            key,
            audit_map=audit_map,
            reconcile_map=reconcile_map,
            execute_map=execute_map,
            verify_map=verify_map,
        )
        for key in ordered_keys
    ]

    report_complete = all(
        [
            source_audit_summary_path,
            source_reconcile_summary_path,
            source_reconcile_execute_summary_path,
            source_reconcile_verify_summary_path,
        ]
    )
    report_state = derive_report_state(
        source_audit_summary,
        source_reconcile_summary,
        source_reconcile_execute_summary,
        source_reconcile_verify_summary,
    )

    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "target_root": display_path(resolved_target_root),
        "stage_dir": display_path(resolved_stage_dir),
        "report_complete": report_complete,
        "report_state": report_state,
        "action_count": len(actions),
        "source_audit_summary_path": source_audit_summary_path,
        "source_reconcile_summary_path": source_reconcile_summary_path,
        "source_reconcile_execute_summary_path": source_reconcile_execute_summary_path,
        "source_reconcile_verify_summary_path": source_reconcile_verify_summary_path,
        "source_audit": source_audit_summary,
        "source_reconcile": source_reconcile_summary,
        "source_reconcile_execution": source_reconcile_execute_summary,
        "source_reconcile_verification": source_reconcile_verify_summary,
        "actions": actions,
    }


def render_markdown(payload: dict) -> str:
    source_audit = payload.get("source_audit", {})
    source_reconcile = payload.get("source_reconcile", {})
    source_reconcile_execution = payload.get("source_reconcile_execution", {})
    source_reconcile_verification = payload.get("source_reconcile_verification", {})

    lines = [
        "# Installed Baseline History Waiver Source Reconcile Report",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Report complete: `{payload.get('report_complete', False)}`",
        f"- Report state: `{payload.get('report_state', '')}`",
        f"- Action count: `{payload.get('action_count', 0)}`",
        f"- Source-audit summary: `{payload.get('source_audit_summary_path', '')}`",
        f"- Source-reconcile summary: `{payload.get('source_reconcile_summary_path', '')}`",
        f"- Source-reconcile execute summary: `{payload.get('source_reconcile_execute_summary_path', '')}`",
        f"- Source-reconcile verify summary: `{payload.get('source_reconcile_verify_summary_path', '')}`",
        "",
        "## Workflow",
        "",
        f"- Source audit: pending=`{source_audit.get('pending_count', 0)}` applied=`{source_audit.get('applied_count', 0)}` drift=`{source_audit.get('drift_count', 0)}` passes=`{source_audit.get('passes', False)}`",
        f"- Source reconcile: actions=`{source_reconcile.get('action_count', 0)}` restore_target=`{source_reconcile.get('restore_target_count', 0)}` restore_delete=`{source_reconcile.get('restore_delete_count', 0)}`",
        f"- Source reconcile execution: available=`{source_reconcile_execution.get('available', False)}` staged=`{source_reconcile_execution.get('staged_update_count', 0) + source_reconcile_execution.get('staged_delete_count', 0)}` written=`{source_reconcile_execution.get('written_update_count', 0) + source_reconcile_execution.get('written_delete_count', 0)}` blocked=`{source_reconcile_execution.get('blocked_action_count', 0)}`",
        f"- Source reconcile verification: verified=`{source_reconcile_verification.get('verified_count', 0)}` pending=`{source_reconcile_verification.get('pending_count', 0)}` blocked=`{source_reconcile_verification.get('blocked_count', 0)}` drift=`{source_reconcile_verification.get('drift_count', 0)}`",
        "",
        "## Actions",
        "",
    ]
    actions = payload.get("actions", [])
    if not actions:
        lines.append("- No source-reconcile report actions available.")
    else:
        for action in actions:
            lines.append(
                f"- `{action.get('waiver_id', '')}` `{action.get('action_code', '')}` audit=`{action.get('source_audit_state', '')}` reconcile=`{action.get('source_reconcile_mode', '')}` execute=`{action.get('source_reconcile_execute_status', '')}` verify=`{action.get('verification_state', '')}`"
            )
            if action.get("source_path"):
                lines.append(f"  source: `{action.get('source_path', '')}`")
            if action.get("source_reconcile_patch_path"):
                lines.append(f"  reconcile patch: `{action.get('source_reconcile_patch_path', '')}`")
            if action.get("source_reconcile_target_artifact_path"):
                lines.append(f"  reconcile target: `{action.get('source_reconcile_target_artifact_path', '')}`")
            if action.get("source_reconcile_review_artifact_path"):
                lines.append(f"  reconcile review: `{action.get('source_reconcile_review_artifact_path', '')}`")
            if action.get("source_reconcile_execute_stage_path"):
                lines.append(f"  staged path: `{action.get('source_reconcile_execute_stage_path', '')}`")
            if action.get("source_reconcile_execute_write_path"):
                lines.append(f"  written path: `{action.get('source_reconcile_execute_write_path', '')}`")
            if action.get("verification_path"):
                lines.append(f"  verification path: `{action.get('verification_path', '')}`")
            message_parts = [
                part
                for part in [
                    action.get("source_audit_message", ""),
                    action.get("source_reconcile_message", ""),
                    action.get("source_reconcile_execute_message", ""),
                    action.get("verification_message", ""),
                ]
                if part
            ]
            if message_parts:
                lines.append(f"  notes: {' | '.join(message_parts)}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    execute_summary_path = resolve_repo_path(args.execute_summary_path) if args.execute_summary_path else None

    payload = build_report_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "source-reconcile-report-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "source-reconcile-report-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed baseline history waiver source reconcile report:")
    print(f"- History: {payload['history_path']}")
    print(f"- Report state: {payload['report_state']}")
    print(f"- Report complete: {'yes' if payload['report_complete'] else 'no'}")
    print(f"- Action count: {payload['action_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
