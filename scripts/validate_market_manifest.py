#!/usr/bin/env python3
"""Validate skills market manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_utils import ROOT, iter_manifest_paths, validate_market_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate one or more skill market manifests.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional manifest file paths. Defaults to all skills/*/market/skill.json."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifest_paths = args.paths or iter_manifest_paths()
    if not manifest_paths:
        print("ERROR: no market manifests found")
        return 1

    errors: list[str] = []
    for path in manifest_paths:
        resolved = path if path.is_absolute() else (ROOT / path)
        if not resolved.is_file():
            errors.append(f"missing manifest file: {path}")
            continue
        _, manifest_errors = validate_market_manifest(resolved.resolve())
        errors.extend(manifest_errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Market manifest validation passed for {len(manifest_paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
