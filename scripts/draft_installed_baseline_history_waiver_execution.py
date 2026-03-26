#!/usr/bin/env python3
"""Generate execution scaffolding for installed baseline history waiver remediation."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
from datetime import date, timedelta
from pathlib import Path

import audit_installed_baseline_history_waivers
import check_installed_baseline_history_alerts
import remediate_installed_baseline_history_waivers
from market_utils import ROOT, repo_relative_path


DEFAULT_OUTPUT_DIR = ROOT / "dist" / "installed-history-waiver-execution"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draft execution scaffolding for installed baseline history waiver remediation."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to prepare. Defaults to all known waivers.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory for generated execution artifacts.",
    )
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


def build_policy_alert_payload(history_path: Path, policy_id: str) -> dict | None:
    if not policy_id:
        return None
    return check_installed_baseline_history_alerts.build_alert_payload(
        history_path,
        audit_installed_baseline_history_waivers.build_alert_args(policy_id),
    )


def summarize_transition_candidates(alert_payload: dict | None) -> list[dict]:
    if not isinstance(alert_payload, dict):
        return []
    candidates: list[dict] = []
    for transition in alert_payload.get("transitions", []):
        if not isinstance(transition, dict):
            continue
        metrics = sorted(
            {
                str(alert.get("metric", "")).strip()
                for alert in transition.get("alerts", [])
                if isinstance(alert, dict) and str(alert.get("metric", "")).strip()
            }
        )
        candidates.append(
            {
                "before_entry": transition.get("before_entry"),
                "after_entry": transition.get("after_entry"),
                "before_target_root": transition.get("before_target_root", ""),
                "after_target_root": transition.get("after_target_root", ""),
                "before_target_root_suffix": path_suffix(str(transition.get("before_target_root", ""))),
                "after_target_root_suffix": path_suffix(str(transition.get("after_target_root", ""))),
                "alert_metrics": metrics,
                "active_alert_count": transition.get("active_alert_count", 0),
                "alert_count": transition.get("alert_count", 0),
                "removed_skill_ids": list(transition.get("removed_skill_ids", [])),
                "removed_bundle_ids": list(transition.get("removed_bundle_ids", [])),
                "changed_skill_ids": list(transition.get("changed_skill_ids", [])),
                "changed_bundle_ids": list(transition.get("changed_bundle_ids", [])),
                "summary_delta": transition.get("summary_delta", {}),
            }
        )
    return candidates


def choose_transition_candidate(
    waiver: dict,
    candidates: list[dict],
    *,
    preferred_pairs: set[str] | None = None,
) -> dict | None:
    if not candidates:
        return None

    match = waiver.get("match", {})
    if not isinstance(match, dict):
        match = {}

    preferred_pairs = preferred_pairs or set()
    original_metrics = {str(item).strip() for item in match.get("metrics", []) if str(item).strip()}
    original_removed_skills = {
        str(item).strip() for item in match.get("removed_skill_ids", []) if str(item).strip()
    }
    original_removed_bundles = {
        str(item).strip() for item in match.get("removed_bundle_ids", []) if str(item).strip()
    }
    before_suffix = str(match.get("before_target_root_suffix", "")).strip()
    after_suffix = str(match.get("after_target_root_suffix", "")).strip()

    def candidate_score(candidate: dict) -> tuple[int, int, int]:
        pair = f"{candidate.get('before_entry')}->{candidate.get('after_entry')}"
        score = 0
        if pair in preferred_pairs:
            score += 10
        candidate_metrics = set(candidate.get("alert_metrics", []))
        score += len(candidate_metrics & original_metrics) * 4
        score += len(set(candidate.get("removed_skill_ids", [])) & original_removed_skills) * 2
        score += len(set(candidate.get("removed_bundle_ids", [])) & original_removed_bundles) * 2
        if before_suffix and candidate.get("before_target_root_suffix") == before_suffix:
            score += 1
        if after_suffix and candidate.get("after_target_root_suffix") == after_suffix:
            score += 1
        score += int(candidate.get("active_alert_count", 0))
        return (
            score,
            int(candidate.get("after_entry") or 0),
            int(candidate.get("before_entry") or 0),
        )

    return max(candidates, key=candidate_score)


def merge_metrics(existing_metrics: list[str], candidate_metrics: list[str]) -> list[str]:
    existing = [str(item).strip() for item in existing_metrics if str(item).strip()]
    candidate = [str(item).strip() for item in candidate_metrics if str(item).strip()]
    intersection = sorted(set(existing) & set(candidate))
    if intersection:
        return intersection
    if candidate:
        return sorted(dict.fromkeys(candidate))
    return sorted(dict.fromkeys(existing))


def build_review_metadata(strategy: str, waiver_result: dict, candidate: dict | None) -> dict:
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
    if candidate is not None:
        metadata["candidate_transition"] = {
            "before_entry": candidate.get("before_entry"),
            "after_entry": candidate.get("after_entry"),
            "before_target_root_suffix": candidate.get("before_target_root_suffix", ""),
            "after_target_root_suffix": candidate.get("after_target_root_suffix", ""),
            "alert_metrics": candidate.get("alert_metrics", []),
            "removed_skill_ids": candidate.get("removed_skill_ids", []),
            "removed_bundle_ids": candidate.get("removed_bundle_ids", []),
        }
    return metadata


def build_renewal_draft(waiver: dict, waiver_result: dict) -> dict:
    payload = sanitize_waiver_payload(waiver)
    approval = payload.setdefault("approval", {})
    approval["approved_at"] = iso_today()
    previous_reason = str(approval.get("reason", "")).strip()
    approval["reason"] = (
        f"TODO: refresh the approval rationale for waiver '{payload.get('id', '')}'. "
        f"Previous reason: {previous_reason}"
    )
    payload["expires_on"] = suggested_expiry()
    payload["_draft"] = build_review_metadata("renew", waiver_result, None)
    payload["_draft"]["review_notes"] = [
        "Confirm the exception is still expected before keeping the waiver.",
        "Replace the TODO approval reason with a reviewer-approved explanation.",
        "Adjust expires_on to the real renewal window before promoting the draft.",
    ]
    return payload


def apply_transition_to_match(match: dict, candidate: dict) -> None:
    if candidate.get("before_entry") is not None:
        match["before_entry"] = candidate.get("before_entry")
    if candidate.get("after_entry") is not None:
        match["after_entry"] = candidate.get("after_entry")

    before_suffix = str(candidate.get("before_target_root_suffix", "")).strip()
    if before_suffix:
        match["before_target_root_suffix"] = before_suffix
    else:
        match.pop("before_target_root_suffix", None)

    after_suffix = str(candidate.get("after_target_root_suffix", "")).strip()
    if after_suffix:
        match["after_target_root_suffix"] = after_suffix
    else:
        match.pop("after_target_root_suffix", None)


def sync_selector_lists(match: dict, candidate: dict) -> None:
    metrics = [str(item).strip() for item in match.get("metrics", []) if str(item).strip()]
    if "removed_skills" in metrics and candidate.get("removed_skill_ids"):
        match["removed_skill_ids"] = list(candidate.get("removed_skill_ids", []))
    else:
        match.pop("removed_skill_ids", None)

    if "removed_bundles" in metrics and candidate.get("removed_bundle_ids"):
        match["removed_bundle_ids"] = list(candidate.get("removed_bundle_ids", []))
    else:
        match.pop("removed_bundle_ids", None)


def build_rescope_draft(waiver: dict, waiver_result: dict, candidate: dict) -> dict:
    payload = sanitize_waiver_payload(waiver)
    match = payload.setdefault("match", {})
    existing_metrics = list(match.get("metrics", []))
    apply_transition_to_match(match, candidate)
    match["metrics"] = merge_metrics(existing_metrics, list(candidate.get("alert_metrics", [])))
    sync_selector_lists(match, candidate)

    approval = payload.setdefault("approval", {})
    approval["approved_at"] = iso_today()
    approval["reason"] = (
        f"TODO: confirm the new retained transition for waiver '{payload.get('id', '')}' "
        "and replace this placeholder with the reviewed approval rationale."
    )
    payload["_draft"] = build_review_metadata("rescope", waiver_result, candidate)
    payload["_draft"]["review_notes"] = [
        "Confirm the suggested retained transition is the one the team still wants to waive.",
        "Review the regenerated metrics and selector lists before updating the source waiver file.",
        "Delete the source waiver instead if this exception is no longer needed.",
    ]
    return payload


def build_replacement_draft(waiver: dict, waiver_result: dict, candidate: dict) -> dict:
    payload = sanitize_waiver_payload(waiver)
    match = payload.setdefault("match", {})
    existing_metrics = list(match.get("metrics", []))
    match["metrics"] = merge_metrics(existing_metrics, list(candidate.get("alert_metrics", [])))
    apply_transition_to_match(match, candidate)
    sync_selector_lists(match, candidate)

    approval = payload.setdefault("approval", {})
    approval["approved_at"] = iso_today()
    approval["reason"] = (
        f"TODO: confirm the replacement alert scope for waiver '{payload.get('id', '')}' "
        "and replace this placeholder with the reviewed approval rationale."
    )
    payload["_draft"] = build_review_metadata("replace", waiver_result, candidate)
    payload["_draft"]["review_notes"] = [
        "Make sure the proposed metrics represent the alert that still needs approval.",
        "Drop the waiver instead of replacing it if no current alert should stay waived.",
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
        "finding_codes": [
            str(finding.get("code", "")).strip()
            for finding in waiver_result.get("findings", [])
            if isinstance(finding, dict) and str(finding.get("code", "")).strip()
        ],
    }


def build_execution_artifacts(
    history_path: Path,
    waiver: dict,
    waiver_result: dict,
    action: dict,
    output_dir: Path | None,
) -> tuple[dict, list[tuple[Path, str]]]:
    artifacts: list[tuple[Path, str]] = []
    waiver_id = str(waiver.get("id", "")).strip()
    policy_id = str(waiver.get("policy_id", "")).strip()
    alert_payload = build_policy_alert_payload(history_path, policy_id)
    candidates = summarize_transition_candidates(alert_payload)
    action_code = str(action.get("code", "")).strip()
    slug = slugify(waiver_id)
    base_dir = output_dir / "waivers" / slug if output_dir is not None else None

    if action_code == "renew_or_remove":
        draft_payload = build_renewal_draft(waiver, waiver_result)
        draft_relative = f"waivers/{slug}/renewal-draft.json"
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
                "draft_path": draft_relative if output_dir is not None else "",
                "delete_path": str(waiver.get("_path", "")),
                "review_steps": list(action.get("suggested_steps", [])),
                "candidate_transition": None,
                "candidate_metrics": [],
            },
            artifacts,
        )

    if action_code == "rescope_or_remove":
        candidate = choose_transition_candidate(waiver, candidates)
        if candidate is not None and candidate.get("alert_metrics"):
            draft_payload = build_rescope_draft(waiver, waiver_result, candidate)
            draft_relative = f"waivers/{slug}/rescope-draft.json"
            if base_dir is not None:
                artifacts.append((base_dir / "rescope-draft.json", json.dumps(draft_payload, indent=2, ensure_ascii=False) + "\n"))
            return (
                {
                    "waiver_id": waiver_id,
                    "action_code": action_code,
                    "mode": "draft_update",
                    "priority": action.get("priority"),
                    "summary": action.get("summary"),
                    "why": action.get("why"),
                    "source_path": str(waiver.get("_path", "")),
                    "draft_path": draft_relative if output_dir is not None else "",
                    "delete_path": str(waiver.get("_path", "")),
                    "review_steps": list(action.get("suggested_steps", [])),
                    "candidate_transition": candidate,
                    "candidate_metrics": list(candidate.get("alert_metrics", [])),
                },
                artifacts,
            )
        review_payload = build_remove_review(action, waiver, waiver_result)
        if base_dir is not None:
            artifacts.append((base_dir / "remove-review.json", json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n"))
        return (
            {
                **review_payload,
                "review_path": f"waivers/{slug}/remove-review.json" if output_dir is not None else "",
                "candidate_transition": None,
                "candidate_metrics": [],
            },
            artifacts,
        )

    if action_code == "retire_or_replace":
        preferred_pairs = {
            str(pair).strip()
            for pair in waiver_result.get("matched_transition_pairs", [])
            if str(pair).strip()
        }
        candidate = choose_transition_candidate(waiver, candidates, preferred_pairs=preferred_pairs)
        if candidate is not None and candidate.get("alert_metrics"):
            draft_payload = build_replacement_draft(waiver, waiver_result, candidate)
            draft_relative = f"waivers/{slug}/replacement-draft.json"
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
                    "draft_path": draft_relative if output_dir is not None else "",
                    "delete_path": str(waiver.get("_path", "")),
                    "review_steps": list(action.get("suggested_steps", [])),
                    "candidate_transition": candidate,
                    "candidate_metrics": list(candidate.get("alert_metrics", [])),
                },
                artifacts,
            )
        review_payload = build_remove_review(action, waiver, waiver_result)
        if base_dir is not None:
            artifacts.append((base_dir / "remove-review.json", json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n"))
        return (
            {
                **review_payload,
                "review_path": f"waivers/{slug}/remove-review.json" if output_dir is not None else "",
                "candidate_transition": candidate,
                "candidate_metrics": list(candidate.get("alert_metrics", [])) if candidate is not None else [],
            },
            artifacts,
        )

    review_payload = build_policy_review(action, waiver, waiver_result)
    if base_dir is not None:
        artifacts.append((base_dir / "policy-review.json", json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n"))
    return (
        {
            **review_payload,
            "review_path": f"waivers/{slug}/policy-review.json" if output_dir is not None else "",
            "candidate_transition": None,
            "candidate_metrics": [],
        },
        artifacts,
    )


def write_execution_artifacts(base_dir: Path, waiver_summary: dict, action_summaries: list[dict], files: list[tuple[Path, str]]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    execution_payload = dict(waiver_summary)
    execution_payload["execution_actions"] = action_summaries
    write_text(base_dir / "execution.json", json.dumps(execution_payload, indent=2, ensure_ascii=False) + "\n")

    markdown_lines = [
        f"# Waiver Execution Draft: {waiver_summary.get('id', '')}",
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


def build_execution_payload(history_path: Path, waiver_tokens: list[str], output_dir: Path | None) -> dict:
    remediation_payload = remediate_installed_baseline_history_waivers.build_remediation_payload(
        history_path,
        waiver_tokens,
    )
    actual_waivers = audit_installed_baseline_history_waivers.resolve_audited_waivers(waiver_tokens)
    waivers_by_id = {
        str(waiver.get("id", "")).strip(): waiver
        for waiver in actual_waivers
        if isinstance(waiver, dict) and str(waiver.get("id", "")).strip()
    }

    waiver_payloads: list[dict] = []
    execution_count = 0
    draft_count = 0
    review_count = 0

    if output_dir is not None:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

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
                    source_waiver,
                    waiver_summary,
                    action,
                    output_dir,
                )
                actions_summary.append(execution_summary)
                artifact_files.extend(files)

        execution_count += len(actions_summary)
        draft_count += sum(1 for item in actions_summary if item.get("mode") == "draft_update")
        review_count += sum(1 for item in actions_summary if item.get("mode") != "draft_update")

        waiver_payload = dict(waiver_summary)
        waiver_payload["execution_actions"] = actions_summary
        if output_dir is not None and actions_summary:
            waiver_dir = output_dir / "waivers" / slugify(waiver_id)
            write_execution_artifacts(waiver_dir, waiver_summary, actions_summary, artifact_files)
            waiver_payload["artifact_dir"] = repo_relative_path(waiver_dir)
        else:
            waiver_payload["artifact_dir"] = ""
        waiver_payloads.append(waiver_payload)

    return {
        "history_path": remediation_payload.get("history_path", ""),
        "waiver_count": remediation_payload.get("waiver_count", 0),
        "finding_count": remediation_payload.get("finding_count", 0),
        "remediation_count": remediation_payload.get("remediation_count", 0),
        "execution_count": execution_count,
        "draft_count": draft_count,
        "review_count": review_count,
        "passes": execution_count == 0,
        "output_dir": repo_relative_path(output_dir) if output_dir is not None else "",
        "waivers": waiver_payloads,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Waiver Execution Drafts",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Waivers: `{payload.get('waiver_count', 0)}`",
        f"- Findings: `{payload.get('finding_count', 0)}`",
        f"- Execution actions: `{payload.get('execution_count', 0)}`",
        f"- Draft updates: `{payload.get('draft_count', 0)}`",
        f"- Review-only actions: `{payload.get('review_count', 0)}`",
        f"- Output dir: `{payload.get('output_dir', '')}`",
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
                draft_path = str(action.get("draft_path", "")).strip()
                review_path = str(action.get("review_path", "")).strip()
                location = draft_path or review_path or "(inline only)"
                lines.append(
                    f"  - `{action.get('action_code', '')}` mode=`{action.get('mode', '')}` location=`{location}`"
                )

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = resolve_repo_path(args.output_dir) if args.output_dir else None
    payload = build_execution_payload(args.history, args.waiver, output_dir)

    summary_json_path = resolve_repo_path(args.output_path) if args.output_path else None
    summary_markdown_path = resolve_repo_path(args.markdown_path) if args.markdown_path else None

    if output_dir is not None and summary_json_path is None:
        summary_json_path = output_dir / "execution-summary.json"
    if output_dir is not None and summary_markdown_path is None:
        summary_markdown_path = output_dir / "execution-summary.md"

    if summary_json_path is not None:
        write_text(summary_json_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    if summary_markdown_path is not None:
        write_text(summary_markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history waiver execution drafts:")
        print(f"- History: {payload['history_path']}")
        print(f"- Waivers: {payload['waiver_count']}")
        print(f"- Execution actions: {payload['execution_count']}")
        print(f"- Draft updates: {payload['draft_count']}")
        print(f"- Review-only actions: {payload['review_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
