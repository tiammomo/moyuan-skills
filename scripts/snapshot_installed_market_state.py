#!/usr/bin/env python3
"""Export a reusable installed-state snapshot for the local skills market client."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import check_installed_market_state
import repair_installed_market_state
from market_utils import (
    iter_bundle_report_paths,
    load_bundle_report,
    load_lock_payload,
    normalize_install_sources,
    resolve_target_root,
)


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export an installed-state snapshot for archive, review, or later diffing."
    )
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON snapshot output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown summary output path.")
    parser.add_argument("--json", action="store_true", help="Print the snapshot payload as JSON.")
    return parser


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_snapshot_payload(target_root: Path) -> dict:
    resolved_root = resolve_target_root(target_root)
    lock_path, lock_payload = load_lock_payload(resolved_root)
    doctor_payload = check_installed_market_state.analyze_target(resolved_root)
    repair_preview = repair_installed_market_state.analyze_repair_plan(resolved_root)

    installed_entries = sorted(
        [
            entry for entry in lock_payload.get("installed", [])
            if isinstance(entry, dict) and str(entry.get("skill_id", "")).strip()
        ],
        key=lambda item: str(item.get("skill_id", "")),
    )
    installed: list[dict] = []
    channel_counts: Counter[str] = Counter()
    lifecycle_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    installed_by_id: dict[str, dict] = {}

    for entry in installed_entries:
        skill_id = str(entry.get("skill_id", ""))
        sources = normalize_install_sources(entry)
        installed_item = {
            "skill_id": skill_id,
            "version": str(entry.get("version", "")),
            "channel": str(entry.get("channel", "")),
            "lifecycle_status": str(entry.get("lifecycle_status", "")),
            "install_target": str(entry.get("install_target", "")),
            "installed_at": str(entry.get("installed_at", "")),
            "install_spec": str(entry.get("install_spec", "")),
            "provenance_path": str(entry.get("provenance_path", "")),
            "sources": sources,
        }
        installed.append(installed_item)
        installed_by_id[skill_id] = installed_item
        channel_counts[installed_item["channel"] or "unknown"] += 1
        lifecycle_counts[installed_item["lifecycle_status"] or "unknown"] += 1
        for source in sources:
            source_counts[source["kind"]] += 1

    bundles: list[dict] = []
    for report_path in iter_bundle_report_paths(resolved_root):
        report = load_bundle_report(report_path)
        bundle_id = str(report.get("bundle_id", report_path.stem))
        status_counts = Counter(
            str(result.get("status", "unknown"))
            for result in report.get("results", [])
            if isinstance(result, dict)
        )
        managed_skill_ids: list[str] = []
        shared_skill_ids: list[str] = []
        for result in report.get("results", []):
            if not isinstance(result, dict) or result.get("status") != "installed":
                continue
            skill_id = str(result.get("skill_id", "")).strip()
            if not skill_id:
                continue
            entry = installed_by_id.get(skill_id)
            if not entry:
                continue
            sources = entry.get("sources", [])
            if any(item["kind"] == "bundle" and item["id"] == bundle_id for item in sources):
                managed_skill_ids.append(skill_id)
                if len(sources) > 1:
                    shared_skill_ids.append(skill_id)
        bundles.append(
            {
                "bundle_id": bundle_id,
                "title": str(report.get("title", bundle_id)),
                "report_path": str(report_path),
                "generated_at": str(report.get("generated_at", "")),
                "org_policy": report.get("org_policy"),
                "status_counts": dict(sorted(status_counts.items())),
                "managed_skill_ids": managed_skill_ids,
                "shared_skill_ids": shared_skill_ids,
            }
        )
    bundles.sort(key=lambda item: item["bundle_id"])

    finding_severity_counts = Counter(
        str(finding.get("severity", "unknown"))
        for finding in doctor_payload.get("findings", [])
        if isinstance(finding, dict)
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_root": str(resolved_root),
        "lock_path": str(lock_path),
        "summary": {
            "installed_count": len(installed),
            "bundle_count": len(bundles),
            "doctor_finding_count": int(doctor_payload.get("finding_count", 0)),
            "repairable_finding_count": int(repair_preview.get("repairable_finding_count", 0)),
            "skipped_finding_count": int(repair_preview.get("skipped_finding_count", 0)),
        },
        "counts": {
            "channels": dict(sorted(channel_counts.items())),
            "lifecycle_statuses": dict(sorted(lifecycle_counts.items())),
            "source_kinds": dict(sorted(source_counts.items())),
            "finding_severities": dict(sorted(finding_severity_counts.items())),
        },
        "installed": installed,
        "bundles": bundles,
        "doctor": doctor_payload,
        "repair_preview": {
            "repairable_finding_count": int(repair_preview.get("repairable_finding_count", 0)),
            "orphan_directories": repair_preview.get("orphan_directories", []),
            "stale_bundle_reports": repair_preview.get("stale_bundle_reports", []),
            "skipped_finding_count": int(repair_preview.get("skipped_finding_count", 0)),
            "skipped_findings": repair_preview.get("skipped_findings", []),
        },
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    counts = payload["counts"]
    lines = [
        "# Installed Market Snapshot",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Target root: `{payload['target_root']}`",
        f"- Lock path: `{payload['lock_path']}`",
        f"- Installed skills: `{summary['installed_count']}`",
        f"- Installed bundles: `{summary['bundle_count']}`",
        f"- Doctor findings: `{summary['doctor_finding_count']}`",
        f"- Repairable findings: `{summary['repairable_finding_count']}`",
        "",
        "## Installed Skills",
        "",
    ]

    if payload["installed"]:
        for item in payload["installed"]:
            source_summary = ", ".join(f"{source['kind']}:{source['id']}" for source in item.get("sources", [])) or "none"
            lines.extend(
                [
                    f"- `{item['skill_id']}` [{item['channel'] or '?'}]",
                    f"  version: `{item['version'] or '?'}`",
                    f"  lifecycle: `{item['lifecycle_status'] or '?'}`",
                    f"  target: `{item['install_target'] or '?'}`",
                    f"  sources: `{source_summary}`",
                ]
            )
    else:
        lines.append("- No installed skills recorded.")

    lines.extend(
        [
            "",
            "## Installed Bundles",
            "",
        ]
    )

    if payload["bundles"]:
        for bundle in payload["bundles"]:
            count_summary = ", ".join(f"{key}={value}" for key, value in bundle["status_counts"].items()) or "none"
            lines.extend(
                [
                    f"- `{bundle['bundle_id']}`",
                    f"  title: `{bundle['title']}`",
                    f"  results: `{count_summary}`",
                    f"  managed skills: `{len(bundle['managed_skill_ids'])}`",
                ]
            )
    else:
        lines.append("- No installed bundle reports recorded.")

    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Channels: `{json.dumps(counts['channels'], ensure_ascii=False)}`",
            f"- Lifecycle statuses: `{json.dumps(counts['lifecycle_statuses'], ensure_ascii=False)}`",
            f"- Source kinds: `{json.dumps(counts['source_kinds'], ensure_ascii=False)}`",
            f"- Finding severities: `{json.dumps(counts['finding_severities'], ensure_ascii=False)}`",
            "",
            "## Repair Preview",
            "",
        ]
    )

    repair_preview = payload["repair_preview"]
    if repair_preview["repairable_finding_count"] == 0:
        lines.append("- No low-risk repairs are currently suggested.")
    else:
        if repair_preview["orphan_directories"]:
            lines.append(f"- Orphan directories: `{json.dumps(repair_preview['orphan_directories'], ensure_ascii=False)}`")
        if repair_preview["stale_bundle_reports"]:
            stale_report_paths = [item["path"] for item in repair_preview["stale_bundle_reports"]]
            lines.append(f"- Stale bundle reports: `{json.dumps(stale_report_paths, ensure_ascii=False)}`")
    if repair_preview["skipped_finding_count"]:
        lines.append(f"- Higher-risk findings left for manual review: `{repair_preview['skipped_finding_count']}`")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_snapshot_payload(args.target_root)

    if args.output_path:
        output_path = args.output_path if args.output_path.is_absolute() else (resolve_target_root(Path(".")) / args.output_path)
        _write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    markdown_content = render_markdown(payload)
    if args.markdown_path:
        markdown_path = args.markdown_path if args.markdown_path.is_absolute() else (resolve_target_root(Path(".")) / args.markdown_path)
        _write_text(markdown_path, markdown_content)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Installed market snapshot for {payload['target_root']}:")
    print(f"- Installed skills: {payload['summary']['installed_count']}")
    print(f"- Installed bundles: {payload['summary']['bundle_count']}")
    print(f"- Doctor findings: {payload['summary']['doctor_finding_count']}")
    print(f"- Repairable findings: {payload['summary']['repairable_finding_count']}")
    if args.output_path:
        print(f"- JSON snapshot: {output_path}")
    if args.markdown_path:
        print(f"- Markdown summary: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
