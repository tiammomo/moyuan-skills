#!/usr/bin/env python3
"""Helpers for the local skills market draft."""

from __future__ import annotations

import hashlib
import json
import re
import shlex
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
PUBLISHERS_DIR = ROOT / "publishers"
GOVERNANCE_DIR = ROOT / "governance"
ORG_POLICIES_DIR = GOVERNANCE_DIR / "orgs"
BUNDLES_DIR = ROOT / "bundles"
MARKET_CHANNELS = {"stable", "beta", "internal"}
PLATFORMS = {"windows", "macos", "linux"}
WORKSPACE_LEVELS = {"none", "read", "write"}
ACCESS_LEVELS = {"none", "limited", "full"}
SECRET_LEVELS = {"none", "read", "write"}
REVIEW_STATUSES = {"draft", "reviewed", "deprecated"}
TRUST_LEVELS = {"community", "verified", "official"}
LIFECYCLE_STATUSES = {"active", "deprecated", "blocked", "archived"}
BUNDLE_STATUSES = {"draft", "published"}
SUBMISSION_REVIEW_STATUSES = {"pending", "approved", "rejected", "needs-changes"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return payload


def dump_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_for_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify_filename_token(value: str, *, fallback: str = "item", max_length: int = 12) -> str:
    slug = FILENAME_TOKEN_RE.sub("-", value.strip().lower()).strip("-")
    if not slug:
        return fallback
    trimmed = slug[:max_length].strip("-")
    return trimmed or fallback


def build_hashed_artifact_name(*parts: str, suffix: str = "", fallback: str = "artifact") -> str:
    normalized_parts = [str(part).strip() for part in parts if str(part).strip()]
    digest_source = "::".join(normalized_parts or [fallback]).encode("utf-8")
    digest = sha256_for_bytes(digest_source)[:10]
    stem_parts = [
        slugify_filename_token(part, fallback=f"{fallback}{index + 1}")
        for index, part in enumerate(normalized_parts[:3])
    ]
    stem = "-".join(stem_parts) if stem_parts else fallback
    normalized_suffix = suffix if not suffix or suffix.startswith(".") else f".{suffix}"
    return f"{stem}-{digest}{normalized_suffix}"


def repo_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"path must stay inside repository root: {resolved}") from exc


def rewrite_command_paths(command: str, replacements: list[tuple[str, str]]) -> str:
    if not command:
        return command
    try:
        tokens = shlex.split(command)
    except ValueError:
        return command

    normalized = sorted(
        [(old.rstrip("/"), new.rstrip("/")) for old, new in replacements if old and new],
        key=lambda item: len(item[0]),
        reverse=True,
    )
    rewritten: list[str] = []
    for token in tokens:
        updated = token
        for old_prefix, new_prefix in normalized:
            if token == old_prefix:
                updated = new_prefix
                break
            if token.startswith(f"{old_prefix}/"):
                updated = f"{new_prefix}{token[len(old_prefix):]}"
                break
        rewritten.append(updated)
    return shlex.join(rewritten)


def resolve_target_root(target_root: Path) -> Path:
    return target_root if target_root.is_absolute() else (ROOT / target_root)


def load_lock_payload(target_root: Path) -> tuple[Path, dict]:
    resolved_root = resolve_target_root(target_root)
    lock_path = resolved_root / "skills.lock.json"
    if lock_path.is_file():
        payload = load_json(lock_path)
    else:
        payload = {"installed": []}
    if not isinstance(payload.get("installed"), list):
        payload["installed"] = []
    return lock_path, payload


def write_lock_payload(lock_path: Path, payload: dict) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_install_sources(entry: dict | None) -> list[dict]:
    if entry is None:
        return []
    if not isinstance(entry, dict):
        return []
    raw_sources = entry.get("sources")
    normalized: list[dict] = []
    if isinstance(raw_sources, list):
        for item in raw_sources:
            if not isinstance(item, dict):
                continue
            kind = str(item.get("kind", "")).strip().lower()
            source_id = str(item.get("id", "")).strip()
            if not kind or not source_id:
                continue
            normalized.append({"kind": kind, "id": source_id})
    if normalized:
        deduped: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for item in normalized:
            key = (item["kind"], item["id"])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped
    return [{"kind": "direct", "id": "direct-install"}]


def merge_install_source(entry: dict | None, source_kind: str, source_id: str) -> list[dict]:
    sources = normalize_install_sources(entry)
    key = (source_kind, source_id)
    if key not in {(item["kind"], item["id"]) for item in sources}:
        sources.append({"kind": source_kind, "id": source_id})
    return sources


def remove_install_source(entry: dict, source_kind: str, source_id: str) -> list[dict]:
    return [
        item
        for item in normalize_install_sources(entry)
        if not (item["kind"] == source_kind and item["id"] == source_id)
    ]


def match_bundle_token(bundle: dict, token: str) -> bool:
    lowered = token.strip().lower()
    return lowered in {
        str(bundle.get("id", "")).lower(),
        str(bundle.get("title", "")).lower(),
    }


def resolve_bundle_definition(bundles: list[dict], token: str) -> dict | None:
    return next((bundle for bundle in bundles if match_bundle_token(bundle, token)), None)


def match_installed_entry(entry: dict, token: str) -> bool:
    lowered = token.strip().lower()
    candidates = [
        str(entry.get("skill_id", "")),
        str(entry.get("skill_name", "")),
        str(entry.get("install_target", "")),
    ]
    return any(candidate.lower() == lowered for candidate in candidates if candidate)


def iter_manifest_paths() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/market/skill.json"))


def iter_publisher_profile_paths() -> list[Path]:
    return sorted(PUBLISHERS_DIR.glob("*.json"))


def iter_org_policy_paths() -> list[Path]:
    return sorted(ORG_POLICIES_DIR.glob("*.json"))


def iter_bundle_paths() -> list[Path]:
    return sorted(BUNDLES_DIR.glob("*.json"))


def iter_skill_source_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for file_path in sorted(source_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if "__pycache__" in file_path.parts or ".pytest_cache" in file_path.parts:
            continue
        files.append(file_path)
    return files


def required_string(payload: dict, key: str, errors: list[str], label: str, min_length: int = 1) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or len(value.strip()) < min_length:
        errors.append(f"{label}: '{key}' must be a non-empty string")
        return ""
    return value.strip()


def optional_string(
    payload: dict,
    key: str,
    errors: list[str],
    label: str,
    *,
    min_length: int = 1,
) -> str:
    value = payload.get(key, "")
    if value in ("", None):
        return ""
    if not isinstance(value, str) or len(value.strip()) < min_length:
        errors.append(f"{label}: optional field '{key}' must be a string when provided")
        return ""
    return value.strip()


def required_list(payload: dict, key: str, errors: list[str], label: str, allow_empty: bool = False) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{label}: '{key}' must be a list of strings")
        return []
    cleaned = [item.strip() for item in value]
    if not allow_empty and not cleaned:
        errors.append(f"{label}: '{key}' must be a non-empty list of strings")
    return cleaned


def optional_date(payload: dict, key: str, errors: list[str], label: str) -> str:
    value = optional_string(payload, key, errors, label)
    if value and not DATE_RE.match(value):
        errors.append(f"{label}: optional field '{key}' must use YYYY-MM-DD format")
        return ""
    return value


def validate_market_manifest(path: Path) -> tuple[dict, list[str]]:
    payload = load_json(path)
    errors: list[str] = []
    label = path.relative_to(ROOT).as_posix()

    skill_id = required_string(payload, "id", errors, label, min_length=3)
    publisher = required_string(payload, "publisher", errors, label, min_length=2)
    name = required_string(payload, "name", errors, label, min_length=2)
    required_string(payload, "title", errors, label, min_length=3)
    required_string(payload, "version", errors, label, min_length=3)
    channel = required_string(payload, "channel", errors, label, min_length=4)
    required_string(payload, "summary", errors, label, min_length=20)
    required_string(payload, "description", errors, label, min_length=40)
    required_list(payload, "categories", errors, label)
    required_list(payload, "tags", errors, label)

    if channel and channel not in MARKET_CHANNELS:
        errors.append(f"{label}: 'channel' must be one of {sorted(MARKET_CHANNELS)}")
    if skill_id and publisher and not skill_id.startswith(f"{publisher}."):
        errors.append(f"{label}: 'id' should start with publisher namespace '{publisher}.'")

    expected_name = path.parents[1].name
    if name and name != expected_name:
        errors.append(f"{label}: manifest 'name' should match skill directory '{expected_name}'")

    compatibility = payload.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append(f"{label}: 'compatibility' must be an object")
    else:
        required_string(compatibility, "codex_min_version", errors, f"{label}:compatibility", min_length=3)
        required_string(compatibility, "python", errors, f"{label}:compatibility", min_length=3)
        platforms = required_list(compatibility, "platforms", errors, f"{label}:compatibility")
        if platforms and any(platform not in PLATFORMS for platform in platforms):
            errors.append(f"{label}:compatibility: 'platforms' contains unsupported values")

    permissions = payload.get("permissions")
    if not isinstance(permissions, dict):
        errors.append(f"{label}: 'permissions' must be an object")
    else:
        workspace = required_string(permissions, "workspace", errors, f"{label}:permissions", min_length=2)
        network = required_string(permissions, "network", errors, f"{label}:permissions", min_length=2)
        shell = required_string(permissions, "shell", errors, f"{label}:permissions", min_length=2)
        secrets = required_string(permissions, "secrets", errors, f"{label}:permissions", min_length=2)
        review = permissions.get("human_review_required")
        if workspace and workspace not in WORKSPACE_LEVELS:
            errors.append(f"{label}:permissions: unsupported workspace level '{workspace}'")
        if network and network not in ACCESS_LEVELS:
            errors.append(f"{label}:permissions: unsupported network level '{network}'")
        if shell and shell not in ACCESS_LEVELS:
            errors.append(f"{label}:permissions: unsupported shell level '{shell}'")
        if secrets and secrets not in SECRET_LEVELS:
            errors.append(f"{label}:permissions: unsupported secrets level '{secrets}'")
        if not isinstance(review, bool):
            errors.append(f"{label}:permissions: 'human_review_required' must be a boolean")

    quality = payload.get("quality")
    if not isinstance(quality, dict):
        errors.append(f"{label}: 'quality' must be an object")
    else:
        checker = required_string(quality, "checker", errors, f"{label}:quality", min_length=5)
        eval_command = required_string(quality, "eval", errors, f"{label}:quality", min_length=5)
        review_status = required_string(quality, "review_status", errors, f"{label}:quality", min_length=5)
        if review_status and review_status not in REVIEW_STATUSES:
            errors.append(f"{label}:quality: unsupported review_status '{review_status}'")
        for key, command in (("checker", checker), ("eval", eval_command)):
            if command and not command.startswith("python "):
                errors.append(f"{label}:quality: '{key}' should be a python command for this repo draft")

    lifecycle = payload.get("lifecycle")
    if not isinstance(lifecycle, dict):
        errors.append(f"{label}: 'lifecycle' must be an object")
    else:
        status = required_string(lifecycle, "status", errors, f"{label}:lifecycle", min_length=4)
        replacement_skill_id = optional_string(lifecycle, "replacement_skill_id", errors, f"{label}:lifecycle", min_length=3)
        sunset_at = optional_date(lifecycle, "sunset_at", errors, f"{label}:lifecycle")
        optional_string(lifecycle, "notes", errors, f"{label}:lifecycle", min_length=5)
        if status and status not in LIFECYCLE_STATUSES:
            errors.append(f"{label}:lifecycle: unsupported status '{status}'")
        if replacement_skill_id and "." not in replacement_skill_id:
            errors.append(f"{label}:lifecycle: 'replacement_skill_id' should look like a namespaced skill id")
        if sunset_at and status == "active":
            errors.append(f"{label}:lifecycle: active skills should not define 'sunset_at'")

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append(f"{label}: 'artifacts' must be an object")
    else:
        source_dir = required_string(artifacts, "source_dir", errors, f"{label}:artifacts", min_length=5)
        entrypoint = required_string(artifacts, "entrypoint", errors, f"{label}:artifacts", min_length=5)
        docs = required_string(artifacts, "docs", errors, f"{label}:artifacts", min_length=5)
        for key, raw_path in (("source_dir", source_dir), ("entrypoint", entrypoint), ("docs", docs)):
            if raw_path and not (ROOT / raw_path).exists():
                errors.append(f"{label}:artifacts: '{key}' points to missing path '{raw_path}'")

    search = payload.get("search")
    if not isinstance(search, dict):
        errors.append(f"{label}: 'search' must be an object")
    else:
        required_list(search, "keywords", errors, f"{label}:search")
        related = search.get("related_skills")
        if not isinstance(related, list) or not all(isinstance(item, str) and item.strip() for item in related):
            errors.append(f"{label}:search: 'related_skills' must be a list of strings")

    distribution = payload.get("distribution")
    if not isinstance(distribution, dict):
        errors.append(f"{label}: 'distribution' must be an object")
    else:
        capabilities = required_list(distribution, "capabilities", errors, f"{label}:distribution")
        starter_bundle_ids = required_list(distribution, "starter_bundle_ids", errors, f"{label}:distribution", allow_empty=True)
        if capabilities and any(" " not in value and "-" not in value for value in capabilities):
            errors.append(f"{label}:distribution: 'capabilities' should use descriptive slugs")
        if starter_bundle_ids and any(len(value) < 3 for value in starter_bundle_ids):
            errors.append(f"{label}:distribution: 'starter_bundle_ids' contains unsupported values")

    return payload, errors


def validate_install_spec_payload(payload: dict, label: str) -> list[str]:
    errors: list[str] = []

    required_string(payload, "skill_id", errors, label, min_length=3)
    required_string(payload, "skill_name", errors, label, min_length=2)
    required_string(payload, "publisher", errors, label, min_length=2)
    required_string(payload, "version", errors, label, min_length=3)
    channel = required_string(payload, "channel", errors, label, min_length=4)
    package_type = required_string(payload, "package_type", errors, label, min_length=3)
    package_path = required_string(payload, "package_path", errors, label, min_length=5)
    checksum = required_string(payload, "checksum_sha256", errors, label, min_length=64)
    required_string(payload, "entrypoint", errors, label, min_length=5)
    required_string(payload, "install_target", errors, label, min_length=2)
    review_status = required_string(payload, "review_status", errors, label, min_length=5)
    lifecycle_status = required_string(payload, "lifecycle_status", errors, label, min_length=4)
    provenance_path = required_string(payload, "provenance_path", errors, label, min_length=5)
    provenance_sha256 = required_string(payload, "provenance_sha256", errors, label, min_length=64)

    if channel and channel not in MARKET_CHANNELS:
        errors.append(f"{label}: unsupported channel '{channel}'")
    if package_type and package_type != "zip":
        errors.append(f"{label}: 'package_type' must be 'zip'")
    if checksum and not SHA256_RE.match(checksum):
        errors.append(f"{label}: 'checksum_sha256' must be a lowercase 64-character SHA256 digest")
    if review_status and review_status not in REVIEW_STATUSES:
        errors.append(f"{label}: unsupported review_status '{review_status}'")
    if lifecycle_status and lifecycle_status not in LIFECYCLE_STATUSES:
        errors.append(f"{label}: unsupported lifecycle_status '{lifecycle_status}'")
    if provenance_sha256 and not SHA256_RE.match(provenance_sha256):
        errors.append(f"{label}: 'provenance_sha256' must be a lowercase 64-character SHA256 digest")
    if package_path:
        resolved_package = ROOT / package_path
        if not resolved_package.is_file():
            errors.append(f"{label}: 'package_path' points to missing artifact '{package_path}'")
    if provenance_path:
        resolved_provenance = ROOT / provenance_path
        if not resolved_provenance.is_file():
            errors.append(f"{label}: 'provenance_path' points to missing artifact '{provenance_path}'")

    return errors


def validate_provenance_payload(payload: dict, label: str, *, require_local_paths: bool = True) -> list[str]:
    errors: list[str] = []

    required_string(payload, "attestation_format", errors, label, min_length=5)
    required_string(payload, "skill_id", errors, label, min_length=3)
    required_string(payload, "skill_name", errors, label, min_length=2)
    required_string(payload, "publisher", errors, label, min_length=2)
    required_string(payload, "version", errors, label, min_length=3)
    channel = required_string(payload, "channel", errors, label, min_length=4)
    required_string(payload, "generated_at", errors, label, min_length=10)
    required_string(payload, "builder", errors, label, min_length=5)
    required_string(payload, "manifest_path", errors, label, min_length=5)
    required_string(payload, "source_dir", errors, label, min_length=5)
    manifest_checksum = required_string(payload, "manifest_checksum_sha256", errors, label, min_length=64)
    source_checksum = required_string(payload, "source_tree_checksum_sha256", errors, label, min_length=64)

    if channel and channel not in MARKET_CHANNELS:
        errors.append(f"{label}: unsupported channel '{channel}'")
    for key, value in (
        ("manifest_checksum_sha256", manifest_checksum),
        ("source_tree_checksum_sha256", source_checksum),
    ):
        if value and not SHA256_RE.match(value):
            errors.append(f"{label}: '{key}' must be a lowercase 64-character SHA256 digest")

    package = payload.get("package")
    if not isinstance(package, dict):
        errors.append(f"{label}: 'package' must be an object")
    else:
        package_path = required_string(package, "path", errors, f"{label}:package", min_length=5)
        package_checksum = required_string(package, "checksum_sha256", errors, f"{label}:package", min_length=64)
        size_bytes = package.get("size_bytes")
        if package_checksum and not SHA256_RE.match(package_checksum):
            errors.append(f"{label}:package: 'checksum_sha256' must be a lowercase 64-character SHA256 digest")
        if not isinstance(size_bytes, int) or size_bytes <= 0:
            errors.append(f"{label}:package: 'size_bytes' must be a positive integer")
        if require_local_paths and package_path and not (ROOT / package_path).is_file():
            errors.append(f"{label}:package: missing package artifact '{package_path}'")

    quality = payload.get("quality")
    if not isinstance(quality, dict):
        errors.append(f"{label}: 'quality' must be an object")
    else:
        checker = required_string(quality, "checker", errors, f"{label}:quality", min_length=5)
        eval_command = required_string(quality, "eval", errors, f"{label}:quality", min_length=5)
        review_status = required_string(quality, "review_status", errors, f"{label}:quality", min_length=5)
        if review_status and review_status not in REVIEW_STATUSES:
            errors.append(f"{label}:quality: unsupported review_status '{review_status}'")
        for key, command in (("checker", checker), ("eval", eval_command)):
            if command and not command.startswith("python "):
                errors.append(f"{label}:quality: '{key}' should be a python command for this repo draft")

    lifecycle = payload.get("lifecycle")
    if not isinstance(lifecycle, dict):
        errors.append(f"{label}: 'lifecycle' must be an object")
    else:
        status = required_string(lifecycle, "status", errors, f"{label}:lifecycle", min_length=4)
        replacement_skill_id = optional_string(lifecycle, "replacement_skill_id", errors, f"{label}:lifecycle", min_length=3)
        optional_date(lifecycle, "sunset_at", errors, f"{label}:lifecycle")
        if status and status not in LIFECYCLE_STATUSES:
            errors.append(f"{label}:lifecycle: unsupported status '{status}'")
        if replacement_skill_id and "." not in replacement_skill_id:
            errors.append(f"{label}:lifecycle: 'replacement_skill_id' should look like a namespaced skill id")

    files = payload.get("files")
    if not isinstance(files, list) or not files:
        errors.append(f"{label}: 'files' must be a non-empty list")
    else:
        for index, item in enumerate(files):
            if not isinstance(item, dict):
                errors.append(f"{label}:files[{index}] must be an object")
                continue
            file_path = required_string(item, "path", errors, f"{label}:files[{index}]", min_length=5)
            file_checksum = required_string(item, "sha256", errors, f"{label}:files[{index}]", min_length=64)
            if file_checksum and not SHA256_RE.match(file_checksum):
                errors.append(f"{label}:files[{index}]: 'sha256' must be a lowercase 64-character SHA256 digest")
            if require_local_paths and file_path and not (ROOT / file_path).is_file():
                errors.append(f"{label}:files[{index}]: missing source file '{file_path}'")

    return errors


def validate_skill_submission_payload(payload: dict, label: str) -> list[str]:
    errors: list[str] = []

    submission_format = required_string(payload, "submission_format", errors, label, min_length=10)
    submission_id = required_string(payload, "submission_id", errors, label, min_length=5)
    required_string(payload, "publisher", errors, label, min_length=2)
    skill_id = required_string(payload, "skill_id", errors, label, min_length=3)
    required_string(payload, "skill_name", errors, label, min_length=2)
    version = required_string(payload, "version", errors, label, min_length=3)
    channel = required_string(payload, "channel", errors, label, min_length=4)
    required_string(payload, "created_at", errors, label, min_length=10)
    source_dir = required_string(payload, "source_dir", errors, label, min_length=5)
    docs_path = required_string(payload, "docs_path", errors, label, min_length=5)
    manifest_path = required_string(payload, "manifest_path", errors, label, min_length=5)
    install_spec_path = required_string(payload, "install_spec_path", errors, label, min_length=5)
    provenance_path = required_string(payload, "provenance_path", errors, label, min_length=5)
    package_path = required_string(payload, "package_path", errors, label, min_length=5)
    payload_archive_path = required_string(payload, "payload_archive_path", errors, label, min_length=5)
    payload_archive_sha256 = required_string(payload, "payload_archive_sha256", errors, label, min_length=64)
    required_string(payload, "checker_command", errors, label, min_length=5)
    required_string(payload, "eval_command", errors, label, min_length=5)
    required_string(payload, "release_notes", errors, label, min_length=3)

    if submission_format and submission_format != "moyuan-skill-submission@v1":
        errors.append(f"{label}: unsupported submission_format '{submission_format}'")
    if submission_id and skill_id and version and submission_id != f"{skill_id}@{version}":
        errors.append(f"{label}: 'submission_id' must match '<skill_id>@<version>'")
    if channel and channel not in MARKET_CHANNELS:
        errors.append(f"{label}: unsupported channel '{channel}'")
    if payload_archive_sha256 and not SHA256_RE.match(payload_archive_sha256):
        errors.append(f"{label}: 'payload_archive_sha256' must be a lowercase 64-character SHA256 digest")

    for key, raw_path in (
        ("source_dir", source_dir),
        ("docs_path", docs_path),
        ("manifest_path", manifest_path),
        ("install_spec_path", install_spec_path),
        ("provenance_path", provenance_path),
        ("package_path", package_path),
        ("payload_archive_path", payload_archive_path),
    ):
        if not raw_path:
            continue
        path_obj = Path(raw_path)
        if path_obj.is_absolute():
            errors.append(f"{label}: '{key}' must use a repo-relative path")
            continue
        resolved = (ROOT / path_obj).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            errors.append(f"{label}: '{key}' must stay inside the repository root")
            continue
        if not resolved.exists():
            errors.append(f"{label}: '{key}' points to missing path '{raw_path}'")
            continue
        if key in {"source_dir"} and not resolved.is_dir():
            errors.append(f"{label}: '{key}' must point to a directory")
        if key not in {"source_dir"} and not resolved.is_file():
            errors.append(f"{label}: '{key}' must point to a file")

    return errors


def validate_skill_submission_review_payload(payload: dict, label: str) -> list[str]:
    errors: list[str] = []

    review_format = required_string(payload, "review_format", errors, label, min_length=10)
    required_string(payload, "submission_id", errors, label, min_length=5)
    review_status = required_string(payload, "review_status", errors, label, min_length=6)
    required_string(payload, "reviewer", errors, label, min_length=2)
    required_string(payload, "reviewed_at", errors, label, min_length=10)
    required_string(payload, "summary", errors, label, min_length=5)

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        errors.append(f"{label}: 'findings' must be a list")
    else:
        for index, finding in enumerate(findings, start=1):
            item_label = f"{label}:findings[{index}]"
            if not isinstance(finding, dict):
                errors.append(f"{item_label} must be an object")
                continue
            severity = required_string(finding, "severity", errors, item_label, min_length=3)
            required_string(finding, "message", errors, item_label, min_length=3)
            optional_string(finding, "path", errors, item_label, min_length=3)
            if severity and severity not in {"critical", "high", "medium", "low", "info"}:
                errors.append(f"{item_label}: unsupported severity '{severity}'")

    if review_format and review_format != "moyuan-skill-submission-review@v1":
        errors.append(f"{label}: unsupported review_format '{review_format}'")
    if review_status and review_status not in SUBMISSION_REVIEW_STATUSES:
        errors.append(f"{label}: unsupported review_status '{review_status}'")

    return errors


def validate_publisher_profile(path: Path) -> tuple[dict, list[str]]:
    payload = load_json(path)
    errors: list[str] = []
    label = path.relative_to(ROOT).as_posix()

    publisher_id = required_string(payload, "id", errors, label, min_length=2)
    required_string(payload, "display_name", errors, label, min_length=3)
    trust_level = required_string(payload, "trust_level", errors, label, min_length=3)
    contact_email = required_string(payload, "contact_email", errors, label, min_length=6)
    homepage = required_string(payload, "homepage", errors, label, min_length=8)
    namespaces = required_list(payload, "namespaces", errors, label)
    verified = payload.get("verified")

    if trust_level and trust_level not in TRUST_LEVELS:
        errors.append(f"{label}: unsupported trust_level '{trust_level}'")
    if contact_email and not EMAIL_RE.match(contact_email):
        errors.append(f"{label}: 'contact_email' must look like a valid email address")
    if homepage and not homepage.startswith(("https://", "http://")):
        errors.append(f"{label}: 'homepage' should be an http(s) URL")
    if not isinstance(verified, bool):
        errors.append(f"{label}: 'verified' must be a boolean")
    if publisher_id and namespaces and publisher_id not in namespaces:
        errors.append(f"{label}: 'namespaces' should include publisher id '{publisher_id}'")
    if verified is True and trust_level == "community":
        errors.append(f"{label}: verified publishers should not use trust_level 'community'")

    verification = payload.get("verification")
    if verified:
        if not isinstance(verification, dict):
            errors.append(f"{label}: verified publishers must define a 'verification' object")
        else:
            required_string(verification, "issued_by", errors, f"{label}:verification", min_length=3)
            issued_at = optional_date(verification, "issued_at", errors, f"{label}:verification")
            policy = required_string(verification, "policy_url", errors, f"{label}:verification", min_length=8)
            required_string(verification, "method", errors, f"{label}:verification", min_length=5)
            if issued_at and not DATE_RE.match(issued_at):
                errors.append(f"{label}:verification: 'issued_at' must use YYYY-MM-DD format")
            if policy and not policy.startswith(("https://", "http://")):
                errors.append(f"{label}:verification: 'policy_url' should be an http(s) URL")
    elif verification not in (None, {}):
        errors.append(f"{label}: unverified publishers should not define a 'verification' object")

    return payload, errors


def load_publisher_profiles() -> tuple[dict[str, dict], list[str]]:
    profiles: dict[str, dict] = {}
    errors: list[str] = []

    for path in iter_publisher_profile_paths():
        payload, profile_errors = validate_publisher_profile(path)
        if profile_errors:
            errors.extend(profile_errors)
            continue
        publisher_id = payload["id"]
        if publisher_id in profiles:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: duplicate publisher id '{publisher_id}'")
            continue
        profiles[publisher_id] = payload

    return profiles, errors


def validate_org_policy(path: Path, publisher_profiles: dict[str, dict], known_skill_ids: set[str]) -> tuple[dict, list[str]]:
    payload = load_json(path)
    errors: list[str] = []
    label = path.relative_to(ROOT).as_posix()

    org_id = required_string(payload, "org_id", errors, label, min_length=3)
    required_string(payload, "display_name", errors, label, min_length=3)
    include_channels = required_list(payload, "include_channels", errors, label)
    allowed_publishers = required_list(payload, "allowed_publishers", errors, label)
    allowed_review_statuses = required_list(payload, "allowed_review_statuses", errors, label)
    allowed_lifecycle_statuses = required_list(payload, "allowed_lifecycle_statuses", errors, label)
    allowed_skills = required_list(payload, "allowed_skills", errors, label, allow_empty=True)
    blocked_skills = required_list(payload, "blocked_skills", errors, label, allow_empty=True)
    preferred_skills = required_list(payload, "preferred_skills", errors, label, allow_empty=True)
    featured_bundles = required_list(payload, "featured_bundles", errors, label, allow_empty=True)
    require_verified_publishers = payload.get("require_verified_publishers")

    if not isinstance(require_verified_publishers, bool):
        errors.append(f"{label}: 'require_verified_publishers' must be a boolean")
    if include_channels and any(channel not in MARKET_CHANNELS for channel in include_channels):
        errors.append(f"{label}: 'include_channels' contains unsupported values")
    if allowed_review_statuses and any(status not in REVIEW_STATUSES for status in allowed_review_statuses):
        errors.append(f"{label}: 'allowed_review_statuses' contains unsupported values")
    if allowed_lifecycle_statuses and any(status not in LIFECYCLE_STATUSES for status in allowed_lifecycle_statuses):
        errors.append(f"{label}: 'allowed_lifecycle_statuses' contains unsupported values")
    for publisher in allowed_publishers:
        if publisher not in publisher_profiles:
            errors.append(f"{label}: unknown publisher '{publisher}' in 'allowed_publishers'")
    for skill_id in allowed_skills + blocked_skills + preferred_skills:
        if skill_id not in known_skill_ids:
            errors.append(f"{label}: unknown skill id '{skill_id}'")
    if featured_bundles and any(len(bundle_id) < 3 for bundle_id in featured_bundles):
        errors.append(f"{label}: 'featured_bundles' contains unsupported values")
    if org_id and any(char.isspace() for char in org_id):
        errors.append(f"{label}: 'org_id' should not contain whitespace")

    return payload, errors


def validate_bundle_definition(path: Path, known_skill_ids: set[str]) -> tuple[dict, list[str]]:
    payload = load_json(path)
    errors: list[str] = []
    label = path.relative_to(ROOT).as_posix()

    bundle_id = required_string(payload, "id", errors, label, min_length=3)
    required_string(payload, "title", errors, label, min_length=3)
    required_string(payload, "summary", errors, label, min_length=20)
    required_string(payload, "description", errors, label, min_length=40)
    status = required_string(payload, "status", errors, label, min_length=5)
    channels = required_list(payload, "channels", errors, label)
    skills = required_list(payload, "skills", errors, label)
    required_list(payload, "use_cases", errors, label)
    required_list(payload, "keywords", errors, label)

    if bundle_id and " " in bundle_id:
        errors.append(f"{label}: 'id' should use a slug without spaces")
    if status and status not in BUNDLE_STATUSES:
        errors.append(f"{label}: unsupported bundle status '{status}'")
    if channels and any(channel not in MARKET_CHANNELS for channel in channels):
        errors.append(f"{label}: 'channels' contains unsupported values")
    for skill_id in skills:
        if skill_id not in known_skill_ids:
            errors.append(f"{label}: unknown skill id '{skill_id}'")

    return payload, errors


def load_bundle_definitions(known_skill_ids: set[str]) -> tuple[list[dict], list[str]]:
    bundles: list[dict] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in iter_bundle_paths():
        payload, bundle_errors = validate_bundle_definition(path, known_skill_ids)
        if bundle_errors:
            errors.extend(bundle_errors)
            continue
        bundle_id = payload["id"]
        if bundle_id in seen_ids:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: duplicate bundle id '{bundle_id}'")
            continue
        seen_ids.add(bundle_id)
        bundles.append(payload)

    bundles.sort(key=lambda item: item["title"].lower())
    return bundles, errors


def load_filtered_market_inputs(org_policy_path: Path | None = None) -> tuple[list[dict], list[dict], dict | None, list[str]]:
    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    errors = [*manifest_errors, *publisher_errors]
    policy_payload: dict | None = None

    if org_policy_path is not None:
        resolved_policy = org_policy_path if org_policy_path.is_absolute() else (ROOT / org_policy_path)
        if not resolved_policy.is_file():
            errors.append(f"missing org policy file: {resolved_policy}")
        else:
            policy_payload = load_json(resolved_policy)
            _, policy_errors = validate_org_policy(
                resolved_policy.resolve(),
                publisher_profiles,
                {manifest["id"] for manifest in manifests},
            )
            errors.extend(policy_errors)

    bundles, bundle_errors = load_bundle_definitions({manifest["id"] for manifest in manifests})
    errors.extend(bundle_errors)

    if errors:
        return [], [], None, errors

    if policy_payload is not None:
        manifests = filter_manifests_for_policy(manifests, policy_payload, publisher_profiles)

    manifest_ids = {manifest["id"] for manifest in manifests}
    featured_bundle_ids = set(policy_payload.get("featured_bundles", [])) if policy_payload else set()
    filtered_bundles: list[dict] = []
    for bundle in bundles:
        bundle_skill_ids = [skill_id for skill_id in bundle["skills"] if skill_id in manifest_ids]
        if not bundle_skill_ids:
            continue
        if policy_payload is not None and featured_bundle_ids and bundle["id"] not in featured_bundle_ids:
            continue
        filtered = dict(bundle)
        filtered["skills"] = bundle_skill_ids
        filtered_bundles.append(filtered)

    enriched = [enrich_manifest(manifest, publisher_profiles) for manifest in manifests]
    enriched.sort(key=lambda item: (item["channel"], item["title"].lower()))
    filtered_bundles.sort(key=lambda item: (item["id"] not in featured_bundle_ids, item["title"].lower()))
    return enriched, filtered_bundles, policy_payload, []


def load_channel_skill_lookup(market_dir: Path, channels: set[str] | None = None) -> tuple[dict[str, dict], list[str]]:
    requested_channels = channels or set(MARKET_CHANNELS)
    lookup: dict[str, dict] = {}
    errors: list[str] = []

    for channel in sorted(requested_channels):
        if channel not in MARKET_CHANNELS:
            errors.append(f"unsupported market channel '{channel}'")
            continue
        index_path = market_dir / "channels" / f"{channel}.json"
        if not index_path.is_file():
            errors.append(f"missing channel index: {index_path}")
            continue
        payload = load_json(index_path)
        skills = payload.get("skills", [])
        if not isinstance(skills, list):
            errors.append(f"{index_path}: 'skills' must be a list")
            continue
        for skill in skills:
            if not isinstance(skill, dict):
                errors.append(f"{index_path}: channel entries must be objects")
                continue
            skill_id = str(skill.get("id", "")).strip()
            if not skill_id:
                errors.append(f"{index_path}: channel entry is missing 'id'")
                continue
            lookup[skill_id] = skill

    return lookup, errors


def bundle_reports_dir(target_root: Path) -> Path:
    return resolve_target_root(target_root) / "bundle-reports"


def load_bundle_report(report_path: Path) -> dict:
    payload = load_json(report_path)
    results = payload.get("results")
    if not isinstance(results, list):
        payload["results"] = []
    return payload


def iter_bundle_report_paths(target_root: Path) -> list[Path]:
    reports_dir = bundle_reports_dir(target_root)
    if not reports_dir.is_dir():
        return []
    return sorted(reports_dir.glob("*.json"))


def resolve_bundle_report(target_root: Path, token: str) -> tuple[Path | None, dict | None, list[str]]:
    available: list[str] = []
    for candidate_path in iter_bundle_report_paths(target_root):
        candidate_payload = load_bundle_report(candidate_path)
        bundle_id = str(candidate_payload.get("bundle_id", candidate_path.stem))
        available.append(bundle_id)
        if match_bundle_token(candidate_payload, token) or candidate_path.stem.lower() == token.strip().lower():
            return candidate_path, candidate_payload, available
    return None, None, available


def reconcile_bundle_sources(
    target_root: Path,
    bundle_id: str,
    keep_skill_ids: set[str],
    *,
    apply_changes: bool,
) -> dict:
    resolved_root = resolve_target_root(target_root)
    lock_path, lock_payload = load_lock_payload(resolved_root)
    installed_entries = list(lock_payload.get("installed", []))

    removed_skill_ids: list[str] = []
    retained_skill_ids: list[str] = []
    updated_entries: dict[str, dict] = {}

    for entry in installed_entries:
        if not isinstance(entry, dict):
            continue
        skill_id = str(entry.get("skill_id", ""))
        if not skill_id:
            continue
        sources = normalize_install_sources(entry)
        if not any(item["kind"] == "bundle" and item["id"] == bundle_id for item in sources):
            continue
        if skill_id in keep_skill_ids:
            retained_skill_ids.append(skill_id)
            continue
        remaining_sources = remove_install_source(entry, "bundle", bundle_id)
        if remaining_sources:
            updated = dict(entry)
            updated["sources"] = remaining_sources
            updated_entries[skill_id] = updated
            retained_skill_ids.append(skill_id)
        else:
            removed_skill_ids.append(skill_id)

    final_installed: list[dict] = []
    for entry in installed_entries:
        skill_id = str(entry.get("skill_id", ""))
        if skill_id in removed_skill_ids:
            continue
        final_installed.append(updated_entries.get(skill_id, entry))

    if apply_changes:
        for skill_id in removed_skill_ids:
            entry = next(
                (item for item in installed_entries if isinstance(item, dict) and str(item.get("skill_id", "")) == skill_id),
                None,
            )
            skill_dir = resolved_root / str(entry.get("install_target", "")) if isinstance(entry, dict) else None
            if skill_dir and skill_dir.exists():
                for child in [skill_dir]:
                    shutil.rmtree(child)
        lock_payload["installed"] = final_installed
        write_lock_payload(lock_path, lock_payload)

    return {
        "lock_path": lock_path,
        "final_installed": final_installed,
        "removed_skill_ids": removed_skill_ids,
        "retained_skill_ids": retained_skill_ids,
    }


def collect_valid_manifests() -> tuple[list[dict], list[str]]:
    manifests: list[dict] = []
    errors: list[str] = []
    for path in iter_manifest_paths():
        payload, manifest_errors = validate_market_manifest(path)
        if manifest_errors:
            errors.extend(manifest_errors)
            continue
        manifests.append(payload)
    manifests.sort(key=lambda item: (item["channel"], item["title"].lower()))
    return manifests, errors


def enrich_manifest(payload: dict, publisher_profiles: dict[str, dict]) -> dict:
    enriched = json.loads(json.dumps(payload))
    publisher_profile = publisher_profiles.get(payload["publisher"], {})
    enriched["publisher_profile"] = {
        "display_name": publisher_profile.get("display_name", payload["publisher"]),
        "verified": publisher_profile.get("verified", False),
        "trust_level": publisher_profile.get("trust_level", "community"),
        "homepage": publisher_profile.get("homepage", ""),
        "contact_email": publisher_profile.get("contact_email", ""),
        "verification": publisher_profile.get("verification", {}),
    }
    return enriched


def filter_manifests_for_policy(
    manifests: list[dict],
    policy: dict,
    publisher_profiles: dict[str, dict],
) -> list[dict]:
    filtered: list[dict] = []
    allowed_skills = set(policy.get("allowed_skills", []))
    blocked_skills = set(policy.get("blocked_skills", []))
    preferred = set(policy.get("preferred_skills", []))
    allowed_publishers = set(policy.get("allowed_publishers", []))
    include_channels = set(policy.get("include_channels", []))
    allowed_review_statuses = set(policy.get("allowed_review_statuses", []))
    allowed_lifecycle_statuses = set(policy.get("allowed_lifecycle_statuses", []))
    require_verified = bool(policy.get("require_verified_publishers", False))

    for manifest in manifests:
        if manifest["channel"] not in include_channels:
            continue
        if manifest["quality"]["review_status"] not in allowed_review_statuses:
            continue
        if manifest["lifecycle"]["status"] not in allowed_lifecycle_statuses:
            continue
        if manifest["id"] in blocked_skills:
            continue
        if manifest["publisher"] not in allowed_publishers and manifest["id"] not in allowed_skills:
            continue
        publisher_profile = publisher_profiles.get(manifest["publisher"], {})
        if require_verified and not publisher_profile.get("verified", False):
            continue
        filtered.append(manifest)

    filtered.sort(
        key=lambda item: (
            item["id"] not in preferred,
            item["channel"],
            item["title"].lower(),
        )
    )
    return filtered


def build_source_file_checksums(source_dir: Path) -> list[dict]:
    return [
        {
            "path": repo_relative_path(file_path),
            "sha256": sha256_for_file(file_path),
        }
        for file_path in iter_skill_source_files(source_dir)
    ]


def hash_file_checksum_entries(entries: list[dict]) -> str:
    joined = "\n".join(f"{entry['path']}:{entry['sha256']}" for entry in entries)
    return sha256_for_bytes(joined.encode("utf-8"))


def build_provenance_payload(manifest: dict, package_path: Path, package_checksum: str) -> dict:
    source_dir = ROOT / manifest["artifacts"]["source_dir"]
    manifest_path = source_dir / "market" / "skill.json"
    file_checksums = build_source_file_checksums(source_dir)
    lifecycle = manifest["lifecycle"]
    return {
        "attestation_format": "moyuan-skill-provenance@v1",
        "skill_id": manifest["id"],
        "skill_name": manifest["name"],
        "publisher": manifest["publisher"],
        "version": manifest["version"],
        "channel": manifest["channel"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "builder": "scripts/package_skill.py",
        "manifest_path": repo_relative_path(manifest_path),
        "source_dir": repo_relative_path(source_dir),
        "manifest_checksum_sha256": sha256_for_file(manifest_path),
        "source_tree_checksum_sha256": hash_file_checksum_entries(file_checksums),
        "package": {
            "path": repo_relative_path(package_path),
            "checksum_sha256": package_checksum,
            "size_bytes": package_path.stat().st_size,
        },
        "quality": {
            "checker": manifest["quality"]["checker"],
            "eval": manifest["quality"]["eval"],
            "review_status": manifest["quality"]["review_status"],
        },
        "lifecycle": {
            "status": lifecycle["status"],
            "replacement_skill_id": lifecycle.get("replacement_skill_id", ""),
            "sunset_at": lifecycle.get("sunset_at", ""),
            "notes": lifecycle.get("notes", ""),
        },
        "files": file_checksums,
    }


def verify_provenance_against_install_spec(
    provenance: dict,
    install_spec: dict,
    label: str,
    *,
    expected_package_path: str | None = None,
) -> list[str]:
    errors: list[str] = []
    package = provenance.get("package", {})
    lifecycle = provenance.get("lifecycle", {})
    quality = provenance.get("quality", {})
    package_path = expected_package_path or str(install_spec.get("package_path", ""))

    if provenance.get("skill_id") != install_spec.get("skill_id"):
        errors.append(f"{label}: provenance skill_id does not match install spec")
    if provenance.get("skill_name") != install_spec.get("skill_name"):
        errors.append(f"{label}: provenance skill_name does not match install spec")
    if provenance.get("publisher") != install_spec.get("publisher"):
        errors.append(f"{label}: provenance publisher does not match install spec")
    if provenance.get("version") != install_spec.get("version"):
        errors.append(f"{label}: provenance version does not match install spec")
    if provenance.get("channel") != install_spec.get("channel"):
        errors.append(f"{label}: provenance channel does not match install spec")
    if package.get("path") != package_path:
        errors.append(f"{label}: provenance package path does not match install spec")
    if package.get("checksum_sha256") != install_spec.get("checksum_sha256"):
        errors.append(f"{label}: provenance package checksum does not match install spec")
    if lifecycle.get("status") != install_spec.get("lifecycle_status"):
        errors.append(f"{label}: provenance lifecycle status does not match install spec")
    if quality.get("review_status") != install_spec.get("review_status"):
        errors.append(f"{label}: provenance review status does not match install spec")
    return errors


def manifest_summary(payload: dict, output_dir: Path, publisher_profiles: dict[str, dict] | None = None) -> dict:
    install_spec_path = output_dir / "install" / f"{payload['name']}-{payload['version']}.json"
    provenance_path = output_dir / "provenance" / f"{payload['name']}-{payload['version']}.json"
    publisher_profile = (publisher_profiles or {}).get(payload["publisher"], {})
    return {
        "id": payload["id"],
        "name": payload["name"],
        "title": payload["title"],
        "publisher": payload["publisher"],
        "publisher_display_name": publisher_profile.get("display_name", payload["publisher"]),
        "publisher_verified": publisher_profile.get("verified", False),
        "trust_level": publisher_profile.get("trust_level", "community"),
        "channel": payload["channel"],
        "version": payload["version"],
        "summary": payload["summary"],
        "categories": payload["categories"],
        "tags": payload["tags"],
        "capabilities": payload["distribution"]["capabilities"],
        "starter_bundle_ids": payload["distribution"]["starter_bundle_ids"],
        "install_spec": repo_relative_path(install_spec_path),
        "install_available": install_spec_path.is_file(),
        "provenance_path": repo_relative_path(provenance_path),
        "provenance_available": provenance_path.is_file(),
        "review_status": payload["quality"]["review_status"],
        "lifecycle_status": payload["lifecycle"]["status"],
        "replacement_skill_id": payload["lifecycle"].get("replacement_skill_id", ""),
    }


def channel_index_payload(
    channel: str,
    manifests: list[dict],
    output_dir: Path,
    publisher_profiles: dict[str, dict] | None = None,
) -> dict:
    return {
        "channel": channel,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skills": [
            manifest_summary(payload, output_dir, publisher_profiles)
            for payload in manifests
            if payload["channel"] == channel
        ],
    }


def aggregate_index_payload(manifests: list[dict], output_dir: Path) -> dict:
    lifecycle_counts = {
        status: sum(1 for payload in manifests if payload["lifecycle"]["status"] == status)
        for status in sorted(LIFECYCLE_STATUSES)
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(manifests),
        "lifecycle_counts": lifecycle_counts,
        "channels": {
            channel: {
                "count": sum(1 for payload in manifests if payload["channel"] == channel),
                "path": repo_relative_path(output_dir / "channels" / f"{channel}.json"),
            }
            for channel in sorted(MARKET_CHANNELS)
        },
    }
