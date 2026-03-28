from __future__ import annotations

import sys
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import get_settings
from .jobs import LocalJobStore, resolve_local_target_path
from .repository import MarketRepository, VALID_CHANNELS


settings = get_settings()
repository = MarketRepository(settings)
job_store = LocalJobStore(settings)

app = FastAPI(
    title="Moyuan Skills Market API",
    version="0.1.0",
    description="Python backend for serving the existing Moyuan skills market frontend with real repo-backed data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins) or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _not_found(kind: str, identifier: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{kind} not found: {identifier}")


class LocalSkillInstallRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Skill name used in the market routes.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the local install lifecycle.",
    )
    dry_run: bool = Field(default=False, description="Resolve the install through the backend without extracting files.")


class LocalBundleInstallRequest(BaseModel):
    bundle_id: str = Field(..., min_length=1, description="Bundle id used in the market routes.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the local bundle install lifecycle.",
    )
    market_dir: str | None = Field(
        default="dist/market",
        description="Generated market artifact directory used by the bundle installer.",
    )
    dry_run: bool = Field(default=False, description="Resolve the bundle install through the backend without extracting files.")


class LocalSkillUpdateRequest(BaseModel):
    skill: str = Field(..., min_length=1, description="Installed skill id, name, or install target.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the local install lifecycle.",
    )
    index: str | None = Field(
        default="dist/market/channels/stable.json",
        description="Channel index JSON used to resolve the latest install spec.",
    )
    dry_run: bool = Field(default=False, description="Resolve the update without extracting files.")


class LocalSkillRemoveRequest(BaseModel):
    skill: str = Field(..., min_length=1, description="Installed skill id, name, or install target.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the local install lifecycle.",
    )
    dry_run: bool = Field(default=False, description="Show the removal plan without deleting files.")


class LocalBundleUpdateRequest(BaseModel):
    bundle_id: str = Field(..., min_length=1, description="Bundle id or title.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the local bundle lifecycle.",
    )
    market_dir: str | None = Field(
        default="dist/market",
        description="Generated market artifact directory used by the bundle updater.",
    )
    org_policy: str | None = Field(
        default=None,
        description="Optional org market policy JSON file.",
    )
    dry_run: bool = Field(default=False, description="Resolve the bundle update without extracting files.")


class LocalBundleRemoveRequest(BaseModel):
    bundle_id: str = Field(..., min_length=1, description="Bundle id or title.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the local bundle lifecycle.",
    )
    dry_run: bool = Field(default=False, description="Show the removal plan without deleting files.")


class RemoteSkillInstallRequest(BaseModel):
    skill: str = Field(..., min_length=1, description="Remote skill id or skill name.")
    registry_url: str = Field(..., min_length=8, description="Hosted registry base URL or registry.json URL.")
    channel: str = Field(default="stable", description="Remote channel used to resolve the skill install spec.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the remote install lifecycle.",
    )
    cache_root: str | None = Field(
        default="dist/backend-remote-cache",
        description="Cache directory for downloaded remote registry artifacts.",
    )
    dry_run: bool = Field(default=False, description="Resolve the remote install without extracting files.")


class RemoteBundleInstallRequest(BaseModel):
    bundle_id: str = Field(..., min_length=1, description="Remote bundle id or title.")
    registry_url: str = Field(..., min_length=8, description="Hosted registry base URL or registry.json URL.")
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Target directory for the remote bundle lifecycle.",
    )
    cache_root: str | None = Field(
        default="dist/backend-remote-cache",
        description="Cache directory for downloaded remote registry artifacts.",
    )
    dry_run: bool = Field(default=False, description="Resolve the remote bundle install without extracting files.")


class RemoteCleanupRequest(BaseModel):
    target_root: str | None = Field(
        default=None,
        description="Installed target directory to clean up after a failed or abandoned remote run.",
    )
    cache_root: str | None = Field(
        default=None,
        description="Remote cache directory to clear after a failed or abandoned remote run.",
    )
    scope: str = Field(default="remote-registry-execution", description="UI scope label for the cleanup action.")


class RemoteRollbackRequest(BaseModel):
    target_root: str = Field(
        ...,
        min_length=3,
        description="Dedicated remote target directory to reset after a failed or abandoned frontend registry run.",
    )
    cache_root: str | None = Field(
        default=None,
        description="Optional dedicated remote cache directory to reset alongside the target root.",
    )
    scope: str = Field(default="remote-registry-execution", description="UI scope label for the rollback action.")


class LocalStateDoctorRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory to inspect with the doctor snapshot.",
    )
    scope: str = Field(default="installed-state-doctor", description="UI scope label for the doctor action.")


class LocalStateRepairRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory to repair when low-risk drift is found.",
    )
    dry_run: bool = Field(default=False, description="Only print the low-risk repair plan without changing files.")
    scope: str = Field(default="installed-state-repair", description="UI scope label for the repair action.")


class LocalStateBaselinePromoteRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory to snapshot into the promoted baseline history.",
    )
    scope: str = Field(default="installed-state-baseline", description="UI scope label for the baseline action.")


class LocalStateGovernanceRefreshRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory whose retained baseline history should be summarized for governance review.",
    )
    policy: str = Field(
        default="source-reconcile-review-handoff",
        description="Reusable governance policy id used to build the first review-oriented summary.",
    )
    scope: str = Field(default="installed-state-governance", description="UI scope label for the governance action.")


class LocalStateGovernanceWaiverApplyPrepareRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory whose retained governance summary should drive the first waiver/apply handoff pack.",
    )
    scope: str = Field(
        default="installed-state-governance-waiver-apply",
        description="UI scope label for the waiver/apply prepare action.",
    )


class LocalStateGovernanceWaiverApplyStageRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory whose prepared waiver/apply pack should be staged into the safe mirror root.",
    )
    scope: str = Field(
        default="installed-state-governance-waiver-apply",
        description="UI scope label for the waiver/apply stage action.",
    )


class LocalStateGovernanceWaiverApplyVerifyRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory whose staged waiver/apply results should be re-verified.",
    )
    scope: str = Field(
        default="installed-state-governance-waiver-apply",
        description="UI scope label for the waiver/apply verify action.",
    )


class LocalStateGovernanceWaiverApplyApprovalRequest(BaseModel):
    target_root: str | None = Field(
        default="dist/backend-installed-market",
        description="Installed target directory whose current write handoff should receive a persisted approval record.",
    )
    note: str = Field(
        default="",
        max_length=400,
        description="Optional operator note stored with the persisted approval record.",
    )
    scope: str = Field(
        default="installed-state-governance-waiver-apply",
        description="UI scope label for the waiver/apply approval capture action.",
    )


def _create_local_job(
    *,
    kind: str,
    command: list[str],
    summary: dict,
    artifacts: dict,
    request_payload: dict,
) -> dict:
    return job_store.create_subprocess_job(
        kind=kind,
        command=command,
        summary=summary,
        artifacts=artifacts,
        request_payload=request_payload,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/meta/repo")
def repo_meta() -> dict:
    return repository.get_repo_snapshot()


@app.get("/api/v1/market/index")
def market_index() -> dict:
    return repository.get_market_index()


@app.get("/api/v1/market/channels/{channel}")
def channel_index(channel: str) -> dict:
    if channel not in VALID_CHANNELS:
        raise _not_found("channel", channel)
    return repository.get_channel_skills(channel)


@app.get("/api/v1/market/skills")
def market_skills(
    q: str = "",
    channel: Annotated[list[str] | None, Query()] = None,
    category: Annotated[list[str] | None, Query()] = None,
    tag: Annotated[list[str] | None, Query()] = None,
) -> dict:
    skills = repository.search_skills(
        query=q,
        channels=channel or [],
        categories=category or [],
        tags=tag or [],
    )
    return {"count": len(skills), "skills": skills}


@app.get("/api/v1/market/skills/{name}")
def skill_detail(name: str) -> dict:
    payload = repository.get_skill_detail(name)
    if not payload:
        raise _not_found("skill", name)
    return payload


@app.get("/api/v1/market/skills/{name}/install-spec")
def skill_install_spec(name: str) -> dict:
    spec = repository.get_install_spec(name)
    if not spec:
        raise _not_found("install spec", name)
    return spec


@app.get("/api/v1/market/skills/{name}/doc")
def skill_doc(name: str) -> dict:
    markdown = repository.get_skill_doc(name)
    if markdown is None:
        raise _not_found("skill doc", name)
    return {
        "name": name,
        "markdown": markdown,
        "path": f"docs/{name}.md",
    }


@app.get("/api/v1/market/categories")
def categories() -> dict:
    payload = repository.get_categories()
    return {"count": len(payload), "categories": payload}


@app.get("/api/v1/market/tags")
def tags() -> dict:
    payload = repository.get_tags()
    return {"count": len(payload), "tags": payload}


@app.get("/api/v1/market/bundles")
def bundles() -> dict:
    payload = repository.list_bundles()
    return {"count": len(payload), "bundles": payload}


@app.get("/api/v1/market/bundles/{bundle_id}")
def bundle_detail(bundle_id: str) -> dict:
    payload = repository.get_bundle(bundle_id)
    if not payload:
        raise _not_found("bundle", bundle_id)
    return payload


@app.post("/api/v1/local/skills/install", status_code=202)
def local_skill_install(request: LocalSkillInstallRequest) -> dict:
    detail = repository.get_skill_detail(request.name)
    if not detail or not detail.get("manifest"):
        raise _not_found("skill", request.name)

    manifest = detail["manifest"]
    install_spec = detail.get("install_spec")
    if not install_spec:
        raise _not_found("install spec", request.name)

    install_spec_path = settings.dist_market_root / "install" / f"{request.name}-{install_spec['version']}.json"
    if not install_spec_path.is_file():
        raise _not_found("install spec file", install_spec_path.name)

    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "install_skill.py"),
        str(install_spec_path),
        "--target-root",
        str(target_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="skill-install",
        command=command,
        summary={
            "skill_id": manifest["id"],
            "skill_name": manifest["name"],
            "title": manifest["title"],
            "version": manifest["version"],
            "channel": manifest["channel"],
            "mode": "dry-run" if request.dry_run else "install",
        },
        artifacts={
            "target_root": str(target_root),
            "install_spec": str(install_spec_path),
            "entrypoint": install_spec["entrypoint"],
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/registry/skills/install", status_code=202)
def registry_skill_install(request: RemoteSkillInstallRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    cache_root = resolve_local_target_path(settings.repo_root, request.cache_root, "dist/backend-remote-cache")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "install_remote_skill.py"),
        request.skill,
        "--registry",
        request.registry_url,
        "--channel",
        request.channel,
        "--target-root",
        str(target_root),
        "--cache-root",
        str(cache_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="registry-skill-install",
        command=command,
        summary={
            "skill": request.skill,
            "registry_url": request.registry_url,
            "channel": request.channel,
            "mode": "dry-run" if request.dry_run else "install",
        },
        artifacts={
            "target_root": str(target_root),
            "cache_root": str(cache_root),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/skills/update", status_code=202)
def local_skill_update(request: LocalSkillUpdateRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    index_path = resolve_local_target_path(settings.repo_root, request.index, "dist/market/channels/stable.json")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "update_installed_skill.py"),
        request.skill,
        "--index",
        str(index_path),
        "--target-root",
        str(target_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="skill-update",
        command=command,
        summary={
            "skill": request.skill,
            "mode": "dry-run" if request.dry_run else "update",
        },
        artifacts={
            "target_root": str(target_root),
            "index": str(index_path),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/skills/remove", status_code=202)
def local_skill_remove(request: LocalSkillRemoveRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "remove_skill.py"),
        request.skill,
        "--target-root",
        str(target_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="skill-remove",
        command=command,
        summary={
            "skill": request.skill,
            "mode": "dry-run" if request.dry_run else "remove",
        },
        artifacts={
            "target_root": str(target_root),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/bundles/install", status_code=202)
def local_bundle_install(request: LocalBundleInstallRequest) -> dict:
    detail = repository.get_bundle(request.bundle_id)
    if not detail or not detail.get("bundle"):
        raise _not_found("bundle", request.bundle_id)

    bundle = detail["bundle"]
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    market_dir = resolve_local_target_path(settings.repo_root, request.market_dir, "dist/market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "install_skill_bundle.py"),
        request.bundle_id,
        "--market-dir",
        str(market_dir),
        "--target-root",
        str(target_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="bundle-install",
        command=command,
        summary={
            "bundle_id": bundle["id"],
            "title": bundle["title"],
            "skill_count": bundle["skill_count"],
            "channels": bundle["channels"],
            "mode": "dry-run" if request.dry_run else "install",
        },
        artifacts={
            "target_root": str(target_root),
            "market_dir": str(market_dir),
            "bundle_report": str(target_root / "bundle-reports" / f"{request.bundle_id}.json"),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/registry/bundles/install", status_code=202)
def registry_bundle_install(request: RemoteBundleInstallRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    cache_root = resolve_local_target_path(settings.repo_root, request.cache_root, "dist/backend-remote-cache")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "install_remote_bundle.py"),
        request.bundle_id,
        "--registry",
        request.registry_url,
        "--target-root",
        str(target_root),
        "--cache-root",
        str(cache_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="registry-bundle-install",
        command=command,
        summary={
            "bundle_id": request.bundle_id,
            "registry_url": request.registry_url,
            "mode": "dry-run" if request.dry_run else "install",
        },
        artifacts={
            "target_root": str(target_root),
            "cache_root": str(cache_root),
            "bundle_report": str(target_root / "bundle-reports" / f"{request.bundle_id}.json"),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/registry/cleanup", status_code=202)
def registry_cleanup(request: RemoteCleanupRequest) -> dict:
    target_root = (
        resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
        if request.target_root
        else None
    )
    cache_root = (
        resolve_local_target_path(settings.repo_root, request.cache_root, "dist/backend-remote-cache")
        if request.cache_root
        else None
    )
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "cleanup_remote_install.py"),
    ]
    if target_root is not None:
        command.extend(["--target-root", str(target_root)])
    if cache_root is not None:
        command.extend(["--cache-root", str(cache_root)])

    job = _create_local_job(
        kind="registry-cleanup",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "cleanup",
        },
        artifacts={
            "target_root": str(target_root) if target_root is not None else "",
            "cache_root": str(cache_root) if cache_root is not None else "",
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/registry/rollback", status_code=202)
def registry_rollback(request: RemoteRollbackRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, request.target_root)
    cache_root = (
        resolve_local_target_path(settings.repo_root, request.cache_root, request.cache_root)
        if request.cache_root
        else None
    )
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "rollback_remote_install.py"),
        "--target-root",
        str(target_root),
    ]
    if cache_root is not None:
        command.extend(["--cache-root", str(cache_root)])

    job = _create_local_job(
        kind="registry-rollback",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "rollback",
        },
        artifacts={
            "target_root": str(target_root),
            "cache_root": str(cache_root) if cache_root is not None else "",
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/bundles/update", status_code=202)
def local_bundle_update(request: LocalBundleUpdateRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    market_dir = resolve_local_target_path(settings.repo_root, request.market_dir, "dist/market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "update_skill_bundle.py"),
        request.bundle_id,
        "--market-dir",
        str(market_dir),
        "--target-root",
        str(target_root),
    ]
    org_policy_path = None
    if request.org_policy:
        org_policy_path = resolve_local_target_path(settings.repo_root, request.org_policy, request.org_policy)
        command.extend(["--org-policy", str(org_policy_path)])
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="bundle-update",
        command=command,
        summary={
            "bundle_id": request.bundle_id,
            "mode": "dry-run" if request.dry_run else "update",
        },
        artifacts={
            "target_root": str(target_root),
            "market_dir": str(market_dir),
            "org_policy": str(org_policy_path) if org_policy_path else "",
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/bundles/remove", status_code=202)
def local_bundle_remove(request: LocalBundleRemoveRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "remove_skill_bundle.py"),
        request.bundle_id,
        "--target-root",
        str(target_root),
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="bundle-remove",
        command=command,
        summary={
            "bundle_id": request.bundle_id,
            "mode": "dry-run" if request.dry_run else "remove",
        },
        artifacts={
            "target_root": str(target_root),
            "bundle_report": str(target_root / "bundle-reports" / f"{request.bundle_id}.json"),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.get("/api/v1/local/jobs/{job_id}")
def local_job_detail(job_id: str) -> dict:
    payload = job_store.get_job(job_id)
    if not payload:
        raise _not_found("job", job_id)
    return payload


@app.get("/api/v1/local/state")
def local_state(target_root: str = "dist/backend-installed-market") -> dict:
    resolved_root = resolve_local_target_path(settings.repo_root, target_root, "dist/backend-installed-market")
    return repository.get_installed_state(resolved_root)


@app.get("/api/v1/local/state/baseline")
def local_state_baseline(target_root: str = "dist/backend-installed-market") -> dict:
    resolved_root = resolve_local_target_path(settings.repo_root, target_root, "dist/backend-installed-market")
    return repository.get_installed_baseline_state(resolved_root)


@app.get("/api/v1/local/state/governance")
def local_state_governance(target_root: str = "dist/backend-installed-market") -> dict:
    resolved_root = resolve_local_target_path(settings.repo_root, target_root, "dist/backend-installed-market")
    return repository.get_installed_governance_state(resolved_root)


@app.get("/api/v1/local/state/governance/waiver-apply")
def local_state_governance_waiver_apply(target_root: str = "dist/backend-installed-market") -> dict:
    resolved_root = resolve_local_target_path(settings.repo_root, target_root, "dist/backend-installed-market")
    return repository.get_installed_governance_waiver_apply_state(resolved_root)


@app.post("/api/v1/local/state/governance/waiver-apply/approval")
def local_state_governance_waiver_apply_approval(
    request: LocalStateGovernanceWaiverApplyApprovalRequest,
) -> dict:
    resolved_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    try:
        return repository.capture_installed_governance_waiver_apply_approval(
            resolved_root,
            note=request.note,
            scope=request.scope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/v1/local/state/doctor", status_code=202)
def local_state_doctor(request: LocalStateDoctorRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "snapshot_installed_market_state.py"),
        "--target-root",
        str(target_root),
        "--json",
    ]

    job = _create_local_job(
        kind="state-doctor",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "doctor",
        },
        artifacts={
            "target_root": str(target_root),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/state/baseline/promote", status_code=202)
def local_state_baseline_promote(request: LocalStateBaselinePromoteRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    snapshots_dir = target_root / "snapshots"
    baseline_path = snapshots_dir / "baseline.json"
    history_path = snapshots_dir / "baseline-history.json"
    archive_dir = snapshots_dir / "baseline-archive"
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "promote_installed_market_baseline.py"),
        str(baseline_path),
        "--target-root",
        str(target_root),
        "--history-path",
        str(history_path),
        "--archive-dir",
        str(archive_dir),
        "--json",
    ]

    job = _create_local_job(
        kind="state-baseline-promote",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "baseline-promote",
        },
        artifacts={
            "target_root": str(target_root),
            "baseline_path": str(baseline_path),
            "history_path": str(history_path),
            "archive_dir": str(archive_dir),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/state/governance/refresh", status_code=202)
def local_state_governance_refresh(request: LocalStateGovernanceRefreshRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    history_path = target_root / "snapshots" / "baseline-history.json"
    output_dir = target_root / "snapshots" / "governance"
    summary_path = output_dir / "governance-summary.json"
    summary_markdown_path = output_dir / "governance-summary.md"

    if not history_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Installed governance review needs a retained baseline history first. Capture a baseline before refreshing governance.",
        )

    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "refresh_installed_governance_summary.py"),
        str(history_path),
        "--target-root",
        str(target_root),
        "--output-dir",
        str(output_dir),
        "--policy",
        request.policy,
        "--json",
    ]

    job = _create_local_job(
        kind="state-governance-refresh",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "governance-refresh",
            "policy": request.policy,
        },
        artifacts={
            "target_root": str(target_root),
            "history_path": str(history_path),
            "output_dir": str(output_dir),
            "summary_path": str(summary_path),
            "summary_markdown_path": str(summary_markdown_path),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/state/governance/waiver-apply/prepare", status_code=202)
def local_state_governance_waiver_apply_prepare(request: LocalStateGovernanceWaiverApplyPrepareRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    history_path = target_root / "snapshots" / "baseline-history.json"
    governance_dir = target_root / "snapshots" / "governance"
    governance_summary_path = governance_dir / "governance-summary.json"
    output_dir = governance_dir / "waiver-apply"
    stage_dir = output_dir / "source-reconcile-gate-waiver-apply-staged-root"
    apply_summary_path = output_dir / "source-reconcile-gate-waiver-apply-summary.json"
    verify_summary_path = output_dir / "source-reconcile-gate-waiver-apply-verify-summary.json"
    report_summary_path = output_dir / "source-reconcile-gate-waiver-apply-report-summary.json"
    report_markdown_path = output_dir / "source-reconcile-gate-waiver-apply-report-summary.md"

    if not history_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply handoff needs a retained baseline history first. Capture a baseline before preparing the apply pack.",
        )
    if not governance_summary_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply handoff needs a governance summary first. Refresh governance before preparing the apply pack.",
        )

    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "report_source_reconcile_gate_waiver_apply.py"),
        str(history_path),
        "--output-dir",
        str(output_dir),
        "--target-root",
        str(target_root),
        "--stage-dir",
        str(stage_dir),
        "--json",
    ]

    job = _create_local_job(
        kind="state-governance-waiver-apply-prepare",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "governance-waiver-apply-prepare",
        },
        artifacts={
            "target_root": str(target_root),
            "history_path": str(history_path),
            "governance_summary_path": str(governance_summary_path),
            "output_dir": str(output_dir),
            "stage_dir": str(stage_dir),
            "apply_summary_path": str(apply_summary_path),
            "verify_summary_path": str(verify_summary_path),
            "report_summary_path": str(report_summary_path),
            "report_markdown_path": str(report_markdown_path),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/state/governance/waiver-apply/stage", status_code=202)
def local_state_governance_waiver_apply_stage(request: LocalStateGovernanceWaiverApplyStageRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    history_path = target_root / "snapshots" / "baseline-history.json"
    governance_dir = target_root / "snapshots" / "governance"
    governance_summary_path = governance_dir / "governance-summary.json"
    output_dir = governance_dir / "waiver-apply"
    stage_dir = output_dir / "source-reconcile-gate-waiver-apply-staged-root"
    apply_summary_path = output_dir / "source-reconcile-gate-waiver-apply-summary.json"
    apply_execute_summary_path = output_dir / "source-reconcile-gate-waiver-apply-execute-summary.json"
    verify_summary_path = output_dir / "source-reconcile-gate-waiver-apply-verify-summary.json"
    report_summary_path = output_dir / "source-reconcile-gate-waiver-apply-report-summary.json"
    report_markdown_path = output_dir / "source-reconcile-gate-waiver-apply-report-summary.md"

    if not history_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply stage needs a retained baseline history first. Capture a baseline before staging apply changes.",
        )
    if not governance_summary_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply stage needs a governance summary first. Refresh governance before staging apply changes.",
        )
    if not apply_summary_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply stage needs a prepared apply handoff pack first. Prepare the apply pack before staging changes.",
        )

    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "run_source_reconcile_gate_waiver_apply_stage.py"),
        str(history_path),
        "--output-dir",
        str(output_dir),
        "--stage-dir",
        str(stage_dir),
        "--json",
    ]

    job = _create_local_job(
        kind="state-governance-waiver-apply-stage",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "governance-waiver-apply-stage",
        },
        artifacts={
            "target_root": str(target_root),
            "history_path": str(history_path),
            "governance_summary_path": str(governance_summary_path),
            "output_dir": str(output_dir),
            "stage_dir": str(stage_dir),
            "apply_summary_path": str(apply_summary_path),
            "apply_execute_summary_path": str(apply_execute_summary_path),
            "verify_summary_path": str(verify_summary_path),
            "report_summary_path": str(report_summary_path),
            "report_markdown_path": str(report_markdown_path),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/state/governance/waiver-apply/verify", status_code=202)
def local_state_governance_waiver_apply_verify(request: LocalStateGovernanceWaiverApplyVerifyRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    history_path = target_root / "snapshots" / "baseline-history.json"
    governance_dir = target_root / "snapshots" / "governance"
    governance_summary_path = governance_dir / "governance-summary.json"
    output_dir = governance_dir / "waiver-apply"
    stage_dir = output_dir / "source-reconcile-gate-waiver-apply-staged-root"
    apply_summary_path = output_dir / "source-reconcile-gate-waiver-apply-summary.json"
    apply_execute_summary_path = output_dir / "source-reconcile-gate-waiver-apply-execute-summary.json"
    verify_summary_path = output_dir / "source-reconcile-gate-waiver-apply-verify-summary.json"
    report_summary_path = output_dir / "source-reconcile-gate-waiver-apply-report-summary.json"
    report_markdown_path = output_dir / "source-reconcile-gate-waiver-apply-report-summary.md"

    if not history_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply verification needs a retained baseline history first. Capture a baseline before verifying staged changes.",
        )
    if not governance_summary_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply verification needs a governance summary first. Refresh governance before verifying staged changes.",
        )
    if not apply_summary_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply verification needs a prepared apply handoff pack first. Prepare the apply pack before verifying staged changes.",
        )
    if not apply_execute_summary_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Waiver/apply verification needs staged or written execution records first. Stage the apply changes before running verification again.",
        )

    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "run_source_reconcile_gate_waiver_apply_verify.py"),
        str(history_path),
        "--output-dir",
        str(output_dir),
        "--stage-dir",
        str(stage_dir),
        "--apply-execute-summary-path",
        str(apply_execute_summary_path),
        "--json",
    ]

    job = _create_local_job(
        kind="state-governance-waiver-apply-verify",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "governance-waiver-apply-verify",
        },
        artifacts={
            "target_root": str(target_root),
            "history_path": str(history_path),
            "governance_summary_path": str(governance_summary_path),
            "output_dir": str(output_dir),
            "stage_dir": str(stage_dir),
            "apply_summary_path": str(apply_summary_path),
            "apply_execute_summary_path": str(apply_execute_summary_path),
            "verify_summary_path": str(verify_summary_path),
            "report_summary_path": str(report_summary_path),
            "report_markdown_path": str(report_markdown_path),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.post("/api/v1/local/state/repair", status_code=202)
def local_state_repair(request: LocalStateRepairRequest) -> dict:
    target_root = resolve_local_target_path(settings.repo_root, request.target_root, "dist/backend-installed-market")
    command = [
        sys.executable,
        str(settings.repo_root / "scripts" / "repair_installed_market_state.py"),
        "--target-root",
        str(target_root),
        "--json",
    ]
    if request.dry_run:
        command.append("--dry-run")

    job = _create_local_job(
        kind="state-repair",
        command=command,
        summary={
            "scope": request.scope,
            "mode": "repair-dry-run" if request.dry_run else "repair",
        },
        artifacts={
            "target_root": str(target_root),
        },
        request_payload=request.model_dump(),
    )
    return job


@app.get("/api/v1/docs/catalog")
def docs_catalog() -> dict:
    return repository.get_docs_catalog()


@app.get("/api/v1/docs/teaching/{doc_id}")
def teaching_doc(doc_id: str) -> dict:
    payload = repository.get_teaching_doc(doc_id)
    if not payload:
        raise _not_found("teaching doc", doc_id)
    return payload


@app.get("/api/v1/docs/project/{doc_id}")
def project_doc(doc_id: str) -> dict:
    payload = repository.get_project_doc(doc_id)
    if not payload:
        raise _not_found("project doc", doc_id)
    return payload
