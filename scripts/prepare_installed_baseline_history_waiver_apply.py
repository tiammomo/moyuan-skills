#!/usr/bin/env python3
"""Generate apply-ready patch outputs for installed baseline history waiver changes."""

from __future__ import annotations

import argparse
import difflib
import json
import shutil
from pathlib import Path

import preview_installed_baseline_history_waiver_execution
from market_utils import ROOT, load_json, repo_relative_path


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-apply"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare apply-ready patch outputs for installed baseline history waiver changes."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to prepare. Defaults to all known waivers.",
    )
    parser.add_argument("--output-dir", type=Path, help="Optional directory for generated apply artifacts.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON apply summary output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown apply summary output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when apply follow-up is required.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_json_payload(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def unified_patch(source_path: Path, source_text: str, target_text: str | None) -> str:
    relative_path = repo_relative_path(source_path)
    target_lines = [] if target_text is None else target_text.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            source_text.splitlines(keepends=True),
            target_lines,
            fromfile=f"a/{relative_path}",
            tofile="/dev/null" if target_text is None else f"b/{relative_path}",
        )
    )


def render_waiver_apply_markdown(waiver_payload: dict) -> str:
    lines = [
        f"# Waiver Apply Pack: {waiver_payload.get('id', '')}",
        "",
        f"- Source path: `{waiver_payload.get('source_path', '')}`",
        f"- Apply actions: `{len(waiver_payload.get('apply_actions', []))}`",
        "",
        "## Actions",
        "",
    ]
    actions = waiver_payload.get("apply_actions", [])
    if not actions:
        lines.append("- No apply actions required.")
    else:
        for action in actions:
            lines.append(
                f"- `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` patch=`{action.get('patch_path', '')}`"
            )
            lines.append(f"  summary: {action.get('summary', '')}")
            if action.get("target_path"):
                lines.append(f"  target: `{action.get('target_path', '')}`")
            if action.get("preview_path"):
                lines.append(f"  preview: `{action.get('preview_path', '')}`")
    return "\n".join(lines).rstrip() + "\n"


def build_update_apply_action(action_preview: dict, output_dir: Path) -> tuple[dict, str, str]:
    source_path = Path(str(action_preview.get("source_path", "")))
    draft_relative = str(action_preview.get("draft_path", "")).strip()
    draft_path = output_dir / draft_relative
    draft_payload = load_json(draft_path)
    target_payload = preview_installed_baseline_history_waiver_execution.normalize_compare_payload(draft_payload)
    target_text = render_json_payload(target_payload)
    source_text = source_path.read_text(encoding="utf-8")
    patch_text = unified_patch(source_path, source_text, target_text)
    return (
        {
            "action_code": action_preview.get("action_code"),
            "mode": action_preview.get("mode"),
            "summary": action_preview.get("summary"),
            "why": action_preview.get("why"),
            "source_path": str(source_path),
            "preview_path": action_preview.get("draft_path", ""),
            "target_path": "",
            "patch_path": "",
            "change_count": action_preview.get("change_count", 0),
            "candidate_transition": action_preview.get("candidate_transition"),
            "candidate_metrics": action_preview.get("candidate_metrics", []),
            "draft_strategy": action_preview.get("draft_strategy"),
        },
        target_text,
        patch_text,
    )


def build_delete_apply_action(action_preview: dict) -> tuple[dict, str | None, str]:
    source_path = Path(str(action_preview.get("source_path", "")))
    source_text = source_path.read_text(encoding="utf-8")
    patch_text = unified_patch(source_path, source_text, None)
    return (
        {
            "action_code": action_preview.get("action_code"),
            "mode": action_preview.get("mode"),
            "summary": action_preview.get("summary"),
            "why": action_preview.get("why"),
            "source_path": str(source_path),
            "preview_path": action_preview.get("review_path", ""),
            "target_path": "",
            "patch_path": "",
            "change_count": action_preview.get("change_count", 0),
            "candidate_transition": action_preview.get("candidate_transition"),
            "candidate_metrics": action_preview.get("candidate_metrics", []),
            "review_steps": action_preview.get("review_steps", []),
        },
        None,
        patch_text,
    )


def build_manual_apply_action(action_preview: dict) -> tuple[dict, str | None, str]:
    return (
        {
            "action_code": action_preview.get("action_code"),
            "mode": action_preview.get("mode"),
            "summary": action_preview.get("summary"),
            "why": action_preview.get("why"),
            "source_path": action_preview.get("source_path", ""),
            "preview_path": action_preview.get("review_path", ""),
            "target_path": "",
            "patch_path": "",
            "change_count": action_preview.get("change_count", 0),
            "candidate_transition": action_preview.get("candidate_transition"),
            "candidate_metrics": action_preview.get("candidate_metrics", []),
            "review_steps": action_preview.get("review_steps", []),
        },
        None,
        "",
    )


def build_apply_payload(history_path: Path, waiver_tokens: list[str], output_dir: Path) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    preview_payload = preview_installed_baseline_history_waiver_execution.build_preview_payload(
        history_path,
        waiver_tokens,
        output_dir,
    )

    combined_patches: list[str] = []
    waivers: list[dict] = []
    action_count = 0
    patch_count = 0
    update_patch_count = 0
    delete_patch_count = 0
    manual_review_count = 0

    for waiver_preview in preview_payload.get("waivers", []):
        if not isinstance(waiver_preview, dict):
            continue
        artifact_dir_value = str(waiver_preview.get("artifact_dir", "")).strip()
        artifact_dir = ROOT / artifact_dir_value if artifact_dir_value else None
        apply_actions: list[dict] = []

        for index, action_preview in enumerate(waiver_preview.get("action_previews", []), start=1):
            if not isinstance(action_preview, dict):
                continue
            mode = str(action_preview.get("mode", "")).strip()
            if mode == "draft_update":
                action_payload, target_text, patch_text = build_update_apply_action(action_preview, output_dir)
                update_patch_count += 1
            elif mode == "remove_review":
                action_payload, target_text, patch_text = build_delete_apply_action(action_preview)
                delete_patch_count += 1
            else:
                action_payload, target_text, patch_text = build_manual_apply_action(action_preview)
                manual_review_count += 1

            action_count += 1
            action_name = f"apply-action-{index:02d}"
            if artifact_dir is not None:
                if target_text is not None:
                    target_path = artifact_dir / f"{action_name}.target.json"
                    write_text(target_path, target_text)
                    action_payload["target_path"] = repo_relative_path(target_path)
                if patch_text:
                    patch_path = artifact_dir / f"{action_name}.patch"
                    write_text(patch_path, patch_text)
                    action_payload["patch_path"] = repo_relative_path(patch_path)
                    combined_patches.append(patch_text)
                    patch_count += 1
                if not patch_text and mode != "draft_update":
                    review_path = artifact_dir / f"{action_name}.review.json"
                    write_text(review_path, render_json_payload(action_payload))
                    action_payload["review_artifact_path"] = repo_relative_path(review_path)
            apply_actions.append(action_payload)

        waiver_apply = {
            "id": waiver_preview.get("id"),
            "title": waiver_preview.get("title"),
            "source_path": waiver_preview.get("source_path", ""),
            "artifact_dir": artifact_dir_value,
            "apply_actions": apply_actions,
            "apply_path": "",
            "apply_markdown_path": "",
        }

        if artifact_dir is not None:
            apply_json_path = artifact_dir / "apply.json"
            apply_markdown_path = artifact_dir / "apply.md"
            write_text(apply_json_path, render_json_payload(waiver_apply))
            write_text(apply_markdown_path, render_waiver_apply_markdown(waiver_apply))
            waiver_apply["apply_path"] = repo_relative_path(apply_json_path)
            waiver_apply["apply_markdown_path"] = repo_relative_path(apply_markdown_path)
            write_text(apply_json_path, render_json_payload(waiver_apply))
            write_text(apply_markdown_path, render_waiver_apply_markdown(waiver_apply))

        waivers.append(waiver_apply)

    combined_patch_path = output_dir / "apply.patch"
    if combined_patches:
        write_text(combined_patch_path, "".join(combined_patches))

    return {
        "history_path": preview_payload.get("history_path", ""),
        "waiver_count": preview_payload.get("waiver_count", 0),
        "finding_count": preview_payload.get("finding_count", 0),
        "preview_count": preview_payload.get("preview_count", 0),
        "action_count": action_count,
        "patch_count": patch_count,
        "update_patch_count": update_patch_count,
        "delete_patch_count": delete_patch_count,
        "manual_review_count": manual_review_count,
        "passes": action_count == 0,
        "output_dir": repo_relative_path(output_dir),
        "combined_patch_path": repo_relative_path(combined_patch_path) if combined_patches else "",
        "waivers": waivers,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Apply Pack",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Preview actions: `{payload.get('preview_count', 0)}`",
        f"- Apply actions: `{payload.get('action_count', 0)}`",
        f"- Patch files: `{payload.get('patch_count', 0)}`",
        f"- Update patches: `{payload.get('update_patch_count', 0)}`",
        f"- Delete patches: `{payload.get('delete_patch_count', 0)}`",
        f"- Manual review actions: `{payload.get('manual_review_count', 0)}`",
        f"- Combined patch: `{payload.get('combined_patch_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Waivers",
        "",
    ]
    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No apply actions required.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` apply_actions=`{len(waiver.get('apply_actions', []))}` apply_path=`{waiver.get('apply_path', '')}`"
            )
            for action in waiver.get("apply_actions", []):
                lines.append(
                    f"  - `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` patch=`{action.get('patch_path', '')}`"
                )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    payload = build_apply_payload(args.history, args.waiver, output_dir)

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "apply-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "apply-summary.md")

    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver apply pack:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Apply actions: {payload['action_count']}")
        print(f"- Patch files: {payload['patch_count']}")
        print(f"- Manual review actions: {payload['manual_review_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
