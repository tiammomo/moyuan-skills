#!/usr/bin/env python3
"""Run a minimal executable harness runtime from a blueprint."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from harness_proto_utils import evaluate_gate_payload, load_simple_yaml


ROOT = Path(__file__).resolve().parents[1]


def resolve_repo_path(raw_value: str) -> Path:
    path = Path(raw_value)
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def run_command(command: str) -> dict:
    result = subprocess.run(
        command,
        shell=True,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def skipped_command(command: str, reason: str) -> dict:
    return {
        "command": command,
        "exit_code": None,
        "passed": False,
        "stdout": "",
        "stderr": "",
        "skipped": True,
        "reason": reason,
    }


def collect_artifacts(artifact_map: dict) -> list[dict]:
    statuses: list[dict] = []
    for label, raw_path in artifact_map.items():
        resolved = resolve_repo_path(str(raw_path))
        statuses.append(
            {
                "label": label,
                "path": resolved.as_posix(),
                "exists": resolved.is_file(),
            }
        )
    return statuses


def render_markdown_report(payload: dict) -> str:
    lines = [
        f"# Harness Runtime Report: {payload['blueprint_id']}",
        "",
        f"- Skill: {payload['skill']}",
        f"- Automation: {payload['automation_name']}",
        f"- Started at: {payload['started_at']}",
        f"- Completed at: {payload['completed_at']}",
        f"- Status: {'PASS' if payload['passed'] else 'FAIL'}",
        "",
        "## Commands",
        "",
        "| Stage | Status | Command |",
        "| --- | --- | --- |",
    ]

    for stage, results in (
        ("Precheck", payload["prechecks"]),
        ("Main", [payload["main_command"]]),
        ("Postcheck", payload["postchecks"]),
    ):
        for result in results:
            if result.get("skipped"):
                status = "SKIP"
            else:
                status = "PASS" if result["passed"] else "FAIL"
            lines.append(f"| {stage} | {status} | `{result['command']}` |")

    lines.extend(
        [
            "",
            "## Gate",
            "",
            f"- Gate id: {payload['gate']['id']}",
            f"- Gate status: {'PASS' if payload['gate']['passed'] else 'FAIL'}",
            f"- Completed checks: {', '.join(payload['gate']['completed_checks'])}",
            f"- Present artifacts: {', '.join(payload['gate']['present_artifacts'])}",
        ]
    )

    if payload["gate"]["messages"]:
        lines.append("- Gate messages:")
        for message in payload["gate"]["messages"]:
            lines.append(f"  - {message}")

    lines.extend(["", "## Artifacts", ""])
    for artifact in payload["artifacts"]:
        status = "present" if artifact["exists"] else "missing"
        lines.append(f"- {artifact['label']}: `{artifact['path']}` ({status})")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a minimal executable harness runtime from a blueprint.")
    parser.add_argument("blueprint", type=Path, help="Path to the runtime blueprint YAML file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    blueprint_payload = load_simple_yaml(args.blueprint)["runtime_blueprint"]
    automation_path = resolve_repo_path(str(blueprint_payload["automation"]))
    tool_contract_path = resolve_repo_path(str(blueprint_payload["tool_contract"]))
    gate_path = resolve_repo_path(str(blueprint_payload["gate"]))

    automation = tomllib.loads(automation_path.read_text(encoding="utf-8"))
    tool_contract = load_simple_yaml(tool_contract_path)["tool_contract"]
    gate = load_simple_yaml(gate_path)["gate"]

    started_at = datetime.now(timezone.utc).isoformat()
    skill = str(blueprint_payload["skill"])
    action = str(blueprint_payload["action"])

    consistency_errors: list[str] = []
    if automation.get("skill") != skill:
        consistency_errors.append("automation skill does not match runtime blueprint skill")
    if tool_contract.get("skill") != skill:
        consistency_errors.append("tool contract skill does not match runtime blueprint skill")
    if skill not in gate.get("applies_to", {}).get("skills", []):
        consistency_errors.append("gate does not apply to the runtime blueprint skill")
    if action not in gate.get("applies_to", {}).get("actions", []):
        consistency_errors.append("gate does not apply to the runtime blueprint action")

    prechecks = [run_command(command) for command in automation.get("prechecks", [])]
    prechecks_passed = all(result["passed"] for result in prechecks)

    if consistency_errors:
        main_command = skipped_command(automation["command"], "consistency validation failed")
        postchecks = [
            skipped_command(command, "consistency validation failed")
            for command in automation.get("postchecks", [])
        ]
    elif not prechecks_passed:
        main_command = skipped_command(automation["command"], "prechecks failed")
        postchecks = [
            skipped_command(command, "prechecks failed")
            for command in automation.get("postchecks", [])
        ]
    else:
        main_command = run_command(automation["command"])
        if main_command["passed"]:
            postchecks = [run_command(command) for command in automation.get("postchecks", [])]
        else:
            postchecks = [
                skipped_command(command, "main command failed")
                for command in automation.get("postchecks", [])
            ]

    postchecks_passed = all(result["passed"] for result in postchecks if not result.get("skipped"))
    artifacts = collect_artifacts(dict(blueprint_payload.get("artifacts", {})))
    present_artifacts = [artifact["label"] for artifact in artifacts if artifact["exists"]]

    completed_checks: list[str] = []
    if main_command["passed"] and postchecks_passed:
        completed_checks.extend(list(blueprint_payload.get("checks", {}).get("automated", [])))
    if {"review note", "approval record"} <= set(present_artifacts):
        completed_checks.extend(list(blueprint_payload.get("checks", {}).get("manual", [])))

    gate_passed, gate_messages = evaluate_gate_payload(
        {"gate": gate},
        checks=completed_checks,
        artifacts=present_artifacts,
        blockers=[],
    )

    completed_at = datetime.now(timezone.utc).isoformat()
    passed = (
        not consistency_errors
        and prechecks_passed
        and main_command["passed"]
        and postchecks_passed
        and gate_passed
    )

    report_payload = {
        "blueprint_id": blueprint_payload["id"],
        "skill": skill,
        "automation_name": automation["name"],
        "started_at": started_at,
        "completed_at": completed_at,
        "consistency_errors": consistency_errors,
        "prechecks": prechecks,
        "main_command": main_command,
        "postchecks": postchecks,
        "artifacts": artifacts,
        "gate": {
            "id": gate["id"],
            "passed": gate_passed,
            "messages": consistency_errors + gate_messages,
            "completed_checks": completed_checks,
            "present_artifacts": present_artifacts,
        },
        "passed": passed,
    }

    outputs = dict(blueprint_payload.get("outputs", {}))
    json_path = resolve_repo_path(str(outputs["report_json"]))
    markdown_path = resolve_repo_path(str(outputs["report_markdown"]))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown_report(report_payload), encoding="utf-8")

    print(
        f"Harness runtime completed: {'PASS' if passed else 'FAIL'} for "
        f"{blueprint_payload['id']}."
    )
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
