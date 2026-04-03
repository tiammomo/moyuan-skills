#!/usr/bin/env python3
"""Helpers for fetching and staging remote skills market registry artifacts."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from market_utils import (
    ROOT,
    dump_json,
    load_json,
    repo_relative_path,
    resolve_target_root,
    sha256_for_bytes,
    sha256_for_file,
    validate_install_spec_payload,
    validate_provenance_payload,
    verify_provenance_against_install_spec,
)


DEFAULT_REMOTE_CACHE = ROOT / "dist" / "remote-registry-cache"
USER_AGENT = "moyuan-skills-remote-installer/0.1"
DEFAULT_TIMEOUT_SECONDS = 20.0
REMOTE_CHANNEL_ORDER = ("stable", "beta", "internal")


class RemoteRegistryError(RuntimeError):
    """Raised when a remote registry lookup or download fails."""


@dataclass
class RemoteSkillStage:
    registry_url: str
    resolved_channel: str
    summary: dict
    staged_install_spec_path: Path
    raw_install_spec_path: Path
    package_path: Path
    provenance_path: Path
    upstream_install_spec_url: str
    upstream_package_url: str
    upstream_provenance_url: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_registry_url(registry_url: str) -> str:
    value = registry_url.strip()
    if not value:
        raise RemoteRegistryError("registry URL must be a non-empty string")
    return value.rstrip("/")


def _repo_cache_root(cache_root: Path | None) -> Path:
    resolved = resolve_target_root(cache_root or DEFAULT_REMOTE_CACHE).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:  # pragma: no cover - defensive path
        raise RemoteRegistryError(f"cache root must stay inside the repository: {resolved}") from exc
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _is_remote_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _url_for(base_url: str, reference: str) -> str:
    if not reference:
        raise RemoteRegistryError("remote reference must be a non-empty string")
    if _is_remote_url(reference):
        return reference
    return urllib.parse.urljoin(f"{base_url.rstrip('/')}/", reference.lstrip("/"))


def _fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
        return response.read()


def _format_fetch_error(url: str, error: Exception) -> str:
    if isinstance(error, urllib.error.HTTPError):
        return f"{url} -> HTTP {error.code}"
    if isinstance(error, urllib.error.URLError):
        return f"{url} -> {error.reason}"
    return f"{url} -> {error}"


class RemoteRegistryClient:
    def __init__(self, registry_url: str) -> None:
        self.registry_url = _normalize_registry_url(registry_url)
        self.base_url = self.registry_url
        self.registry_metadata: dict | None = None
        self._index_payload: dict | None = None
        self._index_url: str | None = None
        self._channel_cache: dict[str, dict] = {}
        self._channel_urls: dict[str, str] = {}
        self._bundles_payload: dict | None = None
        self._bundles_url: str | None = None
        self._load_registry_metadata()

    def _load_registry_metadata(self) -> None:
        direct_registry_url = self.registry_url if self.registry_url.endswith(".json") else ""
        candidate_urls = [direct_registry_url] if direct_registry_url else []
        if not direct_registry_url:
            candidate_urls.append(_url_for(self.registry_url, "registry.json"))

        for candidate_url in candidate_urls:
            try:
                payload = json.loads(_fetch_bytes(candidate_url).decode("utf-8"))
            except Exception:
                continue
            if isinstance(payload, dict) and payload.get("format") == "moyuan-skills-hosted-registry@v1":
                self.registry_metadata = payload
                if candidate_url.endswith(".json"):
                    self.base_url = candidate_url.rsplit("/", 1)[0]
                return

        if self.registry_url.endswith(".json"):
            self.base_url = self.registry_url.rsplit("/", 1)[0]

    def _public_reference(self, key: str, default: str) -> str:
        public = self.registry_metadata.get("public", {}) if isinstance(self.registry_metadata, dict) else {}
        value = public.get(key)
        return str(value).strip() if isinstance(value, str) and value.strip() else default

    def _fetch_json_candidates(self, references: list[str]) -> tuple[dict, str]:
        attempts: list[str] = []
        for reference in references:
            if not reference:
                continue
            url = _url_for(self.base_url, reference)
            try:
                payload = json.loads(_fetch_bytes(url).decode("utf-8"))
            except Exception as error:
                attempts.append(_format_fetch_error(url, error))
                continue
            if not isinstance(payload, dict):
                attempts.append(f"{url} -> JSON root must be an object")
                continue
            return payload, url
        joined = "; ".join(attempts) if attempts else "no remote candidates were available"
        raise RemoteRegistryError(f"unable to fetch remote JSON payload ({joined})")

    def _download_candidates(self, references: list[str], destination: Path) -> tuple[Path, str]:
        attempts: list[str] = []
        for reference in references:
            if not reference:
                continue
            url = _url_for(self.base_url, reference)
            try:
                payload = _fetch_bytes(url)
            except Exception as error:
                attempts.append(_format_fetch_error(url, error))
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
            return destination, url
        joined = "; ".join(attempts) if attempts else "no remote candidates were available"
        raise RemoteRegistryError(f"unable to download remote artifact ({joined})")

    def load_index_document(self) -> tuple[dict, str]:
        if self._index_payload is None or self._index_url is None:
            index_reference = self._public_reference("index", "index.json")
            self._index_payload, self._index_url = self._fetch_json_candidates([index_reference, "index.json"])
        return self._index_payload, self._index_url

    def load_index(self) -> dict:
        return self.load_index_document()[0]

    def load_channel_index_document(self, channel: str) -> tuple[dict, str]:
        if channel in self._channel_cache and channel in self._channel_urls:
            return self._channel_cache[channel], self._channel_urls[channel]
        index_payload = self.load_index()
        channel_payload = index_payload.get("channels", {}).get(channel, {})
        references = []
        if isinstance(channel_payload, dict):
            candidate = channel_payload.get("path")
            if isinstance(candidate, str) and candidate.strip():
                references.append(candidate)
        references.append(f"channels/{channel}.json")
        payload, url = self._fetch_json_candidates(references)
        self._channel_cache[channel] = payload
        self._channel_urls[channel] = url
        return payload, url

    def load_channel_index(self, channel: str) -> dict:
        return self.load_channel_index_document(channel)[0]

    def load_bundles_document(self) -> tuple[dict, str]:
        if self._bundles_payload is None or self._bundles_url is None:
            bundles_reference = self._public_reference("bundles", "recommendations/bundles.json")
            self._bundles_payload, self._bundles_url = self._fetch_json_candidates([bundles_reference, "recommendations/bundles.json"])
        return self._bundles_payload, self._bundles_url

    def load_bundles(self) -> dict:
        return self.load_bundles_document()[0]

    def install_dir_reference(self) -> str:
        return self._public_reference("install_dir", "install")

    def packages_dir_reference(self) -> str:
        return self._public_reference("packages_dir", "packages")

    def provenance_dir_reference(self) -> str:
        return self._public_reference("provenance_dir", "provenance")


def _match_skill_summary(summary: dict, token: str) -> bool:
    lowered = token.strip().lower()
    return lowered in {
        str(summary.get("id", "")).strip().lower(),
        str(summary.get("name", "")).strip().lower(),
    }


def _channel_sort_key(channel: str) -> tuple[int, str]:
    try:
        return REMOTE_CHANNEL_ORDER.index(channel), channel
    except ValueError:
        return len(REMOTE_CHANNEL_ORDER), channel


def ordered_remote_channels(index_payload: dict) -> list[str]:
    raw_channels = index_payload.get("channels", {})
    if not isinstance(raw_channels, dict):
        return []
    channels = [
        str(channel).strip()
        for channel in raw_channels.keys()
        if str(channel).strip()
    ]
    return sorted(dict.fromkeys(channels), key=_channel_sort_key)


def build_remote_registry_profile(client: RemoteRegistryClient) -> dict:
    metadata = client.registry_metadata if isinstance(client.registry_metadata, dict) else {}
    public = metadata.get("public", {}) if isinstance(metadata.get("public", {}), dict) else {}
    orgs = metadata.get("orgs", []) if isinstance(metadata.get("orgs", []), list) else []
    return {
        "registry_url": client.registry_url,
        "registry_base_url": client.base_url,
        "has_registry_metadata": bool(metadata),
        "format": str(metadata.get("format", "")).strip(),
        "generated_at": str(metadata.get("generated_at", "")).strip(),
        "public": public,
        "org_count": len(orgs),
        "orgs": orgs,
    }


def load_remote_registry_catalog(client: RemoteRegistryClient) -> dict:
    index_payload, index_url = client.load_index_document()
    bundles_payload, bundles_url = client.load_bundles_document()
    channels_payload = index_payload.get("channels", {}) if isinstance(index_payload.get("channels", {}), dict) else {}
    bundles = bundles_payload.get("bundles", []) if isinstance(bundles_payload.get("bundles", []), list) else []

    return {
        "registry": build_remote_registry_profile(client),
        "index_url": index_url,
        "index": index_payload,
        "channels": [
            {
                "channel": channel,
                "count": int(channels_payload.get(channel, {}).get("count", 0))
                if isinstance(channels_payload.get(channel, {}), dict)
                else 0,
                "path": str(channels_payload.get(channel, {}).get("path", "")).strip()
                if isinstance(channels_payload.get(channel, {}), dict)
                else "",
            }
            for channel in ordered_remote_channels(index_payload)
        ],
        "bundles_url": bundles_url,
        "bundle_count": len(bundles),
        "bundles": bundles,
    }


def inspect_remote_skill_payload(
    client: RemoteRegistryClient,
    token: str,
    *,
    channel: str = "",
    channels: list[str] | None = None,
) -> dict:
    index_payload = client.load_index()
    candidate_channels = [item.strip() for item in (channels or []) if str(item).strip()]
    if channel.strip():
        candidate_channels.insert(0, channel.strip())
    if not candidate_channels:
        candidate_channels = ordered_remote_channels(index_payload)
    summary, resolved_channel = resolve_remote_skill_summary(client, token, candidate_channels)
    install_spec, install_spec_url = client._fetch_json_candidates(_build_install_spec_references(client, summary))
    provenance, provenance_url = client._fetch_json_candidates(_build_provenance_references(client, install_spec, summary))
    package_path = str(install_spec.get("package_path", "")).strip()
    return {
        "registry": build_remote_registry_profile(client),
        "resolved_channel": resolved_channel,
        "skill": summary,
        "install_spec": install_spec,
        "install_spec_url": install_spec_url,
        "provenance": provenance,
        "provenance_url": provenance_url,
        "package_url": _url_for(client.base_url, package_path) if package_path else "",
    }


def inspect_remote_bundle_payload(client: RemoteRegistryClient, token: str) -> dict:
    bundle = resolve_remote_bundle_payload(client, token)
    _, bundles_url = client.load_bundles_document()
    return {
        "registry": build_remote_registry_profile(client),
        "bundle": bundle,
        "bundles_url": bundles_url,
    }


def resolve_remote_skill_summary(client: RemoteRegistryClient, token: str, channels: list[str]) -> tuple[dict, str]:
    available_tokens: list[str] = []
    for channel in channels:
        channel_payload = client.load_channel_index(channel)
        skills = channel_payload.get("skills", [])
        if not isinstance(skills, list):
            continue
        for summary in skills:
            if not isinstance(summary, dict):
                continue
            available_tokens.extend(
                value
                for value in [str(summary.get("id", "")).strip(), str(summary.get("name", "")).strip()]
                if value
            )
            if _match_skill_summary(summary, token):
                return summary, channel
    available = ", ".join(sorted(dict.fromkeys(available_tokens)))
    raise RemoteRegistryError(
        f"could not find remote skill '{token}' in channels {channels}. "
        f"Available ids/names: {available or 'none'}"
    )


def resolve_remote_bundle_payload(client: RemoteRegistryClient, token: str) -> dict:
    bundles_payload = client.load_bundles()
    bundles = bundles_payload.get("bundles", [])
    if not isinstance(bundles, list):
        raise RemoteRegistryError("remote bundles payload is missing the 'bundles' list")
    lowered = token.strip().lower()
    available: list[str] = []
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        bundle_id = str(bundle.get("id", "")).strip()
        title = str(bundle.get("title", "")).strip()
        if bundle_id:
            available.append(bundle_id)
        if lowered in {bundle_id.lower(), title.lower()}:
            return bundle
    raise RemoteRegistryError(
        f"could not find remote bundle '{token}'. Available bundles: {', '.join(sorted(dict.fromkeys(available))) or 'none'}"
    )


def _required_string(payload: dict, key: str, *, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RemoteRegistryError(f"{label}: missing required string field '{key}'")
    return value.strip()


def _skill_cache_dir(cache_root: Path, registry_url: str, skill_name: str, version: str) -> Path:
    registry_hash = sha256_for_bytes(registry_url.encode("utf-8"))[:16]
    return cache_root / registry_hash / f"{skill_name}-{version}"


def _build_install_spec_references(client: RemoteRegistryClient, summary: dict) -> list[str]:
    references: list[str] = []
    candidate = summary.get("install_spec")
    if isinstance(candidate, str) and candidate.strip():
        references.append(candidate.strip())
    references.append(f"{client.install_dir_reference().strip('/')}/{summary['name']}-{summary['version']}.json")
    return references


def _build_package_references(client: RemoteRegistryClient, install_spec: dict, summary: dict) -> list[str]:
    references: list[str] = []
    candidate = install_spec.get("package_path")
    if isinstance(candidate, str) and candidate.strip():
        references.append(candidate.strip())
        references.append(f"{client.packages_dir_reference().strip('/')}/{Path(candidate).name}")
    references.append(f"{client.packages_dir_reference().strip('/')}/{summary['name']}-{summary['version']}.zip")
    return references


def _build_provenance_references(client: RemoteRegistryClient, install_spec: dict, summary: dict) -> list[str]:
    references: list[str] = []
    candidate = install_spec.get("provenance_path")
    if isinstance(candidate, str) and candidate.strip():
        references.append(candidate.strip())
        references.append(f"{client.provenance_dir_reference().strip('/')}/{Path(candidate).name}")
    references.append(f"{client.provenance_dir_reference().strip('/')}/{summary['name']}-{summary['version']}.json")
    return references


def stage_remote_skill_install(
    skill_token: str,
    registry_url: str,
    *,
    channel: str = "stable",
    channels: list[str] | None = None,
    cache_root: Path | None = None,
    client: RemoteRegistryClient | None = None,
) -> RemoteSkillStage:
    remote_client = client or RemoteRegistryClient(registry_url)
    requested_channels = [item.strip() for item in (channels or [channel]) if str(item).strip()]
    if not requested_channels:
        requested_channels = ["stable"]
    summary, resolved_channel = resolve_remote_skill_summary(remote_client, skill_token, requested_channels)
    skill_name = _required_string(summary, "name", label=f"remote skill {skill_token}")
    version = _required_string(summary, "version", label=f"remote skill {skill_token}")
    cache_dir = _skill_cache_dir(_repo_cache_root(cache_root), remote_client.registry_url, skill_name, version)
    raw_dir = cache_dir / "downloads"
    staged_dir = cache_dir / "staged"

    raw_install_spec, install_spec_url = remote_client._fetch_json_candidates(_build_install_spec_references(remote_client, summary))
    raw_install_spec_path = raw_dir / "install" / f"{skill_name}-{version}.json"
    dump_json(raw_install_spec_path, raw_install_spec)

    upstream_package_path = _required_string(raw_install_spec, "package_path", label=f"remote install spec {skill_name}")
    upstream_provenance_path = _required_string(raw_install_spec, "provenance_path", label=f"remote install spec {skill_name}")

    package_path, package_url = remote_client._download_candidates(
        _build_package_references(remote_client, raw_install_spec, summary),
        raw_dir / "packages" / f"{skill_name}-{version}.zip",
    )
    provenance_path, provenance_url = remote_client._download_candidates(
        _build_provenance_references(remote_client, raw_install_spec, summary),
        raw_dir / "provenance" / f"{skill_name}-{version}.json",
    )

    expected_package_checksum = _required_string(
        raw_install_spec,
        "checksum_sha256",
        label=f"remote install spec {skill_name}",
    )
    actual_package_checksum = sha256_for_file(package_path)
    if actual_package_checksum != expected_package_checksum:
        raise RemoteRegistryError(
            f"checksum mismatch for remote package {package_url}: "
            f"expected {expected_package_checksum}, got {actual_package_checksum}"
        )

    expected_provenance_checksum = _required_string(
        raw_install_spec,
        "provenance_sha256",
        label=f"remote install spec {skill_name}",
    )
    actual_provenance_checksum = sha256_for_file(provenance_path)
    if actual_provenance_checksum != expected_provenance_checksum:
        raise RemoteRegistryError(
            f"checksum mismatch for remote provenance {provenance_url}: "
            f"expected {expected_provenance_checksum}, got {actual_provenance_checksum}"
        )

    provenance_payload = load_json(provenance_path)
    provenance_label = repo_relative_path(provenance_path)
    provenance_errors = validate_provenance_payload(provenance_payload, provenance_label, require_local_paths=False)
    provenance_errors.extend(
        verify_provenance_against_install_spec(
            provenance_payload,
            raw_install_spec,
            provenance_label,
            expected_package_path=upstream_package_path,
        )
    )
    if provenance_errors:
        raise RemoteRegistryError("\n".join(provenance_errors))

    staged_install_spec = dict(raw_install_spec)
    staged_install_spec["package_path"] = repo_relative_path(package_path)
    staged_install_spec["provenance_path"] = repo_relative_path(provenance_path)
    staged_install_spec["remote_source"] = {
        "registry_url": remote_client.registry_url,
        "registry_base_url": remote_client.base_url,
        "resolved_channel": resolved_channel,
        "upstream_install_spec_url": install_spec_url,
        "upstream_package_url": package_url,
        "upstream_provenance_url": provenance_url,
        "upstream_package_path": upstream_package_path,
        "upstream_provenance_path": upstream_provenance_path,
        "raw_install_spec_path": repo_relative_path(raw_install_spec_path),
        "cached_package_path": repo_relative_path(package_path),
        "cached_provenance_path": repo_relative_path(provenance_path),
        "downloaded_at": _utc_now(),
    }
    staged_install_spec_path = staged_dir / "install" / f"{skill_name}-{version}.json"
    dump_json(staged_install_spec_path, staged_install_spec)

    install_errors = validate_install_spec_payload(staged_install_spec, repo_relative_path(staged_install_spec_path))
    if install_errors:
        raise RemoteRegistryError("\n".join(install_errors))

    return RemoteSkillStage(
        registry_url=remote_client.registry_url,
        resolved_channel=resolved_channel,
        summary=summary,
        staged_install_spec_path=staged_install_spec_path,
        raw_install_spec_path=raw_install_spec_path,
        package_path=package_path,
        provenance_path=provenance_path,
        upstream_install_spec_url=install_spec_url,
        upstream_package_url=package_url,
        upstream_provenance_url=provenance_url,
    )
