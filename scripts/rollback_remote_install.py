#!/usr/bin/env python3
"""Rollback a frontend-managed remote install target root."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from market_utils import ROOT, resolve_target_root


ALLOWED_REMOTE_ROOT = (ROOT / "dist" / "frontend-remote-execution").resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reset a dedicated frontend remote install target root and optional cache root."
    )
    parser.add_argument("--target-root", type=Path, required=True, help="Dedicated remote target root to remove.")
    parser.add_argument("--cache-root", type=Path, default=None, help="Optional remote cache root to remove.")
    return parser


def ensure_allowed_remote_path(path: Path, *, allow_root: bool) -> Path:
    resolved = resolve_target_root(path).resolve()
    if not resolved.is_relative_to(ALLOWED_REMOTE_ROOT):
        raise SystemExit(
            f"remote rollback path must stay inside {ALLOWED_REMOTE_ROOT}: {resolved}"
        )
    if not allow_root and resolved == ALLOWED_REMOTE_ROOT:
        raise SystemExit(
            f"refusing to remove the top-level frontend remote execution root: {resolved}"
        )
    return resolved


def remove_tree(path: Path | None, *, allow_root: bool) -> tuple[str, bool]:
    if path is None:
        return "", False

    resolved = ensure_allowed_remote_path(path, allow_root=allow_root)
    if resolved.exists():
        shutil.rmtree(resolved)
        return str(resolved), True
    return str(resolved), False


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_path, target_removed = remove_tree(args.target_root, allow_root=False)
    cache_path, cache_removed = remove_tree(args.cache_root, allow_root=True)

    print(f"Allowed remote rollback root: {ALLOWED_REMOTE_ROOT}")
    print(f"Target root: {target_path} ({'removed' if target_removed else 'not present'})")
    if cache_path:
        print(f"Cache root: {cache_path} ({'removed' if cache_removed else 'not present'})")
    print("Remote install rollback completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
