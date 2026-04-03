#!/usr/bin/env python3
"""Ingest an approved inbox submission into a target skills/docs layout."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from market_utils import (
    ROOT,
    dump_json,
    load_json,
    repo_relative_path,
    rewrite_command_paths,
    validate_market_manifest,
    validate_skill_submission_review_payload,
)
from validate_skill_submission import validate_submission_file


DEFAULT_SKILLS_DIR = ROOT / "skills"
DEFAULT_DOCS_DIR = ROOT / "docs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest an approved inbox submission into a target skills/docs layout.")
    parser.add_argument("path", type=Path, help="Path to submission.json.")
    parser.add_argument("--review-path", type=Path, help="Optional review artifact path. Defaults to sibling review.json.")
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_SKILLS_DIR, help="Destination root for ingested skills.")
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR, help="Destination root for ingested docs.")
    parser.add_argument("--force", action="store_true", help="Replace existing ingested skill/docs targets.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    resolved = path if path.is_absolute() else (ROOT / path)
    resolved = resolved.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"path must stay inside the repository root: {resolved}") from exc
    return resolved


def load_review(review_path: Path, submission_id: str) -> tuple[dict, list[str]]:
    if not review_path.is_file():
        return {}, [f"missing review artifact {repo_relative_path(review_path)}"]

    payload = load_json(review_path)
    errors = validate_skill_submission_review_payload(payload, repo_relative_path(review_path))
    if payload.get("submission_id") != submission_id:
        errors.append(f"{repo_relative_path(review_path)}: submission_id does not match the submission being ingested")
    return payload, errors


def rewrite_docs_text(raw_text: str, replacements: list[tuple[str, str]]) -> str:
    updated = raw_text
    for old, new in replacements:
        if old and old != new:
            updated = updated.replace(old, new)
    return updated


def ingest_submission(args: argparse.Namespace) -> int:
    try:
        submission_path = resolve_repo_path(args.path)
        skills_dir = resolve_repo_path(args.skills_dir)
        docs_dir = resolve_repo_path(args.docs_dir)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    submission, errors = validate_submission_file(submission_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    review_path = resolve_repo_path(args.review_path) if args.review_path else submission_path.parent / "review.json"
    review_payload, review_errors = load_review(review_path, submission["submission_id"])
    if review_errors:
        for error in review_errors:
            print(f"ERROR: {error}")
        return 1
    if review_payload["review_status"] != "approved":
        print(f"ERROR: review status must be approved before ingest, got '{review_payload['review_status']}'")
        return 1

    uploaded_skill_dir = resolve_repo_path(Path(submission["source_dir"]))
    uploaded_docs_path = resolve_repo_path(Path(submission["docs_path"]))
    uploaded_manifest_path = resolve_repo_path(Path(submission["manifest_path"]))
    uploaded_source_root = submission_path.parent / "source"

    canonical_skill_dir = skills_dir / submission["skill_name"]
    canonical_manifest_path = canonical_skill_dir / "market" / "skill.json"
    try:
        relative_docs_path = uploaded_docs_path.relative_to(uploaded_source_root / "docs")
    except ValueError:
        relative_docs_path = Path(uploaded_docs_path.name)
    canonical_docs_path = docs_dir / relative_docs_path
    canonical_skill_rel = repo_relative_path(canonical_skill_dir)
    canonical_docs_rel = repo_relative_path(canonical_docs_path)
    canonical_entrypoint_rel = f"{canonical_skill_rel}/SKILL.md"

    existing_targets: list[Path] = []
    if canonical_skill_dir.exists():
        existing_targets.append(canonical_skill_dir)
    if canonical_docs_path.exists():
        existing_targets.append(canonical_docs_path)
    if existing_targets and not args.force:
        joined = ", ".join(repo_relative_path(path) for path in existing_targets)
        print(f"ERROR: ingest targets already exist: {joined}")
        return 1

    if canonical_skill_dir.exists():
        shutil.rmtree(canonical_skill_dir)
    if canonical_docs_path.exists():
        canonical_docs_path.unlink()

    canonical_skill_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(uploaded_skill_dir, canonical_skill_dir)

    source_manifest = load_json(uploaded_manifest_path)
    source_artifacts = source_manifest.get("artifacts", {})
    original_source_dir = str(source_artifacts.get("source_dir", "")).strip() or submission["source_dir"]
    original_entrypoint = str(source_artifacts.get("entrypoint", "")).strip() or f"{original_source_dir}/SKILL.md"
    original_docs_rel = str(source_artifacts.get("docs", "")).strip() or submission["docs_path"]
    replacements = [
        (original_source_dir, canonical_skill_rel),
        (original_entrypoint, canonical_entrypoint_rel),
        (original_docs_rel, canonical_docs_rel),
    ]

    ingested_manifest = load_json(canonical_manifest_path)
    ingested_manifest["artifacts"]["source_dir"] = canonical_skill_rel
    ingested_manifest["artifacts"]["entrypoint"] = canonical_entrypoint_rel
    ingested_manifest["artifacts"]["docs"] = canonical_docs_rel
    ingested_manifest["quality"]["checker"] = rewrite_command_paths(
        str(ingested_manifest["quality"]["checker"]),
        replacements,
    )
    ingested_manifest["quality"]["eval"] = rewrite_command_paths(
        str(ingested_manifest["quality"]["eval"]),
        replacements,
    )
    ingested_manifest["quality"]["review_status"] = "reviewed"
    dump_json(canonical_manifest_path, ingested_manifest)

    canonical_docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_text = rewrite_docs_text(uploaded_docs_path.read_text(encoding="utf-8"), replacements)
    canonical_docs_path.write_text(docs_text, encoding="utf-8")

    _, manifest_errors = validate_market_manifest(canonical_manifest_path)
    if manifest_errors:
        for error in manifest_errors:
            print(f"ERROR: {error}")
        return 1

    ingest_receipt_path = submission_path.parent / "ingest.json"
    ingest_payload = {
        "ingest_format": "moyuan-skill-ingest@v1",
        "submission_id": submission["submission_id"],
        "review_path": repo_relative_path(review_path),
        "review_status": review_payload["review_status"],
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "ingested_by": review_payload["reviewer"],
        "target_source_dir": canonical_skill_rel,
        "target_docs_path": canonical_docs_rel,
        "target_manifest_path": repo_relative_path(canonical_manifest_path),
        "status": "ingested",
    }
    dump_json(ingest_receipt_path, ingest_payload)

    print(f"Ingested submission {submission['submission_id']}")
    print(f"Skill directory: {canonical_skill_dir}")
    print(f"Docs path: {canonical_docs_path}")
    print(f"Ingest receipt: {ingest_receipt_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return ingest_submission(args)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
