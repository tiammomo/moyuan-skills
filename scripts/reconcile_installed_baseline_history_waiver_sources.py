#!/usr/bin/env python3
"""Build reconcile-ready artifacts for waiver source drift findings."""

from __future__ import annotations

import argparse
import difflib
import json
import shutil
from pathlib import Path

import audit_installed_baseline_history_waiver_sources
from market_utils import ROOT, repo_relative_path, sha256_for_file


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build reconcile-ready artifacts for waiver source drift findings."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to reconcile. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-audit artifacts and receiving source-reconcile outputs.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source reconciliation.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON source-reconcile output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown source-reconcile output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when reconcile follow-up is required.")
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


def unified_patch(source_path: Path, source_text: str, target_text: str | None) -> str:
    label = display_path(source_path)
    target_lines = [] if target_text is None else target_text.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            source_text.splitlines(keepends=True),
            target_lines,
            fromfile=f"a/{label}",
            tofile="/dev/null" if target_text is None else f"b/{label}",
        )
    )


def build_action_map(apply_payload: dict) -> dict[tuple[str, str], dict]:
    action_map: dict[tuple[str, str], dict] = {}
    for waiver in apply_payload.get("waivers", []):
        if not isinstance(waiver, dict):
            continue
        waiver_id = str(waiver.get("id", "")).strip()
        for action in waiver.get("apply_actions", []):
            if not isinstance(action, dict):
                continue
            action_code = str(action.get("action_code", "")).strip()
            if waiver_id and action_code:
                action_map[(waiver_id, action_code)] = action
    return action_map


def build_restore_target_action(
    *,
    result: dict,
    action: dict,
    actual_source_path: Path,
    artifact_dir: Path,
    action_index: int,
) -> dict:
    target_text = str(action.get("resolved_target_text", ""))
    if not target_text:
        target_path = ROOT / str(action.get("target_path", "")).strip()
        target_text = target_path.read_text(encoding="utf-8")
    current_text = actual_source_path.read_text(encoding="utf-8") if actual_source_path.is_file() else ""
    patch_text = unified_patch(actual_source_path, current_text, target_text)

    target_artifact = artifact_dir / f"reconcile-action-{action_index:02d}.target.json"
    patch_artifact = artifact_dir / f"reconcile-action-{action_index:02d}.patch"
    write_text(target_artifact, target_text)
    write_text(patch_artifact, patch_text)

    return {
        "waiver_id": result.get("waiver_id"),
        "action_code": result.get("action_code"),
        "mode": "restore_target",
        "source_state": result.get("state"),
        "execute_status": result.get("execute_status"),
        "source_path": result.get("source_path"),
        "current_sha256": result.get("current_sha256", ""),
        "target_sha256": sha256_for_file(target_artifact),
        "target_artifact_path": display_path(target_artifact),
        "patch_path": display_path(patch_artifact),
        "message": "restore the source file to the latest reviewed target content",
    }


def build_restore_delete_action(
    *,
    result: dict,
    actual_source_path: Path,
    artifact_dir: Path,
    action_index: int,
) -> dict:
    current_text = actual_source_path.read_text(encoding="utf-8") if actual_source_path.is_file() else ""
    patch_text = unified_patch(actual_source_path, current_text, None)
    patch_artifact = artifact_dir / f"reconcile-action-{action_index:02d}.patch"
    write_text(patch_artifact, patch_text)

    return {
        "waiver_id": result.get("waiver_id"),
        "action_code": result.get("action_code"),
        "mode": "restore_delete",
        "source_state": result.get("state"),
        "execute_status": result.get("execute_status"),
        "source_path": result.get("source_path"),
        "current_sha256": result.get("current_sha256", ""),
        "target_sha256": "",
        "target_artifact_path": "",
        "patch_path": display_path(patch_artifact),
        "message": "delete the source file again so it matches the reviewed delete state",
    }


def build_review_action(
    *,
    result: dict,
    artifact_dir: Path,
    action_index: int,
) -> dict:
    review_artifact = artifact_dir / f"reconcile-action-{action_index:02d}.review.json"
    review_payload = {
        "waiver_id": result.get("waiver_id"),
        "action_code": result.get("action_code"),
        "state": result.get("state"),
        "execute_status": result.get("execute_status"),
        "source_path": result.get("source_path"),
        "current_sha256": result.get("current_sha256", ""),
        "message": "review manually before restoring because no authoritative written state is available",
    }
    write_text(review_artifact, render_json_payload(review_payload))
    review_payload["review_artifact_path"] = display_path(review_artifact)
    return {
        **review_payload,
        "mode": "review_source_drift",
        "target_artifact_path": "",
        "patch_path": "",
    }


def build_reconcile_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_payload = audit_installed_baseline_history_waiver_sources.build_source_audit_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
    )
    apply_payload = audit_installed_baseline_history_waiver_sources.build_apply_payload(history_path, waiver_tokens)
    action_map = build_action_map(apply_payload)

    reconcile_root = output_dir / "source-reconcile"
    if reconcile_root.exists():
        shutil.rmtree(reconcile_root)
    reconcile_root.mkdir(parents=True, exist_ok=True)

    actions: list[dict] = []
    restore_target_count = 0
    restore_delete_count = 0
    review_action_count = 0

    waiver_counters: dict[str, int] = {}

    for result in audit_payload.get("results", []):
        if not isinstance(result, dict) or result.get("passes") is True:
            continue

        waiver_id = str(result.get("waiver_id", "")).strip()
        action_code = str(result.get("action_code", "")).strip()
        execute_status = str(result.get("execute_status", "")).strip()
        action = action_map.get((waiver_id, action_code))
        if action is None:
            continue

        counter = waiver_counters.get(waiver_id, 0) + 1
        waiver_counters[waiver_id] = counter
        artifact_dir = reconcile_root / "waivers" / (waiver_id or "unknown-waiver")
        artifact_dir.mkdir(parents=True, exist_ok=True)

        actual_source_path = resolve_repo_path(Path(str(result.get("source_path", "")).strip()))

        if execute_status == "written" and str(action.get("target_path", "")).strip():
            actions.append(
                build_restore_target_action(
                    result=result,
                    action=action,
                    actual_source_path=actual_source_path,
                    artifact_dir=artifact_dir,
                    action_index=counter,
                )
            )
            restore_target_count += 1
            continue

        if execute_status == "written_delete" and str(action.get("patch_path", "")).strip():
            actions.append(
                build_restore_delete_action(
                    result=result,
                    actual_source_path=actual_source_path,
                    artifact_dir=artifact_dir,
                    action_index=counter,
                )
            )
            restore_delete_count += 1
            continue

        actions.append(
            build_review_action(
                result=result,
                artifact_dir=artifact_dir,
                action_index=counter,
            )
        )
        review_action_count += 1

    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "target_root": display_path(target_root),
        "audit_summary_path": audit_payload.get("output_dir", ""),
        "waiver_count": audit_payload.get("waiver_count", 0),
        "drift_count": audit_payload.get("drift_count", 0),
        "action_count": len(actions),
        "restore_target_count": restore_target_count,
        "restore_delete_count": restore_delete_count,
        "review_action_count": review_action_count,
        "passes": len(actions) == 0,
        "actions": actions,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Reconcile",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Drift findings: `{payload.get('drift_count', 0)}`",
        f"- Reconcile actions: `{payload.get('action_count', 0)}`",
        f"- Restore target actions: `{payload.get('restore_target_count', 0)}`",
        f"- Restore delete actions: `{payload.get('restore_delete_count', 0)}`",
        f"- Review actions: `{payload.get('review_action_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Actions",
        "",
    ]
    actions = payload.get("actions", [])
    if not actions:
        lines.append("- No source-reconcile actions required.")
    else:
        for action in actions:
            lines.append(
                f"- `{action.get('waiver_id', '')}` `{action.get('action_code', '')}` mode=`{action.get('mode', '')}`"
            )
            if action.get("patch_path"):
                lines.append(f"  patch: `{action.get('patch_path', '')}`")
            if action.get("target_artifact_path"):
                lines.append(f"  target: `{action.get('target_artifact_path', '')}`")
            if action.get("review_artifact_path"):
                lines.append(f"  review: `{action.get('review_artifact_path', '')}`")
            lines.append(f"  message: {action.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else ROOT
    payload = build_reconcile_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        target_root=target_root,
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "source-reconcile-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "source-reconcile-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source reconcile:")
        print(f"- History: {payload['history_path']}")
        print(f"- Drift findings: {payload['drift_count']}")
        print(f"- Reconcile actions: {payload['action_count']}")
        print(f"- Restore target actions: {payload['restore_target_count']}")
        print(f"- Restore delete actions: {payload['restore_delete_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
