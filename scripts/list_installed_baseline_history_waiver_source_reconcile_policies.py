#!/usr/bin/env python3
"""List reusable source-reconcile gate policy profiles."""

from __future__ import annotations

import argparse
import json

import check_installed_baseline_history_waiver_source_reconcile_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List reusable installed history waiver source-reconcile gate policies.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    policies, errors = check_installed_baseline_history_waiver_source_reconcile_gate.load_policy_profiles()
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
                "allowed_states": policy.get("defaults", {}).get("allowed_states", []),
                "require_report_complete": policy.get("defaults", {}).get("require_report_complete"),
                "fail_on_blocked_execution": policy.get("defaults", {}).get("fail_on_blocked_execution"),
                "fail_on_pending_verification": policy.get("defaults", {}).get("fail_on_pending_verification"),
                "fail_on_blocked_verification": policy.get("defaults", {}).get("fail_on_blocked_verification"),
                "fail_on_verification_drift": policy.get("defaults", {}).get("fail_on_verification_drift"),
                "path": policy.get("_path"),
            }
            for policy in policies
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Installed history waiver source-reconcile gate policies:")
    print(f"- Count: {payload['count']}")
    if not payload["policies"]:
        print("- No policies defined.")
        return 0
    for policy in payload["policies"]:
        states = ", ".join(policy["allowed_states"]) or "(none)"
        print(f"- {policy['id']}: {policy['title']} (states={states})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
