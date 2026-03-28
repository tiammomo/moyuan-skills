'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
  LocalInstalledGovernanceState,
  LocalInstalledWaiverApplyReportAction,
  LocalInstalledWaiverApplyReportSummary,
  LocalInstalledWaiverApplyState,
  LocalInstalledWaiverApplyWriteHandoff,
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

type WaiverApplyActionMode = 'prepare' | 'stage' | 'verify';

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
          ? `The latest governance review captured ${governanceActionCount} review action(s). Prepare the first apply handoff pack to inspect patch-ready follow-ups before any stage or write decision.`
          : 'Governance review is ready. Prepare the first apply handoff pack to see whether any waiver follow-up can move into staged execution.',
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
      note: 'The latest handoff refresh generated apply patches, stage-ready targets, and CLI follow-ups. You can safely stage from this page, while write mode remains review-first in the CLI.',
      canPrepare,
    };
  }

  if (waiverApplyState.latest_report.report_state === 'needs_verification_followup') {
    return {
      label: 'Staged apply needs follow-up',
      variant: 'beta',
      note: 'Execution records exist, but verification still reports pending or blocked follow-up. Re-run verification after manual adjustments, or inspect the staged outputs before any write-mode step.',
      canPrepare,
    };
  }

  if (waiverApplyState.latest_report.report_state === 'verified') {
    return {
      label: waiverApplyState.latest_report.apply_execution.write_mode
        ? 'Written apply verified'
        : 'Staged apply verified',
      variant: 'stable',
      note: waiverApplyState.latest_report.apply_execution.write_mode
        ? 'The latest waiver/apply run wrote approved changes and verification still matches the reviewed target artifacts.'
        : 'The latest waiver/apply run staged governance-source changes inside the safe staging root and verification still matches the reviewed target artifacts.',
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

function failureFallbackFor(mode: WaiverApplyActionMode): string {
  if (mode === 'prepare') {
    return 'Waiver/apply handoff preparation failed.';
  }
  if (mode === 'stage') {
    return 'Waiver/apply stage refresh failed.';
  }
  return 'Waiver/apply verification refresh failed.';
}

function describeWriteHandoffVariant(
  writeHandoff: LocalInstalledWaiverApplyWriteHandoff | null
): 'keyword' | 'stable' | 'beta' | 'internal' | 'tag' {
  if (!writeHandoff) {
    return 'tag';
  }

  if (writeHandoff.state === 'ready' || writeHandoff.state === 'completed') {
    return 'stable';
  }

  if (writeHandoff.state === 'blocked') {
    return 'internal';
  }

  if (writeHandoff.state === 'drifted') {
    return 'beta';
  }

  return 'tag';
}

function describeWriteEvidenceVariant(
  writeHandoff: LocalInstalledWaiverApplyWriteHandoff | null
): 'keyword' | 'stable' | 'beta' | 'internal' | 'tag' {
  if (!writeHandoff) {
    return 'tag';
  }

  if (writeHandoff.evidence.state === 'post_write_verified' || writeHandoff.evidence.state === 'pre_write_ready') {
    return 'stable';
  }

  if (writeHandoff.evidence.state === 'post_write_drifted' || writeHandoff.evidence.state === 'drifted') {
    return 'beta';
  }

  if (writeHandoff.state === 'blocked') {
    return 'internal';
  }

  return 'tag';
}

function formatApprovalCapturedAt(value: string | null): string {
  if (!value) {
    return '';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
}

export function InstalledWaiverApplyPanel({
  panelTestId,
  targetRoot,
  governanceState,
}: InstalledWaiverApplyPanelProps) {
  const [waiverApplyState, setWaiverApplyState] = useState<LocalInstalledWaiverApplyState | null>(null);
  const [waiverApplyJob, setWaiverApplyJob] = useState<LocalJobRecord | null>(null);
  const [jobMode, setJobMode] = useState<WaiverApplyActionMode | null>(null);
  const [preparePayload, setPreparePayload] = useState<LocalInstalledWaiverApplyReportSummary | null>(null);
  const [stagePayload, setStagePayload] = useState<LocalInstalledWaiverApplyReportSummary | null>(null);
  const [verifyPayload, setVerifyPayload] = useState<LocalInstalledWaiverApplyReportSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [approvalCapturedAt, setApprovalCapturedAt] = useState<string | null>(null);

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
    setWaiverApplyJob(null);
    setJobMode(null);
    setPreparePayload(null);
    setStagePayload(null);
    setVerifyPayload(null);
    setLoading(true);
    setErrorMessage(null);
    void loadWaiverApplyState();
  }, [loadWaiverApplyState, targetRoot]);

  useEffect(() => {
    if (!waiverApplyJob || (waiverApplyJob.status !== 'queued' && waiverApplyJob.status !== 'running')) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${waiverApplyJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        setWaiverApplyJob(payload);
      } catch (error) {
        setJobMode(null);
        setErrorMessage(
          `Unable to refresh waiver/apply handoff job status: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }, 700);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [waiverApplyJob]);

  useEffect(() => {
    if (!waiverApplyJob || !jobMode || (waiverApplyJob.status !== 'succeeded' && waiverApplyJob.status !== 'failed')) {
      return;
    }

    const completedMode = jobMode;
    setJobMode(null);

    if (waiverApplyJob.status === 'failed') {
      setErrorMessage(jobFailureMessage(waiverApplyJob, failureFallbackFor(completedMode)));
      return;
    }

    try {
      const payload = parseJobPayload<LocalInstalledWaiverApplyReportSummary>(waiverApplyJob);
      if (completedMode === 'prepare') {
        setPreparePayload(payload);
      } else if (completedMode === 'stage') {
        setStagePayload(payload);
      } else {
        setVerifyPayload(payload);
      }
      void loadWaiverApplyState();
    } catch (error) {
      setErrorMessage(
        `Unable to parse waiver/apply handoff output: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }, [jobMode, loadWaiverApplyState, waiverApplyJob]);

  async function runWaiverApplyAction(
    mode: WaiverApplyActionMode,
    pathname: string,
    fallbackMessage: string
  ) {
    setErrorMessage(null);
    if (mode === 'prepare') {
      setPreparePayload(null);
    } else if (mode === 'stage') {
      setStagePayload(null);
    } else {
      setVerifyPayload(null);
    }
    setWaiverApplyJob(null);
    setJobMode(mode);

    try {
      const response = await fetch(pathname, {
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
        setJobMode(null);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? fallbackMessage : fallbackMessage
        );
        return;
      }

      setWaiverApplyJob(payload as LocalJobRecord);
    } catch (error) {
      setJobMode(null);
      setErrorMessage(
        `${fallbackMessage.replace(/\.$/, '')}: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  const handoffDescription = useMemo(
    () => describeWaiverApplyState(waiverApplyState, governanceState ?? null),
    [governanceState, waiverApplyState]
  );
  const latestReport = waiverApplyState?.latest_report;
  const writeHandoff = waiverApplyState?.write_handoff ?? null;
  const recentActions = useMemo(() => latestReport?.actions ?? [], [latestReport?.actions]);
  const writeHandoffVariant = useMemo(
    () => describeWriteHandoffVariant(writeHandoff),
    [writeHandoff]
  );
  const writeEvidenceVariant = useMemo(
    () => describeWriteEvidenceVariant(writeHandoff),
    [writeHandoff]
  );
  const approvalStorageKey = useMemo(() => {
    if (!writeHandoff || !waiverApplyState?.report_summary_path) {
      return null;
    }

    return [
      'moyuan-write-handoff-approval',
      targetRoot,
      waiverApplyState.report_summary_path,
      latestReport?.apply_execute_summary_path ?? '',
      latestReport?.report_state ?? '',
    ].join(':');
  }, [latestReport?.apply_execute_summary_path, latestReport?.report_state, targetRoot, waiverApplyState?.report_summary_path, writeHandoff]);
  const actionPending = Boolean(
    jobMode && waiverApplyJob && (waiverApplyJob.status === 'queued' || waiverApplyJob.status === 'running')
  );
  const canStage = Boolean(latestReport && latestReport.action_count > 0 && handoffDescription.canPrepare);
  const canVerify = Boolean(
    latestReport?.apply_execution.available && latestReport.apply_execution.action_count > 0
  );
  const approvalEnabled = Boolean(writeHandoff?.approval_enabled);
  const approvalCaptured = Boolean(approvalCapturedAt);

  useEffect(() => {
    if (!approvalStorageKey || typeof window === 'undefined') {
      setApprovalCapturedAt(null);
      return;
    }

    const storedValue = window.localStorage.getItem(approvalStorageKey);
    setApprovalCapturedAt(storedValue && storedValue.trim() ? storedValue : null);
  }, [approvalStorageKey]);

  function handleApprovalChange(checked: boolean) {
    if (!approvalStorageKey || typeof window === 'undefined') {
      setApprovalCapturedAt(null);
      return;
    }

    if (!checked) {
      window.localStorage.removeItem(approvalStorageKey);
      setApprovalCapturedAt(null);
      return;
    }

    const capturedAt = new Date().toISOString();
    window.localStorage.setItem(approvalStorageKey, capturedAt);
    setApprovalCapturedAt(capturedAt);
  }

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
            This frontend pass can prepare, safely stage, re-verify, and hand off waiver/apply write guidance inside the governance staging flow. Repo-source write mode still stays review-first outside this page because it updates governance sources only after explicit approval.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={reloadWaiverApplyState}
            disabled={actionPending}
            data-testid={`${panelTestId}-reload`}
          >
            Reload handoff
          </Button>
          <Button
            type="button"
            onClick={() =>
              void runWaiverApplyAction(
                'prepare',
                '/api/local/state/governance/waiver-apply/prepare',
                'Waiver/apply handoff preparation failed.'
              )
            }
            disabled={actionPending || !handoffDescription.canPrepare}
            data-testid={`${panelTestId}-prepare`}
          >
            {actionPending && jobMode === 'prepare'
              ? 'Preparing handoff...'
              : latestReport
                ? 'Refresh apply handoff'
                : 'Prepare apply handoff'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() =>
              void runWaiverApplyAction(
                'stage',
                '/api/local/state/governance/waiver-apply/stage',
                'Waiver/apply stage refresh failed.'
              )
            }
            disabled={actionPending || !canStage}
            data-testid={`${panelTestId}-stage`}
          >
            {actionPending && jobMode === 'stage'
              ? 'Staging apply...'
              : latestReport?.apply_execution.available
                ? 'Restage apply changes'
                : 'Stage apply changes'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() =>
              void runWaiverApplyAction(
                'verify',
                '/api/local/state/governance/waiver-apply/verify',
                'Waiver/apply verification refresh failed.'
              )
            }
            disabled={actionPending || !canVerify}
            data-testid={`${panelTestId}-verify`}
          >
            {actionPending && jobMode === 'verify'
              ? 'Refreshing verification...'
              : latestReport?.apply_verification.action_count
                ? 'Refresh verification'
                : 'Verify staged changes'}
          </Button>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {loading && (
          <p className="text-xs text-muted" data-testid={`${panelTestId}-loading`}>
            Loading waiver/apply handoff...
          </p>
        )}

        {actionPending && jobMode && (
          <p className="text-xs text-muted" data-testid={`${panelTestId}-${jobMode}-loading`}>
            {jobMode === 'prepare'
              ? 'Preparing the latest apply handoff pack...'
              : jobMode === 'stage'
                ? 'Staging reviewed apply targets and refreshing the report...'
                : 'Re-verifying staged apply targets and refreshing the report...'}
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
                    <dt className="text-muted">Apply execute summary</dt>
                    <dd className="text-right break-all">{latestReport.apply_execute_summary_path || '-'}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Stage records</dt>
                    <dd>
                      {latestReport.apply_execution.staged_update_count +
                        latestReport.apply_execution.staged_delete_count}
                    </dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Blocked apply actions</dt>
                    <dd>{latestReport.apply_execution.blocked_action_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Verified actions</dt>
                    <dd>{latestReport.apply_verification.verified_count}</dd>
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

        {writeHandoff && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-write-handoff`}
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <Chip
                    variant={writeHandoffVariant}
                    data-testid={`${panelTestId}-write-handoff-status`}
                  >
                    {writeHandoff.title}
                  </Chip>
                  <Chip variant="internal">CLI write only</Chip>
                  {writeHandoff.requires_explicit_approval && <Chip variant="tag">Explicit approval required</Chip>}
                </div>
                <p className="text-sm text-ink" data-testid={`${panelTestId}-write-handoff-summary`}>
                  {writeHandoff.summary}
                </p>
              </div>
              <div className="rounded-card border border-dashed border-line bg-bg/70 px-3 py-3 text-xs text-ink">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Eligibility</p>
                <p className="mt-1">
                  {writeHandoff.ready
                    ? 'Staged verification is clean, so the page can hand off the final CLI write pack.'
                    : 'The page keeps write mode read-only until the remaining review, verification, or drift work is cleared.'}
                </p>
              </div>
            </div>

            {writeHandoff.blocked_reasons.length > 0 && (
              <div
                className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
                data-testid={`${panelTestId}-write-handoff-blockers`}
              >
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Why write stays gated</p>
                <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                  {writeHandoff.blocked_reasons.map((reason) => (
                    <li key={reason}>- {reason}</li>
                  ))}
                </ul>
              </div>
            )}

            <div
              className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
              data-testid={`${panelTestId}-write-approval`}
            >
              <label className="flex items-start gap-3 text-sm text-ink">
                <input
                  type="checkbox"
                  checked={approvalCaptured}
                  onChange={(event) => handleApprovalChange(event.target.checked)}
                  disabled={!approvalEnabled}
                  className="mt-1 h-4 w-4 rounded border border-line disabled:cursor-not-allowed"
                  data-testid={`${panelTestId}-write-approval-checkbox`}
                />
                <span>{writeHandoff.approval_label}</span>
              </label>
              <p className="mt-2 text-xs text-muted" data-testid={`${panelTestId}-write-approval-help`}>
                {writeHandoff.approval_help}
              </p>
              <p className="mt-2 text-xs text-muted" data-testid={`${panelTestId}-write-approval-state`}>
                {approvalEnabled
                  ? approvalCaptured
                    ? `Approval captured in this browser at ${formatApprovalCapturedAt(approvalCapturedAt)}.`
                    : 'Waiting for explicit approval capture before handing off the CLI write pack.'
                  : 'Approval capture unlocks only after the latest handoff reaches a clean ready or completed state.'}
              </p>
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-2">
              {writeHandoff.write_command && (
                <div className="rounded-card border border-line bg-bg/70 px-3 py-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                    Approved write command
                  </p>
                  <pre
                    className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink"
                    data-testid={`${panelTestId}-write-command`}
                  >
                    <code>{writeHandoff.write_command}</code>
                  </pre>
                </div>
              )}

              {writeHandoff.verify_command && (
                <div className="rounded-card border border-line bg-bg/70 px-3 py-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                    Post-write verify command
                  </p>
                  <pre
                    className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink"
                    data-testid={`${panelTestId}-verify-command`}
                  >
                    <code>{writeHandoff.verify_command}</code>
                  </pre>
                </div>
              )}
            </div>

            {writeHandoff.governance_source_paths.length > 0 && (
              <div
                className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
                data-testid={`${panelTestId}-write-handoff-sources`}
              >
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                  Planned governance sources
                </p>
                <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                  {writeHandoff.governance_source_paths.map((sourcePath) => (
                    <li key={sourcePath}>- {sourcePath}</li>
                  ))}
                </ul>
              </div>
            )}

            {writeHandoff.artifact_paths.length > 0 && (
              <div
                className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
                data-testid={`${panelTestId}-write-handoff-artifacts`}
              >
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                  Review artifacts
                </p>
                <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                  {writeHandoff.artifact_paths.map((artifactPath) => (
                    <li key={artifactPath}>- {artifactPath}</li>
                  ))}
                </ul>
              </div>
            )}

            {writeHandoff.checklist.length > 0 && (
              <div
                className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
                data-testid={`${panelTestId}-write-handoff-checklist`}
              >
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                  Approval checklist
                </p>
                <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                  {writeHandoff.checklist.map((item) => (
                    <li key={item}>- {item}</li>
                  ))}
                </ul>
              </div>
            )}

            <div
              className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
              data-testid={`${panelTestId}-write-evidence`}
            >
              <div className="flex flex-wrap items-center gap-2">
                <Chip variant={writeEvidenceVariant}>{writeHandoff.evidence.title}</Chip>
                <Chip variant="tag">Evidence pack</Chip>
              </div>
              <p className="mt-2 text-sm text-ink" data-testid={`${panelTestId}-write-evidence-summary`}>
                {writeHandoff.evidence.summary}
              </p>
              <dl className="mt-3 space-y-2 text-xs text-ink">
                {writeHandoff.evidence.entries.map((entry) => (
                  <div key={`${entry.label}-${entry.value}`} className="flex justify-between gap-3">
                    <dt className="text-muted">{entry.label}</dt>
                    <dd className="text-right break-all">{entry.value || '-'}</dd>
                  </div>
                ))}
              </dl>
              {writeHandoff.evidence.follow_ups.length > 0 && (
                <div
                  className="mt-3 rounded-card border border-dashed border-line bg-paper/70 px-3 py-3"
                  data-testid={`${panelTestId}-write-evidence-follow-ups`}
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                    Evidence follow-ups
                  </p>
                  <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                    {writeHandoff.evidence.follow_ups.map((item) => (
                      <li key={item}>- {item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div
              className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3 text-xs leading-6 text-ink"
              data-testid={`${panelTestId}-rollback-hint`}
            >
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Rollback hint</p>
              <p className="mt-1">{writeHandoff.rollback_hint}</p>
            </div>
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
                  {action.apply_execute_stage_path && (
                    <p className="mt-1 break-all text-muted">staged: {action.apply_execute_stage_path}</p>
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

        {stagePayload && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-stage-summary`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant={stagePayload.apply_verification.passes ? 'stable' : 'beta'}>Stage refreshed</Chip>
              <p className="text-sm font-semibold text-ink">{stagePayload.report_state}</p>
            </div>
            <dl className="mt-3 space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Staged updates</dt>
                <dd>{stagePayload.apply_execution.staged_update_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Staged deletes</dt>
                <dd>{stagePayload.apply_execution.staged_delete_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Blocked actions</dt>
                <dd>{stagePayload.apply_execution.blocked_action_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Verified actions</dt>
                <dd>{stagePayload.apply_verification.verified_count}</dd>
              </div>
            </dl>
          </div>
        )}

        {verifyPayload && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-verify-summary`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant={verifyPayload.apply_verification.passes ? 'stable' : 'beta'}>
                Verification refreshed
              </Chip>
              <p className="text-sm font-semibold text-ink">{verifyPayload.report_state}</p>
            </div>
            <dl className="mt-3 space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Verified actions</dt>
                <dd>{verifyPayload.apply_verification.verified_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Pending verification</dt>
                <dd>{verifyPayload.apply_verification.pending_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Blocked verification</dt>
                <dd>{verifyPayload.apply_verification.blocked_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Drift findings</dt>
                <dd>{verifyPayload.apply_verification.drift_count}</dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </Card>
  );
}
