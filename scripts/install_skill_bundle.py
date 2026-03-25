#!/usr/bin/env python3
"""Install every installable skill from a starter bundle."""

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
    resolve_bundle_definition,
    resolve_target_root,
)


DEFAULT_TARGET = Path("dist/installed-skills")
DEFAULT_MARKET_DIR = Path("dist/market")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install every installable skill from a starter bundle.")
    parser.add_argument("bundle", help="Bundle id or title.")
    parser.add_argument("--market-dir", type=Path, default=DEFAULT_MARKET_DIR, help="Generated market artifact directory.")
    parser.add_argument("--org-policy", type=Path, default=None, help="Optional org market policy JSON file.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the bundle install plan without extracting files.")
    return parser

def result_entry(manifest: dict, summary: dict | None, status: str, reason: str = "") -> dict:
    return {
        "skill_id": manifest["id"],
        "title": manifest["title"],
        "channel": manifest["channel"],
        "version": manifest["version"],
        "lifecycle_status": manifest["lifecycle"]["status"],
        "install_spec": str((summary or {}).get("install_spec", "")),
        "status": status,
        "reason": reason,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifests, bundles, policy_payload, errors = load_filtered_market_inputs(args.org_policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    bundle = resolve_bundle_definition(bundles, args.bundle)
    if bundle is None:
        print(f"ERROR: could not find starter bundle matching '{args.bundle}'")
        if bundles:
            print("Available bundles:")
            for item in bundles:
                print(f"- {item['id']}")
        return 1

    market_dir = (args.market_dir if args.market_dir.is_absolute() else (ROOT / args.market_dir)).resolve()
    org_policy_path = ""
    if args.org_policy is not None:
        resolved_policy = args.org_policy if args.org_policy.is_absolute() else (ROOT / args.org_policy)
        org_policy_path = str(resolved_policy.resolve())
    channel_lookup, lookup_errors = load_channel_skill_lookup(market_dir, set(bundle["channels"]))
    if lookup_errors:
        for error in lookup_errors:
            print(f"ERROR: {error}")
        return 1

    target_root = resolve_target_root(args.target_root)
    manifest_by_id = {manifest["id"]: manifest for manifest in manifests}
    report = {
        "bundle_id": bundle["id"],
        "title": bundle["title"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run" if args.dry_run else "install",
        "org_policy": policy_payload["org_id"] if policy_payload else None,
        "org_policy_path": org_policy_path,
        "market_dir": str(market_dir),
        "target_root": str(target_root),
        "results": [],
    }

    unexpected_failures = False
    print(f"Processing bundle {bundle['id']} ({len(bundle['skills'])} skill(s))")
    for skill_id in bundle["skills"]:
        manifest = manifest_by_id.get(skill_id)
        if manifest is None:
            report["results"].append(
                {
                    "skill_id": skill_id,
                    "status": "failed",
                    "reason": "bundle member is not available in the current market scope",
                }
            )
            print(f"FAILED: {skill_id} is not available in the current market scope")
            unexpected_failures = True
            continue

        summary = channel_lookup.get(skill_id)
        install_spec = str((summary or {}).get("install_spec", ""))
        lifecycle_status = manifest["lifecycle"]["status"]
        if lifecycle_status in {"blocked", "archived"}:
            reason = f"lifecycle status '{lifecycle_status}' is not installable"
            report["results"].append(result_entry(manifest, summary, "skipped", reason))
            print(f"SKIPPED: {skill_id} ({reason})")
            continue
        if not install_spec:
            report["results"].append(result_entry(manifest, summary, "failed", "missing install spec in channel index"))
            print(f"FAILED: {skill_id} (missing install spec in channel index)")
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
            report["results"].append(result_entry(manifest, summary, "planned" if args.dry_run else "installed"))
        else:
            report["results"].append(result_entry(manifest, summary, "failed", "install command returned a non-zero exit code"))
            print(f"FAILED: {skill_id} (install command returned a non-zero exit code)")
            unexpected_failures = True

    counts = Counter(result["status"] for result in report["results"])
    print(
        f"Bundle {bundle['id']} summary: "
        f"installed={counts.get('installed', 0)} "
        f"planned={counts.get('planned', 0)} "
        f"skipped={counts.get('skipped', 0)} "
        f"failed={counts.get('failed', 0)}"
    )

    if not args.dry_run:
        report_path = target_root / "bundle-reports" / f"{bundle['id']}.json"
        dump_json(report_path, report)
        print(f"Bundle report: {report_path}")

    return 1 if unexpected_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
