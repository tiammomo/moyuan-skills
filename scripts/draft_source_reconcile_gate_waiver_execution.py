#!/usr/bin/env python3
"""Generate execution drafts for source-reconcile gate waiver remediation."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from datetime import date, timedelta
from pathlib import Path

import audit_installed_baseline_history_waiver_source_reconcile_waivers
import check_installed_baseline_history_waiver_source_reconcile_gate
import remediate_installed_baseline_history_waiver_source_reconcile_waivers
import report_installed_baseline_history_waiver_source_reconcile
from market_utils import ROOT, repo_relative_path


DEFAULT_OUTPUT_DIR = report_installed_baseline_history_waiver_source_reconcile.DEFAULT_OUTPUT_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draft execution scaffolding for source-reconcile gate waiver remediation."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to prepare. Defaults to all known gate waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing source-reconcile artifacts and receiving execution summaries.",
    )
    parser.add_argument("--target-root", type=Path, help="Optional repo-root mirror used for source audits and verification.")
    parser.add_argument("--stage-dir", type=Path, help="Optional staging directory used for staged verification.")
    parser.add_argument("--execute-summary-path", type=Path, help="Optional source-reconcile execution summary JSON path.")
    parser.add_argument("--output-path", type=Path, help="Optional JSON summary output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown summary output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when follow-up execution is required.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def slugify(value: str) -> str:
    cleaned = [
        character.lower() if character.isalnum() else "-"
        for character in value.strip()
    ]
    slug = "".join(cleaned).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "waiver"


def iso_today() -> str:
    return date.today().isoformat()


def suggested_expiry(days: int = 90) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def path_suffix(path_value: str) -> str:
    normalized = path_value.replace("\\", "/").rstrip("/")
    if not normalized:
        return ""
    return normalized.split("/")[-1]


def sanitize_waiver_payload(waiver: dict) -> dict:
    payload = copy.deepcopy(waiver)
    payload.pop("_path", None)
    return payload


def build_policy_gate_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    policy_id: str,
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
) -> dict | None:
    if not policy_id:
        return None
    policy_payload, policy_path = check_installed_baseline_history_waiver_source_reconcile_gate.resolve_policy_reference(
        policy_id
    )
    return audit_installed_baseline_history_waiver_source_reconcile_waivers.build_gate_context_payload(
        history_path,
        source_waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
        policy_payload=policy_payload,
        policy_path=policy_path,
    )


def summarize_report_actions(payload: dict) -> list[dict]:
    report = payload.get("report", {})
    actions = report.get("actions", []) if isinstance(report, dict) else []
    candidates: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        waiver_id = str(action.get("waiver_id", "")).strip()
        action_code = str(action.get("action_code", "")).strip()
        if not waiver_id and not action_code:
            continue
        candidates.append(
            {
                "waiver_id": waiver_id,
                "action_code": action_code,
                "source_audit_state": str(action.get("source_audit_state", "")).strip(),
                "source_reconcile_mode": str(action.get("source_reconcile_mode", "")).strip(),
                "verification_state": str(action.get("verification_state", "")).strip(),
            }
        )
    return candidates


def summarize_active_findings(payload: dict) -> list[dict]:
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        return []
    summary: list[dict] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        if finding.get("waived"):
            continue
        code = str(finding.get("code", "")).strip()
        if not code:
            continue
        summary.append(
            {
                "code": code,
                "message": str(finding.get("message", "")).strip(),
            }
        )
    return summary


def choose_action_candidate(waiver: dict, action_candidates: list[dict]) -> dict | None:
    if not action_candidates:
        return None

    match = waiver.get("match", {})
    if not isinstance(match, dict):
        match = {}

    expected_waiver_ids = {
        str(item).strip()
        for item in match.get("action_waiver_ids", [])
        if isinstance(item, str) and item.strip()
    }
    expected_action_codes = {
        str(item).strip()
        for item in match.get("action_codes", [])
        if isinstance(item, str) and item.strip()
    }

    def score(candidate: dict) -> tuple[int, str, str]:
        points = 0
        if expected_waiver_ids and str(candidate.get("waiver_id", "")).strip() in expected_waiver_ids:
            points += 3
        if expected_action_codes and str(candidate.get("action_code", "")).strip() in expected_action_codes:
            points += 3
        if str(candidate.get("source_reconcile_mode", "")).strip():
            points += 1
        if str(candidate.get("verification_state", "")).strip() == "drifted":
            points += 1
        return (
            points,
            str(candidate.get("waiver_id", "")),
            str(candidate.get("action_code", "")),
        )

    return max(action_candidates, key=score)


def merge_strings(existing: list[str], suggested: list[str]) -> list[str]:
    existing_values = [str(item).strip() for item in existing if str(item).strip()]
    suggested_values = [str(item).strip() for item in suggested if str(item).strip()]
    intersection = sorted(set(existing_values) & set(suggested_values))
    if intersection:
        return intersection
    if suggested_values:
        return sorted(dict.fromkeys(suggested_values))
    return sorted(dict.fromkeys(existing_values))


def apply_scope_selectors(match: dict, gate_payload: dict) -> None:
    report_state = str(gate_payload.get("report_state", "")).strip()
    if report_state:
        match["report_states"] = [report_state]
    elif "report_states" in match:
        match.pop("report_states", None)

    actual_target_root_suffix = path_suffix(str(gate_payload.get("target_root", "")))
    if actual_target_root_suffix:
        match["target_root_suffix"] = actual_target_root_suffix
    elif "target_root_suffix" in match:
        match.pop("target_root_suffix", None)

    if "stage_dir_suffix" in match:
        actual_stage_suffix = path_suffix(str(gate_payload.get("stage_dir", "")))
        if actual_stage_suffix:
            match["stage_dir_suffix"] = actual_stage_suffix
        else:
            match.pop("stage_dir_suffix", None)


def apply_action_selectors(match: dict, candidate: dict | None) -> None:
    if candidate is None:
        return
    waiver_id = str(candidate.get("waiver_id", "")).strip()
    action_code = str(candidate.get("action_code", "")).strip()
    if waiver_id and ("action_waiver_ids" in match or "action_codes" not in match):
        match["action_waiver_ids"] = [waiver_id]
    if action_code and ("action_codes" in match or "action_waiver_ids" not in match):
        match["action_codes"] = [action_code]


def build_review_metadata(strategy: str, waiver_result: dict, gate_payload: dict | None, action_candidate: dict | None) -> dict:
    metadata: dict = {
        "generated_at": iso_today(),
        "strategy": strategy,
        "finding_codes": [
            str(finding.get("code", "")).strip()
            for finding in waiver_result.get("findings", [])
            if isinstance(finding, dict) and str(finding.get("code", "")).strip()
        ],
        "review_required": True,
    }
    if gate_payload is not None:
        metadata["candidate_report_scope"] = {
            "policy_id": gate_payload.get("policy_id"),
            "report_state": gate_payload.get("report_state", ""),
            "target_root_suffix": path_suffix(str(gate_payload.get("target_root", ""))),
            "stage_dir_suffix": path_suffix(str(gate_payload.get("stage_dir", ""))),
            "active_finding_codes": [
                item.get("code")
                for item in summarize_active_findings(gate_payload)
            ],
        }
    if action_candidate is not None:
        metadata["candidate_action"] = {
            "waiver_id": action_candidate.get("waiver_id", ""),
            "action_code": action_candidate.get("action_code", ""),
            "source_audit_state": action_candidate.get("source_audit_state", ""),
            "source_reconcile_mode": action_candidate.get("source_reconcile_mode", ""),
            "verification_state": action_candidate.get("verification_state", ""),
        }
    return metadata


def build_renewal_draft(waiver: dict, waiver_result: dict, gate_payload: dict | None, action_candidate: dict | None) -> dict:
    payload = sanitize_waiver_payload(waiver)
    approval = payload.setdefault("approval", {})
    approval["approved_at"] = iso_today()
    previous_reason = str(approval.get("reason", "")).strip()
    approval["reason"] = (
        f"TODO: refresh the approval rationale for source-reconcile gate waiver '{payload.get('id', '')}'. "
        f"Previous reason: {previous_reason}"
    )
    payload["expires_on"] = suggested_expiry()
    payload["_draft"] = build_review_metadata("renew", waiver_result, gate_payload, action_candidate)
    payload["_draft"]["review_notes"] = [
        "Confirm the source-reconcile exception is still intentional before renewing it.",
        "Replace the TODO approval reason with a reviewer-approved explanation.",
        "Adjust expires_on to the real renewal window before promoting the draft.",
    ]
    return payload


def build_retarget_draft(waiver: dict, waiver_result: dict, gate_payload: dict, action_candidate: dict | None) -> dict:
    payload = sanitize_waiver_payload(waiver)
    match = payload.setdefault("match", {})
    existing_finding_codes = list(match.get("finding_codes", []))
    apply_scope_selectors(match, gate_payload)
    apply_action_selectors(match, action_candidate)
    match["finding_codes"] = merge_strings(existing_finding_codes, existing_finding_codes)

    approval = payload.setdefault("approval", {})
    approval["approved_at"] = iso_today()
    approval["reason"] = (
        f"TODO: confirm the refreshed source-reconcile report scope for waiver '{payload.get('id', '')}' "
        "and replace this placeholder with the reviewed approval rationale."
    )
    payload["_draft"] = build_review_metadata("retarget", waiver_result, gate_payload, action_candidate)
    payload["_draft"]["review_notes"] = [
        "Confirm the current report scope is still the intended place to waive this finding.",
        "Review target_root_suffix and any action selectors before updating the source waiver file.",
        "Delete the source waiver instead if this exception is no longer needed.",
    ]
    return payload


def build_replacement_draft(waiver: dict, waiver_result: dict, gate_payload: dict, action_candidate: dict | None) -> dict:
    payload = sanitize_waiver_payload(waiver)
    match = payload.setdefault("match", {})
    active_finding_codes = [item.get("code") for item in summarize_active_findings(gate_payload)]
    existing_finding_codes = list(match.get("finding_codes", []))
    match["finding_codes"] = merge_strings(existing_finding_codes, active_finding_codes)
    apply_scope_selectors(match, gate_payload)
    apply_action_selectors(match, action_candidate)

    approval = payload.setdefault("approval", {})
    approval["approved_at"] = iso_today()
    approval["reason"] = (
        f"TODO: confirm the replacement source-reconcile finding scope for waiver '{payload.get('id', '')}' "
        "and replace this placeholder with the reviewed approval rationale."
    )
    payload["_draft"] = build_review_metadata("replace", waiver_result, gate_payload, action_candidate)
    payload["_draft"]["review_notes"] = [
        "Confirm the proposed active finding codes represent the exception that still needs approval.",
        "Drop the gate waiver instead of replacing it if no current source-reconcile finding should stay waived.",
    ]
    return payload


def build_remove_review(action: dict, waiver: dict, waiver_result: dict) -> dict:
    return {
        "waiver_id": waiver.get("id"),
        "action_code": action.get("code"),
        "mode": "remove_review",
        "priority": action.get("priority"),
        "summary": action.get("summary"),
        "why": action.get("why"),
        "source_path": str(waiver.get("_path", "")),
        "delete_path": str(waiver.get("_path", "")),
        "review_steps": list(action.get("suggested_steps", [])),
        "finding_codes": [
            str(finding.get("code", "")).strip()
            for finding in waiver_result.get("findings", [])
            if isinstance(finding, dict) and str(finding.get("code", "")).strip()
        ],
    }


def build_policy_review(action: dict, waiver: dict, waiver_result: dict) -> dict:
    return {
        "waiver_id": waiver.get("id"),
        "action_code": action.get("code"),
        "mode": "policy_review",
        "priority": action.get("priority"),
        "summary": action.get("summary"),
        "why": action.get("why"),
        "source_path": str(waiver.get("_path", "")),
        "review_steps": list(action.get("suggested_steps", [])),
        "candidate_policy_ids": list(action.get("candidate_policy_ids", [])),
        "finding_codes": [
            str(finding.get("code", "")).strip()
            for finding in waiver_result.get("findings", [])
            if isinstance(finding, dict) and str(finding.get("code", "")).strip()
        ],
    }


def build_execution_artifacts(
    history_path: Path,
    source_waiver_tokens: list[str],
    waiver: dict,
    waiver_result: dict,
    action: dict,
    *,
    output_dir: Path | None,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
) -> tuple[dict, list[tuple[Path, str]]]:
    artifacts: list[tuple[Path, str]] = []
    waiver_id = str(waiver.get("id", "")).strip()
    policy_id = str(waiver.get("policy_id", "")).strip()
    gate_payload = build_policy_gate_payload(
        history_path,
        source_waiver_tokens,
        policy_id,
        output_dir=output_dir if output_dir is not None else DEFAULT_OUTPUT_DIR,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )
    action_candidates = summarize_report_actions(gate_payload or {})
    action_candidate = choose_action_candidate(waiver, action_candidates)
    active_findings = summarize_active_findings(gate_payload or {})
    action_code = str(action.get("code", "")).strip()
    slug = slugify(waiver_id)
    base_dir = output_dir / "waivers" / slug if output_dir is not None else None

    def candidate_scope(strategy: str) -> dict:
        return build_review_metadata(strategy, waiver_result, gate_payload, action_candidate).get(
            "candidate_report_scope",
            {},
        )

    def candidate_action_summary(strategy: str) -> dict:
        return build_review_metadata(strategy, waiver_result, gate_payload, action_candidate).get(
            "candidate_action",
            {},
        )

    if action_code == "renew_or_remove":
        draft_payload = build_renewal_draft(waiver, waiver_result, gate_payload, action_candidate)
        draft_relative = repo_relative_path(base_dir / "renewal-draft.json") if base_dir is not None else ""
        if base_dir is not None:
            artifacts.append((base_dir / "renewal-draft.json", json.dumps(draft_payload, indent=2, ensure_ascii=False) + "\n"))
        return (
            {
                "waiver_id": waiver_id,
                "action_code": action_code,
                "mode": "draft_update",
                "priority": action.get("priority"),
                "summary": action.get("summary"),
                "why": action.get("why"),
                "source_path": str(waiver.get("_path", "")),
                "draft_path": draft_relative,
                "delete_path": str(waiver.get("_path", "")),
                "review_steps": list(action.get("suggested_steps", [])),
                "candidate_policy_ids": list(action.get("candidate_policy_ids", [])),
                "candidate_report_scope": candidate_scope("renew"),
                "candidate_action": candidate_action_summary("renew"),
                "candidate_finding_codes": [item.get("code") for item in active_findings],
            },
            artifacts,
        )

    if action_code == "retarget_or_remove":
        if gate_payload is not None:
            draft_payload = build_retarget_draft(waiver, waiver_result, gate_payload, action_candidate)
            draft_relative = repo_relative_path(base_dir / "retarget-draft.json") if base_dir is not None else ""
            if base_dir is not None:
                artifacts.append((base_dir / "retarget-draft.json", json.dumps(draft_payload, indent=2, ensure_ascii=False) + "\n"))
            return (
                {
                    "waiver_id": waiver_id,
                    "action_code": action_code,
                    "mode": "draft_update",
                    "priority": action.get("priority"),
                    "summary": action.get("summary"),
                    "why": action.get("why"),
                    "source_path": str(waiver.get("_path", "")),
                    "draft_path": draft_relative,
                    "delete_path": str(waiver.get("_path", "")),
                    "review_steps": list(action.get("suggested_steps", [])),
                    "candidate_policy_ids": list(action.get("candidate_policy_ids", [])),
                    "candidate_report_scope": candidate_scope("retarget"),
                    "candidate_action": candidate_action_summary("retarget"),
                    "candidate_finding_codes": [item.get("code") for item in active_findings],
                },
                artifacts,
            )
        review_payload = build_remove_review(action, waiver, waiver_result)
        if base_dir is not None:
            artifacts.append((base_dir / "remove-review.json", json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n"))
        return (
            {
                **review_payload,
                "review_path": repo_relative_path(base_dir / "remove-review.json") if base_dir is not None else "",
                "candidate_policy_ids": list(action.get("candidate_policy_ids", [])),
                "candidate_report_scope": {},
                "candidate_action": {},
                "candidate_finding_codes": [item.get("code") for item in active_findings],
            },
            artifacts,
        )

    if action_code == "retire_or_replace":
        if gate_payload is not None and active_findings:
            draft_payload = build_replacement_draft(waiver, waiver_result, gate_payload, action_candidate)
            draft_relative = repo_relative_path(base_dir / "replacement-draft.json") if base_dir is not None else ""
            if base_dir is not None:
                artifacts.append((base_dir / "replacement-draft.json", json.dumps(draft_payload, indent=2, ensure_ascii=False) + "\n"))
            return (
                {
                    "waiver_id": waiver_id,
                    "action_code": action_code,
                    "mode": "draft_update",
                    "priority": action.get("priority"),
                    "summary": action.get("summary"),
                    "why": action.get("why"),
                    "source_path": str(waiver.get("_path", "")),
                    "draft_path": draft_relative,
                    "delete_path": str(waiver.get("_path", "")),
                    "review_steps": list(action.get("suggested_steps", [])),
                    "candidate_policy_ids": list(action.get("candidate_policy_ids", [])),
                    "candidate_report_scope": candidate_scope("replace"),
                    "candidate_action": candidate_action_summary("replace"),
                    "candidate_finding_codes": [item.get("code") for item in active_findings],
                },
                artifacts,
            )
        review_payload = build_remove_review(action, waiver, waiver_result)
        if base_dir is not None:
            artifacts.append((base_dir / "remove-review.json", json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n"))
        return (
            {
                **review_payload,
                "review_path": repo_relative_path(base_dir / "remove-review.json") if base_dir is not None else "",
                "candidate_policy_ids": list(action.get("candidate_policy_ids", [])),
                "candidate_report_scope": {},
                "candidate_action": {},
                "candidate_finding_codes": [item.get("code") for item in active_findings],
            },
            artifacts,
        )

    review_payload = build_policy_review(action, waiver, waiver_result)
    if base_dir is not None:
        artifacts.append((base_dir / "policy-review.json", json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n"))
    return (
        {
            **review_payload,
            "review_path": repo_relative_path(base_dir / "policy-review.json") if base_dir is not None else "",
            "candidate_report_scope": {},
            "candidate_action": {},
            "candidate_finding_codes": [item.get("code") for item in active_findings],
        },
        artifacts,
    )


def write_execution_artifacts(base_dir: Path, waiver_summary: dict, action_summaries: list[dict], files: list[tuple[Path, str]]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    execution_payload = dict(waiver_summary)
    execution_payload["execution_actions"] = action_summaries
    write_text(base_dir / "execution.json", json.dumps(execution_payload, indent=2, ensure_ascii=False) + "\n")

    markdown_lines = [
        f"# Source Reconcile Gate Waiver Execution Draft: {waiver_summary.get('id', '')}",
        "",
        f"- Source path: `{waiver_summary.get('path', '')}`",
        f"- Findings: `{len(waiver_summary.get('findings', []))}`",
        f"- Needs remediation: `{waiver_summary.get('needs_remediation', False)}`",
        "",
        "## Actions",
        "",
    ]
    if not action_summaries:
        markdown_lines.append("- No execution actions required.")
    else:
        for action in action_summaries:
            markdown_lines.append(
                f"- `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` priority=`{action.get('priority', '')}`"
            )
            markdown_lines.append(f"  summary: {action.get('summary', '')}")
            draft_path = str(action.get("draft_path", "")).strip()
            review_path = str(action.get("review_path", "")).strip()
            if draft_path:
                markdown_lines.append(f"  draft: `{draft_path}`")
            if review_path:
                markdown_lines.append(f"  review: `{review_path}`")
    write_text(base_dir / "execution.md", "\n".join(markdown_lines).rstrip() + "\n")

    for path, content in files:
        write_text(path, content)


def build_execution_payload(
    history_path: Path,
    source_waiver_tokens: list[str],
    gate_waiver_tokens: list[str],
    *,
    output_dir: Path,
    target_root: Path | None,
    stage_dir: Path | None,
    execute_summary_path: Path | None,
    persist_artifacts: bool,
) -> dict:
    remediation_payload = remediate_installed_baseline_history_waiver_source_reconcile_waivers.build_remediation_payload(
        history_path,
        source_waiver_tokens,
        gate_waiver_tokens,
        output_dir=output_dir,
        target_root=target_root,
        stage_dir=stage_dir,
        execute_summary_path=execute_summary_path,
    )
    actual_waivers = audit_installed_baseline_history_waiver_source_reconcile_waivers.resolve_audited_gate_waivers(
        gate_waiver_tokens
    )
    waivers_by_id = {
        str(waiver.get("id", "")).strip(): waiver
        for waiver in actual_waivers
        if isinstance(waiver, dict) and str(waiver.get("id", "")).strip()
    }

    artifact_root = output_dir / "source-reconcile-gate-waiver-execution"
    waiver_payloads: list[dict] = []
    execution_count = 0
    draft_count = 0
    review_count = 0

    for waiver_summary in remediation_payload.get("waivers", []):
        if not isinstance(waiver_summary, dict):
            continue
        waiver_id = str(waiver_summary.get("id", "")).strip()
        source_waiver = waivers_by_id.get(waiver_id)
        actions_summary: list[dict] = []
        artifact_files: list[tuple[Path, str]] = []

        if source_waiver is not None:
            for action in waiver_summary.get("actions", []):
                if not isinstance(action, dict):
                    continue
                execution_summary, files = build_execution_artifacts(
                    history_path,
                    source_waiver_tokens,
                    source_waiver,
                    waiver_summary,
                    action,
                    output_dir=artifact_root if persist_artifacts else None,
                    target_root=target_root,
                    stage_dir=stage_dir,
                    execute_summary_path=execute_summary_path,
                )
                actions_summary.append(execution_summary)
                artifact_files.extend(files)

        execution_count += len(actions_summary)
        draft_count += sum(1 for item in actions_summary if item.get("mode") == "draft_update")
        review_count += sum(1 for item in actions_summary if item.get("mode") != "draft_update")

        waiver_payload = dict(waiver_summary)
        waiver_payload["execution_actions"] = actions_summary
        if persist_artifacts and actions_summary:
            waiver_dir = artifact_root / "waivers" / slugify(waiver_id)
            write_execution_artifacts(waiver_dir, waiver_summary, actions_summary, artifact_files)
            waiver_payload["artifact_dir"] = repo_relative_path(waiver_dir)
        else:
            waiver_payload["artifact_dir"] = ""
        waiver_payloads.append(waiver_payload)

    return {
        "history_path": remediation_payload.get("history_path", ""),
        "output_dir": repo_relative_path(output_dir) if persist_artifacts else "",
        "artifact_root": repo_relative_path(artifact_root) if persist_artifacts else "",
        "target_root": remediation_payload.get("target_root", ""),
        "stage_dir": remediation_payload.get("stage_dir", ""),
        "waiver_count": remediation_payload.get("waiver_count", 0),
        "finding_count": remediation_payload.get("finding_count", 0),
        "remediation_count": remediation_payload.get("remediation_count", 0),
        "execution_count": execution_count,
        "draft_count": draft_count,
        "review_count": review_count,
        "passes": execution_count == 0,
        "waivers": waiver_payloads,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Source Reconcile Gate Waiver Execution Drafts",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
        f"- Artifact root: `{payload.get('artifact_root', '')}`",
        f"- Target root: `{payload.get('target_root', '')}`",
        f"- Stage dir: `{payload.get('stage_dir', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Remediation actions: `{payload.get('remediation_count', 0)}`",
        f"- Execution actions: `{payload.get('execution_count', 0)}`",
        f"- Draft updates: `{payload.get('draft_count', 0)}`",
        f"- Review-only actions: `{payload.get('review_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Waiver Execution Packs",
        "",
    ]

    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No waivers analyzed.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` actions=`{len(waiver.get('execution_actions', []))}` artifact_dir=`{waiver.get('artifact_dir', '')}`"
            )
            actions = waiver.get("execution_actions", [])
            if not actions:
                lines.append("  - no execution actions required")
                continue
            for action in actions:
                location = str(action.get("draft_path", "")).strip() or str(action.get("review_path", "")).strip() or "(inline only)"
                lines.append(
                    f"  - `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` location=`{location}`"
                )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_root = resolve_repo_path(args.target_root) if args.target_root else None
    stage_dir = resolve_repo_path(args.stage_dir) if args.stage_dir else None
    execute_summary_path = resolve_repo_path(args.execute_summary_path) if args.execute_summary_path else None
    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else None

    temp_dir_handle: tempfile.TemporaryDirectory[str] | None = None
    if output_dir is None:
        temp_dir_handle = tempfile.TemporaryDirectory(prefix="source-reconcile-gate-waiver-execution-", dir=ROOT / "dist")
        working_output_dir = Path(temp_dir_handle.name)
        persist_artifacts = False
    else:
        working_output_dir = output_dir
        persist_artifacts = True

    try:
        payload = build_execution_payload(
            args.history,
            args.waiver,
            args.gate_waiver,
            output_dir=working_output_dir,
            target_root=target_root,
            stage_dir=stage_dir,
            execute_summary_path=execute_summary_path,
            persist_artifacts=persist_artifacts,
        )

        summary_json_path = resolve_repo_path(args.output_path) if args.output_path else None
        summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else None
        if persist_artifacts and summary_json_path is None:
            summary_json_path = working_output_dir / "source-reconcile-gate-waiver-execution-summary.json"
        if persist_artifacts and summary_markdown_path is None:
            summary_markdown_path = working_output_dir / "source-reconcile-gate-waiver-execution-summary.md"

        if summary_json_path is not None:
            write_text(summary_json_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        if summary_markdown_path is not None:
            write_text(summary_markdown_path, render_markdown(payload))

        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("Installed baseline history waiver source reconcile gate waiver execution drafts:")
            print(f"- History: {payload['history_path']}")
            print(f"- Waivers: {payload['waiver_count']}")
            print(f"- Execution actions: {payload['execution_count']}")
            print(f"- Draft updates: {payload['draft_count']}")
            print(f"- Review-only actions: {payload['review_count']}")
            print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

        if args.strict and not payload["passes"]:
            return 1
        return 0
    finally:
        if temp_dir_handle is not None:
            temp_dir_handle.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
