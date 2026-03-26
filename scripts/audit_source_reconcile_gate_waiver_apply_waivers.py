#!/usr/bin/env python3
"""Audit reusable source-reconcile gate waiver apply waivers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import check_source_reconcile_gate_waiver_apply_gate
import report_source_reconcile_gate_waiver_apply
from market_utils import ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit source-reconcile gate waiver apply waivers for expired, unmatched, stale, or policy-mismatch cases."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile context.",
    )
    parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path used to build the apply-gate context.",
    )
    parser.add_argument(
        "--apply-gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver apply waiver id or JSON file path to audit. Defaults to all known apply-gate waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing apply-gate artifacts and receiving audit summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for write verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument(
        "--source-reconcile-execute-summary-path",
        type=Path,
        help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.",
    )
    parser.add_argument(
        "--apply-execute-summary-path",
        type=Path,
        help="Optional source-reconcile gate waiver apply execution summary JSON path.",
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


def resolve_audited_apply_gate_waivers(tokens: list[str]) -> list[dict]:
    if tokens:
        return check_source_reconcile_gate_waiver_apply_gate.resolve_requested_waivers(tokens)
    waivers, errors = check_source_reconcile_gate_waiver_apply_gate.load_waiver_profiles()
    if errors:
        raise SystemExit("\n".join(errors))
    return waivers


def build_apply_gate_context_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    source_reconcile_execute_summary_path: Path | None,
    apply_execute_summary_path: Path | None,
    policy_payload: dict,
    policy_path: Path,
) -> dict:
    defaults = check_source_reconcile_gate_waiver_apply_gate.policy_defaults(policy_payload)
    allowed_states = check_source_reconcile_gate_waiver_apply_gate.normalize_allowed_states(
        defaults["allowed_states"]
    )
    return check_source_reconcile_gate_waiver_apply_gate.build_gate_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
        policy_payload=policy_payload,
        policy_path=policy_path,
        allowed_states=allowed_states,
        apply_gate_waiver_tokens=[],
    )


def load_all_policy_profiles() -> tuple[list[dict], list[str]]:
    return check_source_reconcile_gate_waiver_apply_gate.load_policy_profiles()


def audit_single_apply_gate_waiver(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    apply_gate_waiver: dict,
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    source_reconcile_execute_summary_path: Path | None,
    apply_execute_summary_path: Path | None,
) -> dict:
    apply_gate_waiver_id = str(apply_gate_waiver.get("id", "")).strip()
    policy_id = str(apply_gate_waiver.get("policy_id", "")).strip()
    findings: list[dict] = []

    try:
        policy_payload, policy_path = check_source_reconcile_gate_waiver_apply_gate.resolve_policy_reference(policy_id)
        payload = build_apply_gate_context_payload(
            history_path,
            source_waiver_tokens,
            gate_waiver_tokens,
            output_dir=output_dir,
            target_root=target_root,
            stage_dir=stage_dir,
            source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
            apply_execute_summary_path=apply_execute_summary_path,
            policy_payload=policy_payload,
            policy_path=policy_path,
        )
    except SystemExit as exc:
        findings.append({"code": "policy_error", "message": str(exc)})
        return {
            "id": apply_gate_waiver_id,
            "title": apply_gate_waiver.get("title"),
            "policy_id": policy_id,
            "path": apply_gate_waiver.get("_path"),
            "expires_on": apply_gate_waiver.get("expires_on", ""),
            "active": check_source_reconcile_gate_waiver_apply_gate.is_waiver_active(apply_gate_waiver),
            "report_state": "",
            "selector_matches": False,
            "matching_finding_count": 0,
            "matched_finding_codes": [],
            "matched_policy_ids": [],
            "findings": findings,
            "passes": False,
        }

    selector_matches = check_source_reconcile_gate_waiver_apply_gate.waiver_matches_report_scope(
        apply_gate_waiver,
        policy_id,
        payload,
        require_active=False,
    )
    matching_findings = [
        finding
        for finding in payload.get("findings", [])
        if isinstance(finding, dict)
        and check_source_reconcile_gate_waiver_apply_gate.waiver_matches_finding(
            apply_gate_waiver,
            policy_id,
            payload,
            finding,
            require_active=False,
        )
    ]
    active = check_source_reconcile_gate_waiver_apply_gate.is_waiver_active(apply_gate_waiver)
    if not active:
        findings.append(
            {
                "code": "expired",
                "message": f"source-reconcile gate waiver apply waiver '{apply_gate_waiver_id}' is expired and should be removed or renewed",
            }
        )
    if not selector_matches:
        findings.append(
            {
                "code": "unmatched",
                "message": f"source-reconcile gate waiver apply waiver '{apply_gate_waiver_id}' no longer matches the current apply-gate report scope",
            }
        )
    elif not matching_findings:
        all_policies, policy_errors = load_all_policy_profiles()
        if policy_errors:
            findings.extend({"code": "policy_error", "message": error} for error in policy_errors)
        alternative_policy_ids: list[str] = []
        for alternative in all_policies:
            alternative_policy_id = str(alternative.get("id", "")).strip()
            if not alternative_policy_id or alternative_policy_id == policy_id:
                continue
            alternative_path = Path(str(alternative.get("_path", "")))
            alternative_payload = build_apply_gate_context_payload(
                history_path,
                source_waiver_tokens,
                gate_waiver_tokens,
                output_dir=output_dir,
                target_root=target_root,
                stage_dir=stage_dir,
                source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
                apply_execute_summary_path=apply_execute_summary_path,
                policy_payload=alternative,
                policy_path=alternative_path,
            )
            if not check_source_reconcile_gate_waiver_apply_gate.waiver_selectors_match_report(
                apply_gate_waiver,
                alternative_payload,
                require_active=False,
            ):
                continue
            if any(
                check_source_reconcile_gate_waiver_apply_gate.finding_codes_match_waiver(
                    apply_gate_waiver,
                    finding,
                )
                for finding in alternative_payload.get("findings", [])
                if isinstance(finding, dict)
            ):
                alternative_policy_ids.append(alternative_policy_id)

        if alternative_policy_ids:
            findings.append(
                {
                    "code": "policy_mismatch",
                    "message": f"source-reconcile gate waiver apply waiver '{apply_gate_waiver_id}' does not match findings under policy '{policy_id}' but would match under {', '.join(sorted(alternative_policy_ids))}",
                }
            )
        else:
            findings.append(
                {
                    "code": "stale",
                    "message": f"source-reconcile gate waiver apply waiver '{apply_gate_waiver_id}' matches the report scope but no longer matches any active apply-gate finding",
                }
            )
    else:
        alternative_policy_ids = []

    if "alternative_policy_ids" not in locals():
        alternative_policy_ids = []

    return {
        "id": apply_gate_waiver_id,
        "title": apply_gate_waiver.get("title"),
        "policy_id": policy_id,
        "path": apply_gate_waiver.get("_path"),
        "expires_on": apply_gate_waiver.get("expires_on", ""),
        "active": active,
        "report_state": payload.get("report_state", ""),
        "selector_matches": selector_matches,
        "matching_finding_count": len(matching_findings),
        "matched_finding_codes": sorted(
            {
                str(finding.get("code", "")).strip()
                for finding in matching_findings
                if str(finding.get("code", "")).strip()
            }
        ),
        "matched_policy_ids": sorted({policy_id, *alternative_policy_ids} if matching_findings else set(alternative_policy_ids)),
        "finding_count": payload.get("finding_count", 0),
        "active_finding_count": payload.get("active_finding_count", 0),
        "waived_finding_count": payload.get("waived_finding_count", 0),
        "findings": findings,
        "passes": len(findings) == 0,
    }


def build_audit_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    apply_gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    source_reconcile_execute_summary_path: Path | None,
    apply_execute_summary_path: Path | None,
) -> dict:
    waivers = resolve_audited_apply_gate_waivers(apply_gate_waiver_tokens)
    results = [
        audit_single_apply_gate_waiver(
            history_path,
            source_waiver_tokens,
            gate_waiver_tokens,
            waiver,
            output_dir=output_dir,
            target_root=target_root,
            stage_dir=stage_dir,
            source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
            apply_execute_summary_path=apply_execute_summary_path,
        )
        for waiver in waivers
    ]
    finding_codes = [
        finding.get("code")
        for result in results
        for finding in result.get("findings", [])
        if isinstance(finding, dict)
    ]
    return {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": report_source_reconcile_gate_waiver_apply.display_path(output_dir),
        "target_root": report_source_reconcile_gate_waiver_apply.display_path(target_root),
        "stage_dir": report_source_reconcile_gate_waiver_apply.display_path(stage_dir),
        "waiver_count": len(results),
        "finding_count": len(finding_codes),
        "expired_count": sum(1 for code in finding_codes if code == "expired"),
        "unmatched_count": sum(1 for code in finding_codes if code == "unmatched"),
        "stale_count": sum(1 for code in finding_codes if code == "stale"),
        "policy_error_count": sum(1 for code in finding_codes if code == "policy_error"),
        "policy_mismatch_count": sum(1 for code in finding_codes if code == "policy_mismatch"),
        "passes": len(finding_codes) == 0,
        "waivers": results,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Reconcile Gate Waiver Apply Waiver Audit",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Expired: `{payload.get('expired_count', 0)}`",
        f"- Unmatched: `{payload.get('unmatched_count', 0)}`",
        f"- Stale: `{payload.get('stale_count', 0)}`",
        f"- Policy mismatch: `{payload.get('policy_mismatch_count', 0)}`",
        f"- Policy error: `{payload.get('policy_error_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Waiver Results",
        "",
    ]
    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No source-reconcile gate waiver apply waivers audited.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` active=`{waiver.get('active', False)}`"
                f" selector_matches=`{waiver.get('selector_matches', False)}`"
                f" matching_findings=`{waiver.get('matching_finding_count', 0)}`"
                f" report_state=`{waiver.get('report_state', '')}`"
            )
            findings = waiver.get("findings", [])
            if not findings:
                lines.append("  - no findings")
            else:
                for finding in findings:
                    lines.append(f"  - `{finding.get('code', '')}`: {finding.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = (
        resolve_repo_path(args.output_dir)
        if args.output_dir
        else report_source_reconcile_gate_waiver_apply.DEFAULT_OUTPUT_DIR
    )
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    source_reconcile_execute_summary_path = (
        resolve_repo_path(args.source_reconcile_execute_summary_path)
        if args.source_reconcile_execute_summary_path
        else None
    )
    apply_execute_summary_path = (
        resolve_repo_path(args.apply_execute_summary_path)
        if args.apply_execute_summary_path
        else None
    )

    payload = build_audit_payload(
        args.history,
        args.waiver,
        args.gate_waiver,
        args.apply_gate_waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        source_reconcile_execute_summary_path=source_reconcile_execute_summary_path,
        apply_execute_summary_path=apply_execute_summary_path,
    )

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source reconcile gate waiver apply waiver audit:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Findings: {payload['finding_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
