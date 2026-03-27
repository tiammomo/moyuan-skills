from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import Settings, get_settings


VALID_CHANNELS = ("stable", "beta", "internal")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def _first_paragraph(markdown: str) -> str:
    lines = [line.strip() for line in markdown.splitlines()]
    buffer: list[str] = []
    started = False
    for line in lines:
        if not line:
            if started and buffer:
                break
            continue
        if line.startswith("#") and not started:
            continue
        started = True
        buffer.append(line)
    return " ".join(buffer).strip()


def _is_internal_iteration_doc(path: Path) -> bool:
    return path.stem.endswith("-iteration")


class MarketRepository:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def repo_root(self) -> Path:
        return self.settings.repo_root

    def _dist_path(self, *parts: str) -> Path:
        return self.settings.dist_market_root.joinpath(*parts)

    def get_market_index(self) -> dict[str, Any]:
        return _read_json(self._dist_path("index.json"))

    def get_channel_skills(self, channel: str) -> dict[str, Any]:
        if channel not in VALID_CHANNELS:
            raise ValueError(f"unsupported channel: {channel}")
        return _read_json(self._dist_path("channels", f"{channel}.json"))

    def get_all_skills(self) -> list[dict[str, Any]]:
        skills: list[dict[str, Any]] = []
        for channel in VALID_CHANNELS:
            channel_path = self._dist_path("channels", f"{channel}.json")
            if not channel_path.is_file():
                continue
            channel_payload = _read_json(channel_path)
            skills.extend(channel_payload.get("skills", []))
        return skills

    def search_skills(
        self,
        *,
        query: str = "",
        channels: list[str] | None = None,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        selected_channels = {item for item in (channels or []) if item}
        selected_categories = {item for item in (categories or []) if item}
        selected_tags = {item for item in (tags or []) if item}
        needle = query.strip().lower()
        results: list[dict[str, Any]] = []
        for skill in self.get_all_skills():
            channel = str(skill.get("channel", "")).strip()
            if selected_channels and channel not in selected_channels:
                continue
            skill_categories = {str(item).strip() for item in skill.get("categories", []) if str(item).strip()}
            if selected_categories and not skill_categories.intersection(selected_categories):
                continue
            skill_tags = {str(item).strip() for item in skill.get("tags", []) if str(item).strip()}
            if selected_tags and not skill_tags.intersection(selected_tags):
                continue
            if needle:
                haystack = " ".join(
                    [
                        str(skill.get("title", "")),
                        str(skill.get("summary", "")),
                        " ".join(sorted(skill_categories)),
                        " ".join(sorted(skill_tags)),
                    ]
                ).lower()
                if needle not in haystack:
                    continue
            results.append(skill)
        return results

    def get_skill_summary(self, name: str) -> dict[str, Any] | None:
        normalized = name.strip().lower()
        for skill in self.get_all_skills():
            if str(skill.get("name", "")).strip().lower() == normalized:
                return skill
        return None

    def get_skill_manifest(self, name: str) -> dict[str, Any] | None:
        manifest_path = self.settings.skills_root / name / "market" / "skill.json"
        if not manifest_path.is_file():
            return None
        return _read_json(manifest_path)

    def get_install_spec(self, name: str, version: str | None = None) -> dict[str, Any] | None:
        resolved_version = version
        if not resolved_version:
            skill = self.get_skill_summary(name)
            if not skill:
                return None
            resolved_version = str(skill.get("version", "")).strip()
        if not resolved_version:
            return None
        spec_path = self._dist_path("install", f"{name}-{resolved_version}.json")
        if not spec_path.is_file():
            return None
        return _read_json(spec_path)

    def get_skill_doc(self, name: str) -> str | None:
        doc_path = self.settings.docs_root / f"{name}.md"
        if not doc_path.is_file():
            return None
        return _read_text(doc_path)

    def get_teaching_doc(self, doc_id: str) -> dict[str, Any] | None:
        path = self.settings.teaching_root / f"{doc_id}.md"
        if not path.is_file():
            return None
        markdown = _read_text(path)
        return {
            "id": doc_id,
            "kind": "teaching",
            "title": _first_heading(markdown, doc_id),
            "summary": _first_paragraph(markdown),
            "markdown": markdown,
            "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
        }

    def get_project_doc(self, doc_id: str) -> dict[str, Any] | None:
        path = self.settings.docs_root / f"{doc_id}.md"
        if not path.is_file() or _is_internal_iteration_doc(path):
            return None
        markdown = _read_text(path)
        return {
            "id": doc_id,
            "kind": "project",
            "title": _first_heading(markdown, doc_id),
            "summary": _first_paragraph(markdown),
            "markdown": markdown,
            "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
        }

    def get_skill_detail(self, name: str) -> dict[str, Any] | None:
        manifest = self.get_skill_manifest(name)
        if not manifest:
            return None
        install_spec = self.get_install_spec(name, str(manifest.get("version", "")).strip())
        doc_markdown = self.get_skill_doc(name)
        related_skills: list[dict[str, Any]] = []
        all_skills = self.get_all_skills()
        by_id = {str(skill.get("id", "")).strip(): skill for skill in all_skills}
        search_info = manifest.get("search", {})
        if isinstance(search_info, dict):
            for skill_id in search_info.get("related_skills", []):
                related = by_id.get(str(skill_id).strip())
                if related:
                    related_skills.append(related)
        return {
            "manifest": manifest,
            "install_spec": install_spec,
            "doc_markdown": doc_markdown,
            "related_skills": related_skills,
        }

    def get_categories(self) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for skill in self.get_all_skills():
            for category in skill.get("categories", []):
                key = str(category).strip()
                if key:
                    counts[key] = counts.get(key, 0) + 1
        return [
            {"category": category, "count": count}
            for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    def get_tags(self) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for skill in self.get_all_skills():
            for tag in skill.get("tags", []):
                key = str(tag).strip()
                if key:
                    counts[key] = counts.get(key, 0) + 1
        return [
            {"tag": tag, "count": count}
            for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    def list_bundles(self) -> list[dict[str, Any]]:
        all_skills = self.get_all_skills()
        by_id = {str(skill.get("id", "")).strip(): skill for skill in all_skills}
        bundles: list[dict[str, Any]] = []
        for bundle_path in sorted(self.settings.bundles_root.glob("*.json")):
            payload = _read_json(bundle_path)
            skill_summaries = [
                by_id[skill_id]
                for skill_id in payload.get("skills", [])
                if str(skill_id).strip() in by_id
            ]
            bundles.append(
                {
                    **payload,
                    "skill_count": len(payload.get("skills", [])),
                    "skill_summaries": skill_summaries,
                    "path": str(bundle_path.relative_to(self.repo_root)).replace("\\", "/"),
                }
            )
        return bundles

    def get_bundle(self, bundle_id: str) -> dict[str, Any] | None:
        normalized = bundle_id.strip().lower()
        for bundle in self.list_bundles():
            if str(bundle.get("id", "")).strip().lower() != normalized:
                continue
            install_specs: list[dict[str, Any]] = []
            for skill in bundle.get("skill_summaries", []):
                name = str(skill.get("name", "")).strip()
                version = str(skill.get("version", "")).strip()
                spec = self.get_install_spec(name, version)
                if spec:
                    install_specs.append(spec)
            return {
                "bundle": bundle,
                "skills": bundle.get("skill_summaries", []),
                "install_specs": install_specs,
            }
        return None

    def get_docs_catalog(self) -> dict[str, Any]:
        skill_docs: list[dict[str, Any]] = []
        for skill in self.get_all_skills():
            name = str(skill.get("name", "")).strip()
            if not name:
                continue
            markdown = self.get_skill_doc(name)
            if not markdown:
                continue
            skill_docs.append(
                {
                    "id": name,
                    "kind": "skill",
                    "title": _first_heading(markdown, str(skill.get("title", name))),
                    "summary": _first_paragraph(markdown) or str(skill.get("summary", "")),
                    "path": f"docs/{name}.md",
                }
            )

        teaching_docs: list[dict[str, Any]] = []
        for path in sorted(self.settings.teaching_root.glob("*.md")):
            markdown = _read_text(path)
            teaching_docs.append(
                {
                    "id": path.stem,
                    "kind": "teaching",
                    "title": _first_heading(markdown, path.stem),
                    "summary": _first_paragraph(markdown),
                    "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
                }
            )

        root_docs: list[dict[str, Any]] = []
        skill_doc_names = {f"{skill['name']}.md" for skill in self.get_all_skills() if skill.get("name")}
        for path in sorted(self.settings.docs_root.glob("*.md")):
            if path.name == "README.md" or path.name in skill_doc_names or _is_internal_iteration_doc(path):
                continue
            markdown = _read_text(path)
            root_docs.append(
                {
                    "id": path.stem,
                    "kind": "project",
                    "title": _first_heading(markdown, path.stem),
                    "summary": _first_paragraph(markdown),
                    "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
                }
            )

        all_docs = sorted(
            [*skill_docs, *teaching_docs, *root_docs],
            key=lambda item: (str(item.get("title", "")).lower(), str(item.get("id", "")).lower()),
        )

        return {
            "skill_docs": skill_docs,
            "teaching_docs": teaching_docs,
            "project_docs": root_docs,
            "all_docs": all_docs,
        }

    def get_repo_snapshot(self) -> dict[str, Any]:
        index = self.get_market_index()
        return {
            "market_index": index,
            "channels": {channel: index.get("channels", {}).get(channel, {}) for channel in VALID_CHANNELS},
            "skill_count": len(self.get_all_skills()),
            "bundle_count": len(self.list_bundles()),
            "doc_catalog": {
                "skill_doc_count": len(self.get_docs_catalog().get("skill_docs", [])),
                "teaching_doc_count": len(self.get_docs_catalog().get("teaching_docs", [])),
                "project_doc_count": len(self.get_docs_catalog().get("project_docs", [])),
            },
        }

    def get_installed_state(self, target_root: Path) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        lock_path = resolved_root / "skills.lock.json"
        if lock_path.is_file():
            lock_payload = _read_json(lock_path)
        else:
            lock_payload = {"installed": []}

        installed = sorted(
            [
                entry
                for entry in lock_payload.get("installed", [])
                if isinstance(entry, dict) and str(entry.get("skill_id", "")).strip()
            ],
            key=lambda item: (
                str(item.get("skill_id", "")).lower(),
                str(item.get("install_target", "")).lower(),
            ),
        )

        bundles: list[dict[str, Any]] = []
        bundle_reports_dir = resolved_root / "bundle-reports"
        if bundle_reports_dir.is_dir():
            for report_path in sorted(bundle_reports_dir.glob("*.json")):
                report = _read_json(report_path)
                results = report.get("results", [])
                active_skill_ids = sorted(
                    str(item.get("skill_id", "")).strip()
                    for item in results
                    if isinstance(item, dict) and item.get("status") == "installed" and str(item.get("skill_id", "")).strip()
                )
                bundles.append(
                    {
                        "bundle_id": str(report.get("bundle_id", report_path.stem)),
                        "title": str(report.get("title", report_path.stem)),
                        "generated_at": str(report.get("generated_at", "")),
                        "report_path": str(report_path),
                        "target_root": str(resolved_root),
                        "skill_count": len(active_skill_ids),
                        "active_skill_ids": active_skill_ids,
                    }
                )

        return {
            "target_root": str(resolved_root),
            "lock_path": str(lock_path),
            "installed_count": len(installed),
            "bundle_count": len(bundles),
            "installed": installed,
            "bundles": bundles,
        }

    def get_installed_baseline_state(self, target_root: Path) -> dict[str, Any]:
        resolved_root = target_root.resolve()
        snapshots_dir = resolved_root / "snapshots"
        baseline_path = snapshots_dir / "baseline.json"
        baseline_markdown_path = snapshots_dir / "baseline.md"
        history_path = snapshots_dir / "baseline-history.json"
        history_markdown_path = snapshots_dir / "baseline-history.md"
        archive_dir = snapshots_dir / "baseline-archive"

        baseline_payload = _read_json(baseline_path) if baseline_path.is_file() else None
        raw_history_payload = _read_json(history_path) if history_path.is_file() else None
        history_entries = (
            raw_history_payload.get("entries", [])
            if isinstance(raw_history_payload, dict) and isinstance(raw_history_payload.get("entries", []), list)
            else []
        )
        normalized_entries = [
            entry
            for entry in history_entries
            if isinstance(entry, dict)
        ]
        latest_entry = normalized_entries[-1] if normalized_entries else None
        next_sequence = (
            raw_history_payload.get("next_sequence", 1)
            if isinstance(raw_history_payload, dict)
            else 1
        )

        return {
            "target_root": str(resolved_root),
            "snapshots_dir": str(snapshots_dir),
            "baseline_path": str(baseline_path),
            "baseline_markdown_path": str(baseline_markdown_path),
            "history_path": str(history_path),
            "history_markdown_path": str(history_markdown_path),
            "archive_dir": str(archive_dir),
            "baseline_exists": baseline_path.is_file(),
            "history_exists": history_path.is_file(),
            "history_entry_count": len(normalized_entries),
            "next_sequence": int(next_sequence) if str(next_sequence).isdigit() else 1,
            "current_baseline": (
                {
                    "generated_at": str(baseline_payload.get("generated_at", "")),
                    "target_root": str(baseline_payload.get("target_root", "")),
                    "summary": baseline_payload.get("summary", {}),
                }
                if isinstance(baseline_payload, dict)
                else None
            ),
            "latest_entry": latest_entry,
            "entries": normalized_entries[-5:],
        }
