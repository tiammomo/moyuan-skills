#!/usr/bin/env python3
"""Validate publisher profiles and org market policies."""

from __future__ import annotations

from market_utils import (
    collect_valid_manifests,
    iter_org_policy_paths,
    load_publisher_profiles,
    validate_org_policy,
)


def main() -> int:
    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    errors = [*manifest_errors, *publisher_errors]

    known_skill_ids = {manifest["id"] for manifest in manifests}
    valid_policy_count = 0
    for path in iter_org_policy_paths():
        _, policy_errors = validate_org_policy(path, publisher_profiles, known_skill_ids)
        if policy_errors:
            errors.extend(policy_errors)
            continue
        valid_policy_count += 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Market governance check passed for "
        f"{len(publisher_profiles)} publisher profile(s) and {valid_policy_count} org policy file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
