#!/usr/bin/env python3
"""Audit waiver source files against the latest reviewed apply or execute artifacts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import prepare_installed_baseline_history_waiver_apply
from market_utils import ROOT, load_json, repo_relative_path, sha256_for_file


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit waiver source files against the latest reviewed apply or execute artifacts."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to audit. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing execute artifacts and receiving source-audit summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source audits.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON source-audit output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown source-audit output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when source drift is detected.")
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


def resolve_action_target_path(source_path: str, target_root: Path) -> Path:
    resolved_source = Path(source_path).resolve()
    relative = resolved_source.relative_to(ROOT)
    return (target_root / relative).resolve()


def build_apply_payload(history_path: Path, waiver_tokens: list[str]) -> dict:
    temp_root = ROOT / "dist"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="waiver-source-audit-", dir=temp_root) as temp_dir:
        payload = prepare_installed_baseline_history_waiver_apply.build_apply_payload(
            history_path,
            waiver_tokens,
            Path(temp_dir),
        )
        for waiver in payload.get("waivers", []):
            if not isinstance(waiver, dict):
                continue
            for action in waiver.get("apply_actions", []):
                if not isinstance(action, dict):
                    continue
                target_path_value = str(action.get("target_path", "")).strip()
                if target_path_value and (ROOT / target_path_value).is_file():
                    action["resolved_target_sha256"] = sha256_for_file(ROOT / target_path_value)
                    action["resolved_target_text"] = (ROOT / target_path_value).read_text(encoding="utf-8")
        return payload


def load_execute_action_map(output_dir: Path) -> tuple[dict[tuple[str, str], dict], str]:
    execute_summary_path = output_dir / "execute-summary.json"
    if not execute_summary_path.is_file():
        return {}, ""
    execute_payload = load_json(execute_summary_path)
    action_map: dict[tuple[str, str], dict] = {}
    for action in execute_payload.get("actions", []):
        if not isinstance(action, dict):
            continue
        waiver_id = str(action.get("waiver_id", "")).strip()
        action_code = str(action.get("action_code", "")).strip()
        if waiver_id and action_code:
            action_map[(waiver_id, action_code)] = action
    return action_map, display_path(execute_summary_path)


def build_manual_result(
    *,
    waiver_id: str,
    action: dict,
    execute_status: str,
    audited_path: Path,
) -> dict:
    return {
        "waiver_id": waiver_id,
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "execute_status": execute_status,
        "source_path": display_path(audited_path),
        "state": "manual_review",
        "expected_state": "manual_review",
        "current_sha256": sha256_for_file(audited_path) if audited_path.is_file() else "",
        "passes": True,
        "message": "action still requires manual review; no apply-ready patch is available",
    }


def build_update_result(
    *,
    waiver_id: str,
    action: dict,
    execute_status: str,
    audited_path: Path,
) -> dict:
    source_sha = str(action.get("source_sha256", "")).strip()
    target_sha = str(action.get("resolved_target_sha256", "")).strip() or str(action.get("target_sha256", "")).strip()
    current_exists = audited_path.is_file()
    current_sha = sha256_for_file(audited_path) if current_exists else ""
    write_expected = execute_status == "written"

    result = {
        "waiver_id": waiver_id,
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "execute_status": execute_status,
        "source_path": display_path(audited_path),
        "state": "",
        "expected_state": "target" if write_expected else "source_or_target",
        "current_sha256": current_sha,
        "passes": False,
        "message": "",
    }

    if write_expected:
        if current_exists and current_sha == target_sha:
            result["state"] = "matches_target"
            result["passes"] = True
            result["message"] = "source file still matches the reviewed target after write execution"
        elif not current_exists:
            result["state"] = "drift_missing_after_write"
            result["message"] = "source file is missing after write execution"
        else:
            result["state"] = "drifted_after_write"
            result["message"] = "source file no longer matches the reviewed target after write execution"
        return result

    if current_exists and current_sha == target_sha:
        result["state"] = "matches_target"
        result["passes"] = True
        result["message"] = "source file already matches the reviewed target"
    elif current_exists and source_sha and current_sha == source_sha:
        result["state"] = "matches_source"
        result["passes"] = True
        result["message"] = "source file still matches the reviewed source content"
    elif not current_exists:
        result["state"] = "drift_missing_source"
        result["message"] = "source file is missing before the reviewed update is applied"
    else:
        result["state"] = "drifted"
        result["message"] = "source file no longer matches either the reviewed source or target content"
    return result


def build_delete_result(
    *,
    waiver_id: str,
    action: dict,
    execute_status: str,
    audited_path: Path,
) -> dict:
    source_sha = str(action.get("source_sha256", "")).strip()
    current_exists = audited_path.is_file()
    current_sha = sha256_for_file(audited_path) if current_exists else ""
    write_expected = execute_status == "written_delete"

    result = {
        "waiver_id": waiver_id,
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "execute_status": execute_status,
        "source_path": display_path(audited_path),
        "state": "",
        "expected_state": "deleted" if write_expected else "source_or_deleted",
        "current_sha256": current_sha,
        "passes": False,
        "message": "",
    }

    if write_expected:
        if not current_exists:
            result["state"] = "matches_delete"
            result["passes"] = True
            result["message"] = "source file remains deleted after write execution"
        else:
            result["state"] = "drifted_after_delete"
            result["message"] = "source file still exists after delete execution"
        return result

    if not current_exists:
        result["state"] = "matches_delete"
        result["passes"] = True
        result["message"] = "source file is already deleted as reviewed"
    elif source_sha and current_sha == source_sha:
        result["state"] = "matches_source"
        result["passes"] = True
        result["message"] = "source file still matches the reviewed pre-delete content"
    else:
        result["state"] = "drifted"
        result["message"] = "source file no longer matches the reviewed pre-delete content"
    return result


def audit_action(
    action: dict,
    *,
    waiver_id: str,
    execute_action: dict | None,
    target_root: Path,
) -> dict:
    execute_status = str((execute_action or {}).get("status", "")).strip()
    audited_path = resolve_action_target_path(str(action.get("source_path", "")).strip(), target_root)

    has_target = bool(str(action.get("target_path", "")).strip())
    has_patch = bool(str(action.get("patch_path", "")).strip())

    if not has_target and not has_patch:
        return build_manual_result(
            waiver_id=waiver_id,
            action=action,
            execute_status=execute_status,
            audited_path=audited_path,
        )

    if has_target:
        return build_update_result(
            waiver_id=waiver_id,
            action=action,
            execute_status=execute_status,
            audited_path=audited_path,
        )

    return build_delete_result(
        waiver_id=waiver_id,
        action=action,
        execute_status=execute_status,
        audited_path=audited_path,
    )


def build_source_audit_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    apply_payload = build_apply_payload(history_path, waiver_tokens)
    execute_action_map, execute_summary_path = load_execute_action_map(output_dir)

    results: list[dict] = []
    source_match_count = 0
    target_match_count = 0
    deleted_match_count = 0
    drift_count = 0
    manual_review_count = 0
    write_record_count = 0
    staged_record_count = 0

    for waiver in apply_payload.get("waivers", []):
        if not isinstance(waiver, dict):
            continue
        waiver_id = str(waiver.get("id", "")).strip()
        for action in waiver.get("apply_actions", []):
            if not isinstance(action, dict):
                continue
            execute_action = execute_action_map.get((waiver_id, str(action.get("action_code", "")).strip()))
            result = audit_action(
                action,
                waiver_id=waiver_id,
                execute_action=execute_action,
                target_root=target_root,
            )
            execute_status = str(result.get("execute_status", "")).strip()
            if execute_status in {"written", "written_delete"}:
                write_record_count += 1
            elif execute_status in {"staged", "staged_delete"}:
                staged_record_count += 1

            state = str(result.get("state", "")).strip()
            if state == "matches_source":
                source_match_count += 1
            elif state == "matches_target":
                target_match_count += 1
            elif state == "matches_delete":
                deleted_match_count += 1
            elif state == "manual_review":
                manual_review_count += 1
            elif result.get("passes") is not True:
                drift_count += 1
            results.append(result)

    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "target_root": display_path(target_root),
        "execute_summary_path": execute_summary_path,
        "waiver_count": apply_payload.get("waiver_count", 0),
        "action_count": len(results),
        "source_match_count": source_match_count,
        "target_match_count": target_match_count,
        "deleted_match_count": deleted_match_count,
        "pending_count": source_match_count,
        "applied_count": target_match_count + deleted_match_count,
        "manual_review_count": manual_review_count,
        "drift_count": drift_count,
        "write_record_count": write_record_count,
        "staged_record_count": staged_record_count,
        "passes": drift_count == 0,
        "results": results,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Audit",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Execute summary: `{payload.get('execute_summary_path', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Actions: `{payload.get('action_count', 0)}`",
        f"- Pending/source matches: `{payload.get('pending_count', 0)}`",
        f"- Applied matches: `{payload.get('applied_count', 0)}`",
        f"- Manual review actions: `{payload.get('manual_review_count', 0)}`",
        f"- Drift findings: `{payload.get('drift_count', 0)}`",
        f"- Write records: `{payload.get('write_record_count', 0)}`",
        f"- Staged records: `{payload.get('staged_record_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Results",
        "",
    ]
    results = payload.get("results", [])
    if not results:
        lines.append("- No source-audit actions required.")
    else:
        for result in results:
            lines.append(
                f"- `{result.get('waiver_id', '')}` `{result.get('action_code', '')}` state=`{result.get('state', '')}` execute=`{result.get('execute_status', '')}`"
            )
            lines.append(f"  path: `{result.get('source_path', '')}`")
            lines.append(f"  message: {result.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else ROOT
    payload = build_source_audit_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        target_root=target_root,
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "source-audit-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "source-audit-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source audit:")
        print(f"- History: {payload['history_path']}")
        print(f"- Actions: {payload['action_count']}")
        print(f"- Pending/source matches: {payload['pending_count']}")
        print(f"- Applied matches: {payload['applied_count']}")
        print(f"- Drift findings: {payload['drift_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
