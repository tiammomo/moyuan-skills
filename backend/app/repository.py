from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from .config import Settings, get_settings


VALID_CHANNELS = ("stable", "beta", "internal")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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

    return {
        "state": state,
        "ready": state == "ready",
        "requires_explicit_approval": True,
        "title": title,
        "summary": summary,
        "write_command": write_command if commands_available else "",
        "verify_command": verify_command if commands_available else "",
        "rollback_hint": rollback_hint,
        "blocked_reasons": blocked_reasons,
        "checklist": checklist,
        "governance_source_paths": source_paths,
        "artifact_paths": artifact_paths,
    }


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

    def get_skill_doc(self, name: str) -> str | None:
        doc_path = self.settings.docs_root / f"{name}.md"
        if not doc_path.is_file():
            return None
        return _read_text(doc_path)

    def get_teaching_doc(self, doc_id: str) -> dict[str, Any] | None:
        path = self.settings.teaching_root / f"{doc_id}.md"
        if not path.is_file():
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
        path = self.settings.docs_root / f"{doc_id}.md"
        if not path.is_file() or _is_internal_iteration_doc(path):
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
            markdown = self.get_skill_doc(name)
            if not markdown:
                continue
            skill_docs.append(
                {
                    "id": name,
                    "kind": "skill",
                    "title": _first_heading(markdown, str(skill.get("title", name))),
                    "summary": _first_paragraph(markdown) or str(skill.get("summary", "")),
                    "path": f"docs/{name}.md",
                }
            )

        teaching_docs: list[dict[str, Any]] = []
        for path in sorted(self.settings.teaching_root.glob("*.md")):
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
        skill_doc_names = {f"{skill['name']}.md" for skill in self.get_all_skills() if skill.get("name")}
        for path in sorted(self.settings.docs_root.glob("*.md")):
            if path.name == "README.md" or path.name in skill_doc_names or _is_internal_iteration_doc(path):
                continue
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
            "write_handoff": _build_waiver_apply_write_handoff(
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
            ),
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
