#!/usr/bin/env python3
"""Install a packaged skill from a local install spec."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from market_utils import (
    ROOT,
    load_json,
    load_lock_payload,
    merge_install_source,
    resolve_target_root,
    sha256_for_file,
    validate_install_spec_payload,
    validate_provenance_payload,
    verify_provenance_against_install_spec,
    write_lock_payload,
)


DEFAULT_TARGET = ROOT / "dist" / "installed-skills"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install a skill from a local install spec.")
    parser.add_argument("install_spec", type=Path, help="Path to the install spec JSON file.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Only print planned actions without extracting files.")
    parser.add_argument("--source-kind", default="direct", help="Logical source kind for this installation record.")
    parser.add_argument("--source-id", default="direct-install", help="Logical source id for this installation record.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_kind = str(args.source_kind).strip().lower() or "direct"
    source_id = str(args.source_id).strip() or "direct-install"

    install_spec_path = args.install_spec if args.install_spec.is_absolute() else (ROOT / args.install_spec)
    if not install_spec_path.is_file():
        print(f"ERROR: missing install spec {install_spec_path}")
        return 1

    install_spec = load_json(install_spec_path)
    remote_source = install_spec.get("remote_source")
    if not isinstance(remote_source, dict):
        remote_source = {}
    try:
        spec_label = install_spec_path.relative_to(ROOT).as_posix()
    except ValueError:
        spec_label = install_spec_path.as_posix()
    spec_errors = validate_install_spec_payload(install_spec, spec_label)
    if spec_errors:
        for error in spec_errors:
            print(f"ERROR: {error}")
        return 1

    package_path = ROOT / str(install_spec["package_path"])
    if not package_path.is_file():
        print(f"ERROR: missing package artifact {package_path}")
        return 1

    provenance_path = ROOT / str(install_spec["provenance_path"])
    if not provenance_path.is_file():
        print(f"ERROR: missing provenance artifact {provenance_path}")
        return 1

    checksum = sha256_for_file(package_path)
    if checksum != install_spec["checksum_sha256"]:
        print(
            "ERROR: checksum mismatch for "
            f"{package_path} (expected {install_spec['checksum_sha256']}, got {checksum})"
        )
        return 1
    provenance_checksum = sha256_for_file(provenance_path)
    if provenance_checksum != install_spec["provenance_sha256"]:
        print(
            "ERROR: provenance checksum mismatch for "
            f"{provenance_path} (expected {install_spec['provenance_sha256']}, got {provenance_checksum})"
        )
        return 1

    provenance_payload = load_json(provenance_path)
    try:
        provenance_label = provenance_path.relative_to(ROOT).as_posix()
    except ValueError:
        provenance_label = provenance_path.as_posix()
    provenance_errors = validate_provenance_payload(
        provenance_payload,
        provenance_label,
        require_local_paths=not bool(remote_source),
    )
    provenance_errors.extend(
        verify_provenance_against_install_spec(
            provenance_payload,
            install_spec,
            provenance_label,
            expected_package_path=str(remote_source.get("upstream_package_path", "")) or None,
        )
    )
    if provenance_errors:
        for error in provenance_errors:
            print(f"ERROR: {error}")
        return 1

    lifecycle_status = install_spec["lifecycle_status"]
    if lifecycle_status in {"blocked", "archived"}:
        print(
            "ERROR: install is denied because this skill is "
            f"marked as '{lifecycle_status}' in the market lifecycle metadata"
        )
        return 1
    if lifecycle_status == "deprecated":
        replacement = provenance_payload.get("lifecycle", {}).get("replacement_skill_id", "")
        replacement_line = f" Consider {replacement} instead." if replacement else ""
        print(
            "WARNING: installing a deprecated skill. "
            f"This skill remains available for compatibility.{replacement_line}"
        )

    target_root = resolve_target_root(args.target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    skill_target = target_root / str(install_spec["install_target"])

    if args.dry_run:
        print(f"Dry run: would install {install_spec['skill_id']} {install_spec['version']}")
        print(f"Package: {package_path}")
        print(f"Provenance: {provenance_path}")
        print(f"Target: {skill_target}")
        print(f"Checksum verified: {checksum}")
        print(f"Source: {source_kind}:{source_id}")
        return 0

    if skill_target.exists():
        shutil.rmtree(skill_target)

    with zipfile.ZipFile(package_path, "r") as archive:
        archive.extractall(target_root)

    installed_entrypoint = target_root / str(install_spec["entrypoint"])
    if not installed_entrypoint.is_file():
        print(f"ERROR: installed entrypoint missing after extraction: {installed_entrypoint}")
        return 1

    lock_path, lock_payload = load_lock_payload(target_root)

    existing_entry = next(
        (entry for entry in lock_payload.get("installed", []) if entry.get("skill_id") == install_spec["skill_id"]),
        None,
    )
    installed = [entry for entry in lock_payload.get("installed", []) if entry.get("skill_id") != install_spec["skill_id"]]
    installed.append(
        {
            "skill_id": install_spec["skill_id"],
            "skill_name": install_spec["skill_name"],
            "publisher": install_spec["publisher"],
            "version": install_spec["version"],
            "channel": install_spec["channel"],
            "install_target": install_spec["install_target"],
            "review_status": install_spec["review_status"],
            "lifecycle_status": install_spec["lifecycle_status"],
            "install_spec": str(install_spec_path),
            "provenance_path": str(provenance_path),
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "sources": merge_install_source(existing_entry, source_kind, source_id),
        }
    )
    lock_payload["installed"] = installed
    write_lock_payload(lock_path, lock_payload)

    print(f"Installed {install_spec['skill_id']} to {skill_target}")
    print(f"Installed entrypoint: {installed_entrypoint}")
    print(f"Updated lock file: {lock_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
