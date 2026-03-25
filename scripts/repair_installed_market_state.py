#!/usr/bin/env python3
"""Conservatively repair low-risk local installed market drift."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import check_installed_market_state
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
        description="Conservatively repair low-risk installed-state drift for the local skills market client."
    )
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Only print planned repairs without changing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def analyze_repair_plan(target_root: Path) -> dict:
    resolved_root = resolve_target_root(target_root)
    doctor_payload = check_installed_market_state.analyze_target(resolved_root)
    _, lock_payload = load_lock_payload(resolved_root)

    installed_entries = [
        entry for entry in lock_payload.get("installed", [])
        if isinstance(entry, dict) and str(entry.get("skill_id", "")).strip()
    ]
    expected_dirs = {
        str(entry.get("install_target", "")).strip()
        for entry in installed_entries
        if str(entry.get("install_target", "")).strip()
    }
    actual_dirs = {
        path.name
        for path in resolved_root.iterdir()
        if path.is_dir() and path.name not in check_installed_market_state.IGNORED_ROOT_NAMES
    } if resolved_root.is_dir() else set()
    orphan_dirs = sorted(actual_dirs - expected_dirs)

    owned_bundle_ids = {
        source["id"]
        for entry in installed_entries
        for source in normalize_install_sources(entry)
        if source["kind"] == "bundle"
    }

    stale_bundle_reports: list[dict] = []
    for report_path in iter_bundle_report_paths(resolved_root):
        report = load_bundle_report(report_path)
        bundle_id = str(report.get("bundle_id", report_path.stem))
        if bundle_id in owned_bundle_ids:
            continue
        stale_bundle_reports.append(
            {
                "bundle_id": bundle_id,
                "path": str(report_path),
                "title": str(report.get("title", "")).strip(),
            }
        )

    repairable_paths = {str(resolved_root / name) for name in orphan_dirs}
    repairable_bundle_ids = {item["bundle_id"] for item in stale_bundle_reports}
    skipped_findings: list[dict] = []
    repairable_findings: list[dict] = []
    for finding in doctor_payload.get("findings", []):
        kind = str(finding.get("kind", ""))
        message = str(finding.get("message", ""))
        bundle_id = str(finding.get("bundle_id", ""))
        if kind == "filesystem" and any(path in message for path in repairable_paths):
            repairable_findings.append(finding)
            continue
        if kind == "bundle-report" and bundle_id in repairable_bundle_ids:
            repairable_findings.append(finding)
            continue
        skipped_findings.append(finding)

    return {
        "target_root": str(resolved_root),
        "dry_run": False,
        "doctor_finding_count": int(doctor_payload.get("finding_count", 0)),
        "repairable_finding_count": len(repairable_findings),
        "repairable_findings": repairable_findings,
        "orphan_directories": [str(resolved_root / name) for name in orphan_dirs],
        "stale_bundle_reports": stale_bundle_reports,
        "skipped_finding_count": len(skipped_findings),
        "skipped_findings": skipped_findings,
    }


def apply_repairs(plan: dict, *, dry_run: bool) -> dict:
    applied = {
        "removed_orphan_directories": [],
        "removed_bundle_reports": [],
    }

    if not dry_run:
        for directory in plan["orphan_directories"]:
            path = Path(directory)
            if path.exists():
                shutil.rmtree(path)
            applied["removed_orphan_directories"].append(directory)

        for report in plan["stale_bundle_reports"]:
            report_path = Path(report["path"])
            if report_path.exists():
                report_path.unlink()
            applied["removed_bundle_reports"].append(report["path"])

        bundle_reports_dir = Path(plan["target_root"]) / "bundle-reports"
        if bundle_reports_dir.is_dir() and not any(bundle_reports_dir.iterdir()):
            bundle_reports_dir.rmdir()
    else:
        applied["removed_orphan_directories"] = list(plan["orphan_directories"])
        applied["removed_bundle_reports"] = [report["path"] for report in plan["stale_bundle_reports"]]

    plan = dict(plan)
    plan["dry_run"] = dry_run
    plan["applied"] = applied
    plan["applied_count"] = len(applied["removed_orphan_directories"]) + len(applied["removed_bundle_reports"])
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    plan = analyze_repair_plan(args.target_root)
    payload = apply_repairs(plan, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    action_word = "Would remove" if args.dry_run else "Removed"
    print(f"Installed-state repair plan for {payload['target_root']}:")

    orphan_dirs = payload["applied"]["removed_orphan_directories"]
    if orphan_dirs:
        print(f"- {action_word} orphan directories:")
        for directory in orphan_dirs:
            print(f"  - {directory}")
    else:
        print("- No orphan directories to repair.")

    stale_reports = payload["applied"]["removed_bundle_reports"]
    if stale_reports:
        print(f"- {action_word} stale bundle reports:")
        for report in stale_reports:
            print(f"  - {report}")
    else:
        print("- No stale bundle reports to repair.")

    if payload["skipped_findings"]:
        print(f"- Skipped higher-risk findings: {payload['skipped_finding_count']}")
        for finding in payload["skipped_findings"]:
            scope_parts = []
            if finding.get("skill_id"):
                scope_parts.append(str(finding["skill_id"]))
            if finding.get("bundle_id"):
                scope_parts.append(str(finding["bundle_id"]))
            scope = f" ({', '.join(scope_parts)})" if scope_parts else ""
            print(f"  - [{finding['severity']}] {finding['kind']}{scope}: {finding['message']}")
    else:
        print("- No higher-risk findings were left for manual repair.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
