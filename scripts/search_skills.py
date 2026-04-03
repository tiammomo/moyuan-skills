#!/usr/bin/env python3
"""Search local skills market manifests or channel index files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_utils import ROOT, iter_manifest_paths, load_json, validate_market_manifest
from remote_registry_utils import RemoteRegistryClient, RemoteRegistryError, build_remote_registry_profile, ordered_remote_channels


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search skills market manifests.")
    parser.add_argument("--query", default="", help="Free-text query against id, name, title, summary, tags, keywords, capabilities, and bundles.")
    parser.add_argument("--category", default="", help="Filter by category.")
    parser.add_argument("--tag", default="", help="Filter by tag.")
    parser.add_argument("--channel", default="", help="Filter by channel.")
    parser.add_argument("--index", type=Path, default=None, help="Optional prebuilt channel index JSON file.")
    parser.add_argument("--registry", default="", help="Hosted registry base URL or registry.json URL.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def search_index_payload(payload: dict, query: str, category: str, tag: str, channel: str) -> list[dict]:
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


def search_index(index_path: Path, query: str, category: str, tag: str, channel: str) -> list[dict]:
    payload = load_json(index_path)
    return search_index_payload(payload, query, category, tag, channel)


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


def search_remote_registry(
    registry_url: str,
    *,
    query: str,
    category: str,
    tag: str,
    channel: str,
) -> dict:
    client = RemoteRegistryClient(registry_url)
    index_payload = client.load_index()
    selected_channels = [channel] if channel else ordered_remote_channels(index_payload)

    results: list[dict] = []
    searched_channels: list[dict] = []
    for selected_channel in selected_channels:
        channel_payload, channel_url = client.load_channel_index_document(selected_channel)
        channel_results = search_index_payload(channel_payload, query, category, tag, "")
        searched_channels.append(
            {
                "channel": selected_channel,
                "url": channel_url,
                "result_count": len(channel_results),
            }
        )
        for skill in channel_results:
            results.append(
                {
                    **skill,
                    "registry_url": client.registry_url,
                }
            )

    results.sort(key=lambda item: (str(item.get("title", "")).lower(), str(item.get("id", "")).lower()))
    return {
        "registry": build_remote_registry_profile(client),
        "query": query,
        "filters": {
            "category": category,
            "tag": tag,
            "channel": channel,
        },
        "searched_channels": searched_channels,
        "result_count": len(results),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    query = args.query.strip().lower()
    category = args.category.strip()
    tag = args.tag.strip()
    channel = args.channel.strip()

    if args.registry:
        try:
            payload = search_remote_registry(
                args.registry,
                query=query,
                category=category,
                tag=tag,
                channel=channel,
            )
        except RemoteRegistryError as error:
            print(f"ERROR: {error}")
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0
        if not payload["results"]:
            print("No remote skills matched the query.")
            return 0
        print(f"Remote registry: {payload['registry']['registry_url']}")
        channels_label = ", ".join(item["channel"] for item in payload["searched_channels"]) or "none"
        print(f"Searched channels: {channels_label}")
        results = payload["results"]
    elif args.index is not None:
        index_path = args.index if args.index.is_absolute() else (ROOT / args.index)
        results = search_index(index_path, query, category, tag, channel)
    else:
        results = search_manifests(query, category, tag, channel)

    if not args.registry and args.json:
        print(json.dumps({"result_count": len(results), "results": results}, indent=2, ensure_ascii=False))
        return 0

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
