#!/usr/bin/env python3
"""List installed starter bundles recorded under a target root."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from market_utils import (
    iter_bundle_report_paths,
    load_bundle_report,
    load_lock_payload,
    normalize_install_sources,
    resolve_target_root,
)


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List installed starter bundles from bundle reports.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_root = resolve_target_root(args.target_root)
    report_paths = iter_bundle_report_paths(target_root)
    lock_path, lock_payload = load_lock_payload(target_root)
    installed_by_id = {
        str(entry.get("skill_id", "")): entry
        for entry in lock_payload.get("installed", [])
        if isinstance(entry, dict) and entry.get("skill_id")
    }

    payload = {
        "target_root": str(target_root),
        "lock_path": str(lock_path),
        "bundle_count": 0,
        "bundles": [],
    }

    for report_path in report_paths:
        report = load_bundle_report(report_path)
        bundle_id = str(report.get("bundle_id", report_path.stem))
        status_counts = Counter(result.get("status", "unknown") for result in report.get("results", []))
        managed_skill_ids: list[str] = []
        shared_skill_ids: list[str] = []
        for result in report.get("results", []):
            if result.get("status") != "installed":
                continue
            skill_id = str(result.get("skill_id", ""))
            entry = installed_by_id.get(skill_id)
            if not entry:
                continue
            sources = normalize_install_sources(entry)
            if any(item["kind"] == "bundle" and item["id"] == bundle_id for item in sources):
                managed_skill_ids.append(skill_id)
                if len(sources) > 1:
                    shared_skill_ids.append(skill_id)
        payload["bundles"].append(
            {
                "bundle_id": bundle_id,
                "title": report.get("title", bundle_id),
                "report_path": str(report_path),
                "generated_at": report.get("generated_at", ""),
                "org_policy": report.get("org_policy"),
                "status_counts": dict(sorted(status_counts.items())),
                "managed_skill_ids": managed_skill_ids,
                "shared_skill_ids": shared_skill_ids,
            }
        )

    payload["bundle_count"] = len(payload["bundles"])

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not payload["bundles"]:
        print(f"No installed bundle reports found under {target_root}")
        return 0

    print(f"Installed bundles under {target_root}:")
    for bundle in payload["bundles"]:
        counts = ", ".join(f"{key}={value}" for key, value in bundle["status_counts"].items())
        print(f"- {bundle['bundle_id']}")
        print(f"  title: {bundle['title']}")
        print(f"  report: {bundle['report_path']}")
        print(f"  results: {counts or 'none'}")
        print(f"  active managed skills: {len(bundle['managed_skill_ids'])}")
        if bundle["shared_skill_ids"]:
            print(f"  shared skills: {', '.join(bundle['shared_skill_ids'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
