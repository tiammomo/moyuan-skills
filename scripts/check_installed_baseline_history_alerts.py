#!/usr/bin/env python3
"""Flag unusually large installed baseline history transitions."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import report_installed_baseline_history
from market_utils import ROOT


HISTORY_ALERT_POLICIES_DIR = ROOT / "governance" / "history-alert-policies"
HISTORY_ALERT_WAIVERS_DIR = ROOT / "governance" / "history-alert-waivers"
DEFAULT_MAX_ADDED_SKILLS = 1
DEFAULT_MAX_REMOVED_SKILLS = 1
DEFAULT_MAX_CHANGED_SKILLS = 2
DEFAULT_MAX_ADDED_BUNDLES = 0
DEFAULT_MAX_REMOVED_BUNDLES = 0
DEFAULT_MAX_CHANGED_BUNDLES = 1
DEFAULT_MAX_INSTALLED_DELTA = 1
DEFAULT_MAX_BUNDLE_DELTA = 0
ALERT_METRICS = (
    "added_skills",
    "removed_skills",
    "changed_skills",
    "added_bundles",
    "removed_bundles",
    "changed_bundles",
    "installed_delta",
    "bundle_delta",
)
THRESHOLD_FIELDS = (
    "max_added_skills",
    "max_removed_skills",
    "max_changed_skills",
    "max_added_bundles",
    "max_removed_bundles",
    "max_changed_bundles",
    "max_installed_delta",
    "max_bundle_delta",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate installed baseline history transitions against alert thresholds."
    )
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--policy", help="Named policy id or JSON file path for reusable alert thresholds.")
    parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path for approved alert exceptions. May be used more than once.",
    )
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument(
        "--latest-only",
        dest="latest_only",
        action="store_true",
        help="Only evaluate the latest retained transition.",
    )
    scope_group.add_argument(
        "--all-transitions",
        dest="latest_only",
        action="store_false",
        help="Evaluate every retained transition.",
    )
    parser.set_defaults(latest_only=None)
    parser.add_argument("--max-added-skills", type=int, help="Maximum allowed added skills per transition.")
    parser.add_argument("--max-removed-skills", type=int, help="Maximum allowed removed skills per transition.")
    parser.add_argument("--max-changed-skills", type=int, help="Maximum allowed changed skills per transition.")
    parser.add_argument("--max-added-bundles", type=int, help="Maximum allowed added bundles per transition.")
    parser.add_argument("--max-removed-bundles", type=int, help="Maximum allowed removed bundles per transition.")
    parser.add_argument("--max-changed-bundles", type=int, help="Maximum allowed changed bundles per transition.")
    parser.add_argument(
        "--max-installed-delta",
        type=int,
        help="Maximum allowed absolute installed-count delta per transition.",
    )
    parser.add_argument(
        "--max-bundle-delta",
        type=int,
        help="Maximum allowed absolute bundle-count delta per transition.",
    )
    parser.add_argument("--output-path", type=Path, help="Optional JSON alert report output path.")
    parser.add_argument("--markdown-path", type=Path, help="Optional Markdown alert report output path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when active alerts are present.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def default_thresholds() -> dict:
    return {
        "max_added_skills": DEFAULT_MAX_ADDED_SKILLS,
        "max_removed_skills": DEFAULT_MAX_REMOVED_SKILLS,
        "max_changed_skills": DEFAULT_MAX_CHANGED_SKILLS,
        "max_added_bundles": DEFAULT_MAX_ADDED_BUNDLES,
        "max_removed_bundles": DEFAULT_MAX_REMOVED_BUNDLES,
        "max_changed_bundles": DEFAULT_MAX_CHANGED_BUNDLES,
        "max_installed_delta": DEFAULT_MAX_INSTALLED_DELTA,
        "max_bundle_delta": DEFAULT_MAX_BUNDLE_DELTA,
    }


def iter_policy_paths() -> list[Path]:
    return sorted(HISTORY_ALERT_POLICIES_DIR.glob("*.json"))


def iter_waiver_paths() -> list[Path]:
    return sorted(HISTORY_ALERT_WAIVERS_DIR.glob("*.json"))


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
    else:
        latest_only = defaults.get("latest_only")
        if not isinstance(latest_only, bool):
            errors.append(f"{label}: 'defaults.latest_only' must be a boolean")

    thresholds = payload.get("thresholds")
    if not isinstance(thresholds, dict):
        errors.append(f"{label}: 'thresholds' must be an object")
    else:
        for key in THRESHOLD_FIELDS:
            value = thresholds.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"{label}: 'thresholds.{key}' must be an integer >= 0")
        unexpected = sorted(set(thresholds) - set(THRESHOLD_FIELDS))
        if unexpected:
            errors.append(f"{label}: unsupported threshold keys: {', '.join(unexpected)}")

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
        metrics = match.get("metrics")
        if not isinstance(metrics, list) or not metrics or not all(isinstance(item, str) and item.strip() for item in metrics):
            errors.append(f"{label}: 'match.metrics' must be a non-empty list of strings")
        else:
            invalid_metrics = sorted({item.strip() for item in metrics if item.strip() not in ALERT_METRICS})
            if invalid_metrics:
                errors.append(f"{label}: unsupported match metrics: {', '.join(invalid_metrics)}")

        for key in ("before_entry", "after_entry"):
            value = match.get(key)
            if value is None:
                continue
            selectors_present = True
            if not isinstance(value, int) or value < 1:
                errors.append(f"{label}: 'match.{key}' must be an integer >= 1")

        for key in ("before_target_root_suffix", "after_target_root_suffix"):
            value = match.get(key)
            if value is None:
                continue
            selectors_present = True
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: 'match.{key}' must be a non-empty string")

        for key in ("removed_skill_ids", "removed_bundle_ids"):
            value = match.get(key)
            if value is None:
                continue
            selectors_present = True
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{label}: 'match.{key}' must be a list of strings")

        if not selectors_present:
            errors.append(
                f"{label}: 'match' must include at least one selector such as entries, target-root suffix, or removed ids"
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
    raise SystemExit(f"installed history alert policy not found: {token}")


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
    raise SystemExit(f"installed history alert waiver not found: {token}")


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


def threshold_payload(args: argparse.Namespace, policy_payload: dict | None = None) -> dict:
    merged = default_thresholds()
    if isinstance(policy_payload, dict):
        thresholds = policy_payload.get("thresholds", {})
        if isinstance(thresholds, dict):
            for key in THRESHOLD_FIELDS:
                value = thresholds.get(key)
                if isinstance(value, int) and value >= 0:
                    merged[key] = value

    overrides = {
        "max_added_skills": args.max_added_skills,
        "max_removed_skills": args.max_removed_skills,
        "max_changed_skills": args.max_changed_skills,
        "max_added_bundles": args.max_added_bundles,
        "max_removed_bundles": args.max_removed_bundles,
        "max_changed_bundles": args.max_changed_bundles,
        "max_installed_delta": args.max_installed_delta,
        "max_bundle_delta": args.max_bundle_delta,
    }
    for key, value in overrides.items():
        if value is not None:
            merged[key] = value
    return merged


def resolve_latest_only(args: argparse.Namespace, policy_payload: dict | None = None) -> bool:
    if args.latest_only is not None:
        return args.latest_only
    if isinstance(policy_payload, dict):
        defaults = policy_payload.get("defaults", {})
        if isinstance(defaults, dict) and isinstance(defaults.get("latest_only"), bool):
            return defaults["latest_only"]
    return False


def check_count(
    metric: str,
    actual: int,
    threshold: int,
    *,
    before_entry: object,
    after_entry: object,
) -> dict | None:
    if actual <= threshold:
        return None
    return {
        "metric": metric,
        "actual": actual,
        "threshold": threshold,
        "message": f"transition #{before_entry}->{after_entry} exceeds {metric}: {actual} > {threshold}",
    }


def evaluate_transition(transition: dict, thresholds: dict) -> dict:
    summary_delta = transition.get("summary_delta", {})
    installed_delta = summary_delta.get("installed_count", {})
    bundle_delta = summary_delta.get("bundle_count", {})
    before_entry = transition.get("before_entry")
    after_entry = transition.get("after_entry")

    alerts = [
        check_count(
            "added_skills",
            len(transition.get("added_skill_ids", [])),
            thresholds["max_added_skills"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "removed_skills",
            len(transition.get("removed_skill_ids", [])),
            thresholds["max_removed_skills"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "changed_skills",
            len(transition.get("changed_skill_ids", [])),
            thresholds["max_changed_skills"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "added_bundles",
            len(transition.get("added_bundle_ids", [])),
            thresholds["max_added_bundles"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "removed_bundles",
            len(transition.get("removed_bundle_ids", [])),
            thresholds["max_removed_bundles"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "changed_bundles",
            len(transition.get("changed_bundle_ids", [])),
            thresholds["max_changed_bundles"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "installed_delta",
            abs(int(installed_delta.get("delta", 0))) if isinstance(installed_delta, dict) else 0,
            thresholds["max_installed_delta"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
        check_count(
            "bundle_delta",
            abs(int(bundle_delta.get("delta", 0))) if isinstance(bundle_delta, dict) else 0,
            thresholds["max_bundle_delta"],
            before_entry=before_entry,
            after_entry=after_entry,
        ),
    ]
    normalized_alerts = [item for item in alerts if item is not None]
    return {
        "before_entry": before_entry,
        "after_entry": after_entry,
        "before_promoted_at": transition.get("before_promoted_at", ""),
        "after_promoted_at": transition.get("after_promoted_at", ""),
        "before_target_root": transition.get("before_target_root", ""),
        "after_target_root": transition.get("after_target_root", ""),
        "alerts": normalized_alerts,
        "alert_count": len(normalized_alerts),
        "summary_delta": summary_delta,
        "added_skill_ids": transition.get("added_skill_ids", []),
        "removed_skill_ids": transition.get("removed_skill_ids", []),
        "changed_skill_ids": transition.get("changed_skill_ids", []),
        "added_bundle_ids": transition.get("added_bundle_ids", []),
        "removed_bundle_ids": transition.get("removed_bundle_ids", []),
        "changed_bundle_ids": transition.get("changed_bundle_ids", []),
    }


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


def waiver_matches_transition_scope(
    waiver: dict,
    policy_id: str | None,
    transition: dict,
    *,
    require_active: bool = True,
) -> bool:
    if require_active and not is_waiver_active(waiver):
        return False
    waiver_policy_id = str(waiver.get("policy_id", "")).strip()
    if waiver_policy_id and waiver_policy_id != str(policy_id or "").strip():
        return False

    match = waiver.get("match", {})
    if not isinstance(match, dict):
        return False

    before_entry = match.get("before_entry")
    if isinstance(before_entry, int) and transition.get("before_entry") != before_entry:
        return False
    after_entry = match.get("after_entry")
    if isinstance(after_entry, int) and transition.get("after_entry") != after_entry:
        return False

    before_target_root_suffix = str(match.get("before_target_root_suffix", "")).strip()
    if before_target_root_suffix and not normalized_suffix_match(
        str(transition.get("before_target_root", "")),
        before_target_root_suffix,
    ):
        return False
    after_target_root_suffix = str(match.get("after_target_root_suffix", "")).strip()
    if after_target_root_suffix and not normalized_suffix_match(
        str(transition.get("after_target_root", "")),
        after_target_root_suffix,
    ):
        return False

    removed_skill_ids = [
        str(item).strip()
        for item in match.get("removed_skill_ids", [])
        if isinstance(item, str) and item.strip()
    ]
    if removed_skill_ids and not set(removed_skill_ids).issubset(set(transition.get("removed_skill_ids", []))):
        return False

    removed_bundle_ids = [
        str(item).strip()
        for item in match.get("removed_bundle_ids", [])
        if isinstance(item, str) and item.strip()
    ]
    if removed_bundle_ids and not set(removed_bundle_ids).issubset(set(transition.get("removed_bundle_ids", []))):
        return False

    return True


def waiver_matches_alert(
    waiver: dict,
    policy_id: str | None,
    transition: dict,
    alert: dict,
    *,
    require_active: bool = True,
) -> bool:
    if not waiver_matches_transition_scope(
        waiver,
        policy_id,
        transition,
        require_active=require_active,
    ):
        return False

    match = waiver.get("match", {})
    if not isinstance(match, dict):
        return False

    metrics = [str(item).strip() for item in match.get("metrics", []) if str(item).strip()]
    if metrics and alert.get("metric") not in metrics:
        return False

    return True


def apply_waivers_to_transitions(
    transitions: list[dict],
    waivers: list[dict],
    policy_id: str | None,
) -> tuple[int, int, list[dict]]:
    waived_alert_count = 0
    active_alert_count = 0
    matched_waiver_ids: set[str] = set()

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

    for transition in transitions:
        matched_for_transition: set[str] = set()
        alerts = transition.get("alerts", [])
        if not isinstance(alerts, list):
            transition["alerts"] = []
            transition["active_alert_count"] = 0
            transition["waived_alert_count"] = 0
            transition["matched_waiver_ids"] = []
            continue

        for alert in alerts:
            if not isinstance(alert, dict):
                active_alert_count += 1
                continue

            matched_waiver: dict | None = None
            for waiver in waivers:
                if waiver_matches_alert(waiver, policy_id, transition, alert):
                    matched_waiver = waiver
                    break

            if matched_waiver is None:
                alert["waived"] = False
                active_alert_count += 1
                continue

            waiver_id = str(matched_waiver.get("id", "")).strip()
            alert["waived"] = True
            alert["waiver_id"] = waiver_id
            alert["waiver_title"] = matched_waiver.get("title")
            alert["waiver_path"] = matched_waiver.get("_path")
            waived_alert_count += 1
            matched_for_transition.add(waiver_id)
            matched_waiver_ids.add(waiver_id)
            summary = summary_by_id.get(waiver_id)
            if summary is not None:
                summary["matched"] = True

        transition["waived_alert_count"] = sum(
            1 for alert in transition.get("alerts", []) if isinstance(alert, dict) and alert.get("waived") is True
        )
        transition["active_alert_count"] = sum(
            1 for alert in transition.get("alerts", []) if isinstance(alert, dict) and alert.get("waived") is not True
        )
        transition["matched_waiver_ids"] = sorted(matched_for_transition)

    return active_alert_count, waived_alert_count, waiver_summaries


def build_alert_payload(history_path: Path, args: argparse.Namespace) -> dict:
    policy_payload: dict | None = None
    policy_path: Path | None = None
    if args.policy:
        policy_payload, policy_path = resolve_policy_reference(args.policy)
    waivers = resolve_requested_waivers(args.waiver or [])
    report_payload = report_installed_baseline_history.build_report_payload(history_path)
    thresholds = threshold_payload(args, policy_payload)
    transitions = report_payload.get("transitions", [])
    latest_only = resolve_latest_only(args, policy_payload)
    if latest_only and transitions:
        transitions = [transitions[-1]]
    evaluated = [evaluate_transition(item, thresholds) for item in transitions if isinstance(item, dict)]
    alert_count = sum(item.get("alert_count", 0) for item in evaluated)
    active_alert_count, waived_alert_count, waiver_summaries = apply_waivers_to_transitions(
        evaluated,
        waivers,
        str(policy_payload.get("id")) if policy_payload else None,
    )
    return {
        "history_path": report_payload.get("history_path", ""),
        "latest_only": latest_only,
        "policy_id": policy_payload.get("id") if policy_payload else None,
        "policy_title": policy_payload.get("title") if policy_payload else None,
        "policy_path": str(policy_path) if policy_path is not None else None,
        "waivers": waiver_summaries,
        "requested_waiver_count": len(waiver_summaries),
        "matched_waiver_count": sum(1 for item in waiver_summaries if item.get("matched")),
        "thresholds": thresholds,
        "entries_count": report_payload.get("entries_count", 0),
        "evaluated_transition_count": len(evaluated),
        "alert_count": alert_count,
        "active_alert_count": active_alert_count,
        "waived_alert_count": waived_alert_count,
        "passes": active_alert_count == 0,
        "transitions": evaluated,
        "latest_entry": report_payload.get("latest_entry"),
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Installed Baseline History Alerts",
        "",
        f"- History path: `{payload.get('history_path', '')}`",
        f"- Policy id: `{payload.get('policy_id', '')}`",
        f"- Latest only: `{payload.get('latest_only', False)}`",
        f"- Evaluated transitions: `{payload.get('evaluated_transition_count', 0)}`",
        f"- Alert count: `{payload.get('alert_count', 0)}`",
        f"- Active alert count: `{payload.get('active_alert_count', 0)}`",
        f"- Waived alert count: `{payload.get('waived_alert_count', 0)}`",
        f"- Passes: `{payload.get('passes', False)}`",
        "",
        "## Thresholds",
        "",
    ]
    for key, value in payload.get("thresholds", {}).items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Waivers", ""])
    waivers = payload.get("waivers", [])
    if not waivers:
        lines.append("- No waivers requested.")
    else:
        for waiver in waivers:
            lines.append(
                f"- `{waiver.get('id', '')}` active=`{waiver.get('active', False)}` matched=`{waiver.get('matched', False)}`"
            )

    lines.extend(["", "## Transition Alerts", ""])
    transitions = payload.get("transitions", [])
    if not transitions:
        lines.append("- No retained transitions to evaluate.")
    else:
        for item in transitions:
            lines.append(
                f"- `#{item.get('before_entry', '?')}` -> `#{item.get('after_entry', '?')}`"
                f" alerts=`{item.get('alert_count', 0)}`"
                f" active=`{item.get('active_alert_count', 0)}`"
                f" waived=`{item.get('waived_alert_count', 0)}`"
            )
            alerts = item.get("alerts", [])
            if not alerts:
                lines.append("  no alerts")
                continue
            for alert in alerts:
                if alert.get("waived"):
                    lines.append(
                        "  - "
                        f"`{alert.get('metric', '')}` actual=`{alert.get('actual', '')}` threshold=`{alert.get('threshold', '')}`"
                        f" waived_by=`{alert.get('waiver_id', '')}`"
                    )
                else:
                    lines.append(
                        f"  - `{alert.get('metric', '')}` actual=`{alert.get('actual', '')}` threshold=`{alert.get('threshold', '')}`"
                    )

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = build_alert_payload(args.history, args)

    if args.output_path:
        output_path = resolve_repo_path(args.output_path)
        write_text(output_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.markdown_path:
        markdown_path = resolve_repo_path(args.markdown_path)
        write_text(markdown_path, render_markdown(payload))

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Installed baseline history alert check:")
        print(f"- History: {payload['history_path']}")
        print(f"- Latest only: {payload['latest_only']}")
        print(f"- Evaluated transitions: {payload['evaluated_transition_count']}")
        print(f"- Alert count: {payload['alert_count']}")
        print(f"- Active alert count: {payload['active_alert_count']}")
        print(f"- Waived alert count: {payload['waived_alert_count']}")
        print(f"- Passes: {'yes' if payload['passes'] else 'no'}")

    if args.strict and not payload["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
