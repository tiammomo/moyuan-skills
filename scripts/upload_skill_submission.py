#!/usr/bin/env python3
"""Upload a repo-compatible skill submission into a local inbox."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from build_skill_submission import build_payload_archive
from market_utils import (
    ROOT,
    build_provenance_payload,
    dump_json,
    load_json,
    repo_relative_path,
    rewrite_command_paths,
    sha256_for_file,
    validate_market_manifest,
)
from validate_skill_submission import validate_submission_file


DEFAULT_INBOX_DIR = ROOT / "incoming" / "submissions"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Upload a skill submission into a local inbox directory.")
    parser.add_argument("path", type=Path, help="Path to submission.json.")
    parser.add_argument("--inbox-dir", type=Path, default=DEFAULT_INBOX_DIR, help="Inbox directory receiving uploaded submissions.")
    parser.add_argument("--force", action="store_true", help="Replace an existing uploaded submission directory.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    resolved = path if path.is_absolute() else (ROOT / path)
    resolved = resolved.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"path must stay inside the repository root: {resolved}") from exc
    return resolved


def upload_submission(args: argparse.Namespace) -> int:
    try:
        submission_path = resolve_repo_path(args.path)
        inbox_dir = resolve_repo_path(args.inbox_dir)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    submission, errors = validate_submission_file(submission_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    uploaded_dir = inbox_dir / submission["publisher"] / submission["skill_name"] / submission["version"]
    if uploaded_dir.exists():
        if not args.force:
            print(f"ERROR: uploaded submission directory already exists: {repo_relative_path(uploaded_dir)}")
            return 1
        shutil.rmtree(uploaded_dir)

    source_dir = resolve_repo_path(Path(submission["source_dir"]))
    docs_path = resolve_repo_path(Path(submission["docs_path"]))
    package_path = resolve_repo_path(Path(submission["package_path"]))
    install_spec_path = resolve_repo_path(Path(submission["install_spec_path"]))
    provenance_path = resolve_repo_path(Path(submission["provenance_path"]))
    source_rel = Path(submission["source_dir"])
    docs_rel = Path(submission["docs_path"])

    uploaded_source_root = uploaded_dir / "source"
    uploaded_artifacts_root = uploaded_dir / "artifacts"
    uploaded_skill_dir = uploaded_source_root / source_rel
    uploaded_docs_path = uploaded_source_root / docs_rel
    uploaded_package_path = uploaded_artifacts_root / "packages" / package_path.name
    uploaded_install_spec_path = uploaded_artifacts_root / "install" / install_spec_path.name
    uploaded_provenance_path = uploaded_artifacts_root / "provenance" / provenance_path.name
    uploaded_manifest_path = uploaded_skill_dir / "market" / "skill.json"
    uploaded_payload_archive_path = uploaded_dir / "payload.tgz"

    uploaded_skill_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, uploaded_skill_dir)
    uploaded_docs_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(docs_path, uploaded_docs_path)
    uploaded_package_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(package_path, uploaded_package_path)

    uploaded_manifest = load_json(uploaded_manifest_path)
    uploaded_path_replacements = [
        (submission["source_dir"], repo_relative_path(uploaded_skill_dir)),
        (submission["docs_path"], repo_relative_path(uploaded_docs_path)),
    ]
    uploaded_manifest["artifacts"]["source_dir"] = repo_relative_path(uploaded_skill_dir)
    uploaded_manifest["artifacts"]["entrypoint"] = repo_relative_path(uploaded_skill_dir / "SKILL.md")
    uploaded_manifest["artifacts"]["docs"] = repo_relative_path(uploaded_docs_path)
    uploaded_manifest["quality"]["checker"] = rewrite_command_paths(uploaded_manifest["quality"]["checker"], uploaded_path_replacements)
    uploaded_manifest["quality"]["eval"] = rewrite_command_paths(uploaded_manifest["quality"]["eval"], uploaded_path_replacements)
    dump_json(uploaded_manifest_path, uploaded_manifest)

    _, uploaded_manifest_errors = validate_market_manifest(uploaded_manifest_path)
    if uploaded_manifest_errors:
        for error in uploaded_manifest_errors:
            print(f"ERROR: {error}")
        return 1

    uploaded_package_checksum = sha256_for_file(uploaded_package_path)
    uploaded_provenance = build_provenance_payload(uploaded_manifest, uploaded_package_path, uploaded_package_checksum)
    uploaded_provenance["generated_at"] = datetime.now(timezone.utc).isoformat()
    uploaded_provenance["builder"] = "scripts/upload_skill_submission.py"
    uploaded_provenance_path.parent.mkdir(parents=True, exist_ok=True)
    dump_json(uploaded_provenance_path, uploaded_provenance)

    uploaded_install_spec = load_json(install_spec_path)
    uploaded_install_spec["package_path"] = repo_relative_path(uploaded_package_path)
    uploaded_install_spec["checksum_sha256"] = uploaded_package_checksum
    uploaded_install_spec["provenance_path"] = repo_relative_path(uploaded_provenance_path)
    uploaded_install_spec["provenance_sha256"] = sha256_for_file(uploaded_provenance_path)
    uploaded_install_spec_path.parent.mkdir(parents=True, exist_ok=True)
    dump_json(uploaded_install_spec_path, uploaded_install_spec)

    build_payload_archive(uploaded_skill_dir, uploaded_docs_path, uploaded_payload_archive_path)
    uploaded_submission = dict(submission)
    uploaded_submission["manifest_path"] = repo_relative_path(uploaded_manifest_path)
    uploaded_submission["source_dir"] = repo_relative_path(uploaded_skill_dir)
    uploaded_submission["docs_path"] = repo_relative_path(uploaded_docs_path)
    uploaded_submission["install_spec_path"] = repo_relative_path(uploaded_install_spec_path)
    uploaded_submission["provenance_path"] = repo_relative_path(uploaded_provenance_path)
    uploaded_submission["package_path"] = repo_relative_path(uploaded_package_path)
    uploaded_submission["payload_archive_path"] = repo_relative_path(uploaded_payload_archive_path)
    uploaded_submission["payload_archive_sha256"] = sha256_for_file(uploaded_payload_archive_path)
    uploaded_submission["checker_command"] = uploaded_manifest["quality"]["checker"]
    uploaded_submission["eval_command"] = uploaded_manifest["quality"]["eval"]
    uploaded_submission_path = uploaded_dir / "submission.json"
    dump_json(uploaded_submission_path, uploaded_submission)

    _, uploaded_errors = validate_submission_file(uploaded_submission_path)
    if uploaded_errors:
        for error in uploaded_errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Uploaded submission to {uploaded_submission_path}")
    print(f"Uploaded payload archive: {uploaded_payload_archive_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return upload_submission(args)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
