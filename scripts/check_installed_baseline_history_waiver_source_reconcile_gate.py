#!/usr/bin/env python3
"""Evaluate source-reconcile report artifacts as a reusable CI/release gate."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import report_installed_baseline_history_waiver_source_reconcile
from market_utils import ROOT, repo_relative_path


DEFAULT_ALLOWED_STATES = ("verified", "no_reconcile_actions")
SOURCE_RECONCILE_GATE_POLICIES_DIR = ROOT / "governance" / "source-reconcile-gate-policies"
SOURCE_RECONCILE_GATE_WAIVERS_DIR = ROOT / "governance" / "source-reconcile-gate-waivers"
SOURCE_RECONCILE_REPORT_STATES = (
    "needs_execution",
    "drifted",
    "needs_verification_followup",
    "verified",
    "no_reconcile_actions",
    "review_required",
)
SOURCE_RECONCILE_FINDING_CODES = (
    "incomplete_report",
    "disallowed_report_state",
    "blocked_execution",
    "pending_verification",
    "blocked_verification",
    "verification_drift",
)


def iter_policy_paths() -> list[Path]:
    return sorted(SOURCE_RECONCILE_GATE_POLICIES_DIR.glob("*.json"))


def iter_waiver_paths() -> list[Path]:
    return sorted(SOURCE_RECONCILE_GATE_WAIVERS_DIR.glob("*.json"))


def parse_iso_date(value: object, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty YYYY-MM-DD string")
        return ""
    normalized = value.strip()
    try:
        date.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{label} must use YYYY-MM-DD format")
        return ""
    return normalized


def validate_policy_payload(path: Path) -> tuple[dict, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    label = path.relative_to(ROOT).as_posix()
    if not isinstance(payload, dict):
        return {}, [f"{label}: JSON root must be an object"]

    policy_version = payload.get("policy_version")
    if not isinstance(policy_version, int) or policy_version < 1:
        errors.append(f"{label}: 'policy_version' must be an integer >= 1")
    policy_id = payload.get("id")
    if not isinstance(policy_id, str) or len(policy_id.strip()) < 3:
        errors.append(f"{label}: 'id' must be a non-empty string")
    title = payload.get("title")
    if not isinstance(title, str) or len(title.strip()) < 3:
        errors.append(f"{label}: 'title' must be a non-empty string")
    description = payload.get("description")
    if not isinstance(description, str) or len(description.strip()) < 20:
        errors.append(f"{label}: 'description' must be a descriptive string")

    defaults = payload.get("defaults")
    if not isinstance(defaults, dict):
        errors.append(f"{label}: 'defaults' must be an object")
        return payload, errors

    allowed_states = defaults.get("allowed_states")
    if (
        not isinstance(allowed_states, list)
        or not allowed_states
        or not all(isinstance(item, str) and item.strip() for item in allowed_states)
    ):
        errors.append(f"{label}: 'defaults.allowed_states' must be a non-empty list of strings")

    expected_default_keys = {
        "allowed_states",
        "require_report_complete",
        "fail_on_blocked_execution",
        "fail_on_pending_verification",
        "fail_on_blocked_verification",
        "fail_on_verification_drift",
    }
    for key in expected_default_keys - {"allowed_states"}:
        if not isinstance(defaults.get(key), bool):
            errors.append(f"{label}: 'defaults.{key}' must be a boolean")
    unexpected = sorted(set(defaults) - expected_default_keys)
    if unexpected:
        errors.append(f"{label}: unsupported default keys: {', '.join(unexpected)}")

    return payload, errors


def validate_waiver_payload(path: Path) -> tuple[dict, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    label = path.relative_to(ROOT).as_posix()
    if not isinstance(payload, dict):
        return {}, [f"{label}: JSON root must be an object"]

    waiver_version = payload.get("waiver_version")
    if not isinstance(waiver_version, int) or waiver_version < 1:
        errors.append(f"{label}: 'waiver_version' must be an integer >= 1")
    waiver_id = payload.get("id")
    if not isinstance(waiver_id, str) or len(waiver_id.strip()) < 3:
        errors.append(f"{label}: 'id' must be a non-empty string")
    title = payload.get("title")
    if not isinstance(title, str) or len(title.strip()) < 3:
        errors.append(f"{label}: 'title' must be a non-empty string")
    description = payload.get("description")
    if not isinstance(description, str) or len(description.strip()) < 20:
        errors.append(f"{label}: 'description' must be a descriptive string")
    policy_id = payload.get("policy_id")
    if not isinstance(policy_id, str) or len(policy_id.strip()) < 3:
        errors.append(f"{label}: 'policy_id' must be a non-empty string")

    match = payload.get("match")
    selectors_present = False
    if not isinstance(match, dict):
        errors.append(f"{label}: 'match' must be an object")
    else:
        finding_codes = match.get("finding_codes")
        if (
            not isinstance(finding_codes, list)
            or not finding_codes
            or not all(isinstance(item, str) and item.strip() for item in finding_codes)
        ):
            errors.append(f"{label}: 'match.finding_codes' must be a non-empty list of strings")
        else:
            invalid_codes = sorted(
                {item.strip() for item in finding_codes if item.strip() not in SOURCE_RECONCILE_FINDING_CODES}
            )
            if invalid_codes:
                errors.append(f"{label}: unsupported finding codes: {', '.join(invalid_codes)}")

        report_states = match.get("report_states")
        if report_states is not None:
            selectors_present = True
            if (
                not isinstance(report_states, list)
                or not report_states
                or not all(isinstance(item, str) and item.strip() for item in report_states)
            ):
                errors.append(f"{label}: 'match.report_states' must be a non-empty list of strings")
            else:
                invalid_states = sorted(
                    {item.strip() for item in report_states if item.strip() not in SOURCE_RECONCILE_REPORT_STATES}
                )
                if invalid_states:
                    errors.append(f"{label}: unsupported report states: {', '.join(invalid_states)}")

        for key in ("target_root_suffix", "stage_dir_suffix"):
            value = match.get(key)
            if value is None:
                continue
            selectors_present = True
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: 'match.{key}' must be a non-empty string")

        for key in ("action_waiver_ids", "action_codes"):
            value = match.get(key)
            if value is None:
                continue
            selectors_present = True
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{label}: 'match.{key}' must be a non-empty list of strings")

        if not selectors_present:
            errors.append(
                f"{label}: 'match' must include at least one selector such as report_states, target_root_suffix, stage_dir_suffix, or action selectors"
            )

    approval = payload.get("approval")
    if not isinstance(approval, dict):
        errors.append(f"{label}: 'approval' must be an object")
    else:
        approved_by = approval.get("approved_by")
        if not isinstance(approved_by, str) or len(approved_by.strip()) < 3:
            errors.append(f"{label}: 'approval.approved_by' must be a non-empty string")
        parse_iso_date(approval.get("approved_at"), f"{label}: 'approval.approved_at'", errors)
        reason = approval.get("reason")
        if not isinstance(reason, str) or len(reason.strip()) < 20:
            errors.append(f"{label}: 'approval.reason' must be a descriptive string")

    expires_on = payload.get("expires_on")
    if expires_on not in ("", None):
        parse_iso_date(expires_on, f"{label}: 'expires_on'", errors)

    return payload, errors


def load_policy_profiles() -> tuple[list[dict], list[str]]:
    policies: list[dict] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in iter_policy_paths():
        payload, policy_errors = validate_policy_payload(path)
        if policy_errors:
            errors.extend(policy_errors)
            continue
        policy_id = str(payload.get("id", "")).strip()
        if policy_id in seen_ids:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: duplicate policy id '{policy_id}'")
            continue
        seen_ids.add(policy_id)
        payload["_path"] = str(path)
        policies.append(payload)

    policies.sort(key=lambda item: str(item.get("title", "")).lower())
    return policies, errors


def load_waiver_profiles() -> tuple[list[dict], list[str]]:
    waivers: list[dict] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in iter_waiver_paths():
        payload, waiver_errors = validate_waiver_payload(path)
        if waiver_errors:
            errors.extend(waiver_errors)
            continue
        waiver_id = str(payload.get("id", "")).strip()
        if waiver_id in seen_ids:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: duplicate waiver id '{waiver_id}'")
            continue
        seen_ids.add(waiver_id)
        payload["_path"] = str(path)
        waivers.append(payload)

    waivers.sort(key=lambda item: str(item.get("title", "")).lower())
    return waivers, errors


def resolve_policy_reference(token: str) -> tuple[dict, Path]:
    candidate_path = resolve_repo_path(Path(token))
    if candidate_path.is_file():
        payload, errors = validate_policy_payload(candidate_path)
        if errors:
            raise SystemExit("\n".join(errors))
        payload["_path"] = str(candidate_path)
        return payload, candidate_path

    policies, errors = load_policy_profiles()
    if errors:
        raise SystemExit("\n".join(errors))
    for policy in policies:
        if str(policy.get("id", "")).strip().lower() == token.strip().lower():
            return policy, Path(str(policy.get("_path", "")))
    raise SystemExit(f"installed history waiver source-reconcile gate policy not found: {token}")


def resolve_waiver_reference(token: str) -> tuple[dict, Path]:
    candidate_path = resolve_repo_path(Path(token))
    if candidate_path.is_file():
        payload, errors = validate_waiver_payload(candidate_path)
        if errors:
            raise SystemExit("\n".join(errors))
        payload["_path"] = str(candidate_path)
        return payload, candidate_path

    waivers, errors = load_waiver_profiles()
    if errors:
        raise SystemExit("\n".join(errors))
    for waiver in waivers:
        if str(waiver.get("id", "")).strip().lower() == token.strip().lower():
            return waiver, Path(str(waiver.get("_path", "")))
    raise SystemExit(f"installed history waiver source-reconcile gate waiver not found: {token}")


def resolve_requested_waivers(tokens: list[str]) -> list[dict]:
    resolved: list[dict] = []
    seen_ids: set[str] = set()
    for token in tokens:
        payload, path = resolve_waiver_reference(token)
        waiver_id = str(payload.get("id", "")).strip()
        if waiver_id in seen_ids:
            continue
        seen_ids.add(waiver_id)
        payload["_path"] = str(path)
        resolved.append(payload)
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate source-reconcile report artifacts as a reusable gate."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--policy", help="Named policy id or JSON file path for reusable source-reconcile gate rules.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to gate. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path. May be used more than once.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-reconcile artifacts and receiving gate summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source audits and verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument("--execute-summary-path", type=Path, help="Optional source-reconcile execution summary JSON path.")
    parser.add_argument(
        "--allow-state",
        action="append",
        default=[],
        help="Report state that should be treated as passing. Defaults to verified and no_reconcile_actions.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional JSON gate output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown gate output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when the gate fails.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_json_payload(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def display_path(path: Path) -> str:
    return repo_relative_path(path) if path.is_relative_to(ROOT) else str(path)


def normalize_allowed_states(values: list[str]) -> list[str]:
    normalized = [value.strip() for value in values if value.strip()]
    return normalized or list(DEFAULT_ALLOWED_STATES)


def policy_defaults(policy_payload: dict | None = None) -> dict:
    defaults = {
        "allowed_states": list(DEFAULT_ALLOWED_STATES),
        "require_report_complete": True,
        "fail_on_blocked_execution": True,
        "fail_on_pending_verification": True,
        "fail_on_blocked_verification": True,
        "fail_on_verification_drift": True,
    }
    if isinstance(policy_payload, dict):
        configured = policy_payload.get("defaults", {})
        if isinstance(configured, dict):
            allowed_states = configured.get("allowed_states")
            if isinstance(allowed_states, list) and allowed_states and all(isinstance(item, str) and item.strip() for item in allowed_states):
                defaults["allowed_states"] = [item.strip() for item in allowed_states]
            for key in (
                "require_report_complete",
                "fail_on_blocked_execution",
                "fail_on_pending_verification",
                "fail_on_blocked_verification",
                "fail_on_verification_drift",
            ):
                value = configured.get(key)
                if isinstance(value, bool):
                    defaults[key] = value
    return defaults


def is_waiver_active(waiver: dict) -> bool:
    expires_on = str(waiver.get("expires_on", "")).strip()
    if not expires_on:
        return True
    try:
        return date.today() <= date.fromisoformat(expires_on)
    except ValueError:
        return False


def normalized_suffix_match(actual: str, suffix: str) -> bool:
    normalized_actual = actual.replace("\\", "/").lower()
    normalized_suffix = suffix.replace("\\", "/").lower()
    return normalized_actual.endswith(normalized_suffix)


def waiver_selectors_match_report(
    waiver: dict,
    payload: dict,
    *,
    require_active: bool = True,
) -> bool:
    if require_active and not is_waiver_active(waiver):
        return False

    match = waiver.get("match", {})
    if not isinstance(match, dict):
        return False

    report_states = [
        str(item).strip()
        for item in match.get("report_states", [])
        if isinstance(item, str) and item.strip()
    ]
    if report_states and str(payload.get("report_state", "")).strip() not in report_states:
        return False

    target_root_suffix = str(match.get("target_root_suffix", "")).strip()
    if target_root_suffix and not normalized_suffix_match(
        str(payload.get("target_root", "")),
        target_root_suffix,
    ):
        return False

    stage_dir_suffix = str(match.get("stage_dir_suffix", "")).strip()
    if stage_dir_suffix and not normalized_suffix_match(
        str(payload.get("stage_dir", "")),
        stage_dir_suffix,
    ):
        return False

    actions = payload.get("report", {}).get("actions", [])
    if not isinstance(actions, list):
        actions = []
    action_waiver_ids = {
        str(item.get("waiver_id", "")).strip()
        for item in actions
        if isinstance(item, dict) and str(item.get("waiver_id", "")).strip()
    }
    action_codes = {
        str(item.get("action_code", "")).strip()
        for item in actions
        if isinstance(item, dict) and str(item.get("action_code", "")).strip()
    }

    expected_action_waiver_ids = [
        str(item).strip()
        for item in match.get("action_waiver_ids", [])
        if isinstance(item, str) and item.strip()
    ]
    if expected_action_waiver_ids and not set(expected_action_waiver_ids).issubset(action_waiver_ids):
        return False

    expected_action_codes = [
        str(item).strip()
        for item in match.get("action_codes", [])
        if isinstance(item, str) and item.strip()
    ]
    if expected_action_codes and not set(expected_action_codes).issubset(action_codes):
        return False

    return True


def waiver_matches_report_scope(
    waiver: dict,
    policy_id: str | None,
    payload: dict,
    *,
    require_active: bool = True,
) -> bool:
    waiver_policy_id = str(waiver.get("policy_id", "")).strip()
    if waiver_policy_id and waiver_policy_id != str(policy_id or "").strip():
        return False
    return waiver_selectors_match_report(
        waiver,
        payload,
        require_active=require_active,
    )


def finding_codes_match_waiver(waiver: dict, finding: dict) -> bool:
    match = waiver.get("match", {})
    if not isinstance(match, dict):
        return False
    finding_codes = [
        str(item).strip()
        for item in match.get("finding_codes", [])
        if isinstance(item, str) and item.strip()
    ]
    return str(finding.get("code", "")).strip() in finding_codes


def waiver_matches_finding(
    waiver: dict,
    policy_id: str | None,
    payload: dict,
    finding: dict,
    *,
    require_active: bool = True,
) -> bool:
    if not waiver_matches_report_scope(waiver, policy_id, payload, require_active=require_active):
        return False
    return finding_codes_match_waiver(waiver, finding)


def apply_waivers_to_findings(
    payload: dict,
    waivers: list[dict],
    policy_id: str | None,
) -> tuple[int, int, list[dict]]:
    waived_finding_count = 0
    active_finding_count = 0
    waiver_summaries = [
        {
            "id": waiver.get("id"),
            "title": waiver.get("title"),
            "policy_id": waiver.get("policy_id"),
            "path": waiver.get("_path"),
            "expires_on": waiver.get("expires_on", ""),
            "active": is_waiver_active(waiver),
            "matched": False,
        }
        for waiver in waivers
    ]
    summary_by_id = {
        str(item.get("id", "")).strip(): item
        for item in waiver_summaries
        if isinstance(item.get("id"), str)
    }

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        return 0, 0, waiver_summaries

    for finding in findings:
        if not isinstance(finding, dict):
            active_finding_count += 1
            continue
        matched_waiver: dict | None = None
        for waiver in waivers:
            if waiver_matches_finding(waiver, policy_id, payload, finding):
                matched_waiver = waiver
                break

        if matched_waiver is None:
            finding["waived"] = False
            active_finding_count += 1
            continue

        waiver_id = str(matched_waiver.get("id", "")).strip()
        finding["waived"] = True
        finding["waiver_id"] = waiver_id
        finding["waiver_title"] = matched_waiver.get("title")
        finding["waiver_path"] = matched_waiver.get("_path")
        waived_finding_count += 1
        summary = summary_by_id.get(waiver_id)
        if summary is not None:
            summary["matched"] = True

    return active_finding_count, waived_finding_count, waiver_summaries


def build_gate_payload(
    history_path: Path,
    waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
    policy_payload: dict | None,
    policy_path: Path | None,
    gate_waiver_tokens: list[str],
    allowed_states: list[str],
) -> dict:
    report_payload = report_installed_baseline_history_waiver_source_reconcile.build_report_payload(
        history_path,
        waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )

    defaults = policy_defaults(policy_payload)
    findings: list[dict] = []
    if defaults["require_report_complete"] and report_payload.get("report_complete") is not True:
        findings.append(
            {
                "code": "incomplete_report",
                "message": "source-reconcile handoff is incomplete because one or more workflow summaries are missing",
            }
        )

    report_state = str(report_payload.get("report_state", "")).strip()
    if report_state not in allowed_states:
        findings.append(
            {
                "code": "disallowed_report_state",
                "message": f"report_state={report_state or '(empty)'} is not allowed by this gate",
            }
        )

    execution_summary = report_payload.get("source_reconcile_execution", {})
    if defaults["fail_on_blocked_execution"] and execution_summary.get("blocked_action_count", 0) > 0:
        findings.append(
            {
                "code": "blocked_execution",
                "message": "source-reconcile execution contains blocked actions that must be resolved before promotion",
            }
        )

    verification_summary = report_payload.get("source_reconcile_verification", {})
    if defaults["fail_on_pending_verification"] and verification_summary.get("pending_count", 0) > 0:
        findings.append(
            {
                "code": "pending_verification",
                "message": "source-reconcile verification still has pending actions and cannot be treated as complete",
            }
        )
    if defaults["fail_on_blocked_verification"] and verification_summary.get("blocked_count", 0) > 0:
        findings.append(
            {
                "code": "blocked_verification",
                "message": "source-reconcile verification contains blocked actions and requires follow-up",
            }
        )
    if defaults["fail_on_verification_drift"] and verification_summary.get("drift_count", 0) > 0:
        findings.append(
            {
                "code": "verification_drift",
                "message": "source-reconcile verification detected drift after execution",
            }
        )

    payload = {
        "history_path": str(resolve_repo_path(history_path)),
        "output_dir": display_path(output_dir),
        "target_root": report_payload.get("target_root", ""),
        "stage_dir": report_payload.get("stage_dir", ""),
        "policy_id": policy_payload.get("id") if isinstance(policy_payload, dict) else None,
        "policy_title": policy_payload.get("title") if isinstance(policy_payload, dict) else None,
        "policy_path": str(policy_path) if policy_path is not None else None,
        "policy_defaults": defaults,
        "allowed_states": allowed_states,
        "report_state": report_state,
        "report_complete": report_payload.get("report_complete", False),
        "report_summary_path": display_path(output_dir / "source-reconcile-report-summary.json"),
        "source_reconcile_execution_summary_path": report_payload.get("source_reconcile_execute_summary_path", ""),
        "source_reconcile_verify_summary_path": report_payload.get("source_reconcile_verify_summary_path", ""),
        "finding_count": len(findings),
        "findings": findings,
        "report": report_payload,
    }
    gate_waivers = resolve_requested_waivers(gate_waiver_tokens)
    active_finding_count, waived_finding_count, waiver_summaries = apply_waivers_to_findings(
        payload,
        gate_waivers,
        str(policy_payload.get("id")) if isinstance(policy_payload, dict) else None,
    )
    payload["gate_waivers"] = waiver_summaries
    payload["requested_gate_waiver_count"] = len(waiver_summaries)
    payload["matched_gate_waiver_count"] = sum(1 for item in waiver_summaries if item.get("matched"))
    payload["active_finding_count"] = active_finding_count
    payload["waived_finding_count"] = waived_finding_count
    payload["passes"] = active_finding_count == 0
    return payload


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Reconcile Gate",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Policy id: `{payload.get('policy_id', '')}`",
        f"- Allowed states: `{', '.join(payload.get('allowed_states', []))}`",
        f"- Report state: `{payload.get('report_state', '')}`",
        f"- Report complete: `{payload.get('report_complete', False)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Active findings: `{payload.get('active_finding_count', 0)}`",
        f"- Waived findings: `{payload.get('waived_finding_count', 0)}`",
        f"- Report summary: `{payload.get('report_summary_path', '')}`",
        "",
        "## Gate Waivers",
        "",
    ]
    gate_waivers = payload.get("gate_waivers", [])
    if not gate_waivers:
        lines.append("- No gate waivers requested.")
    else:
        for waiver in gate_waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` active=`{waiver.get('active', False)}` matched=`{waiver.get('matched', False)}`"
            )

    lines.extend([
        "",
        "## Findings",
        "",
    ])
    findings = payload.get("findings", [])
    if not findings:
        lines.append("- Gate passed with no findings.")
    else:
        for finding in findings:
            if finding.get("waived"):
                lines.append(
                    f"- `{finding.get('code', '')}` {finding.get('message', '')} waived_by=`{finding.get('waiver_id', '')}`"
                )
            else:
                lines.append(f"- `{finding.get('code', '')}` {finding.get('message', '')}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else report_installed_baseline_history_waiver_source_reconcile.DEFAULT_OUTPUT_DIR
    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    execute_summary_path = resolve_repo_path(args.execute_summary_path) if args.execute_summary_path else None
    policy_payload: dict | None = None
    policy_path: Path | None = None
    if args.policy:
        policy_payload, policy_path = resolve_policy_reference(args.policy)
    defaults = policy_defaults(policy_payload)
    allowed_states = normalize_allowed_states(args.allow_state or defaults["allowed_states"])

    payload = build_gate_payload(
        args.history,
        args.waiver,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
        policy_payload=policy_payload,
        policy_path=policy_path,
        gate_waiver_tokens=args.gate_waiver,
        allowed_states=allowed_states,
    )

    report_summary_json_path = output_dir / "source-reconcile-report-summary.json"
    report_summary_markdown_path = output_dir / "source-reconcile-report-summary.md"
    write_text(
        report_summary_json_path,
        render_json_payload(payload["report"]),
    )
    write_text(
        report_summary_markdown_path,
        report_installed_baseline_history_waiver_source_reconcile.render_markdown(payload["report"]),
    )

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else (output_dir / "source-reconcile-gate-summary.json")
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else (output_dir / "source-reconcile-gate-summary.md")
    write_text(summary_json_path, render_json_payload(payload))
    write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver source reconcile gate:")
        print(f"- History: {payload['history_path']}")
        print(f"- Report state: {payload['report_state']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")
        print(f"- Findings: {payload['finding_count']}")
        print(f"- Active findings: {payload['active_finding_count']}")
        print(f"- Waived findings: {payload['waived_finding_count']}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
