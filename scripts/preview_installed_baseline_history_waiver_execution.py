#!/usr/bin/env python3
"""Build review-friendly previews for installed baseline history waiver execution drafts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import draft_installed_baseline_history_waiver_execution
from market_utils import ROOT, load_json, repo_relative_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare generated waiver execution drafts against source waiver files."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to preview. Defaults to all known waivers.",
    )
    parser.add_argument("--output-dir", type=Path, help="Optional directory for generated preview artifacts.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON preview summary output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown preview summary output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when review previews are present.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_compare_payload(payload: dict) -> dict:
    normalized = json.loads(json.dumps(payload, ensure_ascii=False))
    if isinstance(normalized, dict):
        normalized.pop("_draft", None)
    return normalized


def flatten_payload(value: object, prefix: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        flattened: dict[str, object] = {}
        for key in sorted(value):
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(flatten_payload(value[key], next_prefix))
        return flattened
    return {prefix: value}


def compare_payloads(source_payload: dict, draft_payload: dict) -> list[dict]:
    source_flat = flatten_payload(normalize_compare_payload(source_payload))
    draft_flat = flatten_payload(normalize_compare_payload(draft_payload))
    changes: list[dict] = []
    for path in sorted(set(source_flat) | set(draft_flat)):
        before = source_flat.get(path, None)
        after = draft_flat.get(path, None)
        if before == after:
            continue
        if path not in source_flat:
            change_type = "added"
        elif path not in draft_flat:
            change_type = "removed"
        else:
            change_type = "modified"
        changes.append(
            {
                "path": path,
                "change_type": change_type,
                "before": before,
                "after": after,
            }
        )
    return changes


def summarize_draft_preview(action: dict, output_dir: Path) -> dict:
    source_path = Path(str(action.get("source_path", "")))
    draft_relative = str(action.get("draft_path", "")).strip()
    draft_path = output_dir / draft_relative if draft_relative else None
    source_payload = load_json(source_path)
    draft_payload = load_json(draft_path) if draft_path is not None else {}
    changes = compare_payloads(source_payload, draft_payload)
    return {
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "summary": action.get("summary"),
        "why": action.get("why"),
        "source_path": str(source_path),
        "draft_path": draft_relative,
        "candidate_transition": action.get("candidate_transition"),
        "candidate_metrics": action.get("candidate_metrics", []),
        "change_count": len(changes),
        "changes": changes,
        "draft_strategy": draft_payload.get("_draft", {}).get("strategy"),
    }


def summarize_review_preview(action: dict) -> dict:
    review_relative = str(action.get("review_path", "")).strip()
    changes = [
        {
            "path": "__file__",
            "change_type": "review",
            "before": str(action.get("source_path", "")),
            "after": str(action.get("delete_path", review_relative or "manual review")),
        }
    ]
    return {
        "action_code": action.get("action_code"),
        "mode": action.get("mode"),
        "summary": action.get("summary"),
        "why": action.get("why"),
        "source_path": str(action.get("source_path", "")),
        "review_path": review_relative,
        "candidate_transition": action.get("candidate_transition"),
        "candidate_metrics": action.get("candidate_metrics", []),
        "change_count": len(changes),
        "changes": changes,
        "review_steps": action.get("review_steps", []),
    }


def render_waiver_preview_markdown(waiver_preview: dict) -> str:
    lines = [
        f"# Waiver Preview: {waiver_preview.get('id', '')}",
        "",
        f"- Source path: `{waiver_preview.get('source_path', '')}`",
        f"- Preview actions: `{len(waiver_preview.get('action_previews', []))}`",
        "",
        "## Actions",
        "",
    ]
    action_previews = waiver_preview.get("action_previews", [])
    if not action_previews:
        lines.append("- No preview actions required.")
    else:
        for action in action_previews:
            lines.append(
                f"- `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` changes=`{action.get('change_count', 0)}`"
            )
            lines.append(f"  summary: {action.get('summary', '')}")
            if action.get("draft_path"):
                lines.append(f"  draft: `{action.get('draft_path', '')}`")
            if action.get("review_path"):
                lines.append(f"  review: `{action.get('review_path', '')}`")
            for change in action.get("changes", []):
                before = json.dumps(change.get("before"), ensure_ascii=False)
                after = json.dumps(change.get("after"), ensure_ascii=False)
                lines.append(
                    f"  - `{change.get('path', '')}` {change.get('change_type', '')}: {before} -> {after}"
                )
    return "\n".join(lines).rstrip() + "\n"


def build_preview_payload(history_path: Path, waiver_tokens: list[str], output_dir: Path | None) -> dict:
    temp_dir_handle: tempfile.TemporaryDirectory[str] | None = None
    if output_dir is None:
        temp_dir_handle = tempfile.TemporaryDirectory(prefix="waiver-preview-", dir=ROOT / "dist")
        execution_dir = Path(temp_dir_handle.name)
        persist_artifacts = False
    else:
        execution_dir = output_dir
        persist_artifacts = True

    try:
        execution_payload = draft_installed_baseline_history_waiver_execution.build_execution_payload(
            history_path,
            waiver_tokens,
            execution_dir,
        )

        waivers: list[dict] = []
        preview_count = 0
        draft_preview_count = 0
        cleanup_preview_count = 0
        review_preview_count = 0

        for waiver in execution_payload.get("waivers", []):
            if not isinstance(waiver, dict):
                continue
            action_previews: list[dict] = []
            for action in waiver.get("execution_actions", []):
                if not isinstance(action, dict):
                    continue
                if action.get("mode") == "draft_update":
                    action_preview = summarize_draft_preview(action, execution_dir)
                    draft_preview_count += 1
                else:
                    action_preview = summarize_review_preview(action)
                    cleanup_preview_count += 1
                    review_preview_count += 1
                action_previews.append(action_preview)
                preview_count += 1

            waiver_preview = {
                "id": waiver.get("id"),
                "title": waiver.get("title"),
                "source_path": waiver.get("path", ""),
                "artifact_dir": waiver.get("artifact_dir", "") if persist_artifacts else "",
                "action_previews": action_previews,
                "preview_path": "",
                "preview_markdown_path": "",
            }

            if persist_artifacts and waiver.get("artifact_dir"):
                artifact_dir = ROOT / str(waiver.get("artifact_dir", ""))
                preview_json_path = artifact_dir / "preview.json"
                preview_markdown_path = artifact_dir / "preview.md"
                write_text(preview_json_path, json.dumps(waiver_preview, indent=2, ensure_ascii=False) + "\n")
                write_text(preview_markdown_path, render_waiver_preview_markdown(waiver_preview))
                waiver_preview["preview_path"] = repo_relative_path(preview_json_path)
                waiver_preview["preview_markdown_path"] = repo_relative_path(preview_markdown_path)
                write_text(preview_json_path, json.dumps(waiver_preview, indent=2, ensure_ascii=False) + "\n")
                write_text(preview_markdown_path, render_waiver_preview_markdown(waiver_preview))

            waivers.append(waiver_preview)

        return {
            "history_path": execution_payload.get("history_path", ""),
            "waiver_count": execution_payload.get("waiver_count", 0),
            "finding_count": execution_payload.get("finding_count", 0),
            "execution_count": execution_payload.get("execution_count", 0),
            "preview_count": preview_count,
            "draft_preview_count": draft_preview_count,
            "cleanup_preview_count": cleanup_preview_count,
            "review_preview_count": review_preview_count,
            "passes": preview_count == 0,
            "output_dir": repo_relative_path(execution_dir) if persist_artifacts else "",
            "waivers": waivers,
        }
    finally:
        if temp_dir_handle is not None:
            temp_dir_handle.cleanup()


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Preview",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Preview actions: `{payload.get('preview_count', 0)}`",
        f"- Draft previews: `{payload.get('draft_preview_count', 0)}`",
        f"- Review previews: `{payload.get('review_preview_count', 0)}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Waivers",
        "",
    ]

    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No waiver previews required.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` previews=`{len(waiver.get('action_previews', []))}` preview_path=`{waiver.get('preview_path', '')}`"
            )
            for action in waiver.get("action_previews", []):
                lines.append(
                    f"  - `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` changes=`{action.get('change_count', 0)}`"
                )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else None
    payload = build_preview_payload(args.history, args.waiver, output_dir)

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else None
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else None
    if output_dir is not None and summary_json_path is None:
        summary_json_path = output_dir / "preview-summary.json"
    if output_dir is not None and summary_markdown_path is None:
        summary_markdown_path = output_dir / "preview-summary.md"

    if summary_json_path is not None:
        write_text(summary_json_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    if summary_markdown_path is not None:
        write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver preview:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Preview actions: {payload['preview_count']}")
        print(f"- Draft previews: {payload['draft_preview_count']}")
        print(f"- Review previews: {payload['review_preview_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
