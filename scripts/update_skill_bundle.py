#!/usr/bin/env python3
"""Update a previously installed starter bundle against the current market state."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import install_skill
from market_utils import (
    ROOT,
    dump_json,
    load_channel_skill_lookup,
    load_filtered_market_inputs,
    load_lock_payload,
    normalize_install_sources,
    reconcile_bundle_sources,
    resolve_bundle_definition,
    resolve_bundle_report,
    resolve_target_root,
)


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update a previously installed starter bundle.")
    parser.add_argument("bundle", help="Bundle id or title.")
    parser.add_argument("--market-dir", type=Path, default=None, help="Generated market artifact directory.")
    parser.add_argument("--org-policy", type=Path, default=None, help="Optional org market policy JSON file.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the bundle update plan without extracting files.")
    return parser


def build_result(skill_id: str, title: str, channel: str, version: str, lifecycle_status: str, install_spec: str, status: str, action: str, reason: str = "") -> dict:
    return {
        "skill_id": skill_id,
        "title": title,
        "channel": channel,
        "version": version,
        "lifecycle_status": lifecycle_status,
        "install_spec": install_spec,
        "status": status,
        "action": action,
        "reason": reason,
    }


def resolve_market_dir(raw_market_dir: Path | None, report_payload: dict) -> Path:
    if raw_market_dir is not None:
        return raw_market_dir if raw_market_dir.is_absolute() else (ROOT / raw_market_dir)
    reported_market_dir = str(report_payload.get("market_dir", "")).strip()
    if reported_market_dir:
        candidate = Path(reported_market_dir)
        return candidate if candidate.is_absolute() else (ROOT / candidate)
    return ROOT / "dist" / "market"


def resolve_org_policy(raw_org_policy: Path | None, report_payload: dict) -> Path | None:
    if raw_org_policy is not None:
        return raw_org_policy if raw_org_policy.is_absolute() else (ROOT / raw_org_policy)
    reported_policy_path = str(report_payload.get("org_policy_path", "")).strip()
    if reported_policy_path:
        candidate = Path(reported_policy_path)
        return candidate if candidate.is_absolute() else (ROOT / candidate)
    if report_payload.get("org_policy"):
        raise ValueError(
            "this bundle was installed with an org-scoped market, but the bundle report does not remember the policy path; rerun with --org-policy"
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_root = resolve_target_root(args.target_root)
    report_path, installed_report, available = resolve_bundle_report(target_root, args.bundle)
    if report_path is None or installed_report is None:
        print(f"ERROR: could not find installed bundle matching '{args.bundle}'")
        if available:
            print("Available installed bundles:")
            for item in available:
                print(f"- {item}")
        return 1

    bundle_id = str(installed_report.get("bundle_id", report_path.stem))
    try:
        org_policy_path = resolve_org_policy(args.org_policy, installed_report)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    market_dir = resolve_market_dir(args.market_dir, installed_report).resolve()

    manifests, bundles, policy_payload, errors = load_filtered_market_inputs(org_policy_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    bundle = resolve_bundle_definition(bundles, bundle_id)
    if bundle is None:
        print(f"ERROR: bundle '{bundle_id}' is no longer available in the current market scope")
        if policy_payload is not None:
            print(f"Current scope: {policy_payload['org_id']}")
        print("If you want to clean it up instead, use remove-bundle.")
        return 1

    channel_lookup, lookup_errors = load_channel_skill_lookup(market_dir, set(bundle["channels"]))
    if lookup_errors:
        for error in lookup_errors:
            print(f"ERROR: {error}")
        return 1

    _, lock_payload = load_lock_payload(target_root)
    installed_entries = [
        entry
        for entry in lock_payload.get("installed", [])
        if isinstance(entry, dict) and entry.get("skill_id")
    ]
    current_managed_ids = {
        str(entry.get("skill_id"))
        for entry in installed_entries
        if any(item["kind"] == "bundle" and item["id"] == bundle_id for item in normalize_install_sources(entry))
    }
    current_entry_by_id = {str(entry.get("skill_id")): entry for entry in installed_entries}
    previous_result_by_id = {
        str(item.get("skill_id")): item
        for item in installed_report.get("results", [])
        if isinstance(item, dict) and item.get("skill_id")
    }
    manifest_by_id = {manifest["id"]: manifest for manifest in manifests}

    report = {
        "bundle_id": bundle["id"],
        "title": bundle["title"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run-update" if args.dry_run else "update",
        "org_policy": policy_payload["org_id"] if policy_payload else None,
        "org_policy_path": str(org_policy_path.resolve()) if org_policy_path is not None else "",
        "market_dir": str(market_dir),
        "target_root": str(target_root),
        "results": [],
    }

    keep_skill_ids: set[str] = set()
    handled_skill_ids: set[str] = set()
    unexpected_failures = False

    print(f"Updating bundle {bundle['id']} ({len(bundle['skills'])} desired skill(s))")
    for skill_id in bundle["skills"]:
        manifest = manifest_by_id.get(skill_id)
        current_owned = skill_id in current_managed_ids
        if manifest is None:
            if current_owned:
                keep_skill_ids.add(skill_id)
            report["results"].append(
                build_result(skill_id, skill_id, "", "", "", "", "failed", "scope-mismatch", "bundle member is not available in the current market scope")
            )
            print(f"FAILED: {skill_id} is not available in the current market scope")
            handled_skill_ids.add(skill_id)
            unexpected_failures = True
            continue

        summary = channel_lookup.get(skill_id)
        install_spec = str((summary or {}).get("install_spec", ""))
        lifecycle_status = manifest["lifecycle"]["status"]

        if lifecycle_status in {"blocked", "archived"}:
            reason = f"lifecycle status '{lifecycle_status}' is not installable"
            status = "planned-removal" if args.dry_run and current_owned else "removed" if current_owned else "skipped"
            action = "reconcile-removal" if current_owned else "skip"
            report["results"].append(
                build_result(
                    skill_id,
                    manifest["title"],
                    manifest["channel"],
                    manifest["version"],
                    lifecycle_status,
                    install_spec,
                    status,
                    action,
                    reason,
                )
            )
            print(f"{status.upper()}: {skill_id} ({reason})")
            handled_skill_ids.add(skill_id)
            continue

        if not install_spec:
            if current_owned:
                keep_skill_ids.add(skill_id)
            report["results"].append(
                build_result(
                    skill_id,
                    manifest["title"],
                    manifest["channel"],
                    manifest["version"],
                    lifecycle_status,
                    install_spec,
                    "failed",
                    "resolve-install-spec",
                    "missing install spec in channel index",
                )
            )
            print(f"FAILED: {skill_id} (missing install spec in channel index)")
            handled_skill_ids.add(skill_id)
            unexpected_failures = True
            continue

        forwarded_args = [
            install_spec,
            "--target-root",
            str(target_root),
            "--source-kind",
            "bundle",
            "--source-id",
            bundle["id"],
        ]
        if args.dry_run:
            forwarded_args.append("--dry-run")
        exit_code = install_skill.main(forwarded_args)
        if exit_code == 0:
            keep_skill_ids.add(skill_id)
            report["results"].append(
                build_result(
                    skill_id,
                    manifest["title"],
                    manifest["channel"],
                    manifest["version"],
                    lifecycle_status,
                    install_spec,
                    "planned" if args.dry_run else "installed",
                    "update" if current_owned else "install",
                )
            )
        else:
            if current_owned:
                keep_skill_ids.add(skill_id)
            report["results"].append(
                build_result(
                    skill_id,
                    manifest["title"],
                    manifest["channel"],
                    manifest["version"],
                    lifecycle_status,
                    install_spec,
                    "failed",
                    "install-command",
                    "install command returned a non-zero exit code",
                )
            )
            print(f"FAILED: {skill_id} (install command returned a non-zero exit code)")
            unexpected_failures = True
        handled_skill_ids.add(skill_id)

    reconcile_result = reconcile_bundle_sources(target_root, bundle_id, keep_skill_ids, apply_changes=not args.dry_run)
    for skill_id in reconcile_result["removed_skill_ids"]:
        if skill_id in handled_skill_ids:
            continue
        previous = previous_result_by_id.get(skill_id, {})
        current_entry = current_entry_by_id.get(skill_id, {})
        report["results"].append(
            build_result(
                skill_id,
                str(previous.get("title") or current_entry.get("skill_name") or skill_id),
                str(previous.get("channel") or current_entry.get("channel") or ""),
                str(previous.get("version") or current_entry.get("version") or ""),
                str(previous.get("lifecycle_status") or current_entry.get("lifecycle_status") or ""),
                str(previous.get("install_spec") or current_entry.get("install_spec") or ""),
                "planned-removal" if args.dry_run else "removed",
                "reconcile-removal",
                "skill is no longer part of the current bundle definition",
            )
        )

    counts = Counter(result["status"] for result in report["results"])
    print(
        f"Bundle {bundle['id']} update summary: "
        f"installed={counts.get('installed', 0)} "
        f"planned={counts.get('planned', 0)} "
        f"removed={counts.get('removed', 0)} "
        f"planned_removals={counts.get('planned-removal', 0)} "
        f"skipped={counts.get('skipped', 0)} "
        f"failed={counts.get('failed', 0)}"
    )

    if not args.dry_run:
        dump_json(report_path, report)
        print(f"Updated bundle report: {report_path}")

    return 1 if unexpected_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
