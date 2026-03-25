#!/usr/bin/env python3
"""Remove a previously installed starter bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_utils import (
    bundle_reports_dir,
    reconcile_bundle_sources,
    resolve_target_root,
    resolve_bundle_report,
)


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Remove a starter bundle from the local install target.")
    parser.add_argument("bundle", help="Bundle id or title.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Only print the planned bundle removal.")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_root = resolve_target_root(args.target_root)
    report_path, report_payload, available = resolve_bundle_report(target_root, args.bundle)
    if report_path is None or report_payload is None:
        print(f"ERROR: could not find installed bundle matching '{args.bundle}' under {bundle_reports_dir(target_root)}")
        if available:
            print("Available installed bundles:")
            for item in available:
                print(f"- {item}")
        return 1

    bundle_id = str(report_payload.get("bundle_id", report_path.stem))
    missing: list[str] = []

    for result in report_payload.get("results", []):
        if result.get("status") != "installed":
            continue
        skill_id = str(result.get("skill_id", ""))
        if not skill_id:
            continue
        if result.get("action") == "removed":
            missing.append(skill_id)

    reconcile_result = reconcile_bundle_sources(target_root, bundle_id, set(), apply_changes=not args.dry_run)
    removed = reconcile_result["removed_skill_ids"]
    retained = reconcile_result["retained_skill_ids"]

    if args.dry_run:
        print(f"Dry run: would remove bundle {bundle_id}")
        print(f"Would remove skills: {', '.join(removed) if removed else 'none'}")
        print(f"Would retain skills: {', '.join(retained) if retained else 'none'}")
        if missing:
            print(f"Missing from lock: {', '.join(missing)}")
        return 0

    if report_path.exists():
        report_path.unlink()
    reports_dir = report_path.parent
    if reports_dir.is_dir() and not any(reports_dir.iterdir()):
        reports_dir.rmdir()

    print(f"Removed bundle {bundle_id}")
    print(f"Removed skills: {', '.join(removed) if removed else 'none'}")
    print(f"Retained skills: {', '.join(retained) if retained else 'none'}")
    if missing:
        print(f"Missing from lock: {', '.join(missing)}")
    print(f"Updated lock file: {reconcile_result['lock_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
