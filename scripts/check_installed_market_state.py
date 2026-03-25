#!/usr/bin/env python3
"""Check local installed market state for lock/report/filesystem consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_utils import (
    load_bundle_report,
    load_json,
    load_lock_payload,
    normalize_install_sources,
    resolve_target_root,
    validate_install_spec_payload,
    validate_provenance_payload,
    verify_provenance_against_install_spec,
)


DEFAULT_TARGET = Path("dist/installed-skills")
IGNORED_ROOT_NAMES = {"skills.lock.json", "bundle-reports"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check a local installed skills target for consistency issues.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when findings are present.")
    return parser


def analyze_target(target_root: Path) -> dict:
    resolved_root = resolve_target_root(target_root)
    lock_path, lock_payload = load_lock_payload(resolved_root)
    findings: list[dict] = []
    infos: list[str] = []

    installed_entries = [
        entry for entry in lock_payload.get("installed", [])
        if isinstance(entry, dict) and str(entry.get("skill_id", "")).strip()
    ]
    installed_by_id = {str(entry["skill_id"]): entry for entry in installed_entries}
    infos.append(f"Installed entries: {len(installed_entries)}")

    bundle_reports_dir = resolved_root / "bundle-reports"
    report_paths = sorted(bundle_reports_dir.glob("*.json")) if bundle_reports_dir.is_dir() else []
    infos.append(f"Bundle reports: {len(report_paths)}")

    for entry in installed_entries:
        skill_id = str(entry.get("skill_id", ""))
        install_target = str(entry.get("install_target", "")).strip()
        install_dir = resolved_root / install_target if install_target else resolved_root / "__missing_target__"
        if not install_target:
            findings.append({"kind": "lock-entry", "severity": "error", "skill_id": skill_id, "message": "missing install_target"})
        elif not install_dir.is_dir():
            findings.append(
                {
                    "kind": "filesystem",
                    "severity": "error",
                    "skill_id": skill_id,
                    "message": f"install_target directory is missing: {install_dir}",
                }
            )

        install_spec_path_raw = str(entry.get("install_spec", "")).strip()
        provenance_path_raw = str(entry.get("provenance_path", "")).strip()
        if not install_spec_path_raw:
            findings.append({"kind": "lock-entry", "severity": "error", "skill_id": skill_id, "message": "missing install_spec path"})
            continue
        install_spec_path = Path(install_spec_path_raw)
        if not install_spec_path.is_file():
            findings.append(
                {
                    "kind": "install-spec",
                    "severity": "error",
                    "skill_id": skill_id,
                    "message": f"install_spec path is missing: {install_spec_path}",
                }
            )
            continue

        install_spec = load_json(install_spec_path)
        install_spec_errors = validate_install_spec_payload(install_spec, install_spec_path.as_posix())
        for error in install_spec_errors:
            findings.append({"kind": "install-spec", "severity": "error", "skill_id": skill_id, "message": error})

        if install_spec.get("skill_id") != skill_id:
            findings.append(
                {
                    "kind": "install-spec",
                    "severity": "error",
                    "skill_id": skill_id,
                    "message": "lock entry skill_id does not match install spec",
                }
            )

        entrypoint = str(install_spec.get("entrypoint", "")).strip()
        if entrypoint:
            installed_entrypoint = resolved_root / entrypoint
            if not installed_entrypoint.is_file():
                findings.append(
                    {
                        "kind": "filesystem",
                        "severity": "error",
                        "skill_id": skill_id,
                        "message": f"installed entrypoint is missing: {installed_entrypoint}",
                    }
                )

        if not provenance_path_raw:
            findings.append({"kind": "provenance", "severity": "error", "skill_id": skill_id, "message": "missing provenance_path"})
        else:
            provenance_path = Path(provenance_path_raw)
            if not provenance_path.is_file():
                findings.append(
                    {
                        "kind": "provenance",
                        "severity": "error",
                        "skill_id": skill_id,
                        "message": f"provenance path is missing: {provenance_path}",
                    }
                )
            else:
                provenance_payload = load_json(provenance_path)
                provenance_errors = validate_provenance_payload(provenance_payload, provenance_path.as_posix())
                provenance_errors.extend(
                    verify_provenance_against_install_spec(provenance_payload, install_spec, provenance_path.as_posix())
                )
                for error in provenance_errors:
                    findings.append({"kind": "provenance", "severity": "error", "skill_id": skill_id, "message": error})

        sources = normalize_install_sources(entry)
        if not sources:
            findings.append({"kind": "ownership", "severity": "warning", "skill_id": skill_id, "message": "entry has no normalized ownership sources"})
        for source in sources:
            if source["kind"] == "bundle":
                expected_report = bundle_reports_dir / f"{source['id']}.json"
                if not expected_report.is_file():
                    findings.append(
                        {
                            "kind": "ownership",
                            "severity": "error",
                            "skill_id": skill_id,
                            "message": f"bundle ownership points to missing report: {expected_report}",
                        }
                    )

    for report_path in report_paths:
        report = load_bundle_report(report_path)
        bundle_id = str(report.get("bundle_id", report_path.stem))
        results = report.get("results", [])
        if not isinstance(results, list):
            findings.append(
                {
                    "kind": "bundle-report",
                    "severity": "error",
                    "bundle_id": bundle_id,
                    "message": f"bundle report has invalid results payload: {report_path}",
                }
            )
            continue
        managed_count = 0
        for result in results:
            if not isinstance(result, dict) or result.get("status") != "installed":
                continue
            skill_id = str(result.get("skill_id", "")).strip()
            if not skill_id:
                continue
            entry = installed_by_id.get(skill_id)
            if entry is None:
                findings.append(
                    {
                        "kind": "bundle-report",
                        "severity": "warning",
                        "bundle_id": bundle_id,
                        "skill_id": skill_id,
                        "message": "bundle report references an installed skill that is missing from skills.lock.json",
                    }
                )
                continue
            sources = normalize_install_sources(entry)
            if any(item["kind"] == "bundle" and item["id"] == bundle_id for item in sources):
                managed_count += 1
            else:
                findings.append(
                    {
                        "kind": "bundle-report",
                        "severity": "warning",
                        "bundle_id": bundle_id,
                        "skill_id": skill_id,
                        "message": "bundle report references a skill that no longer carries this bundle ownership",
                    }
                )
        if managed_count == 0 and results:
            findings.append(
                {
                    "kind": "bundle-report",
                    "severity": "warning",
                    "bundle_id": bundle_id,
                    "message": "bundle report exists but no installed skills are currently managed by it",
                }
            )

    expected_dirs = {
        str(entry.get("install_target", "")).strip()
        for entry in installed_entries
        if str(entry.get("install_target", "")).strip()
    }
    actual_dirs = {
        path.name
        for path in resolved_root.iterdir()
        if path.is_dir() and path.name not in IGNORED_ROOT_NAMES
    } if resolved_root.is_dir() else set()
    orphan_dirs = sorted(actual_dirs - expected_dirs)
    for directory_name in orphan_dirs:
        findings.append(
            {
                "kind": "filesystem",
                "severity": "warning",
                "message": f"orphan installed directory is not tracked in skills.lock.json: {resolved_root / directory_name}",
            }
        )

    return {
        "target_root": str(resolved_root),
        "lock_path": str(lock_path),
        "installed_count": len(installed_entries),
        "bundle_report_count": len(report_paths),
        "finding_count": len(findings),
        "findings": findings,
        "infos": infos,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = analyze_target(args.target_root)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Installed market state for {payload['target_root']}:")
        for info in payload["infos"]:
            print(f"- {info}")
        if not payload["findings"]:
            print("No install-state findings.")
        else:
            print("Findings:")
            for finding in payload["findings"]:
                scope_parts = []
                if finding.get("skill_id"):
                    scope_parts.append(str(finding["skill_id"]))
                if finding.get("bundle_id"):
                    scope_parts.append(str(finding["bundle_id"]))
                scope = f" ({', '.join(scope_parts)})" if scope_parts else ""
                print(f"- [{finding['severity']}] {finding['kind']}{scope}: {finding['message']}")

    if args.strict and payload["findings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
