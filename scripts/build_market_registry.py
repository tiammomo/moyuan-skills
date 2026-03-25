#!/usr/bin/env python3
"""Build a hosted-friendly public/private skills market registry output."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import build_federation_feed
import build_market_catalog
import build_market_index
import build_market_recommendations
import build_org_market_index
import package_skill
from market_utils import ORG_POLICIES_DIR, ROOT, dump_json, iter_org_policy_paths, load_json, repo_relative_path


DEFAULT_OUTPUT = ROOT / "dist" / "market-registry"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a hosted-friendly public/private skills market registry.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory for the registry build.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()
    output_arg = repo_relative_path(output_dir)

    exit_code = package_skill.main(["--all", "--output-dir", output_arg])
    if exit_code != 0:
        return exit_code
    for runner in (
        build_market_index.main,
        build_market_catalog.main,
        build_market_recommendations.main,
        build_federation_feed.main,
    ):
        exit_code = runner(["--output-dir", output_arg])
        if exit_code != 0:
            return exit_code

    org_outputs: list[dict] = []
    for policy_path in iter_org_policy_paths():
        policy_arg = repo_relative_path(policy_path)
        for runner in (
            build_org_market_index.main,
            build_market_catalog.main,
            build_market_recommendations.main,
            build_federation_feed.main,
        ):
            if runner is build_org_market_index.main:
                command_args = [policy_arg, "--output-dir", output_arg]
            else:
                command_args = ["--output-dir", output_arg, "--org-policy", policy_arg]
            exit_code = runner(command_args)
            if exit_code != 0:
                return exit_code
        org_id = load_json(policy_path)["org_id"]
        org_outputs.append(
            {
                "org_id": org_id,
                "policy_path": policy_arg,
                "index": f"orgs/{org_id}/index.json",
                "catalog": f"orgs/{org_id}/site/index.html",
                "recommendations": f"orgs/{org_id}/recommendations/index.json",
                "federation_feed": f"orgs/{org_id}/federation/feed.json",
            }
        )

    registry_payload = {
        "format": "moyuan-skills-hosted-registry@v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "public": {
            "index": "index.json",
            "catalog": "site/index.html",
            "recommendations": "recommendations/index.json",
            "bundles": "recommendations/bundles.json",
            "federation_feed": "federation/public-feed.json",
            "packages_dir": "packages",
            "install_dir": "install",
            "provenance_dir": "provenance",
        },
        "orgs": org_outputs,
        "org_policy_dir": repo_relative_path(ORG_POLICIES_DIR),
    }
    dump_json(output_dir / "registry.json", registry_payload)
    print(f"Built hosted registry output in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
