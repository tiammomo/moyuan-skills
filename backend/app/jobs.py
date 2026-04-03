from __future__ import annotations

import os
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import Settings


TERMINAL_STATUSES = {"succeeded", "failed"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stringify_command(command: list[str]) -> str:
    return " ".join(command)


def _resolve_subprocess_command(command: list[str]) -> list[str]:
    if not command:
        return command
    if Path(command[0]).name.lower().startswith("python"):
        return [sys.executable, *command[1:]]
    return command


class LocalJobStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_subprocess_job(
        self,
        *,
        kind: str,
        command: list[str],
        summary: dict[str, Any],
        artifacts: dict[str, Any],
        request_payload: dict[str, Any],
    ) -> dict[str, Any]:
        job_id = uuid4().hex
        job_record = {
            "job_id": job_id,
            "kind": kind,
            "status": "queued",
            "created_at": _utc_now(),
            "started_at": None,
            "finished_at": None,
            "command": command,
            "command_text": _stringify_command(command),
            "summary": summary,
            "artifacts": artifacts,
            "request": request_payload,
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "error": None,
        }
        with self._lock:
            self._jobs[job_id] = job_record

        worker = threading.Thread(
            target=self._run_subprocess_job,
            args=(job_id, command),
            daemon=True,
            name=f"local-job-{job_id}",
        )
        worker.start()
        return self.get_job(job_id) or job_record

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return dict(job)

    def list_jobs(
        self,
        *,
        kind_prefix: str | None = None,
        summary_filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            jobs = [dict(job) for job in self._jobs.values()]

        matched_jobs: list[dict[str, Any]] = []
        for job in jobs:
            if kind_prefix and not str(job.get("kind", "")).startswith(kind_prefix):
                continue

            if summary_filters:
                summary = job.get("summary", {})
                if not isinstance(summary, dict):
                    continue
                summary_mismatch = False
                for key, expected in summary_filters.items():
                    if str(summary.get(key, "")).strip() != str(expected).strip():
                        summary_mismatch = True
                        break
                if summary_mismatch:
                    continue

            matched_jobs.append(job)

        matched_jobs.sort(key=lambda job: str(job.get("created_at", "")), reverse=True)
        return matched_jobs

    def _run_subprocess_job(self, job_id: str, command: list[str]) -> None:
        self._update_job(
            job_id,
            status="running",
            started_at=_utc_now(),
        )

        env = os.environ.copy()
        env.setdefault("MOYUAN_SKILLS_REPO_ROOT", str(self._settings.repo_root))
        resolved_command = _resolve_subprocess_command(command)

        try:
            completed = subprocess.run(
                resolved_command,
                cwd=self._settings.repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                check=False,
            )
        except Exception as exc:  # pragma: no cover - defensive path
            self._update_job(
                job_id,
                status="failed",
                finished_at=_utc_now(),
                error=str(exc),
                stderr=str(exc),
                exit_code=-1,
            )
            return

        self._update_job(
            job_id,
            status="succeeded" if completed.returncode == 0 else "failed",
            finished_at=_utc_now(),
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )

    def _update_job(self, job_id: str, **updates: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.update(updates)


def resolve_local_target_path(repo_root: Path, value: str | None, default_relative: str) -> Path:
    raw_value = (value or "").strip()
    candidate = Path(raw_value) if raw_value else Path(default_relative)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate.resolve()
