#!/usr/bin/env python3
"""Browse a hosted remote registry without installing any skill artifacts."""

from __future__ import annotations

import argparse
import json

from remote_registry_utils import RemoteRegistryClient, RemoteRegistryError, load_remote_registry_catalog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Browse a hosted remote registry.")
    parser.add_argument("--registry", required=True, help="Hosted registry base URL or registry.json URL.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = load_remote_registry_catalog(RemoteRegistryClient(args.registry))
    except RemoteRegistryError as error:
        print(f"ERROR: {error}")
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    registry = payload["registry"]
    print(f"Remote registry: {registry['registry_url']}")
    print(f"Base URL: {registry['registry_base_url']}")
    if registry.get("format"):
        print(f"Format: {registry['format']}")
    if registry.get("generated_at"):
        print(f"Generated at: {registry['generated_at']}")
    print(f"Catalog URL: {registry.get('public', {}).get('catalog', '')}")
    print(f"Recommendations URL: {registry.get('public', {}).get('recommendations', '')}")

    channels = payload.get("channels", [])
    if channels:
        print("Channels:")
        for channel in channels:
            print(f"- {channel['channel']}: {channel['count']} skill(s)")

    bundles = payload.get("bundles", [])
    if not bundles:
        print("No remote starter bundles were published.")
        return 0

    print("Starter bundles:")
    for bundle in bundles:
        channels_label = ", ".join(bundle.get("channels", [])) or "none"
        skills = bundle.get("skills", [])
        print(f"- {bundle.get('id', '')} [{channels_label}]")
        print(f"  title: {bundle.get('title', '')}")
        print(f"  skills: {len(skills)}")
        print(f"  summary: {bundle.get('summary', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
