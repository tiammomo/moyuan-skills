#!/usr/bin/env python3
"""Build local skills market index files."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_utils import (
    MARKET_CHANNELS,
    ROOT,
    aggregate_index_payload,
    channel_index_payload,
    collect_valid_manifests,
    dump_json,
    load_publisher_profiles,
)


DEFAULT_OUTPUT = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build local market index files from skills/*/market/skill.json.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory for generated market index files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    errors = [*manifest_errors, *publisher_errors]

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()
    channels_dir = output_dir / "channels"
    dump_json(output_dir / "index.json", aggregate_index_payload(manifests, output_dir))

    for channel in sorted(MARKET_CHANNELS):
        dump_json(
            channels_dir / f"{channel}.json",
            channel_index_payload(channel, manifests, output_dir, publisher_profiles),
        )

    print(f"Built market index in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
