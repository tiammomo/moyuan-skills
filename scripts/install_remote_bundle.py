#!/usr/bin/env python3
"""Install a starter bundle directly from a hosted remote registry URL."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import install_skill
from market_utils import dump_json, resolve_target_root
from remote_registry_utils import (
    DEFAULT_REMOTE_CACHE,
    RemoteRegistryClient,
    RemoteRegistryError,
    resolve_remote_bundle_payload,
    stage_remote_skill_install,
)


DEFAULT_TARGET = Path("dist/installed-skills")


def infer_remote_error_kind(message: str) -> str:
    lowered = message.lower()
    if (
        "checksum mismatch" in lowered
        or "provenance" in lowered
        or "blocked" in lowered
        or "archived" in lowered
        or "human review" in lowered
        or "not installable" in lowered
    ):
        return "trust"
    return "download"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install a starter bundle directly from a hosted remote registry.")
    parser.add_argument("bundle", help="Remote bundle id or title.")
    parser.add_argument("--registry", required=True, help="Hosted registry base URL or registry.json URL.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_REMOTE_CACHE, help="Cache directory for downloaded remote artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve and verify the bundle install without extracting files.")
    return parser


def _result_entry(
    *,
    skill_id: str,
    title: str,
    version: str,
    channel: str,
    lifecycle_status: str,
    install_spec: str,
    status: str,
    reason: str = "",
    registry_url: str = "",
) -> dict:
    return {
        "skill_id": skill_id,
        "title": title,
        "version": version,
        "channel": channel,
        "lifecycle_status": lifecycle_status,
        "install_spec": install_spec,
        "status": status,
        "reason": reason,
        "registry_url": registry_url,
    }


def _bundle_skill_fields(item: object) -> tuple[str, str, str]:
    if isinstance(item, dict):
        skill_id = str(item.get("id", "")).strip()
        channel = str(item.get("channel", "")).strip()
        lifecycle_status = str(item.get("lifecycle_status", "")).strip()
        return skill_id, channel, lifecycle_status
    return str(item).strip(), "", ""


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        client = RemoteRegistryClient(args.registry)
        bundle = resolve_remote_bundle_payload(client, args.bundle)
    except RemoteRegistryError as error:
        print(f"RECOVERY_KIND: {infer_remote_error_kind(str(error))}")
        print(f"ERROR: {error}")
        return 1

    target_root = resolve_target_root(args.target_root)
    cache_root = resolve_target_root(args.cache_root)
    bundle_channels = [
        str(item).strip()
        for item in bundle.get("channels", [])
        if isinstance(item, str) and str(item).strip()
    ]
    if not bundle_channels:
        bundle_channels = ["stable"]

    report = {
        "bundle_id": str(bundle.get("id", args.bundle)).strip(),
        "title": str(bundle.get("title", args.bundle)).strip(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run" if args.dry_run else "install",
        "registry_url": client.registry_url,
        "target_root": str(target_root),
        "cache_root": str(cache_root),
        "results": [],
    }

    unexpected_failures = False
    skills = bundle.get("skills", [])
    if not isinstance(skills, list):
        print("ERROR: remote bundle payload is missing the 'skills' list")
        return 1

    print(f"Processing remote bundle {report['bundle_id']} ({len(skills)} skill(s)) from {client.registry_url}")
    for item in skills:
        skill_id, preferred_channel, lifecycle_status = _bundle_skill_fields(item)
        if not skill_id:
            report["results"].append(
                _result_entry(
                    skill_id="",
                    title="",
                    version="",
                    channel="",
                    lifecycle_status="",
                    install_spec="",
                    status="failed",
                    reason="bundle member is missing a skill id",
                    registry_url=client.registry_url,
                )
            )
            unexpected_failures = True
            continue

        if lifecycle_status in {"blocked", "archived"}:
            reason = f"lifecycle status '{lifecycle_status}' is not installable"
            report["results"].append(
                _result_entry(
                    skill_id=skill_id,
                    title=skill_id,
                    version="",
                    channel=preferred_channel,
                    lifecycle_status=lifecycle_status,
                    install_spec="",
                    status="skipped",
                    reason=reason,
                    registry_url=client.registry_url,
                )
            )
            print(f"SKIPPED: {skill_id} ({reason})")
            continue

        candidate_channels: list[str] = []
        if preferred_channel:
            candidate_channels.append(preferred_channel)
        candidate_channels.extend(bundle_channels)
        ordered_channels: list[str] = []
        for candidate_channel in candidate_channels:
            if candidate_channel and candidate_channel not in ordered_channels:
                ordered_channels.append(candidate_channel)

        try:
            staged = stage_remote_skill_install(
                skill_id,
                client.registry_url,
                channels=ordered_channels,
                cache_root=cache_root,
                client=client,
            )
        except RemoteRegistryError as error:
            print(f"RECOVERY_KIND: {infer_remote_error_kind(str(error))}")
            report["results"].append(
                _result_entry(
                    skill_id=skill_id,
                    title=skill_id,
                    version="",
                    channel=preferred_channel,
                    lifecycle_status=lifecycle_status,
                    install_spec="",
                    status="failed",
                    reason=str(error),
                    registry_url=client.registry_url,
                )
            )
            print(f"FAILED: {skill_id} ({error})")
            unexpected_failures = True
            continue

        staged_lifecycle = str(staged.summary.get("lifecycle_status", "")).strip()
        if staged_lifecycle in {"blocked", "archived"}:
            reason = f"lifecycle status '{staged_lifecycle}' is not installable"
            report["results"].append(
                _result_entry(
                    skill_id=str(staged.summary["id"]),
                    title=str(staged.summary["title"]),
                    version=str(staged.summary["version"]),
                    channel=staged.resolved_channel,
                    lifecycle_status=staged_lifecycle,
                    install_spec=str(staged.staged_install_spec_path),
                    status="skipped",
                    reason=reason,
                    registry_url=client.registry_url,
                )
            )
            print(f"SKIPPED: {staged.summary['id']} ({reason})")
            continue

        forwarded_args = [
            str(staged.staged_install_spec_path),
            "--target-root",
            str(target_root),
            "--source-kind",
            "bundle",
            "--source-id",
            report["bundle_id"],
        ]
        if args.dry_run:
            forwarded_args.append("--dry-run")
        exit_code = install_skill.main(forwarded_args)
        if exit_code == 0:
            report["results"].append(
                _result_entry(
                    skill_id=str(staged.summary["id"]),
                    title=str(staged.summary["title"]),
                    version=str(staged.summary["version"]),
                    channel=staged.resolved_channel,
                    lifecycle_status=staged_lifecycle or str(item.get("lifecycle_status", "") if isinstance(item, dict) else ""),
                    install_spec=str(staged.staged_install_spec_path),
                    status="planned" if args.dry_run else "installed",
                    registry_url=client.registry_url,
                )
            )
        else:
            report["results"].append(
                _result_entry(
                    skill_id=str(staged.summary["id"]),
                    title=str(staged.summary["title"]),
                    version=str(staged.summary["version"]),
                    channel=staged.resolved_channel,
                    lifecycle_status=staged_lifecycle,
                    install_spec=str(staged.staged_install_spec_path),
                    status="failed",
                    reason="install command returned a non-zero exit code",
                    registry_url=client.registry_url,
                )
            )
            print(f"FAILED: {staged.summary['id']} (install command returned a non-zero exit code)")
            unexpected_failures = True

    counts = Counter(result["status"] for result in report["results"])
    print(
        f"Remote bundle {report['bundle_id']} summary: "
        f"installed={counts.get('installed', 0)} "
        f"planned={counts.get('planned', 0)} "
        f"skipped={counts.get('skipped', 0)} "
        f"failed={counts.get('failed', 0)}"
    )

    if not args.dry_run:
        report_path = target_root / "bundle-reports" / f"{report['bundle_id']}.json"
        dump_json(report_path, report)
        print(f"Bundle report: {report_path}")

    return 1 if unexpected_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
