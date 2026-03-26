#!/usr/bin/env python3
"""Smoke-test the local skills market workflow end to end."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from market_utils import ROOT, load_json, repo_relative_path


DEFAULT_OUTPUT_ROOT = ROOT / "dist" / "market-smoke"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a smoke test for the local skills market pipeline.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Workspace for generated smoke-test artifacts.",
    )
    return parser


def run_python(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result


def require_success(step: str, command: list[str]) -> str:
    result = run_python(command)
    if result.returncode != 0:
        print(f"ERROR: {step} failed")
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        raise SystemExit(1)
    return result.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_root = (args.output_root if args.output_root.is_absolute() else (ROOT / args.output_root)).resolve()
    market_root = output_root / "market"
    install_root = output_root / "installed"
    bundle_install_root = output_root / "bundle-installed"
    doctor_bad_root = output_root / "doctor-bad"

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    require_success("validate manifests", ["scripts/validate_market_manifest.py"])
    require_success("validate governance", ["scripts/check_market_governance.py"])
    require_success(
        "package all skills",
        ["scripts/package_skill.py", "--all", "--output-dir", repo_relative_path(market_root)],
    )
    require_success(
        "build market index",
        ["scripts/build_market_index.py", "--output-dir", repo_relative_path(market_root)],
    )
    require_success(
        "build static market catalog",
        ["scripts/build_market_catalog.py", "--output-dir", repo_relative_path(market_root)],
    )
    require_success(
        "build market recommendations",
        ["scripts/build_market_recommendations.py", "--output-dir", repo_relative_path(market_root)],
    )
    require_success(
        "build federation feed",
        ["scripts/build_federation_feed.py", "--output-dir", repo_relative_path(market_root)],
    )
    require_success(
        "build org market index",
        ["scripts/build_org_market_index.py", "governance/orgs/moyuan-internal.json", "--output-dir", repo_relative_path(market_root)],
    )
    require_success(
        "build org market catalog",
        [
            "scripts/build_market_catalog.py",
            "--output-dir",
            repo_relative_path(market_root),
            "--org-policy",
            "governance/orgs/moyuan-internal.json",
        ],
    )
    require_success(
        "build org recommendations",
        [
            "scripts/build_market_recommendations.py",
            "--output-dir",
            repo_relative_path(market_root),
            "--org-policy",
            "governance/orgs/moyuan-internal.json",
        ],
    )
    require_success(
        "build org federation feed",
        [
            "scripts/build_federation_feed.py",
            "--output-dir",
            repo_relative_path(market_root),
            "--org-policy",
            "governance/orgs/moyuan-internal.json",
        ],
    )
    require_success(
        "build hosted registry",
        ["scripts/build_market_registry.py", "--output-dir", repo_relative_path(output_root / "registry")],
    )

    stable_index = market_root / "channels" / "stable.json"
    search_output = require_success(
        "search stable index",
        [
            "scripts/search_skills.py",
            "--query",
            "release",
            "--index",
            repo_relative_path(stable_index),
        ],
    )
    if "moyuan.release-note-writer" not in search_output:
        print("ERROR: search smoke test did not return moyuan.release-note-writer")
        return 1

    catalog_home = market_root / "site" / "index.html"
    if not catalog_home.is_file():
        print(f"ERROR: expected static catalog home {catalog_home} to exist")
        return 1
    catalog_text = catalog_home.read_text(encoding="utf-8")
    if "Moyuan Skills Market" not in catalog_text or "channels/stable.html" not in catalog_text:
        print("ERROR: static catalog home page is missing expected market content")
        return 1
    if "Starter bundles" not in catalog_text:
        print("ERROR: static catalog home page should surface starter bundles")
        return 1
    channel_page = market_root / "site" / "channels" / "stable.html"
    detail_page = market_root / "site" / "skills" / "release-note-writer.html"
    if not channel_page.is_file() or not detail_page.is_file():
        print("ERROR: static catalog should include channel and skill detail pages")
        return 1
    if "../skills/release-note-writer.html" not in channel_page.read_text(encoding="utf-8"):
        print("ERROR: stable channel page should link to the release-note-writer detail page")
        return 1
    if "../channels/stable.html" not in detail_page.read_text(encoding="utf-8"):
        print("ERROR: release-note-writer detail page should link back to its channel page")
        return 1
    if "Verified Publisher" not in catalog_text:
        print("ERROR: static catalog should expose verified publisher badges")
        return 1
    if "<dt>Lifecycle</dt>" not in detail_page.read_text(encoding="utf-8"):
        print("ERROR: skill detail page should include lifecycle metadata")
        return 1

    recommendations_index = load_json(market_root / "recommendations" / "index.json")
    recommendation_paths = recommendations_index.get("skills", {})
    release_recommendation_path = ROOT / recommendation_paths.get("moyuan.release-note-writer", "")
    if not release_recommendation_path.is_file():
        print("ERROR: release-note-writer recommendations should be generated")
        return 1
    release_recommendations = load_json(release_recommendation_path)
    recommended_ids = {item["id"] for item in release_recommendations.get("recommendations", [])}
    if "moyuan.issue-triage-report" not in recommended_ids:
        print("ERROR: release-note-writer recommendations should include issue-triage-report")
        return 1
    bundle_list_output = require_success(
        "list starter bundles",
        ["scripts/list_skill_bundles.py"],
    )
    if "release-engineering-starter" not in bundle_list_output:
        print("ERROR: starter bundle listing should include release-engineering-starter")
        return 1
    org_bundle_list_output = require_success(
        "list org starter bundles",
        ["scripts/list_skill_bundles.py", "--org-policy", "governance/orgs/moyuan-internal.json"],
    )
    if "skill-authoring-starter" in org_bundle_list_output:
        print("ERROR: org bundle listing should respect featured bundle filtering")
        return 1

    federation_feed = load_json(market_root / "federation" / "public-feed.json")
    if not federation_feed.get("bundles"):
        print("ERROR: federation feed should include starter bundles")
        return 1

    org_index = market_root / "orgs" / "moyuan-internal" / "index.json"
    org_catalog = market_root / "orgs" / "moyuan-internal" / "site" / "index.html"
    if not org_index.is_file() or not org_catalog.is_file():
        print("ERROR: org market artifacts should be generated for moyuan-internal")
        return 1
    org_index_payload = load_json(org_index)
    if org_index_payload.get("org", {}).get("org_id") != "moyuan-internal":
        print("ERROR: org market index should expose org metadata")
        return 1
    stable_org_path = market_root / "orgs" / "moyuan-internal" / "channels" / "stable.json"
    beta_org_path = market_root / "orgs" / "moyuan-internal" / "channels" / "beta.json"
    stable_org_payload = load_json(stable_org_path)
    beta_org_payload = load_json(beta_org_path)
    stable_skill_ids = {entry["id"] for entry in stable_org_payload.get("skills", [])}
    beta_skill_ids = {entry["id"] for entry in beta_org_payload.get("skills", [])}
    if "moyuan.release-note-writer" not in stable_skill_ids:
        print("ERROR: org market stable index should include moyuan.release-note-writer")
        return 1
    if "moyuan.harness-engineering" in beta_skill_ids:
        print("ERROR: blocked skill moyuan.harness-engineering should not appear in org beta index")
        return 1
    org_catalog_text = org_catalog.read_text(encoding="utf-8")
    if "Moyuan Internal Skills Market" not in org_catalog_text:
        print("ERROR: org catalog should surface the org display name")
        return 1
    org_feed = load_json(market_root / "orgs" / "moyuan-internal" / "federation" / "feed.json")
    org_feed_ids = {entry["id"] for entry in org_feed.get("skills", [])}
    if org_feed_ids != {
        "moyuan.release-note-writer",
        "moyuan.issue-triage-report",
        "moyuan.api-change-risk-review",
        "moyuan.incident-postmortem-writer",
    }:
        print("ERROR: org federation feed should only expose allowlisted business skills")
        return 1

    release_spec = market_root / "install" / "release-note-writer-0.1.0.json"
    require_success(
        "verify release-note provenance",
        ["scripts/verify_market_provenance.py", repo_relative_path(release_spec)],
    )
    require_success(
        "dry-run install",
        [
            "scripts/install_skill.py",
            repo_relative_path(release_spec),
            "--target-root",
            repo_relative_path(install_root),
            "--dry-run",
        ],
    )
    require_success(
        "install release-note-writer",
        [
            "scripts/install_skill.py",
            repo_relative_path(release_spec),
            "--target-root",
            repo_relative_path(install_root),
        ],
    )
    list_output = require_success(
        "list installed skills",
        [
            "scripts/list_installed_skills.py",
            "--target-root",
            repo_relative_path(install_root),
        ],
    )
    if "moyuan.release-note-writer" not in list_output:
        print("ERROR: list-installed should show moyuan.release-note-writer after install")
        return 1
    require_success(
        "doctor installed direct state",
        [
            "scripts/check_installed_market_state.py",
            "--target-root",
            repo_relative_path(install_root),
            "--strict",
        ],
    )
    require_success(
        "dry-run update release-note-writer",
        [
            "scripts/update_installed_skill.py",
            "moyuan.release-note-writer",
            "--index",
            repo_relative_path(stable_index),
            "--target-root",
            repo_relative_path(install_root),
            "--dry-run",
        ],
    )

    installed_entrypoint = install_root / "release-note-writer" / "SKILL.md"
    if not installed_entrypoint.is_file():
        print(f"ERROR: expected installed entrypoint {installed_entrypoint} to exist")
        return 1

    lock_payload = load_json(install_root / "skills.lock.json")
    installed_skill_ids = {entry.get("skill_id") for entry in lock_payload.get("installed", [])}
    if "moyuan.release-note-writer" not in installed_skill_ids:
        print("ERROR: release-note-writer is missing from skills.lock.json after install")
        return 1

    tampered_spec = load_json(release_spec)
    tampered_spec["checksum_sha256"] = "0" * 64
    tampered_path = output_root / "tampered-release-note-writer.json"
    tampered_path.write_text(json.dumps(tampered_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tampered_result = run_python(
        [
            "scripts/install_skill.py",
            repo_relative_path(tampered_path),
            "--target-root",
            repo_relative_path(install_root),
            "--dry-run",
        ]
    )
    if tampered_result.returncode == 0 or "checksum mismatch" not in tampered_result.stdout:
        print("ERROR: tampered install spec should fail checksum validation")
        if tampered_result.stdout.strip():
            print(tampered_result.stdout.strip())
        if tampered_result.stderr.strip():
            print(tampered_result.stderr.strip())
        return 1

    archived_spec = market_root / "install" / "harness-engineering-0.1.0.json"
    archived_result = run_python(
        [
            "scripts/install_skill.py",
            repo_relative_path(archived_spec),
            "--target-root",
            repo_relative_path(install_root),
            "--dry-run",
        ]
    )
    if archived_result.returncode == 0 or "marked as 'archived'" not in archived_result.stdout:
        print("ERROR: archived skills should be blocked from install")
        if archived_result.stdout.strip():
            print(archived_result.stdout.strip())
        if archived_result.stderr.strip():
            print(archived_result.stderr.strip())
        return 1

    deprecated_spec = market_root / "install" / "progressive-disclosure-0.1.0.json"
    deprecated_result = run_python(
        [
            "scripts/install_skill.py",
            repo_relative_path(deprecated_spec),
            "--target-root",
            repo_relative_path(install_root),
            "--dry-run",
        ]
    )
    if deprecated_result.returncode != 0 or "WARNING: installing a deprecated skill" not in deprecated_result.stdout:
        print("ERROR: deprecated skills should warn but remain installable")
        if deprecated_result.stdout.strip():
            print(deprecated_result.stdout.strip())
        if deprecated_result.stderr.strip():
            print(deprecated_result.stderr.strip())
        return 1

    require_success(
        "remove release-note-writer",
        [
            "scripts/remove_skill.py",
            "moyuan.release-note-writer",
            "--target-root",
            repo_relative_path(install_root),
        ],
    )
    if installed_entrypoint.exists():
        print("ERROR: remove should delete the installed skill directory")
        return 1
    lock_after_remove = load_json(install_root / "skills.lock.json")
    if any(entry.get("skill_id") == "moyuan.release-note-writer" for entry in lock_after_remove.get("installed", [])):
        print("ERROR: remove should delete release-note-writer from the lock file")
        return 1

    require_success(
        "direct install release-note-writer into bundle target",
        [
            "scripts/install_skill.py",
            repo_relative_path(release_spec),
            "--target-root",
            repo_relative_path(bundle_install_root),
        ],
    )
    require_success(
        "install release-engineering bundle",
        [
            "scripts/install_skill_bundle.py",
            "release-engineering-starter",
            "--market-dir",
            repo_relative_path(market_root),
            "--target-root",
            repo_relative_path(bundle_install_root),
        ],
    )
    bundle_report_path = bundle_install_root / "bundle-reports" / "release-engineering-starter.json"
    if not bundle_report_path.is_file():
        print("ERROR: bundle install should produce a bundle report")
        return 1
    installed_bundles_output = require_success(
        "list installed bundles",
        [
            "scripts/list_installed_bundles.py",
            "--target-root",
            repo_relative_path(bundle_install_root),
        ],
    )
    if "release-engineering-starter" not in installed_bundles_output:
        print("ERROR: installed bundle listing should include release-engineering-starter")
        return 1
    require_success(
        "doctor installed bundle state",
        [
            "scripts/check_installed_market_state.py",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--strict",
        ],
    )
    update_bundle_dry_run = require_success(
        "dry-run update release-engineering bundle",
        [
            "scripts/update_skill_bundle.py",
            "release-engineering-starter",
            "--market-dir",
            repo_relative_path(market_root),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--dry-run",
        ],
    )
    if "planned=3" not in update_bundle_dry_run or "failed=0" not in update_bundle_dry_run:
        print("ERROR: bundle update dry run should plan to refresh all three bundle members without failures")
        return 1
    require_success(
        "update release-engineering bundle",
        [
            "scripts/update_skill_bundle.py",
            "release-engineering-starter",
            "--market-dir",
            repo_relative_path(market_root),
            "--target-root",
            repo_relative_path(bundle_install_root),
        ],
    )
    bundle_report = load_json(bundle_report_path)
    bundle_installed_ids = {
        entry.get("skill_id")
        for entry in bundle_report.get("results", [])
        if entry.get("status") == "installed"
    }
    if bundle_installed_ids != {
        "moyuan.release-note-writer",
        "moyuan.issue-triage-report",
        "moyuan.api-change-risk-review",
    }:
        print("ERROR: release-engineering-starter should install all three expected skills")
        return 1
    bundle_lock_payload = load_json(bundle_install_root / "skills.lock.json")
    bundle_lock_ids = {entry.get("skill_id") for entry in bundle_lock_payload.get("installed", [])}
    if bundle_lock_ids != bundle_installed_ids:
        print("ERROR: bundle install should update skills.lock.json for every installed skill")
        return 1
    release_bundle_entry = next(
        (entry for entry in bundle_lock_payload.get("installed", []) if entry.get("skill_id") == "moyuan.release-note-writer"),
        None,
    )
    release_sources = release_bundle_entry.get("sources", []) if isinstance(release_bundle_entry, dict) else []
    release_source_pairs = {
        (item.get("kind"), item.get("id"))
        for item in release_sources
        if isinstance(item, dict)
    }
    if release_source_pairs != {("direct", "direct-install"), ("bundle", "release-engineering-starter")}:
        print("ERROR: release-note-writer should retain both direct and bundle ownership sources")
        return 1
    snapshot_json_path = output_root / "snapshots" / "bundle-installed.json"
    snapshot_markdown_path = output_root / "snapshots" / "bundle-installed.md"
    require_success(
        "snapshot installed bundle state",
        [
            "scripts/skills_market.py",
            "snapshot-installed",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--output-path",
            repo_relative_path(snapshot_json_path),
            "--markdown-path",
            repo_relative_path(snapshot_markdown_path),
        ],
    )
    if not snapshot_json_path.is_file() or not snapshot_markdown_path.is_file():
        print("ERROR: snapshot-installed should write both JSON and Markdown outputs")
        return 1
    snapshot_payload = load_json(snapshot_json_path)
    if snapshot_payload.get("summary", {}).get("installed_count") != 3:
        print("ERROR: snapshot-installed should capture the full installed skill count for the bundle target")
        return 1
    if snapshot_payload.get("summary", {}).get("bundle_count") != 1:
        print("ERROR: snapshot-installed should capture the installed bundle count")
        return 1
    if snapshot_payload.get("counts", {}).get("source_kinds", {}).get("bundle") != 3:
        print("ERROR: snapshot-installed should summarize bundle ownership counts")
        return 1
    if "Installed Market Snapshot" not in snapshot_markdown_path.read_text(encoding="utf-8"):
        print("ERROR: snapshot-installed Markdown output should contain the snapshot heading")
        return 1
    verify_same_dir = output_root / "verify-same"
    require_success(
        "verify installed state against baseline snapshot",
        [
            "scripts/skills_market.py",
            "verify-installed",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--output-dir",
            repo_relative_path(verify_same_dir),
            "--strict",
        ],
    )
    expected_verify_outputs = [
        verify_same_dir / "current-snapshot.json",
        verify_same_dir / "current-snapshot.md",
        verify_same_dir / "diff.json",
        verify_same_dir / "diff.md",
    ]
    if not all(path.is_file() for path in expected_verify_outputs):
        print("ERROR: verify-installed should write current snapshot and diff artifacts")
        return 1
    promotion_history_json = output_root / "snapshots" / "bundle-installed-history.json"
    promotion_history_markdown = output_root / "snapshots" / "bundle-installed-history.md"
    promotion_archive_dir = output_root / "snapshots" / "bundle-installed-archive"
    require_success(
        "promote initial installed baseline",
        [
            "scripts/skills_market.py",
            "promote-installed-baseline",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--markdown-path",
            repo_relative_path(snapshot_markdown_path),
            "--history-path",
            repo_relative_path(promotion_history_json),
            "--history-markdown-path",
            repo_relative_path(promotion_history_markdown),
            "--archive-dir",
            repo_relative_path(promotion_archive_dir),
        ],
    )
    initial_history_payload = load_json(promotion_history_json)
    if len(initial_history_payload.get("entries", [])) != 1:
        print("ERROR: initial baseline promotion should create the first history entry")
        return 1
    initial_history_entry = initial_history_payload["entries"][0]
    if initial_history_entry.get("summary", {}).get("installed_count") != 3:
        print("ERROR: initial baseline promotion history should capture the full bundle-installed count")
        return 1
    archived_initial_baseline = Path(str(initial_history_entry.get("archived_baseline_path", "")))
    if not archived_initial_baseline.is_file():
        print("ERROR: initial baseline promotion should archive the promoted baseline snapshot")
        return 1
    initial_history_output = require_success(
        "list initial installed baseline history",
        [
            "scripts/skills_market.py",
            "list-installed-baseline-history",
            repo_relative_path(promotion_history_json),
        ],
    )
    if "Entries: 1" not in initial_history_output:
        print("ERROR: initial baseline history listing should report one promotion entry")
        return 1
    bundle_dry_run = require_success(
        "dry-run install skill-authoring bundle",
        [
            "scripts/install_skill_bundle.py",
            "skill-authoring-starter",
            "--market-dir",
            repo_relative_path(market_root),
            "--target-root",
            repo_relative_path(output_root / "bundle-dry-run"),
            "--dry-run",
        ],
    )
    if "moyuan.harness-engineering" not in bundle_dry_run or "skipped=1" not in bundle_dry_run:
        print("ERROR: skill-authoring bundle dry run should surface the archived-skill skip")
        return 1
    remove_bundle_dry_run = require_success(
        "dry-run remove release-engineering bundle",
        [
            "scripts/remove_skill_bundle.py",
            "release-engineering-starter",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--dry-run",
        ],
    )
    if "Would remove skills: moyuan.issue-triage-report, moyuan.api-change-risk-review" not in remove_bundle_dry_run:
        print("ERROR: bundle dry-run removal should plan to remove issue-triage-report and api-change-risk-review")
        return 1
    if "Would retain skills: moyuan.release-note-writer" not in remove_bundle_dry_run:
        print("ERROR: bundle dry-run removal should retain release-note-writer because of direct ownership")
        return 1
    require_success(
        "remove release-engineering bundle",
        [
            "scripts/remove_skill_bundle.py",
            "release-engineering-starter",
            "--target-root",
            repo_relative_path(bundle_install_root),
        ],
    )
    if bundle_report_path.exists():
        print("ERROR: remove-bundle should delete the bundle report")
        return 1
    bundle_lock_after_remove = load_json(bundle_install_root / "skills.lock.json")
    bundle_lock_after_remove_ids = {entry.get("skill_id") for entry in bundle_lock_after_remove.get("installed", [])}
    if bundle_lock_after_remove_ids != {"moyuan.release-note-writer"}:
        print("ERROR: remove-bundle should retain only the directly owned release-note-writer")
        return 1
    release_after_remove = next(
        (entry for entry in bundle_lock_after_remove.get("installed", []) if entry.get("skill_id") == "moyuan.release-note-writer"),
        None,
    )
    release_after_sources = release_after_remove.get("sources", []) if isinstance(release_after_remove, dict) else []
    release_after_pairs = {
        (item.get("kind"), item.get("id"))
        for item in release_after_sources
        if isinstance(item, dict)
    }
    if release_after_pairs != {("direct", "direct-install")}:
        print("ERROR: remove-bundle should leave release-note-writer with only its direct source")
        return 1
    if not (bundle_install_root / "release-note-writer" / "SKILL.md").is_file():
        print("ERROR: remove-bundle should keep the directly owned release-note-writer files")
        return 1
    if (bundle_install_root / "issue-triage-report").exists() or (bundle_install_root / "api-change-risk-review").exists():
        print("ERROR: remove-bundle should delete bundle-only skills")
        return 1
    snapshot_after_remove_json = output_root / "snapshots" / "bundle-after-remove.json"
    snapshot_after_remove_markdown = output_root / "snapshots" / "bundle-after-remove.md"
    require_success(
        "snapshot post-remove bundle state",
        [
            "scripts/skills_market.py",
            "snapshot-installed",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--output-path",
            repo_relative_path(snapshot_after_remove_json),
            "--markdown-path",
            repo_relative_path(snapshot_after_remove_markdown),
        ],
    )
    snapshot_diff_json = output_root / "snapshots" / "bundle-installed-diff.json"
    snapshot_diff_markdown = output_root / "snapshots" / "bundle-installed-diff.md"
    require_success(
        "diff installed snapshots",
        [
            "scripts/skills_market.py",
            "diff-installed",
            repo_relative_path(snapshot_json_path),
            repo_relative_path(snapshot_after_remove_json),
            "--output-path",
            repo_relative_path(snapshot_diff_json),
            "--markdown-path",
            repo_relative_path(snapshot_diff_markdown),
        ],
    )
    if not snapshot_diff_json.is_file() or not snapshot_diff_markdown.is_file():
        print("ERROR: diff-installed should write both JSON and Markdown diff outputs")
        return 1
    snapshot_diff_payload = load_json(snapshot_diff_json)
    removed_skill_ids = {
        entry.get("skill_id")
        for entry in snapshot_diff_payload.get("skills", {}).get("removed", [])
        if isinstance(entry, dict)
    }
    if removed_skill_ids != {"moyuan.issue-triage-report", "moyuan.api-change-risk-review"}:
        print("ERROR: snapshot diff should report the two bundle-only skills as removed")
        return 1
    changed_skill_ids = {
        entry.get("skill_id")
        for entry in snapshot_diff_payload.get("skills", {}).get("changed", [])
        if isinstance(entry, dict)
    }
    if "moyuan.release-note-writer" not in changed_skill_ids:
        print("ERROR: snapshot diff should report release-note-writer source changes after bundle removal")
        return 1
    removed_bundle_ids = {
        entry.get("bundle_id")
        for entry in snapshot_diff_payload.get("bundles", {}).get("removed", [])
        if isinstance(entry, dict)
    }
    if removed_bundle_ids != {"release-engineering-starter"}:
        print("ERROR: snapshot diff should report the removed release-engineering bundle")
        return 1
    if "Installed Market Snapshot Diff" not in snapshot_diff_markdown.read_text(encoding="utf-8"):
        print("ERROR: snapshot diff Markdown output should contain the diff heading")
        return 1
    verify_drift = run_python(
        [
            "scripts/skills_market.py",
            "verify-installed",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--json",
            "--strict",
        ]
    )
    if verify_drift.returncode == 0:
        print("ERROR: verify-installed should fail in strict mode when the live state drifts from baseline")
        if verify_drift.stdout.strip():
            print(verify_drift.stdout.strip())
        if verify_drift.stderr.strip():
            print(verify_drift.stderr.strip())
        return 1
    verify_drift_payload = json.loads(verify_drift.stdout)
    if verify_drift_payload.get("matches") is not False:
        print("ERROR: verify-installed drift payload should report matches=false")
        return 1
    verify_removed_skill_ids = {
        entry.get("skill_id")
        for entry in verify_drift_payload.get("diff", {}).get("skills", {}).get("removed", [])
        if isinstance(entry, dict)
    }
    if verify_removed_skill_ids != {"moyuan.issue-triage-report", "moyuan.api-change-risk-review"}:
        print("ERROR: verify-installed should surface the removed bundle-only skills")
        return 1
    promotion_diff_json = output_root / "snapshots" / "bundle-baseline-transition.json"
    promotion_diff_markdown = output_root / "snapshots" / "bundle-baseline-transition.md"
    require_success(
        "promote installed baseline",
        [
            "scripts/skills_market.py",
            "promote-installed-baseline",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--markdown-path",
            repo_relative_path(snapshot_markdown_path),
            "--diff-output-path",
            repo_relative_path(promotion_diff_json),
            "--diff-markdown-path",
            repo_relative_path(promotion_diff_markdown),
            "--history-path",
            repo_relative_path(promotion_history_json),
            "--history-markdown-path",
            repo_relative_path(promotion_history_markdown),
            "--archive-dir",
            repo_relative_path(promotion_archive_dir),
        ],
    )
    if not promotion_history_json.is_file() or not promotion_history_markdown.is_file():
        print("ERROR: promote-installed-baseline should write baseline history artifacts")
        return 1
    if not promotion_diff_json.is_file() or not promotion_diff_markdown.is_file():
        print("ERROR: promote-installed-baseline should write transition diff artifacts when replacing a baseline")
        return 1
    promoted_baseline = load_json(snapshot_json_path)
    if promoted_baseline.get("summary", {}).get("installed_count") != 1:
        print("ERROR: promoted baseline should capture the current post-remove installed skill count")
        return 1
    if promoted_baseline.get("summary", {}).get("bundle_count") != 0:
        print("ERROR: promoted baseline should capture that no bundles remain after bundle removal")
        return 1
    promotion_diff_payload = load_json(promotion_diff_json)
    promotion_removed_skill_ids = {
        entry.get("skill_id")
        for entry in promotion_diff_payload.get("skills", {}).get("removed", [])
        if isinstance(entry, dict)
    }
    if promotion_removed_skill_ids != {"moyuan.issue-triage-report", "moyuan.api-change-risk-review"}:
        print("ERROR: promoted baseline transition diff should preserve the removed bundle-only skills")
        return 1
    history_payload = load_json(promotion_history_json)
    if len(history_payload.get("entries", [])) != 2:
        print("ERROR: baseline history should record both the original and refreshed promoted baselines")
        return 1
    latest_history_entry = history_payload["entries"][-1]
    if latest_history_entry.get("summary", {}).get("installed_count") != 1:
        print("ERROR: baseline history entry should capture the promoted installed skill count")
        return 1
    archived_latest_baseline = Path(str(latest_history_entry.get("archived_baseline_path", "")))
    if not archived_latest_baseline.is_file():
        print("ERROR: refreshed baseline promotion should archive the new baseline snapshot")
        return 1
    history_output = require_success(
        "list installed baseline history",
        [
            "scripts/skills_market.py",
            "list-installed-baseline-history",
            repo_relative_path(promotion_history_json),
        ],
    )
    if "Entries: 2" not in history_output:
        print("ERROR: list-installed-baseline-history should report both recorded promotion entries")
        return 1
    verify_history_entry_one = run_python(
        [
            "scripts/skills_market.py",
            "verify-installed-history",
            repo_relative_path(promotion_history_json),
            "1",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--json",
            "--strict",
        ]
    )
    if verify_history_entry_one.returncode == 0:
        print("ERROR: verify-installed-history should fail in strict mode when an older archived baseline drifts from live state")
        if verify_history_entry_one.stdout.strip():
            print(verify_history_entry_one.stdout.strip())
        if verify_history_entry_one.stderr.strip():
            print(verify_history_entry_one.stderr.strip())
        return 1
    verify_history_entry_one_payload = json.loads(verify_history_entry_one.stdout)
    if verify_history_entry_one_payload.get("history_entry") != 1 or verify_history_entry_one_payload.get("matches") is not False:
        print("ERROR: verify-installed-history should report the requested historical entry and drift state")
        return 1
    verify_history_latest_dir = output_root / "verify-history-latest"
    require_success(
        "verify latest archived installed baseline history",
        [
            "scripts/skills_market.py",
            "verify-installed-history",
            repo_relative_path(promotion_history_json),
            "latest",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--output-dir",
            repo_relative_path(verify_history_latest_dir),
            "--strict",
        ],
    )
    expected_verify_history_outputs = [
        verify_history_latest_dir / "current-snapshot.json",
        verify_history_latest_dir / "current-snapshot.md",
        verify_history_latest_dir / "diff.json",
        verify_history_latest_dir / "diff.md",
    ]
    if not all(path.is_file() for path in expected_verify_history_outputs):
        print("ERROR: verify-installed-history should write current snapshot and diff artifacts")
        return 1
    history_diff_json = output_root / "snapshots" / "history-entry-diff.json"
    history_diff_markdown = output_root / "snapshots" / "history-entry-diff.md"
    require_success(
        "diff archived installed baseline history entries",
        [
            "scripts/skills_market.py",
            "diff-installed-history",
            repo_relative_path(promotion_history_json),
            "1",
            "2",
            "--output-path",
            repo_relative_path(history_diff_json),
            "--markdown-path",
            repo_relative_path(history_diff_markdown),
        ],
    )
    if not history_diff_json.is_file() or not history_diff_markdown.is_file():
        print("ERROR: diff-installed-history should write both JSON and Markdown diff outputs")
        return 1
    history_diff_payload = load_json(history_diff_json)
    if history_diff_payload.get("before_entry") != 1 or history_diff_payload.get("after_entry") != 2:
        print("ERROR: diff-installed-history should record the resolved history entry numbers")
        return 1
    history_removed_skill_ids = {
        entry.get("skill_id")
        for entry in history_diff_payload.get("skills", {}).get("removed", [])
        if isinstance(entry, dict)
    }
    if history_removed_skill_ids != {"moyuan.issue-triage-report", "moyuan.api-change-risk-review"}:
        print("ERROR: diff-installed-history should report the two bundle-only skills as removed between entry 1 and entry 2")
        return 1
    if "Installed Market Snapshot Diff" not in history_diff_markdown.read_text(encoding="utf-8"):
        print("ERROR: diff-installed-history Markdown output should contain the diff heading")
        return 1
    history_report_json = output_root / "snapshots" / "history-report.json"
    history_report_markdown = output_root / "snapshots" / "history-report.md"
    require_success(
        "report installed baseline history",
        [
            "scripts/skills_market.py",
            "report-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--output-path",
            repo_relative_path(history_report_json),
            "--markdown-path",
            repo_relative_path(history_report_markdown),
        ],
    )
    if not history_report_json.is_file() or not history_report_markdown.is_file():
        print("ERROR: report-installed-baseline-history should write both JSON and Markdown outputs")
        return 1
    history_report_payload = load_json(history_report_json)
    if history_report_payload.get("entries_count") != 2:
        print("ERROR: history report should summarize both retained entries before prune")
        return 1
    report_sequences = [item.get("sequence") for item in history_report_payload.get("timeline", []) if isinstance(item, dict)]
    if report_sequences != [1, 2]:
        print("ERROR: history report timeline should preserve the retained sequence order")
        return 1
    report_transitions = history_report_payload.get("transitions", [])
    if len(report_transitions) != 1 or report_transitions[0].get("before_entry") != 1 or report_transitions[0].get("after_entry") != 2:
        print("ERROR: history report should summarize the single transition between entry 1 and entry 2")
        return 1
    report_removed_skill_ids = set(report_transitions[0].get("removed_skill_ids", []))
    if report_removed_skill_ids != {"moyuan.issue-triage-report", "moyuan.api-change-risk-review"}:
        print("ERROR: history report should surface the removed bundle-only skills in its transition summary")
        return 1
    if "Installed Baseline History Report" not in history_report_markdown.read_text(encoding="utf-8"):
        print("ERROR: history report Markdown output should contain the report heading")
        return 1
    history_policy_output = require_success(
        "list installed baseline history policies",
        [
            "scripts/skills_market.py",
            "list-installed-history-policies",
        ],
    )
    if "latest-release-gate" not in history_policy_output or "history-audit" not in history_policy_output:
        print("ERROR: list-installed-history-policies should expose both reusable history alert profiles")
        return 1
    history_waiver_output = require_success(
        "list installed baseline history waivers",
        [
            "scripts/skills_market.py",
            "list-installed-history-waivers",
        ],
    )
    if "approved-release-engineering-downsize" not in history_waiver_output:
        print("ERROR: list-installed-history-waivers should expose the approved release-engineering waiver")
        return 1
    history_waiver_audit_json = output_root / "snapshots" / "history-waiver-audit.json"
    history_waiver_audit_markdown = output_root / "snapshots" / "history-waiver-audit.md"
    require_success(
        "audit installed baseline history waivers",
        [
            "scripts/skills_market.py",
            "audit-installed-history-waivers",
            repo_relative_path(promotion_history_json),
            "--output-path",
            repo_relative_path(history_waiver_audit_json),
            "--markdown-path",
            repo_relative_path(history_waiver_audit_markdown),
            "--json",
            "--strict",
        ],
    )
    history_waiver_audit_payload = load_json(history_waiver_audit_json)
    if history_waiver_audit_payload.get("passes") is not True or history_waiver_audit_payload.get("finding_count") != 0:
        print("ERROR: waiver audit should pass when all configured waivers are active and still match current alerts")
        return 1
    if history_waiver_audit_payload.get("waiver_count") != 1:
        print("ERROR: waiver audit should include the single reusable waiver before smoke adds temporary fixtures")
        return 1
    if "Installed Baseline History Waiver Audit" not in history_waiver_audit_markdown.read_text(encoding="utf-8"):
        print("ERROR: waiver audit Markdown output should contain the audit heading")
        return 1
    history_waiver_remediation_json = output_root / "snapshots" / "history-waiver-remediation.json"
    history_waiver_remediation_markdown = output_root / "snapshots" / "history-waiver-remediation.md"
    require_success(
        "remediate installed baseline history waivers",
        [
            "scripts/skills_market.py",
            "remediate-installed-history-waivers",
            repo_relative_path(promotion_history_json),
            "--output-path",
            repo_relative_path(history_waiver_remediation_json),
            "--markdown-path",
            repo_relative_path(history_waiver_remediation_markdown),
            "--json",
            "--strict",
        ],
    )
    history_waiver_remediation_payload = load_json(history_waiver_remediation_json)
    if history_waiver_remediation_payload.get("passes") is not True or history_waiver_remediation_payload.get("remediation_count") != 0:
        print("ERROR: waiver remediation should report zero actions when waiver audit is already healthy")
        return 1
    if "Installed Baseline History Waiver Remediation" not in history_waiver_remediation_markdown.read_text(encoding="utf-8"):
        print("ERROR: waiver remediation Markdown output should contain the remediation heading")
        return 1
    history_waiver_execution_dir = output_root / "waiver-execution-healthy"
    history_waiver_execution_output = require_success(
        "draft installed baseline history waiver execution",
        [
            "scripts/skills_market.py",
            "draft-installed-history-waiver-execution",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(history_waiver_execution_dir),
            "--json",
            "--strict",
        ],
    )
    history_waiver_execution_payload = json.loads(history_waiver_execution_output)
    if history_waiver_execution_payload.get("passes") is not True or history_waiver_execution_payload.get("execution_count") != 0:
        print("ERROR: healthy waiver execution drafting should report zero follow-up actions")
        return 1
    if history_waiver_execution_payload.get("draft_count") != 0 or history_waiver_execution_payload.get("review_count") != 0:
        print("ERROR: healthy waiver execution drafting should not create draft or review actions")
        return 1
    healthy_execution_summary_json = history_waiver_execution_dir / "execution-summary.json"
    healthy_execution_summary_markdown = history_waiver_execution_dir / "execution-summary.md"
    if not healthy_execution_summary_json.is_file() or not healthy_execution_summary_markdown.is_file():
        print("ERROR: healthy waiver execution drafting should write summary artifacts when an output dir is requested")
        return 1
    if "Installed Baseline History Waiver Execution Drafts" not in healthy_execution_summary_markdown.read_text(encoding="utf-8"):
        print("ERROR: healthy waiver execution Markdown output should contain the execution heading")
        return 1
    history_waiver_preview_dir = output_root / "waiver-preview-healthy"
    history_waiver_preview_output = require_success(
        "preview installed baseline history waiver execution",
        [
            "scripts/skills_market.py",
            "preview-installed-history-waiver-execution",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(history_waiver_preview_dir),
            "--json",
            "--strict",
        ],
    )
    history_waiver_preview_payload = json.loads(history_waiver_preview_output)
    if history_waiver_preview_payload.get("passes") is not True or history_waiver_preview_payload.get("preview_count") != 0:
        print("ERROR: healthy waiver preview should report zero review actions")
        return 1
    healthy_preview_summary_json = history_waiver_preview_dir / "preview-summary.json"
    healthy_preview_summary_markdown = history_waiver_preview_dir / "preview-summary.md"
    if not healthy_preview_summary_json.is_file() or not healthy_preview_summary_markdown.is_file():
        print("ERROR: healthy waiver preview should write summary artifacts when an output dir is requested")
        return 1
    if "Installed Baseline History Waiver Preview" not in healthy_preview_summary_markdown.read_text(encoding="utf-8"):
        print("ERROR: healthy waiver preview Markdown output should contain the preview heading")
        return 1
    history_waiver_apply_dir = output_root / "waiver-apply-healthy"
    history_waiver_apply_output = require_success(
        "prepare installed baseline history waiver apply pack",
        [
            "scripts/skills_market.py",
            "prepare-installed-history-waiver-apply",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(history_waiver_apply_dir),
            "--json",
            "--strict",
        ],
    )
    history_waiver_apply_payload = json.loads(history_waiver_apply_output)
    if history_waiver_apply_payload.get("passes") is not True or history_waiver_apply_payload.get("action_count") != 0:
        print("ERROR: healthy waiver apply pack should report zero apply actions")
        return 1
    healthy_apply_summary_json = history_waiver_apply_dir / "apply-summary.json"
    healthy_apply_summary_markdown = history_waiver_apply_dir / "apply-summary.md"
    if not healthy_apply_summary_json.is_file() or not healthy_apply_summary_markdown.is_file():
        print("ERROR: healthy waiver apply pack should write summary artifacts when an output dir is requested")
        return 1
    if "Installed Baseline History Waiver Apply Pack" not in healthy_apply_summary_markdown.read_text(encoding="utf-8"):
        print("ERROR: healthy waiver apply Markdown output should contain the apply heading")
        return 1
    history_waiver_execute_dir = output_root / "waiver-execute-healthy"
    history_waiver_execute_output = require_success(
        "execute installed baseline history waiver apply pack",
        [
            "scripts/skills_market.py",
            "execute-installed-history-waiver-apply",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(history_waiver_execute_dir),
            "--json",
            "--strict",
        ],
    )
    history_waiver_execute_payload = json.loads(history_waiver_execute_output)
    if history_waiver_execute_payload.get("passes") is not True or history_waiver_execute_payload.get("action_count") != 0:
        print("ERROR: healthy waiver execute should report zero execution actions")
        return 1
    healthy_execute_summary_json = history_waiver_execute_dir / "execute-summary.json"
    healthy_execute_summary_markdown = history_waiver_execute_dir / "execute-summary.md"
    if not healthy_execute_summary_json.is_file() or not healthy_execute_summary_markdown.is_file():
        print("ERROR: healthy waiver execute should write summary artifacts when an output dir is requested")
        return 1
    if "Installed Baseline History Waiver Apply Execution" not in healthy_execute_summary_markdown.read_text(encoding="utf-8"):
        print("ERROR: healthy waiver execute Markdown output should contain the execution heading")
        return 1
    waiver_temp_dir = output_root / "waivers"
    waiver_temp_dir.mkdir(parents=True, exist_ok=True)
    expired_history_waiver_path = waiver_temp_dir / "expired-release-downsize.json"
    expired_history_waiver_path.write_text(
        json.dumps(
            {
                "waiver_version": 1,
                "id": "expired-release-downsize",
                "title": "Expired Release Downsize",
                "description": "An old approval record kept only to verify that waiver audit can flag expired exceptions.",
                "policy_id": "latest-release-gate",
                "match": {
                    "before_entry": 1,
                    "after_entry": 2,
                    "after_target_root_suffix": "bundle-installed",
                    "metrics": [
                        "removed_skills"
                    ],
                    "removed_skill_ids": [
                        "moyuan.issue-triage-report"
                    ]
                },
                "approval": {
                    "approved_by": "Moyuan Release Review",
                    "approved_at": "2026-03-20",
                    "reason": "This expired fixture exists only so the smoke test can confirm that waiver audit catches old approvals."
                },
                "expires_on": "2026-03-21"
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    stale_history_waiver_path = waiver_temp_dir / "stale-added-skills.json"
    stale_history_waiver_path.write_text(
        json.dumps(
            {
                "waiver_version": 1,
                "id": "stale-added-skills",
                "title": "Stale Added Skills Waiver",
                "description": "A stale approval record that still points at the retained transition but no longer matches any active alert metric.",
                "policy_id": "latest-release-gate",
                "match": {
                    "before_entry": 1,
                    "after_entry": 2,
                    "after_target_root_suffix": "bundle-installed",
                    "metrics": [
                        "added_skills"
                    ]
                },
                "approval": {
                    "approved_by": "Moyuan Release Review",
                    "approved_at": "2026-03-26",
                    "reason": "This fixture exists only so the smoke test can confirm that waiver audit catches stale approvals."
                },
                "expires_on": "2026-12-31"
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    history_waiver_audit_findings_json = output_root / "snapshots" / "history-waiver-audit-findings.json"
    history_waiver_audit_findings_result = run_python(
        [
            "scripts/skills_market.py",
            "audit-installed-history-waivers",
            repo_relative_path(promotion_history_json),
            "--waiver",
            "approved-release-engineering-downsize",
            "--waiver",
            repo_relative_path(expired_history_waiver_path),
            "--waiver",
            repo_relative_path(stale_history_waiver_path),
            "--output-path",
            repo_relative_path(history_waiver_audit_findings_json),
            "--json",
            "--strict",
        ]
    )
    if history_waiver_audit_findings_result.returncode == 0:
        print("ERROR: waiver audit should fail in strict mode when expired or stale waiver records are supplied")
        if history_waiver_audit_findings_result.stdout.strip():
            print(history_waiver_audit_findings_result.stdout.strip())
        if history_waiver_audit_findings_result.stderr.strip():
            print(history_waiver_audit_findings_result.stderr.strip())
        return 1
    history_waiver_audit_findings_payload = load_json(history_waiver_audit_findings_json)
    if history_waiver_audit_findings_payload.get("expired_count") != 1 or history_waiver_audit_findings_payload.get("stale_count") != 1:
        print("ERROR: waiver audit should separately classify expired and stale waiver findings")
        return 1
    if history_waiver_audit_findings_payload.get("unmatched_count") != 0:
        print("ERROR: pre-prune waiver audit should not report unmatched waivers for the temporary fixtures")
        return 1
    waiver_findings_by_id = {
        item.get("id"): {finding.get("code") for finding in item.get("findings", []) if isinstance(finding, dict)}
        for item in history_waiver_audit_findings_payload.get("waivers", [])
        if isinstance(item, dict)
    }
    if waiver_findings_by_id.get("expired-release-downsize") != {"expired"}:
        print("ERROR: expired waiver fixture should report only the expired finding code")
        return 1
    if waiver_findings_by_id.get("stale-added-skills") != {"stale"}:
        print("ERROR: stale waiver fixture should report only the stale finding code")
        return 1
    history_waiver_remediation_findings_json = output_root / "snapshots" / "history-waiver-remediation-findings.json"
    history_waiver_remediation_findings_result = run_python(
        [
            "scripts/skills_market.py",
            "remediate-installed-history-waivers",
            repo_relative_path(promotion_history_json),
            "--waiver",
            "approved-release-engineering-downsize",
            "--waiver",
            repo_relative_path(expired_history_waiver_path),
            "--waiver",
            repo_relative_path(stale_history_waiver_path),
            "--output-path",
            repo_relative_path(history_waiver_remediation_findings_json),
            "--json",
            "--strict",
        ]
    )
    if history_waiver_remediation_findings_result.returncode == 0:
        print("ERROR: waiver remediation should fail in strict mode when action is required")
        if history_waiver_remediation_findings_result.stdout.strip():
            print(history_waiver_remediation_findings_result.stdout.strip())
        if history_waiver_remediation_findings_result.stderr.strip():
            print(history_waiver_remediation_findings_result.stderr.strip())
        return 1
    history_waiver_remediation_findings_payload = load_json(history_waiver_remediation_findings_json)
    if history_waiver_remediation_findings_payload.get("remediation_count") != 2:
        print("ERROR: waiver remediation should emit one remediation action for each failing temporary waiver")
        return 1
    remediation_actions_by_id = {
        item.get("id"): {
            action.get("code")
            for action in item.get("actions", [])
            if isinstance(action, dict)
        }
        for item in history_waiver_remediation_findings_payload.get("waivers", [])
        if isinstance(item, dict)
    }
    if remediation_actions_by_id.get("expired-release-downsize") != {"renew_or_remove"}:
        print("ERROR: expired waiver remediation should suggest renewing or removing the waiver")
        return 1
    if remediation_actions_by_id.get("stale-added-skills") != {"retire_or_replace"}:
        print("ERROR: stale waiver remediation should suggest retiring or replacing the waiver")
        return 1
    history_waiver_execution_findings_dir = output_root / "waiver-execution-findings"
    history_waiver_execution_findings_result = run_python(
        [
            "scripts/skills_market.py",
            "draft-installed-history-waiver-execution",
            repo_relative_path(promotion_history_json),
            "--waiver",
            "approved-release-engineering-downsize",
            "--waiver",
            repo_relative_path(expired_history_waiver_path),
            "--waiver",
            repo_relative_path(stale_history_waiver_path),
            "--output-dir",
            repo_relative_path(history_waiver_execution_findings_dir),
            "--json",
            "--strict",
        ]
    )
    if history_waiver_execution_findings_result.returncode == 0:
        print("ERROR: waiver execution drafting should fail in strict mode when follow-up actions are required")
        if history_waiver_execution_findings_result.stdout.strip():
            print(history_waiver_execution_findings_result.stdout.strip())
        if history_waiver_execution_findings_result.stderr.strip():
            print(history_waiver_execution_findings_result.stderr.strip())
        return 1
    history_waiver_execution_findings_payload = json.loads(history_waiver_execution_findings_result.stdout)
    if history_waiver_execution_findings_payload.get("execution_count") != 2:
        print("ERROR: waiver execution drafting should emit one execution action for each failing temporary waiver")
        return 1
    if history_waiver_execution_findings_payload.get("draft_count") != 2 or history_waiver_execution_findings_payload.get("review_count") != 0:
        print("ERROR: expired and stale fixture waivers should both receive draft updates before prune")
        return 1
    expired_execution_draft = history_waiver_execution_findings_dir / "waivers" / "expired-release-downsize" / "renewal-draft.json"
    stale_execution_draft = history_waiver_execution_findings_dir / "waivers" / "stale-added-skills" / "replacement-draft.json"
    if not expired_execution_draft.is_file() or not stale_execution_draft.is_file():
        print("ERROR: waiver execution drafting should write renewal and replacement drafts for the temporary failing waivers")
        return 1
    expired_execution_payload = load_json(expired_execution_draft)
    if expired_execution_payload.get("_draft", {}).get("strategy") != "renew":
        print("ERROR: expired waiver execution draft should be marked as a renewal strategy")
        return 1
    if expired_execution_payload.get("expires_on", "") <= "2026-03-21":
        print("ERROR: expired waiver execution draft should extend the expiry window beyond the stale fixture date")
        return 1
    stale_execution_payload = load_json(stale_execution_draft)
    stale_metrics = set(stale_execution_payload.get("match", {}).get("metrics", []))
    if "added_skills" in stale_metrics or "removed_skills" not in stale_metrics:
        print("ERROR: stale waiver execution draft should pivot to the currently active removed-skills alert scope")
        return 1
    history_waiver_preview_findings_dir = output_root / "waiver-preview-findings"
    history_waiver_preview_findings_result = run_python(
        [
            "scripts/skills_market.py",
            "preview-installed-history-waiver-execution",
            repo_relative_path(promotion_history_json),
            "--waiver",
            "approved-release-engineering-downsize",
            "--waiver",
            repo_relative_path(expired_history_waiver_path),
            "--waiver",
            repo_relative_path(stale_history_waiver_path),
            "--output-dir",
            repo_relative_path(history_waiver_preview_findings_dir),
            "--json",
            "--strict",
        ]
    )
    if history_waiver_preview_findings_result.returncode == 0:
        print("ERROR: waiver preview should fail in strict mode when review previews are present")
        if history_waiver_preview_findings_result.stdout.strip():
            print(history_waiver_preview_findings_result.stdout.strip())
        if history_waiver_preview_findings_result.stderr.strip():
            print(history_waiver_preview_findings_result.stderr.strip())
        return 1
    history_waiver_preview_findings_payload = json.loads(history_waiver_preview_findings_result.stdout)
    if history_waiver_preview_findings_payload.get("preview_count") != 2:
        print("ERROR: waiver preview should emit one preview action for each failing temporary waiver")
        return 1
    if history_waiver_preview_findings_payload.get("draft_preview_count") != 2 or history_waiver_preview_findings_payload.get("review_preview_count") != 0:
        print("ERROR: pre-prune waiver preview should show two draft previews and no cleanup-only previews")
        return 1
    expired_preview_payload = load_json(
        history_waiver_preview_findings_dir / "waivers" / "expired-release-downsize" / "preview.json"
    )
    stale_preview_payload = load_json(
        history_waiver_preview_findings_dir / "waivers" / "stale-added-skills" / "preview.json"
    )
    expired_changed_paths = {
        change.get("path")
        for action in expired_preview_payload.get("action_previews", [])
        if isinstance(action, dict)
        for change in action.get("changes", [])
        if isinstance(change, dict)
    }
    stale_changed_paths = {
        change.get("path")
        for action in stale_preview_payload.get("action_previews", [])
        if isinstance(action, dict)
        for change in action.get("changes", [])
        if isinstance(change, dict)
    }
    if "expires_on" not in expired_changed_paths or "approval.reason" not in expired_changed_paths:
        print("ERROR: expired waiver preview should show the renewed expiry and approval reason changes")
        return 1
    if "match.metrics" not in stale_changed_paths:
        print("ERROR: stale waiver preview should show the metric replacement in the generated draft")
        return 1
    history_waiver_apply_findings_dir = output_root / "waiver-apply-findings"
    history_waiver_apply_findings_result = run_python(
        [
            "scripts/skills_market.py",
            "prepare-installed-history-waiver-apply",
            repo_relative_path(promotion_history_json),
            "--waiver",
            "approved-release-engineering-downsize",
            "--waiver",
            repo_relative_path(expired_history_waiver_path),
            "--waiver",
            repo_relative_path(stale_history_waiver_path),
            "--output-dir",
            repo_relative_path(history_waiver_apply_findings_dir),
            "--json",
            "--strict",
        ]
    )
    if history_waiver_apply_findings_result.returncode == 0:
        print("ERROR: waiver apply pack should fail in strict mode when apply actions are present")
        if history_waiver_apply_findings_result.stdout.strip():
            print(history_waiver_apply_findings_result.stdout.strip())
        if history_waiver_apply_findings_result.stderr.strip():
            print(history_waiver_apply_findings_result.stderr.strip())
        return 1
    history_waiver_apply_findings_payload = json.loads(history_waiver_apply_findings_result.stdout)
    if history_waiver_apply_findings_payload.get("action_count") != 2 or history_waiver_apply_findings_payload.get("patch_count") != 2:
        print("ERROR: waiver apply pack should emit two patch actions for the failing temporary waivers")
        return 1
    if history_waiver_apply_findings_payload.get("update_patch_count") != 2 or history_waiver_apply_findings_payload.get("delete_patch_count") != 0:
        print("ERROR: pre-prune waiver apply pack should only generate update patches")
        return 1
    expired_apply_target = history_waiver_apply_findings_dir / "waivers" / "expired-release-downsize" / "apply-action-01.target.json"
    stale_apply_target = history_waiver_apply_findings_dir / "waivers" / "stale-added-skills" / "apply-action-01.target.json"
    expired_apply_patch = history_waiver_apply_findings_dir / "waivers" / "expired-release-downsize" / "apply-action-01.patch"
    stale_apply_patch = history_waiver_apply_findings_dir / "waivers" / "stale-added-skills" / "apply-action-01.patch"
    if not all(path.is_file() for path in [expired_apply_target, stale_apply_target, expired_apply_patch, stale_apply_patch]):
        print("ERROR: waiver apply pack should emit per-waiver target and patch artifacts for the failing temporary waivers")
        return 1
    expired_apply_payload = load_json(expired_apply_target)
    stale_apply_payload = load_json(stale_apply_target)
    if "_draft" in expired_apply_payload or "_draft" in stale_apply_payload:
        print("ERROR: apply target payloads should strip draft-only metadata before generating patches")
        return 1
    if expired_apply_payload.get("expires_on", "") <= "2026-03-21":
        print("ERROR: expired waiver apply target should keep the renewed expiry date from the execution draft")
        return 1
    stale_apply_metrics = set(stale_apply_payload.get("match", {}).get("metrics", []))
    if "added_skills" in stale_apply_metrics or "removed_skills" not in stale_apply_metrics:
        print("ERROR: stale waiver apply target should preserve the replacement metric set")
        return 1
    combined_apply_patch = history_waiver_apply_findings_dir / "apply.patch"
    if not combined_apply_patch.is_file():
        print("ERROR: waiver apply pack should emit a combined patch when patch actions exist")
        return 1
    combined_apply_patch_text = combined_apply_patch.read_text(encoding="utf-8")
    if "expires_on" not in combined_apply_patch_text or "removed_skills" not in combined_apply_patch_text:
        print("ERROR: combined apply patch should include both the renewal and replacement edits")
        return 1
    history_waiver_execute_findings_dir = output_root / "waiver-execute-findings"
    history_waiver_execute_stage_dir = history_waiver_execute_findings_dir / "staged-root"
    history_waiver_execute_findings_output = require_success(
        "execute installed baseline history waiver apply pack with staging",
        [
            "scripts/skills_market.py",
            "execute-installed-history-waiver-apply",
            repo_relative_path(promotion_history_json),
            "--waiver",
            "approved-release-engineering-downsize",
            "--waiver",
            repo_relative_path(expired_history_waiver_path),
            "--waiver",
            repo_relative_path(stale_history_waiver_path),
            "--output-dir",
            repo_relative_path(history_waiver_execute_findings_dir),
            "--stage-dir",
            repo_relative_path(history_waiver_execute_stage_dir),
            "--json",
            "--strict",
        ],
    )
    history_waiver_execute_findings_payload = json.loads(history_waiver_execute_findings_output)
    if history_waiver_execute_findings_payload.get("staged_update_count") != 2 or history_waiver_execute_findings_payload.get("written_update_count") != 0:
        print("ERROR: waiver execute staging should stage two update actions without writing source files")
        return 1
    if history_waiver_execute_findings_payload.get("blocked_action_count") != 0:
        print("ERROR: waiver execute staging should not block healthy reviewed apply packs")
        return 1
    staged_expired_path = history_waiver_execute_stage_dir / expired_history_waiver_path.relative_to(ROOT)
    staged_stale_path = history_waiver_execute_stage_dir / stale_history_waiver_path.relative_to(ROOT)
    if not staged_expired_path.is_file() or not staged_stale_path.is_file():
        print("ERROR: waiver execute staging should materialize staged update files under the staging root")
        return 1
    if load_json(staged_expired_path).get("expires_on", "") <= "2026-03-21":
        print("ERROR: staged expired waiver file should preserve the renewed expiry date")
        return 1
    staged_stale_metrics = set(load_json(staged_stale_path).get("match", {}).get("metrics", []))
    if "added_skills" in staged_stale_metrics or "removed_skills" not in staged_stale_metrics:
        print("ERROR: staged stale waiver file should preserve the replacement metric set")
        return 1
    history_alert_json = output_root / "snapshots" / "history-alerts.json"
    history_alert_markdown = output_root / "snapshots" / "history-alerts.md"
    history_alert_result = run_python(
        [
            "scripts/skills_market.py",
            "alert-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--policy",
            "latest-release-gate",
            "--output-path",
            repo_relative_path(history_alert_json),
            "--markdown-path",
            repo_relative_path(history_alert_markdown),
            "--json",
            "--strict",
        ]
    )
    if history_alert_result.returncode == 0:
        print("ERROR: alert-installed-baseline-history should fail in strict mode for oversized historical transitions")
        if history_alert_result.stdout.strip():
            print(history_alert_result.stdout.strip())
        if history_alert_result.stderr.strip():
            print(history_alert_result.stderr.strip())
        return 1
    if not history_alert_json.is_file() or not history_alert_markdown.is_file():
        print("ERROR: alert-installed-baseline-history should write both JSON and Markdown outputs")
        return 1
    history_alert_payload = json.loads(history_alert_result.stdout)
    if history_alert_payload.get("passes") is not False or history_alert_payload.get("alert_count", 0) < 1:
        print("ERROR: alert-installed-baseline-history should report alert findings for oversized transitions")
        return 1
    if history_alert_payload.get("active_alert_count", 0) < 1 or history_alert_payload.get("waived_alert_count", 0) != 0:
        print("ERROR: unwaived history alert should preserve active findings and report zero waived alerts")
        return 1
    if history_alert_payload.get("policy_id") != "latest-release-gate" or history_alert_payload.get("latest_only") is not True:
        print("ERROR: history alert policy should resolve latest-release-gate with latest_only defaults")
        return 1
    alert_transitions = history_alert_payload.get("transitions", [])
    if len(alert_transitions) != 1 or alert_transitions[0].get("before_entry") != 1 or alert_transitions[0].get("after_entry") != 2:
        print("ERROR: alert-installed-baseline-history should evaluate the retained transition between entry 1 and entry 2")
        return 1
    alert_metrics = {item.get("metric") for item in alert_transitions[0].get("alerts", []) if isinstance(item, dict)}
    if "removed_skills" not in alert_metrics or "removed_bundles" not in alert_metrics:
        print("ERROR: alert-installed-baseline-history should flag both removed skills and removed bundles when thresholds are exceeded")
        return 1
    if "Installed Baseline History Alerts" not in history_alert_markdown.read_text(encoding="utf-8"):
        print("ERROR: history alert Markdown output should contain the alert heading")
        return 1
    waived_history_alert_json = output_root / "snapshots" / "history-alerts-waived.json"
    waived_history_alert_markdown = output_root / "snapshots" / "history-alerts-waived.md"
    require_success(
        "alert installed baseline history with waiver",
        [
            "scripts/skills_market.py",
            "alert-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--policy",
            "latest-release-gate",
            "--waiver",
            "approved-release-engineering-downsize",
            "--output-path",
            repo_relative_path(waived_history_alert_json),
            "--markdown-path",
            repo_relative_path(waived_history_alert_markdown),
            "--json",
            "--strict",
        ],
    )
    waived_history_alert_payload = load_json(waived_history_alert_json)
    if waived_history_alert_payload.get("passes") is not True:
        print("ERROR: history alert should pass when all findings are covered by an approved waiver")
        return 1
    if waived_history_alert_payload.get("active_alert_count") != 0 or waived_history_alert_payload.get("waived_alert_count", 0) < 1:
        print("ERROR: waived history alert should move findings out of the active gate result")
        return 1
    if waived_history_alert_payload.get("matched_waiver_count") != 1:
        print("ERROR: waived history alert should report the matched waiver count")
        return 1
    waived_alerts = waived_history_alert_payload.get("transitions", [])[0].get("alerts", [])
    waived_ids = {
        alert.get("waiver_id")
        for alert in waived_alerts
        if isinstance(alert, dict) and alert.get("waived") is True
    }
    if waived_ids != {"approved-release-engineering-downsize"}:
        print("ERROR: waived history alerts should record the matched waiver id on each waived alert")
        return 1
    if "approved-release-engineering-downsize" not in waived_history_alert_markdown.read_text(encoding="utf-8"):
        print("ERROR: waived history alert Markdown output should surface the applied waiver id")
        return 1
    require_success(
        "restore original installed baseline",
        [
            "scripts/skills_market.py",
            "restore-installed-baseline",
            repo_relative_path(promotion_history_json),
            "1",
            "--baseline-path",
            repo_relative_path(snapshot_json_path),
            "--markdown-path",
            repo_relative_path(snapshot_markdown_path),
        ],
    )
    restored_original_baseline = load_json(snapshot_json_path)
    if restored_original_baseline.get("summary", {}).get("installed_count") != 3:
        print("ERROR: restoring the first baseline history entry should recover the original installed skill count")
        return 1
    if restored_original_baseline.get("summary", {}).get("bundle_count") != 1:
        print("ERROR: restoring the first baseline history entry should recover the original bundle count")
        return 1
    restored_drift = run_python(
        [
            "scripts/skills_market.py",
            "verify-installed",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--strict",
        ]
    )
    if restored_drift.returncode == 0:
        print("ERROR: restoring an older baseline should surface drift against the current live state")
        if restored_drift.stdout.strip():
            print(restored_drift.stdout.strip())
        if restored_drift.stderr.strip():
            print(restored_drift.stderr.strip())
        return 1
    require_success(
        "restore latest installed baseline",
        [
            "scripts/skills_market.py",
            "restore-installed-baseline",
            repo_relative_path(promotion_history_json),
            "latest",
            "--baseline-path",
            repo_relative_path(snapshot_json_path),
            "--markdown-path",
            repo_relative_path(snapshot_markdown_path),
        ],
    )
    restored_latest_baseline = load_json(snapshot_json_path)
    if restored_latest_baseline.get("summary", {}).get("installed_count") != 1:
        print("ERROR: restoring the latest baseline history entry should recover the refreshed installed skill count")
        return 1
    require_success(
        "verify installed state against promoted baseline",
        [
            "scripts/skills_market.py",
            "verify-installed",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--strict",
        ],
    )
    prune_history_dry_run = require_success(
        "dry-run prune installed baseline history",
        [
            "scripts/skills_market.py",
            "prune-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--keep-last",
            "1",
            "--dry-run",
        ],
    )
    if "Pruned sequences: 1" not in prune_history_dry_run or "Retained sequences: 2" not in prune_history_dry_run:
        print("ERROR: prune-installed-baseline-history dry-run should report pruning the first entry and keeping the latest one")
        return 1
    require_success(
        "prune installed baseline history",
        [
            "scripts/skills_market.py",
            "prune-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--keep-last",
            "1",
        ],
    )
    pruned_history_payload = load_json(promotion_history_json)
    if len(pruned_history_payload.get("entries", [])) != 1:
        print("ERROR: pruning baseline history should retain only one entry")
        return 1
    retained_entry = pruned_history_payload["entries"][0]
    if retained_entry.get("sequence") != 2:
        print("ERROR: pruning baseline history should retain the latest promoted entry without renumbering it")
        return 1
    if archived_initial_baseline.exists():
        print("ERROR: pruning baseline history should remove archived files for pruned entries")
        return 1
    pruned_history_output = require_success(
        "list pruned installed baseline history",
        [
            "scripts/skills_market.py",
            "list-installed-baseline-history",
            repo_relative_path(promotion_history_json),
        ],
    )
    if "Entries: 1" not in pruned_history_output or "Next sequence: 3" not in pruned_history_output:
        print("ERROR: pruned baseline history should preserve the next sequence after dropping old entries")
        return 1
    verify_pruned_entry = run_python(
        [
            "scripts/skills_market.py",
            "verify-installed-history",
            repo_relative_path(promotion_history_json),
            "1",
            "--target-root",
            repo_relative_path(bundle_install_root),
        ]
    )
    if verify_pruned_entry.returncode == 0 or "baseline history entry not found: 1" not in verify_pruned_entry.stderr:
        print("ERROR: verify-installed-history should stop resolving pruned history entries")
        if verify_pruned_entry.stdout.strip():
            print(verify_pruned_entry.stdout.strip())
        if verify_pruned_entry.stderr.strip():
            print(verify_pruned_entry.stderr.strip())
        return 1
    diff_pruned_entry = run_python(
        [
            "scripts/skills_market.py",
            "diff-installed-history",
            repo_relative_path(promotion_history_json),
            "1",
            "latest",
        ]
    )
    if diff_pruned_entry.returncode == 0 or "baseline history entry not found: 1" not in diff_pruned_entry.stderr:
        print("ERROR: diff-installed-history should stop resolving pruned history entries")
        if diff_pruned_entry.stdout.strip():
            print(diff_pruned_entry.stdout.strip())
        if diff_pruned_entry.stderr.strip():
            print(diff_pruned_entry.stderr.strip())
        return 1
    require_success(
        "promote installed baseline after prune",
        [
            "scripts/skills_market.py",
            "promote-installed-baseline",
            repo_relative_path(snapshot_json_path),
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--markdown-path",
            repo_relative_path(snapshot_markdown_path),
            "--history-path",
            repo_relative_path(promotion_history_json),
            "--history-markdown-path",
            repo_relative_path(promotion_history_markdown),
            "--archive-dir",
            repo_relative_path(promotion_archive_dir),
        ],
    )
    post_prune_promotion_history = load_json(promotion_history_json)
    post_prune_sequences = [
        entry.get("sequence")
        for entry in post_prune_promotion_history.get("entries", [])
        if isinstance(entry, dict)
    ]
    if post_prune_sequences != [2, 3]:
        print("ERROR: promotion after prune should append a new sequence instead of reusing a pruned one")
        return 1
    if post_prune_promotion_history.get("next_sequence") != 4:
        print("ERROR: promotion after prune should advance the next sequence marker")
        return 1
    post_prune_history_report_json = output_root / "snapshots" / "history-report-post-prune.json"
    require_success(
        "report installed baseline history after prune",
        [
            "scripts/skills_market.py",
            "report-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--output-path",
            repo_relative_path(post_prune_history_report_json),
        ],
    )
    post_prune_history_report = load_json(post_prune_history_report_json)
    post_prune_report_sequences = [
        item.get("sequence")
        for item in post_prune_history_report.get("timeline", [])
        if isinstance(item, dict)
    ]
    if post_prune_report_sequences != [2, 3]:
        print("ERROR: history report should reflect the retained sequences after prune and re-promotion")
        return 1
    post_prune_history_alert_json = output_root / "snapshots" / "history-alerts-post-prune.json"
    require_success(
        "alert installed baseline history after prune",
        [
            "scripts/skills_market.py",
            "alert-installed-baseline-history",
            repo_relative_path(promotion_history_json),
            "--policy",
            "latest-release-gate",
            "--output-path",
            repo_relative_path(post_prune_history_alert_json),
            "--strict",
        ],
    )
    post_prune_history_alert = load_json(post_prune_history_alert_json)
    if post_prune_history_alert.get("passes") is not True or post_prune_history_alert.get("alert_count") != 0:
        print("ERROR: latest-only history alert should pass after prune and re-promotion keep the latest transition small")
        return 1
    if post_prune_history_alert.get("policy_id") != "latest-release-gate":
        print("ERROR: post-prune history alert should keep reporting the applied policy id")
        return 1
    post_prune_history_waiver_audit_json = output_root / "snapshots" / "history-waiver-audit-post-prune.json"
    post_prune_history_waiver_audit_result = run_python(
        [
            "scripts/skills_market.py",
            "audit-installed-history-waivers",
            repo_relative_path(promotion_history_json),
            "--output-path",
            repo_relative_path(post_prune_history_waiver_audit_json),
            "--json",
            "--strict",
        ]
    )
    if post_prune_history_waiver_audit_result.returncode == 0:
        print("ERROR: waiver audit should fail after prune when the retained history no longer matches the built-in waiver")
        if post_prune_history_waiver_audit_result.stdout.strip():
            print(post_prune_history_waiver_audit_result.stdout.strip())
        if post_prune_history_waiver_audit_result.stderr.strip():
            print(post_prune_history_waiver_audit_result.stderr.strip())
        return 1
    post_prune_history_waiver_audit = load_json(post_prune_history_waiver_audit_json)
    if post_prune_history_waiver_audit.get("unmatched_count") != 1 or post_prune_history_waiver_audit.get("stale_count") != 0:
        print("ERROR: waiver audit should classify the built-in waiver as unmatched after prune removes its retained transition")
        return 1
    post_prune_history_waiver_remediation_json = output_root / "snapshots" / "history-waiver-remediation-post-prune.json"
    post_prune_history_waiver_remediation_result = run_python(
        [
            "scripts/skills_market.py",
            "remediate-installed-history-waivers",
            repo_relative_path(promotion_history_json),
            "--output-path",
            repo_relative_path(post_prune_history_waiver_remediation_json),
            "--json",
            "--strict",
        ]
    )
    if post_prune_history_waiver_remediation_result.returncode == 0:
        print("ERROR: waiver remediation should fail after prune when the built-in waiver needs follow-up")
        if post_prune_history_waiver_remediation_result.stdout.strip():
            print(post_prune_history_waiver_remediation_result.stdout.strip())
        if post_prune_history_waiver_remediation_result.stderr.strip():
            print(post_prune_history_waiver_remediation_result.stderr.strip())
        return 1
    post_prune_history_waiver_remediation = load_json(post_prune_history_waiver_remediation_json)
    post_prune_actions = {
        action.get("code")
        for waiver in post_prune_history_waiver_remediation.get("waivers", [])
        if isinstance(waiver, dict)
        for action in waiver.get("actions", [])
        if isinstance(action, dict)
    }
    if post_prune_actions != {"rescope_or_remove"}:
        print("ERROR: post-prune waiver remediation should suggest rescoping or removing the unmatched waiver")
        return 1
    post_prune_history_waiver_execution_dir = output_root / "waiver-execution-post-prune"
    post_prune_history_waiver_execution_result = run_python(
        [
            "scripts/skills_market.py",
            "draft-installed-history-waiver-execution",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(post_prune_history_waiver_execution_dir),
            "--json",
            "--strict",
        ]
    )
    if post_prune_history_waiver_execution_result.returncode == 0:
        print("ERROR: post-prune waiver execution drafting should fail in strict mode when the built-in waiver needs follow-up")
        if post_prune_history_waiver_execution_result.stdout.strip():
            print(post_prune_history_waiver_execution_result.stdout.strip())
        if post_prune_history_waiver_execution_result.stderr.strip():
            print(post_prune_history_waiver_execution_result.stderr.strip())
        return 1
    post_prune_history_waiver_execution = json.loads(post_prune_history_waiver_execution_result.stdout)
    if post_prune_history_waiver_execution.get("execution_count") != 1:
        print("ERROR: post-prune waiver execution drafting should emit one cleanup action for the unmatched built-in waiver")
        return 1
    if post_prune_history_waiver_execution.get("draft_count") != 0 or post_prune_history_waiver_execution.get("review_count") != 1:
        print("ERROR: post-prune waiver execution drafting should fall back to a review-only cleanup action when no retained transition remains")
        return 1
    post_prune_remove_review = (
        post_prune_history_waiver_execution_dir
        / "waivers"
        / "approved-release-engineering-downsize"
        / "remove-review.json"
    )
    if not post_prune_remove_review.is_file():
        print("ERROR: post-prune waiver execution drafting should emit a remove-review artifact for the unmatched built-in waiver")
        return 1
    if load_json(post_prune_remove_review).get("mode") != "remove_review":
        print("ERROR: post-prune remove-review artifact should record the cleanup review mode")
        return 1
    post_prune_history_waiver_preview_dir = output_root / "waiver-preview-post-prune"
    post_prune_history_waiver_preview_result = run_python(
        [
            "scripts/skills_market.py",
            "preview-installed-history-waiver-execution",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(post_prune_history_waiver_preview_dir),
            "--json",
            "--strict",
        ]
    )
    if post_prune_history_waiver_preview_result.returncode == 0:
        print("ERROR: post-prune waiver preview should fail in strict mode when cleanup review is required")
        if post_prune_history_waiver_preview_result.stdout.strip():
            print(post_prune_history_waiver_preview_result.stdout.strip())
        if post_prune_history_waiver_preview_result.stderr.strip():
            print(post_prune_history_waiver_preview_result.stderr.strip())
        return 1
    post_prune_history_waiver_preview = json.loads(post_prune_history_waiver_preview_result.stdout)
    if post_prune_history_waiver_preview.get("preview_count") != 1:
        print("ERROR: post-prune waiver preview should emit one cleanup preview for the unmatched built-in waiver")
        return 1
    if post_prune_history_waiver_preview.get("draft_preview_count") != 0 or post_prune_history_waiver_preview.get("review_preview_count") != 1:
        print("ERROR: post-prune waiver preview should fall back to a single review-only preview")
        return 1
    post_prune_preview_payload = load_json(
        post_prune_history_waiver_preview_dir / "waivers" / "approved-release-engineering-downsize" / "preview.json"
    )
    if post_prune_preview_payload.get("action_previews", [])[0].get("mode") != "remove_review":
        print("ERROR: post-prune waiver preview should surface the remove-review action mode")
        return 1
    post_prune_history_waiver_apply_dir = output_root / "waiver-apply-post-prune"
    post_prune_history_waiver_apply_result = run_python(
        [
            "scripts/skills_market.py",
            "prepare-installed-history-waiver-apply",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(post_prune_history_waiver_apply_dir),
            "--json",
            "--strict",
        ]
    )
    if post_prune_history_waiver_apply_result.returncode == 0:
        print("ERROR: post-prune waiver apply pack should fail in strict mode when cleanup patches are required")
        if post_prune_history_waiver_apply_result.stdout.strip():
            print(post_prune_history_waiver_apply_result.stdout.strip())
        if post_prune_history_waiver_apply_result.stderr.strip():
            print(post_prune_history_waiver_apply_result.stderr.strip())
        return 1
    post_prune_history_waiver_apply = json.loads(post_prune_history_waiver_apply_result.stdout)
    if post_prune_history_waiver_apply.get("action_count") != 1 or post_prune_history_waiver_apply.get("delete_patch_count") != 1:
        print("ERROR: post-prune waiver apply pack should emit one delete patch for the unmatched built-in waiver")
        return 1
    if post_prune_history_waiver_apply.get("update_patch_count") != 0 or post_prune_history_waiver_apply.get("manual_review_count") != 0:
        print("ERROR: post-prune waiver apply pack should only emit a delete patch, not update or manual-review actions")
        return 1
    post_prune_apply_patch = (
        post_prune_history_waiver_apply_dir
        / "waivers"
        / "approved-release-engineering-downsize"
        / "apply-action-01.patch"
    )
    if not post_prune_apply_patch.is_file():
        print("ERROR: post-prune waiver apply pack should emit a delete patch artifact for the built-in waiver")
        return 1
    post_prune_apply_patch_text = post_prune_apply_patch.read_text(encoding="utf-8")
    if "/dev/null" not in post_prune_apply_patch_text:
        print("ERROR: post-prune delete patch should target /dev/null")
        return 1
    post_prune_execute_write_root = output_root / "waiver-execute-write-root"
    shutil.copytree(ROOT / "governance", post_prune_execute_write_root / "governance")
    post_prune_history_waiver_execute_dir = output_root / "waiver-execute-post-prune"
    post_prune_history_waiver_execute_output = require_success(
        "execute installed baseline history waiver apply pack with write mode",
        [
            "scripts/skills_market.py",
            "execute-installed-history-waiver-apply",
            repo_relative_path(promotion_history_json),
            "--output-dir",
            repo_relative_path(post_prune_history_waiver_execute_dir),
            "--target-root",
            repo_relative_path(post_prune_execute_write_root),
            "--write",
            "--json",
            "--strict",
        ],
    )
    post_prune_history_waiver_execute_payload = json.loads(post_prune_history_waiver_execute_output)
    if post_prune_history_waiver_execute_payload.get("written_delete_count") != 1 or post_prune_history_waiver_execute_payload.get("blocked_action_count") != 0:
        print("ERROR: post-prune waiver execute should write one delete action without safety-check failures")
        return 1
    executed_delete_target = (
        post_prune_execute_write_root
        / "governance"
        / "history-alert-waivers"
        / "approved-release-engineering-downsize.json"
    )
    if executed_delete_target.exists():
        print("ERROR: post-prune write execution should delete the mirrored waiver source file")
        return 1
    require_success(
        "verify newest archived installed baseline history after prune",
        [
            "scripts/skills_market.py",
            "verify-installed-history",
            repo_relative_path(promotion_history_json),
            "latest",
            "--target-root",
            repo_relative_path(bundle_install_root),
            "--strict",
        ],
    )

    doctor_bad_root.mkdir(parents=True, exist_ok=True)
    (doctor_bad_root / "orphan-skill").mkdir(parents=True, exist_ok=True)
    stale_report_dir = doctor_bad_root / "bundle-reports"
    stale_report_dir.mkdir(parents=True, exist_ok=True)
    stale_report_path = stale_report_dir / "stale-bundle.json"
    stale_report_path.write_text(
        json.dumps(
            {
                "bundle_id": "stale-bundle",
                "title": "Stale Bundle",
                "results": [
                    {
                        "skill_id": "moyuan.missing-skill",
                        "status": "installed",
                    }
                ],
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    doctor_bad = run_python(
        [
            "scripts/check_installed_market_state.py",
            "--target-root",
            repo_relative_path(doctor_bad_root),
            "--strict",
        ]
    )
    if doctor_bad.returncode == 0 or "orphan installed directory" not in doctor_bad.stdout:
        print("ERROR: doctor-installed should fail in strict mode when orphan directories exist")
        if doctor_bad.stdout.strip():
            print(doctor_bad.stdout.strip())
        if doctor_bad.stderr.strip():
            print(doctor_bad.stderr.strip())
        return 1
    if "stale-bundle" not in doctor_bad.stdout:
        print("ERROR: doctor-installed should flag stale bundle reports")
        if doctor_bad.stdout.strip():
            print(doctor_bad.stdout.strip())
        return 1

    repair_dry_run = require_success(
        "repair installed state dry-run",
        [
            "scripts/skills_market.py",
            "repair-installed",
            "--target-root",
            repo_relative_path(doctor_bad_root),
            "--dry-run",
        ],
    )
    if "Would remove orphan directories" not in repair_dry_run or "Would remove stale bundle reports" not in repair_dry_run:
        print("ERROR: repair-installed dry-run should describe both orphan directories and stale bundle reports")
        return 1

    require_success(
        "repair installed state",
        [
            "scripts/skills_market.py",
            "repair-installed",
            "--target-root",
            repo_relative_path(doctor_bad_root),
        ],
    )
    if (doctor_bad_root / "orphan-skill").exists():
        print("ERROR: repair-installed should delete orphan install directories")
        return 1
    if stale_report_path.exists():
        print("ERROR: repair-installed should delete stale bundle reports")
        return 1
    doctor_repaired = run_python(
        [
            "scripts/check_installed_market_state.py",
            "--target-root",
            repo_relative_path(doctor_bad_root),
            "--strict",
        ]
    )
    if doctor_repaired.returncode != 0:
        print("ERROR: doctor-installed should pass after repair-installed resolves low-risk drift")
        if doctor_repaired.stdout.strip():
            print(doctor_repaired.stdout.strip())
        if doctor_repaired.stderr.strip():
            print(doctor_repaired.stderr.strip())
        return 1

    registry_index = load_json(output_root / "registry" / "registry.json")
    if registry_index.get("public", {}).get("federation_feed") != "federation/public-feed.json":
        print("ERROR: hosted registry output should publish the public federation feed path")
        return 1

    index_payload = load_json(market_root / "index.json")
    stable_count = index_payload["channels"]["stable"]["count"]
    beta_count = index_payload["channels"]["beta"]["count"]
    if stable_count < 1 or beta_count < 1:
        print("ERROR: market index should expose both stable and beta channels in smoke test")
        return 1

    print("Market pipeline smoke test passed.")
    print(f"Stable channel count: {stable_count}")
    print(f"Beta channel count: {beta_count}")
    print(f"Artifacts root: {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
