#!/usr/bin/env python3
"""Unified CLI for the local skills market workflow."""

from __future__ import annotations

import argparse

import audit_installed_baseline_history_waivers
import audit_installed_baseline_history_waiver_source_reconcile_waivers
import audit_source_reconcile_gate_waiver_apply_waivers
import build_skill_submission
import catalog_remote_registry
import build_federation_feed
import build_market_catalog
import build_market_index
import build_market_recommendations
import build_market_registry
import build_org_market_index
import check_installed_baseline_history_alerts
import audit_installed_baseline_history_waiver_sources
import check_installed_baseline_history_waiver_source_reconcile_gate
import check_source_reconcile_gate_waiver_apply_gate
import check_market_governance
import check_installed_market_state
import check_market_pipeline
import doctor_skill
import diff_installed_history_baselines
import diff_installed_market_snapshots
import draft_installed_baseline_history_waiver_execution
import draft_source_reconcile_gate_waiver_execution
import execute_installed_baseline_history_waiver_apply
import execute_reconcile_installed_baseline_history_waiver_sources
import install_skill_bundle
import install_skill
import install_remote_skill
import install_remote_bundle
import inspect_remote_skill
import list_installed_baseline_history
import list_installed_baseline_history_policies
import list_installed_baseline_history_waivers
import list_installed_baseline_history_waiver_source_reconcile_policies
import list_installed_baseline_history_waiver_source_reconcile_waivers
import list_source_reconcile_gate_waiver_apply_policies
import list_source_reconcile_gate_waiver_apply_waivers
import list_installed_bundles
import list_skill_bundles
import list_installed_skills
import execute_source_reconcile_gate_waiver_apply
import package_skill
import prepare_source_reconcile_gate_waiver_apply
import prepare_installed_baseline_history_waiver_apply
import preview_installed_baseline_history_waiver_execution
import preview_source_reconcile_gate_waiver_execution
import verify_source_reconcile_gate_waiver_apply
import promote_installed_market_baseline
import prune_installed_baseline_history
import report_installed_baseline_history
import report_installed_baseline_history_waiver_source_reconcile
import report_source_reconcile_gate_waiver_apply
import repair_installed_market_state
import reconcile_installed_baseline_history_waiver_sources
import remediate_installed_baseline_history_waivers
import remediate_installed_baseline_history_waiver_source_reconcile_waivers
import review_skill_submission
import remove_skill_bundle
import remove_skill
import restore_installed_market_baseline
import search_skills
import snapshot_installed_market_state
import scaffold_skill
import ingest_skill_submission
import update_skill_bundle
import update_installed_skill
import upload_skill_submission
import verify_installed_history_baseline
import verify_installed_baseline_history_waiver_source_reconcile
import validate_market_manifest
import verify_installed_market_baseline
import verify_market_provenance
import validate_skill_submission


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified entrypoint for local skills market workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate market manifests.")
    validate_parser.add_argument("paths", nargs="*", help="Optional manifest file paths.")

    index_parser = subparsers.add_parser("index", help="Build market index files.")
    index_parser.add_argument("--output-dir", help="Output directory for generated market index files.")

    catalog_parser = subparsers.add_parser("catalog", help="Build local catalog pages or browse a hosted remote registry.")
    catalog_parser.add_argument("--output-dir", help="Output directory containing market artifacts.")
    catalog_parser.add_argument("--org-policy", help="Optional org market policy file.")
    catalog_parser.add_argument("--registry", help="Hosted registry base URL or registry.json URL.")
    catalog_parser.add_argument("--json", action="store_true", help="Print JSON output when --registry is provided.")

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

    search_parser = subparsers.add_parser("search", help="Search local manifests, a generated index, or a hosted remote registry.")
    search_parser.add_argument("--query", default="", help="Free-text query.")
    search_parser.add_argument("--category", default="", help="Filter by category.")
    search_parser.add_argument("--tag", default="", help="Filter by tag.")
    search_parser.add_argument("--channel", default="", help="Filter by channel.")
    search_parser.add_argument("--index", default=None, help="Optional channel index JSON file.")
    search_parser.add_argument("--registry", default=None, help="Hosted registry base URL or registry.json URL.")
    search_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    bundle_list_parser = subparsers.add_parser("list-bundles", help="List starter bundles available in the market.")
    bundle_list_parser.add_argument("--org-policy", help="Optional org market policy file.")
    bundle_list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    package_parser = subparsers.add_parser("package", help="Package one skill or every skill.")
    package_parser.add_argument("skill", nargs="?", help="Skill directory name or path.")
    package_parser.add_argument("--all", action="store_true", help="Package every skill that has a market manifest.")
    package_parser.add_argument("--output-dir", help="Output directory for package and install artifacts.")

    build_submission_parser = subparsers.add_parser("build-submission", help="Build a repo-compatible skill submission artifact.")
    build_submission_parser.add_argument("skill", help="Skill directory name or path.")
    build_submission_parser.add_argument("--output-dir", help="Output directory for submission artifacts.")
    build_submission_parser.add_argument("--market-dir", help="Market artifact directory used for package/install/provenance artifacts.")
    build_submission_parser.add_argument("--release-notes", help="Inline release notes text for the submission.")
    build_submission_parser.add_argument("--release-notes-file", help="Optional file whose contents become the submission release notes.")

    validate_submission_parser = subparsers.add_parser("validate-submission", help="Validate a skill submission artifact.")
    validate_submission_parser.add_argument("path", help="Path to submission.json.")

    upload_submission_parser = subparsers.add_parser("upload-submission", help="Upload a skill submission into a local inbox.")
    upload_submission_parser.add_argument("path", help="Path to submission.json.")
    upload_submission_parser.add_argument("--inbox-dir", help="Inbox directory receiving uploaded submissions.")
    upload_submission_parser.add_argument("--force", action="store_true", help="Replace an existing uploaded submission directory.")

    review_submission_parser = subparsers.add_parser("review-submission", help="Review an uploaded skill submission.")
    review_submission_parser.add_argument("path", help="Path to an uploaded submission.json file.")
    review_submission_parser.add_argument(
        "--status",
        "--review-status",
        dest="review_status",
        choices=["pending", "approved", "rejected", "needs-changes"],
        default="approved",
        help="Review decision to record.",
    )
    review_submission_parser.add_argument("--reviewer", help="Reviewer id.")
    review_submission_parser.add_argument("--summary", help="Short review summary.")
    review_submission_parser.add_argument("--finding", action="append", help="Optional finding entry.")
    review_submission_parser.add_argument("--run-checker", action="store_true", help="Run the uploaded checker command before writing review.json.")
    review_submission_parser.add_argument("--review-path", help="Optional path for review.json.")
    review_submission_parser.add_argument("--force", action="store_true", help="Replace an existing review.json file.")

    ingest_submission_parser = subparsers.add_parser("ingest-submission", help="Ingest an approved uploaded skill submission.")
    ingest_submission_parser.add_argument("path", help="Path to an uploaded submission.json file.")
    ingest_submission_parser.add_argument("--review-path", help="Optional path to review.json.")
    ingest_submission_parser.add_argument("--skills-dir", help="Destination root for ingested skills.")
    ingest_submission_parser.add_argument("--docs-dir", help="Destination root for ingested docs.")
    ingest_submission_parser.add_argument("--force", action="store_true", help="Replace existing canonical skill/docs targets when needed.")

    scaffold_parser = subparsers.add_parser("scaffold-skill", help="Scaffold a new skill from a bundled template pack.")
    scaffold_parser.add_argument("skill_name", help="Skill directory name, for example release-note-writer.")
    scaffold_parser.add_argument(
        "--template",
        choices=["beginner", "advanced", "market-ready"],
        help="Template pack to scaffold. Defaults to market-ready.",
    )
    scaffold_parser.add_argument("--path", help="Repo-relative parent directory for the generated skill.")
    scaffold_parser.add_argument("--title", help="Optional display title.")
    scaffold_parser.add_argument("--publisher", help="Publisher id used by market-ready manifests.")
    scaffold_parser.add_argument("--channel", help="Release channel for market-ready manifests.")
    scaffold_parser.add_argument("--version", help="Initial version for market-ready manifests.")
    scaffold_parser.add_argument("--summary", help="Optional market summary for market-ready scaffolds.")
    scaffold_parser.add_argument("--description", help="Optional market description for market-ready scaffolds.")
    scaffold_parser.add_argument("--category", action="append", help="Category value for market-ready manifests.")
    scaffold_parser.add_argument("--tag", action="append", help="Tag value for market-ready manifests.")
    scaffold_parser.add_argument("--keyword", action="append", help="Search keyword value for market-ready manifests.")

    doctor_skill_parser = subparsers.add_parser("doctor-skill", help="Inspect a skill for authoring and market-readiness gaps.")
    doctor_skill_parser.add_argument("skill", help="Skill directory name or path.")
    doctor_skill_parser.add_argument("--run-checker", action="store_true", help="Execute the checker command when available.")
    doctor_skill_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    install_parser = subparsers.add_parser("install", help="Install a skill from a local install spec or remote registry.")
    install_parser.add_argument("install_spec", help="Local install spec path, or a remote skill id/name when --registry is provided.")
    install_parser.add_argument("--registry", help="Hosted registry base URL or registry.json URL.")
    install_parser.add_argument("--channel", default="stable", help="Remote channel to resolve when --registry is used.")
    install_parser.add_argument("--cache-root", help="Cache directory for downloaded remote artifacts.")
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
    install_bundle_parser.add_argument("--registry", help="Hosted registry base URL or registry.json URL.")
    install_bundle_parser.add_argument("--cache-root", help="Cache directory for downloaded remote artifacts.")
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

    source_reconcile_policy_parser = subparsers.add_parser(
        "list-installed-history-waiver-source-reconcile-policies",
        help="List reusable installed history waiver source-reconcile gate policies.",
    )
    source_reconcile_policy_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    source_reconcile_apply_policy_parser = subparsers.add_parser(
        "list-installed-history-waiver-source-reconcile-waiver-apply-policies",
        help="List reusable source-reconcile gate waiver apply policies.",
    )
    source_reconcile_apply_policy_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    source_reconcile_apply_waiver_parser = subparsers.add_parser(
        "list-installed-history-waiver-source-reconcile-waiver-apply-waivers",
        help="List reusable source-reconcile gate waiver apply waivers.",
    )
    source_reconcile_apply_waiver_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    audit_source_reconcile_apply_waivers_parser = subparsers.add_parser(
        "audit-installed-history-waiver-source-reconcile-waiver-apply-waivers",
        help="Audit source-reconcile gate waiver apply waivers for expired, unmatched, stale, or policy-mismatch records.",
    )
    audit_source_reconcile_apply_waivers_parser.add_argument("history", help="Baseline history JSON file.")
    audit_source_reconcile_apply_waivers_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile context.",
    )
    audit_source_reconcile_apply_waivers_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path used to build the apply-gate context.",
    )
    audit_source_reconcile_apply_waivers_parser.add_argument(
        "--apply-gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver apply waiver id or JSON file path to audit. Defaults to all known apply-gate waivers.",
    )
    audit_source_reconcile_apply_waivers_parser.add_argument("--output-dir", help="Directory containing apply-gate artifacts and receiving audit summaries.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--target-root", help="Optional repo-root mirror used for write verification.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--source-reconcile-execute-summary-path", help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--apply-execute-summary-path", help="Optional source-reconcile gate waiver apply execution summary JSON path.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--output-path", help="Optional JSON audit output path.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--markdown-path", help="Optional Markdown audit output path.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    audit_source_reconcile_apply_waivers_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when findings are present.")

    source_reconcile_waiver_parser = subparsers.add_parser(
        "list-installed-history-waiver-source-reconcile-waivers",
        help="List reusable installed history waiver source-reconcile gate waivers.",
    )
    source_reconcile_waiver_parser.add_argument("--json", action="store_true", help="Print JSON output.")

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

    audit_source_reconcile_waivers_parser = subparsers.add_parser(
        "audit-installed-history-waiver-source-reconcile-waivers",
        help="Audit source-reconcile gate waivers for expired, unmatched, stale, or policy-mismatch records.",
    )
    audit_source_reconcile_waivers_parser.add_argument("history", help="Baseline history JSON file.")
    audit_source_reconcile_waivers_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    audit_source_reconcile_waivers_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to audit. Defaults to all known gate waivers.",
    )
    audit_source_reconcile_waivers_parser.add_argument("--output-dir", help="Directory containing source-reconcile artifacts and receiving audit summaries.")
    audit_source_reconcile_waivers_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    audit_source_reconcile_waivers_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    audit_source_reconcile_waivers_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    audit_source_reconcile_waivers_parser.add_argument("--output-path", help="Optional JSON audit output path.")
    audit_source_reconcile_waivers_parser.add_argument("--markdown-path", help="Optional Markdown audit output path.")
    audit_source_reconcile_waivers_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    audit_source_reconcile_waivers_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when findings are present.")

    remediate_source_reconcile_waivers_parser = subparsers.add_parser(
        "remediate-installed-history-waiver-source-reconcile-waivers",
        help="Suggest remediation actions for source-reconcile gate waiver findings.",
    )
    remediate_source_reconcile_waivers_parser.add_argument("history", help="Baseline history JSON file.")
    remediate_source_reconcile_waivers_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    remediate_source_reconcile_waivers_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to remediate. Defaults to all known gate waivers.",
    )
    remediate_source_reconcile_waivers_parser.add_argument("--output-dir", help="Directory containing source-reconcile artifacts and receiving remediation summaries.")
    remediate_source_reconcile_waivers_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    remediate_source_reconcile_waivers_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    remediate_source_reconcile_waivers_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    remediate_source_reconcile_waivers_parser.add_argument("--output-path", help="Optional JSON remediation output path.")
    remediate_source_reconcile_waivers_parser.add_argument("--markdown-path", help="Optional Markdown remediation output path.")
    remediate_source_reconcile_waivers_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    remediate_source_reconcile_waivers_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when remediations are required.")

    draft_source_reconcile_waiver_execution_parser = subparsers.add_parser(
        "draft-installed-history-waiver-source-reconcile-waiver-execution",
        help="Generate execution drafts for source-reconcile gate waiver follow-up work.",
    )
    draft_source_reconcile_waiver_execution_parser.add_argument("history", help="Baseline history JSON file.")
    draft_source_reconcile_waiver_execution_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    draft_source_reconcile_waiver_execution_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to prepare. Defaults to all known gate waivers.",
    )
    draft_source_reconcile_waiver_execution_parser.add_argument("--output-dir", help="Directory containing source-reconcile artifacts and receiving execution summaries.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--output-path", help="Optional JSON execution summary output path.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--markdown-path", help="Optional Markdown execution summary output path.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    draft_source_reconcile_waiver_execution_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when execution follow-up is required.")

    preview_source_reconcile_waiver_execution_parser = subparsers.add_parser(
        "preview-installed-history-waiver-source-reconcile-waiver-execution",
        help="Compare source-reconcile gate waiver execution drafts against source waiver files.",
    )
    preview_source_reconcile_waiver_execution_parser.add_argument("history", help="Baseline history JSON file.")
    preview_source_reconcile_waiver_execution_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    preview_source_reconcile_waiver_execution_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to preview. Defaults to all known gate waivers.",
    )
    preview_source_reconcile_waiver_execution_parser.add_argument("--output-dir", help="Directory containing source-reconcile artifacts and receiving preview summaries.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--output-path", help="Optional JSON preview summary output path.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--markdown-path", help="Optional Markdown preview summary output path.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    preview_source_reconcile_waiver_execution_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when review previews are present.")

    prepare_source_reconcile_waiver_apply_parser = subparsers.add_parser(
        "prepare-installed-history-waiver-source-reconcile-waiver-apply",
        help="Generate apply-ready patch outputs for source-reconcile gate waiver changes.",
    )
    prepare_source_reconcile_waiver_apply_parser.add_argument("history", help="Baseline history JSON file.")
    prepare_source_reconcile_waiver_apply_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    prepare_source_reconcile_waiver_apply_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to prepare. Defaults to all known gate waivers.",
    )
    prepare_source_reconcile_waiver_apply_parser.add_argument("--output-dir", help="Directory containing source-reconcile artifacts and receiving apply summaries.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--output-path", help="Optional JSON apply summary output path.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--markdown-path", help="Optional Markdown apply summary output path.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    prepare_source_reconcile_waiver_apply_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when apply follow-up is required.")

    execute_source_reconcile_waiver_apply_parser = subparsers.add_parser(
        "execute-installed-history-waiver-source-reconcile-waiver-apply",
        help="Stage or write reviewed source-reconcile gate waiver apply packs safely.",
    )
    execute_source_reconcile_waiver_apply_parser.add_argument("history", help="Baseline history JSON file.")
    execute_source_reconcile_waiver_apply_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    execute_source_reconcile_waiver_apply_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to execute. Defaults to all known gate waivers.",
    )
    execute_source_reconcile_waiver_apply_parser.add_argument("--output-dir", help="Directory containing or receiving apply-pack artifacts.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--stage-dir", help="Optional staging directory for rendered file changes.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--target-root", help="Optional repo-root mirror used for --write mode.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--write", action="store_true", help="Write approved changes into the target root.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--output-path", help="Optional JSON execution summary output path.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--markdown-path", help="Optional Markdown execution summary output path.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    execute_source_reconcile_waiver_apply_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when safety checks block execution.")

    verify_source_reconcile_waiver_apply_parser = subparsers.add_parser(
        "verify-installed-history-waiver-source-reconcile-waiver-apply",
        help="Verify source-reconcile gate waiver apply execution results against reviewed apply artifacts.",
    )
    verify_source_reconcile_waiver_apply_parser.add_argument("history", help="Baseline history JSON file.")
    verify_source_reconcile_waiver_apply_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    verify_source_reconcile_waiver_apply_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to verify. Defaults to all known gate waivers.",
    )
    verify_source_reconcile_waiver_apply_parser.add_argument("--output-dir", help="Directory containing apply and execution artifacts.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--target-root", help="Optional repo-root mirror used for write verification.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--source-reconcile-execute-summary-path", help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--apply-execute-summary-path", help="Optional source-reconcile gate waiver apply execution summary JSON path.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--output-path", help="Optional JSON verification summary output path.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--markdown-path", help="Optional Markdown verification summary output path.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    verify_source_reconcile_waiver_apply_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when verification drift is detected.")

    report_source_reconcile_waiver_apply_parser = subparsers.add_parser(
        "report-installed-history-waiver-source-reconcile-waiver-apply",
        help="Aggregate apply, execution, and verification artifacts for source-reconcile gate waiver changes.",
    )
    report_source_reconcile_waiver_apply_parser.add_argument("history", help="Baseline history JSON file.")
    report_source_reconcile_waiver_apply_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named installed-history waiver id or JSON file path used to build the source-reconcile report context.",
    )
    report_source_reconcile_waiver_apply_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path to report. Defaults to all known gate waivers.",
    )
    report_source_reconcile_waiver_apply_parser.add_argument("--output-dir", help="Directory containing apply and verification artifacts.")
    report_source_reconcile_waiver_apply_parser.add_argument("--target-root", help="Optional repo-root mirror used for write verification.")
    report_source_reconcile_waiver_apply_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    report_source_reconcile_waiver_apply_parser.add_argument("--source-reconcile-execute-summary-path", help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.")
    report_source_reconcile_waiver_apply_parser.add_argument("--apply-execute-summary-path", help="Optional source-reconcile gate waiver apply execution summary JSON path.")
    report_source_reconcile_waiver_apply_parser.add_argument("--output-path", help="Optional JSON report output path.")
    report_source_reconcile_waiver_apply_parser.add_argument("--markdown-path", help="Optional Markdown report output path.")
    report_source_reconcile_waiver_apply_parser.add_argument("--json", action="store_true", help="Print JSON output.")

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

    gate_reconcile_history_source_parser = subparsers.add_parser(
        "gate-installed-history-waiver-source-reconcile",
        help="Evaluate source-reconcile report artifacts as a reusable gate.",
    )
    gate_reconcile_history_source_parser.add_argument("history", help="Baseline history JSON file.")
    gate_reconcile_history_source_parser.add_argument("--policy", help="Named policy id or JSON file path for reusable source-reconcile gate rules.")
    gate_reconcile_history_source_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to gate. Defaults to all known waivers.",
    )
    gate_reconcile_history_source_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path. May be used more than once.",
    )
    gate_reconcile_history_source_parser.add_argument(
        "--output-dir",
        help="Directory containing source-reconcile artifacts and receiving gate summaries.",
    )
    gate_reconcile_history_source_parser.add_argument("--target-root", help="Optional repo-root mirror used for source audits and verification.")
    gate_reconcile_history_source_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    gate_reconcile_history_source_parser.add_argument("--execute-summary-path", help="Optional source-reconcile execution summary JSON path.")
    gate_reconcile_history_source_parser.add_argument(
        "--allow-state",
        action="append",
        default=[],
        help="Report state that should be treated as passing. Defaults to verified and no_reconcile_actions.",
    )
    gate_reconcile_history_source_parser.add_argument("--output-path", help="Optional JSON gate output path.")
    gate_reconcile_history_source_parser.add_argument("--markdown-path", help="Optional Markdown gate output path.")
    gate_reconcile_history_source_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    gate_reconcile_history_source_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when the gate fails.")

    gate_reconcile_history_source_apply_parser = subparsers.add_parser(
        "gate-installed-history-waiver-source-reconcile-waiver-apply",
        help="Evaluate source-reconcile gate waiver apply reports as a reusable gate.",
    )
    gate_reconcile_history_source_apply_parser.add_argument("history", help="Baseline history JSON file.")
    gate_reconcile_history_source_apply_parser.add_argument("--policy", help="Named policy id or JSON file path for reusable apply gate rules.")
    gate_reconcile_history_source_apply_parser.add_argument(
        "--waiver",
        action="append",
        default=[],
        help="Named waiver id or JSON file path to report. Defaults to all known waivers.",
    )
    gate_reconcile_history_source_apply_parser.add_argument(
        "--gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver id or JSON file path. May be used more than once.",
    )
    gate_reconcile_history_source_apply_parser.add_argument(
        "--apply-gate-waiver",
        action="append",
        default=[],
        help="Named source-reconcile gate waiver apply waiver id or JSON file path. May be used more than once.",
    )
    gate_reconcile_history_source_apply_parser.add_argument("--output-dir", help="Directory containing apply artifacts and receiving gate summaries.")
    gate_reconcile_history_source_apply_parser.add_argument("--target-root", help="Optional repo-root mirror used for write verification.")
    gate_reconcile_history_source_apply_parser.add_argument("--stage-dir", help="Optional staging directory used for staged verification.")
    gate_reconcile_history_source_apply_parser.add_argument("--source-reconcile-execute-summary-path", help="Optional source-reconcile execution summary JSON path used when apply artifacts must be regenerated.")
    gate_reconcile_history_source_apply_parser.add_argument("--apply-execute-summary-path", help="Optional source-reconcile gate waiver apply execution summary JSON path.")
    gate_reconcile_history_source_apply_parser.add_argument(
        "--allow-state",
        action="append",
        default=[],
        help="Report state that should be treated as passing. Defaults to verified and no_apply_actions.",
    )
    gate_reconcile_history_source_apply_parser.add_argument("--output-path", help="Optional JSON gate output path.")
    gate_reconcile_history_source_apply_parser.add_argument("--markdown-path", help="Optional Markdown gate output path.")
    gate_reconcile_history_source_apply_parser.add_argument("--json", action="store_true", help="Print JSON output.")
    gate_reconcile_history_source_apply_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when the gate fails.")

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

    inspect_remote_parser = subparsers.add_parser("inspect-remote-skill", help="Inspect one remote skill from a hosted registry.")
    inspect_remote_parser.add_argument("skill", help="Remote skill id or skill name.")
    inspect_remote_parser.add_argument("--registry", required=True, help="Hosted registry base URL or registry.json URL.")
    inspect_remote_parser.add_argument("--channel", default="", help="Optional preferred channel when resolving the remote skill.")
    inspect_remote_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    smoke_parser = subparsers.add_parser("smoke", help="Run the end-to-end market smoke pipeline.")
    smoke_parser.add_argument("--output-root", help="Workspace for generated smoke-test artifacts.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate_market_manifest.main(args.paths)

    if args.command == "scaffold-skill":
        forwarded_args = [args.skill_name]
        if args.template:
            forwarded_args.extend(["--template", args.template])
        if args.path:
            forwarded_args.extend(["--path", args.path])
        if args.title:
            forwarded_args.extend(["--title", args.title])
        if args.publisher:
            forwarded_args.extend(["--publisher", args.publisher])
        if args.channel:
            forwarded_args.extend(["--channel", args.channel])
        if args.version:
            forwarded_args.extend(["--version", args.version])
        if args.summary:
            forwarded_args.extend(["--summary", args.summary])
        if args.description:
            forwarded_args.extend(["--description", args.description])
        if args.category:
            for item in args.category:
                forwarded_args.extend(["--category", item])
        if args.tag:
            for item in args.tag:
                forwarded_args.extend(["--tag", item])
        if args.keyword:
            for item in args.keyword:
                forwarded_args.extend(["--keyword", item])
        return scaffold_skill.main(forwarded_args)

    if args.command == "doctor-skill":
        forwarded_args = [args.skill]
        if args.run_checker:
            forwarded_args.append("--run-checker")
        if args.json:
            forwarded_args.append("--json")
        return doctor_skill.main(forwarded_args)

    if args.command == "index":
        forwarded_args: list[str] = []
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        return build_market_index.main(forwarded_args)

    if args.command == "catalog":
        if args.registry:
            forwarded_args = ["--registry", args.registry]
            if args.json:
                forwarded_args.append("--json")
            return catalog_remote_registry.main(forwarded_args)
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
        if args.registry:
            forwarded_args.extend(["--registry", args.registry])
        if args.json:
            forwarded_args.append("--json")
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

    if args.command == "build-submission":
        forwarded_args = [args.skill]
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.market_dir:
            forwarded_args.extend(["--market-dir", args.market_dir])
        if args.release_notes:
            forwarded_args.extend(["--release-notes", args.release_notes])
        if args.release_notes_file:
            forwarded_args.extend(["--release-notes-file", args.release_notes_file])
        return build_skill_submission.main(forwarded_args)

    if args.command == "validate-submission":
        return validate_skill_submission.main([args.path])

    if args.command == "upload-submission":
        forwarded_args = [args.path]
        if args.inbox_dir:
            forwarded_args.extend(["--inbox-dir", args.inbox_dir])
        if args.force:
            forwarded_args.append("--force")
        return upload_skill_submission.main(forwarded_args)

    if args.command == "review-submission":
        forwarded_args = [args.path]
        if args.review_status:
            forwarded_args.extend(["--review-status", args.review_status])
        if args.reviewer:
            forwarded_args.extend(["--reviewer", args.reviewer])
        if args.summary:
            forwarded_args.extend(["--summary", args.summary])
        if args.finding:
            for finding in args.finding:
                forwarded_args.extend(["--finding", finding])
        if args.run_checker:
            forwarded_args.append("--run-checker")
        if args.review_path:
            forwarded_args.extend(["--review-path", args.review_path])
        if args.force:
            forwarded_args.append("--force")
        return review_skill_submission.main(forwarded_args)

    if args.command == "ingest-submission":
        forwarded_args = [args.path]
        if args.review_path:
            forwarded_args.extend(["--review-path", args.review_path])
        if args.skills_dir:
            forwarded_args.extend(["--skills-dir", args.skills_dir])
        if args.docs_dir:
            forwarded_args.extend(["--docs-dir", args.docs_dir])
        if args.force:
            forwarded_args.append("--force")
        return ingest_skill_submission.main(forwarded_args)

    if args.command == "install":
        forwarded_args = [args.install_spec]
        if args.registry:
            forwarded_args.extend(["--registry", args.registry])
            if args.channel:
                forwarded_args.extend(["--channel", args.channel])
            if args.cache_root:
                forwarded_args.extend(["--cache-root", args.cache_root])
            if args.target_root:
                forwarded_args.extend(["--target-root", args.target_root])
            if args.dry_run:
                forwarded_args.append("--dry-run")
            return install_remote_skill.main(forwarded_args)
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
        if args.registry:
            forwarded_args.extend(["--registry", args.registry])
            if args.cache_root:
                forwarded_args.extend(["--cache-root", args.cache_root])
            if args.target_root:
                forwarded_args.extend(["--target-root", args.target_root])
            if args.dry_run:
                forwarded_args.append("--dry-run")
            return install_remote_bundle.main(forwarded_args)
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

    if args.command == "list-installed-history-waiver-source-reconcile-policies":
        forwarded_args = []
        if args.json:
            forwarded_args.append("--json")
        return list_installed_baseline_history_waiver_source_reconcile_policies.main(forwarded_args)

    if args.command == "list-installed-history-waiver-source-reconcile-waiver-apply-policies":
        forwarded_args = []
        if args.json:
            forwarded_args.append("--json")
        return list_source_reconcile_gate_waiver_apply_policies.main(forwarded_args)

    if args.command == "list-installed-history-waiver-source-reconcile-waiver-apply-waivers":
        forwarded_args = []
        if args.json:
            forwarded_args.append("--json")
        return list_source_reconcile_gate_waiver_apply_waivers.main(forwarded_args)

    if args.command == "audit-installed-history-waiver-source-reconcile-waiver-apply-waivers":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
        for apply_gate_waiver in args.apply_gate_waiver:
            forwarded_args.extend(["--apply-gate-waiver", apply_gate_waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.source_reconcile_execute_summary_path:
            forwarded_args.extend(["--source-reconcile-execute-summary-path", args.source_reconcile_execute_summary_path])
        if args.apply_execute_summary_path:
            forwarded_args.extend(["--apply-execute-summary-path", args.apply_execute_summary_path])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return audit_source_reconcile_gate_waiver_apply_waivers.main(forwarded_args)

    if args.command == "list-installed-history-waiver-source-reconcile-waivers":
        forwarded_args = []
        if args.json:
            forwarded_args.append("--json")
        return list_installed_baseline_history_waiver_source_reconcile_waivers.main(forwarded_args)

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

    if args.command == "audit-installed-history-waiver-source-reconcile-waivers":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
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
        return audit_installed_baseline_history_waiver_source_reconcile_waivers.main(forwarded_args)

    if args.command == "remediate-installed-history-waiver-source-reconcile-waivers":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
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
        return remediate_installed_baseline_history_waiver_source_reconcile_waivers.main(forwarded_args)

    if args.command == "draft-installed-history-waiver-source-reconcile-waiver-execution":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
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
        return draft_source_reconcile_gate_waiver_execution.main(forwarded_args)

    if args.command == "preview-installed-history-waiver-source-reconcile-waiver-execution":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
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
        return preview_source_reconcile_gate_waiver_execution.main(forwarded_args)

    if args.command == "prepare-installed-history-waiver-source-reconcile-waiver-apply":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
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
        return prepare_source_reconcile_gate_waiver_apply.main(forwarded_args)

    if args.command == "execute-installed-history-waiver-source-reconcile-waiver-apply":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.write:
            forwarded_args.append("--write")
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
        return execute_source_reconcile_gate_waiver_apply.main(forwarded_args)

    if args.command == "verify-installed-history-waiver-source-reconcile-waiver-apply":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.source_reconcile_execute_summary_path:
            forwarded_args.extend(["--source-reconcile-execute-summary-path", args.source_reconcile_execute_summary_path])
        if args.apply_execute_summary_path:
            forwarded_args.extend(["--apply-execute-summary-path", args.apply_execute_summary_path])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return verify_source_reconcile_gate_waiver_apply.main(forwarded_args)

    if args.command == "report-installed-history-waiver-source-reconcile-waiver-apply":
        forwarded_args = [args.history]
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.source_reconcile_execute_summary_path:
            forwarded_args.extend(["--source-reconcile-execute-summary-path", args.source_reconcile_execute_summary_path])
        if args.apply_execute_summary_path:
            forwarded_args.extend(["--apply-execute-summary-path", args.apply_execute_summary_path])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        return report_source_reconcile_gate_waiver_apply.main(forwarded_args)

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

    if args.command == "gate-installed-history-waiver-source-reconcile":
        forwarded_args = [args.history]
        if args.policy:
            forwarded_args.extend(["--policy", args.policy])
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.execute_summary_path:
            forwarded_args.extend(["--execute-summary-path", args.execute_summary_path])
        for allowed_state in args.allow_state:
            forwarded_args.extend(["--allow-state", allowed_state])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return check_installed_baseline_history_waiver_source_reconcile_gate.main(forwarded_args)

    if args.command == "gate-installed-history-waiver-source-reconcile-waiver-apply":
        forwarded_args = [args.history]
        if args.policy:
            forwarded_args.extend(["--policy", args.policy])
        for waiver in args.waiver:
            forwarded_args.extend(["--waiver", waiver])
        for gate_waiver in args.gate_waiver:
            forwarded_args.extend(["--gate-waiver", gate_waiver])
        for apply_gate_waiver in args.apply_gate_waiver:
            forwarded_args.extend(["--apply-gate-waiver", apply_gate_waiver])
        if args.output_dir:
            forwarded_args.extend(["--output-dir", args.output_dir])
        if args.target_root:
            forwarded_args.extend(["--target-root", args.target_root])
        if args.stage_dir:
            forwarded_args.extend(["--stage-dir", args.stage_dir])
        if args.source_reconcile_execute_summary_path:
            forwarded_args.extend(["--source-reconcile-execute-summary-path", args.source_reconcile_execute_summary_path])
        if args.apply_execute_summary_path:
            forwarded_args.extend(["--apply-execute-summary-path", args.apply_execute_summary_path])
        for allowed_state in args.allow_state:
            forwarded_args.extend(["--allow-state", allowed_state])
        if args.output_path:
            forwarded_args.extend(["--output-path", args.output_path])
        if args.markdown_path:
            forwarded_args.extend(["--markdown-path", args.markdown_path])
        if args.json:
            forwarded_args.append("--json")
        if args.strict:
            forwarded_args.append("--strict")
        return check_source_reconcile_gate_waiver_apply_gate.main(forwarded_args)

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

    if args.command == "inspect-remote-skill":
        forwarded_args = [args.skill, "--registry", args.registry]
        if args.channel:
            forwarded_args.extend(["--channel", args.channel])
        if args.json:
            forwarded_args.append("--json")
        return inspect_remote_skill.main(forwarded_args)

    if args.command == "smoke":
        forwarded_args = []
        if args.output_root:
            forwarded_args.extend(["--output-root", args.output_root])
        return check_market_pipeline.main(forwarded_args)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
