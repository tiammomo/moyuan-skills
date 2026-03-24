#!/usr/bin/env python3
"""Backward-compatible wrapper for the repository eval harness."""

from __future__ import annotations

from run_eval_harness import main


if __name__ == "__main__":
    raise SystemExit(main())
