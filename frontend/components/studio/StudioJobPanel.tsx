'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { LocalBackendStatus, LocalJobRecord } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export type StudioRequestPath =
  | '/api/author/submissions/build'
  | '/api/author/submissions/upload'
  | '/api/author/submissions/review'
  | '/api/author/submissions/ingest';

type StudioFieldOption = {
  label: string;
  value: string;
};

export interface StudioField {
  name: string;
  label: string;
  description?: string;
  placeholder?: string;
  defaultValue?: string;
  required?: boolean;
  type?: 'text' | 'textarea' | 'select';
  options?: StudioFieldOption[];
}

interface StudioJobPanelProps {
  panelTestId: string;
  title: string;
  description: string;
  requestPath: StudioRequestPath;
  requestBody?: Record<string, unknown>;
  fields?: StudioField[];
  runButtonLabel?: string;
  runningLabel?: string;
  footnote?: string;
  refreshOnSettled?: boolean;
}

const TERMINAL_STATUSES = new Set<LocalJobRecord['status']>(['succeeded', 'failed']);

function truncateOutput(value: string): string {
  const normalized = value.trim();
  if (normalized.length <= 1200) {
    return normalized;
  }
  return `${normalized.slice(0, 1200)}\n...\n(output truncated)`;
}

function formatStatus(status: LocalJobRecord['status'] | 'idle'): string {
  if (status === 'idle') {
    return 'Ready';
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

function statusClasses(status: LocalJobRecord['status'] | 'idle'): string {
  if (status === 'succeeded') {
    return 'bg-[color:var(--olive)] text-[color:var(--paper)]';
  }
  if (status === 'failed') {
    return 'bg-[color:var(--accent)] text-[color:var(--paper)]';
  }
  if (status === 'running' || status === 'queued') {
    return 'bg-[color:var(--accent-soft)] text-[color:var(--ink)]';
  }
  return 'bg-[color:var(--paper)] text-[color:var(--ink)] border border-[color:var(--line)]';
}

export function StudioJobPanel({
  panelTestId,
  title,
  description,
  requestPath,
  requestBody = {},
  fields = [],
  runButtonLabel = 'Run via backend',
  runningLabel = 'Running...',
  footnote,
  refreshOnSettled = true,
}: StudioJobPanelProps) {
  const router = useRouter();
  const [availability, setAvailability] = useState<LocalBackendStatus | null>(null);
  const [job, setJob] = useState<LocalJobRecord | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [fieldValues, setFieldValues] = useState<Record<string, string>>(
    Object.fromEntries(fields.map((field) => [field.name, field.defaultValue ?? '']))
  );

  useEffect(() => {
    let cancelled = false;

    async function loadAvailability() {
      try {
        const response = await fetch('/api/local/status', { cache: 'no-store' });
        const payload = (await response.json()) as LocalBackendStatus;
        if (!cancelled) {
          setAvailability(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setAvailability({
            available: false,
            configured: false,
            message: error instanceof Error ? error.message : String(error),
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
    if (!job || TERMINAL_STATUSES.has(job.status)) {
      return;
    }

    let cancelled = false;
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${job.job_id}`, { cache: 'no-store' });
        const payload = (await response.json()) as LocalJobRecord;
        if (!cancelled) {
          setJob(payload);
          if (TERMINAL_STATUSES.has(payload.status)) {
            setSubmitting(false);
            if (refreshOnSettled) {
              router.refresh();
            }
          }
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(error instanceof Error ? error.message : String(error));
          setSubmitting(false);
        }
      }
    }, 1000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [job, refreshOnSettled, router]);

  function updateFieldValue(name: string, value: string) {
    setFieldValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function runExecution() {
    setErrorMessage(null);

    for (const field of fields) {
      if (field.required && !(fieldValues[field.name] ?? '').trim()) {
        setErrorMessage(`Field "${field.label}" is required.`);
        return;
      }
    }

    setSubmitting(true);
    try {
      const response = await fetch(requestPath, {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          ...requestBody,
          ...fieldValues,
        }),
      });
      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setErrorMessage('detail' in payload ? payload.detail || 'Request failed.' : 'Request failed.');
        setSubmitting(false);
        return;
      }
      setJob(payload as LocalJobRecord);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : String(error));
      setSubmitting(false);
    }
  }

  const status = formatStatus(job?.status ?? 'idle');

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-ink">{title}</h3>
          <p className="mt-2 text-sm text-muted">{description}</p>
        </div>
        <span
          className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(job?.status ?? 'idle')}`}
          data-testid={`${panelTestId}-status`}
        >
          {status}
        </span>
      </div>

      {fields.length > 0 && (
        <div className="mt-5 space-y-4">
          {fields.map((field) => {
            const value = fieldValues[field.name] ?? '';
            if (field.type === 'textarea') {
              return (
                <div key={field.name} className="space-y-1.5">
                  <label className="text-sm font-medium text-ink" htmlFor={`${panelTestId}-${field.name}`}>
                    {field.label}
                  </label>
                  <textarea
                    id={`${panelTestId}-${field.name}`}
                    value={value}
                    onChange={(event) => updateFieldValue(field.name, event.target.value)}
                    placeholder={field.placeholder}
                    className="min-h-28 w-full rounded-card border border-line bg-paper px-4 py-3 text-sm text-ink placeholder:text-muted/60 focus:border-olive focus:outline-none focus:ring-2 focus:ring-olive/20"
                    data-testid={`${panelTestId}-field-${field.name}`}
                  />
                  {field.description && <p className="text-xs text-muted">{field.description}</p>}
                </div>
              );
            }

            if (field.type === 'select') {
              return (
                <div key={field.name} className="space-y-1.5">
                  <label className="text-sm font-medium text-ink" htmlFor={`${panelTestId}-${field.name}`}>
                    {field.label}
                  </label>
                  <select
                    id={`${panelTestId}-${field.name}`}
                    value={value}
                    onChange={(event) => updateFieldValue(field.name, event.target.value)}
                    className="w-full rounded-card border border-line bg-paper px-4 py-2.5 text-sm text-ink focus:border-olive focus:outline-none focus:ring-2 focus:ring-olive/20"
                    data-testid={`${panelTestId}-field-${field.name}`}
                  >
                    {(field.options ?? []).map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  {field.description && <p className="text-xs text-muted">{field.description}</p>}
                </div>
              );
            }

            return (
              <div key={field.name} className="space-y-1.5">
                <Input
                  label={field.label}
                  value={value}
                  onChange={(event) => updateFieldValue(field.name, event.target.value)}
                  placeholder={field.placeholder}
                  data-testid={`${panelTestId}-field-${field.name}`}
                />
                {field.description && <p className="text-xs text-muted">{field.description}</p>}
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <Button
          type="button"
          onClick={() => void runExecution()}
          disabled={!availability?.available || submitting}
          data-testid={`${panelTestId}-run`}
        >
          {submitting ? runningLabel : runButtonLabel}
        </Button>
        {availability && (
          <p className="text-xs text-muted" data-testid={`${panelTestId}-availability`}>
            {availability.message}
          </p>
        )}
      </div>

      {footnote && <p className="mt-3 text-xs text-muted">{footnote}</p>}

      {errorMessage && (
        <div className="mt-4 rounded-card border border-line bg-[color:var(--paper)] px-4 py-3 text-sm text-ink" data-testid={`${panelTestId}-error`}>
          {errorMessage}
        </div>
      )}

      {job && (
        <div className="mt-5 space-y-4">
          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-wide text-muted">Job</dt>
              <dd className="font-mono text-ink">{job.job_id}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-muted">Kind</dt>
              <dd className="text-ink">{job.kind}</dd>
            </div>
          </dl>

          <div className="rounded-card border border-line bg-[color:var(--bg)] px-4 py-3">
            <p className="text-xs uppercase tracking-wide text-muted">Command</p>
            <pre className="mt-2 overflow-x-auto text-xs text-ink">{job.command_text}</pre>
          </div>

          {job.stdout.trim() && (
            <div className="rounded-card border border-line bg-[color:var(--paper)] px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-muted">Stdout</p>
              <pre className="mt-2 overflow-x-auto text-xs text-ink">{truncateOutput(job.stdout)}</pre>
            </div>
          )}

          {job.stderr.trim() && (
            <div className="rounded-card border border-line bg-[color:var(--paper)] px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-muted">Stderr</p>
              <pre className="mt-2 overflow-x-auto text-xs text-ink">{truncateOutput(job.stderr)}</pre>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
