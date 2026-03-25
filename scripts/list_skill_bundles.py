#!/usr/bin/env python3
"""List starter bundles available in the local skills market."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from market_utils import load_filtered_market_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List starter bundles from the local skills market.")
    parser.add_argument("--org-policy", type=Path, default=None, help="Optional org market policy JSON file.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifests, bundles, policy_payload, errors = load_filtered_market_inputs(args.org_policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    manifest_by_id = {manifest["id"]: manifest for manifest in manifests}
    payload = {
        "org_policy": policy_payload["org_id"] if policy_payload else None,
        "bundle_count": len(bundles),
        "bundles": [],
    }

    for bundle in bundles:
        status_counts = Counter(
            manifest_by_id[skill_id]["lifecycle"]["status"]
            for skill_id in bundle["skills"]
            if skill_id in manifest_by_id
        )
        payload["bundles"].append(
            {
                "id": bundle["id"],
                "title": bundle["title"],
                "status": bundle["status"],
                "channels": bundle["channels"],
                "skill_count": len(bundle["skills"]),
                "skills": bundle["skills"],
                "lifecycle_mix": dict(sorted(status_counts.items())),
                "summary": bundle["summary"],
            }
        )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if policy_payload:
        print(f"Bundle scope: {policy_payload['org_id']}")
    if not payload["bundles"]:
        print("No starter bundles available in the current market scope.")
        return 0

    print("Starter bundles:")
    for bundle in payload["bundles"]:
        channels = ", ".join(bundle["channels"])
        mix = ", ".join(f"{status}={count}" for status, count in bundle["lifecycle_mix"].items()) or "none"
        print(f"- {bundle['id']} [{channels}]")
        print(f"  title: {bundle['title']}")
        print(f"  skills: {bundle['skill_count']}")
        print(f"  lifecycle mix: {mix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
