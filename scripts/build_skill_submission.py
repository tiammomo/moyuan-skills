#!/usr/bin/env python3
"""Build a repo-compatible skill submission artifact."""

from __future__ import annotations

import argparse
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import package_skill
from market_utils import (
    ROOT,
    dump_json,
    repo_relative_path,
    sha256_for_file,
    validate_market_manifest,
)


DEFAULT_OUTPUT = ROOT / "dist" / "submissions"
DEFAULT_MARKET_DIR = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a repo-compatible skill submission artifact.")
    parser.add_argument("skill", help="Skill directory name or path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory for submission artifacts.")
    parser.add_argument("--market-dir", type=Path, default=DEFAULT_MARKET_DIR, help="Market artifact directory used for package/install/provenance artifacts.")
    parser.add_argument("--release-notes", help="Inline release notes text for the submission.")
    parser.add_argument("--release-notes-file", type=Path, help="Optional file whose contents become the submission release notes.")
    return parser


def resolve_output_dir(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path).resolve()


def load_release_notes(args: argparse.Namespace, manifest: dict) -> str:
    if args.release_notes and args.release_notes_file:
        raise ValueError("choose either --release-notes or --release-notes-file")
    if args.release_notes_file:
        source = args.release_notes_file if args.release_notes_file.is_absolute() else (ROOT / args.release_notes_file)
        if not source.is_file():
            raise ValueError(f"release notes file does not exist: {args.release_notes_file}")
        content = source.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("release notes file is empty")
        return content
    if args.release_notes:
        return args.release_notes.strip()
    return f"Submission built from local market artifacts for {manifest['id']} {manifest['version']}."


def add_archive_member(archive: tarfile.TarFile, file_path: Path, added_members: set[str]) -> None:
    arcname = repo_relative_path(file_path)
    if arcname in added_members:
        return
    archive.add(file_path, arcname=arcname, recursive=False)
    added_members.add(arcname)


def build_payload_archive(skill_dir: Path, docs_path: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    added_members: set[str] = set()
    with tarfile.open(archive_path, "w:gz") as archive:
        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file() or "__pycache__" in file_path.parts:
                continue
            add_archive_member(archive, file_path, added_members)
        add_archive_member(archive, docs_path, added_members)


def build_submission(args: argparse.Namespace) -> int:
    try:
        skill_dir = package_skill.resolve_skill_dir(args.skill)
        market_dir = resolve_output_dir(args.market_dir)
        output_dir = resolve_output_dir(args.output_dir)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    manifest_path = skill_dir / "market" / "skill.json"
    if not manifest_path.is_file():
        print(f"ERROR: missing market manifest {repo_relative_path(manifest_path)}")
        return 1

    manifest, manifest_errors = validate_market_manifest(manifest_path)
    if manifest_errors:
        for error in manifest_errors:
            print(f"ERROR: {error}")
        return 1

    package_exit_code = package_skill.package_one_skill(args.skill, market_dir)
    if package_exit_code != 0:
        return package_exit_code

    install_spec_path = market_dir / "install" / f"{manifest['name']}-{manifest['version']}.json"
    provenance_path = market_dir / "provenance" / f"{manifest['name']}-{manifest['version']}.json"
    package_path = market_dir / "packages" / f"{manifest['name']}-{manifest['version']}.zip"
    docs_path = ROOT / manifest["artifacts"]["docs"]

    expected_artifacts = (
        ("docs", docs_path),
        ("install spec", install_spec_path),
        ("provenance", provenance_path),
        ("package", package_path),
    )
    for label, path in expected_artifacts:
        if not path.is_file():
            raise ValueError(f"missing {label} artifact: {repo_relative_path(path)}")

    submission_dir = output_dir / manifest["publisher"] / manifest["name"] / manifest["version"]
    payload_archive_path = submission_dir / "payload.tgz"

    release_notes = load_release_notes(args, manifest)
    build_payload_archive(skill_dir, docs_path, payload_archive_path)
    payload_archive_sha256 = sha256_for_file(payload_archive_path)

    submission_payload = {
        "submission_format": "moyuan-skill-submission@v1",
        "submission_id": f"{manifest['id']}@{manifest['version']}",
        "publisher": manifest["publisher"],
        "skill_id": manifest["id"],
        "skill_name": manifest["name"],
        "version": manifest["version"],
        "channel": manifest["channel"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": manifest["artifacts"]["source_dir"],
        "docs_path": manifest["artifacts"]["docs"],
        "manifest_path": repo_relative_path(manifest_path),
        "install_spec_path": repo_relative_path(install_spec_path),
        "provenance_path": repo_relative_path(provenance_path),
        "package_path": repo_relative_path(package_path),
        "payload_archive_path": repo_relative_path(payload_archive_path),
        "payload_archive_sha256": payload_archive_sha256,
        "checker_command": manifest["quality"]["checker"],
        "eval_command": manifest["quality"]["eval"],
        "release_notes": release_notes,
    }

    submission_path = submission_dir / "submission.json"
    dump_json(submission_path, submission_payload)

    print(f"Built submission: {submission_path}")
    print(f"Payload archive: {payload_archive_path}")
    print(f"Install spec: {install_spec_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return build_submission(args)
    except (OSError, ValueError, tarfile.TarError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
