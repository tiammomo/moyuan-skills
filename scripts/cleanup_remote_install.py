#!/usr/bin/env python3
"""Remove staged remote install artifacts and/or target roots."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from market_utils import resolve_target_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean up a remote install target root and cache root.")
    parser.add_argument("--target-root", type=Path, default=None, help="Installed target root to remove.")
    parser.add_argument("--cache-root", type=Path, default=None, help="Remote cache root to remove.")
    return parser


def _remove_tree(path: Path | None) -> tuple[str, bool]:
    if path is None:
        return "", False

    resolved = resolve_target_root(path)
    if resolved.exists():
        shutil.rmtree(resolved)
        return str(resolved), True
    return str(resolved), False


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.target_root is None and args.cache_root is None:
        print("ERROR: provide at least one of --target-root or --cache-root")
        return 1

    target_path, target_removed = _remove_tree(args.target_root)
    cache_path, cache_removed = _remove_tree(args.cache_root)

    if target_path:
        print(f"Target root: {target_path} ({'removed' if target_removed else 'not present'})")
    if cache_path:
        print(f"Cache root: {cache_path} ({'removed' if cache_removed else 'not present'})")
    print("Remote install cleanup completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
