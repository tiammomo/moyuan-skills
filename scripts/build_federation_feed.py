#!/usr/bin/env python3
"""Export a metadata-only feed for downstream skills-market aggregators."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from market_utils import (
    ROOT,
    collect_valid_manifests,
    dump_json,
    enrich_manifest,
    filter_manifests_for_policy,
    load_bundle_definitions,
    load_json,
    load_publisher_profiles,
    repo_relative_path,
    validate_org_policy,
)


DEFAULT_OUTPUT = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a metadata-only feed for downstream aggregators.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory containing market artifacts.")
    parser.add_argument("--org-policy", type=Path, default=None, help="Optional org market policy JSON file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    errors = [*manifest_errors, *publisher_errors]
    policy_payload: dict | None = None

    if args.org_policy is not None:
        policy_path = args.org_policy if args.org_policy.is_absolute() else (ROOT / args.org_policy)
        if not policy_path.is_file():
            errors.append(f"missing org policy file: {policy_path}")
        else:
            policy_payload = load_json(policy_path)
            _, policy_errors = validate_org_policy(
                policy_path.resolve(),
                publisher_profiles,
                {manifest["id"] for manifest in manifests},
            )
            errors.extend(policy_errors)

    bundles, bundle_errors = load_bundle_definitions({manifest["id"] for manifest in manifests})
    errors.extend(bundle_errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if policy_payload is not None:
        manifests = filter_manifests_for_policy(manifests, policy_payload, publisher_profiles)

    manifest_ids = {manifest["id"] for manifest in manifests}
    bundles = [
        bundle
        for bundle in bundles
        if any(skill_id in manifest_ids for skill_id in bundle["skills"])
    ]
    if policy_payload and policy_payload.get("featured_bundles"):
        allowed_bundle_ids = set(policy_payload["featured_bundles"])
        bundles = [bundle for bundle in bundles if bundle["id"] in allowed_bundle_ids]

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()
    feed_path = output_dir / "federation" / "public-feed.json"
    if policy_payload is not None:
        feed_path = output_dir / "orgs" / policy_payload["org_id"] / "federation" / "feed.json"

    enriched = [enrich_manifest(manifest, publisher_profiles) for manifest in manifests]
    payload = {
        "format": "moyuan-skills-market-feed@v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "type": "org" if policy_payload else "public",
            "id": policy_payload["org_id"] if policy_payload else "public",
        },
        "skills": [
            {
                "id": manifest["id"],
                "name": manifest["name"],
                "title": manifest["title"],
                "publisher": manifest["publisher"],
                "publisher_display_name": manifest["publisher_profile"]["display_name"],
                "publisher_verified": manifest["publisher_profile"]["verified"],
                "trust_level": manifest["publisher_profile"]["trust_level"],
                "version": manifest["version"],
                "channel": manifest["channel"],
                "summary": manifest["summary"],
                "categories": manifest["categories"],
                "tags": manifest["tags"],
                "capabilities": manifest["distribution"]["capabilities"],
                "starter_bundle_ids": manifest["distribution"]["starter_bundle_ids"],
                "review_status": manifest["quality"]["review_status"],
                "lifecycle_status": manifest["lifecycle"]["status"],
                "install_spec": repo_relative_path(output_dir / "install" / f"{manifest['name']}-{manifest['version']}.json"),
                "provenance_path": repo_relative_path(output_dir / "provenance" / f"{manifest['name']}-{manifest['version']}.json"),
            }
            for manifest in enriched
        ],
        "bundles": [
            {
                "id": bundle["id"],
                "title": bundle["title"],
                "summary": bundle["summary"],
                "channels": bundle["channels"],
                "skills": [skill_id for skill_id in bundle["skills"] if skill_id in manifest_ids],
            }
            for bundle in bundles
        ],
    }
    dump_json(feed_path, payload)
    print(f"Built federation feed in {feed_path}")
    if policy_payload is not None:
        print(f"Feed scope: {policy_payload['org_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
