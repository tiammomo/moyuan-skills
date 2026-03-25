#!/usr/bin/env python3
"""Build starter-bundle and skill-to-skill recommendation outputs for the skills market."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from market_utils import (
    ROOT,
    dump_json,
    load_filtered_market_inputs,
    repo_relative_path,
)


DEFAULT_OUTPUT = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build recommendation outputs for the local skills market.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory containing market artifacts.")
    parser.add_argument("--org-policy", type=Path, default=None, help="Optional org market policy JSON file.")
    return parser

def bundle_membership_map(bundles: list[dict]) -> dict[str, set[str]]:
    memberships: dict[str, set[str]] = {}
    for bundle in bundles:
        bundle_id = bundle["id"]
        for skill_id in bundle["skills"]:
            memberships.setdefault(skill_id, set()).add(bundle_id)
    return memberships


def recommendation_entry(source: dict, target: dict, memberships: dict[str, set[str]]) -> dict | None:
    if source["id"] == target["id"]:
        return None
    if target["lifecycle"]["status"] in {"blocked", "archived"}:
        return None

    score = 0
    reasons: list[str] = []
    source_related = set(source["search"]["related_skills"])
    if target["name"] in source_related or target["id"] in source_related:
        score += 120
        reasons.append("listed as a related skill")

    shared_categories = sorted(set(source["categories"]) & set(target["categories"]))
    if shared_categories:
        score += 30 * len(shared_categories)
        reasons.append("shares categories: " + ", ".join(shared_categories))

    shared_tags = sorted(set(source["tags"]) & set(target["tags"]))
    if shared_tags:
        score += 15 * len(shared_tags)
        reasons.append("shares tags: " + ", ".join(shared_tags[:3]))

    shared_capabilities = sorted(set(source["distribution"]["capabilities"]) & set(target["distribution"]["capabilities"]))
    if shared_capabilities:
        score += 25 * len(shared_capabilities)
        reasons.append("shares capabilities: " + ", ".join(shared_capabilities[:3]))

    shared_bundles = sorted(memberships.get(source["id"], set()) & memberships.get(target["id"], set()))
    if shared_bundles:
        score += 50 * len(shared_bundles)
        reasons.append("appears in the same starter bundle: " + ", ".join(shared_bundles))

    if source["channel"] == target["channel"]:
        score += 5
        reasons.append("published in the same channel")
    if target["channel"] == "stable":
        score += 8
        reasons.append("available in the stable channel")
    if target["publisher_profile"]["verified"]:
        score += 5
        reasons.append("comes from a verified publisher")
    if target["lifecycle"]["status"] == "deprecated":
        score -= 40
        reasons.append("deprecated lifecycle status lowers priority")

    if score <= 0:
        return None

    return {
        "id": target["id"],
        "name": target["name"],
        "title": target["title"],
        "channel": target["channel"],
        "score": score,
        "reasons": reasons,
        "lifecycle_status": target["lifecycle"]["status"],
        "starter_bundle_ids": target["distribution"]["starter_bundle_ids"],
    }


def build_bundle_payloads(bundles: list[dict], manifests_by_id: dict[str, dict]) -> list[dict]:
    payloads: list[dict] = []
    for bundle in bundles:
        payloads.append(
            {
                "id": bundle["id"],
                "title": bundle["title"],
                "summary": bundle["summary"],
                "status": bundle["status"],
                "channels": bundle["channels"],
                "use_cases": bundle["use_cases"],
                "keywords": bundle["keywords"],
                "skills": [
                    {
                        "id": skill_id,
                        "title": manifests_by_id[skill_id]["title"],
                        "channel": manifests_by_id[skill_id]["channel"],
                        "lifecycle_status": manifests_by_id[skill_id]["lifecycle"]["status"],
                    }
                    for skill_id in bundle["skills"]
                    if skill_id in manifests_by_id
                ],
            }
        )
    return payloads


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifests, bundles, policy_payload, errors = load_filtered_market_inputs(args.org_policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()
    recommendations_dir = output_dir / "recommendations"
    if policy_payload is not None:
        recommendations_dir = output_dir / "orgs" / policy_payload["org_id"] / "recommendations"
    skill_recommendations_dir = recommendations_dir / "skills"
    manifests_by_id = {manifest["id"]: manifest for manifest in manifests}
    memberships = bundle_membership_map(bundles)

    bundle_payloads = build_bundle_payloads(bundles, manifests_by_id)
    dump_json(recommendations_dir / "bundles.json", {"bundles": bundle_payloads})

    index_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "org_policy": policy_payload["org_id"] if policy_payload else None,
        "bundle_count": len(bundle_payloads),
        "skill_count": len(manifests),
        "skills": {},
        "bundles_path": repo_relative_path(recommendations_dir / "bundles.json"),
    }

    for source in manifests:
        recommendations = [
            entry
            for candidate in manifests
            if (entry := recommendation_entry(source, candidate, memberships)) is not None
        ]
        recommendations.sort(key=lambda item: (-item["score"], item["title"].lower()))
        payload = {
            "skill_id": source["id"],
            "title": source["title"],
            "channel": source["channel"],
            "recommendations": recommendations[:5],
        }
        skill_path = skill_recommendations_dir / f"{source['name']}.json"
        dump_json(skill_path, payload)
        index_payload["skills"][source["id"]] = repo_relative_path(skill_path)

    dump_json(recommendations_dir / "index.json", index_payload)
    print(f"Built market recommendations in {recommendations_dir}")
    if policy_payload is not None:
        print(f"Recommendation scope: {policy_payload['org_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
