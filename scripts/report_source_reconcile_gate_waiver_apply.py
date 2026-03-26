#!/usr/bin/env python3
"""Aggregate source-reconcile gate waiver apply artifacts into one review pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import execute_source_reconcile_gate_waiver_apply
import verify_source_reconcile_gate_waiver_apply
from market_utils import ROOT, load_json, repo_relative_path


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate source-reconcile gate waiver apply summaries, execution, and verification into one report."
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
        help="Named source-reconcile gate waiver id or JSON file path to report. Defaults to all known gate waivers.",
    )
    parser.add_argument("--output-dir", type=Path, help="Directory containing apply and verification artifacts.")
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for write verification.")
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


def ensure_apply_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    source_reconcile_execute_summary_path: Path | None,
) -> tuple[dict, str]:
    summary_path = output_dir / "source-reconcile-gate-waiver-apply-summary.json"
    if summary_path.is_file() and not source_waiver_tokens and not gate_waiver_tokens and source_reconcile_execute_summary_path is None:
        return load_json(summary_path), display_path(summary_path)

    payload = execute_source_reconcile_gate_waiver_apply.ensure_apply_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        execute_summary_path=source_reconcile_execute_summary_path,
    )
    write_text(summary_path, render_json_payload(payload))
    write_text(
        output_dir / "source-reconcile-gate-waiver-apply-summary.md",
        execute_source_reconcile_gate_waiver_apply.prepare_source_reconcile_gate_waiver_apply.render_markdown(payload),
    )
    return payload, display_path(summary_path)


def load_apply_execute_payload(output_dir: Path, apply_execute_summary_path: Path | None) -> tuple[dict, str]:
    summary_path = (
        apply_execute_summary_path
        if apply_execute_summary_path is not None
        else (output_dir / "source-reconcile-gate-waiver-apply-execute-summary.json")
    )
    if not summary_path.is_file():
        return {"actions": []}, ""
    return load_json(summary_path), display_path(summary_path)


def ensure_verify_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    source_reconcile_execute_summary_path: Path | None,
    apply_execute_summary_path: Path | None,
) -> tuple[dict, str]:
    summary_path = output_dir / "source-reconcile-gate-waiver-apply-verify-summary.json"
    if (
        summary_path.is_file()
        and not source_waiver_tokens
        and not gate_waiver_tokens
        and source_reconcile_execute_summary_path is None
        and apply_execute_summary_path is None
    ):
        return load_json(summary_path), display_path(summary_path)

    payload = verify_source_reconcile_gate_waiver_apply.build_verification_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
    )
    write_text(summary_path, render_json_payload(payload))
    write_text(summary_path.with_suffix(".md"), verify_source_reconcile_gate_waiver_apply.render_markdown(payload))
    return payload, display_path(summary_path)


def build_action_map(items: list[dict]) -> dict[tuple[str, str], dict]:
    action_map: dict[tuple[str, str], dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        waiver_id = str(item.get("waiver_id", "") or item.get("id", "")).strip()
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
            str(item.get("waiver_id", "") or item.get("id", "")).strip(),
            str(item.get("action_code", "")).strip(),
        )
        if key[0] and key[1] and key not in seen:
            ordered_keys.append(key)
            seen.add(key)


def summarize_apply(payload: dict, summary_path: str) -> dict:
    return {
        "summary_path": summary_path,
        "waiver_count": payload.get("waiver_count", 0),
        "finding_count": payload.get("finding_count", 0),
        "preview_count": payload.get("preview_count", 0),
        "action_count": payload.get("action_count", 0),
        "patch_count": payload.get("patch_count", 0),
        "update_patch_count": payload.get("update_patch_count", 0),
        "delete_patch_count": payload.get("delete_patch_count", 0),
        "manual_review_count": payload.get("manual_review_count", 0),
        "passes": payload.get("passes", False),
    }


def summarize_apply_execution(payload: dict, summary_path: str) -> dict:
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
        "blocked_manual_review_count": payload.get("blocked_manual_review_count", 0),
        "source_mismatch_count": payload.get("source_mismatch_count", 0),
        "passes": payload.get("passes", False),
    }


def summarize_apply_verification(payload: dict, summary_path: str) -> dict:
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


def derive_report_state(apply_summary: dict, apply_execution_summary: dict, apply_verification_summary: dict) -> str:
    if apply_summary.get("action_count", 0) == 0:
        return "no_apply_actions"
    if not apply_execution_summary.get("available", False):
        return "needs_execution"
    if apply_verification_summary.get("drift_count", 0) > 0:
        return "drifted"
    if (
        apply_verification_summary.get("pending_count", 0) > 0
        or apply_verification_summary.get("blocked_count", 0) > 0
    ):
        return "needs_verification_followup"
    if apply_verification_summary.get("passes", False):
        return "verified"
    return "review_required"


def build_action_report(
    key: tuple[str, str],
    *,
    apply_map: dict[tuple[str, str], dict],
    apply_execute_map: dict[tuple[str, str], dict],
    apply_verify_map: dict[tuple[str, str], dict],
) -> dict:
    apply_item = apply_map.get(key, {})
    apply_execute_item = apply_execute_map.get(key, {})
    apply_verify_item = apply_verify_map.get(key, {})
    return {
        "waiver_id": key[0],
        "action_code": key[1],
        "apply_mode": apply_item.get("mode", ""),
        "apply_summary": apply_item.get("summary", ""),
        "apply_source_path": apply_item.get("source_path", ""),
        "apply_preview_path": apply_item.get("preview_path", ""),
        "apply_target_path": apply_item.get("target_path", ""),
        "apply_patch_path": apply_item.get("patch_path", ""),
        "apply_review_artifact_path": apply_item.get("review_artifact_path", ""),
        "apply_execute_status": apply_execute_item.get("status", ""),
        "apply_execute_message": apply_execute_item.get("message", ""),
        "apply_execute_stage_path": apply_execute_item.get("stage_path", ""),
        "apply_execute_write_path": apply_execute_item.get("write_path", ""),
        "verification_state": apply_verify_item.get("state", ""),
        "verification_execute_status": apply_verify_item.get("execute_status", ""),
        "verification_expected_state": apply_verify_item.get("expected_state", ""),
        "verification_path": apply_verify_item.get("verification_path", ""),
        "verification_message": apply_verify_item.get("message", ""),
        "verification_passes": apply_verify_item.get("passes"),
    }


def build_report_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    source_reconcile_execute_summary_path: Path | None,
    apply_execute_summary_path: Path | None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    apply_payload, apply_summary_path = ensure_apply_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
    )
    apply_execute_payload, apply_execute_summary_display_path = load_apply_execute_payload(
        output_dir,
        apply_execute_summary_path,
    )

    effective_target_root = target_root
    if effective_target_root is None:
        execute_target_root = str(apply_execute_payload.get("target_root", "")).strip()
        effective_target_root = resolve_repo_path(Path(execute_target_root)) if execute_target_root else ROOT

    effective_stage_dir = stage_dir
    if effective_stage_dir is None:
        execute_stage_dir = str(apply_execute_payload.get("stage_dir", "")).strip()
        if execute_stage_dir:
            effective_stage_dir = resolve_repo_path(Path(execute_stage_dir))

    apply_verify_payload, apply_verify_summary_path = ensure_verify_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        target_root=effective_target_root,
        stage_dir=effective_stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
    )

    ordered_keys: list[tuple[str, str]] = []
    for waiver in apply_payload.get("waivers", []):
        if not isinstance(waiver, dict):
            continue
        for action in waiver.get("apply_actions", []):
            if not isinstance(action, dict):
                continue
            action_copy = dict(action)
            action_copy["waiver_id"] = waiver.get("id")
            append_action_keys(ordered_keys, [action_copy])
    append_action_keys(ordered_keys, apply_execute_payload.get("actions", []))
    append_action_keys(ordered_keys, apply_verify_payload.get("results", []))

    apply_items: list[dict] = []
    for waiver in apply_payload.get("waivers", []):
        if not isinstance(waiver, dict):
            continue
        for action in waiver.get("apply_actions", []):
            if not isinstance(action, dict):
                continue
            action_copy = dict(action)
            action_copy["waiver_id"] = waiver.get("id")
            apply_items.append(action_copy)

    apply_map = build_action_map(apply_items)
    apply_execute_map = build_action_map(apply_execute_payload.get("actions", []))
    apply_verify_map = build_action_map(apply_verify_payload.get("results", []))

    actions = [
        build_action_report(
            key,
            apply_map=apply_map,
            apply_execute_map=apply_execute_map,
            apply_verify_map=apply_verify_map,
        )
        for key in ordered_keys
    ]

    apply_summary = summarize_apply(apply_payload, apply_summary_path)
    apply_execution_summary = summarize_apply_execution(apply_execute_payload, apply_execute_summary_display_path)
    apply_verification_summary = summarize_apply_verification(apply_verify_payload, apply_verify_summary_path)
    report_state = derive_report_state(apply_summary, apply_execution_summary, apply_verification_summary)

    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "target_root": display_path(effective_target_root),
        "stage_dir": display_path(effective_stage_dir) if effective_stage_dir is not None else "",
        "source_reconcile_execute_summary_path": display_path(source_reconcile_execute_summary_path)
        if source_reconcile_execute_summary_path is not None and source_reconcile_execute_summary_path.is_file()
        else "",
        "apply_summary_path": apply_summary_path,
        "apply_execute_summary_path": apply_execute_summary_display_path,
        "apply_verify_summary_path": apply_verify_summary_path,
        "report_complete": bool(apply_summary_path and apply_execute_summary_display_path and apply_verify_summary_path),
        "report_state": report_state,
        "waiver_count": apply_payload.get("waiver_count", 0),
        "action_count": len(actions),
        "apply": apply_summary,
        "apply_execution": apply_execution_summary,
        "apply_verification": apply_verification_summary,
        "actions": actions,
    }


def render_markdown(payload: dict) -> str:
    apply_summary = payload.get("apply", {})
    apply_execution_summary = payload.get("apply_execution", {})
    apply_verification_summary = payload.get("apply_verification", {})
    lines = [
        "# Installed Baseline History Waiver Source Reconcile Gate Waiver Apply Report",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Report complete: `{payload.get('report_complete', False)}`",
        f"- Report state: `{payload.get('report_state', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Actions: `{payload.get('action_count', 0)}`",
        f"- Apply summary: `{payload.get('apply_summary_path', '')}`",
        f"- Apply execute summary: `{payload.get('apply_execute_summary_path', '')}`",
        f"- Apply verify summary: `{payload.get('apply_verify_summary_path', '')}`",
        "",
        "## Workflow",
        "",
        f"- Apply pack: actions=`{apply_summary.get('action_count', 0)}` patches=`{apply_summary.get('patch_count', 0)}` manual_review=`{apply_summary.get('manual_review_count', 0)}`",
        f"- Apply execution: available=`{apply_execution_summary.get('available', False)}` staged=`{apply_execution_summary.get('staged_update_count', 0) + apply_execution_summary.get('staged_delete_count', 0)}` written=`{apply_execution_summary.get('written_update_count', 0) + apply_execution_summary.get('written_delete_count', 0)}` blocked=`{apply_execution_summary.get('blocked_action_count', 0)}`",
        f"- Apply verification: verified=`{apply_verification_summary.get('verified_count', 0)}` pending=`{apply_verification_summary.get('pending_count', 0)}` blocked=`{apply_verification_summary.get('blocked_count', 0)}` drift=`{apply_verification_summary.get('drift_count', 0)}`",
        "",
        "## Actions",
        "",
    ]
    actions = payload.get("actions", [])
    if not actions:
        lines.append("- No source-reconcile gate waiver apply actions available.")
    else:
        for action in actions:
            lines.append(
                f"- `{action.get('waiver_id', '')}` `{action.get('action_code', '')}` apply=`{action.get('apply_mode', '')}` execute=`{action.get('apply_execute_status', '')}` verify=`{action.get('verification_state', '')}`"
            )
            if action.get("apply_source_path"):
                lines.append(f"  source: `{action.get('apply_source_path', '')}`")
            if action.get("apply_target_path"):
                lines.append(f"  target: `{action.get('apply_target_path', '')}`")
            if action.get("apply_patch_path"):
                lines.append(f"  patch: `{action.get('apply_patch_path', '')}`")
            if action.get("apply_review_artifact_path"):
                lines.append(f"  review: `{action.get('apply_review_artifact_path', '')}`")
            if action.get("apply_execute_stage_path"):
                lines.append(f"  staged path: `{action.get('apply_execute_stage_path', '')}`")
            if action.get("apply_execute_write_path"):
                lines.append(f"  written path: `{action.get('apply_execute_write_path', '')}`")
            if action.get("verification_path"):
                lines.append(f"  verification path: `{action.get('verification_path', '')}`")
            notes = [
                part
                for part in [
                    action.get("apply_summary", ""),
                    action.get("apply_execute_message", ""),
                    action.get("verification_message", ""),
                ]
                if part
            ]
            if notes:
                lines.append(f"  notes: {' | '.join(notes)}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    source_reconcile_execute_summary_path = (
        resolve_repo_path(args.source_reconcile_execute_summary_path)
        if args.source_reconcile_execute_summary_path
        else None
    )
    apply_execute_summary_path = (
        resolve_repo_path(args.apply_execute_summary_path)
        if args.apply_execute_summary_path
        else None
    )

    payload = build_report_payload(
        args.history,
        args.waiver,
        args.gate_waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
    )

    summary_json_path = (
        resolve_repo_path(args.output_path)
        if args.output_path
        else (output_dir / "source-reconcile-gate-waiver-apply-report-summary.json")
    )
    summary_markdown_path = (
        resolve_repo_path(args.markdown_path)
        if args.markdown_path
        else (output_dir / "source-reconcile-gate-waiver-apply-report-summary.md")
    )
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed baseline history waiver source reconcile gate waiver apply report:")
    print(f"- History: {payload['history_path']}")
    print(f"- Report state: {payload['report_state']}")
    print(f"- Report complete: {'yes' if payload['report_complete'] else 'no'}")
    print(f"- Action count: {payload['action_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
