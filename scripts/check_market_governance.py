#!/usr/bin/env python3
"""Validate publisher profiles and org market policies."""

from __future__ import annotations

import check_installed_baseline_history_alerts
import check_installed_baseline_history_waiver_source_reconcile_gate
import check_source_reconcile_gate_waiver_apply_gate
from market_utils import (
    collect_valid_manifests,
    iter_org_policy_paths,
    load_publisher_profiles,
    validate_org_policy,
)


def main() -> int:
    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    history_alert_policies, history_alert_policy_errors = check_installed_baseline_history_alerts.load_policy_profiles()
    history_alert_waivers, history_alert_waiver_errors = check_installed_baseline_history_alerts.load_waiver_profiles()
    source_reconcile_gate_policies, source_reconcile_gate_policy_errors = check_installed_baseline_history_waiver_source_reconcile_gate.load_policy_profiles()
    source_reconcile_gate_waivers, source_reconcile_gate_waiver_errors = check_installed_baseline_history_waiver_source_reconcile_gate.load_waiver_profiles()
    source_reconcile_apply_gate_policies, source_reconcile_apply_gate_policy_errors = check_source_reconcile_gate_waiver_apply_gate.load_policy_profiles()
    source_reconcile_apply_gate_waivers, source_reconcile_apply_gate_waiver_errors = check_source_reconcile_gate_waiver_apply_gate.load_waiver_profiles()
    errors = [
        *manifest_errors,
        *publisher_errors,
        *history_alert_policy_errors,
        *history_alert_waiver_errors,
        *source_reconcile_gate_policy_errors,
        *source_reconcile_gate_waiver_errors,
        *source_reconcile_apply_gate_policy_errors,
        *source_reconcile_apply_gate_waiver_errors,
    ]
    known_history_policy_ids = {
        str(policy.get("id", "")).strip()
        for policy in history_alert_policies
        if isinstance(policy, dict)
    }
    known_source_reconcile_policy_ids = {
        str(policy.get("id", "")).strip()
        for policy in source_reconcile_gate_policies
        if isinstance(policy, dict)
    }
    known_source_reconcile_apply_policy_ids = {
        str(policy.get("id", "")).strip()
        for policy in source_reconcile_apply_gate_policies
        if isinstance(policy, dict)
    }

    known_skill_ids = {manifest["id"] for manifest in manifests}
    valid_policy_count = 0
    for path in iter_org_policy_paths():
        _, policy_errors = validate_org_policy(path, publisher_profiles, known_skill_ids)
        if policy_errors:
            errors.extend(policy_errors)
            continue
        valid_policy_count += 1

    for waiver in history_alert_waivers:
        waiver_id = str(waiver.get("id", "")).strip()
        policy_id = str(waiver.get("policy_id", "")).strip()
        if policy_id and policy_id not in known_history_policy_ids:
            errors.append(
                f"history alert waiver '{waiver_id}' references unknown policy id '{policy_id}'"
            )
    for waiver in source_reconcile_gate_waivers:
        waiver_id = str(waiver.get("id", "")).strip()
        policy_id = str(waiver.get("policy_id", "")).strip()
        if policy_id and policy_id not in known_source_reconcile_policy_ids:
            errors.append(
                f"source-reconcile gate waiver '{waiver_id}' references unknown policy id '{policy_id}'"
            )
    for waiver in source_reconcile_apply_gate_waivers:
        waiver_id = str(waiver.get("id", "")).strip()
        policy_id = str(waiver.get("policy_id", "")).strip()
        if policy_id and policy_id not in known_source_reconcile_apply_policy_ids:
            errors.append(
                f"source-reconcile gate waiver apply waiver '{waiver_id}' references unknown policy id '{policy_id}'"
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Market governance check passed for "
        f"{len(publisher_profiles)} publisher profile(s), "
        f"{valid_policy_count} org policy file(s), and "
        f"{len(history_alert_policies)} history alert policy file(s), "
        f"{len(history_alert_waivers)} history alert waiver file(s), and "
        f"{len(source_reconcile_gate_policies)} source-reconcile gate policy file(s), and "
        f"{len(source_reconcile_gate_waivers)} source-reconcile gate waiver file(s), and "
        f"{len(source_reconcile_apply_gate_policies)} source-reconcile gate waiver apply policy file(s), and "
        f"{len(source_reconcile_apply_gate_waivers)} source-reconcile gate waiver apply waiver file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
