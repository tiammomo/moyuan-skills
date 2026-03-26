#!/usr/bin/env python3
"""Verify source-reconcile execution results against reviewed reconcile artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import execute_reconcile_installed_baseline_history_waiver_sources
import reconcile_installed_baseline_history_waiver_sources
from market_utils import ROOT, load_json, repo_relative_path, sha256_for_file


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify source-reconcile execution results against reviewed reconcile artifacts."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to verify. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-reconcile and execution artifacts.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for write verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument("--execute-summary-path", type=Path, help="Optional source-reconcile execution summary JSON path.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON verification summary output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown verification summary output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when verification drift is detected.")
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


def ensure_reconcile_payload(
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


def load_execute_payload(output_dir: Path, execute_summary_path: Path | None) -> tuple[dict, str]:
    summary_path = execute_summary_path if execute_summary_path is not None else (output_dir / "source-reconcile-execute-summary.json")
    if not summary_path.is_file():
        return {"actions": []}, ""
    return load_json(summary_path), display_path(summary_path)


def build_execute_action_map(execute_payload: dict) -> dict[tuple[str, str], dict]:
    action_map: dict[tuple[str, str], dict] = {}
    for action in execute_payload.get("actions", []):
        if not isinstance(action, dict):
            continue
        waiver_id = str(action.get("waiver_id", "")).strip()
        action_code = str(action.get("action_code", "")).strip()
        if waiver_id and action_code:
            action_map[(waiver_id, action_code)] = action
    return action_map


def resolve_stage_dir(execute_action: dict, default_stage_dir: Path | None) -> Path | None:
    stage_path_value = str(execute_action.get("stage_path", "")).strip()
    if stage_path_value:
        return resolve_repo_path(Path(stage_path_value)).parent
    stage_dir_value = str(execute_action.get("stage_dir", "")).strip()
    if stage_dir_value:
        return resolve_repo_path(Path(stage_dir_value))
    return default_stage_dir


def resolve_written_source_path(action: dict, execute_action: dict) -> Path:
    for key in ("write_path", "source_path"):
        value = str(execute_action.get(key, "")).strip()
        if value:
            return resolve_repo_path(Path(value))
    return resolve_repo_path(Path(str(action.get("source_path", "")).strip()))


def build_pending_result(action: dict, execute_status: str, verification_path: str, message: str) -> dict:
    return {
        "waiver_id": action.get("waiver_id"),
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "execute_status": execute_status,
        "verification_path": verification_path,
        "state": "pending_execution",
        "expected_state": "executed",
        "current_sha256": "",
        "passes": False,
        "message": message,
    }


def build_blocked_result(action: dict, execute_status: str, verification_path: str, message: str) -> dict:
    return {
        "waiver_id": action.get("waiver_id"),
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "execute_status": execute_status,
        "verification_path": verification_path,
        "state": execute_status or "blocked",
        "expected_state": "executed",
        "current_sha256": "",
        "passes": False,
        "message": message,
    }


def verify_restore_target(
    action: dict,
    execute_action: dict,
    *,
    target_root: Path,
    default_stage_dir: Path | None,
) -> dict:
    execute_status = str(execute_action.get("status", "")).strip()
    target_sha = str(action.get("target_sha256", "")).strip()

    if not execute_status:
        return build_pending_result(
            action,
            execute_status,
            "",
            "source-reconcile action exists, but no execution record is available yet",
        )
    if execute_status.startswith("blocked"):
        return build_blocked_result(
            action,
            execute_status,
            str(execute_action.get("source_path", "")).strip(),
            str(execute_action.get("message", "")).strip() or "source-reconcile execution was blocked",
        )

    if execute_status == "staged":
        stage_path_value = str(execute_action.get("stage_path", "")).strip()
        if stage_path_value:
            stage_path = resolve_repo_path(Path(stage_path_value))
        else:
            stage_dir = resolve_stage_dir(execute_action, default_stage_dir)
            if stage_dir is None:
                return build_pending_result(
                    action,
                    execute_status,
                    "",
                    "staged reconcile verification requires a stage path or stage directory",
                )
            source_path = resolve_written_source_path(action, execute_action)
            stage_path = execute_reconcile_installed_baseline_history_waiver_sources.staged_restore_target_path(
                action,
                source_path,
                stage_dir,
            )
        current_sha = sha256_for_file(stage_path) if stage_path.is_file() else ""
        if stage_path.is_file() and current_sha == target_sha:
            state = "matches_staged_target"
            passes = True
            message = "staged reconcile target still matches the reviewed restore artifact"
        elif not stage_path.is_file():
            state = "missing_staged_target"
            passes = False
            message = "staged reconcile target is missing"
        else:
            state = "drifted_staged_target"
            passes = False
            message = "staged reconcile target no longer matches the reviewed restore artifact"
        return {
            "waiver_id": action.get("waiver_id"),
            "action_code": action.get("action_code"),
            "mode": action.get("mode"),
            "execute_status": execute_status,
            "verification_path": display_path(stage_path),
            "state": state,
            "expected_state": "target",
            "current_sha256": current_sha,
            "passes": passes,
            "message": message,
        }

    if execute_status == "written":
        source_path = resolve_written_source_path(action, execute_action)
        current_sha = sha256_for_file(source_path) if source_path.is_file() else ""
        if source_path.is_file() and current_sha == target_sha:
            state = "matches_written_target"
            passes = True
            message = "written reconcile target still matches the reviewed restore artifact"
        elif not source_path.is_file():
            state = "missing_written_target"
            passes = False
            message = "written reconcile target is missing"
        else:
            state = "drifted_after_write"
            passes = False
            message = "written reconcile target no longer matches the reviewed restore artifact"
        return {
            "waiver_id": action.get("waiver_id"),
            "action_code": action.get("action_code"),
            "mode": action.get("mode"),
            "execute_status": execute_status,
            "verification_path": display_path(source_path if source_path.is_relative_to(ROOT) else source_path),
            "state": state,
            "expected_state": "target",
            "current_sha256": current_sha,
            "passes": passes,
            "message": message,
        }

    return build_blocked_result(
        action,
        execute_status,
        "",
        f"unexpected execute status for restore_target: {execute_status}",
    )


def verify_restore_delete(
    action: dict,
    execute_action: dict,
    *,
    target_root: Path,
    default_stage_dir: Path | None,
) -> dict:
    execute_status = str(execute_action.get("status", "")).strip()

    if not execute_status:
        return build_pending_result(
            action,
            execute_status,
            "",
            "source-reconcile delete action exists, but no execution record is available yet",
        )
    if execute_status.startswith("blocked"):
        return build_blocked_result(
            action,
            execute_status,
            str(execute_action.get("source_path", "")).strip(),
            str(execute_action.get("message", "")).strip() or "source-reconcile execution was blocked",
        )

    if execute_status == "staged_delete":
        stage_path_value = str(execute_action.get("stage_path", "")).strip()
        stage_path = resolve_repo_path(Path(stage_path_value)) if stage_path_value else None
        if stage_path is None:
            stage_dir = resolve_stage_dir(execute_action, default_stage_dir)
            if stage_dir is not None:
                stage_path = stage_dir / "deletions.json"
        if stage_path is None:
            return build_pending_result(
                action,
                execute_status,
                "",
                "staged delete verification requires a deletions manifest",
            )
        deletions: list[str] = []
        if stage_path.is_file():
            try:
                loaded = json.loads(stage_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    deletions = [str(item) for item in loaded]
            except json.JSONDecodeError:
                deletions = []
        source_path = resolve_written_source_path(action, execute_action)
        expected_entry = execute_reconcile_installed_baseline_history_waiver_sources.relative_stage_path(
            source_path,
            target_root,
        ).as_posix()
        if stage_path.is_file() and expected_entry in deletions:
            state = "matches_staged_delete"
            passes = True
            message = "staged delete manifest still records the reviewed delete target"
        elif not stage_path.is_file():
            state = "missing_staged_delete_manifest"
            passes = False
            message = "staged delete manifest is missing"
        else:
            state = "drifted_staged_delete"
            passes = False
            message = "staged delete manifest no longer records the reviewed delete target"
        return {
            "waiver_id": action.get("waiver_id"),
            "action_code": action.get("action_code"),
            "mode": action.get("mode"),
            "execute_status": execute_status,
            "verification_path": display_path(stage_path),
            "state": state,
            "expected_state": "deleted",
            "current_sha256": sha256_for_file(stage_path) if stage_path.is_file() else "",
            "passes": passes,
            "message": message,
        }

    if execute_status == "written_delete":
        source_path = resolve_written_source_path(action, execute_action)
        if not source_path.exists():
            state = "matches_written_delete"
            passes = True
            message = "written reconcile delete still matches the reviewed delete state"
            current_sha = ""
        else:
            state = "drifted_after_delete"
            passes = False
            message = "written reconcile delete no longer matches the reviewed delete state"
            current_sha = sha256_for_file(source_path)
        return {
            "waiver_id": action.get("waiver_id"),
            "action_code": action.get("action_code"),
            "mode": action.get("mode"),
            "execute_status": execute_status,
            "verification_path": display_path(source_path if source_path.is_relative_to(ROOT) else source_path),
            "state": state,
            "expected_state": "deleted",
            "current_sha256": current_sha,
            "passes": passes,
            "message": message,
        }

    return build_blocked_result(
        action,
        execute_status,
        "",
        f"unexpected execute status for restore_delete: {execute_status}",
    )


def verify_action(
    action: dict,
    execute_action: dict | None,
    *,
    target_root: Path,
    default_stage_dir: Path | None,
) -> dict:
    execute_action = execute_action or {}
    mode = str(action.get("mode", "")).strip()
    if mode == "restore_target":
        return verify_restore_target(
            action,
            execute_action,
            target_root=target_root,
            default_stage_dir=default_stage_dir,
        )
    if mode == "restore_delete":
        return verify_restore_delete(
            action,
            execute_action,
            target_root=target_root,
            default_stage_dir=default_stage_dir,
        )
    execute_status = str(execute_action.get("status", "")).strip()
    if execute_status in {"", "blocked_manual_review"}:
        message = str(execute_action.get("message", "")).strip() or "action still requires manual review"
        return {
            "waiver_id": action.get("waiver_id"),
            "action_code": action.get("action_code"),
            "mode": mode,
            "execute_status": execute_status,
            "verification_path": "",
            "state": "manual_review",
            "expected_state": "manual_review",
            "current_sha256": "",
            "passes": True,
            "message": message,
        }
    return build_blocked_result(
        action,
        execute_status,
        "",
        f"unexpected reconcile verification mode: {mode}",
    )


def build_verification_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
) -> dict:
    execute_payload, resolved_execute_summary_path = load_execute_payload(output_dir, execute_summary_path)
    effective_target_root = target_root
    target_root_value = str(execute_payload.get("target_root", "")).strip()
    if effective_target_root is None and target_root_value:
        effective_target_root = resolve_repo_path(Path(target_root_value))
    if effective_target_root is None:
        effective_target_root = ROOT

    effective_stage_dir = stage_dir
    if effective_stage_dir is None:
        stage_dir_value = str(execute_payload.get("stage_dir", "")).strip()
        if stage_dir_value:
            effective_stage_dir = resolve_repo_path(Path(stage_dir_value))

    reconcile_payload, reconcile_summary_path = ensure_reconcile_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=effective_target_root,
    )
    execute_action_map = build_execute_action_map(execute_payload)

    results: list[dict] = []
    staged_target_match_count = 0
    staged_delete_match_count = 0
    written_target_match_count = 0
    written_delete_match_count = 0
    manual_review_count = 0
    pending_count = 0
    blocked_count = 0
    drift_count = 0

    for action in reconcile_payload.get("actions", []):
        if not isinstance(action, dict):
            continue
        key = (
            str(action.get("waiver_id", "")).strip(),
            str(action.get("action_code", "")).strip(),
        )
        result = verify_action(
            action,
            execute_action_map.get(key),
            target_root=effective_target_root,
            default_stage_dir=effective_stage_dir,
        )
        state = str(result.get("state", "")).strip()
        if state == "matches_staged_target":
            staged_target_match_count += 1
        elif state == "matches_staged_delete":
            staged_delete_match_count += 1
        elif state == "matches_written_target":
            written_target_match_count += 1
        elif state == "matches_written_delete":
            written_delete_match_count += 1
        elif state == "manual_review":
            manual_review_count += 1
        elif state == "pending_execution":
            pending_count += 1
        elif state.startswith("blocked") or state == "unexpected_execute_status":
            blocked_count += 1
        elif result.get("passes") is not True:
            drift_count += 1
        results.append(result)

    verified_count = (
        staged_target_match_count
        + staged_delete_match_count
        + written_target_match_count
        + written_delete_match_count
        + manual_review_count
    )

    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "reconcile_summary_path": reconcile_summary_path,
        "execute_summary_path": resolved_execute_summary_path,
        "target_root": display_path(effective_target_root),
        "stage_dir": display_path(effective_stage_dir) if effective_stage_dir is not None else "",
        "waiver_count": reconcile_payload.get("waiver_count", 0),
        "action_count": len(results),
        "verified_count": verified_count,
        "staged_target_match_count": staged_target_match_count,
        "staged_delete_match_count": staged_delete_match_count,
        "written_target_match_count": written_target_match_count,
        "written_delete_match_count": written_delete_match_count,
        "manual_review_count": manual_review_count,
        "pending_count": pending_count,
        "blocked_count": blocked_count,
        "drift_count": drift_count,
        "passes": pending_count == 0 and blocked_count == 0 and drift_count == 0,
        "results": results,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Reconcile Verification",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Reconcile summary: `{payload.get('reconcile_summary_path', '')}`",
        f"- Execute summary: `{payload.get('execute_summary_path', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Actions: `{payload.get('action_count', 0)}`",
        f"- Verified actions: `{payload.get('verified_count', 0)}`",
        f"- Staged target matches: `{payload.get('staged_target_match_count', 0)}`",
        f"- Staged delete matches: `{payload.get('staged_delete_match_count', 0)}`",
        f"- Written target matches: `{payload.get('written_target_match_count', 0)}`",
        f"- Written delete matches: `{payload.get('written_delete_match_count', 0)}`",
        f"- Manual review actions: `{payload.get('manual_review_count', 0)}`",
        f"- Pending actions: `{payload.get('pending_count', 0)}`",
        f"- Blocked actions: `{payload.get('blocked_count', 0)}`",
        f"- Drift findings: `{payload.get('drift_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Results",
        "",
    ]
    results = payload.get("results", [])
    if not results:
        lines.append("- No source-reconcile verification actions required.")
    else:
        for result in results:
            lines.append(
                f"- `{result.get('waiver_id', '')}` `{result.get('action_code', '')}` state=`{result.get('state', '')}` execute=`{result.get('execute_status', '')}`"
            )
            if result.get("verification_path"):
                lines.append(f"  path: `{result.get('verification_path', '')}`")
            lines.append(f"  message: {result.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    execute_summary_path = resolve_repo_path(args.execute_summary_path) if args.execute_summary_path else None
    payload = build_verification_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "source-reconcile-verify-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "source-reconcile-verify-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source reconcile verification:")
        print(f"- History: {payload['history_path']}")
        print(f"- Action count: {payload['action_count']}")
        print(f"- Verified actions: {payload['verified_count']}")
        print(f"- Pending actions: {payload['pending_count']}")
        print(f"- Blocked actions: {payload['blocked_count']}")
        print(f"- Drift findings: {payload['drift_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
