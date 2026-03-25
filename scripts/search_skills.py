#!/usr/bin/env python3
"""Search local skills market manifests or channel index files."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_utils import ROOT, iter_manifest_paths, load_json, validate_market_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search skills market manifests.")
    parser.add_argument("--query", default="", help="Free-text query against id, name, title, summary, tags, keywords, capabilities, and bundles.")
    parser.add_argument("--category", default="", help="Filter by category.")
    parser.add_argument("--tag", default="", help="Filter by tag.")
    parser.add_argument("--channel", default="", help="Filter by channel.")
    parser.add_argument("--index", type=Path, default=None, help="Optional prebuilt channel index JSON file.")
    return parser


def search_index(index_path: Path, query: str, category: str, tag: str, channel: str) -> list[dict]:
    payload = load_json(index_path)
    results = []
    for skill in payload.get("skills", []):
        haystack = " ".join(
            [
                skill.get("id", ""),
                skill.get("name", ""),
                skill.get("title", ""),
                skill.get("publisher", ""),
                skill.get("publisher_display_name", ""),
                skill.get("summary", ""),
                " ".join(skill.get("tags", [])),
                " ".join(skill.get("capabilities", [])),
                " ".join(skill.get("starter_bundle_ids", [])),
                skill.get("lifecycle_status", ""),
            ]
        ).lower()
        if query and query not in haystack:
            continue
        if category and category not in skill.get("categories", []):
            continue
        if tag and tag not in skill.get("tags", []):
            continue
        if channel and channel != skill.get("channel", ""):
            continue
        results.append(skill)
    return results


def search_manifests(query: str, category: str, tag: str, channel: str) -> list[dict]:
    results = []
    for path in iter_manifest_paths():
        payload, errors = validate_market_manifest(path)
        if errors:
            continue
        haystack = " ".join(
            [
                payload.get("id", ""),
                payload.get("name", ""),
                payload.get("title", ""),
                payload.get("publisher", ""),
                payload.get("summary", ""),
                " ".join(payload.get("tags", [])),
                " ".join(payload.get("search", {}).get("keywords", [])),
                " ".join(payload.get("distribution", {}).get("capabilities", [])),
                " ".join(payload.get("distribution", {}).get("starter_bundle_ids", [])),
                payload.get("lifecycle", {}).get("status", ""),
            ]
        ).lower()
        if query and query not in haystack:
            continue
        if category and category not in payload.get("categories", []):
            continue
        if tag and tag not in payload.get("tags", []):
            continue
        if channel and channel != payload.get("channel", ""):
            continue
        results.append(payload)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    query = args.query.strip().lower()
    category = args.category.strip()
    tag = args.tag.strip()
    channel = args.channel.strip()

    if args.index is not None:
        index_path = args.index if args.index.is_absolute() else (ROOT / args.index)
        results = search_index(index_path, query, category, tag, channel)
    else:
        results = search_manifests(query, category, tag, channel)

    if not results:
        print("No skills matched the query.")
        return 0

    for skill in results:
        print(f"{skill['id']} [{skill.get('channel', 'index')}]")
        print(f"  title: {skill['title']}")
        if "publisher_display_name" in skill:
            verified_label = " verified" if skill.get("publisher_verified") else ""
            print(f"  publisher: {skill['publisher_display_name']} ({skill.get('trust_level', 'community')}{verified_label})")
        elif "publisher" in skill:
            print(f"  publisher: {skill['publisher']}")
        print(f"  summary: {skill['summary']}")
        print(f"  tags: {', '.join(skill.get('tags', []))}")
        if "categories" in skill:
            print(f"  categories: {', '.join(skill.get('categories', []))}")
        if "capabilities" in skill:
            print(f"  capabilities: {', '.join(skill.get('capabilities', []))}")
        lifecycle = skill.get("lifecycle_status") or skill.get("lifecycle", {}).get("status", "")
        if lifecycle:
            print(f"  lifecycle: {lifecycle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
