#!/usr/bin/env python3
"""Install a skill from a hosted remote registry URL."""

from __future__ import annotations

import argparse
from pathlib import Path

import install_skill
from market_utils import ROOT, resolve_target_root
from remote_registry_utils import DEFAULT_REMOTE_CACHE, RemoteRegistryError, stage_remote_skill_install


DEFAULT_TARGET = ROOT / "dist" / "installed-skills"


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
    parser = argparse.ArgumentParser(description="Install a skill directly from a remote hosted registry.")
    parser.add_argument("skill", help="Remote skill id or skill name.")
    parser.add_argument("--registry", required=True, help="Hosted registry base URL or registry.json URL.")
    parser.add_argument("--channel", default="stable", help="Remote release channel to resolve. Defaults to stable.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_REMOTE_CACHE, help="Cache directory for downloaded remote artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve and verify the remote install without extracting files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        staged = stage_remote_skill_install(
            args.skill,
            args.registry,
            channel=args.channel,
            cache_root=args.cache_root,
        )
    except RemoteRegistryError as error:
        print(f"RECOVERY_KIND: {infer_remote_error_kind(str(error))}")
        print(f"ERROR: {error}")
        return 1

    target_root = resolve_target_root(args.target_root)
    source_id = f"{staged.registry_url}#{staged.resolved_channel}"
    print(
        f"Resolved remote skill {staged.summary['id']} from {staged.registry_url} "
        f"({staged.resolved_channel})"
    )
    print(f"Staged install spec: {staged.staged_install_spec_path}")
    print(f"Cached package: {staged.package_path}")
    print(f"Cached provenance: {staged.provenance_path}")

    forwarded_args = [
        str(staged.staged_install_spec_path),
        "--target-root",
        str(target_root),
        "--source-kind",
        "registry",
        "--source-id",
        source_id,
    ]
    if args.dry_run:
        forwarded_args.append("--dry-run")
    return install_skill.main(forwarded_args)


if __name__ == "__main__":
    raise SystemExit(main())
