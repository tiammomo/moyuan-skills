'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
  LocalInstalledGovernanceState,
  LocalInstalledWaiverApplyReportAction,
  LocalInstalledWaiverApplyReportSummary,
  LocalInstalledWaiverApplyState,
  LocalJobRecord,
} from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface InstalledWaiverApplyPanelProps {
  panelTestId: string;
  targetRoot: string;
  governanceState?: LocalInstalledGovernanceState | null;
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

function describeWaiverApplyState(
  waiverApplyState: LocalInstalledWaiverApplyState | null,
  governanceState: LocalInstalledGovernanceState | null
): {
  label: string;
  variant: 'keyword' | 'stable' | 'beta' | 'internal' | 'tag';
  note: string;
  canPrepare: boolean;
} {
  const historyExists = Boolean(governanceState?.history_exists || waiverApplyState?.history_exists);
  const governanceSummaryExists = Boolean(
    governanceState?.summary_exists || waiverApplyState?.governance_summary_exists
  );
  const governanceActionCount =
    governanceState?.latest_summary?.report.action_count ?? waiverApplyState?.governance_action_count ?? 0;
  const canPrepare = Boolean(
    waiverApplyState?.can_prepare || (governanceState?.history_exists && governanceState?.summary_exists)
  );

  if (!historyExists) {
    return {
      label: 'No baseline history yet',
      variant: 'tag',
      note: 'Capture a retained baseline and refresh governance first so this target root has review context for waiver/apply handoff.',
      canPrepare: false,
    };
  }

  if (!governanceSummaryExists) {
    return {
      label: 'Governance summary required',
      variant: 'internal',
      note: 'Refresh the governance summary first. The first waiver/apply handoff stays anchored to the latest governance review for this target root.',
      canPrepare: false,
    };
  }

  if (!waiverApplyState || !waiverApplyState.report_summary_exists || !waiverApplyState.latest_report) {
    return {
      label: 'Apply handoff not prepared',
      variant: 'beta',
      note:
        governanceActionCount > 0
          ? `The latest governance review captured ${governanceActionCount} review action(s). Prepare the first apply handoff pack to inspect patch-ready follow-ups without writing repo governance files from this page.`
          : 'Governance review is ready. Prepare the first apply handoff pack to see whether any waiver follow-up can move into CLI execution.',
      canPrepare,
    };
  }

  if (waiverApplyState.latest_report.action_count === 0) {
    return {
      label: 'No apply actions prepared',
      variant: 'stable',
      note: 'The latest handoff refresh did not find any apply-ready waiver follow-ups for this target root.',
      canPrepare,
    };
  }

  if (waiverApplyState.latest_report.report_state === 'needs_execution') {
    return {
      label: 'Apply handoff prepared',
      variant: 'keyword',
      note: 'The latest handoff refresh generated apply patches and CLI follow-ups. Review the pack here, then continue with stage or write mode from the CLI.',
      canPrepare,
    };
  }

  if (waiverApplyState.latest_report.report_state === 'drifted') {
    return {
      label: 'Apply handoff drift detected',
      variant: 'beta',
      note: 'The prepared waiver/apply handoff now includes verification drift. Rebuild or re-review the pack before any write-mode execution.',
      canPrepare,
    };
  }

  return {
    label: 'Apply handoff refreshed',
    variant: 'stable',
    note: `The latest waiver/apply handoff report is in state "${waiverApplyState.latest_report.report_state}".`,
    canPrepare,
  };
}

function describeExecutionStatus(action: LocalInstalledWaiverApplyReportAction): {
  label: string;
  variant: 'keyword' | 'stable' | 'beta' | 'internal' | 'tag';
} {
  const status = action.apply_execute_status.trim();
  if (!status) {
    return {
      label: 'CLI execution pending',
      variant: 'tag',
    };
  }
  if (status.startsWith('blocked')) {
    return {
      label: status,
      variant: 'internal',
    };
  }
  if (status.startsWith('staged')) {
    return {
      label: status,
      variant: 'beta',
    };
  }
  if (status.startsWith('written')) {
    return {
      label: status,
      variant: 'keyword',
    };
  }
  return {
    label: status,
    variant: 'tag',
  };
}

function describeVerificationStatus(action: LocalInstalledWaiverApplyReportAction): {
  label: string;
  variant: 'keyword' | 'stable' | 'beta' | 'internal' | 'tag';
} {
  const state = action.verification_state.trim();
  if (!state) {
    return {
      label: 'Verification pending',
      variant: 'tag',
    };
  }
  if (state.startsWith('matches_')) {
    return {
      label: state,
      variant: 'stable',
    };
  }
  if (state.startsWith('blocked') || state === 'manual_review') {
    return {
      label: state,
      variant: 'internal',
    };
  }
  if (state.startsWith('pending') || state.startsWith('missing')) {
    return {
      label: state,
      variant: 'beta',
    };
  }
  if (state.startsWith('drifted')) {
    return {
      label: state,
      variant: 'beta',
    };
  }
  return {
    label: state,
    variant: 'tag',
  };
}

export function InstalledWaiverApplyPanel({
  panelTestId,
  targetRoot,
  governanceState,
}: InstalledWaiverApplyPanelProps) {
  const [waiverApplyState, setWaiverApplyState] = useState<LocalInstalledWaiverApplyState | null>(null);
  const [prepareJob, setPrepareJob] = useState<LocalJobRecord | null>(null);
  const [preparePayload, setPreparePayload] = useState<LocalInstalledWaiverApplyReportSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [preparePending, setPreparePending] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadWaiverApplyState = useCallback(async () => {
    setErrorMessage(null);
    try {
      const response = await fetch(
        `/api/local/state/governance/waiver-apply?target_root=${encodeURIComponent(targetRoot)}`,
        {
          cache: 'no-store',
        }
      );
      const payload = (await response.json()) as LocalInstalledWaiverApplyState | { detail?: string };
      if (!response.ok) {
        setErrorMessage(
          payload && 'detail' in payload
            ? payload.detail ?? 'Unable to read waiver/apply handoff state.'
            : 'Unable to read waiver/apply handoff state.'
        );
        setLoading(false);
        return;
      }
      setWaiverApplyState(payload as LocalInstalledWaiverApplyState);
      setLoading(false);
    } catch (error) {
      setErrorMessage(
        `Unable to read waiver/apply handoff state: ${error instanceof Error ? error.message : String(error)}`
      );
      setLoading(false);
    }
  }, [targetRoot]);

  const reloadWaiverApplyState = useCallback(() => {
    setLoading(true);
    void loadWaiverApplyState();
  }, [loadWaiverApplyState]);

  useEffect(() => {
    if (waiverApplyState?.target_root !== targetRoot) {
      setWaiverApplyState(null);
    }
    setPrepareJob(null);
    setPreparePayload(null);
    setLoading(true);
    setPreparePending(false);
    setErrorMessage(null);
    void loadWaiverApplyState();
  }, [loadWaiverApplyState, targetRoot]);

  useEffect(() => {
    if (!prepareJob || (prepareJob.status !== 'queued' && prepareJob.status !== 'running')) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${prepareJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        setPrepareJob(payload);
      } catch (error) {
        setPreparePending(false);
        setErrorMessage(
          `Unable to refresh waiver/apply handoff job status: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }, 700);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [prepareJob]);

  useEffect(() => {
    if (!prepareJob || (prepareJob.status !== 'succeeded' && prepareJob.status !== 'failed')) {
      return;
    }

    setPreparePending(false);
    if (prepareJob.status === 'failed') {
      setErrorMessage(jobFailureMessage(prepareJob, 'Waiver/apply handoff preparation failed.'));
      return;
    }

    try {
      setPreparePayload(parseJobPayload<LocalInstalledWaiverApplyReportSummary>(prepareJob));
      void loadWaiverApplyState();
    } catch (error) {
      setErrorMessage(
        `Unable to parse waiver/apply handoff output: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }, [loadWaiverApplyState, prepareJob]);

  async function runWaiverApplyPrepare() {
    setErrorMessage(null);
    setPreparePending(true);

    try {
      const response = await fetch('/api/local/state/governance/waiver-apply/prepare', {
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
        setPreparePending(false);
        setErrorMessage(
          payload && 'detail' in payload
            ? payload.detail ?? 'Waiver/apply handoff preparation failed.'
            : 'Waiver/apply handoff preparation failed.'
        );
        return;
      }

      setPrepareJob(payload as LocalJobRecord);
    } catch (error) {
      setPreparePending(false);
      setErrorMessage(
        `Waiver/apply handoff request failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  const handoffDescription = useMemo(
    () => describeWaiverApplyState(waiverApplyState, governanceState ?? null),
    [governanceState, waiverApplyState]
  );
  const latestReport = waiverApplyState?.latest_report;
  const recentActions = useMemo(() => latestReport?.actions ?? [], [latestReport?.actions]);

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Chip variant={handoffDescription.variant} data-testid={`${panelTestId}-status`}>
              {handoffDescription.label}
            </Chip>
            <Chip variant="tag">Waiver / apply handoff</Chip>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">Waiver / apply</h3>
            <p className="text-sm text-muted" data-testid={`${panelTestId}-note`}>
              {handoffDescription.note}
            </p>
          </div>
          <p className="text-xs text-muted" data-testid={`${panelTestId}-fallback-note`}>
            This first frontend pass only prepares read-only apply packs, patch files, and CLI follow-ups. Stage mode and write mode still stay review-first outside this page because they update repo governance sources instead of the installed target root itself.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={reloadWaiverApplyState}
            disabled={preparePending}
            data-testid={`${panelTestId}-reload`}
          >
            Reload handoff
          </Button>
          <Button
            type="button"
            onClick={() => void runWaiverApplyPrepare()}
            disabled={preparePending || !handoffDescription.canPrepare}
            data-testid={`${panelTestId}-prepare`}
          >
            {preparePending ? 'Preparing handoff...' : latestReport ? 'Refresh apply handoff' : 'Prepare apply handoff'}
          </Button>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {loading && (
          <p className="text-xs text-muted" data-testid={`${panelTestId}-loading`}>
            Loading waiver/apply handoff...
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

        {waiverApplyState && (
          <div
            className="rounded-card border border-line bg-bg/70 px-4 py-4"
            data-testid={`${panelTestId}-summary`}
          >
            <dl className="space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Governance summary</dt>
                <dd className="text-right break-all">{waiverApplyState.governance_summary_path}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Apply handoff directory</dt>
                <dd className="text-right break-all">{waiverApplyState.waiver_apply_dir}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Governance report state</dt>
                <dd>{waiverApplyState.governance_report_state || '-'}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Governance review actions</dt>
                <dd>{waiverApplyState.governance_action_count}</dd>
              </div>
              {latestReport && (
                <>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Apply handoff state</dt>
                    <dd>{latestReport.report_state}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Apply actions</dt>
                    <dd>{latestReport.apply.action_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Patch files</dt>
                    <dd>{latestReport.apply.patch_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Pending verification</dt>
                    <dd>{latestReport.apply_verification.pending_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Verification drift</dt>
                    <dd>{latestReport.apply_verification.drift_count}</dd>
                  </div>
                </>
              )}
            </dl>
          </div>
        )}

        {latestReport && recentActions.length > 0 && (
          <div className="space-y-2" data-testid={`${panelTestId}-actions`}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Prepared apply actions</p>
            {recentActions.map((action) => {
              const executionStatus = describeExecutionStatus(action);
              const verificationStatus = describeVerificationStatus(action);
              return (
                <div
                  key={`${action.waiver_id}-${action.action_code}`}
                  className="rounded-card border border-line bg-paper/70 px-3 py-3 text-xs text-ink"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <Chip variant="keyword">{action.waiver_id}</Chip>
                    <Chip variant="tag">{action.action_code}</Chip>
                    <Chip variant={executionStatus.variant}>{executionStatus.label}</Chip>
                    <Chip variant={verificationStatus.variant}>{verificationStatus.label}</Chip>
                  </div>
                  <p className="mt-2">{action.apply_summary}</p>
                  {action.apply_source_path && (
                    <p className="mt-1 break-all text-muted">source: {action.apply_source_path}</p>
                  )}
                  {action.apply_target_path && (
                    <p className="mt-1 break-all text-muted">target: {action.apply_target_path}</p>
                  )}
                  {action.apply_patch_path && (
                    <p className="mt-1 break-all text-muted">patch: {action.apply_patch_path}</p>
                  )}
                  {action.verification_message && <p className="mt-1 text-muted">{action.verification_message}</p>}
                </div>
              );
            })}
          </div>
        )}

        {waiverApplyState && waiverApplyState.recommended_follow_ups.length > 0 && (
          <div className="space-y-2" data-testid={`${panelTestId}-follow-ups`}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">CLI follow-ups</p>
            {waiverApplyState.recommended_follow_ups.map((item) => (
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
        )}

        {preparePayload && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-prepare-summary`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant="keyword">Apply handoff refreshed</Chip>
              <p className="text-sm font-semibold text-ink">{preparePayload.report_state}</p>
            </div>
            <dl className="mt-3 space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Apply actions</dt>
                <dd>{preparePayload.apply.action_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Patch files</dt>
                <dd>{preparePayload.apply.patch_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Pending verification</dt>
                <dd>{preparePayload.apply_verification.pending_count}</dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </Card>
  );
}
