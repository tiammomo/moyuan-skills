#!/usr/bin/env python3
"""Smoke-check the Python market backend repository layer."""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.repository import MarketRepository


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

    shutil.rmtree(local_target_root, ignore_errors=True)

    print(
        "Python market backend check passed for "
        f"{len(repository.get_all_skills())} skill summary record(s), "
        f"{len(bundles)} bundle(s), and "
        f"{len(docs_catalog.get('skill_docs', []))} skill doc record(s), "
        "plus local install, update, remove, and state jobs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
