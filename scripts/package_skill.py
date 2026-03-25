#!/usr/bin/env python3
"""Package a skill into a local zip artifact and generate an install spec."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from market_utils import (
    ROOT,
    build_provenance_payload,
    dump_json,
    iter_manifest_paths,
    repo_relative_path,
    sha256_for_bytes,
    sha256_for_file,
    validate_market_manifest,
)


DEFAULT_OUTPUT = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package a skill and emit a local install spec.")
    parser.add_argument("skill", nargs="?", help="Skill directory name, for example release-note-writer.")
    parser.add_argument("--all", action="store_true", help="Package every skill that has a market manifest.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory for package and install artifacts.")
    return parser


def package_one_skill(skill_name: str, output_dir: Path) -> int:
    skill_dir = ROOT / "skills" / skill_name
    manifest_path = skill_dir / "market" / "skill.json"
    if not skill_dir.is_dir():
        print(f"ERROR: missing skill directory {skill_dir}")
        return 1
    if not manifest_path.is_file():
        print(f"ERROR: missing market manifest {manifest_path}")
        return 1

    manifest, errors = validate_market_manifest(manifest_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    packages_dir = output_dir / "packages"
    installs_dir = output_dir / "install"
    provenance_dir = output_dir / "provenance"
    package_path = packages_dir / f"{manifest['name']}-{manifest['version']}.zip"
    package_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(skill_dir.rglob("*")):
            if file_path.is_file() and "__pycache__" not in file_path.parts:
                archive.write(file_path, arcname=file_path.relative_to(skill_dir.parent))

    checksum = sha256_for_file(package_path)
    provenance_payload = build_provenance_payload(manifest, package_path, checksum)
    provenance_path = provenance_dir / f"{manifest['name']}-{manifest['version']}.json"
    dump_json(provenance_path, provenance_payload)
    provenance_checksum = sha256_for_bytes(provenance_path.read_bytes())
    install_spec = {
        "skill_id": manifest["id"],
        "skill_name": manifest["name"],
        "publisher": manifest["publisher"],
        "version": manifest["version"],
        "channel": manifest["channel"],
        "package_type": "zip",
        "package_path": repo_relative_path(package_path),
        "checksum_sha256": checksum,
        "entrypoint": f"{manifest['name']}/SKILL.md",
        "install_target": manifest["name"],
        "review_status": manifest["quality"]["review_status"],
        "lifecycle_status": manifest["lifecycle"]["status"],
        "provenance_path": repo_relative_path(provenance_path),
        "provenance_sha256": provenance_checksum,
    }
    install_path = installs_dir / f"{manifest['name']}-{manifest['version']}.json"
    dump_json(install_path, install_spec)

    print(f"Packaged skill to {package_path}")
    print(f"Provenance: {provenance_path}")
    print(f"Install spec: {install_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.all and args.skill:
        print("ERROR: choose either a specific skill or --all")
        return 1
    if not args.all and not args.skill:
        print("ERROR: provide a skill name or use --all")
        return 1

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()

    if args.all:
        skill_names = [path.parents[1].name for path in iter_manifest_paths()]
        if not skill_names:
            print("ERROR: no market manifests found")
            return 1
        exit_code = 0
        for skill_name in skill_names:
            exit_code = max(exit_code, package_one_skill(skill_name, output_dir))
        return exit_code

    return package_one_skill(args.skill, output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
