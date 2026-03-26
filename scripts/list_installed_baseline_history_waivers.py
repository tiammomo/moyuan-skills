#!/usr/bin/env python3
"""List reusable waiver records for installed baseline history alerts."""

from __future__ import annotations

import argparse
import json

import check_installed_baseline_history_alerts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List reusable installed baseline history alert waivers.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    waivers, errors = check_installed_baseline_history_alerts.load_waiver_profiles()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    payload = {
        "count": len(waivers),
        "waivers": [
            {
                "id": waiver.get("id"),
                "title": waiver.get("title"),
                "policy_id": waiver.get("policy_id"),
                "expires_on": waiver.get("expires_on", ""),
                "active": check_installed_baseline_history_alerts.is_waiver_active(waiver),
                "path": waiver.get("_path"),
            }
            for waiver in waivers
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed baseline history alert waivers:")
    print(f"- Count: {payload['count']}")
    if not payload["waivers"]:
        print("- No waivers defined.")
        return 0
    for waiver in payload["waivers"]:
        print(
            f"- {waiver['id']}: {waiver['title']} "
            f"(policy={waiver['policy_id']}, active={waiver['active']}, expires_on={waiver['expires_on'] or 'never'})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
