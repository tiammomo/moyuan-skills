#!/usr/bin/env python3
"""Validate a repo-compatible skill submission artifact."""

from __future__ import annotations

import argparse
import tarfile
from pathlib import Path

from market_utils import (
    ROOT,
    load_json,
    sha256_for_file,
    validate_install_spec_payload,
    validate_market_manifest,
    validate_provenance_payload,
    validate_skill_submission_payload,
    verify_provenance_against_install_spec,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a skill submission artifact.")
    parser.add_argument("path", type=Path, help="Path to submission.json.")
    return parser


def validate_payload_archive(submission: dict, archive_path: Path, label: str) -> list[str]:
    errors: list[str] = []
    archive_checksum = sha256_for_file(archive_path)
    if archive_checksum != submission["payload_archive_sha256"]:
        errors.append(f"{label}: payload archive checksum does not match submission record")

    expected_members = {
        str(submission["manifest_path"]),
        str(Path(submission["source_dir"]) / "SKILL.md"),
        str(submission["docs_path"]),
    }
    with tarfile.open(archive_path, "r:gz") as archive:
        names: set[str] = set()
        duplicates: set[str] = set()
        for raw_name in archive.getnames():
            name = raw_name.rstrip("/")
            if name in names:
                duplicates.add(name)
            names.add(name)
    for member in sorted(duplicates):
        errors.append(f"{label}: payload archive contains duplicate member '{member}'")
    for member in sorted(expected_members):
        if member not in names:
            errors.append(f"{label}: payload archive is missing expected member '{member}'")
    return errors


def validate_submission_file(submission_path: Path) -> tuple[dict, list[str]]:
    submission_path = submission_path if submission_path.is_absolute() else (ROOT / submission_path)
    if not submission_path.is_file():
        return {}, [f"missing submission file {submission_path}"]

    submission = load_json(submission_path)
    try:
        label = submission_path.relative_to(ROOT).as_posix()
    except ValueError:
        label = submission_path.as_posix()

    errors = validate_skill_submission_payload(submission, label)
    if errors:
        return {}, errors

    manifest_path = ROOT / submission["manifest_path"]
    install_spec_path = ROOT / submission["install_spec_path"]
    provenance_path = ROOT / submission["provenance_path"]
    package_path = ROOT / submission["package_path"]
    payload_archive_path = ROOT / submission["payload_archive_path"]

    manifest, manifest_errors = validate_market_manifest(manifest_path)
    errors.extend(manifest_errors)

    install_spec = load_json(install_spec_path)
    errors.extend(validate_install_spec_payload(install_spec, submission["install_spec_path"]))

    provenance = load_json(provenance_path)
    errors.extend(validate_provenance_payload(provenance, submission["provenance_path"]))
    errors.extend(verify_provenance_against_install_spec(provenance, install_spec, submission["install_spec_path"]))

    if sha256_for_file(package_path) != install_spec["checksum_sha256"]:
        errors.append(f"{label}: package checksum does not match install spec")
    if sha256_for_file(provenance_path) != install_spec["provenance_sha256"]:
        errors.append(f"{label}: provenance checksum does not match install spec")

    errors.extend(validate_payload_archive(submission, payload_archive_path, label))

    if not manifest_errors:
        expected_pairs = (
            ("publisher", manifest["publisher"]),
            ("skill_id", manifest["id"]),
            ("skill_name", manifest["name"]),
            ("version", manifest["version"]),
            ("channel", manifest["channel"]),
            ("checker_command", manifest["quality"]["checker"]),
            ("eval_command", manifest["quality"]["eval"]),
        )
        for key, expected in expected_pairs:
            if submission.get(key) != expected:
                errors.append(f"{label}: '{key}' does not match the current market manifest")

    if submission["skill_id"] != install_spec.get("skill_id"):
        errors.append(f"{label}: skill_id does not match install spec")
    if submission["skill_name"] != install_spec.get("skill_name"):
        errors.append(f"{label}: skill_name does not match install spec")
    if submission["publisher"] != install_spec.get("publisher"):
        errors.append(f"{label}: publisher does not match install spec")
    if submission["version"] != install_spec.get("version"):
        errors.append(f"{label}: version does not match install spec")
    if submission["channel"] != install_spec.get("channel"):
        errors.append(f"{label}: channel does not match install spec")

    return submission, errors


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        submission, errors = validate_submission_file(args.path)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1

        print(f"Validated submission for {submission['skill_id']}")
        return 0
    except (OSError, ValueError, tarfile.TarError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
