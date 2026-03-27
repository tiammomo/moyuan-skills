'use client';

import { useEffect, useState } from 'react';
import type { LocalBackendStatus, LocalJobRecord, RemoteExecutionTrustSummary } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { Input } from '@/components/ui/Input';

export type ExecutionRequestPath =
  | '/api/local/skills/install'
  | '/api/local/skills/update'
  | '/api/local/skills/remove'
  | '/api/local/bundles/install'
  | '/api/local/bundles/update'
  | '/api/local/bundles/remove'
  | '/api/registry/cleanup'
  | '/api/registry/skills/install'
  | '/api/registry/bundles/install';

export interface ExecutionField {
  name: string;
  label: string;
  description?: string;
  placeholder?: string;
  defaultValue?: string;
  required?: boolean;
}

export interface LocalExecutionCardProps {
  panelTestId: string;
  title: string;
  description: string;
  requestPath: ExecutionRequestPath;
  requestBody: Record<string, unknown>;
  fallbackNote: string;
  modeLabel?: string;
  badges?: string[];
  fields?: ExecutionField[];
  runButtonLabel?: string;
  dryRunButtonLabel?: string;
  runningLabel?: string;
  dryRunRunningLabel?: string;
  remoteTrust?: RemoteExecutionTrustSummary | null;
  cleanupRequestPath?: ExecutionRequestPath;
  cleanupRequestBody?: Record<string, unknown>;
  onJobSettled?: (job: LocalJobRecord) => void;
}

interface RecoveryDescriptor {
  kind: 'download' | 'trust' | 'installer' | 'request';
  title: string;
  summary: string;
  hints: string[];
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

function isRegistryExecutionPath(path: ExecutionRequestPath): boolean {
  return path === '/api/registry/skills/install' || path === '/api/registry/bundles/install';
}

function detectRecoveryDescriptor(job: LocalJobRecord | null, errorMessage: string | null): RecoveryDescriptor | null {
  const source = [errorMessage, job?.error, job?.stderr, job?.stdout].filter(Boolean).join('\n').toLowerCase();

  if (!(job?.status === 'failed') && !errorMessage) {
    return null;
  }

  if (
    source.includes('recovery_kind: download') ||
    source.includes('unable to fetch remote json payload') ||
    source.includes('failed to fetch') ||
    source.includes('connection refused') ||
    source.includes('no connection could be made') ||
    source.includes('timed out') ||
    source.includes('404') ||
    source.includes('name or service not known') ||
    source.includes('无法连接')
  ) {
    return {
      kind: 'download',
      title: 'Remote download failed',
      summary: 'The backend could not resolve or download the remote registry payload with the current registry settings.',
      hints: [
        'Check the registry URL and make sure the hosted registry is reachable from the backend.',
        'Retry after the registry fixture or remote host is available again.',
        'Use cleanup if you want to clear partially staged cache or target files before retrying.',
      ],
    };
  }

  if (
    source.includes('recovery_kind: trust') ||
    source.includes('checksum mismatch') ||
    source.includes('provenance') ||
    source.includes("marked as 'archived'") ||
    source.includes("lifecycle status 'blocked'") ||
    source.includes('not installable') ||
    source.includes('human review')
  ) {
    return {
      kind: 'trust',
      title: 'Trust or lifecycle check failed',
      summary: 'The remote artifact resolved, but the local install step stopped because a lifecycle or trust rule was not satisfied.',
      hints: [
        'Review the trust summary, lifecycle status, and provenance hints before retrying.',
        'Choose a different skill or bundle version if the current one is blocked, archived, or otherwise not installable.',
        'Use cleanup if you want to reset staged files before trying a safer target.',
      ],
    };
  }

  if (errorMessage) {
    return {
      kind: 'request',
      title: 'Frontend request failed',
      summary: errorMessage,
      hints: [
        'Check the backend proxy health and the required form fields before retrying.',
        'If the request reached the backend earlier, use cleanup to clear any partially staged files.',
      ],
    };
  }

  return {
    kind: 'installer',
    title: 'Installer failed after staging',
    summary: 'The remote payload was staged, but the downstream local installer still failed to complete cleanly.',
    hints: [
      'Review stdout and stderr to see whether the failure happened during extraction or lockfile reconciliation.',
      'Use cleanup to remove staged cache and target files before retrying.',
      'Keep the copy-first CLI fallback available if you want to rerun the exact command manually.',
    ],
  };
}

export function LocalExecutionCard({
  panelTestId,
  title,
  description,
  requestPath,
  requestBody,
  fallbackNote,
  modeLabel = 'Backend execution',
  badges = ['Copy fallback stays available'],
  fields = [],
  runButtonLabel = 'Run via backend',
  dryRunButtonLabel = 'Dry run via backend',
  runningLabel = 'Running...',
  dryRunRunningLabel = 'Running dry run...',
  remoteTrust = null,
  cleanupRequestPath,
  cleanupRequestBody,
  onJobSettled,
}: LocalExecutionCardProps) {
  const [availability, setAvailability] = useState<LocalBackendStatus | null>(null);
  const [job, setJob] = useState<LocalJobRecord | null>(null);
  const [recoveryJob, setRecoveryJob] = useState<LocalJobRecord | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState<'install' | 'dry-run' | null>(null);
  const [recoveryMode, setRecoveryMode] = useState<'cleanup' | null>(null);
  const [reportedCompletionJobId, setReportedCompletionJobId] = useState<string | null>(null);
  const [approvalChecked, setApprovalChecked] = useState(false);
  const [lastSubmittedDryRun, setLastSubmittedDryRun] = useState<boolean | null>(null);
  const [fieldValues, setFieldValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(fields.map((field) => [field.name, field.defaultValue ?? '']))
  );

  const approvalRequired = Boolean(remoteTrust?.approval_required);
  const approvalMissing = approvalRequired && !approvalChecked;
  const isRegistryExecution = isRegistryExecutionPath(requestPath);

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
            message: `Unable to reach the frontend backend execution proxy: ${
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
    if (!recoveryJob || (recoveryJob.status !== 'queued' && recoveryJob.status !== 'running')) {
      return undefined;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${recoveryJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        if (!cancelled) {
          setRecoveryJob(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            `Unable to refresh recovery job status: ${error instanceof Error ? error.message : String(error)}`
          );
        }
      }
    }, 700);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [recoveryJob]);

  useEffect(() => {
    setFieldValues((currentValues) => {
      const nextValues = { ...currentValues };
      let changed = false;

      for (const field of fields) {
        if (!(field.name in nextValues)) {
          nextValues[field.name] = field.defaultValue ?? '';
          changed = true;
        }
      }

      for (const key of Object.keys(nextValues)) {
        if (!fields.some((field) => field.name === key)) {
          delete nextValues[key];
          changed = true;
        }
      }

      return changed ? nextValues : currentValues;
    });
  }, [fields]);

  useEffect(() => {
    if (job?.status === 'succeeded' || job?.status === 'failed') {
      setActiveMode(null);
    }
  }, [job?.status]);

  useEffect(() => {
    if (recoveryJob?.status === 'succeeded' || recoveryJob?.status === 'failed') {
      setRecoveryMode(null);
    }
  }, [recoveryJob?.status]);

  useEffect(() => {
    if (!job || (job.status !== 'succeeded' && job.status !== 'failed')) {
      return;
    }
    if (reportedCompletionJobId === job.job_id) {
      return;
    }
    setReportedCompletionJobId(job.job_id);
    onJobSettled?.(job);
  }, [job, onJobSettled, reportedCompletionJobId]);

  function updateFieldValue(fieldName: string, value: string) {
    setFieldValues((currentValues) => ({
      ...currentValues,
      [fieldName]: value,
    }));
  }

  async function runExecution(dryRun: boolean) {
    setErrorMessage(null);
    setRecoveryJob(null);
    setActiveMode(dryRun ? 'dry-run' : 'install');
    setLastSubmittedDryRun(dryRun);

    if (approvalMissing) {
      setActiveMode(null);
      setErrorMessage('Remote execution requires explicit approval before the backend job can start.');
      return;
    }

    const missingField = fields.find((field) => field.required && !(fieldValues[field.name] ?? '').trim());
    if (missingField) {
      setActiveMode(null);
      setErrorMessage(`${missingField.label} is required before this backend run can start.`);
      return;
    }

    try {
      const response = await fetch(requestPath, {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          ...requestBody,
          ...Object.fromEntries(
            Object.entries(fieldValues).map(([key, value]) => [key, value.trim()])
          ),
          dry_run: dryRun,
        }),
      });

      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setJob(null);
        setActiveMode(null);
        setReportedCompletionJobId(null);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Backend execution failed.' : 'Backend execution failed.'
        );
        return;
      }

      setJob(payload as LocalJobRecord);
      setReportedCompletionJobId(null);
    } catch (error) {
      setJob(null);
      setActiveMode(null);
      setReportedCompletionJobId(null);
      setErrorMessage(`Backend execution request failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async function runCleanup() {
    if (!cleanupRequestPath || !cleanupRequestBody) {
      return;
    }

    setErrorMessage(null);
    setRecoveryMode('cleanup');

    try {
      const response = await fetch(cleanupRequestPath, {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify(cleanupRequestBody),
      });

      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setRecoveryJob(null);
        setRecoveryMode(null);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Remote cleanup failed.' : 'Remote cleanup failed.'
        );
        return;
      }

      setRecoveryJob(payload as LocalJobRecord);
    } catch (error) {
      setRecoveryJob(null);
      setRecoveryMode(null);
      setErrorMessage(`Remote cleanup request failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  const buttonsDisabled = !availability?.available || activeMode !== null || approvalMissing;
  const recoveryButtonsDisabled = !availability?.available || recoveryMode !== null;
  const status = formatStatus(job?.status ?? 'idle');
  const statusVariant =
    job?.status === 'succeeded' ? 'keyword' : job?.status === 'failed' ? 'internal' : 'tag';
  const recoveryDescriptor = isRegistryExecution ? detectRecoveryDescriptor(job, errorMessage) : null;
  const canRetry = Boolean(recoveryDescriptor) && lastSubmittedDryRun !== null;
  const canCleanup = Boolean(recoveryDescriptor) && Boolean(cleanupRequestPath && cleanupRequestBody);

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
          <Chip variant="keyword">{modeLabel}</Chip>
          {badges.map((badge) => (
            <Chip key={badge} variant="tag">
              {badge}
            </Chip>
          ))}
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{title}</h3>
          <p className="text-sm text-muted">{description}</p>
        </div>
        <p className="text-xs text-muted" data-testid={`${panelTestId}-fallback-note`}>
          {fallbackNote}
        </p>
      </div>

      {remoteTrust && (
        <div
          className="mb-4 rounded-card border border-line bg-bg/70 px-4 py-4"
          data-testid={`${panelTestId}-trust`}
        >
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
            {remoteTrust.title}
          </p>
          <dl className="mt-3 space-y-2 text-xs text-ink">
            {remoteTrust.entries.map((entry) => (
              <div key={`${entry.label}-${entry.value}`} className="flex justify-between gap-3">
                <dt className="text-muted">{entry.label}</dt>
                <dd
                  className={`text-right break-words ${
                    entry.tone === 'positive'
                      ? 'text-olive'
                      : entry.tone === 'warning' || entry.tone === 'critical'
                        ? 'text-accent'
                        : 'text-ink'
                  }`}
                >
                  {entry.value}
                </dd>
              </div>
            ))}
          </dl>
          {remoteTrust.warnings.length > 0 && (
            <div className="mt-3 space-y-2" data-testid={`${panelTestId}-trust-warnings`}>
            {remoteTrust.warnings.map((warning) => (
                <p
                  key={warning}
                  className="rounded-card border border-[#f0d4b8] bg-[#fff4e8] px-3 py-2 text-xs text-accent"
                >
                  {warning}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {fields.length > 0 && (
        <div className="mb-4 space-y-3">
          {fields.map((field) => (
            <div key={field.name} className="space-y-1">
              <Input
                label={field.label}
                value={fieldValues[field.name] ?? ''}
                onChange={(event) => updateFieldValue(field.name, event.target.value)}
                placeholder={field.placeholder}
                required={field.required}
                data-testid={`${panelTestId}-field-${field.name}`}
              />
              {field.description && (
                <p className="text-xs text-muted" data-testid={`${panelTestId}-field-${field.name}-description`}>
                  {field.description}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {approvalRequired && (
        <div
          className="mb-4 rounded-card border border-line bg-bg/70 px-4 py-4"
          data-testid={`${panelTestId}-approval-panel`}
        >
          <label className="flex items-start gap-3 text-sm text-ink">
            <input
              type="checkbox"
              checked={approvalChecked}
              onChange={(event) => setApprovalChecked(event.target.checked)}
              className="mt-1 h-4 w-4 rounded border border-line"
              data-testid={`${panelTestId}-approval-checkbox`}
            />
            <span>{remoteTrust?.approval_label}</span>
          </label>
          {remoteTrust?.approval_help && (
            <p className="mt-2 text-xs text-muted" data-testid={`${panelTestId}-approval-help`}>
              {remoteTrust.approval_help}
            </p>
          )}
          <p className="mt-2 text-xs text-muted" data-testid={`${panelTestId}-approval-state`}>
            {approvalMissing ? 'Waiting for explicit approval before remote execution.' : 'Approval captured for remote execution.'}
          </p>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <Button
          type="button"
          onClick={() => runExecution(false)}
          disabled={buttonsDisabled}
          data-testid={`${panelTestId}-run`}
        >
          {activeMode === 'install' && (!job || job.status === 'queued' || job.status === 'running')
            ? runningLabel
            : runButtonLabel}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => runExecution(true)}
          disabled={buttonsDisabled}
          data-testid={`${panelTestId}-dry-run`}
        >
          {activeMode === 'dry-run' && (!job || job.status === 'queued' || job.status === 'running')
            ? dryRunRunningLabel
            : dryRunButtonLabel}
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

        {recoveryDescriptor && (
          <div
            className="rounded-card border border-[#f0d4b8] bg-[#fff4e8] px-4 py-4"
            data-testid={`${panelTestId}-recovery`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant="beta" data-testid={`${panelTestId}-recovery-kind`}>
                {recoveryDescriptor.kind}
              </Chip>
              <p className="text-sm font-semibold text-ink">{recoveryDescriptor.title}</p>
            </div>
            <p className="mt-2 text-sm text-ink" data-testid={`${panelTestId}-recovery-summary`}>
              {recoveryDescriptor.summary}
            </p>
            <div className="mt-3 space-y-1 text-xs text-ink" data-testid={`${panelTestId}-recovery-hints`}>
              {recoveryDescriptor.hints.map((hint) => (
                <p key={hint}>{hint}</p>
              ))}
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              {canRetry && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => runExecution(Boolean(lastSubmittedDryRun))}
                  disabled={buttonsDisabled}
                  data-testid={`${panelTestId}-retry`}
                >
                  Retry last remote run
                </Button>
              )}
              {canCleanup && (
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => void runCleanup()}
                  disabled={recoveryButtonsDisabled}
                  data-testid={`${panelTestId}-cleanup`}
                >
                  {recoveryMode === 'cleanup' ? 'Cleaning up...' : 'Clean staged remote files'}
                </Button>
              )}
            </div>

            {recoveryJob && (
              <div className="mt-4 rounded-card border border-line bg-paper/70 px-3 py-3" data-testid={`${panelTestId}-cleanup-summary`}>
                <div className="flex flex-wrap items-center gap-2">
                  <Chip
                    variant={recoveryJob.status === 'succeeded' ? 'keyword' : recoveryJob.status === 'failed' ? 'internal' : 'tag'}
                    data-testid={`${panelTestId}-cleanup-status`}
                  >
                    {formatStatus(recoveryJob.status)}
                  </Chip>
                  <span className="text-xs text-muted">Cleanup job</span>
                </div>
                <dl className="mt-2 space-y-2 text-xs text-ink">
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Job ID</dt>
                    <dd className="font-mono text-right">{recoveryJob.job_id}</dd>
                  </div>
                  {Object.entries({ ...recoveryJob.summary, ...recoveryJob.artifacts }).map(([key, value]) => (
                    <div key={key} className="flex justify-between gap-3">
                      <dt className="text-muted">{key.replace(/_/g, ' ')}</dt>
                      <dd className="text-right break-all">{formatValue(value)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
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
