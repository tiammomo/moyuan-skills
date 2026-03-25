#!/usr/bin/env python3
"""Verify a market provenance attestation or an install spec that references it."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_utils import (
    ROOT,
    load_json,
    sha256_for_file,
    validate_install_spec_payload,
    validate_provenance_payload,
    verify_provenance_against_install_spec,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify market provenance from an install spec or attestation JSON.")
    parser.add_argument("path", type=Path, help="Install spec JSON or provenance attestation JSON.")
    parser.add_argument(
        "--kind",
        choices=["auto", "install-spec", "provenance"],
        default="auto",
        help="Interpretation mode for the input path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_path = args.path if args.path.is_absolute() else (ROOT / args.path)
    if not target_path.is_file():
        print(f"ERROR: missing input file {target_path}")
        return 1

    payload = load_json(target_path)
    mode = args.kind
    if mode == "auto":
        mode = "install-spec" if "package_type" in payload else "provenance"

    if mode == "install-spec":
        try:
            label = target_path.relative_to(ROOT).as_posix()
        except ValueError:
            label = target_path.as_posix()
        errors = validate_install_spec_payload(payload, label)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1

        provenance_path = ROOT / str(payload["provenance_path"])
        provenance_payload = load_json(provenance_path)
        provenance_errors = validate_provenance_payload(
            provenance_payload,
            provenance_path.relative_to(ROOT).as_posix(),
        )
        provenance_errors.extend(verify_provenance_against_install_spec(provenance_payload, payload, label))
        package_checksum = sha256_for_file(ROOT / str(payload["package_path"]))
        provenance_checksum = sha256_for_file(provenance_path)
        if package_checksum != payload["checksum_sha256"]:
            provenance_errors.append("install spec package checksum does not match local artifact")
        if provenance_checksum != payload["provenance_sha256"]:
            provenance_errors.append("install spec provenance checksum does not match local artifact")
        if provenance_errors:
            for error in provenance_errors:
                print(f"ERROR: {error}")
            return 1
        print(f"Verified install spec provenance for {payload['skill_id']}")
        return 0

    try:
        label = target_path.relative_to(ROOT).as_posix()
    except ValueError:
        label = target_path.as_posix()
    errors = validate_provenance_payload(payload, label)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    package_payload = payload["package"]
    package_checksum = sha256_for_file(ROOT / str(package_payload["path"]))
    if package_checksum != package_payload["checksum_sha256"]:
        print("ERROR: provenance package checksum does not match local artifact")
        return 1
    print(f"Verified provenance attestation for {payload['skill_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
