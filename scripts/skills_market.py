#!/usr/bin/env python3
"""Unified CLI for the local skills market workflow."""

from __future__ import annotations

import argparse

import audit_installed_baseline_history_waivers
import build_federation_feed
import build_market_catalog
import build_market_index
import build_market_recommendations
import build_market_registry
import build_org_market_index
import check_installed_baseline_history_alerts
import audit_installed_baseline_history_waiver_sources
import check_market_governance
import check_installed_market_state
import check_market_pipeline
import diff_installed_history_baselines
import diff_installed_market_snapshots
import draft_installed_baseline_history_waiver_execution
import execute_installed_baseline_history_waiver_apply
import execute_reconcile_installed_baseline_history_waiver_sources
import install_skill_bundle
import install_skill
import list_installed_baseline_history
import list_installed_baseline_history_policies
import list_installed_baseline_history_waivers
import list_installed_bundles
import list_skill_bundles
import list_installed_skills
import package_skill
import prepare_installed_baseline_history_waiver_apply
import preview_installed_baseline_history_waiver_execution
import promote_installed_market_baseline
import prune_installed_baseline_history
import report_installed_baseline_history
import report_installed_baseline_history_waiver_source_reconcile
import repair_installed_market_state
import reconcile_installed_baseline_history_waiver_sources
import remediate_installed_baseline_history_waivers
import remove_skill_bundle
import remove_skill
import restore_installed_market_baseline
import search_skills
import snapshot_installed_market_state
import update_skill_bundle
import update_installed_skill
import verify_installed_history_baseline
import verify_installed_baseline_history_waiver_source_reconcile
import validate_market_manifest
import verify_installed_market_baseline
import verify_market_provenance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified entrypoint for local skills market workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate market manifests.")
    validate_parser.add_argument("paths", nargs="*", help="Optional manifest file paths.")

    index_parser = subparsers.add_parser("index", help="Build market index files.")
    index_parser.add_argument("--output-dir", help="Output directory for generated market index files.")

    catalog_parser = subparsers.add_parser("catalog", help="Build static HTML market catalog pages.")
    catalog_parser.add_argument("--output-dir", help="Output directory containing market artifacts.")
    catalog_parser.add_argument("--org-policy", help="Optional org market policy file.")

    recommend_parser = subparsers.add_parser("recommend", help="Build recommendation and starter-bundle outputs.")
    recommend_parser.add_argument("--output-dir", help="Output directory containing market artifacts.")
    recommend_parser.add_argument("--org-policy", help="Optional org market policy file.")

    federation_parser = subparsers.add_parser("federation-feed", help="Build a metadata-only federation feed.")
    federation_parser.add_argument("--output-dir", help="Output directory containing market artifacts.")
    federation_parser.add_argument("--org-policy", help="Optional org market policy file.")

    org_index_parser = subparsers.add_parser("org-index", help="Build an org-scoped market index.")
    org_index_parser.add_argument("policy", nargs="?", help="Path to an org market policy JSON file.")
    org_index_parser.add_argument("--output-dir", help="Output directory for generated market artifacts.")

    subparsers.add_parser("governance-check", help="Validate publisher profiles and org market policies.")

    search_parser = subparsers.add_parser("search", help="Search manifests or a generated index.")
    search_parser.add_argument("--query", default="", help="Free-text query.")
    search_parser.add_argument("--category", default="", help="Filter by category.")
    search_parser.add_argument("--tag", default="", help="Filter by tag.")
    search_parser.add_argument("--channel", default="", help="Filter by channel.")
    search_parser.add_argument("--index", default=None, help="Optional channel index JSON file.")

    bundle_list_parser = subparsers.add_parser("list-bundles", help="List starter bundles available in the market.")
    bundle_list_parser.add_argument("--org-policy", help="Optional org market policy file.")
    bundle_list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    package_parser = subparsers.add_parser("package", help="Package one skill or every skill.")
    package_parser.add_argument("skill", nargs="?", help="Skill directory name.")
    package_parser.add_argument("--all", action="store_true", help="Package every skill that has a market manifest.")
    package_parser.add_argument("--output-dir", help="Output directory for package and install artifacts.")

    install_parser = subparsers.add_parser("install", help="Install a skill from an install spec.")
    install_parser.add_argument("install_spec", help="Path to the install spec JSON file.")
    install_parser.add_argument("--target-root", help="Installation root directory.")
    install_parser.add_argument("--dry-run", action="store_true", help="Only print planned actions without extracting files.")

    list_parser = subparsers.add_parser("list-installed", help="List installed skills from skills.lock.json.")
    list_parser.add_argument("--target-root", help="Installation root directory.")
    list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    installed_bundles_parser = subparsers.add_parser("list-installed-bundles", help="List installed starter bundles from bundle reports.")
    installed_bundles_parser.add_argument("--target-root", help="Installation root directory.")
    installed_bundles_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    update_parser = subparsers.add_parser("update", help="Update an installed skill from a generated channel index.")
    update_parser.add_argument("skill", help="Installed skill id, name, or install target.")
    update_parser.add_argument("--index", help="Channel index JSON used to resolve the latest install spec.")
    update_parser.add_argument("--target-root", help="Installation root directory.")
    update_parser.add_argument("--dry-run", action="store_true", help="Only print planned actions.")

    remove_parser = subparsers.add_parser("remove", help="Remove an installed skill and update skills.lock.json.")
    remove_parser.add_argument("skill", help="Installed skill id, name, or install target.")
    remove_parser.add_argument("--target-root", help="Installation root directory.")
    remove_parser.add_argument("--dry-run", action="store_true", help="Only print planned removal.")

    install_bundle_parser = subparsers.add_parser("install-bundle", help="Install every installable skill from a starter bundle.")
    install_bundle_parser.add_argument("bundle", help="Bundle id or title.")
    install_bundle_parser.add_argument("--market-dir", help="Generated market artifact directory.")
    install_bundle_parser.add_argument("--org-policy", help="Optional org market policy file.")
    install_bundle_parser.add_argument("--target-root", help="Installation root directory.")
    install_bundle_parser.add_argument("--dry-run", action="store_true", help="Resolve the bundle install plan without extracting files.")

    update_bundle_parser = subparsers.add_parser("update-bundle", help="Update a previously installed starter bundle.")
    update_bundle_parser.add_argument("bundle", help="Bundle id or title.")
    update_bundle_parser.add_argument("--market-dir", help="Generated market artifact directory.")
    update_bundle_parser.add_argument("--org-policy", help="Optional org market policy file.")
    update_bundle_parser.add_argument("--target-root", help="Installation root directory.")
    update_bundle_parser.add_argument("--dry-run", action="store_true", help="Resolve the bundle update plan without extracting files.")

    remove_bundle_parser = subparsers.add_parser("remove-bundle", help="Remove a previously installed starter bundle.")
    remove_bundle_parser.add_argument("bundle", help="Bundle id or title.")
    remove_bundle_parser.add_argument("--target-root", help="Installation root directory.")
    remove_bundle_parser.add_argument("--dry-run", action="store_true", help="Only print the planned bundle removal.")

    doctor_parser = subparsers.add_parser("doctor-installed", help="Check installed market state for lock/report/filesystem consistency.")
    doctor_parser.add_argument("--target-root", help="Installation root directory.")
    doctor_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    doctor_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when findings are present.")

    repair_parser = subparsers.add_parser("repair-installed", help="Conservatively repair low-risk installed-state drift.")
    repair_parser.add_argument("--target-root", help="Installation root directory.")
    repair_parser.add_argument("--dry-run", action="store_true", help="Only print planned repairs without changing files.")
    repair_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    snapshot_parser = subparsers.add_parser("snapshot-installed", help="Export an installed-state snapshot for archive or review.")
    snapshot_parser.add_argument("--target-root", help="Installation root directory.")
    snapshot_parser.add_argument("--output-path", help="Optional JSON snapshot output path.")
    snapshot_parser.add_argument("--markdown-path", help="Optional Markdown summary output path.")
    snapshot_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    diff_parser = subparsers.add_parser("diff-installed", help="Compare two installed-state snapshots.")
    diff_parser.add_argument("before", help="Baseline snapshot JSON file.")
    diff_parser.add_argument("after", help="Newer snapshot JSON file.")
    diff_parser.add_argument("--output-path", help="Optional JSON diff output path.")
    diff_parser.add_argument("--markdown-path", help="Optional Markdown diff output path.")
    diff_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    diff_history_parser = subparsers.add_parser("diff-installed-history", help="Compare two archived installed baseline history entries.")
    diff_history_parser.add_argument("history", help="Baseline history JSON file.")
    diff_history_parser.add_argument("before_entry", help="Older history entry sequence number or 'latest'.")
    diff_history_parser.add_argument("after_entry", help="Newer history entry sequence number or 'latest'.")
    diff_history_parser.add_argument("--output-path", help="Optional JSON diff output path.")
    diff_history_parser.add_argument("--markdown-path", help="Optional Markdown diff output path.")
    diff_history_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    verify_parser = subparsers.add_parser("verify-installed", help="Compare a live installed-state target against a baseline snapshot.")
    verify_parser.add_argument("baseline", help="Baseline snapshot JSON file.")
    verify_parser.add_argument("--target-root", help="Installation root directory.")
    verify_parser.add_argument("--output-dir", help="Optional directory for current snapshot and diff artifacts.")
    verify_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    verify_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when drift is detected.")

    verify_history_parser = subparsers.add_parser("verify-installed-history", help="Compare a live installed-state target against an archived baseline history entry.")
    verify_history_parser.add_argument("history", help="Baseline history JSON file.")
    verify_history_parser.add_argument("entry", help="History entry sequence number or 'latest'.")
    verify_history_parser.add_argument("--target-root", help="Installation root directory.")
    verify_history_parser.add_argument("--output-dir", help="Optional directory for current snapshot and diff artifacts.")
    verify_history_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    verify_history_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when drift is detected.")

    history_parser = subparsers.add_parser("list-installed-baseline-history", help="List installed-state baseline promotion history.")
    history_parser.add_argument("history", help="Baseline history JSON file.")
    history_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    history_policy_parser = subparsers.add_parser("list-installed-history-policies", help="List reusable installed baseline history alert policies.")
    history_policy_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    history_waiver_parser = subparsers.add_parser("list-installed-history-waivers", help="List reusable installed baseline history alert waivers.")
    history_waiver_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    audit_history_waivers_parser = subparsers.add_parser(
        "audit-installed-history-waivers",
        help="Audit installed baseline history waivers for expired, unmatched, or stale records.",
    )
    audit_history_waivers_parser.add_argument("history", help="Baseline history JSON file.")
    audit_history_waivers_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to audit. Defaults to all known waivers.",
    )
    audit_history_waivers_parser.add_argument("--output-path", help="Optional JSON audit output path.")
    audit_history_waivers_parser.add_argument("--markdown-path", help="Optional Markdown audit output path.")
    audit_history_waivers_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    audit_history_waivers_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when findings are present.")

    remediate_history_waivers_parser = subparsers.add_parser(
        "remediate-installed-history-waivers",
        help="Suggest remediation actions for installed baseline history waiver findings.",
    )
    remediate_history_waivers_parser.add_argument("history", help="Baseline history JSON file.")
    remediate_history_waivers_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to remediate. Defaults to all known waivers.",
    )
    remediate_history_waivers_parser.add_argument("--output-path", help="Optional JSON remediation output path.")
    remediate_history_waivers_parser.add_argument("--markdown-path", help="Optional Markdown remediation output path.")
    remediate_history_waivers_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    remediate_history_waivers_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when remediation is required.")

    draft_history_execution_parser = subparsers.add_parser(
        "draft-installed-history-waiver-execution",
        help="Generate execution drafts for installed baseline history waiver follow-up work.",
    )
    draft_history_execution_parser.add_argument("history", help="Baseline history JSON file.")
    draft_history_execution_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to prepare. Defaults to all known waivers.",
    )
    draft_history_execution_parser.add_argument("--output-dir", help="Optional directory for generated execution artifacts.")
    draft_history_execution_parser.add_argument("--output-path", help="Optional JSON execution summary output path.")
    draft_history_execution_parser.add_argument("--markdown-path", help="Optional Markdown execution summary output path.")
    draft_history_execution_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    draft_history_execution_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when follow-up execution is required.")

    preview_history_execution_parser = subparsers.add_parser(
        "preview-installed-history-waiver-execution",
        help="Compare waiver execution drafts against source waiver files.",
    )
    preview_history_execution_parser.add_argument("history", help="Baseline history JSON file.")
    preview_history_execution_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to preview. Defaults to all known waivers.",
    )
    preview_history_execution_parser.add_argument("--output-dir", help="Optional directory for generated preview artifacts.")
    preview_history_execution_parser.add_argument("--output-path", help="Optional JSON preview summary output path.")
    preview_history_execution_parser.add_argument("--markdown-path", help="Optional Markdown preview summary output path.")
    preview_history_execution_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    preview_history_execution_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when review previews are present.")

    apply_history_execution_parser = subparsers.add_parser(
        "prepare-installed-history-waiver-apply",
        help="Generate apply-ready patch outputs for installed baseline history waiver changes.",
    )
    apply_history_execution_parser.add_argument("history", help="Baseline history JSON file.")
    apply_history_execution_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to prepare. Defaults to all known waivers.",
    )
    apply_history_execution_parser.add_argument("--output-dir", help="Optional directory for generated apply artifacts.")
    apply_history_execution_parser.add_argument("--output-path", help="Optional JSON apply summary output path.")
    apply_history_execution_parser.add_argument("--markdown-path", help="Optional Markdown apply summary output path.")
    apply_history_execution_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    apply_history_execution_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when apply follow-up is required.")

    execute_history_apply_parser = subparsers.add_parser(
        "execute-installed-history-waiver-apply",
        help="Stage or write reviewed installed baseline history waiver apply packs safely.",
    )
    execute_history_apply_parser.add_argument("history", help="Baseline history JSON file.")
    execute_history_apply_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to execute. Defaults to all known waivers.",
    )
    execute_history_apply_parser.add_argument("--output-dir", help="Directory containing or receiving apply-pack artifacts.")
    execute_history_apply_parser.add_argument("--stage-dir", help="Optional staging directory for rendered file changes.")
    execute_history_apply_parser.add_argument("--target-root", help="Optional repo-root mirror used for --write mode.")
    execute_history_apply_parser.add_argument("--write", action="store_true", help="Write approved changes into the target root.")
    execute_history_apply_parser.add_argument("--output-path", help="Optional JSON execution summary output path.")
    execute_history_apply_parser.add_argument("--markdown-path", help="Optional Markdown execution summary output path.")
    execute_history_apply_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    execute_history_apply_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when safety checks block execution.")

    audit_history_source_parser = subparsers.add_parser(
        "audit-installed-history-waiver-sources",
        help="Audit waiver source files against the latest reviewed apply or execute artifacts.",
    )
    audit_history_source_parser.add_argument("history", help="Baseline history JSON file.")
    audit_history_source_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to audit. Defaults to all known waivers.",
    )
    audit_history_source_parser.add_argument(
        "--output-dir",
        help="Directory containing execute artifacts and receiving source-audit summaries.",
    )
    audit_history_source_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits.")
    audit_history_source_parser.add_argument("--output-path", help="Optional JSON source-audit output path.")
    audit_history_source_parser.add_argument("--markdown-path", help="Optional Markdown source-audit output path.")
    audit_history_source_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    audit_history_source_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when source drift is detected.")

    reconcile_history_source_parser = subparsers.add_parser(
        "reconcile-installed-history-waiver-sources",
        help="Build reconcile-ready artifacts for waiver source drift findings.",
    )
    reconcile_history_source_parser.add_argument("history", help="Baseline history JSON file.")
    reconcile_history_source_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to reconcile. Defaults to all known waivers.",
    )
    reconcile_history_source_parser.add_argument(
        "--output-dir",
        help="Directory containing source-audit artifacts and receiving source-reconcile outputs.",
    )
    reconcile_history_source_parser.add_argument("--target-root", help="Optional repo-root mirror used for source reconciliation.")
    reconcile_history_source_parser.add_argument("--output-path", help="Optional JSON source-reconcile output path.")
    reconcile_history_source_parser.add_argument("--markdown-path", help="Optional Markdown source-reconcile output path.")
    reconcile_history_source_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    reconcile_history_source_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when reconcile follow-up is required.")

    execute_reconcile_history_source_parser = subparsers.add_parser(
        "execute-installed-history-waiver-source-reconcile",
        help="Stage or write reviewed source-reconcile repair artifacts safely.",
    )
    execute_reconcile_history_source_parser.add_argument("history", help="Baseline history JSON file.")
    execute_reconcile_history_source_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to execute. Defaults to all known waivers.",
    )
    execute_reconcile_history_source_parser.add_argument(
        "--output-dir",
        help="Directory containing source-reconcile artifacts and receiving execution summaries.",
    )
    execute_reconcile_history_source_parser.add_argument("--stage-dir", help="Optional staging directory for rendered reconcile changes.")
    execute_reconcile_history_source_parser.add_argument("--target-root", help="Optional repo-root mirror used for --write mode.")
    execute_reconcile_history_source_parser.add_argument("--write", action="store_true", help="Write approved reconcile changes into the target root.")
    execute_reconcile_history_source_parser.add_argument("--output-path", help="Optional JSON execution summary output path.")
    execute_reconcile_history_source_parser.add_argument("--markdown-path", help="Optional Markdown execution summary output path.")
    execute_reconcile_history_source_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    execute_reconcile_history_source_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when safety checks block execution.")

    verify_reconcile_history_source_parser = subparsers.add_parser(
        "verify-installed-history-waiver-source-reconcile",
        help="Verify executed source-reconcile repairs against reviewed reconcile artifacts.",
    )
    verify_reconcile_history_source_parser.add_argument("history", help="Baseline history JSON file.")
    verify_reconcile_history_source_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to verify. Defaults to all known waivers.",
    )
    verify_reconcile_history_source_parser.add_argument(
        "--output-dir",
        help="Directory containing source-reconcile and execution artifacts.",
    )
    verify_reconcile_history_source_parser.add_argument("--target-root", help="Optional repo-root mirror used for write verification.")
    verify_reconcile_history_source_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    verify_reconcile_history_source_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    verify_reconcile_history_source_parser.add_argument("--output-path", help="Optional JSON verification summary output path.")
    verify_reconcile_history_source_parser.add_argument("--markdown-path", help="Optional Markdown verification summary output path.")
    verify_reconcile_history_source_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    verify_reconcile_history_source_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when verification drift is detected.")

    report_reconcile_history_source_parser = subparsers.add_parser(
        "report-installed-history-waiver-source-reconcile",
        help="Aggregate source-audit, source-reconcile, execution, and verification artifacts into one report.",
    )
    report_reconcile_history_source_parser.add_argument("history", help="Baseline history JSON file.")
    report_reconcile_history_source_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to report. Defaults to all known waivers.",
    )
    report_reconcile_history_source_parser.add_argument(
        "--output-dir",
        help="Directory containing source-reconcile artifacts and receiving report summaries.",
    )
    report_reconcile_history_source_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    report_reconcile_history_source_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    report_reconcile_history_source_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    report_reconcile_history_source_parser.add_argument("--output-path", help="Optional JSON report output path.")
    report_reconcile_history_source_parser.add_argument("--markdown-path", help="Optional Markdown report output path.")
    report_reconcile_history_source_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    report_history_parser = subparsers.add_parser("report-installed-baseline-history", help="Build a readable report for retained installed baseline history.")
    report_history_parser.add_argument("history", help="Baseline history JSON file.")
    report_history_parser.add_argument("--output-path", help="Optional JSON report output path.")
    report_history_parser.add_argument("--markdown-path", help="Optional Markdown report output path.")
    report_history_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    alert_history_parser = subparsers.add_parser("alert-installed-baseline-history", help="Flag unusually large retained installed baseline history transitions.")
    alert_history_parser.add_argument("history", help="Baseline history JSON file.")
    alert_history_parser.add_argument("--policy", help="Named policy id or JSON file path for reusable alert thresholds.")
    alert_history_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path for approved alert exceptions. May be used more than once.",
    )
    alert_scope_group = alert_history_parser.add_mutually_exclusive_group()
    alert_scope_group.add_argument("--latest-only", dest="latest_only", action="store_true", help="Only evaluate the latest retained transition.")
    alert_scope_group.add_argument("--all-transitions", dest="latest_only", action="store_false", help="Evaluate every retained transition.")
    alert_history_parser.set_defaults(latest_only=None)
    alert_history_parser.add_argument("--max-added-skills", type=int, help="Maximum allowed added skills per transition.")
    alert_history_parser.add_argument("--max-removed-skills", type=int, help="Maximum allowed removed skills per transition.")
    alert_history_parser.add_argument("--max-changed-skills", type=int, help="Maximum allowed changed skills per transition.")
    alert_history_parser.add_argument("--max-added-bundles", type=int, help="Maximum allowed added bundles per transition.")
    alert_history_parser.add_argument("--max-removed-bundles", type=int, help="Maximum allowed removed bundles per transition.")
    alert_history_parser.add_argument("--max-changed-bundles", type=int, help="Maximum allowed changed bundles per transition.")
    alert_history_parser.add_argument("--max-installed-delta", type=int, help="Maximum allowed absolute installed-count delta per transition.")
    alert_history_parser.add_argument("--max-bundle-delta", type=int, help="Maximum allowed absolute bundle-count delta per transition.")
    alert_history_parser.add_argument("--output-path", help="Optional JSON alert output path.")
    alert_history_parser.add_argument("--markdown-path", help="Optional Markdown alert output path.")
    alert_history_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    alert_history_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when alerts are present.")

    prune_history_parser = subparsers.add_parser("prune-installed-baseline-history", help="Prune retained installed-state baseline history entries.")
    prune_history_parser.add_argument("history", help="Baseline history JSON file.")
    prune_history_parser.add_argument("--keep-last", type=int, required=True, help="Number of newest history entries to keep.")
    prune_history_parser.add_argument("--history-markdown-path", help="Optional Markdown history summary path.")
    prune_history_parser.add_argument("--dry-run", action="store_true", help="Only print planned archive removals.")
    prune_history_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    promote_parser = subparsers.add_parser("promote-installed-baseline", help="Promote the current live state into a refreshed baseline snapshot.")
    promote_parser.add_argument("baseline", help="Destination baseline snapshot JSON file.")
    promote_parser.add_argument("--target-root", help="Installation root directory.")
    promote_parser.add_argument("--markdown-path", help="Optional Markdown baseline summary path.")
    promote_parser.add_argument("--diff-output-path", help="Optional JSON path for the transition diff.")
    promote_parser.add_argument("--diff-markdown-path", help="Optional Markdown path for the transition diff.")
    promote_parser.add_argument("--history-path", help="Optional JSON path for baseline promotion history.")
    promote_parser.add_argument("--history-markdown-path", help="Optional Markdown path for baseline promotion history.")
    promote_parser.add_argument("--archive-dir", help="Optional archive directory for promoted baseline copies.")
    promote_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    restore_parser = subparsers.add_parser("restore-installed-baseline", help="Restore a promoted installed-state baseline from history.")
    restore_parser.add_argument("history", help="Baseline history JSON file.")
    restore_parser.add_argument("entry", help="History entry sequence number or 'latest'.")
    restore_parser.add_argument("--baseline-path", help="Optional restore destination for the baseline JSON.")
    restore_parser.add_argument("--markdown-path", help="Optional restore destination for the baseline Markdown summary.")
    restore_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    provenance_parser = subparsers.add_parser("provenance-check", help="Verify install spec provenance or a provenance attestation.")
    provenance_parser.add_argument("path", help="Install spec JSON or provenance attestation JSON.")
    provenance_parser.add_argument("--kind", choices=["auto", "install-spec", "provenance"], default="auto")

    registry_parser = subparsers.add_parser("registry", help="Build a hosted-friendly public/private registry output.")
    registry_parser.add_argument("--output-dir", help="Output directory for the registry build.")

    smoke_parser = subparsers.add_parser("smoke", help="Run the end-to-end market smoke pipeline.")
    smoke_parser.add_argument("--output-root", help="Workspace for generated smoke-test artifacts.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate_market_manifest.main(args.paths)

    if args.command == "index":
        forwarded_args: list[str] = []
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        return build_market_index.main(forwarded_args)

    if args.command == "catalog":
        forwarded_args: list[str] = []
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.org_policy:
            forwarded_args.extend(["--org-policy", args.org_policy])
        return build_market_catalog.main(forwarded_args)

    if args.command == "recommend":
        forwarded_args: list[str] = []
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.org_policy:
            forwarded_args.extend(["--org-policy", args.org_policy])
        return build_market_recommendations.main(forwarded_args)

    if args.command == "federation-feed":
        forwarded_args: list[str] = []
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.org_policy:
            forwarded_args.extend(["--org-policy", args.org_policy])
        return build_federation_feed.main(forwarded_args)

    if args.command == "org-index":
        forwarded_args: list[str] = []
        if args.policy:
            forwarded_args.append(args.policy)
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        return build_org_market_index.main(forwarded_args)

    if args.command == "governance-check":
        return check_market_governance.main()

    if args.command == "search":
        forwarded_args: list[str] = []
        if args.query:
            forwarded_args.extend(["--query", args.query])
        if args.category:
            forwarded_args.extend(["--category", args.category])
        if args.tag:
            forwarded_args.extend(["--tag", args.tag])
        if args.channel:
            forwarded_args.extend(["--channel", args.channel])
        if args.index:
            forwarded_args.extend(["--index", args.index])
        return search_skills.main(forwarded_args)

    if args.command == "list-bundles":
        forwarded_args = []
        if args.org_policy:
            forwarded_args.extend(["--org-policy", args.org_policy])
        if args.json:
            forwarded_args.append("--json")
        return list_skill_bundles.main(forwarded_args)

    if args.command == "package":
        forwarded_args: list[str] = []
        if args.skill:
            forwarded_args.append(args.skill)
        if args.all:
            forwarded_args.append("--all")
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        return package_skill.main(forwarded_args)

    if args.command == "install":
        forwarded_args = [args.install_spec]
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        return install_skill.main(forwarded_args)

    if args.command == "list-installed":
        forwarded_args = []
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.json:
            forwarded_args.append("--json")
        return list_installed_skills.main(forwarded_args)

    if args.command == "list-installed-bundles":
        forwarded_args = []
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.json:
            forwarded_args.append("--json")
        return list_installed_bundles.main(forwarded_args)

    if args.command == "update":
        forwarded_args = [args.skill]
        if args.index:
            forwarded_args.extend(["--index", args.index])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        return update_installed_skill.main(forwarded_args)

    if args.command == "remove":
        forwarded_args = [args.skill]
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        return remove_skill.main(forwarded_args)

    if args.command == "install-bundle":
        forwarded_args = [args.bundle]
        if args.market_dir:
            forwarded_args.extend(["--market-dir", args.market_dir])
        if args.org_policy:
            forwarded_args.extend(["--org-policy", args.org_policy])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        return install_skill_bundle.main(forwarded_args)

    if args.command == "update-bundle":
        forwarded_args = [args.bundle]
        if args.market_dir:
            forwarded_args.extend(["--market-dir", args.market_dir])
        if args.org_policy:
            forwarded_args.extend(["--org-policy", args.org_policy])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        return update_skill_bundle.main(forwarded_args)

    if args.command == "remove-bundle":
        forwarded_args = [args.bundle]
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        return remove_skill_bundle.main(forwarded_args)

    if args.command == "doctor-installed":
        forwarded_args = []
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return check_installed_market_state.main(forwarded_args)

    if args.command == "repair-installed":
        forwarded_args = []
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        if args.json:
            forwarded_args.append("--json")
        return repair_installed_market_state.main(forwarded_args)

    if args.command == "snapshot-installed":
        forwarded_args = []
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return snapshot_installed_market_state.main(forwarded_args)

    if args.command == "diff-installed":
        forwarded_args = [args.before, args.after]
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return diff_installed_market_snapshots.main(forwarded_args)

    if args.command == "diff-installed-history":
        forwarded_args = [args.history, args.before_entry, args.after_entry]
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return diff_installed_history_baselines.main(forwarded_args)

    if args.command == "verify-installed":
        forwarded_args = [args.baseline]
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return verify_installed_market_baseline.main(forwarded_args)

    if args.command == "verify-installed-history":
        forwarded_args = [args.history, args.entry]
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return verify_installed_history_baseline.main(forwarded_args)

    if args.command == "list-installed-baseline-history":
        forwarded_args = [args.history]
        if args.json:
            forwarded_args.append("--json")
        return list_installed_baseline_history.main(forwarded_args)

    if args.command == "list-installed-history-policies":
        forwarded_args = []
        if args.json:
            forwarded_args.append("--json")
        return list_installed_baseline_history_policies.main(forwarded_args)

    if args.command == "list-installed-history-waivers":
        forwarded_args = []
        if args.json:
            forwarded_args.append("--json")
        return list_installed_baseline_history_waivers.main(forwarded_args)

    if args.command == "audit-installed-history-waivers":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return audit_installed_baseline_history_waivers.main(forwarded_args)

    if args.command == "remediate-installed-history-waivers":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return remediate_installed_baseline_history_waivers.main(forwarded_args)

    if args.command == "draft-installed-history-waiver-execution":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return draft_installed_baseline_history_waiver_execution.main(forwarded_args)

    if args.command == "preview-installed-history-waiver-execution":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return preview_installed_baseline_history_waiver_execution.main(forwarded_args)

    if args.command == "prepare-installed-history-waiver-apply":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return prepare_installed_baseline_history_waiver_apply.main(forwarded_args)

    if args.command == "execute-installed-history-waiver-apply":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.write:
            forwarded_args.append("--write")
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return execute_installed_baseline_history_waiver_apply.main(forwarded_args)

    if args.command == "audit-installed-history-waiver-sources":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return audit_installed_baseline_history_waiver_sources.main(forwarded_args)

    if args.command == "reconcile-installed-history-waiver-sources":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return reconcile_installed_baseline_history_waiver_sources.main(forwarded_args)

    if args.command == "execute-installed-history-waiver-source-reconcile":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.write:
            forwarded_args.append("--write")
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return execute_reconcile_installed_baseline_history_waiver_sources.main(forwarded_args)

    if args.command == "verify-installed-history-waiver-source-reconcile":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.execute_summary_path:
            forwarded_args.extend(["--execute-summary-path", args.execute_summary_path])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return verify_installed_baseline_history_waiver_source_reconcile.main(forwarded_args)

    if args.command == "report-installed-history-waiver-source-reconcile":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.execute_summary_path:
            forwarded_args.extend(["--execute-summary-path", args.execute_summary_path])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return report_installed_baseline_history_waiver_source_reconcile.main(forwarded_args)

    if args.command == "report-installed-baseline-history":
        forwarded_args = [args.history]
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return report_installed_baseline_history.main(forwarded_args)

    if args.command == "alert-installed-baseline-history":
        forwarded_args = [args.history]
        if args.policy:
            forwarded_args.extend(["--policy", args.policy])
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        if args.latest_only is True:
            forwarded_args.append("--latest-only")
        if args.latest_only is False:
            forwarded_args.append("--all-transitions")
        if args.max_added_skills is not None:
            forwarded_args.extend(["--max-added-skills", str(args.max_added_skills)])
        if args.max_removed_skills is not None:
            forwarded_args.extend(["--max-removed-skills", str(args.max_removed_skills)])
        if args.max_changed_skills is not None:
            forwarded_args.extend(["--max-changed-skills", str(args.max_changed_skills)])
        if args.max_added_bundles is not None:
            forwarded_args.extend(["--max-added-bundles", str(args.max_added_bundles)])
        if args.max_removed_bundles is not None:
            forwarded_args.extend(["--max-removed-bundles", str(args.max_removed_bundles)])
        if args.max_changed_bundles is not None:
            forwarded_args.extend(["--max-changed-bundles", str(args.max_changed_bundles)])
        if args.max_installed_delta is not None:
            forwarded_args.extend(["--max-installed-delta", str(args.max_installed_delta)])
        if args.max_bundle_delta is not None:
            forwarded_args.extend(["--max-bundle-delta", str(args.max_bundle_delta)])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return check_installed_baseline_history_alerts.main(forwarded_args)

    if args.command == "prune-installed-baseline-history":
        forwarded_args = [args.history, "--keep-last", str(args.keep_last)]
        if args.history_markdown_path:
            forwarded_args.extend(["--history-markdown-path", args.history_markdown_path])
        if args.dry_run:
            forwarded_args.append("--dry-run")
        if args.json:
            forwarded_args.append("--json")
        return prune_installed_baseline_history.main(forwarded_args)

    if args.command == "promote-installed-baseline":
        forwarded_args = [args.baseline]
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.diff_output_path:
            forwarded_args.extend(["--diff-output-path", args.diff_output_path])
        if args.diff_markdown_path:
            forwarded_args.extend(["--diff-markdown-path", args.diff_markdown_path])
        if args.history_path:
            forwarded_args.extend(["--history-path", args.history_path])
        if args.history_markdown_path:
            forwarded_args.extend(["--history-markdown-path", args.history_markdown_path])
        if args.archive_dir:
            forwarded_args.extend(["--archive-dir", args.archive_dir])
        if args.json:
            forwarded_args.append("--json")
        return promote_installed_market_baseline.main(forwarded_args)

    if args.command == "restore-installed-baseline":
        forwarded_args = [args.history, args.entry]
        if args.baseline_path:
            forwarded_args.extend(["--baseline-path", args.baseline_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return restore_installed_market_baseline.main(forwarded_args)

    if args.command == "provenance-check":
        forwarded_args = [args.path]
        if args.kind:
            forwarded_args.extend(["--kind", args.kind])
        return verify_market_provenance.main(forwarded_args)

    if args.command == "registry":
        forwarded_args = []
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        return build_market_registry.main(forwarded_args)

    if args.command == "smoke":
        forwarded_args = []
        if args.output_root:
            forwarded_args.extend(["--output-root", args.output_root])
        return check_market_pipeline.main(forwarded_args)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
