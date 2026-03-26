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
    if not docs_catalog.get("skill_docs") or not docs_catalog.get("teaching_docs"):
        print("ERROR: docs catalog should include both skill docs and teaching docs")
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
