from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    dist_market_root: Path
    skills_root: Path
    docs_root: Path
    teaching_root: Path
    bundles_root: Path
    cors_origins: tuple[str, ...]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    repo_root = Path(os.environ.get("MOYUAN_SKILLS_REPO_ROOT", _default_repo_root())).resolve()
    cors_env = os.environ.get("MOYUAN_SKILLS_API_CORS", "http://localhost:3000")
    cors_origins = tuple(origin.strip() for origin in cors_env.split(",") if origin.strip())
    return Settings(
        repo_root=repo_root,
        dist_market_root=repo_root / "dist" / "market",
        skills_root=repo_root / "skills",
        docs_root=repo_root / "docs",
        teaching_root=repo_root / "docs" / "teaching",
        bundles_root=repo_root / "bundles",
        cors_origins=cors_origins,
    )
