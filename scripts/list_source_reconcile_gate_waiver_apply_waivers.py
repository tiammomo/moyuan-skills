#!/usr/bin/env python3
"""List reusable source-reconcile gate waiver apply waivers."""

from __future__ import annotations

import argparse
import json

import check_source_reconcile_gate_waiver_apply_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List reusable source-reconcile gate waiver apply waivers.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    waivers, errors = check_source_reconcile_gate_waiver_apply_gate.load_waiver_profiles()
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

    print("Source-reconcile gate waiver apply waivers:")
    print(f"- Count: {payload['count']}")
    if not payload["waivers"]:
        print("- No waivers defined.")
        return 0
    for waiver in payload["waivers"]:
        findings = ", ".join(waiver["finding_codes"]) or "(none)"
        print(f"- {waiver['id']}: {waiver['title']} (findings={findings})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
