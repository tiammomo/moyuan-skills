'use client';

import { useEffect, useState } from 'react';
import type { LocalBackendStatus, LocalJobRecord } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface LocalExecutionCardProps {
  panelTestId: string;
  title: string;
  description: string;
  requestPath: '/api/local/skills/install' | '/api/local/bundles/install';
  requestBody: Record<string, unknown>;
  fallbackNote: string;
}

function formatValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'boolean') {
    return value ? 'yes' : 'no';
  }
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  return String(value);
}

function truncateOutput(value: string): string {
  const normalized = value.trim();
  if (normalized.length <= 800) {
    return normalized;
  }
  return `...${normalized.slice(-800)}`;
}

function formatStatus(status: LocalJobRecord['status'] | 'idle'): string {
  if (status === 'idle') {
    return 'Ready to run';
  }
  if (status === 'queued') {
    return 'Queued';
  }
  if (status === 'running') {
    return 'Running';
  }
  if (status === 'succeeded') {
    return 'Succeeded';
  }
  return 'Failed';
}

export function LocalExecutionCard({
  panelTestId,
  title,
  description,
  requestPath,
  requestBody,
  fallbackNote,
}: LocalExecutionCardProps) {
  const [availability, setAvailability] = useState<LocalBackendStatus | null>(null);
  const [job, setJob] = useState<LocalJobRecord | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState<'install' | 'dry-run' | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadAvailability() {
      try {
        const response = await fetch('/api/local/status', {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalBackendStatus;
        if (!cancelled) {
          setAvailability(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setAvailability({
            available: false,
            configured: false,
            message: `Unable to reach the frontend local execution proxy: ${
              error instanceof Error ? error.message : String(error)
            }`,
          });
        }
      }
    }

    void loadAvailability();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!job || (job.status !== 'queued' && job.status !== 'running')) {
      return undefined;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${job.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        if (!cancelled) {
          setJob(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            `Unable to refresh job status: ${error instanceof Error ? error.message : String(error)}`
          );
        }
      }
    }, 700);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [job]);

  useEffect(() => {
    if (job?.status === 'succeeded' || job?.status === 'failed') {
      setActiveMode(null);
    }
  }, [job?.status]);

  async function runExecution(dryRun: boolean) {
    setErrorMessage(null);
    setActiveMode(dryRun ? 'dry-run' : 'install');

    try {
      const response = await fetch(requestPath, {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          ...requestBody,
          dry_run: dryRun,
        }),
      });

      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setJob(null);
        setActiveMode(null);
        setErrorMessage(payload && 'detail' in payload ? payload.detail ?? 'Local execution failed.' : 'Local execution failed.');
        return;
      }

      setJob(payload as LocalJobRecord);
    } catch (error) {
      setJob(null);
      setActiveMode(null);
      setErrorMessage(`Local execution request failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  const buttonsDisabled = !availability?.available || activeMode !== null;
  const status = formatStatus(job?.status ?? 'idle');
  const statusVariant =
    job?.status === 'succeeded' ? 'keyword' : job?.status === 'failed' ? 'internal' : 'tag';

  const summaryEntries = job
    ? [
        ...Object.entries(job.summary),
        ...Object.entries(job.artifacts),
      ]
    : [];

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="mb-5 space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Chip variant="keyword">Backend execution</Chip>
          <Chip variant="tag">Copy fallback stays available</Chip>
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{title}</h3>
          <p className="text-sm text-muted">{description}</p>
        </div>
        <p className="text-xs text-muted" data-testid={`${panelTestId}-fallback-note`}>
          {fallbackNote}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Button
          type="button"
          onClick={() => runExecution(false)}
          disabled={buttonsDisabled}
          data-testid={`${panelTestId}-run`}
        >
          {activeMode === 'install' && (!job || job.status === 'queued' || job.status === 'running')
            ? 'Running install...'
            : 'Run via backend'}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => runExecution(true)}
          disabled={buttonsDisabled}
          data-testid={`${panelTestId}-dry-run`}
        >
          {activeMode === 'dry-run' && (!job || job.status === 'queued' || job.status === 'running')
            ? 'Running dry-run...'
            : 'Dry run via backend'}
        </Button>
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Chip variant={statusVariant} data-testid={`${panelTestId}-status`}>
            {status}
          </Chip>
          {availability && (
            <span className="text-xs text-muted" data-testid={`${panelTestId}-availability`}>
              {availability.message}
            </span>
          )}
        </div>

        {errorMessage && (
          <div className="rounded-card border border-line bg-bg/70 px-3 py-3 text-xs text-ink" data-testid={`${panelTestId}-error`}>
            {errorMessage}
          </div>
        )}

        {job && (
          <div className="space-y-3">
            <div
              className="rounded-card border border-line bg-bg/70 px-3 py-3"
              data-testid={`${panelTestId}-summary`}
            >
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Job summary</p>
              <dl className="mt-2 space-y-2 text-xs text-ink">
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Job ID</dt>
                  <dd className="font-mono text-right">{job.job_id}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Command</dt>
                  <dd className="font-mono text-right break-all">{job.command_text}</dd>
                </div>
                {summaryEntries.map(([key, value]) => (
                  <div key={key} className="flex justify-between gap-3">
                    <dt className="text-muted">{key.replace(/_/g, ' ')}</dt>
                    <dd className="text-right break-all">{formatValue(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>

            {job.stdout.trim() && (
              <div className="rounded-card border border-line bg-bg/70 px-3 py-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">stdout snippet</p>
                <pre
                  className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink"
                  data-testid={`${panelTestId}-stdout`}
                >
                  <code>{truncateOutput(job.stdout)}</code>
                </pre>
              </div>
            )}

            {job.stderr.trim() && (
              <div className="rounded-card border border-line bg-bg/70 px-3 py-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">stderr snippet</p>
                <pre
                  className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink"
                  data-testid={`${panelTestId}-stderr`}
                >
                  <code>{truncateOutput(job.stderr)}</code>
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
