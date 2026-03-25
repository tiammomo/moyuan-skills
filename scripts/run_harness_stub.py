#!/usr/bin/env python3
"""Run small executable stubs for harness prototype files."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

from harness_proto_utils import evaluate_gate_payload, load_simple_yaml


def summarize_tool_contract(path: Path) -> str:
    payload = load_simple_yaml(path)["tool_contract"]
    required_fields = payload["input"]["required_fields"]
    headings = payload["output"]["required_headings"]
    return "\n".join(
        [
            f"Tool contract: {payload['id']}",
            f"Skill: {payload['skill']}",
            f"Command: {payload['command']}",
            f"Required input fields: {', '.join(required_fields)}",
            f"Required output headings: {', '.join(headings)}",
        ]
    )


def evaluate_gate(path: Path, checks: list[str], artifacts: list[str], blockers: list[str]) -> tuple[bool, list[str]]:
    payload = load_simple_yaml(path)
    return evaluate_gate_payload(payload, checks, artifacts, blockers)


def summarize_automation(path: Path) -> str:
    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    return "\n".join(
        [
            f"Automation: {payload['name']}",
            f"Skill: {payload['skill']}",
            f"Schedule: {payload['schedule']}",
            f"Review required: {payload['review_required']}",
            f"Prechecks: {len(payload['prechecks'])}",
            f"Postchecks: {len(payload['postchecks'])}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run executable stubs for harness prototype files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tool_parser = subparsers.add_parser("tool-contract", help="Summarize a tool contract.")
    tool_parser.add_argument("path", type=Path, help="Path to the tool contract YAML file.")

    gate_parser = subparsers.add_parser("gate", help="Evaluate a safety gate with supplied checks and artifacts.")
    gate_parser.add_argument("path", type=Path, help="Path to the safety gate YAML file.")
    gate_parser.add_argument("--check", action="append", default=[], help="Completed check label.")
    gate_parser.add_argument("--artifact", action="append", default=[], help="Available artifact label.")
    gate_parser.add_argument("--blocker", action="append", default=[], help="Observed blocker label.")

    automation_parser = subparsers.add_parser("automation", help="Summarize an automation spec.")
    automation_parser.add_argument("path", type=Path, help="Path to the automation TOML file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "tool-contract":
        print(summarize_tool_contract(args.path))
        return 0

    if args.command == "gate":
        passed, messages = evaluate_gate(args.path, args.check, args.artifact, args.blocker)
        if passed:
            print("Gate evaluation: PASS")
            return 0
        print("Gate evaluation: FAIL")
        for message in messages:
            print(message)
        return 1

    if args.command == "automation":
        print(summarize_automation(args.path))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
