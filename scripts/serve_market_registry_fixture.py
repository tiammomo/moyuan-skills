#!/usr/bin/env python3
"""Build and serve a hosted market registry fixture for browser tests."""

from __future__ import annotations

import argparse
import http.server
import shutil
from pathlib import Path

import build_market_registry
from market_utils import ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and serve a local hosted market registry fixture.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=38765, help="Port to bind.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "dist" / "playwright-registry",
        help="Output directory for the generated hosted registry.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the output directory before rebuilding the hosted registry.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)
    output_dir = output_dir.resolve()

    if args.clean and output_dir.exists():
        shutil.rmtree(output_dir)

    build_args = ["--output-dir", str(output_dir)]
    exit_code = build_market_registry.main(build_args)
    if exit_code != 0:
        return exit_code

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **handler_kwargs):
            super().__init__(*handler_args, directory=str(output_dir), **handler_kwargs)

        def log_message(self, format: str, *handler_args) -> None:  # noqa: A003 - stdlib signature
            return

    server = http.server.ThreadingHTTPServer((args.host, args.port), QuietHandler)
    print(f"Serving hosted registry fixture from {output_dir} at http://{args.host}:{args.port}/registry.json")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
