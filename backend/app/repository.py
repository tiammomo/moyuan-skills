from __future__ import annotations

import hashlib
import json
import re
import shlex
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .config import Settings, get_settings


VALID_CHANNELS = ("stable", "beta", "internal")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_sort_key(value: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        return ""
    candidate = normalized[:-1] + "+00:00" if normalized.endswith("Z") else normalized
    try:
        return datetime.fromisoformat(candidate).astimezone(timezone.utc).isoformat()
    except ValueError:
        return normalized


def _file_token(path: Path) -> str:
    if not path.is_file():
        return ""
    stat = path.stat()
    return f"{stat.st_mtime_ns}:{stat.st_size}"


def _build_waiver_apply_approval_fingerprint(
    *,
    report_summary_path: Path,
    apply_execute_summary_path: Path,
    verify_summary_path: Path,
    report_payload: dict[str, Any] | None,
) -> str:
    fingerprint_payload = {
        "report_summary_path": str(report_summary_path),
        "report_summary_token": _file_token(report_summary_path),
        "apply_execute_summary_path": str(apply_execute_summary_path),
        "apply_execute_summary_token": _file_token(apply_execute_summary_path),
        "verify_summary_path": str(verify_summary_path),
        "verify_summary_token": _file_token(verify_summary_path),
        "report_state": str(report_payload.get("report_state", "")).strip() if isinstance(report_payload, dict) else "",
        "action_count": int(report_payload.get("action_count", 0)) if isinstance(report_payload, dict) else 0,
        "written_change_count": (
            int(report_payload.get("apply_execution", {}).get("written_update_count", 0))
            + int(report_payload.get("apply_execution", {}).get("written_delete_count", 0))
        )
        if isinstance(report_payload, dict)
        else 0,
        "verified_count": int(report_payload.get("apply_verification", {}).get("verified_count", 0))
        if isinstance(report_payload, dict)
        else 0,
    }
    return hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def _display_repo_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def _first_paragraph(markdown: str) -> str:
    lines = [line.strip() for line in markdown.splitlines()]
    buffer: list[str] = []
    started = False
    for line in lines:
        if not line:
            if started and buffer:
                break
            continue
        if line.startswith("#") and not started:
            continue
        started = True
        buffer.append(line)
    return " ".join(buffer).strip()


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _collect_waiver_apply_paths(report_payload: dict[str, Any] | None) -> dict[str, list[str]]:
    if not isinstance(report_payload, dict):
        return {
            "source_paths": [],
            "artifact_paths": [],
        }

    source_paths: list[str] = []
    artifact_paths: list[str] = []
    for action in report_payload.get("actions", []):
        if not isinstance(action, dict):
            continue
        source_paths.extend(
            [
                str(action.get("apply_source_path", "")),
                str(action.get("apply_execute_write_path", "")),
            ]
        )
        artifact_paths.extend(
            [
                str(action.get("apply_target_path", "")),
                str(action.get("apply_patch_path", "")),
                str(action.get("apply_review_artifact_path", "")),
                str(action.get("apply_execute_stage_path", "")),
                str(action.get("verification_path", "")),
            ]
        )

    return {
        "source_paths": _dedupe_strings(source_paths),
        "artifact_paths": _dedupe_strings(artifact_paths),
    }


def _build_waiver_apply_write_handoff(
    *,
    history_exists: bool,
    governance_summary_exists: bool,
    report_payload: dict[str, Any] | None,
    display_stage_dir: str,
    display_apply_summary_path: str,
    display_apply_execute_summary_path: str,
    display_verify_summary_path: str,
    display_report_summary_path: str,
    write_command: str,
    verify_command: str,
) -> dict[str, Any]:
    report_state = str(report_payload.get("report_state", "")).strip() if isinstance(report_payload, dict) else ""
    action_count = int(report_payload.get("action_count", 0)) if isinstance(report_payload, dict) else 0
    apply_summary = report_payload.get("apply", {}) if isinstance(report_payload, dict) else {}
    apply_execution = report_payload.get("apply_execution", {}) if isinstance(report_payload, dict) else {}
    apply_verification = report_payload.get("apply_verification", {}) if isinstance(report_payload, dict) else {}

    blocked_action_count = int(apply_execution.get("blocked_action_count", 0))
    blocked_manual_review_count = int(apply_execution.get("blocked_manual_review_count", 0))
    source_mismatch_count = int(apply_execution.get("source_mismatch_count", 0))
    pending_count = int(apply_verification.get("pending_count", 0))
    blocked_count = int(apply_verification.get("blocked_count", 0))
    drift_count = int(apply_verification.get("drift_count", 0))
    verified_count = int(apply_verification.get("verified_count", 0))
    written_count = int(apply_execution.get("written_update_count", 0)) + int(
        apply_execution.get("written_delete_count", 0)
    )
    write_mode = bool(apply_execution.get("write_mode", False))
    manual_review_count = int(apply_summary.get("manual_review_count", 0))

    path_summary = _collect_waiver_apply_paths(report_payload if isinstance(report_payload, dict) else None)
    source_paths = path_summary["source_paths"]
    report_apply_summary_path = str(report_payload.get("apply_summary_path", "")).strip() if isinstance(report_payload, dict) else ""
    report_apply_execute_summary_path = (
        str(report_payload.get("apply_execute_summary_path", "")).strip() if isinstance(report_payload, dict) else ""
    )
    report_verify_summary_path = str(report_payload.get("apply_verify_summary_path", "")).strip() if isinstance(report_payload, dict) else ""
    artifact_paths = _dedupe_strings(
        [
            display_report_summary_path if report_payload else "",
            report_apply_summary_path or display_apply_summary_path,
            report_apply_execute_summary_path or display_apply_execute_summary_path if apply_execution.get("available", False) else "",
            report_verify_summary_path or display_verify_summary_path if report_payload else "",
            display_stage_dir if apply_execution.get("available", False) else "",
            *path_summary["artifact_paths"],
        ]
    )

    blocked_reasons: list[str] = []
    checklist: list[str] = []
    commands_available = bool(report_payload) and action_count > 0

    if not history_exists:
        blocked_reasons.append("Capture a retained baseline history before approving any governance write handoff.")
    if history_exists and not governance_summary_exists:
        blocked_reasons.append("Refresh governance summary before approving any governance write handoff.")
    if history_exists and governance_summary_exists and not report_payload:
        blocked_reasons.append("Prepare the waiver/apply handoff pack first so the write handoff can reference real review artifacts.")
    if report_payload and action_count == 0:
        blocked_reasons.append("The current apply handoff report does not contain any repo-governance changes to write.")
    if report_state == "needs_execution":
        blocked_reasons.append("Stage the reviewed apply changes first so the write handoff references verified staging artifacts.")
    if blocked_action_count > 0:
        blocked_reasons.append(f"{blocked_action_count} apply action(s) are still blocked during execution.")
    if blocked_manual_review_count > 0:
        blocked_reasons.append(
            f"{blocked_manual_review_count} blocked action(s) remain manual-review only and cannot move into automatic write mode."
        )
    if source_mismatch_count > 0:
        blocked_reasons.append(f"{source_mismatch_count} governance source file(s) no longer match the reviewed apply pack.")
    if pending_count > 0:
        blocked_reasons.append(f"{pending_count} verification result(s) are still pending.")
    if blocked_count > 0:
        blocked_reasons.append(f"{blocked_count} verification result(s) still require follow-up.")
    if drift_count > 0 or report_state == "drifted":
        blocked_reasons.append(f"{max(drift_count, 1)} verification drift finding(s) must be cleared before write approval.")
    if write_mode and report_state == "verified":
        blocked_reasons.append("The latest verified report already reflects a CLI write run.")

    state = "pending"
    title = "Write handoff pending"
    summary = "Prepare and review the waiver/apply pack before handing off a repo-governance write command."

    if write_mode and report_state == "verified":
        state = "completed"
        title = "CLI write already verified"
        summary = (
            f"The latest CLI write run already wrote {written_count} governance source change(s), "
            "and verification still matches the reviewed artifacts."
        )
    elif drift_count > 0 or report_state == "drifted":
        state = "drifted"
        title = "Write handoff paused for drift"
        summary = (
            f"Verification currently reports {max(drift_count, 1)} drift finding(s). "
            "Restage or rebuild the reviewed pack before any CLI write."
        )
    elif blocked_action_count > 0 or blocked_count > 0 or source_mismatch_count > 0:
        state = "blocked"
        title = "Write handoff blocked"
        summary = (
            "The current apply report still contains blocked execution or verification findings, "
            "so the repo-governance write handoff must stay disabled."
        )
    elif report_state == "verified":
        state = "ready"
        title = "Ready for CLI write"
        summary = (
            f"{verified_count} verified action(s) currently match the staged governance targets. "
            "You can now hand off the explicit CLI write and verify commands for operator approval."
        )
    elif report_payload and action_count == 0:
        state = "pending"
        title = "No write actions available"
        summary = "The latest handoff refresh did not produce any repo-governance changes that should be written."
    elif report_state == "needs_verification_followup":
        state = "pending"
        title = "Write handoff pending"
        summary = "Execution records exist, but verification still needs follow-up before write approval can be handed off."
    elif report_state == "needs_execution":
        state = "pending"
        title = "Write handoff pending"
        summary = "Stage the reviewed apply changes first so the handoff references verified staging artifacts instead of patches alone."
    elif not history_exists:
        summary = "Capture a retained baseline history first so the write handoff can stay anchored to a reviewable baseline."
    elif not governance_summary_exists:
        summary = "Refresh governance summary first so the write handoff can stay anchored to the latest review state."
    elif not report_payload:
        summary = "Prepare the waiver/apply handoff first so the UI can package a concrete CLI write handoff."
    elif report_state:
        summary = f'The current waiver/apply report is "{report_state}" and is not yet ready for a CLI write handoff.'

    if state == "ready":
        checklist = [
            "Review the planned governance source files, patch artifacts, and staged outputs together before approval.",
            "Capture explicit operator approval outside the page before running the CLI write command.",
            "Run the CLI write command from the repo root and keep the refreshed execute summary for the change record.",
            "Immediately rerun the verify command and confirm the written targets still match the reviewed artifacts.",
        ]
    elif state == "completed":
        checklist = [
            "Keep the verified execute and verify summaries with the review record for this governance write.",
            "Rerun the verify command after any manual edit to the same governance source files.",
            "Use normal Git review before merging or releasing the written governance changes.",
        ]
    elif state == "drifted":
        checklist = [
            "Inspect the drift findings and compare them with the staged outputs before attempting another write.",
            "Restage or rebuild the apply pack so verification returns to a clean verified state.",
            "Only hand off the CLI write command again after drift is cleared.",
        ]
    elif state == "blocked":
        checklist = [
            "Resolve the blocked execution or verification findings before handing off any write command.",
            "Review source mismatch and manual-review actions in the prepared artifacts instead of forcing write mode.",
            "Re-run stage or verify once the blockers are cleared.",
        ]
    else:
        checklist = [
            "Prepare the waiver/apply handoff so the page has concrete review artifacts to reference.",
            "Stage the reviewed governance changes and wait for a clean verification pass.",
            "Only after that should the CLI write command be handed off for explicit approval.",
        ]
        if manual_review_count > 0:
            checklist.append(
                f"Keep {manual_review_count} manual-review artifact(s) outside the automatic write path until they are explicitly resolved."
            )

    rollback_hint = (
        "If approval changes after write, inspect `git diff -- governance` and revert through your normal Git review workflow; "
        "the UI still does not perform repo-source rollback for you."
        if state in {"ready", "completed"}
        else (
            f"No repo-source write has been triggered from this page yet. If you only need to discard staged artifacts, clear `{display_stage_dir}` and rerun stage."
            if display_stage_dir
            else "No repo-source write has been triggered from this page yet."
        )
    )

    evidence_entries = [
        {
            "label": "Apply report",
            "value": display_report_summary_path if report_payload else "-",
        },
        {
            "label": "Apply summary",
            "value": report_apply_summary_path or display_apply_summary_path if report_payload else "-",
        },
        {
            "label": "Execute summary",
            "value": report_apply_execute_summary_path or display_apply_execute_summary_path
            if apply_execution.get("available", False)
            else "-",
        },
        {
            "label": "Verify summary",
            "value": report_verify_summary_path or display_verify_summary_path if report_payload else "-",
        },
        {
            "label": "Write target root",
            "value": str(apply_verification.get("target_root", "")).strip()
            or str(apply_execution.get("target_root", "")).strip()
            or "-",
        },
        {
            "label": "Stage directory",
            "value": display_stage_dir if apply_execution.get("available", False) else "-",
        },
        {
            "label": "Written changes",
            "value": str(written_count),
        },
        {
            "label": "Verified actions",
            "value": str(verified_count),
        },
        {
            "label": "Verification drift",
            "value": str(drift_count),
        },
    ]
    evidence_state = "pending"
    evidence_title = "Evidence pack pending"
    evidence_summary = "Prepare and stage the latest apply pack first so this page can point to real execution and verification evidence."
    evidence_follow_ups = [
        "Keep the review artifacts and staged outputs together before asking anyone to run the CLI write.",
        "Use the verify summary as the last gate before the write handoff is approved.",
    ]

    if write_mode and report_state == "verified":
        evidence_state = "post_write_verified"
        evidence_title = "Post-write evidence ready"
        evidence_summary = (
            f"The latest CLI write run recorded {written_count} written change(s), "
            "and the refreshed verify summary still matches the reviewed artifacts."
        )
        evidence_follow_ups = [
            "Keep the execute summary, verify summary, and aggregate report with the approval record.",
            "Re-run the verify command after any manual edit to the same governance source files.",
            "Use normal Git review before merging or releasing the written governance updates.",
        ]
    elif write_mode and report_state == "drifted":
        evidence_state = "post_write_drifted"
        evidence_title = "Post-write evidence needs follow-up"
        evidence_summary = (
            f"The latest CLI write run exists, but verification now reports {max(drift_count, 1)} drift finding(s). "
            "Review the written targets again before treating the evidence pack as complete."
        )
        evidence_follow_ups = [
            "Inspect the written target root and compare it with the reviewed target artifacts.",
            "Re-run the verify command after restoring or restaging the drifted files.",
        ]
    elif write_mode:
        evidence_state = "post_write_pending"
        evidence_title = "Post-write evidence pending verification"
        evidence_summary = (
            "A CLI write run is recorded, but the latest verification summary still needs follow-up before the evidence pack is complete."
        )
        evidence_follow_ups = [
            "Re-run the verify command and make sure the written targets still match the reviewed artifacts.",
            "Keep the partial write evidence out of the final approval record until verification is clean.",
        ]
    elif state == "ready":
        evidence_state = "pre_write_ready"
        evidence_title = "Pre-write evidence ready"
        evidence_summary = (
            f"The staged governance targets currently have {verified_count} verified action(s), "
            "so the evidence pack is ready to support an explicit CLI write approval."
        )
        evidence_follow_ups = [
            "Capture explicit operator approval before anyone runs the CLI write command.",
            "After the CLI write completes, refresh verification and archive the updated evidence pack.",
        ]
    elif report_payload and action_count == 0:
        evidence_state = "empty"
        evidence_title = "No write evidence required"
        evidence_summary = "The latest handoff refresh does not contain any governance-source changes that need write approval."
        evidence_follow_ups = [
            "No write evidence pack is needed for this target root unless a future governance refresh generates new apply actions."
        ]
    elif report_state == "drifted":
        evidence_state = "drifted"
        evidence_title = "Evidence pack paused for drift"
        evidence_summary = (
            f"The latest staged verification now reports {max(drift_count, 1)} drift finding(s), "
            "so the evidence pack is no longer safe to hand off."
        )
        evidence_follow_ups = [
            "Restage or rebuild the apply pack until verification returns to a clean verified state.",
            "Only then should the evidence pack be attached to an approval record.",
        ]
    elif report_payload:
        evidence_state = "pre_write_pending"
        evidence_title = "Evidence pack still forming"
        evidence_summary = (
            "The apply pack exists, but staged execution and verification are not yet clean enough to support an approval record."
        )
        evidence_follow_ups = [
            "Finish stage and verify first so the evidence pack points to real execution artifacts instead of patches alone.",
        ]

    return {
        "state": state,
        "ready": state == "ready",
        "requires_explicit_approval": True,
        "approval_enabled": state in {"ready", "completed"},
        "approval_label": "I reviewed the staged governance artifacts and understand the final CLI write still happens outside this page.",
        "approval_help": "This checkbox only records the handoff acknowledgement in the browser UI. Repo governance source write still requires someone to run the CLI command explicitly.",
        "title": title,
        "summary": summary,
        "write_command": write_command if commands_available else "",
        "verify_command": verify_command if commands_available else "",
        "rollback_hint": rollback_hint,
        "blocked_reasons": blocked_reasons,
        "checklist": checklist,
        "governance_source_paths": source_paths,
        "artifact_paths": artifact_paths,
        "evidence": {
            "state": evidence_state,
            "title": evidence_title,
            "summary": evidence_summary,
            "entries": evidence_entries,
            "follow_ups": evidence_follow_ups,
        },
    }


def _render_waiver_apply_approval_audit_markdown(
    *,
    target_root: str,
    audit_payload: dict[str, Any],
) -> str:
    lines = [
        "# Governance Write Approval Audit",
        "",
        f"- Target root: `{target_root}`",
        f"- Audit state: `{audit_payload.get('state', '')}`",
        f"- History count: `{audit_payload.get('history_count', 0)}`",
        f"- Records path: `{audit_payload.get('records_path', '')}`",
        f"- Markdown path: `{audit_payload.get('markdown_path', '')}`",
        "",
        "## Summary",
        "",
        audit_payload.get("summary", ""),
        "",
    ]

    current_record = audit_payload.get("current_record")
    if isinstance(current_record, dict):
        lines.extend(
            [
                "## Current Record",
                "",
                f"- Captured at: `{current_record.get('captured_at', '')}`",
                f"- Timeline state: `{current_record.get('timeline_state', '')}`",
                f"- Report state: `{current_record.get('report_state', '')}`",
                f"- Handoff state: `{current_record.get('write_handoff_state', '')}`",
                f"- Evidence: `{current_record.get('evidence_title', '')}`",
            ]
        )
        note = str(current_record.get("note", "")).strip()
        if note:
            lines.append(f"- Note: {note}")
        lines.append("")

    lines.extend(
        [
            "## Timeline",
            "",
        ]
    )
    timeline = audit_payload.get("timeline", [])
    if not isinstance(timeline, list) or not timeline:
        lines.append("- No persisted approval records yet.")
    else:
        for item in timeline:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{item.get('captured_at', '')}` `{item.get('timeline_state', '')}` "
                f"`{item.get('write_handoff_state', '')}` `{item.get('evidence_title', '')}`"
            )
            note = str(item.get("note", "")).strip()
            if note:
                lines.append(f"  note: {note}")
            lines.append(f"  report_state: `{item.get('report_state', '')}`")

    follow_ups = audit_payload.get("follow_ups", [])
    if isinstance(follow_ups, list) and follow_ups:
        lines.extend(["", "## Follow-ups", ""])
        for item in follow_ups:
            lines.append(f"- {item}")

    return "\n".join(lines).rstrip() + "\n"


def _is_internal_iteration_doc(path: Path) -> bool:
    return path.stem.endswith("-iteration")


def _is_active_waiver(payload: dict[str, Any]) -> bool:
    expires_on = str(payload.get("expires_on", "")).strip()
    if not expires_on:
        return True
    try:
        return date.today() <= date.fromisoformat(expires_on)
    except ValueError:
        return False


class MarketRepository:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def repo_root(self) -> Path:
        return self.settings.repo_root

    def _waiver_apply_approval_artifact_paths(self, waiver_apply_dir: Path) -> tuple[Path, Path]:
        return (
            waiver_apply_dir / "write-approval-records.json",
            waiver_apply_dir / "write-approval-records.md",
        )

    def _build_waiver_apply_approval_audit(
        self,
        *,
        target_root: Path,
        waiver_apply_dir: Path,
        report_summary_path: Path,
        apply_execute_summary_path: Path,
        verify_summary_path: Path,
        report_payload: dict[str, Any] | None,
        write_handoff: dict[str, Any],
    ) -> dict[str, Any]:
        records_path, markdown_path = self._waiver_apply_approval_artifact_paths(waiver_apply_dir)
        raw_records_payload = _read_json(records_path) if records_path.is_file() else {}
        raw_records = raw_records_payload if isinstance(raw_records_payload, list) else raw_records_payload.get("records", [])
        current_fingerprint = _build_waiver_apply_approval_fingerprint(
            report_summary_path=report_summary_path,
            apply_execute_summary_path=apply_execute_summary_path,
            verify_summary_path=verify_summary_path,
            report_payload=report_payload,
        )

        normalized_records: list[dict[str, Any]] = []
        if isinstance(raw_records, list):
            for index, record in enumerate(raw_records, start=1):
                if not isinstance(record, dict):
                    continue
                evidence_snapshot = record.get("evidence_snapshot", {})
                evidence_entries = evidence_snapshot.get("entries", []) if isinstance(evidence_snapshot, dict) else []
                normalized_records.append(
                    {
                        "record_id": str(record.get("record_id", "")).strip() or f"approval-{index:03d}",
                        "captured_at": str(record.get("captured_at", "")).strip(),
                        "scope": str(record.get("scope", "")).strip(),
                        "note": str(record.get("note", "")).strip(),
                        "report_state": str(record.get("report_state", "")).strip(),
                        "write_handoff_state": str(record.get("write_handoff_state", "")).strip(),
                        "write_handoff_title": str(record.get("write_handoff_title", "")).strip(),
                        "evidence_state": str(evidence_snapshot.get("state", "")).strip()
                        if isinstance(evidence_snapshot, dict)
                        else "",
                        "evidence_title": str(evidence_snapshot.get("title", "")).strip()
                        if isinstance(evidence_snapshot, dict)
                        else "",
                        "evidence_summary": str(evidence_snapshot.get("summary", "")).strip()
                        if isinstance(evidence_snapshot, dict)
                        else "",
                        "evidence_entries": evidence_entries if isinstance(evidence_entries, list) else [],
                        "fingerprint": str(record.get("fingerprint", "")).strip(),
                        "artifact_paths": record.get("artifact_paths", []) if isinstance(record.get("artifact_paths", []), list) else [],
                        "governance_source_paths": record.get("governance_source_paths", [])
                        if isinstance(record.get("governance_source_paths", []), list)
                        else [],
                    }
                )

        normalized_records.sort(key=lambda item: _timestamp_sort_key(item.get("captured_at", "")), reverse=True)

        active_record: dict[str, Any] | None = None
        timeline: list[dict[str, Any]] = []
        matched_current = False
        for record in normalized_records:
            matches_current = bool(current_fingerprint and record.get("fingerprint") == current_fingerprint)
            timeline_state = "history"
            if matches_current and not matched_current:
                timeline_state = "active"
                matched_current = True
            elif matches_current:
                timeline_state = "superseded"
            normalized_record = {
                **record,
                "matches_current": matches_current,
                "timeline_state": timeline_state,
            }
            if timeline_state == "active" and active_record is None:
                active_record = normalized_record
            timeline.append(normalized_record)

        latest_record = timeline[0] if timeline else None
        approval_enabled = bool(write_handoff.get("approval_enabled"))

        if active_record:
            state = "active"
            title = "Approval record current"
            summary = (
                f"The current CLI write handoff is covered by a persisted approval record captured at "
                f"{active_record.get('captured_at', '')}."
            )
            follow_ups = [
                "Keep this approval record with the associated execute, verify, and report artifacts.",
                "Capture a fresh approval record after any new stage, verify, or write refresh changes the handoff artifacts.",
            ]
        elif latest_record:
            state = "history_only"
            title = "Approval history available"
            summary = (
                "Saved approval history exists, but the current handoff no longer matches the latest persisted approval record."
            )
            follow_ups = [
                "Review the latest timeline entry and keep it in the historical audit trail.",
                "Capture a fresh approval record only after the current handoff artifacts are the ones you want to approve.",
            ]
        elif approval_enabled:
            state = "empty"
            title = "Approval record not captured"
            summary = "The current handoff is ready, but no persisted approval record exists yet."
            follow_ups = [
                "Capture an approval record before treating the current handoff as operator-approved.",
                "Include an optional note if you want the audit trail to explain why this handoff was approved.",
            ]
        else:
            state = "empty"
            title = "Approval audit waiting"
            summary = "The current handoff is not ready for a persisted approval record yet."
            follow_ups = [
                "Finish stage and verify first so the approval audit trail attaches to a clean handoff state.",
            ]

        return {
            "state": state,
            "title": title,
            "summary": summary,
            "records_path": _display_repo_path(records_path, self.repo_root),
            "markdown_path": _display_repo_path(markdown_path, self.repo_root),
            "history_count": len(timeline),
            "current_record": active_record,
            "latest_record": latest_record,
            "timeline": timeline[:6],
            "follow_ups": follow_ups,
        }

    def capture_installed_governance_waiver_apply_approval(
        self,
        target_root: Path,
        *,
        note: str = "",
        scope: str = "installed-state-governance-waiver-apply",
    ) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        state = self.get_installed_governance_waiver_apply_state(resolved_root)
        write_handoff = state.get("write_handoff", {})
        latest_report = state.get("latest_report")
        if not isinstance(write_handoff, dict) or not write_handoff.get("approval_enabled"):
            raise ValueError("The current waiver/apply handoff is not ready for persisted approval capture yet.")
        if not isinstance(latest_report, dict):
            raise ValueError("A prepared waiver/apply report is required before capturing approval.")

        waiver_apply_dir = Path(str(state.get("waiver_apply_dir", ""))).resolve()
        report_summary_path = Path(str(state.get("report_summary_path", ""))).resolve()
        verify_summary_path = Path(str(state.get("verify_summary_path", ""))).resolve()
        apply_execute_summary_path = (waiver_apply_dir / "source-reconcile-gate-waiver-apply-execute-summary.json").resolve()
        records_path, markdown_path = self._waiver_apply_approval_artifact_paths(waiver_apply_dir)
        current_fingerprint = _build_waiver_apply_approval_fingerprint(
            report_summary_path=report_summary_path,
            apply_execute_summary_path=apply_execute_summary_path,
            verify_summary_path=verify_summary_path,
            report_payload=latest_report,
        )

        existing_payload = _read_json(records_path) if records_path.is_file() else {}
        existing_records = existing_payload.get("records", []) if isinstance(existing_payload, dict) else []
        if not isinstance(existing_records, list):
            existing_records = []

        captured_at = _utc_now_iso()
        record = {
            "record_id": f"approval-{len(existing_records) + 1:03d}-{captured_at.replace(':', '').replace('-', '')}-{current_fingerprint[:8]}",
            "captured_at": captured_at,
            "scope": scope,
            "note": str(note).strip(),
            "target_root": _display_repo_path(resolved_root, self.repo_root),
            "report_summary_path": _display_repo_path(report_summary_path, self.repo_root),
            "report_state": str(latest_report.get("report_state", "")).strip(),
            "write_handoff_state": str(write_handoff.get("state", "")).strip(),
            "write_handoff_title": str(write_handoff.get("title", "")).strip(),
            "fingerprint": current_fingerprint,
            "evidence_snapshot": {
                "state": str(write_handoff.get("evidence", {}).get("state", "")).strip(),
                "title": str(write_handoff.get("evidence", {}).get("title", "")).strip(),
                "summary": str(write_handoff.get("evidence", {}).get("summary", "")).strip(),
                "entries": write_handoff.get("evidence", {}).get("entries", []),
            },
            "artifact_paths": write_handoff.get("artifact_paths", []),
            "governance_source_paths": write_handoff.get("governance_source_paths", []),
        }

        stored_payload = {
            "target_root": _display_repo_path(resolved_root, self.repo_root),
            "waiver_apply_dir": _display_repo_path(waiver_apply_dir, self.repo_root),
            "updated_at": captured_at,
            "records": [*existing_records, record],
        }
        _write_json(records_path, stored_payload)

        audit_payload = self._build_waiver_apply_approval_audit(
            target_root=resolved_root,
            waiver_apply_dir=waiver_apply_dir,
            report_summary_path=report_summary_path,
            apply_execute_summary_path=apply_execute_summary_path,
            verify_summary_path=verify_summary_path,
            report_payload=latest_report,
            write_handoff=write_handoff,
        )
        _write_text(
            markdown_path,
            _render_waiver_apply_approval_audit_markdown(
                target_root=_display_repo_path(resolved_root, self.repo_root),
                audit_payload=audit_payload,
            ),
        )
        return {
            "captured": True,
            "record": audit_payload.get("current_record"),
            "audit": audit_payload,
        }

    def _dist_path(self, *parts: str) -> Path:
        return self.settings.dist_market_root.joinpath(*parts)

    def _count_json_profiles(self, *parts: str) -> int:
        directory = self.repo_root.joinpath(*parts)
        return len(list(directory.glob("*.json"))) if directory.is_dir() else 0

    def _count_active_waivers(self, *parts: str) -> int:
        directory = self.repo_root.joinpath(*parts)
        if not directory.is_dir():
            return 0
        active_count = 0
        for path in directory.glob("*.json"):
            payload = _read_json(path)
            if isinstance(payload, dict) and _is_active_waiver(payload):
                active_count += 1
        return active_count

    def get_market_index(self) -> dict[str, Any]:
        return _read_json(self._dist_path("index.json"))

    def get_channel_skills(self, channel: str) -> dict[str, Any]:
        if channel not in VALID_CHANNELS:
            raise ValueError(f"unsupported channel: {channel}")
        return _read_json(self._dist_path("channels", f"{channel}.json"))

    def get_all_skills(self) -> list[dict[str, Any]]:
        skills: list[dict[str, Any]] = []
        for channel in VALID_CHANNELS:
            channel_path = self._dist_path("channels", f"{channel}.json")
            if not channel_path.is_file():
                continue
            channel_payload = _read_json(channel_path)
            skills.extend(channel_payload.get("skills", []))
        return skills

    def search_skills(
        self,
        *,
        query: str = "",
        channels: list[str] | None = None,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        selected_channels = {item for item in (channels or []) if item}
        selected_categories = {item for item in (categories or []) if item}
        selected_tags = {item for item in (tags or []) if item}
        needle = query.strip().lower()
        results: list[dict[str, Any]] = []
        for skill in self.get_all_skills():
            channel = str(skill.get("channel", "")).strip()
            if selected_channels and channel not in selected_channels:
                continue
            skill_categories = {str(item).strip() for item in skill.get("categories", []) if str(item).strip()}
            if selected_categories and not skill_categories.intersection(selected_categories):
                continue
            skill_tags = {str(item).strip() for item in skill.get("tags", []) if str(item).strip()}
            if selected_tags and not skill_tags.intersection(selected_tags):
                continue
            if needle:
                haystack = " ".join(
                    [
                        str(skill.get("title", "")),
                        str(skill.get("summary", "")),
                        " ".join(sorted(skill_categories)),
                        " ".join(sorted(skill_tags)),
                    ]
                ).lower()
                if needle not in haystack:
                    continue
            results.append(skill)
        return results

    def get_skill_summary(self, name: str) -> dict[str, Any] | None:
        normalized = name.strip().lower()
        for skill in self.get_all_skills():
            if str(skill.get("name", "")).strip().lower() == normalized:
                return skill
        return None

    def get_skill_manifest(self, name: str) -> dict[str, Any] | None:
        manifest_path = self.settings.skills_root / name / "market" / "skill.json"
        if not manifest_path.is_file():
            return None
        return _read_json(manifest_path)

    def get_install_spec(self, name: str, version: str | None = None) -> dict[str, Any] | None:
        resolved_version = version
        if not resolved_version:
            skill = self.get_skill_summary(name)
            if not skill:
                return None
            resolved_version = str(skill.get("version", "")).strip()
        if not resolved_version:
            return None
        spec_path = self._dist_path("install", f"{name}-{resolved_version}.json")
        if not spec_path.is_file():
            return None
        return _read_json(spec_path)

    def _resolve_repo_doc_path(self, raw_path: str) -> Path | None:
        normalized = str(raw_path).strip()
        if not normalized:
            return None
        candidate = Path(normalized)
        candidate = candidate if candidate.is_absolute() else (self.repo_root / candidate)
        candidate = candidate.resolve()
        try:
            candidate.relative_to(self.repo_root)
        except ValueError:
            return None
        return candidate

    def _get_skill_doc_path(self, name: str, manifest: dict[str, Any] | None = None) -> Path | None:
        resolved_manifest = manifest or self.get_skill_manifest(name)
        artifacts = resolved_manifest.get("artifacts", {}) if isinstance(resolved_manifest, dict) else {}
        raw_docs_path = str(artifacts.get("docs", "")).strip()
        manifest_doc_path = self._resolve_repo_doc_path(raw_docs_path)
        if manifest_doc_path and manifest_doc_path.is_file():
            return manifest_doc_path

        fallback = self.settings.docs_root / f"{name}.md"
        if fallback.is_file():
            return fallback
        return None

    def get_skill_doc_path(self, name: str) -> str | None:
        doc_path = self._get_skill_doc_path(name)
        if not doc_path:
            return None
        return _display_repo_path(doc_path, self.repo_root)

    def _iter_teaching_doc_paths(self) -> list[Path]:
        return sorted(path for path in self.settings.teaching_root.rglob("*.md") if path.is_file())

    def _iter_project_doc_paths(self) -> list[Path]:
        skill_doc_paths = {
            path.resolve()
            for skill in self.get_all_skills()
            if (path := self._get_skill_doc_path(str(skill.get("name", "")).strip()))
        }
        project_docs: list[Path] = []
        for path in sorted(self.settings.docs_root.rglob("*.md")):
            if not path.is_file():
                continue
            if path.name == "README.md":
                continue
            if self.settings.teaching_root in path.parents:
                continue
            if "assets" in path.parts:
                continue
            if path.resolve() in skill_doc_paths:
                continue
            if _is_internal_iteration_doc(path):
                continue
            project_docs.append(path)
        return project_docs

    def get_skill_doc(self, name: str) -> str | None:
        doc_path = self._get_skill_doc_path(name)
        if doc_path is None or not doc_path.is_file():
            return None
        return _read_text(doc_path)

    def get_teaching_doc(self, doc_id: str) -> dict[str, Any] | None:
        path = next((candidate for candidate in self._iter_teaching_doc_paths() if candidate.stem == doc_id), None)
        if path is None or not path.is_file():
            return None
        markdown = _read_text(path)
        return {
            "id": doc_id,
            "kind": "teaching",
            "title": _first_heading(markdown, doc_id),
            "summary": _first_paragraph(markdown),
            "markdown": markdown,
            "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
        }

    def get_project_doc(self, doc_id: str) -> dict[str, Any] | None:
        path = next((candidate for candidate in self._iter_project_doc_paths() if candidate.stem == doc_id), None)
        if path is None or not path.is_file():
            return None
        markdown = _read_text(path)
        return {
            "id": doc_id,
            "kind": "project",
            "title": _first_heading(markdown, doc_id),
            "summary": _first_paragraph(markdown),
            "markdown": markdown,
            "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
        }

    def get_skill_detail(self, name: str) -> dict[str, Any] | None:
        manifest = self.get_skill_manifest(name)
        if not manifest:
            return None
        install_spec = self.get_install_spec(name, str(manifest.get("version", "")).strip())
        doc_markdown = self.get_skill_doc(name)
        related_skills: list[dict[str, Any]] = []
        all_skills = self.get_all_skills()
        by_id = {str(skill.get("id", "")).strip(): skill for skill in all_skills}
        search_info = manifest.get("search", {})
        if isinstance(search_info, dict):
            for skill_id in search_info.get("related_skills", []):
                related = by_id.get(str(skill_id).strip())
                if related:
                    related_skills.append(related)
        return {
            "manifest": manifest,
            "install_spec": install_spec,
            "doc_markdown": doc_markdown,
            "related_skills": related_skills,
        }

    def get_categories(self) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for skill in self.get_all_skills():
            for category in skill.get("categories", []):
                key = str(category).strip()
                if key:
                    counts[key] = counts.get(key, 0) + 1
        return [
            {"category": category, "count": count}
            for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    def get_tags(self) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for skill in self.get_all_skills():
            for tag in skill.get("tags", []):
                key = str(tag).strip()
                if key:
                    counts[key] = counts.get(key, 0) + 1
        return [
            {"tag": tag, "count": count}
            for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    def list_bundles(self) -> list[dict[str, Any]]:
        all_skills = self.get_all_skills()
        by_id = {str(skill.get("id", "")).strip(): skill for skill in all_skills}
        bundles: list[dict[str, Any]] = []
        for bundle_path in sorted(self.settings.bundles_root.glob("*.json")):
            payload = _read_json(bundle_path)
            skill_summaries = [
                by_id[skill_id]
                for skill_id in payload.get("skills", [])
                if str(skill_id).strip() in by_id
            ]
            bundles.append(
                {
                    **payload,
                    "skill_count": len(payload.get("skills", [])),
                    "skill_summaries": skill_summaries,
                    "path": str(bundle_path.relative_to(self.repo_root)).replace("\\", "/"),
                }
            )
        return bundles

    def get_bundle(self, bundle_id: str) -> dict[str, Any] | None:
        normalized = bundle_id.strip().lower()
        for bundle in self.list_bundles():
            if str(bundle.get("id", "")).strip().lower() != normalized:
                continue
            install_specs: list[dict[str, Any]] = []
            for skill in bundle.get("skill_summaries", []):
                name = str(skill.get("name", "")).strip()
                version = str(skill.get("version", "")).strip()
                spec = self.get_install_spec(name, version)
                if spec:
                    install_specs.append(spec)
            return {
                "bundle": bundle,
                "skills": bundle.get("skill_summaries", []),
                "install_specs": install_specs,
            }
        return None

    def get_docs_catalog(self) -> dict[str, Any]:
        skill_docs: list[dict[str, Any]] = []
        for skill in self.get_all_skills():
            name = str(skill.get("name", "")).strip()
            if not name:
                continue
            doc_path = self._get_skill_doc_path(name)
            if not doc_path:
                continue
            markdown = self.get_skill_doc(name)
            if not markdown:
                continue
            skill_docs.append(
                {
                    "id": name,
                    "kind": "skill",
                    "title": _first_heading(markdown, str(skill.get("title", name))),
                    "summary": _first_paragraph(markdown) or str(skill.get("summary", "")),
                    "path": _display_repo_path(doc_path, self.repo_root),
                }
            )

        teaching_docs: list[dict[str, Any]] = []
        for path in self._iter_teaching_doc_paths():
            markdown = _read_text(path)
            teaching_docs.append(
                {
                    "id": path.stem,
                    "kind": "teaching",
                    "title": _first_heading(markdown, path.stem),
                    "summary": _first_paragraph(markdown),
                    "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
                }
            )

        root_docs: list[dict[str, Any]] = []
        for path in self._iter_project_doc_paths():
            markdown = _read_text(path)
            root_docs.append(
                {
                    "id": path.stem,
                    "kind": "project",
                    "title": _first_heading(markdown, path.stem),
                    "summary": _first_paragraph(markdown),
                    "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
                }
            )

        all_docs = sorted(
            [*skill_docs, *teaching_docs, *root_docs],
            key=lambda item: (str(item.get("title", "")).lower(), str(item.get("id", "")).lower()),
        )

        return {
            "skill_docs": skill_docs,
            "teaching_docs": teaching_docs,
            "project_docs": root_docs,
            "all_docs": all_docs,
        }

    def _split_doc_action_command(self, command: str) -> list[str]:
        return shlex.split(command, posix=False)

    def _doc_action_smoke_output_root(self, doc_kind: str, doc_id: str) -> str:
        normalized_kind = re.sub(r"[^a-z0-9-]+", "-", doc_kind.lower()).strip("-") or "doc"
        normalized_id = re.sub(r"[^a-z0-9-]+", "-", doc_id.lower()).strip("-") or "action"
        return f"dist/market-smoke-doc-actions/{normalized_kind}-{normalized_id}"

    def _build_doc_action_payload(
        self,
        *,
        doc_kind: str,
        doc_id: str,
        doc_title: str,
        doc_path: str,
        action_id: str,
        label: str,
        command: list[str],
        expected_artifacts: list[str],
        execution_summary: str,
    ) -> dict[str, Any]:
        return {
            "kind": f"docs-{doc_kind}-{action_id}",
            "command": command,
            "summary": {
                "doc_kind": doc_kind,
                "doc_id": doc_id,
                "doc_title": doc_title,
                "action_id": action_id,
                "label": label,
            },
            "artifacts": {
                "doc_path": doc_path,
                "expected_artifacts": expected_artifacts,
                "execution_summary": execution_summary,
            },
        }

    def _get_skill_doc_action_execution(self, doc_id: str, action_id: str) -> dict[str, Any] | None:
        detail = self.get_skill_detail(doc_id)
        if not detail or action_id != "skill-checker":
            return None

        manifest = detail.get("manifest", {}) if isinstance(detail, dict) else {}
        quality = manifest.get("quality", {}) if isinstance(manifest, dict) else {}
        raw_command = str(quality.get("checker", "")).strip() or (
            f"python skills/{doc_id}/scripts/check_{doc_id.replace('-', '_')}.py"
        )
        doc_path = self.get_skill_doc_path(doc_id) or f"docs/skills/{doc_id}.md"
        return self._build_doc_action_payload(
            doc_kind="skill",
            doc_id=doc_id,
            doc_title=str(manifest.get("title", doc_id)).strip() or doc_id,
            doc_path=doc_path,
            action_id=action_id,
            label="Run checker",
            command=self._split_doc_action_command(raw_command),
            expected_artifacts=["Checker pass/fail summary printed in the terminal output"],
            execution_summary="Run the repo-backed skill checker from the doc page and keep the copy command for manual reruns.",
        )

    def _get_teaching_doc_action_execution(self, doc_id: str, action_id: str) -> dict[str, Any] | None:
        doc = self.get_teaching_doc(doc_id)
        if not doc:
            return None

        title = str(doc.get("title", doc_id)).strip() or doc_id
        doc_path = str(doc.get("path", f"docs/teaching/{doc_id}.md")).strip()
        smoke_output_root = self._doc_action_smoke_output_root("teaching", doc_id)

        if (
            "build" in doc_id
            or "skill-author" in doc_id
            or "learner" in doc_id
            or "read-the-repo" in doc_id
        ):
            if action_id == "check-progressive-structure":
                return self._build_doc_action_payload(
                    doc_kind="teaching",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Check progressive structure",
                    command=["python", "scripts/check_progressive_skills.py"],
                    expected_artifacts=["Repository-wide structural validation summary in terminal output"],
                    execution_summary="Run the repository-wide progressive skill validation from this teaching page.",
                )
            if action_id == "check-build-skills":
                return self._build_doc_action_payload(
                    doc_kind="teaching",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Run build-skills checker",
                    command=["python", "skills/build-skills/scripts/check_build_skills.py"],
                    expected_artifacts=["build-skills checker summary in terminal output"],
                    execution_summary="Run the build-skills lesson checker without leaving the teaching doc.",
                )
            return None

        if "progressive-disclosure" in doc_id:
            if action_id == "check-progressive-structure":
                return self._build_doc_action_payload(
                    doc_kind="teaching",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Check progressive structure",
                    command=["python", "scripts/check_progressive_skills.py"],
                    expected_artifacts=["Repository-wide structural validation summary in terminal output"],
                    execution_summary="Run the repository-wide progressive skill validation from this teaching page.",
                )
            if action_id == "check-progressive-disclosure":
                return self._build_doc_action_payload(
                    doc_kind="teaching",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Run progressive-disclosure checker",
                    command=["python", "skills/progressive-disclosure/scripts/check_progressive_disclosure.py"],
                    expected_artifacts=["progressive-disclosure checker summary in terminal output"],
                    execution_summary="Run the progressive-disclosure checker directly from the teaching lesson.",
                )
            return None

        if "harness" in doc_id or "evals-and-prototypes" in doc_id:
            if action_id != "check-harness-prototypes":
                return None
            return self._build_doc_action_payload(
                doc_kind="teaching",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check harness prototypes",
                command=["python", "scripts/check_harness_prototypes.py"],
                expected_artifacts=["Prototype validation summary in terminal output"],
                execution_summary="Run the prototype schema and asset validation from this lesson.",
            )

        if "market" in doc_id or "registry" in doc_id or "project-learning-roadmap" in doc_id:
            if action_id == "run-market-smoke":
                return self._build_doc_action_payload(
                    doc_kind="teaching",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Run market smoke",
                    command=["python", "scripts/check_market_pipeline.py", "--output-root", smoke_output_root],
                    expected_artifacts=[f"Smoke output directory under {smoke_output_root}/ plus terminal summary"],
                    execution_summary="Run the market smoke pipeline with a doc-scoped output root and inspect the result summary in-page.",
                )
            if action_id == "check-python-market-backend":
                return self._build_doc_action_payload(
                    doc_kind="teaching",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Check frontend/backend integration",
                    command=["python", "scripts/check_python_market_backend.py"],
                    expected_artifacts=["Backend payload-count summary printed in terminal output"],
                    execution_summary="Run the Python backend payload checker directly from this teaching reference.",
                )
            return None

        if action_id == "check-progressive-structure":
            return self._build_doc_action_payload(
                doc_kind="teaching",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check progressive structure",
                command=["python", "scripts/check_progressive_skills.py"],
                expected_artifacts=["Repository-wide structural validation summary in terminal output"],
                execution_summary="Run the repository-wide progressive skill validation from this teaching page.",
            )
        if action_id == "check-docs-links":
            return self._build_doc_action_payload(
                doc_kind="teaching",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check docs links",
                command=["python", "scripts/check_docs_links.py"],
                expected_artifacts=["Docs link validation summary in terminal output"],
                execution_summary="Run the docs link checker from this lesson and keep the command available for manual follow-up.",
            )
        return None

    def _get_project_doc_action_execution(self, doc_id: str, action_id: str) -> dict[str, Any] | None:
        doc = self.get_project_doc(doc_id)
        if not doc:
            return None

        title = str(doc.get("title", doc_id)).strip() or doc_id
        doc_path = str(doc.get("path", f"docs/{doc_id}.md")).strip()
        smoke_output_root = self._doc_action_smoke_output_root("project", doc_id)

        if doc_id == "frontend-backend-integration":
            if action_id != "check-python-market-backend":
                return None
            return self._build_doc_action_payload(
                doc_kind="project",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check backend repository layer",
                command=["python", "scripts/check_python_market_backend.py"],
                expected_artifacts=["Backend payload-count summary printed in terminal output"],
                execution_summary="Run the Python backend repository check directly from this project reference.",
            )

        if doc_id == "dev-setup":
            if action_id == "compile-backend":
                return self._build_doc_action_payload(
                    doc_kind="project",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Compile backend",
                    command=["python", "-m", "compileall", "backend"],
                    expected_artifacts=["Compiled bytecode under backend/__pycache__/ and nested package cache directories"],
                    execution_summary="Compile the backend package tree and inspect the summary without leaving the setup guide.",
                )
            if action_id == "build-frontend":
                return self._build_doc_action_payload(
                    doc_kind="project",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Build frontend",
                    command=["npm", "run", "build", "--prefix", "frontend"],
                    expected_artifacts=["Production build artifacts under frontend/.next/"],
                    execution_summary="Run the frontend production build from the setup guide and surface the result in-page.",
                )
            return None

        if doc_id == "repo-commands":
            if action_id == "check-progressive-structure":
                return self._build_doc_action_payload(
                    doc_kind="project",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Check progressive structure",
                    command=["python", "scripts/check_progressive_skills.py"],
                    expected_artifacts=["Repository-wide structural validation summary in terminal output"],
                    execution_summary="Run the repository-wide structural validation from the repo commands reference.",
                )
            if action_id == "check-docs-links":
                return self._build_doc_action_payload(
                    doc_kind="project",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Check docs links",
                    command=["python", "scripts/check_docs_links.py"],
                    expected_artifacts=["Docs link validation summary in terminal output"],
                    execution_summary="Run the docs link checker directly from this reference page.",
                )
            return None

        if "market" in doc_id or "consumer-guide" in doc_id or "publisher-guide" in doc_id:
            if action_id == "validate-market-manifests":
                return self._build_doc_action_payload(
                    doc_kind="project",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Validate market manifests",
                    command=["python", "scripts/validate_market_manifest.py"],
                    expected_artifacts=["Manifest validation summary in terminal output"],
                    execution_summary="Run manifest validation from the current market reference and inspect the result in-page.",
                )
            if action_id == "run-market-smoke":
                return self._build_doc_action_payload(
                    doc_kind="project",
                    doc_id=doc_id,
                    doc_title=title,
                    doc_path=doc_path,
                    action_id=action_id,
                    label="Run market smoke",
                    command=["python", "scripts/check_market_pipeline.py", "--output-root", smoke_output_root],
                    expected_artifacts=[f"Smoke output directory under {smoke_output_root}/ plus terminal summary"],
                    execution_summary="Run the market smoke pipeline with a doc-scoped output root and inspect the summary in-page.",
                )
            return None

        if "harness" in doc_id:
            if action_id != "check-harness-prototypes":
                return None
            return self._build_doc_action_payload(
                doc_kind="project",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check harness prototypes",
                command=["python", "scripts/check_harness_prototypes.py"],
                expected_artifacts=["Prototype validation summary in terminal output"],
                execution_summary="Run harness prototype validation directly from this project reference.",
            )

        if action_id == "check-docs-links":
            return self._build_doc_action_payload(
                doc_kind="project",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check docs links",
                command=["python", "scripts/check_docs_links.py"],
                expected_artifacts=["Docs link validation summary in terminal output"],
                execution_summary="Run the docs link checker directly from this project reference.",
            )
        if action_id == "check-progressive-structure":
            return self._build_doc_action_payload(
                doc_kind="project",
                doc_id=doc_id,
                doc_title=title,
                doc_path=doc_path,
                action_id=action_id,
                label="Check progressive structure",
                command=["python", "scripts/check_progressive_skills.py"],
                expected_artifacts=["Repository-wide structural validation summary in terminal output"],
                execution_summary="Run the repository-wide structural validation from this project reference.",
            )
        return None

    def get_doc_action_execution(self, doc_kind: str, doc_id: str, action_id: str) -> dict[str, Any] | None:
        normalized_kind = str(doc_kind).strip().lower()
        normalized_id = str(doc_id).strip()
        normalized_action_id = str(action_id).strip()
        if not normalized_id or not normalized_action_id:
            return None
        if normalized_kind == "skill":
            return self._get_skill_doc_action_execution(normalized_id, normalized_action_id)
        if normalized_kind == "teaching":
            return self._get_teaching_doc_action_execution(normalized_id, normalized_action_id)
        if normalized_kind == "project":
            return self._get_project_doc_action_execution(normalized_id, normalized_action_id)
        return None

    def _iter_submission_records(self, root: Path, *, stage: str) -> list[dict[str, Any]]:
        if not root.is_dir():
            return []

        records: list[dict[str, Any]] = []
        for submission_path in root.glob("*/*/*/submission.json"):
            try:
                payload = _read_json(submission_path)
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue

            review_path = submission_path.with_name("review.json")
            ingest_path = submission_path.with_name("ingest.json")
            review_payload = _read_json(review_path) if review_path.is_file() else None
            ingest_payload = _read_json(ingest_path) if ingest_path.is_file() else None

            findings = review_payload.get("findings", []) if isinstance(review_payload, dict) else []
            record = {
                "submission_id": str(payload.get("submission_id", "")).strip(),
                "publisher": str(payload.get("publisher", "")).strip(),
                "skill_id": str(payload.get("skill_id", "")).strip(),
                "skill_name": str(payload.get("skill_name", "")).strip(),
                "version": str(payload.get("version", "")).strip(),
                "channel": str(payload.get("channel", "")).strip(),
                "created_at": str(payload.get("created_at", "")).strip(),
                "stage": stage,
                "submission_path": _display_repo_path(submission_path, self.repo_root),
                "payload_archive_path": str(payload.get("payload_archive_path", "")).strip(),
                "source_dir": str(payload.get("source_dir", "")).strip(),
                "docs_path": str(payload.get("docs_path", "")).strip(),
                "manifest_path": str(payload.get("manifest_path", "")).strip(),
                "install_spec_path": str(payload.get("install_spec_path", "")).strip(),
                "provenance_path": str(payload.get("provenance_path", "")).strip(),
                "package_path": str(payload.get("package_path", "")).strip(),
                "release_notes": str(payload.get("release_notes", "")).strip(),
                "review": (
                    {
                        "path": _display_repo_path(review_path, self.repo_root),
                        "review_status": str(review_payload.get("review_status", "")).strip(),
                        "reviewer": str(review_payload.get("reviewer", "")).strip(),
                        "reviewed_at": str(review_payload.get("reviewed_at", "")).strip(),
                        "summary": str(review_payload.get("summary", "")).strip(),
                        "findings_count": len(findings) if isinstance(findings, list) else 0,
                    }
                    if isinstance(review_payload, dict)
                    else None
                ),
                "ingest": (
                    {
                        "path": _display_repo_path(ingest_path, self.repo_root),
                        "status": str(ingest_payload.get("status", "")).strip(),
                        "ingested_at": str(ingest_payload.get("ingested_at", "")).strip(),
                        "ingested_by": str(ingest_payload.get("ingested_by", "")).strip(),
                        "target_source_dir": str(ingest_payload.get("target_source_dir", "")).strip(),
                        "target_docs_path": str(ingest_payload.get("target_docs_path", "")).strip(),
                        "target_manifest_path": str(ingest_payload.get("target_manifest_path", "")).strip(),
                    }
                    if isinstance(ingest_payload, dict)
                    else None
                ),
            }
            records.append(record)

        records.sort(
            key=lambda item: (
                _timestamp_sort_key(str(item.get("created_at", ""))),
                str(item.get("submission_id", "")).lower(),
            ),
            reverse=True,
        )
        return records

    def get_author_submissions(
        self,
        *,
        built_root: Path | None = None,
        inbox_root: Path | None = None,
    ) -> dict[str, Any]:
        built_root = (built_root or (self.repo_root / "dist" / "submissions")).resolve()
        inbox_root = (inbox_root or (self.repo_root / "incoming" / "submissions")).resolve()
        built = self._iter_submission_records(built_root, stage="built")
        inbox = self._iter_submission_records(inbox_root, stage="inbox")
        return {
            "workspace": {
                "submissions_root": _display_repo_path(built_root, self.repo_root),
                "inbox_root": _display_repo_path(inbox_root, self.repo_root),
                "skills_root": _display_repo_path(self.settings.skills_root, self.repo_root),
                "docs_root": _display_repo_path(self.settings.docs_root, self.repo_root),
            },
            "counts": {
                "built": len(built),
                "inbox": len(inbox),
                "reviewed": sum(1 for item in inbox if item.get("review")),
                "approved": sum(
                    1
                    for item in inbox
                    if isinstance(item.get("review"), dict) and item["review"].get("review_status") == "approved"
                ),
                "ingested": sum(1 for item in inbox if item.get("ingest")),
            },
            "built": built,
            "inbox": inbox,
        }

    def get_author_overview(
        self,
        *,
        built_root: Path | None = None,
        inbox_root: Path | None = None,
    ) -> dict[str, Any]:
        submissions = self.get_author_submissions(built_root=built_root, inbox_root=inbox_root)
        skill_manifest_count = len(list(self.settings.skills_root.glob("*/market/skill.json")))
        return {
            "workspace": submissions["workspace"],
            "counts": {
                **dict(submissions["counts"]),
                "skill_manifests": skill_manifest_count,
            },
            "recent_built": list(submissions["built"])[:5],
            "recent_inbox": list(submissions["inbox"])[:5],
        }

    def get_repo_snapshot(self) -> dict[str, Any]:
        index = self.get_market_index()
        return {
            "market_index": index,
            "channels": {channel: index.get("channels", {}).get(channel, {}) for channel in VALID_CHANNELS},
            "skill_count": len(self.get_all_skills()),
            "bundle_count": len(self.list_bundles()),
            "doc_catalog": {
                "skill_doc_count": len(self.get_docs_catalog().get("skill_docs", [])),
                "teaching_doc_count": len(self.get_docs_catalog().get("teaching_docs", [])),
                "project_doc_count": len(self.get_docs_catalog().get("project_docs", [])),
            },
        }

    def get_installed_state(self, target_root: Path) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        lock_path = resolved_root / "skills.lock.json"
        if lock_path.is_file():
            lock_payload = _read_json(lock_path)
        else:
            lock_payload = {"installed": []}

        installed = sorted(
            [
                entry
                for entry in lock_payload.get("installed", [])
                if isinstance(entry, dict) and str(entry.get("skill_id", "")).strip()
            ],
            key=lambda item: (
                str(item.get("skill_id", "")).lower(),
                str(item.get("install_target", "")).lower(),
            ),
        )

        bundles: list[dict[str, Any]] = []
        bundle_reports_dir = resolved_root / "bundle-reports"
        if bundle_reports_dir.is_dir():
            for report_path in sorted(bundle_reports_dir.glob("*.json")):
                report = _read_json(report_path)
                results = report.get("results", [])
                active_skill_ids = sorted(
                    str(item.get("skill_id", "")).strip()
                    for item in results
                    if isinstance(item, dict) and item.get("status") == "installed" and str(item.get("skill_id", "")).strip()
                )
                bundles.append(
                    {
                        "bundle_id": str(report.get("bundle_id", report_path.stem)),
                        "title": str(report.get("title", report_path.stem)),
                        "generated_at": str(report.get("generated_at", "")),
                        "report_path": str(report_path),
                        "target_root": str(resolved_root),
                        "skill_count": len(active_skill_ids),
                        "active_skill_ids": active_skill_ids,
                    }
                )

        return {
            "target_root": str(resolved_root),
            "lock_path": str(lock_path),
            "installed_count": len(installed),
            "bundle_count": len(bundles),
            "installed": installed,
            "bundles": bundles,
        }

    def get_installed_baseline_state(self, target_root: Path) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        snapshots_dir = resolved_root / "snapshots"
        baseline_path = snapshots_dir / "baseline.json"
        baseline_markdown_path = snapshots_dir / "baseline.md"
        history_path = snapshots_dir / "baseline-history.json"
        history_markdown_path = snapshots_dir / "baseline-history.md"
        archive_dir = snapshots_dir / "baseline-archive"

        baseline_payload = _read_json(baseline_path) if baseline_path.is_file() else None
        raw_history_payload = _read_json(history_path) if history_path.is_file() else None
        history_entries = (
            raw_history_payload.get("entries", [])
            if isinstance(raw_history_payload, dict) and isinstance(raw_history_payload.get("entries", []), list)
            else []
        )
        normalized_entries = [
            entry
            for entry in history_entries
            if isinstance(entry, dict)
        ]
        latest_entry = normalized_entries[-1] if normalized_entries else None
        next_sequence = (
            raw_history_payload.get("next_sequence", 1)
            if isinstance(raw_history_payload, dict)
            else 1
        )

        return {
            "target_root": str(resolved_root),
            "snapshots_dir": str(snapshots_dir),
            "baseline_path": str(baseline_path),
            "baseline_markdown_path": str(baseline_markdown_path),
            "history_path": str(history_path),
            "history_markdown_path": str(history_markdown_path),
            "archive_dir": str(archive_dir),
            "baseline_exists": baseline_path.is_file(),
            "history_exists": history_path.is_file(),
            "history_entry_count": len(normalized_entries),
            "next_sequence": int(next_sequence) if str(next_sequence).isdigit() else 1,
            "current_baseline": (
                {
                    "generated_at": str(baseline_payload.get("generated_at", "")),
                    "target_root": str(baseline_payload.get("target_root", "")),
                    "summary": baseline_payload.get("summary", {}),
                }
                if isinstance(baseline_payload, dict)
                else None
            ),
            "latest_entry": latest_entry,
            "entries": normalized_entries[-5:],
        }

    def get_installed_governance_state(self, target_root: Path) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        snapshots_dir = resolved_root / "snapshots"
        history_path = snapshots_dir / "baseline-history.json"
        governance_dir = snapshots_dir / "governance"
        summary_path = governance_dir / "governance-summary.json"
        summary_markdown_path = governance_dir / "governance-summary.md"

        summary_payload = _read_json(summary_path) if summary_path.is_file() else None

        return {
            "target_root": str(resolved_root),
            "snapshots_dir": str(snapshots_dir),
            "history_path": str(history_path),
            "governance_dir": str(governance_dir),
            "summary_path": str(summary_path),
            "summary_markdown_path": str(summary_markdown_path),
            "history_exists": history_path.is_file(),
            "summary_exists": summary_path.is_file(),
            "can_refresh": history_path.is_file(),
            "profile_counts": {
                "history_alert_policies": {
                    "count": self._count_json_profiles("governance", "history-alert-policies"),
                },
                "history_alert_waivers": {
                    "count": self._count_json_profiles("governance", "history-alert-waivers"),
                    "active_count": self._count_active_waivers("governance", "history-alert-waivers"),
                },
                "source_reconcile_policies": {
                    "count": self._count_json_profiles("governance", "source-reconcile-gate-policies"),
                },
                "source_reconcile_gate_waivers": {
                    "count": self._count_json_profiles("governance", "source-reconcile-gate-waivers"),
                    "active_count": self._count_active_waivers("governance", "source-reconcile-gate-waivers"),
                },
                "source_reconcile_apply_policies": {
                    "count": self._count_json_profiles("governance", "source-reconcile-gate-waiver-apply-policies"),
                },
                "source_reconcile_apply_gate_waivers": {
                    "count": self._count_json_profiles("governance", "source-reconcile-gate-waiver-apply-waivers"),
                    "active_count": self._count_active_waivers("governance", "source-reconcile-gate-waiver-apply-waivers"),
                },
            },
            "latest_summary": summary_payload if isinstance(summary_payload, dict) else None,
        }

    def get_installed_governance_waiver_apply_state(self, target_root: Path) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        snapshots_dir = resolved_root / "snapshots"
        history_path = snapshots_dir / "baseline-history.json"
        governance_dir = snapshots_dir / "governance"
        governance_summary_path = governance_dir / "governance-summary.json"
        waiver_apply_dir = governance_dir / "waiver-apply"
        apply_summary_path = waiver_apply_dir / "source-reconcile-gate-waiver-apply-summary.json"
        verify_summary_path = waiver_apply_dir / "source-reconcile-gate-waiver-apply-verify-summary.json"
        report_summary_path = waiver_apply_dir / "source-reconcile-gate-waiver-apply-report-summary.json"
        stage_dir = waiver_apply_dir / "source-reconcile-gate-waiver-apply-staged-root"

        governance_summary_payload = _read_json(governance_summary_path) if governance_summary_path.is_file() else None
        report_payload = _read_json(report_summary_path) if report_summary_path.is_file() else None

        display_history_path = _display_repo_path(history_path, self.repo_root)
        display_target_root = _display_repo_path(resolved_root, self.repo_root)
        display_output_dir = _display_repo_path(waiver_apply_dir, self.repo_root)
        display_stage_dir = _display_repo_path(stage_dir, self.repo_root)
        display_apply_summary_path = _display_repo_path(apply_summary_path, self.repo_root)
        display_verify_summary_path = _display_repo_path(verify_summary_path, self.repo_root)
        display_report_summary_path = _display_repo_path(report_summary_path, self.repo_root)
        display_apply_execute_summary_path = _display_repo_path(
            waiver_apply_dir / "source-reconcile-gate-waiver-apply-execute-summary.json",
            self.repo_root,
        )
        governance_action_count = (
            int(governance_summary_payload.get("report", {}).get("action_count", 0))
            if isinstance(governance_summary_payload, dict)
            else 0
        )
        governance_report_state = (
            str(governance_summary_payload.get("report", {}).get("report_state", ""))
            if isinstance(governance_summary_payload, dict)
            else ""
        )
        write_command = (
            "python scripts/execute_source_reconcile_gate_waiver_apply.py "
            f"{display_history_path} --output-dir {display_output_dir} --write --json"
        )
        verify_command = (
            "python scripts/verify_source_reconcile_gate_waiver_apply.py "
            f"{display_history_path} --output-dir {display_output_dir} --json"
        )
        write_handoff = _build_waiver_apply_write_handoff(
            history_exists=history_path.is_file(),
            governance_summary_exists=governance_summary_path.is_file(),
            report_payload=report_payload if isinstance(report_payload, dict) else None,
            display_stage_dir=display_stage_dir,
            display_apply_summary_path=display_apply_summary_path,
            display_apply_execute_summary_path=display_apply_execute_summary_path,
            display_verify_summary_path=display_verify_summary_path,
            display_report_summary_path=display_report_summary_path,
            write_command=write_command,
            verify_command=verify_command,
        )
        approval_audit = self._build_waiver_apply_approval_audit(
            target_root=resolved_root,
            waiver_apply_dir=waiver_apply_dir,
            report_summary_path=report_summary_path,
            apply_execute_summary_path=(waiver_apply_dir / "source-reconcile-gate-waiver-apply-execute-summary.json"),
            verify_summary_path=verify_summary_path,
            report_payload=report_payload if isinstance(report_payload, dict) else None,
            write_handoff=write_handoff,
        )

        return {
            "target_root": str(resolved_root),
            "snapshots_dir": str(snapshots_dir),
            "history_path": str(history_path),
            "governance_dir": str(governance_dir),
            "governance_summary_path": str(governance_summary_path),
            "waiver_apply_dir": str(waiver_apply_dir),
            "apply_summary_path": str(apply_summary_path),
            "verify_summary_path": str(verify_summary_path),
            "report_summary_path": str(report_summary_path),
            "stage_dir": str(stage_dir),
            "history_exists": history_path.is_file(),
            "governance_summary_exists": governance_summary_path.is_file(),
            "apply_summary_exists": apply_summary_path.is_file(),
            "verify_summary_exists": verify_summary_path.is_file(),
            "report_summary_exists": report_summary_path.is_file(),
            "can_prepare": history_path.is_file() and governance_summary_path.is_file(),
            "governance_report_state": governance_report_state,
            "governance_action_count": governance_action_count,
            "latest_report": report_payload if isinstance(report_payload, dict) else None,
            "write_handoff": write_handoff,
            "approval_audit": approval_audit,
            "recommended_follow_ups": (
                [
                    {
                        "label": "Refresh apply handoff pack",
                        "command": (
                            "python scripts/report_source_reconcile_gate_waiver_apply.py "
                            f"{display_history_path} --output-dir {display_output_dir} "
                            f"--target-root {display_target_root} --stage-dir {display_stage_dir} --json"
                        ),
                        "description": "Regenerate the read-only waiver/apply handoff pack for this retained baseline history.",
                    },
                    {
                        "label": "Stage repo governance changes",
                        "command": (
                            "python scripts/execute_source_reconcile_gate_waiver_apply.py "
                            f"{display_history_path} --output-dir {display_output_dir} "
                            f"--stage-dir {display_stage_dir} --json"
                        ),
                        "description": "Stage reviewed governance-source updates inside a safe staging root before any write-mode apply run.",
                    },
                    {
                        "label": "Write approved governance changes",
                        "command": write_command,
                        "description": "Apply approved waiver updates into repo governance files after manual review. This remains CLI-only because it is write mode.",
                    },
                    {
                        "label": "Verify staged or written results",
                        "command": verify_command,
                        "description": "Re-verify staged or written governance changes against the prepared apply artifacts.",
                    },
                ]
                if history_path.is_file() and governance_summary_path.is_file()
                else []
            ),
        }
