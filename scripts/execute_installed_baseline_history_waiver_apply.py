#!/usr/bin/env python3
"""Stage or write reviewed installed baseline history waiver apply packs safely."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import prepare_installed_baseline_history_waiver_apply
from market_utils import ROOT, build_hashed_artifact_name, load_json, repo_relative_path, sha256_for_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stage or write reviewed installed baseline history waiver apply packs safely."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to execute. Defaults to all known waivers.",
    )
    parser.add_argument("--output-dir", type=Path, help="Directory containing or receiving apply-pack artifacts.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory for rendered file changes.")
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for --write mode.")
    parser.add_argument("--write", action="store_true", help="Write approved changes into the target root.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON execution summary output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown execution summary output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when safety checks block execution.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_json_payload(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Apply Execution",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Write mode: `{payload.get('write_mode', False)}`",
        f"- Action count: `{payload.get('action_count', 0)}`",
        f"- Staged updates: `{payload.get('staged_update_count', 0)}`",
        f"- Staged deletes: `{payload.get('staged_delete_count', 0)}`",
        f"- Written updates: `{payload.get('written_update_count', 0)}`",
        f"- Written deletes: `{payload.get('written_delete_count', 0)}`",
        f"- Blocked actions: `{payload.get('blocked_action_count', 0)}`",
        f"- Source mismatches: `{payload.get('source_mismatch_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Actions",
        "",
    ]
    actions = payload.get("actions", [])
    if not actions:
        lines.append("- No execution actions required.")
    else:
        for action in actions:
            lines.append(
                f"- `{action.get('waiver_id', '')}` `{action.get('action_code', '')}` status=`{action.get('status', '')}`"
            )
            if action.get("stage_path"):
                lines.append(f"  stage: `{action.get('stage_path', '')}`")
            if action.get("write_path"):
                lines.append(f"  write: `{action.get('write_path', '')}`")
            if action.get("message"):
                lines.append(f"  message: {action.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def resolve_action_target_path(source_path: str, target_root: Path) -> Path:
    resolved_source = Path(source_path).resolve()
    relative = resolved_source.relative_to(ROOT)
    return (target_root / relative).resolve()


def ensure_apply_payload(history_path: Path, waiver_tokens: list[str], output_dir: Path) -> dict:
    summary_path = output_dir / "apply-summary.json"
    if summary_path.is_file():
        return load_json(summary_path)

    payload = prepare_installed_baseline_history_waiver_apply.build_apply_payload(history_path, waiver_tokens, output_dir)
    write_text(summary_path, render_json_payload(payload))
    write_text(output_dir / "apply-summary.md", prepare_installed_baseline_history_waiver_apply.render_markdown(payload))
    return payload


def prepare_stage_dir(stage_dir: Path | None) -> Path | None:
    if stage_dir is None:
        return None
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)
    return stage_dir


def relative_stage_path(source_path: Path, target_root: Path) -> Path:
    if source_path.is_relative_to(target_root):
        return source_path.relative_to(target_root)
    if source_path.is_relative_to(ROOT):
        return source_path.relative_to(ROOT)
    return Path(source_path.name)


def staged_target_path(action: dict, source_path: Path, stage_dir: Path) -> Path:
    waiver_id = str(action.get("waiver_id", "")).strip() or "unknown-waiver"
    action_code = str(action.get("action_code", "")).strip() or "action"
    waiver_segment = build_hashed_artifact_name(waiver_id, fallback="waiver")
    filename = build_hashed_artifact_name(
        action_code,
        source_path.stem or source_path.name,
        suffix=source_path.suffix or ".json",
        fallback="target",
    )
    return stage_dir / "targets" / waiver_segment / filename


def execute_action(
    action: dict,
    *,
    waiver_id: str,
    output_dir: Path,
    target_root: Path,
    stage_dir: Path | None,
    write_mode: bool,
) -> dict:
    source_path = str(action.get("source_path", "")).strip()
    actual_target_path = resolve_action_target_path(source_path, target_root)
    result = {
        "waiver_id": waiver_id,
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "status": "skipped",
        "stage_path": "",
        "write_path": "",
        "message": "",
        "source_path": str(actual_target_path),
    }

    if not actual_target_path.is_file():
        result["status"] = "blocked_missing_source"
        result["message"] = f"source file missing: {actual_target_path}"
        return result

    expected_source_sha = str(action.get("source_sha256", "")).strip()
    if expected_source_sha and sha256_for_file(actual_target_path) != expected_source_sha:
        result["status"] = "blocked_source_mismatch"
        result["message"] = "source file no longer matches the reviewed apply pack"
        return result

    patch_path = str(action.get("patch_path", "")).strip()
    target_path = str(action.get("target_path", "")).strip()

    if target_path:
        rendered_target_path = ROOT / target_path
        target_text = rendered_target_path.read_text(encoding="utf-8")
        if stage_dir is not None:
            staged_path = staged_target_path(action, actual_target_path, stage_dir)
            write_text(staged_path, target_text)
            result["stage_path"] = repo_relative_path(staged_path)
        if write_mode:
            actual_target_path.parent.mkdir(parents=True, exist_ok=True)
            actual_target_path.write_text(target_text, encoding="utf-8")
            result["write_path"] = str(actual_target_path)
        result["status"] = "written" if write_mode else "staged"
        return result

    if patch_path:
        if stage_dir is not None:
            deletions_path = stage_dir / "deletions.json"
            existing = []
            if deletions_path.is_file():
                existing = json.loads(deletions_path.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            relative_target = relative_stage_path(actual_target_path, target_root).as_posix()
            if relative_target not in existing:
                existing.append(relative_target)
            write_text(deletions_path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
            result["stage_path"] = repo_relative_path(deletions_path)
        if write_mode:
            actual_target_path.unlink()
            result["write_path"] = str(actual_target_path)
        result["status"] = "written_delete" if write_mode else "staged_delete"
        return result

    result["status"] = "blocked_manual_review"
    result["message"] = "action does not contain an apply-ready patch"
    return result


def build_execution_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    stage_dir: Path | None,
    target_root: Path,
    write_mode: bool,
) -> dict:
    apply_payload = ensure_apply_payload(history_path, waiver_tokens, output_dir)
    staged_dir = prepare_stage_dir(stage_dir)

    actions: list[dict] = []
    staged_update_count = 0
    staged_delete_count = 0
    written_update_count = 0
    written_delete_count = 0
    blocked_action_count = 0
    source_mismatch_count = 0

    for waiver in apply_payload.get("waivers", []):
        if not isinstance(waiver, dict):
            continue
        waiver_id = str(waiver.get("id", "")).strip()
        for action in waiver.get("apply_actions", []):
            if not isinstance(action, dict):
                continue
            result = execute_action(
                action,
                waiver_id=waiver_id,
                output_dir=output_dir,
                target_root=target_root,
                stage_dir=staged_dir,
                write_mode=write_mode,
            )
            status = str(result.get("status", "")).strip()
            if status == "staged":
                staged_update_count += 1
            elif status == "staged_delete":
                staged_delete_count += 1
            elif status == "written":
                written_update_count += 1
            elif status == "written_delete":
                written_delete_count += 1
            elif status.startswith("blocked"):
                blocked_action_count += 1
                if status == "blocked_source_mismatch":
                    source_mismatch_count += 1
            actions.append(result)

    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": repo_relative_path(output_dir),
        "stage_dir": repo_relative_path(staged_dir) if staged_dir is not None else "",
        "target_root": repo_relative_path(target_root) if target_root.is_relative_to(ROOT) else str(target_root),
        "write_mode": write_mode,
        "action_count": len(actions),
        "staged_update_count": staged_update_count,
        "staged_delete_count": staged_delete_count,
        "written_update_count": written_update_count,
        "written_delete_count": written_delete_count,
        "blocked_action_count": blocked_action_count,
        "source_mismatch_count": source_mismatch_count,
        "passes": blocked_action_count == 0,
        "actions": actions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else prepare_installed_baseline_history_waiver_apply.DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else ROOT
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else (None if args.write else (output_dir / "staged-root"))

    payload = build_execution_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        stage_dir=stage_dir,
        target_root=target_root,
        write_mode=args.write,
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "execute-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "execute-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver apply execution:")
        print(f"- History: {payload['history_path']}")
        print(f"- Action count: {payload['action_count']}")
        print(f"- Staged updates: {payload['staged_update_count']}")
        print(f"- Staged deletes: {payload['staged_delete_count']}")
        print(f"- Written updates: {payload['written_update_count']}")
        print(f"- Written deletes: {payload['written_delete_count']}")
        print(f"- Blocked actions: {payload['blocked_action_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
