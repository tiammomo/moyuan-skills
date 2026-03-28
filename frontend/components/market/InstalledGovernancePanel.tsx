'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
  LocalInstalledGovernanceAction,
  LocalInstalledGovernanceState,
  LocalInstalledGovernanceSummary,
  LocalJobRecord,
} from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface InstalledGovernancePanelProps {
  panelTestId: string;
  targetRoot: string;
  refreshToken?: number;
  onGovernanceSettled?: () => void;
  onGovernanceStateChange?: (governanceState: LocalInstalledGovernanceState | null) => void;
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

function describeGovernanceState(
  governanceState: LocalInstalledGovernanceState | null
): {
  label: string;
  variant: 'keyword' | 'stable' | 'beta' | 'internal' | 'tag';
  note: string;
  canRefresh: boolean;
} {
  if (!governanceState?.history_exists) {
    return {
      label: 'No governance baseline yet',
      variant: 'tag',
      note: 'Capture a retained installed-state baseline first so governance review can summarize waiver, gate, and audit context for this target root.',
      canRefresh: false,
    };
  }

  if (!governanceState.summary_exists) {
    return {
      label: 'Governance review pending',
      variant: 'internal',
      note: 'A retained baseline history is available. Refresh governance to generate the first review-oriented summary pack for this target root.',
      canRefresh: true,
    };
  }

  return {
    label: 'Governance summary available',
    variant: 'keyword',
    note: 'The latest governance refresh has already generated review-oriented waiver, gate, and audit context for this target root.',
    canRefresh: true,
  };
}

function describeAction(action: LocalInstalledGovernanceAction): string {
  const notes = [
    action.source_audit_state ? `audit=${action.source_audit_state}` : '',
    action.source_reconcile_mode ? `reconcile=${action.source_reconcile_mode}` : '',
    action.verification_state ? `verify=${action.verification_state}` : '',
  ].filter(Boolean);
  return notes.length > 0 ? notes.join(', ') : 'review action recorded';
}

export function InstalledGovernancePanel({
  panelTestId,
  targetRoot,
  refreshToken,
  onGovernanceSettled,
  onGovernanceStateChange,
}: InstalledGovernancePanelProps) {
  const [governanceState, setGovernanceState] = useState<LocalInstalledGovernanceState | null>(null);
  const [governanceJob, setGovernanceJob] = useState<LocalJobRecord | null>(null);
  const [refreshPayload, setRefreshPayload] = useState<LocalInstalledGovernanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshPending, setRefreshPending] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadGovernanceState = useCallback(async () => {
    setErrorMessage(null);
    try {
      const response = await fetch(`/api/local/state/governance?target_root=${encodeURIComponent(targetRoot)}`, {
        cache: 'no-store',
      });
      const payload = (await response.json()) as LocalInstalledGovernanceState | { detail?: string };
      if (!response.ok) {
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Unable to read installed governance state.' : 'Unable to read installed governance state.'
        );
        setLoading(false);
        return;
      }
      setGovernanceState(payload as LocalInstalledGovernanceState);
      onGovernanceStateChange?.(payload as LocalInstalledGovernanceState);
      setLoading(false);
    } catch (error) {
      setErrorMessage(
        `Unable to read installed governance state: ${error instanceof Error ? error.message : String(error)}`
      );
      setLoading(false);
    }
  }, [onGovernanceStateChange, targetRoot]);

  const reloadGovernanceState = useCallback(() => {
    setLoading(true);
    void loadGovernanceState();
  }, [loadGovernanceState]);

  useEffect(() => {
    if (governanceState?.target_root !== targetRoot) {
      setGovernanceState(null);
      onGovernanceStateChange?.(null);
    }
    setGovernanceJob(null);
    setRefreshPayload(null);
    setLoading(true);
    setRefreshPending(false);
    setErrorMessage(null);
    void loadGovernanceState();
  }, [loadGovernanceState, onGovernanceStateChange, refreshToken, targetRoot]);

  useEffect(() => {
    if (!governanceJob || (governanceJob.status !== 'queued' && governanceJob.status !== 'running')) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${governanceJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        setGovernanceJob(payload);
      } catch (error) {
        setRefreshPending(false);
        setErrorMessage(
          `Unable to refresh governance job status: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }, 700);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [governanceJob]);

  useEffect(() => {
    if (!governanceJob || (governanceJob.status !== 'succeeded' && governanceJob.status !== 'failed')) {
      return;
    }

    setRefreshPending(false);
    if (governanceJob.status === 'failed') {
      setErrorMessage(jobFailureMessage(governanceJob, 'Installed governance refresh failed.'));
      return;
    }

    try {
      setRefreshPayload(parseJobPayload<LocalInstalledGovernanceSummary>(governanceJob));
      onGovernanceSettled?.();
      void loadGovernanceState();
    } catch (error) {
      setErrorMessage(
        `Unable to parse governance refresh output: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }, [governanceJob, loadGovernanceState, onGovernanceSettled]);

  async function runGovernanceRefresh() {
    setErrorMessage(null);
    setRefreshPending(true);

    try {
      const response = await fetch('/api/local/state/governance/refresh', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          target_root: targetRoot,
          policy: 'source-reconcile-review-handoff',
          scope: panelTestId,
        }),
      });

      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setRefreshPending(false);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Installed governance refresh failed.' : 'Installed governance refresh failed.'
        );
        return;
      }

      setGovernanceJob(payload as LocalJobRecord);
    } catch (error) {
      setRefreshPending(false);
      setErrorMessage(
        `Installed governance refresh request failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  const governanceDescription = useMemo(() => describeGovernanceState(governanceState), [governanceState]);
  const summary = governanceState?.latest_summary;
  const recentActions = useMemo(() => summary?.report.recent_actions ?? [], [summary?.report.recent_actions]);

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Chip variant={governanceDescription.variant} data-testid={`${panelTestId}-status`}>
              {governanceDescription.label}
            </Chip>
            <Chip variant="tag">Installed governance review</Chip>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">Governance summary</h3>
            <p className="text-sm text-muted" data-testid={`${panelTestId}-note`}>
              {governanceDescription.note}
            </p>
          </div>
          <p className="text-xs text-muted" data-testid={`${panelTestId}-fallback-note`}>
            This first governance pass stays review-oriented. The frontend can refresh waiver, gate, and audit context, while advanced waiver application and write-oriented flows remain copy-first outside this page.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={reloadGovernanceState}
            disabled={refreshPending}
            data-testid={`${panelTestId}-reload`}
          >
            Reload governance
          </Button>
          <Button
            type="button"
            onClick={() => void runGovernanceRefresh()}
            disabled={refreshPending || !governanceDescription.canRefresh}
            data-testid={`${panelTestId}-refresh`}
          >
            {refreshPending ? 'Refreshing governance...' : 'Refresh governance summary'}
          </Button>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {loading && (
          <p className="text-xs text-muted" data-testid={`${panelTestId}-loading`}>
            Loading governance summary...
          </p>
        )}

        {errorMessage && (
          <div
            className="rounded-card border border-line bg-bg/70 px-3 py-3 text-xs text-ink"
            data-testid={`${panelTestId}-error`}
          >
            {errorMessage}
          </div>
        )}

        {governanceState && (
          <div
            className="rounded-card border border-line bg-bg/70 px-4 py-4"
            data-testid={`${panelTestId}-summary`}
          >
            <dl className="space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">History path</dt>
                <dd className="text-right break-all">{governanceState.history_path}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Governance directory</dt>
                <dd className="text-right break-all">{governanceState.governance_dir}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">History alert waivers</dt>
                <dd>
                  {governanceState.profile_counts.history_alert_waivers.count}
                  {typeof governanceState.profile_counts.history_alert_waivers.active_count === 'number'
                    ? ` (${governanceState.profile_counts.history_alert_waivers.active_count} active)`
                    : ''}
                </dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Source-reconcile policies</dt>
                <dd>{governanceState.profile_counts.source_reconcile_policies.count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Source-reconcile gate waivers</dt>
                <dd>
                  {governanceState.profile_counts.source_reconcile_gate_waivers.count}
                  {typeof governanceState.profile_counts.source_reconcile_gate_waivers.active_count === 'number'
                    ? ` (${governanceState.profile_counts.source_reconcile_gate_waivers.active_count} active)`
                    : ''}
                </dd>
              </div>
              {summary && (
                <>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Latest governance refresh</dt>
                    <dd className="text-right break-all">{summary.generated_at}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Refresh summary path</dt>
                    <dd className="text-right break-all">{governanceState.summary_path}</dd>
                  </div>
                </>
              )}
            </dl>
          </div>
        )}

        {summary && (
          <>
            <div className="grid gap-3 lg:grid-cols-2">
              <div
                className="rounded-card border border-line bg-paper/70 px-4 py-4 text-xs text-ink"
                data-testid={`${panelTestId}-audit`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Chip variant={summary.audit.passes ? 'stable' : 'beta'}>Audit findings {summary.audit.finding_count}</Chip>
                  <p className="text-sm font-semibold text-ink">Waiver audit</p>
                </div>
                <dl className="mt-3 space-y-2">
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Audited waivers</dt>
                    <dd>{summary.audit.waiver_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Expired</dt>
                    <dd>{summary.audit.expired_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Unmatched</dt>
                    <dd>{summary.audit.unmatched_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Stale</dt>
                    <dd>{summary.audit.stale_count}</dd>
                  </div>
                </dl>
              </div>

              <div
                className="rounded-card border border-line bg-paper/70 px-4 py-4 text-xs text-ink"
                data-testid={`${panelTestId}-gate`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Chip variant={summary.gate.passes ? 'stable' : 'beta'}>Gate findings {summary.gate.active_finding_count}</Chip>
                  {summary.gate.waived_finding_count > 0 && (
                    <Chip variant="keyword">Waived {summary.gate.waived_finding_count}</Chip>
                  )}
                  <p className="text-sm font-semibold text-ink">{summary.gate.policy_title}</p>
                </div>
                <dl className="mt-3 space-y-2">
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Report state</dt>
                    <dd>{summary.gate.report_state}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Report complete</dt>
                    <dd>{summary.gate.report_complete ? 'yes' : 'no'}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Review actions</dt>
                    <dd>{summary.report.action_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Gate summary</dt>
                    <dd className="text-right break-all">{summary.gate.summary_path}</dd>
                  </div>
                </dl>
              </div>
            </div>

            {recentActions.length > 0 && (
              <div className="space-y-2" data-testid={`${panelTestId}-actions`}>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Recent review actions</p>
                {recentActions.map((action) => (
                  <div
                    key={`${action.waiver_id}-${action.action_code}`}
                    className="rounded-card border border-line bg-bg/70 px-3 py-3 text-xs text-ink"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <Chip variant="keyword">{action.waiver_id}</Chip>
                      <Chip variant="tag">{action.action_code}</Chip>
                    </div>
                    <p className="mt-2">{describeAction(action)}</p>
                    {action.source_path && <p className="mt-1 break-all text-muted">{action.source_path}</p>}
                    {action.source_audit_message && <p className="mt-1 text-muted">{action.source_audit_message}</p>}
                  </div>
                ))}
              </div>
            )}

            <div className="space-y-2" data-testid={`${panelTestId}-follow-ups`}>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">CLI follow-ups</p>
              {summary.recommended_follow_ups.map((item) => (
                <div
                  key={item.label}
                  className="rounded-card border border-line bg-bg/70 px-3 py-3 text-xs text-ink"
                >
                  <p className="font-semibold">{item.label}</p>
                  <p className="mt-1 text-muted">{item.description}</p>
                  <p className="mt-2 break-all">{item.command}</p>
                </div>
              ))}
            </div>
          </>
        )}

        {refreshPayload && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-refresh-summary`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant="keyword">Governance refreshed</Chip>
              <p className="text-sm font-semibold text-ink">{refreshPayload.gate.policy_id}</p>
            </div>
            <dl className="mt-3 space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Audit findings</dt>
                <dd>{refreshPayload.audit.finding_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Gate findings</dt>
                <dd>{refreshPayload.gate.active_finding_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Review actions</dt>
                <dd>{refreshPayload.report.action_count}</dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </Card>
  );
}
