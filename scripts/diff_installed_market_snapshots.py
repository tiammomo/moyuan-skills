#!/usr/bin/env python3
"""Compare two installed-state snapshots for change review."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from market_utils import ROOT, load_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two installed-state snapshots and report skill/bundle changes."
    )
    parser.add_argument("before", type=Path, help="Path to the baseline snapshot JSON file.")
    parser.add_argument("after", type=Path, help="Path to the newer snapshot JSON file.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON diff output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown diff output path.")
    parser.add_argument("--json", action="store_true", help="Print the diff payload as JSON.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def source_tokens(sources: list[dict] | None) -> list[str]:
    if not isinstance(sources, list):
        return []
    tokens = []
    for item in sources:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "")).strip()
        source_id = str(item.get("id", "")).strip()
        if not kind or not source_id:
            continue
        tokens.append(f"{kind}:{source_id}")
    return sorted(set(tokens))


def diff_counter_map(before: dict | None, after: dict | None) -> dict:
    before_map = before if isinstance(before, dict) else {}
    after_map = after if isinstance(after, dict) else {}
    payload: dict[str, dict] = {}
    for key in sorted(set(before_map) | set(after_map)):
        before_value = int(before_map.get(key, 0))
        after_value = int(after_map.get(key, 0))
        if before_value == after_value:
            continue
        payload[key] = {
            "before": before_value,
            "after": after_value,
            "delta": after_value - before_value,
        }
    return payload


def compare_skill_entries(before: dict, after: dict) -> list[dict]:
    changes: list[dict] = []
    tracked_fields = ["version", "channel", "lifecycle_status", "install_target"]
    for field in tracked_fields:
        before_value = str(before.get(field, ""))
        after_value = str(after.get(field, ""))
        if before_value != after_value:
            changes.append({"field": field, "before": before_value, "after": after_value})

    before_sources = source_tokens(before.get("sources"))
    after_sources = source_tokens(after.get("sources"))
    if before_sources != after_sources:
        changes.append({"field": "sources", "before": before_sources, "after": after_sources})
    return changes


def compare_bundle_entries(before: dict, after: dict) -> list[dict]:
    changes: list[dict] = []
    tracked_fields = ["title", "org_policy"]
    for field in tracked_fields:
        before_value = before.get(field)
        after_value = after.get(field)
        if before_value != after_value:
            changes.append({"field": field, "before": before_value, "after": after_value})

    list_fields = ["managed_skill_ids", "shared_skill_ids"]
    for field in list_fields:
        before_value = sorted(str(item) for item in before.get(field, []) if str(item).strip())
        after_value = sorted(str(item) for item in after.get(field, []) if str(item).strip())
        if before_value != after_value:
            changes.append({"field": field, "before": before_value, "after": after_value})

    before_status_counts = before.get("status_counts", {})
    after_status_counts = after.get("status_counts", {})
    if before_status_counts != after_status_counts:
        changes.append({"field": "status_counts", "before": before_status_counts, "after": after_status_counts})
    return changes


def build_diff_payload_from_snapshots(
    before: dict,
    after: dict,
    *,
    before_snapshot: dict | None = None,
    after_snapshot: dict | None = None,
) -> dict:
    before_skills = {
        str(item.get("skill_id", "")): item
        for item in before.get("installed", [])
        if isinstance(item, dict) and str(item.get("skill_id", "")).strip()
    }
    after_skills = {
        str(item.get("skill_id", "")): item
        for item in after.get("installed", [])
        if isinstance(item, dict) and str(item.get("skill_id", "")).strip()
    }

    added_skills = sorted(
        [after_skills[skill_id] for skill_id in set(after_skills) - set(before_skills)],
        key=lambda item: str(item.get("skill_id", "")),
    )
    removed_skills = sorted(
        [before_skills[skill_id] for skill_id in set(before_skills) - set(after_skills)],
        key=lambda item: str(item.get("skill_id", "")),
    )
    changed_skills: list[dict] = []
    for skill_id in sorted(set(before_skills) & set(after_skills)):
        changes = compare_skill_entries(before_skills[skill_id], after_skills[skill_id])
        if changes:
            changed_skills.append({"skill_id": skill_id, "changes": changes})

    before_bundles = {
        str(item.get("bundle_id", "")): item
        for item in before.get("bundles", [])
        if isinstance(item, dict) and str(item.get("bundle_id", "")).strip()
    }
    after_bundles = {
        str(item.get("bundle_id", "")): item
        for item in after.get("bundles", [])
        if isinstance(item, dict) and str(item.get("bundle_id", "")).strip()
    }

    added_bundles = sorted(
        [after_bundles[bundle_id] for bundle_id in set(after_bundles) - set(before_bundles)],
        key=lambda item: str(item.get("bundle_id", "")),
    )
    removed_bundles = sorted(
        [before_bundles[bundle_id] for bundle_id in set(before_bundles) - set(after_bundles)],
        key=lambda item: str(item.get("bundle_id", "")),
    )
    changed_bundles: list[dict] = []
    for bundle_id in sorted(set(before_bundles) & set(after_bundles)):
        changes = compare_bundle_entries(before_bundles[bundle_id], after_bundles[bundle_id])
        if changes:
            changed_bundles.append({"bundle_id": bundle_id, "changes": changes})

    summary_delta = diff_counter_map(before.get("summary"), after.get("summary"))
    count_deltas = {
        "channels": diff_counter_map(before.get("counts", {}).get("channels"), after.get("counts", {}).get("channels")),
        "lifecycle_statuses": diff_counter_map(
            before.get("counts", {}).get("lifecycle_statuses"),
            after.get("counts", {}).get("lifecycle_statuses"),
        ),
        "source_kinds": diff_counter_map(
            before.get("counts", {}).get("source_kinds"),
            after.get("counts", {}).get("source_kinds"),
        ),
        "finding_severities": diff_counter_map(
            before.get("counts", {}).get("finding_severities"),
            after.get("counts", {}).get("finding_severities"),
        ),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "before_snapshot": before_snapshot or {
            "path": "",
            "generated_at": before.get("generated_at", ""),
            "target_root": before.get("target_root", ""),
        },
        "after_snapshot": after_snapshot or {
            "path": "",
            "generated_at": after.get("generated_at", ""),
            "target_root": after.get("target_root", ""),
        },
        "summary_delta": summary_delta,
        "count_deltas": count_deltas,
        "skills": {
            "added": added_skills,
            "removed": removed_skills,
            "changed": changed_skills,
        },
        "bundles": {
            "added": added_bundles,
            "removed": removed_bundles,
            "changed": changed_bundles,
        },
    }


def build_diff_payload(before_path: Path, after_path: Path) -> dict:
    resolved_before = resolve_repo_path(before_path)
    resolved_after = resolve_repo_path(after_path)
    before = load_json(resolved_before)
    after = load_json(resolved_after)
    return build_diff_payload_from_snapshots(
        before,
        after,
        before_snapshot={
            "path": str(resolved_before),
            "generated_at": before.get("generated_at", ""),
            "target_root": before.get("target_root", ""),
        },
        after_snapshot={
            "path": str(resolved_after),
            "generated_at": after.get("generated_at", ""),
            "target_root": after.get("target_root", ""),
        },
    )


def render_markdown(payload: dict) -> str:
    skills = payload["skills"]
    bundles = payload["bundles"]
    lines = [
        "# Installed Market Snapshot Diff",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Before snapshot: `{payload['before_snapshot']['path']}`",
        f"- After snapshot: `{payload['after_snapshot']['path']}`",
        f"- Added skills: `{len(skills['added'])}`",
        f"- Removed skills: `{len(skills['removed'])}`",
        f"- Changed skills: `{len(skills['changed'])}`",
        f"- Added bundles: `{len(bundles['added'])}`",
        f"- Removed bundles: `{len(bundles['removed'])}`",
        f"- Changed bundles: `{len(bundles['changed'])}`",
        "",
        "## Summary Delta",
        "",
    ]

    if payload["summary_delta"]:
        for key, item in payload["summary_delta"].items():
            lines.append(f"- `{key}`: `{item['before']}` -> `{item['after']}` (`delta={item['delta']}`)")
    else:
        lines.append("- No summary deltas.")

    lines.extend(["", "## Skills", ""])
    if skills["added"]:
        lines.append("### Added")
        for item in skills["added"]:
            lines.append(f"- `{item['skill_id']}` [{item.get('channel', '?')}]")
        lines.append("")
    if skills["removed"]:
        lines.append("### Removed")
        for item in skills["removed"]:
            lines.append(f"- `{item['skill_id']}` [{item.get('channel', '?')}]")
        lines.append("")
    if skills["changed"]:
        lines.append("### Changed")
        for item in skills["changed"]:
            lines.append(f"- `{item['skill_id']}`")
            for change in item["changes"]:
                lines.append(f"  - `{change['field']}`: `{json.dumps(change['before'], ensure_ascii=False)}` -> `{json.dumps(change['after'], ensure_ascii=False)}`")
        lines.append("")
    if not (skills["added"] or skills["removed"] or skills["changed"]):
        lines.append("- No skill changes.")
        lines.append("")

    lines.extend(["## Bundles", ""])
    if bundles["added"]:
        lines.append("### Added")
        for item in bundles["added"]:
            lines.append(f"- `{item['bundle_id']}`")
        lines.append("")
    if bundles["removed"]:
        lines.append("### Removed")
        for item in bundles["removed"]:
            lines.append(f"- `{item['bundle_id']}`")
        lines.append("")
    if bundles["changed"]:
        lines.append("### Changed")
        for item in bundles["changed"]:
            lines.append(f"- `{item['bundle_id']}`")
            for change in item["changes"]:
                lines.append(f"  - `{change['field']}`: `{json.dumps(change['before'], ensure_ascii=False)}` -> `{json.dumps(change['after'], ensure_ascii=False)}`")
        lines.append("")
    if not (bundles["added"] or bundles["removed"] or bundles["changed"]):
        lines.append("- No bundle changes.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_diff_payload(args.before, args.after)

    output_path: Path | None = None
    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    markdown_path: Path | None = None
    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed market snapshot diff:")
    print(f"- Added skills: {len(payload['skills']['added'])}")
    print(f"- Removed skills: {len(payload['skills']['removed'])}")
    print(f"- Changed skills: {len(payload['skills']['changed'])}")
    print(f"- Added bundles: {len(payload['bundles']['added'])}")
    print(f"- Removed bundles: {len(payload['bundles']['removed'])}")
    print(f"- Changed bundles: {len(payload['bundles']['changed'])}")
    if output_path:
        print(f"- JSON diff: {output_path}")
    if markdown_path:
        print(f"- Markdown diff: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
