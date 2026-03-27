'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
  LocalInstalledBaselinePromotePayload,
  LocalInstalledBaselineState,
  LocalInstalledDoctorSnapshot,
  LocalJobRecord,
} from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface InstalledBaselinePanelProps {
  panelTestId: string;
  targetRoot: string;
  doctorSnapshot: LocalInstalledDoctorSnapshot | null;
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

function describeBaselineState(
  baselineState: LocalInstalledBaselineState | null,
  doctorSnapshot: LocalInstalledDoctorSnapshot | null
): {
  label: string;
  variant: 'keyword' | 'stable' | 'beta' | 'internal' | 'tag';
  note: string;
  canCapture: boolean;
} {
  const hasHealthyDoctor = Boolean(doctorSnapshot && doctorSnapshot.summary.doctor_finding_count === 0);
  const hasReviewContext = Boolean(baselineState?.baseline_exists || (baselineState?.history_entry_count ?? 0) > 0);

  if (!baselineState?.baseline_exists) {
    return {
      label: 'No baseline yet',
      variant: 'tag',
      note: hasHealthyDoctor
        ? 'The latest doctor check is healthy, so this target root is ready for its first accepted baseline capture.'
        : 'Run a healthy doctor check first, or keep using copy-first baseline commands if you need to review drift before capturing the first baseline.',
      canCapture: hasHealthyDoctor,
    };
  }

  if ((baselineState.history_entry_count ?? 0) > 1) {
    return {
      label: 'Baseline history active',
      variant: 'stable',
      note: hasHealthyDoctor
        ? 'This target root already has retained baseline history, and the latest doctor check is healthy enough for another promotion.'
        : "This target root already has retained baseline history, so you can promote a reviewed follow-up baseline when today's drift has been accepted.",
      canCapture: hasHealthyDoctor || hasReviewContext,
    };
  }

  return {
    label: 'Baseline recorded',
    variant: 'keyword',
    note: hasHealthyDoctor
      ? 'A first baseline is already recorded, and the current target root is healthy enough for another captured revision.'
      : 'A first baseline is already recorded, so later reviewed revisions can be promoted into history from this panel.',
    canCapture: hasHealthyDoctor || hasReviewContext,
  };
}

function formatSummaryDelta(delta: Record<string, { before: number; after: number }>): string {
  const entries = Object.entries(delta);
  if (entries.length === 0) {
    return 'No summary delta recorded';
  }
  return entries.map(([key, value]) => `${key.replace(/_/g, ' ')} ${value.before}->${value.after}`).join(', ');
}

export function InstalledBaselinePanel({
  panelTestId,
  targetRoot,
  doctorSnapshot,
}: InstalledBaselinePanelProps) {
  const [baselineState, setBaselineState] = useState<LocalInstalledBaselineState | null>(null);
  const [baselineJob, setBaselineJob] = useState<LocalJobRecord | null>(null);
  const [promotionPayload, setPromotionPayload] = useState<LocalInstalledBaselinePromotePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [promotionPending, setPromotionPending] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadBaselineState = useCallback(async () => {
    setErrorMessage(null);
    try {
      const response = await fetch(`/api/local/state/baseline?target_root=${encodeURIComponent(targetRoot)}`, {
        cache: 'no-store',
      });
      const payload = (await response.json()) as LocalInstalledBaselineState | { detail?: string };
      if (!response.ok) {
        setBaselineState(null);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Unable to read installed baseline state.' : 'Unable to read installed baseline state.'
        );
        setLoading(false);
        return;
      }
      setBaselineState(payload as LocalInstalledBaselineState);
      setLoading(false);
    } catch (error) {
      setBaselineState(null);
      setErrorMessage(
        `Unable to read installed baseline state: ${error instanceof Error ? error.message : String(error)}`
      );
      setLoading(false);
    }
  }, [targetRoot]);

  useEffect(() => {
    setBaselineState(null);
    setBaselineJob(null);
    setPromotionPayload(null);
    setLoading(true);
    setPromotionPending(false);
    setErrorMessage(null);
    void loadBaselineState();
  }, [loadBaselineState, targetRoot]);

  useEffect(() => {
    if (!baselineJob || (baselineJob.status !== 'queued' && baselineJob.status !== 'running')) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/local/jobs/${baselineJob.job_id}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalJobRecord;
        setBaselineJob(payload);
      } catch (error) {
        setPromotionPending(false);
        setErrorMessage(
          `Unable to refresh baseline promotion job status: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }, 700);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [baselineJob]);

  useEffect(() => {
    if (!baselineJob || (baselineJob.status !== 'succeeded' && baselineJob.status !== 'failed')) {
      return;
    }

    setPromotionPending(false);
    if (baselineJob.status === 'failed') {
      setErrorMessage(jobFailureMessage(baselineJob, 'Installed baseline promotion failed.'));
      return;
    }

    try {
      setPromotionPayload(parseJobPayload<LocalInstalledBaselinePromotePayload>(baselineJob));
      void loadBaselineState();
    } catch (error) {
      setErrorMessage(
        `Unable to parse baseline promotion output: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }, [baselineJob, loadBaselineState]);

  async function runBaselinePromotion() {
    setErrorMessage(null);
    setPromotionPending(true);

    try {
      const response = await fetch('/api/local/state/baseline/promote', {
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
        setPromotionPending(false);
        setErrorMessage(
          payload && 'detail' in payload ? payload.detail ?? 'Installed baseline promotion failed.' : 'Installed baseline promotion failed.'
        );
        return;
      }

      setBaselineJob(payload as LocalJobRecord);
    } catch (error) {
      setPromotionPending(false);
      setErrorMessage(
        `Installed baseline promotion request failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  const baselineDescription = useMemo(
    () => describeBaselineState(baselineState, doctorSnapshot),
    [baselineState, doctorSnapshot]
  );
  const recentEntries = useMemo(
    () => [...(baselineState?.entries ?? [])].reverse(),
    [baselineState?.entries]
  );

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Chip variant={baselineDescription.variant} data-testid={`${panelTestId}-status`}>
              {baselineDescription.label}
            </Chip>
            <Chip variant="tag">Installed baseline history</Chip>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">Baseline history</h3>
            <p className="text-sm text-muted" data-testid={`${panelTestId}-note`}>
              {baselineDescription.note}
            </p>
          </div>
          <p className="text-xs text-muted" data-testid={`${panelTestId}-fallback-note`}>
            This first baseline pass captures the current target root into retained JSON and Markdown history. Deeper compare, restore, and governance review still stay copy-first outside this page.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={() => void loadBaselineState()}
            disabled={promotionPending}
            data-testid={`${panelTestId}-refresh`}
          >
            Refresh baseline
          </Button>
          <Button
            type="button"
            onClick={() => void runBaselinePromotion()}
            disabled={promotionPending || !baselineDescription.canCapture}
            data-testid={`${panelTestId}-capture`}
          >
            {promotionPending ? 'Capturing baseline...' : 'Capture current baseline'}
          </Button>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {loading && (
          <p className="text-xs text-muted" data-testid={`${panelTestId}-loading`}>
            Loading baseline history...
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

        {baselineState && (
          <div
            className="rounded-card border border-line bg-bg/70 px-4 py-4"
            data-testid={`${panelTestId}-summary`}
          >
            <dl className="space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Baseline path</dt>
                <dd className="text-right break-all">{baselineState.baseline_path}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">History path</dt>
                <dd className="text-right break-all">{baselineState.history_path}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">History entries</dt>
                <dd>{baselineState.history_entry_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Next sequence</dt>
                <dd>{baselineState.next_sequence}</dd>
              </div>
              {baselineState.current_baseline && (
                <>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Latest baseline captured at</dt>
                    <dd className="text-right break-all">{baselineState.current_baseline.generated_at}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Baseline installed skills</dt>
                    <dd>{baselineState.current_baseline.summary.installed_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Baseline installed bundles</dt>
                    <dd>{baselineState.current_baseline.summary.bundle_count}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Baseline doctor findings</dt>
                    <dd>{baselineState.current_baseline.summary.doctor_finding_count}</dd>
                  </div>
                </>
              )}
            </dl>
          </div>
        )}

        {baselineState && recentEntries.length > 0 && (
          <div className="space-y-2" data-testid={`${panelTestId}-history`}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Recent baseline entries</p>
            {recentEntries.map((entry) => (
              <div key={`${entry.sequence}-${entry.promoted_at}`} className="rounded-card border border-line bg-paper/70 px-3 py-3 text-xs text-ink">
                <div className="flex flex-wrap items-center gap-2">
                  <Chip variant="keyword">#{entry.sequence}</Chip>
                  {entry.replaced_existing_baseline && <Chip variant="beta">replaced baseline</Chip>}
                </div>
                <div className="mt-2 space-y-1">
                  <p className="break-all">{entry.promoted_at}</p>
                  <p>installed={entry.summary.installed_count}, bundles={entry.summary.bundle_count}</p>
                  <p className="break-all">archive: {entry.archived_baseline_path}</p>
                  {Object.keys(entry.transition_summary_delta ?? {}).length > 0 && (
                    <p data-testid={`${panelTestId}-entry-${entry.sequence}-delta`}>
                      {formatSummaryDelta(entry.transition_summary_delta)}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {promotionPayload && (
          <div
            className="rounded-card border border-line bg-paper/70 px-4 py-4"
            data-testid={`${panelTestId}-capture-summary`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant="keyword">Baseline captured</Chip>
              <p className="text-sm font-semibold text-ink">Promotion summary</p>
            </div>
            <dl className="mt-3 space-y-2 text-xs text-ink">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">History entries</dt>
                <dd>{promotionPayload.history_entry_count}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Replaced existing baseline</dt>
                <dd>{promotionPayload.replaced_existing_baseline ? 'yes' : 'no'}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Transition diff written</dt>
                <dd>{promotionPayload.transition_diff_present ? 'yes' : 'no'}</dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </Card>
  );
}
