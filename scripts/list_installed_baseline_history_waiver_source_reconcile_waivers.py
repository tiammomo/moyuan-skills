#!/usr/bin/env python3
"""List reusable source-reconcile gate waiver profiles."""

from __future__ import annotations

import argparse
import json

import check_installed_baseline_history_waiver_source_reconcile_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List reusable installed history waiver source-reconcile gate waivers.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    waivers, errors = check_installed_baseline_history_waiver_source_reconcile_gate.load_waiver_profiles()
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
                "description": waiver.get("description"),
                "policy_id": waiver.get("policy_id"),
                "finding_codes": waiver.get("match", {}).get("finding_codes", []),
                "report_states": waiver.get("match", {}).get("report_states", []),
                "target_root_suffix": waiver.get("match", {}).get("target_root_suffix"),
                "stage_dir_suffix": waiver.get("match", {}).get("stage_dir_suffix"),
                "action_waiver_ids": waiver.get("match", {}).get("action_waiver_ids", []),
                "action_codes": waiver.get("match", {}).get("action_codes", []),
                "expires_on": waiver.get("expires_on", ""),
                "path": waiver.get("_path"),
            }
            for waiver in waivers
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed history waiver source-reconcile gate waivers:")
    print(f"- Count: {payload['count']}")
    if not payload["waivers"]:
        print("- No waivers defined.")
        return 0
    for waiver in payload["waivers"]:
        codes = ", ".join(waiver["finding_codes"]) or "(none)"
        print(f"- {waiver['id']}: {waiver['title']} (finding_codes={codes})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
