'use client';

import { useEffect, useState } from 'react';
import type {
  LocalInstalledDoctorFinding,
  LocalInstalledDoctorSnapshot,
  LocalInstalledRepairPayload,
  LocalJobRecord,
} from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface InstalledDoctorPanelProps {
  panelTestId: string;
  targetRoot: string;
  onRepairSettled?: () => void;
}

function parseJobPayload<T>(job: LocalJobRecord): T {
  return JSON.parse(job.stdout.trim()) as T;
}

function jobFailureMessage(job: LocalJobRecord, fallback: string): string {
  if (job.error) {
    return job.error;
  }
  if (job.stderr.trim()) {
    return job.stderr.trim();
  }
  return fallback;
}

function formatScopeLabel(finding: LocalInstalledDoctorFinding): string {
  const scopeParts = [finding.skill_id, finding.bundle_id].filter(Boolean);
  return scopeParts.length > 0 ? scopeParts.join(' / ') : finding.kind;
}

function describeHealth(snapshot: LocalInstalledDoctorSnapshot | null): {
  label: string;
  variant: 'keyword' | 'beta' | 'internal' | 'tag';
  note: string;
} {
  if (!snapshot) {
    return {
      label: 'Doctor not run yet',
      variant: 'tag',
      note: 'Run the installed-state doctor to see whether this target root is healthy, drifted, or needs manual review.',
    };
  }

  if (snapshot.summary.doctor_finding_count === 0) {
    return {
      label: 'Healthy',
      variant: 'keyword',
      note: 'No installed-state drift is currently detected for this target root.',
    };
  }

  if (snapshot.summary.repairable_finding_count > 0 && snapshot.summary.skipped_finding_count > 0) {
    return {
      label: 'Repairable drift + manual review',
      variant: 'beta',
      note: 'The doctor found low-risk drift that can be repaired now, plus higher-risk findings that still need manual review.',
    };
  }

  if (snapshot.summary.repairable_finding_count > 0) {
    return {
      label: 'Repairable drift',
      variant: 'beta',
      note: 'The doctor found low-risk drift that the frontend can hand off to repair.',
    };
  }

  return {
    label: 'Manual review needed',
    variant: 'internal',
    note: 'The doctor found drift, but this first frontend repair pass does not change it automatically.',
  };
}

export function InstalledDoctorPanel({ panelTestId, targetRoot, onRepairSettled }: InstalledDoctorPanelProps) {
  const [doctorJob, setDoctorJob] = useState<LocalJobRecord | null>(null);
  const [repairJob, setRepairJob] = useState<LocalJobRecord | null>(null);
  const [doctorSnapshot, setDoctorSnapshot] = useState<LocalInstalledDoctorSnapshot | null>(null);
  const [repairPayload, setRepairPayload] = useState<LocalInstalledRepairPayload | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [doctorPending, setDoctorPending] = useState(false);
  const [repairPending, setRepairPending] = useState(false);

  useEffect(() => {
    setDoctorJob(null);
    setRepairJob(null);
    setDoctorSnapshot(null);
    setRepairPayload(null);
    setErrorMessage(null);
    setDoctorPending(false);
    setRepairPending(false);
  }, [targetRoot]);

  useEffect(() => {
    if (!doctorJob || (doctorJob.status !== 'queued' && doctorJob.status !== 'running')) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${doctorJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        setDoctorJob(payload);
      } catch (error) {
        setDoctorPending(false);
        setErrorMessage(
          `Unable to refresh doctor job status: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }, 700);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [doctorJob]);

  useEffect(() => {
    if (!repairJob || (repairJob.status !== 'queued' && repairJob.status !== 'running')) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${repairJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        setRepairJob(payload);
      } catch (error) {
        setRepairPending(false);
        setErrorMessage(
          `Unable to refresh repair job status: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }, 700);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [repairJob]);

  useEffect(() => {
    if (!doctorJob || (doctorJob.status !== 'succeeded' && doctorJob.status !== 'failed')) {
      return;
    }

    setDoctorPending(false);
    if (doctorJob.status === 'failed') {
      setErrorMessage(jobFailureMessage(doctorJob, 'Installed-state doctor failed.'));
      return;
    }

    try {
      setDoctorSnapshot(parseJobPayload<LocalInstalledDoctorSnapshot>(doctorJob));
    } catch (error) {
      setErrorMessage(
        `Unable to parse installed-state doctor output: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }, [doctorJob]);

  useEffect(() => {
    if (!repairJob || (repairJob.status !== 'succeeded' && repairJob.status !== 'failed')) {
      return;
    }

    setRepairPending(false);
    if (repairJob.status === 'failed') {
      setErrorMessage(jobFailureMessage(repairJob, 'Installed-state repair failed.'));
      return;
    }

    try {
      setRepairPayload(parseJobPayload<LocalInstalledRepairPayload>(repairJob));
      onRepairSettled?.();
      void runDoctor();
    } catch (error) {
      setErrorMessage(
        `Unable to parse installed-state repair output: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }, [repairJob]);

  async function runDoctor() {
    setErrorMessage(null);
    setDoctorPending(true);

    try {
      const response = await fetch('/api/local/state/doctor', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          target_root: targetRoot,
          scope: panelTestId,
        }),
      });

      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setDoctorPending(false);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Installed-state doctor failed.' : 'Installed-state doctor failed.'
        );
        return;
      }

      setDoctorJob(payload as LocalJobRecord);
    } catch (error) {
      setDoctorPending(false);
      setErrorMessage(
        `Installed-state doctor request failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  async function runRepair() {
    setErrorMessage(null);
    setRepairPending(true);

    try {
      const response = await fetch('/api/local/state/repair', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          target_root: targetRoot,
          scope: panelTestId,
        }),
      });

      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setRepairPending(false);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Installed-state repair failed.' : 'Installed-state repair failed.'
        );
        return;
      }

      setRepairJob(payload as LocalJobRecord);
    } catch (error) {
      setRepairPending(false);
      setErrorMessage(
        `Installed-state repair request failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  const health = describeHealth(doctorSnapshot);
  const repairableCount = doctorSnapshot?.summary.repairable_finding_count ?? 0;
  const skippedCount = doctorSnapshot?.summary.skipped_finding_count ?? 0;
  const buttonsDisabled = doctorPending || repairPending;

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Chip variant={health.variant} data-testid={`${panelTestId}-status`}>
              {health.label}
            </Chip>
            <Chip variant="tag">Installed-state doctor</Chip>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">Health check</h3>
            <p className="text-sm text-muted" data-testid={`${panelTestId}-note`}>
              {health.note}
            </p>
          </div>
          <p className="text-xs text-muted" data-testid={`${panelTestId}-fallback-note`}>
            Low-risk repair only removes orphan install directories and stale bundle reports. Higher-risk findings still stay copy-first and review-first.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={() => void runDoctor()}
            disabled={buttonsDisabled}
            data-testid={`${panelTestId}-run`}
          >
            {doctorPending ? 'Checking...' : doctorSnapshot ? 'Check again' : 'Run doctor check'}
          </Button>
          {repairableCount > 0 && (
            <Button
              type="button"
              onClick={() => void runRepair()}
              disabled={buttonsDisabled}
              data-testid={`${panelTestId}-repair`}
            >
              {repairPending ? 'Repairing...' : 'Repair low-risk drift'}
            </Button>
          )}
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {errorMessage && (
          <div
            className="rounded-card border border-line bg-bg/70 px-3 py-3 text-xs text-ink"
            data-testid={`${panelTestId}-error`}
          >
            {errorMessage}
          </div>
        )}

        {doctorSnapshot && (
          <div
            className="rounded-card border border-line bg-bg/70 px-4 py-4"
            data-testid={`${panelTestId}-summary`}
          >
            <dl className="space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Target root</dt>
                <dd className="text-right break-all">{doctorSnapshot.target_root}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Doctor findings</dt>
                <dd>{doctorSnapshot.summary.doctor_finding_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Repairable findings</dt>
                <dd>{repairableCount}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Manual review findings</dt>
                <dd>{skippedCount}</dd>
              </div>
            </dl>

            {doctorSnapshot.repair_preview.orphan_directories.length > 0 && (
              <div className="mt-4 text-xs text-ink" data-testid={`${panelTestId}-orphan-directories`}>
                <p className="font-semibold text-ink">Repairable orphan directories</p>
                <div className="mt-1 space-y-1">
                  {doctorSnapshot.repair_preview.orphan_directories.map((directory) => (
                    <p key={directory} className="break-all">
                      {directory}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {doctorSnapshot.repair_preview.stale_bundle_reports.length > 0 && (
              <div className="mt-4 text-xs text-ink" data-testid={`${panelTestId}-stale-bundle-reports`}>
                <p className="font-semibold text-ink">Repairable stale bundle reports</p>
                <div className="mt-1 space-y-1">
                  {doctorSnapshot.repair_preview.stale_bundle_reports.map((report) => (
                    <p key={report.path} className="break-all">
                      {report.bundle_id}: {report.path}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {doctorSnapshot.doctor.findings.length > 0 && (
              <div className="mt-4 space-y-2 text-xs text-ink" data-testid={`${panelTestId}-findings`}>
                <p className="font-semibold text-ink">Doctor findings</p>
                {doctorSnapshot.doctor.findings.map((finding, index) => (
                  <div key={`${finding.kind}-${finding.message}-${index}`} className="rounded-card border border-line bg-paper/70 px-3 py-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <Chip variant={finding.severity === 'warning' ? 'beta' : 'internal'}>{finding.severity}</Chip>
                      <span className="font-semibold text-ink">{formatScopeLabel(finding)}</span>
                    </div>
                    <p className="mt-2 text-ink">{finding.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {repairPayload && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-repair-summary`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant="keyword">Repair applied</Chip>
              <p className="text-sm font-semibold text-ink">Low-risk repair summary</p>
            </div>
            <dl className="mt-3 space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Applied changes</dt>
                <dd>{repairPayload.applied_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Removed orphan directories</dt>
                <dd>{repairPayload.applied.removed_orphan_directories.length}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Removed bundle reports</dt>
                <dd>{repairPayload.applied.removed_bundle_reports.length}</dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </Card>
  );
}
