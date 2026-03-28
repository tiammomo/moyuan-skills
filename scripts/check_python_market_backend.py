#!/usr/bin/env python3
"""Smoke-check the Python market backend repository layer."""

from __future__ import annotations

import contextlib
import http.server
import json
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.repository import MarketRepository


def run_python(command: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, *command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(command)}\n"
            f"{result.stdout.strip()}\n{result.stderr.strip()}".strip()
        )


@contextlib.contextmanager
def serve_directory(directory: Path):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format: str, *args) -> None:  # noqa: A003 - stdlib signature
            return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        host, port = probe.getsockname()

    server = http.server.ThreadingHTTPServer((host, port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def wait_for_job(client: TestClient, job_id: str, timeout_seconds: float = 20.0) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = client.get(f"/api/v1/local/jobs/{job_id}")
        if response.status_code != 200:
            raise RuntimeError(f"job lookup failed for {job_id}: {response.status_code} {response.text}")
        payload = response.json()
        if payload.get("status") in {"succeeded", "failed"}:
            return payload
        time.sleep(0.2)
    raise RuntimeError(f"timed out while waiting for job {job_id}")


def main() -> int:
    repository = MarketRepository()
    client = TestClient(app)

    index = repository.get_market_index()
    if "channels" not in index:
        print("ERROR: market index must expose channels")
        return 1

    stable = repository.get_channel_skills("stable")
    if not stable.get("skills"):
        print("ERROR: stable channel should expose at least one skill")
        return 1

    release_note = repository.get_skill_detail("release-note-writer")
    if not release_note:
        print("ERROR: release-note-writer detail payload should exist")
        return 1
    if not release_note.get("manifest") or not release_note.get("install_spec") or not release_note.get("doc_markdown"):
        print("ERROR: release-note-writer detail payload should include manifest, install spec, and markdown doc")
        return 1

    bundles = repository.list_bundles()
    if len(bundles) < 1:
        print("ERROR: backend bundle listing should expose at least one bundle")
        return 1

    release_bundle = repository.get_bundle("release-engineering-starter")
    if not release_bundle or len(release_bundle.get("skills", [])) < 3:
        print("ERROR: release-engineering-starter should expose related skills through the backend repository")
        return 1

    docs_catalog = repository.get_docs_catalog()
    if not docs_catalog.get("skill_docs") or not docs_catalog.get("teaching_docs") or not docs_catalog.get("project_docs"):
        print("ERROR: docs catalog should include skill docs, teaching docs, and project docs")
        return 1
    expected_doc_count = (
        len(docs_catalog.get("skill_docs", []))
        + len(docs_catalog.get("teaching_docs", []))
        + len(docs_catalog.get("project_docs", []))
    )
    if len(docs_catalog.get("all_docs", [])) != expected_doc_count:
        print("ERROR: docs catalog all_docs should match the combined doc-family counts")
        return 1

    first_teaching = docs_catalog["teaching_docs"][0]["id"]
    teaching_doc = repository.get_teaching_doc(first_teaching)
    if not teaching_doc or not teaching_doc.get("markdown"):
        print("ERROR: backend should expose teaching doc content for catalog entries")
        return 1

    project_doc = repository.get_project_doc("frontend-backend-integration")
    if not project_doc or not project_doc.get("markdown"):
        print("ERROR: backend should expose project doc content for known project docs")
        return 1

    leaked_internal_doc = repository.get_project_doc("frontend-project-docs-iteration")
    if leaked_internal_doc is not None:
        print("ERROR: temporary iteration notes should not leak through the project docs API")
        return 1

    local_target_root = ROOT / "dist" / "backend-api-check"
    if local_target_root.exists():
        shutil.rmtree(local_target_root)
    local_registry_root = ROOT / "dist" / "backend-api-check-registry"
    if local_registry_root.exists():
        shutil.rmtree(local_registry_root)

    skill_response = client.post(
        "/api/v1/local/skills/install",
        json={
            "name": "release-note-writer",
            "target_root": str(local_target_root / "skills"),
            "dry_run": False,
        },
    )
    if skill_response.status_code != 202:
        print(f"ERROR: backend local skill install should return 202, got {skill_response.status_code}")
        return 1
    skill_job = wait_for_job(client, skill_response.json()["job_id"])
    if skill_job.get("status") != "succeeded":
        print("ERROR: backend local skill install job should succeed")
        print(skill_job.get("stdout", ""))
        print(skill_job.get("stderr", ""))
        return 1
    expected_entrypoint = local_target_root / "skills" / "release-note-writer" / "SKILL.md"
    if not expected_entrypoint.is_file():
        print(f"ERROR: expected installed skill entrypoint is missing: {expected_entrypoint}")
        return 1

    bundle_response = client.post(
        "/api/v1/local/bundles/install",
        json={
            "bundle_id": "release-engineering-starter",
            "target_root": str(local_target_root / "bundles"),
            "market_dir": "dist/market",
            "dry_run": False,
        },
    )
    if bundle_response.status_code != 202:
        print(f"ERROR: backend local bundle install should return 202, got {bundle_response.status_code}")
        return 1
    bundle_job = wait_for_job(client, bundle_response.json()["job_id"])
    if bundle_job.get("status") != "succeeded":
        print("ERROR: backend local bundle install job should succeed")
        print(bundle_job.get("stdout", ""))
        print(bundle_job.get("stderr", ""))
        return 1
    expected_bundle_report = local_target_root / "bundles" / "bundle-reports" / "release-engineering-starter.json"
    if not expected_bundle_report.is_file():
        print(f"ERROR: expected bundle report is missing: {expected_bundle_report}")
        return 1

    skill_state_response = client.get(
        "/api/v1/local/state",
        params={"target_root": str(local_target_root / "skills")},
    )
    if skill_state_response.status_code != 200:
        print(f"ERROR: backend local state should return 200, got {skill_state_response.status_code}")
        return 1
    skill_state = skill_state_response.json()
    if skill_state.get("installed_count") != 1 or skill_state.get("bundle_count") != 0:
        print("ERROR: backend local state should reflect the installed standalone skill")
        return 1

    baseline_state_response = client.get(
        "/api/v1/local/state/baseline",
        params={"target_root": str(local_target_root / "skills")},
    )
    if baseline_state_response.status_code != 200:
        print(f"ERROR: backend local baseline state should return 200, got {baseline_state_response.status_code}")
        return 1
    baseline_state = baseline_state_response.json()
    if baseline_state.get("baseline_exists"):
        print("ERROR: backend baseline state should start empty before the first promotion")
        return 1

    baseline_promote_response = client.post(
        "/api/v1/local/state/baseline/promote",
        json={
            "target_root": str(local_target_root / "skills"),
            "scope": "backend-smoke",
        },
    )
    if baseline_promote_response.status_code != 202:
        print(
            "ERROR: backend baseline promotion should return 202, "
            f"got {baseline_promote_response.status_code}"
        )
        return 1
    baseline_promote_job = wait_for_job(client, baseline_promote_response.json()["job_id"])
    if baseline_promote_job.get("status") != "succeeded":
        print("ERROR: backend baseline promotion job should succeed")
        print(baseline_promote_job.get("stdout", ""))
        print(baseline_promote_job.get("stderr", ""))
        return 1

    baseline_state_after_response = client.get(
        "/api/v1/local/state/baseline",
        params={"target_root": str(local_target_root / "skills")},
    )
    if baseline_state_after_response.status_code != 200:
        print(
            "ERROR: backend local baseline state after promotion should return 200, "
            f"got {baseline_state_after_response.status_code}"
        )
        return 1
    baseline_state_after = baseline_state_after_response.json()
    if not baseline_state_after.get("baseline_exists") or baseline_state_after.get("history_entry_count") != 1:
        print("ERROR: backend baseline state should expose the first retained history entry after promotion")
        return 1
    if baseline_state_after.get("current_baseline", {}).get("summary", {}).get("installed_count") != 1:
        print("ERROR: backend baseline state should surface the captured installed-skill count")
        return 1

    governance_state_response = client.get(
        "/api/v1/local/state/governance",
        params={"target_root": str(local_target_root / "skills")},
    )
    if governance_state_response.status_code != 200:
        print(
            "ERROR: backend local governance state should return 200, "
            f"got {governance_state_response.status_code}"
        )
        return 1
    governance_state = governance_state_response.json()
    if not governance_state.get("history_exists") or governance_state.get("summary_exists"):
        print("ERROR: backend governance state should detect retained history before the first refresh summary exists")
        return 1
    if governance_state.get("profile_counts", {}).get("source_reconcile_policies", {}).get("count", 0) < 1:
        print("ERROR: backend governance state should surface reusable source-reconcile policy counts")
        return 1

    governance_refresh_response = client.post(
        "/api/v1/local/state/governance/refresh",
        json={
            "target_root": str(local_target_root / "skills"),
            "policy": "source-reconcile-review-handoff",
            "scope": "backend-smoke",
        },
    )
    if governance_refresh_response.status_code != 202:
        print(
            "ERROR: backend governance refresh should return 202, "
            f"got {governance_refresh_response.status_code}"
        )
        return 1
    governance_refresh_job = wait_for_job(client, governance_refresh_response.json()["job_id"])
    if governance_refresh_job.get("status") != "succeeded":
        print("ERROR: backend governance refresh job should succeed")
        print(governance_refresh_job.get("stdout", ""))
        print(governance_refresh_job.get("stderr", ""))
        return 1
    governance_refresh_payload = json.loads(governance_refresh_job.get("stdout", "{}"))
    if governance_refresh_payload.get("gate", {}).get("policy_id") != "source-reconcile-review-handoff":
        print("ERROR: backend governance refresh should use the requested review-handoff policy")
        return 1

    governance_state_after_response = client.get(
        "/api/v1/local/state/governance",
        params={"target_root": str(local_target_root / "skills")},
    )
    if governance_state_after_response.status_code != 200:
        print(
            "ERROR: backend governance state after refresh should return 200, "
            f"got {governance_state_after_response.status_code}"
        )
        return 1
    governance_state_after = governance_state_after_response.json()
    if not governance_state_after.get("summary_exists"):
        print("ERROR: backend governance state should expose the refreshed governance summary")
        return 1
    if governance_state_after.get("latest_summary", {}).get("gate", {}).get("policy_id") != "source-reconcile-review-handoff":
        print("ERROR: backend governance state should surface the latest refreshed governance policy")
        return 1

    waiver_apply_state_response = client.get(
        "/api/v1/local/state/governance/waiver-apply",
        params={"target_root": str(local_target_root / "skills")},
    )
    if waiver_apply_state_response.status_code != 200:
        print(
            "ERROR: backend waiver/apply handoff state should return 200, "
            f"got {waiver_apply_state_response.status_code}"
        )
        return 1
    waiver_apply_state = waiver_apply_state_response.json()
    if not waiver_apply_state.get("can_prepare") or waiver_apply_state.get("report_summary_exists"):
        print("ERROR: backend waiver/apply handoff state should be prepare-ready before the first handoff refresh")
        return 1
    waiver_apply_write_handoff = waiver_apply_state.get("write_handoff", {})
    waiver_apply_evidence = waiver_apply_write_handoff.get("evidence", {})
    waiver_apply_audit = waiver_apply_state.get("approval_audit", {})
    if not waiver_apply_write_handoff.get("approval_label") or not waiver_apply_write_handoff.get("approval_help"):
        print("ERROR: backend waiver/apply handoff state should expose approval capture guidance before prepare")
        return 1
    if not waiver_apply_evidence.get("title") or not isinstance(waiver_apply_evidence.get("entries"), list):
        print("ERROR: backend waiver/apply handoff state should expose an evidence pack before prepare")
        return 1
    if waiver_apply_audit.get("history_count") != 0:
        print("ERROR: backend waiver/apply approval audit should start empty before any approval record is captured")
        return 1

    waiver_apply_prepare_response = client.post(
        "/api/v1/local/state/governance/waiver-apply/prepare",
        json={
            "target_root": str(local_target_root / "skills"),
            "scope": "backend-smoke",
        },
    )
    if waiver_apply_prepare_response.status_code != 202:
        print(
            "ERROR: backend waiver/apply handoff prepare should return 202, "
            f"got {waiver_apply_prepare_response.status_code}"
        )
        return 1
    waiver_apply_prepare_job = wait_for_job(client, waiver_apply_prepare_response.json()["job_id"])
    if waiver_apply_prepare_job.get("status") != "succeeded":
        print("ERROR: backend waiver/apply handoff prepare job should succeed")
        print(waiver_apply_prepare_job.get("stdout", ""))
        print(waiver_apply_prepare_job.get("stderr", ""))
        return 1
    waiver_apply_prepare_payload = json.loads(waiver_apply_prepare_job.get("stdout", "{}"))
    if not waiver_apply_prepare_payload.get("apply_summary_path") or not waiver_apply_prepare_payload.get("report_state"):
        print("ERROR: backend waiver/apply handoff prepare should emit a report summary payload")
        return 1

    waiver_apply_state_after_response = client.get(
        "/api/v1/local/state/governance/waiver-apply",
        params={"target_root": str(local_target_root / "skills")},
    )
    if waiver_apply_state_after_response.status_code != 200:
        print(
            "ERROR: backend waiver/apply handoff state after prepare should return 200, "
            f"got {waiver_apply_state_after_response.status_code}"
        )
        return 1
    waiver_apply_state_after = waiver_apply_state_after_response.json()
    if not waiver_apply_state_after.get("report_summary_exists"):
        print("ERROR: backend waiver/apply handoff state should expose the prepared report summary")
        return 1
    if not waiver_apply_state_after.get("latest_report", {}).get("apply", {}).get("summary_path"):
        print("ERROR: backend waiver/apply handoff state should surface the latest apply summary metadata")
        return 1
    waiver_apply_write_handoff_after = waiver_apply_state_after.get("write_handoff", {})
    waiver_apply_evidence_after = waiver_apply_write_handoff_after.get("evidence", {})
    if not waiver_apply_write_handoff_after.get("write_command") or not waiver_apply_write_handoff_after.get(
        "verify_command"
    ):
        print("ERROR: backend waiver/apply handoff state should expose CLI write and verify commands after prepare")
        return 1
    if not waiver_apply_evidence_after.get("summary") or not waiver_apply_evidence_after.get("follow_ups"):
        print("ERROR: backend waiver/apply handoff state should expose evidence guidance after prepare")
        return 1

    waiver_apply_stage_response = client.post(
        "/api/v1/local/state/governance/waiver-apply/stage",
        json={
            "target_root": str(local_target_root / "skills"),
            "scope": "backend-smoke",
        },
    )
    if waiver_apply_stage_response.status_code != 202:
        print(
            "ERROR: backend waiver/apply handoff stage should return 202, "
            f"got {waiver_apply_stage_response.status_code}"
        )
        return 1
    waiver_apply_stage_job = wait_for_job(client, waiver_apply_stage_response.json()["job_id"])
    if waiver_apply_stage_job.get("status") != "succeeded":
        print("ERROR: backend waiver/apply handoff stage job should succeed")
        print(waiver_apply_stage_job.get("stdout", ""))
        print(waiver_apply_stage_job.get("stderr", ""))
        return 1
    waiver_apply_stage_payload = json.loads(waiver_apply_stage_job.get("stdout", "{}"))
    if not waiver_apply_stage_payload.get("apply_execution", {}).get("available"):
        print("ERROR: backend waiver/apply handoff stage should emit execution metadata")
        return 1

    waiver_apply_state_ready_response = client.get(
        "/api/v1/local/state/governance/waiver-apply",
        params={"target_root": str(local_target_root / "skills")},
    )
    if waiver_apply_state_ready_response.status_code != 200:
        print(
            "ERROR: backend waiver/apply handoff state after stage should return 200, "
            f"got {waiver_apply_state_ready_response.status_code}"
        )
        return 1
    waiver_apply_state_ready = waiver_apply_state_ready_response.json()
    if not waiver_apply_state_ready.get("write_handoff", {}).get("approval_enabled"):
        print("ERROR: backend waiver/apply handoff state after stage should enable persisted approval capture")
        return 1

    approval_note = "backend smoke approval record"
    waiver_apply_approval_response = client.post(
        "/api/v1/local/state/governance/waiver-apply/approval",
        json={
            "target_root": str(local_target_root / "skills"),
            "scope": "backend-smoke",
            "note": approval_note,
        },
    )
    if waiver_apply_approval_response.status_code != 200:
        print(
            "ERROR: backend waiver/apply approval capture should return 200, "
            f"got {waiver_apply_approval_response.status_code}"
        )
        return 1
    waiver_apply_approval_payload = waiver_apply_approval_response.json()
    if not waiver_apply_approval_payload.get("captured") or not waiver_apply_approval_payload.get("audit", {}).get(
        "current_record"
    ):
        print("ERROR: backend waiver/apply approval capture should persist a current audit record")
        return 1
    if waiver_apply_approval_payload.get("audit", {}).get("current_record", {}).get("note") != approval_note:
        print("ERROR: backend waiver/apply approval capture should keep the operator note in the audit record")
        return 1

    waiver_apply_state_approved_response = client.get(
        "/api/v1/local/state/governance/waiver-apply",
        params={"target_root": str(local_target_root / "skills")},
    )
    if waiver_apply_state_approved_response.status_code != 200:
        print(
            "ERROR: backend waiver/apply handoff state after approval capture should return 200, "
            f"got {waiver_apply_state_approved_response.status_code}"
        )
        return 1
    waiver_apply_state_approved = waiver_apply_state_approved_response.json()
    approval_audit_after = waiver_apply_state_approved.get("approval_audit", {})
    if approval_audit_after.get("history_count", 0) < 1:
        print("ERROR: backend waiver/apply approval audit should expose persisted history after approval capture")
        return 1
    if approval_audit_after.get("state") != "active":
        print("ERROR: backend waiver/apply approval audit should mark the latest approval as current")
        return 1

    bundle_state_response = client.get(
        "/api/v1/local/state",
        params={"target_root": str(local_target_root / "bundles")},
    )
    if bundle_state_response.status_code != 200:
        print(f"ERROR: backend bundle state should return 200, got {bundle_state_response.status_code}")
        return 1
    bundle_state = bundle_state_response.json()
    if bundle_state.get("bundle_count") != 1 or bundle_state.get("installed_count", 0) < 1:
        print("ERROR: backend local state should reflect the installed bundle and its managed skills")
        return 1

    skill_update_response = client.post(
        "/api/v1/local/skills/update",
        json={
            "skill": "release-note-writer",
            "target_root": str(local_target_root / "skills"),
            "dry_run": True,
        },
    )
    if skill_update_response.status_code != 202:
        print(f"ERROR: backend local skill update should return 202, got {skill_update_response.status_code}")
        return 1
    skill_update_job = wait_for_job(client, skill_update_response.json()["job_id"])
    if skill_update_job.get("status") != "succeeded":
        print("ERROR: backend local skill update dry-run job should succeed")
        print(skill_update_job.get("stdout", ""))
        print(skill_update_job.get("stderr", ""))
        return 1

    bundle_update_response = client.post(
        "/api/v1/local/bundles/update",
        json={
            "bundle_id": "release-engineering-starter",
            "target_root": str(local_target_root / "bundles"),
            "market_dir": "dist/market",
            "dry_run": True,
        },
    )
    if bundle_update_response.status_code != 202:
        print(f"ERROR: backend local bundle update should return 202, got {bundle_update_response.status_code}")
        return 1
    bundle_update_job = wait_for_job(client, bundle_update_response.json()["job_id"])
    if bundle_update_job.get("status") != "succeeded":
        print("ERROR: backend local bundle update dry-run job should succeed")
        print(bundle_update_job.get("stdout", ""))
        print(bundle_update_job.get("stderr", ""))
        return 1

    skill_remove_response = client.post(
        "/api/v1/local/skills/remove",
        json={
            "skill": "release-note-writer",
            "target_root": str(local_target_root / "skills"),
            "dry_run": False,
        },
    )
    if skill_remove_response.status_code != 202:
        print(f"ERROR: backend local skill remove should return 202, got {skill_remove_response.status_code}")
        return 1
    skill_remove_job = wait_for_job(client, skill_remove_response.json()["job_id"])
    if skill_remove_job.get("status") != "succeeded":
        print("ERROR: backend local skill remove job should succeed")
        print(skill_remove_job.get("stdout", ""))
        print(skill_remove_job.get("stderr", ""))
        return 1
    if expected_entrypoint.exists():
        print(f"ERROR: removed skill entrypoint should no longer exist: {expected_entrypoint}")
        return 1

    removed_skill_state = client.get(
        "/api/v1/local/state",
        params={"target_root": str(local_target_root / "skills")},
    ).json()
    if removed_skill_state.get("installed_count") != 0:
        print("ERROR: backend local state should show zero installed skills after removal")
        return 1

    bundle_remove_response = client.post(
        "/api/v1/local/bundles/remove",
        json={
            "bundle_id": "release-engineering-starter",
            "target_root": str(local_target_root / "bundles"),
            "dry_run": False,
        },
    )
    if bundle_remove_response.status_code != 202:
        print(f"ERROR: backend local bundle remove should return 202, got {bundle_remove_response.status_code}")
        return 1
    bundle_remove_job = wait_for_job(client, bundle_remove_response.json()["job_id"])
    if bundle_remove_job.get("status") != "succeeded":
        print("ERROR: backend local bundle remove job should succeed")
        print(bundle_remove_job.get("stdout", ""))
        print(bundle_remove_job.get("stderr", ""))
        return 1
    if expected_bundle_report.exists():
        print(f"ERROR: removed bundle report should no longer exist: {expected_bundle_report}")
        return 1

    removed_bundle_state = client.get(
        "/api/v1/local/state",
        params={"target_root": str(local_target_root / "bundles")},
    ).json()
    if removed_bundle_state.get("bundle_count") != 0:
        print("ERROR: backend local state should show zero installed bundles after removal")
        return 1

    run_python(["scripts/build_market_registry.py", "--output-dir", "dist/backend-api-check-registry"])
    with serve_directory(local_registry_root) as registry_url:
        remote_skill_response = client.post(
            "/api/v1/registry/skills/install",
            json={
                "skill": "moyuan.release-note-writer",
                "registry_url": registry_url,
                "target_root": str(local_target_root / "remote-skills"),
                "cache_root": str(local_target_root / "remote-cache"),
                "dry_run": False,
            },
        )
        if remote_skill_response.status_code != 202:
            print(
                "ERROR: backend remote skill install should return 202, "
                f"got {remote_skill_response.status_code}"
            )
            return 1
        remote_skill_job = wait_for_job(client, remote_skill_response.json()["job_id"])
        if remote_skill_job.get("status") != "succeeded":
            print("ERROR: backend remote skill install job should succeed")
            print(remote_skill_job.get("stdout", ""))
            print(remote_skill_job.get("stderr", ""))
            return 1
        remote_entrypoint = local_target_root / "remote-skills" / "release-note-writer" / "SKILL.md"
        if not remote_entrypoint.is_file():
            print(f"ERROR: expected remote-installed skill entrypoint is missing: {remote_entrypoint}")
            return 1

        remote_bundle_response = client.post(
            "/api/v1/registry/bundles/install",
            json={
                "bundle_id": "release-engineering-starter",
                "registry_url": registry_url,
                "target_root": str(local_target_root / "remote-bundles"),
                "cache_root": str(local_target_root / "remote-cache"),
                "dry_run": False,
            },
        )
        if remote_bundle_response.status_code != 202:
            print(
                "ERROR: backend remote bundle install should return 202, "
                f"got {remote_bundle_response.status_code}"
            )
            return 1
        remote_bundle_job = wait_for_job(client, remote_bundle_response.json()["job_id"])
        if remote_bundle_job.get("status") != "succeeded":
            print("ERROR: backend remote bundle install job should succeed")
            print(remote_bundle_job.get("stdout", ""))
            print(remote_bundle_job.get("stderr", ""))
            return 1
        remote_bundle_report = local_target_root / "remote-bundles" / "bundle-reports" / "release-engineering-starter.json"
        if not remote_bundle_report.is_file():
            print(f"ERROR: expected remote-installed bundle report is missing: {remote_bundle_report}")
            return 1

        cleanup_target_root = local_target_root / "cleanup-target"
        cleanup_cache_root = local_target_root / "cleanup-cache"
        (cleanup_target_root / "partial").mkdir(parents=True, exist_ok=True)
        (cleanup_cache_root / "staged").mkdir(parents=True, exist_ok=True)
        cleanup_response = client.post(
            "/api/v1/registry/cleanup",
            json={
                "target_root": str(cleanup_target_root),
                "cache_root": str(cleanup_cache_root),
                "scope": "backend-smoke",
            },
        )
        if cleanup_response.status_code != 202:
            print(
                "ERROR: backend remote cleanup should return 202, "
                f"got {cleanup_response.status_code}"
            )
            return 1
        cleanup_job = wait_for_job(client, cleanup_response.json()["job_id"])
        if cleanup_job.get("status") != "succeeded":
            print("ERROR: backend remote cleanup job should succeed")
            print(cleanup_job.get("stdout", ""))
            print(cleanup_job.get("stderr", ""))
            return 1
        if cleanup_target_root.exists() or cleanup_cache_root.exists():
            print("ERROR: backend remote cleanup job should remove target and cache roots")
            return 1

        doctor_target_root = local_target_root / "doctor-repair"
        doctor_report_path = doctor_target_root / "bundle-reports" / "stale-bundle.json"
        (doctor_target_root / "orphan-skill").mkdir(parents=True, exist_ok=True)
        doctor_report_path.parent.mkdir(parents=True, exist_ok=True)
        doctor_report_path.write_text(
            json.dumps(
                {
                    "bundle_id": "stale-bundle",
                    "title": "Stale bundle",
                    "generated_at": "2026-03-27T00:00:00+00:00",
                    "results": [
                        {
                            "skill_id": "moyuan.release-note-writer",
                            "status": "installed",
                        }
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        doctor_response = client.post(
            "/api/v1/local/state/doctor",
            json={
                "target_root": str(doctor_target_root),
                "scope": "backend-smoke",
            },
        )
        if doctor_response.status_code != 202:
            print(
                "ERROR: backend installed-state doctor should return 202, "
                f"got {doctor_response.status_code}"
            )
            return 1
        doctor_job = wait_for_job(client, doctor_response.json()["job_id"])
        if doctor_job.get("status") != "succeeded":
            print("ERROR: backend installed-state doctor job should succeed")
            print(doctor_job.get("stdout", ""))
            print(doctor_job.get("stderr", ""))
            return 1
        doctor_payload = json.loads(doctor_job.get("stdout", "{}"))
        if doctor_payload.get("summary", {}).get("doctor_finding_count", 0) < 2:
            print("ERROR: backend installed-state doctor should surface drift findings")
            return 1
        if doctor_payload.get("summary", {}).get("repairable_finding_count", 0) < 2:
            print("ERROR: backend installed-state doctor should expose repairable findings in the snapshot")
            return 1

        repair_response = client.post(
            "/api/v1/local/state/repair",
            json={
                "target_root": str(doctor_target_root),
                "scope": "backend-smoke",
            },
        )
        if repair_response.status_code != 202:
            print(
                "ERROR: backend installed-state repair should return 202, "
                f"got {repair_response.status_code}"
            )
            return 1
        repair_job = wait_for_job(client, repair_response.json()["job_id"])
        if repair_job.get("status") != "succeeded":
            print("ERROR: backend installed-state repair job should succeed")
            print(repair_job.get("stdout", ""))
            print(repair_job.get("stderr", ""))
            return 1
        repair_payload = json.loads(repair_job.get("stdout", "{}"))
        if repair_payload.get("applied_count") != 2:
            print("ERROR: backend installed-state repair should remove the low-risk drift artifacts")
            return 1
        if (doctor_target_root / "orphan-skill").exists() or doctor_report_path.exists():
            print("ERROR: backend installed-state repair should remove orphan directories and stale bundle reports")
            return 1

        repaired_doctor_response = client.post(
            "/api/v1/local/state/doctor",
            json={
                "target_root": str(doctor_target_root),
                "scope": "backend-smoke",
            },
        )
        if repaired_doctor_response.status_code != 202:
            print(
                "ERROR: backend installed-state doctor rerun should return 202, "
                f"got {repaired_doctor_response.status_code}"
            )
            return 1
        repaired_doctor_job = wait_for_job(client, repaired_doctor_response.json()["job_id"])
        if repaired_doctor_job.get("status") != "succeeded":
            print("ERROR: backend installed-state doctor rerun should succeed")
            print(repaired_doctor_job.get("stdout", ""))
            print(repaired_doctor_job.get("stderr", ""))
            return 1
        repaired_doctor_payload = json.loads(repaired_doctor_job.get("stdout", "{}"))
        if repaired_doctor_payload.get("summary", {}).get("doctor_finding_count") != 0:
            print("ERROR: backend installed-state doctor should report a healthy target root after repair")
            return 1

    shutil.rmtree(local_target_root, ignore_errors=True)
    shutil.rmtree(local_registry_root, ignore_errors=True)

    print(
        "Python market backend check passed for "
        f"{len(repository.get_all_skills())} skill summary record(s), "
        f"{len(bundles)} bundle(s), and "
        f"{len(docs_catalog.get('skill_docs', []))} skill doc record(s), "
        "plus local, remote, doctor, repair, baseline, governance, waiver/apply handoff, and cleanup lifecycle jobs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
