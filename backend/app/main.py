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

    job = job_store.create_subprocess_job(
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

    job = job_store.create_subprocess_job(
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


@app.get("/api/v1/local/jobs/{job_id}")
def local_job_detail(job_id: str) -> dict:
    payload = job_store.get_job(job_id)
    if not payload:
        raise _not_found("job", job_id)
    return payload


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
