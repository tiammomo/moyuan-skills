#!/usr/bin/env python3
"""Inspect one remote skill from a hosted registry without installing it."""

from __future__ import annotations

import argparse
import json

from remote_registry_utils import RemoteRegistryClient, RemoteRegistryError, inspect_remote_skill_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect one remote skill from a hosted registry.")
    parser.add_argument("skill", help="Remote skill id or skill name.")
    parser.add_argument("--registry", required=True, help="Hosted registry base URL or registry.json URL.")
    parser.add_argument("--channel", default="", help="Optional preferred channel when resolving the remote skill.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = inspect_remote_skill_payload(
            RemoteRegistryClient(args.registry),
            args.skill,
            channel=args.channel.strip(),
        )
    except RemoteRegistryError as error:
        print(f"ERROR: {error}")
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    skill = payload["skill"]
    install_spec = payload["install_spec"]
    provenance = payload["provenance"]
    quality = provenance.get("quality", {}) if isinstance(provenance.get("quality", {}), dict) else {}
    lifecycle = provenance.get("lifecycle", {}) if isinstance(provenance.get("lifecycle", {}), dict) else {}

    print(f"{skill['id']} [{payload['resolved_channel']}]")
    print(f"  title: {skill.get('title', '')}")
    print(f"  registry: {payload['registry']['registry_url']}")
    print(f"  publisher: {skill.get('publisher_display_name', skill.get('publisher', ''))}")
    print(f"  summary: {skill.get('summary', '')}")
    print(f"  version: {skill.get('version', '')}")
    print(f"  tags: {', '.join(skill.get('tags', []))}")
    print(f"  categories: {', '.join(skill.get('categories', []))}")
    print(f"  capabilities: {', '.join(skill.get('capabilities', []))}")
    print(f"  starter bundles: {', '.join(skill.get('starter_bundle_ids', [])) or 'none'}")
    print(f"  install spec url: {payload.get('install_spec_url', '')}")
    print(f"  package url: {payload.get('package_url', '')}")
    print(f"  provenance url: {payload.get('provenance_url', '')}")
    print(f"  entrypoint: {install_spec.get('entrypoint', '')}")
    print(f"  review: {quality.get('review_status', install_spec.get('review_status', ''))}")
    print(f"  lifecycle: {lifecycle.get('status', install_spec.get('lifecycle_status', ''))}")
    print(f"  checker: {quality.get('checker', '')}")
    print(f"  eval: {quality.get('eval', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
