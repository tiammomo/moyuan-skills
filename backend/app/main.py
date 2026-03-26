from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .repository import MarketRepository, VALID_CHANNELS


settings = get_settings()
repository = MarketRepository(settings)

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


@app.get("/api/v1/docs/catalog")
def docs_catalog() -> dict:
    return repository.get_docs_catalog()
