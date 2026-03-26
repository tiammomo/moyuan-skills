#!/usr/bin/env python3
"""Audit reusable waiver records for installed baseline history alerts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import check_installed_baseline_history_alerts
from market_utils import ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit installed baseline history waivers for expired, unmatched, or stale records."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to audit. Defaults to all known waivers.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional JSON audit output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown audit output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when findings are present.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_audited_waivers(tokens: list[str]) -> list[dict]:
    if tokens:
        return check_installed_baseline_history_alerts.resolve_requested_waivers(tokens)
    waivers, errors = check_installed_baseline_history_alerts.load_waiver_profiles()
    if errors:
        raise SystemExit("\n".join(errors))
    return waivers


def build_alert_args(policy_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        policy=policy_id,
        waiver=[],
        latest_only=False,
        max_added_skills=None,
        max_removed_skills=None,
        max_changed_skills=None,
        max_added_bundles=None,
        max_removed_bundles=None,
        max_changed_bundles=None,
        max_installed_delta=None,
        max_bundle_delta=None,
        output_path=None,
        markdown_path=None,
        json=False,
        strict=False,
    )


def audit_single_waiver(history_path: Path, waiver: dict) -> dict:
    waiver_id = str(waiver.get("id", "")).strip()
    policy_id = str(waiver.get("policy_id", "")).strip()
    findings: list[dict] = []

    try:
        payload = check_installed_baseline_history_alerts.build_alert_payload(
            history_path,
            build_alert_args(policy_id),
        )
    except SystemExit as exc:
        findings.append(
            {
                "code": "policy_error",
                "message": str(exc),
            }
        )
        return {
            "id": waiver_id,
            "title": waiver.get("title"),
            "policy_id": policy_id,
            "path": waiver.get("_path"),
            "expires_on": waiver.get("expires_on", ""),
            "active": check_installed_baseline_history_alerts.is_waiver_active(waiver),
            "selector_match_count": 0,
            "alert_match_count": 0,
            "matched_transition_pairs": [],
            "matched_alert_metrics": [],
            "findings": findings,
            "passes": False,
        }

    transitions = [
        item
        for item in payload.get("transitions", [])
        if isinstance(item, dict)
    ]
    selector_matches = [
        item
        for item in transitions
        if check_installed_baseline_history_alerts.waiver_matches_transition_scope(
            waiver,
            policy_id,
            item,
            require_active=False,
        )
    ]
    alert_matches: list[dict] = []
    for transition in transitions:
        alerts = transition.get("alerts", [])
        if not isinstance(alerts, list):
            continue
        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            if check_installed_baseline_history_alerts.waiver_matches_alert(
                waiver,
                policy_id,
                transition,
                alert,
                require_active=False,
            ):
                alert_matches.append(
                    {
                        "metric": alert.get("metric"),
                        "before_entry": transition.get("before_entry"),
                        "after_entry": transition.get("after_entry"),
                    }
                )

    active = check_installed_baseline_history_alerts.is_waiver_active(waiver)
    if not active:
        findings.append(
            {
                "code": "expired",
                "message": f"waiver '{waiver_id}' is expired and should be removed or renewed",
            }
        )
    if not selector_matches:
        findings.append(
            {
                "code": "unmatched",
                "message": f"waiver '{waiver_id}' no longer matches any retained history transition",
            }
        )
    elif not alert_matches:
        findings.append(
            {
                "code": "stale",
                "message": f"waiver '{waiver_id}' matches a retained transition but no longer matches any active alert",
            }
        )

    return {
        "id": waiver_id,
        "title": waiver.get("title"),
        "policy_id": policy_id,
        "path": waiver.get("_path"),
        "expires_on": waiver.get("expires_on", ""),
        "active": active,
        "selector_match_count": len(selector_matches),
        "alert_match_count": len(alert_matches),
        "matched_transition_pairs": [
            f"{item.get('before_entry')}->{item.get('after_entry')}"
            for item in selector_matches
        ],
        "matched_alert_metrics": sorted(
            {
                str(item.get("metric", "")).strip()
                for item in alert_matches
                if str(item.get("metric", "")).strip()
            }
        ),
        "findings": findings,
        "passes": len(findings) == 0,
    }


def build_audit_payload(history_path: Path, waiver_tokens: list[str]) -> dict:
    waivers = resolve_audited_waivers(waiver_tokens)
    results = [audit_single_waiver(history_path, waiver) for waiver in waivers]
    finding_codes = [
        finding.get("code")
        for result in results
        for finding in result.get("findings", [])
        if isinstance(finding, dict)
    ]
    return {
        "history_path": str(resolve_repo_path(history_path)),
        "waiver_count": len(results),
        "finding_count": len(finding_codes),
        "expired_count": sum(1 for code in finding_codes if code == "expired"),
        "unmatched_count": sum(1 for code in finding_codes if code == "unmatched"),
        "stale_count": sum(1 for code in finding_codes if code == "stale"),
        "policy_error_count": sum(1 for code in finding_codes if code == "policy_error"),
        "passes": len(finding_codes) == 0,
        "waivers": results,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Audit",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Expired: `{payload.get('expired_count', 0)}`",
        f"- Unmatched: `{payload.get('unmatched_count', 0)}`",
        f"- Stale: `{payload.get('stale_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Waiver Results",
        "",
    ]

    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No waivers audited.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` active=`{waiver.get('active', False)}`"
                f" selector_matches=`{waiver.get('selector_match_count', 0)}`"
                f" alert_matches=`{waiver.get('alert_match_count', 0)}`"
            )
            findings = waiver.get("findings", [])
            if not findings:
                lines.append("  - no findings")
                continue
            for finding in findings:
                lines.append(
                    f"  - `{finding.get('code', '')}`: {finding.get('message', '')}"
                )

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_audit_payload(args.history, args.waiver)

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver audit:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Findings: {payload['finding_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
