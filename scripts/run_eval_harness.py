#!/usr/bin/env python3
"""Run the repository eval harness with graders and report generation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "examples" / "eval-harness" / "cases.json"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def skill_script_path(skill: str) -> Path:
    script_name = skill.replace("-", "_") + ".py"
    return ROOT / "skills" / skill / "scripts" / script_name


def grade_contains_all(text: str, values: list[str]) -> tuple[bool, list[str]]:
    missing = [value for value in values if value not in text]
    return not missing, [f"missing required substring: {value}" for value in missing]


def grade_forbids_all(text: str, values: list[str]) -> tuple[bool, list[str]]:
    found = [value for value in values if value in text]
    return not found, [f"found forbidden substring: {value}" for value in found]


def grade_requires_headings(text: str, values: list[str]) -> tuple[bool, list[str]]:
    missing = [value for value in values if value not in text]
    return not missing, [f"missing required heading: {value}" for value in missing]


GRADERS = {
    "contains_all": grade_contains_all,
    "forbids_all": grade_forbids_all,
    "requires_headings": grade_requires_headings,
}


def evaluate_graders(text: str, graders: list[dict]) -> tuple[bool, list[dict]]:
    results: list[dict] = []
    overall_passed = True
    for grader in graders:
        grader_type = grader["type"]
        values = list(grader.get("values", []))
        label = grader.get("label", grader_type)
        passed, messages = GRADERS[grader_type](text, values)
        results.append(
            {
                "type": grader_type,
                "label": label,
                "passed": passed,
                "messages": messages,
            }
        )
        overall_passed = overall_passed and passed
    return overall_passed, results


def run_case(cases_root: Path, case: dict) -> dict:
    skill = str(case["skill"])
    script_path = skill_script_path(skill)
    input_path = cases_root / str(case["input"])
    result: dict = {
        "name": case["name"],
        "skill": skill,
        "draft_passed": False,
        "lint_passed": False,
        "passed": False,
        "graders": [],
        "messages": [],
    }

    if not script_path.is_file():
        result["messages"].append(f"missing skill script: {script_path}")
        return result
    if not input_path.is_file():
        result["messages"].append(f"missing eval input: {input_path}")
        return result

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / f"{case['name']}.md"
        draft_result = run_command(
            [sys.executable, str(script_path), "draft", str(input_path), str(output_path)]
        )
        result["draft_stdout"] = draft_result.stdout.strip()
        result["draft_stderr"] = draft_result.stderr.strip()
        result["draft_exit_code"] = draft_result.returncode
        if draft_result.returncode != 0:
            result["messages"].append("draft command failed")
            return result
        result["draft_passed"] = True

        lint_result = run_command([sys.executable, str(script_path), "lint", str(output_path)])
        result["lint_stdout"] = lint_result.stdout.strip()
        result["lint_stderr"] = lint_result.stderr.strip()
        result["lint_exit_code"] = lint_result.returncode
        if lint_result.returncode != 0:
            result["messages"].append("lint command failed")
            return result
        result["lint_passed"] = True

        text = output_path.read_text(encoding="utf-8")
        graders_passed, grader_results = evaluate_graders(text, list(case.get("graders", [])))
        result["graders"] = grader_results
        result["passed"] = graders_passed and result["draft_passed"] and result["lint_passed"]
        result["output_excerpt"] = "\n".join(text.splitlines()[:12])
        if not graders_passed:
            for grader in grader_results:
                if not grader["passed"]:
                    result["messages"].extend(grader["messages"])

    return result


def render_markdown_report(payload: dict) -> str:
    lines = [
        f"# {payload['report_name']}",
        "",
        f"_Generated at: {payload['generated_at']}_",
        "",
        "## Summary",
        "",
        f"- Cases: {payload['summary']['cases']}",
        f"- Passed: {payload['summary']['passed']}",
        f"- Failed: {payload['summary']['failed']}",
        f"- Graders passed: {payload['summary']['graders_passed']}/{payload['summary']['graders_total']}",
        "",
        "## Case Results",
        "",
        "| Case | Skill | Status | Graders |",
        "| --- | --- | --- | --- |",
    ]

    for case in payload["cases"]:
        grader_total = len(case["graders"])
        grader_passed = sum(1 for grader in case["graders"] if grader["passed"])
        status = "PASS" if case["passed"] else "FAIL"
        lines.append(f"| {case['name']} | {case['skill']} | {status} | {grader_passed}/{grader_total} |")

    lines.append("")
    lines.append("## Details")
    lines.append("")

    for case in payload["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        lines.append(f"### {case['name']} ({status})")
        lines.append("")
        if case["messages"]:
            for message in case["messages"]:
                lines.append(f"- {message}")
        else:
            lines.append("- No failures.")
        lines.append("")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the repository eval harness with graders and report generation.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="Path to the eval case JSON file.")
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Directory to write JSON and markdown reports. Defaults to a temporary directory.",
    )
    parser.add_argument(
        "--skills",
        nargs="*",
        default=None,
        help="Optional list of skill names to filter the case set.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = json.loads(args.cases.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        print("ERROR: eval case file must contain a non-empty 'cases' list")
        return 1

    selected_skills = set(args.skills or [])
    if selected_skills:
        cases = [case for case in cases if case.get("skill") in selected_skills]
    if not cases:
        print("ERROR: no eval cases selected")
        return 1

    cases_root = args.cases.parent
    case_results = [run_case(cases_root, case) for case in cases]
    graders_total = sum(len(case["graders"]) for case in case_results)
    graders_passed = sum(
        1 for case in case_results for grader in case["graders"] if grader["passed"]
    )

    report_payload = {
        "report_name": payload.get("report_name", "Eval Harness Report"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "cases": len(case_results),
            "passed": sum(case["passed"] for case in case_results),
            "failed": sum(not case["passed"] for case in case_results),
            "graders_total": graders_total,
            "graders_passed": graders_passed,
        },
        "cases": case_results,
    }

    if args.report_dir is None:
        report_dir = Path(tempfile.mkdtemp(prefix="moyuan-eval-"))
    else:
        report_dir = args.report_dir
        report_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / "eval-report.json"
    md_path = report_dir / "eval-report.md"
    json_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown_report(report_payload), encoding="utf-8")

    print(
        f"Eval harness completed: {report_payload['summary']['passed']}/{report_payload['summary']['cases']} cases passed."
    )
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")

    return 0 if report_payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
