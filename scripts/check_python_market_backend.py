#!/usr/bin/env python3
"""Smoke-check the Python market backend repository layer."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.repository import MarketRepository


def main() -> int:
    repository = MarketRepository()

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

    print(
        "Python market backend check passed for "
        f"{len(repository.get_all_skills())} skill summary record(s), "
        f"{len(bundles)} bundle(s), and "
        f"{len(docs_catalog.get('skill_docs', []))} skill doc record(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
