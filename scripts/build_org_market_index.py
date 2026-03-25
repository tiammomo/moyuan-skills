#!/usr/bin/env python3
"""Build an org-scoped market index from allowlist policy."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_utils import (
    MARKET_CHANNELS,
    ORG_POLICIES_DIR,
    ROOT,
    aggregate_index_payload,
    channel_index_payload,
    collect_valid_manifests,
    dump_json,
    filter_manifests_for_policy,
    load_json,
    load_publisher_profiles,
    repo_relative_path,
    validate_org_policy,
)


DEFAULT_OUTPUT = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an org-scoped market index from governance policy.")
    parser.add_argument(
        "policy",
        nargs="?",
        type=Path,
        default=ORG_POLICIES_DIR / "moyuan-internal.json",
        help="Path to an org market policy JSON file.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory for generated market artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    policy_path = args.policy if args.policy.is_absolute() else (ROOT / args.policy)

    errors = [*manifest_errors, *publisher_errors]
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

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()
    org_output_dir = output_dir / "orgs" / policy_payload["org_id"]
    channels_dir = org_output_dir / "channels"
    filtered_manifests = filter_manifests_for_policy(manifests, policy_payload, publisher_profiles)

    aggregate_payload = aggregate_index_payload(filtered_manifests, output_dir)
    aggregate_payload["org"] = {
        "org_id": policy_payload["org_id"],
        "display_name": policy_payload["display_name"],
        "policy_path": repo_relative_path(policy_path),
        "allowed_publishers": policy_payload["allowed_publishers"],
        "allowed_review_statuses": policy_payload["allowed_review_statuses"],
        "allowed_lifecycle_statuses": policy_payload["allowed_lifecycle_statuses"],
        "featured_bundles": policy_payload.get("featured_bundles", []),
        "require_verified_publishers": policy_payload["require_verified_publishers"],
    }

    for channel in sorted(MARKET_CHANNELS):
        aggregate_payload["channels"][channel]["path"] = repo_relative_path(channels_dir / f"{channel}.json")

    dump_json(org_output_dir / "index.json", aggregate_payload)
    dump_json(org_output_dir / "policy.json", policy_payload)

    for channel in sorted(MARKET_CHANNELS):
        dump_json(
            channels_dir / f"{channel}.json",
            channel_index_payload(channel, filtered_manifests, output_dir, publisher_profiles),
        )

    print(f"Built org market index in {org_output_dir}")
    print(f"Included skills: {len(filtered_manifests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
