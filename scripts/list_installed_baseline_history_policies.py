#!/usr/bin/env python3
"""List reusable policy profiles for installed baseline history alerts."""

from __future__ import annotations

import argparse
import json

import check_installed_baseline_history_alerts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List reusable installed baseline history alert policies.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    policies, errors = check_installed_baseline_history_alerts.load_policy_profiles()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    payload = {
        "count": len(policies),
        "policies": [
            {
                "id": policy.get("id"),
                "title": policy.get("title"),
                "description": policy.get("description"),
                "latest_only": policy.get("defaults", {}).get("latest_only"),
                "path": policy.get("_path"),
            }
            for policy in policies
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed baseline history alert policies:")
    print(f"- Count: {payload['count']}")
    if not payload["policies"]:
        print("- No policies defined.")
        return 0
    for policy in payload["policies"]:
        print(f"- {policy['id']}: {policy['title']} (latest_only={policy['latest_only']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
