'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import type {
  DocActionCommand,
  DocActionPanelData,
  LocalBackendStatus,
  LocalDocsActionHistoryPayload,
  LocalJobRecord,
} from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { cn } from '@/lib/utils';

interface DocActionPanelProps {
  panel: DocActionPanelData;
}

type DocActionRunState = 'copy' | 'checking' | 'ready' | 'blocked' | 'running' | 'succeeded' | 'failed';

interface CommandExecutionState {
  status: DocActionRunState;
  job: LocalJobRecord | null;
  errorMessage: string | null;
}

interface CommandHistoryState {
  recentRuns: LocalJobRecord[];
  lastSuccess: LocalJobRecord | null;
}

interface CommandDrilldownState {
  artifacts: boolean;
  stdout: boolean;
  stderr: boolean;
}

type CommandHistoryFilter = 'all' | 'failed' | 'succeeded';
type CommandRunDiffState = 'unavailable' | 'baseline' | 'compared';
type CommandDrilldownSection = keyof CommandDrilldownState;
type CommandSectionDiffState = 'unavailable' | 'baseline' | 'changed' | 'stable' | 'empty';

interface CommandRunDiffItem {
  label: string;
  detail: string;
}

interface CommandRunDiffSummary {
  state: CommandRunDiffState;
  summary: string;
  focusHint: string | null;
  focusSection: CommandDrilldownSection | null;
  changedItems: CommandRunDiffItem[];
  stableItems: CommandRunDiffItem[];
}

interface CommandSectionDiff {
  section: CommandDrilldownSection;
  state: CommandSectionDiffState;
  summary: string;
  hasContent: boolean;
  recommended: boolean;
}

interface CommandSequenceMeta {
  badge: string;
  description: string;
}

function getCommandKey(label: string, command: string): string {
  return `${label}:${command}`;
}

function getHistoryKey(command: DocActionCommand): string {
  return command.actionId ?? getCommandKey(command.label, command.command);
}

function transformTestId(testId: string | undefined, replacement: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', replacement);
  }
  return `${testId}-${replacement.replace(/^doc-action-/, '')}`;
}

function getCopyTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-copy-');
}

function getRunTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-run-');
}

function getStatusTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-status-');
}

function getSummaryTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-summary-');
}

function getSummarySourceTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-summary-source-');
}

function getErrorTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-error-');
}

function getOutcomeTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-outcome-');
}

function getPrerequisitesTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-prerequisites-');
}

function getPrerequisiteStateTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-prerequisites-state-');
}

function getArtifactsTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-artifacts-');
}

function getExecutionSummaryTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-execution-summary-');
}

function getHistoryTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-history-');
}

function getLastSuccessTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-last-success-');
}

function getHistoryEntryTestId(testId: string | undefined, index: number): string | undefined {
  const base = transformTestId(testId, 'doc-action-history-entry-');
  return base ? `${base}-${index}` : undefined;
}

function getHistorySummaryTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-history-summary-');
}

function getHistoryFilterTestId(testId: string | undefined, filter: CommandHistoryFilter): string | undefined {
  const base = transformTestId(testId, 'doc-action-history-filter-');
  return base ? `${base}-${filter}` : undefined;
}

function getCompareHintTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-compare-hint-');
}

function getRunDiffSummaryTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-run-diff-summary-');
}

function getRunDiffChangedTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-run-diff-changed-');
}

function getRunDiffStableTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-run-diff-stable-');
}

function getRunDiffFocusTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-run-diff-focus-');
}

function getRunDiffOpenTestId(
  testId: string | undefined,
  section: CommandDrilldownSection
): string | undefined {
  const base = transformTestId(testId, 'doc-action-run-diff-open-');
  return base ? `${base}-${section}` : undefined;
}

function getArtifactToggleTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-artifact-toggle-');
}

function getArtifactDrilldownTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-artifact-drilldown-');
}

function getArtifactDiffStateTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-artifact-diff-state-');
}

function getStdoutToggleTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-stdout-toggle-');
}

function getStdoutDrilldownTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-stdout-drilldown-');
}

function getStdoutDiffStateTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-stdout-diff-state-');
}

function getStderrToggleTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-stderr-toggle-');
}

function getStderrDrilldownTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-stderr-drilldown-');
}

function getStderrDiffStateTestId(testId?: string): string | undefined {
  return transformTestId(testId, 'doc-action-stderr-diff-state-');
}

async function copyCommandText(value: string): Promise<void> {
  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return;
    } catch {
      // Fall back to an in-page copy path when clipboard permissions are unavailable.
    }
  }

  if (typeof document === 'undefined') {
    throw new Error('Clipboard is not available in this environment.');
  }

  const textarea = document.createElement('textarea');
  textarea.value = value;
  textarea.setAttribute('readonly', 'true');
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  textarea.style.pointerEvents = 'none';
  document.body.appendChild(textarea);
  textarea.select();
  textarea.setSelectionRange(0, value.length);
  const succeeded = document.execCommand('copy');
  document.body.removeChild(textarea);

  if (!succeeded) {
    throw new Error('Unable to copy command text.');
  }
}

function getCommandSequenceMeta(index: number, total: number): CommandSequenceMeta {
  if (total <= 1) {
    return { badge: 'Step 1', description: 'Run this command for the current doc flow.' };
  }
  if (index === 0) {
    return { badge: 'Step 1 - Start here', description: 'Use this first so the rest of the runbook has the right baseline.' };
  }
  if (index === total - 1) {
    return {
      badge: `Step ${index + 1} - Finish by verifying`,
      description: 'Close the loop with this final validation or confirmation step.',
    };
  }
  return {
    badge: `Step ${index + 1} - Then continue`,
    description: 'Keep the workflow moving before you run the final verification step.',
  };
}

function truncateDetailedOutput(value: string): string {
  const normalized = value.trim();
  return normalized.length <= 4000 ? normalized : `${normalized.slice(0, 4000)}\n... output truncated ...`;
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

function summarizeOutput(value: string): string {
  const normalized = value.trim();
  if (!normalized) {
    return 'No output captured.';
  }
  const lineCount = normalized.split(/\r?\n/).length;
  return `${lineCount} line(s), ${normalized.length} char(s).`;
}

function summarizeOutputForDiff(value: string): string {
  const normalized = value.trim();
  if (!normalized) {
    return 'no output';
  }
  const lineCount = normalized.split(/\r?\n/).length;
  return `${lineCount} line(s) / ${normalized.length} char(s)`;
}

function formatDetailedValue(value: unknown): string {
  if (typeof value === 'string') {
    return value;
  }
  if (value === null || value === undefined) {
    return '-';
  }
  return JSON.stringify(value, null, 2);
}

function formatRunState(status: DocActionRunState): string {
  if (status === 'copy') return 'Copy only';
  if (status === 'checking') return 'Checking backend';
  if (status === 'ready') return 'Ready';
  if (status === 'blocked') return 'Blocked';
  if (status === 'running') return 'Running';
  if (status === 'succeeded') return 'Succeeded';
  return 'Failed';
}

function runStateVariant(status: DocActionRunState): 'keyword' | 'tag' | 'beta' | 'internal' {
  if (status === 'ready' || status === 'succeeded') return 'keyword';
  if (status === 'running') return 'beta';
  if (status === 'blocked' || status === 'failed') return 'internal';
  return 'tag';
}

function formatPrerequisiteState(state?: DocActionCommand['prerequisitesState']): string {
  if (state === 'ready') return 'Ready in-page';
  if (state === 'blocked') return 'Blocked';
  return 'Manual check';
}

function prerequisiteStateVariant(
  state?: DocActionCommand['prerequisitesState']
): 'keyword' | 'tag' | 'internal' {
  if (state === 'ready') return 'keyword';
  if (state === 'blocked') return 'internal';
  return 'tag';
}

function localJobToRunState(status: LocalJobRecord['status']): DocActionRunState {
  if (status === 'queued' || status === 'running') return 'running';
  if (status === 'succeeded') return 'succeeded';
  return 'failed';
}

function getDefaultRunState(command: DocActionCommand, availability: LocalBackendStatus | null): DocActionRunState {
  if (command.executionMode !== 'backend-job' || !command.actionId) return 'copy';
  if (!availability) return 'checking';
  if (!availability.available || command.prerequisitesState === 'blocked') return 'blocked';
  return 'ready';
}

function formatJobTimestamp(value: string | null): string {
  if (!value) return 'Time unavailable';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString(undefined, {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function dedupeJobs(jobs: LocalJobRecord[]): LocalJobRecord[] {
  const seen = new Set<string>();
  const result: LocalJobRecord[] = [];
  for (const job of jobs) {
    if (seen.has(job.job_id)) continue;
    seen.add(job.job_id);
    result.push(job);
  }
  return result;
}

function sortJobs(jobs: LocalJobRecord[]): LocalJobRecord[] {
  return [...jobs].sort((left, right) => right.created_at.localeCompare(left.created_at));
}

function filterHistoryJobs(jobs: LocalJobRecord[], filter: CommandHistoryFilter): LocalJobRecord[] {
  if (filter === 'all') {
    return jobs;
  }
  return jobs.filter((job) => localJobToRunState(job.status) === filter);
}

function mergeHistory(current: CommandHistoryState | undefined, job: LocalJobRecord): CommandHistoryState {
  const recentRuns = sortJobs(
    dedupeJobs([job, ...(current?.recentRuns ?? []), ...(current?.lastSuccess ? [current.lastSuccess] : [])])
  ).slice(0, 5);
  return {
    recentRuns,
    lastSuccess:
      recentRuns.find((candidate) => candidate.status === 'succeeded') ??
      (job.status === 'succeeded' ? job : null) ??
      current?.lastSuccess ??
      null,
  };
}

function sameHistory(left: CommandHistoryState | undefined, right: CommandHistoryState | undefined): boolean {
  if (!left && !right) return true;
  if (!left || !right) return false;
  if ((left.lastSuccess?.job_id ?? '') !== (right.lastSuccess?.job_id ?? '')) return false;
  if (left.recentRuns.length !== right.recentRuns.length) return false;
  return left.recentRuns.every((job, index) => job.job_id === right.recentRuns[index]?.job_id);
}

function getDrilldownState(
  current: Record<string, CommandDrilldownState>,
  historyKey: string
): CommandDrilldownState {
  return current[historyKey] ?? {
    artifacts: false,
    stdout: false,
    stderr: false,
  };
}

function getHistoryFilterLabel(filter: CommandHistoryFilter): string {
  if (filter === 'failed') return 'Failed';
  if (filter === 'succeeded') return 'Succeeded';
  return 'All';
}

function runDiffVariant(state: CommandRunDiffState): 'keyword' | 'tag' | 'beta' | 'internal' {
  if (state === 'compared') return 'beta';
  if (state === 'baseline') return 'keyword';
  return 'tag';
}

function sectionDiffVariant(state: CommandSectionDiffState): 'keyword' | 'tag' | 'stable' | 'beta' | 'internal' {
  if (state === 'changed') return 'beta';
  if (state === 'stable' || state === 'baseline') return 'stable';
  if (state === 'unavailable') return 'internal';
  return 'tag';
}

function getSectionDiffLabel(state: CommandSectionDiffState): string {
  if (state === 'changed') return 'Changed vs pinned success';
  if (state === 'stable') return 'Matches pinned success';
  if (state === 'baseline') return 'Pinned success selected';
  if (state === 'empty') return 'No output in either run';
  return 'Waiting for baseline';
}

function getSectionHeading(section: CommandDrilldownSection): string {
  if (section === 'artifacts') return 'Artifacts';
  if (section === 'stdout') return 'stdout';
  return 'stderr';
}

interface CommandSectionComparable {
  fingerprint: string;
  hasContent: boolean;
  summary: string;
}

function buildSectionComparable(
  job: LocalJobRecord,
  section: CommandDrilldownSection
): CommandSectionComparable {
  if (section === 'artifacts') {
    const artifactCount = Object.keys(job.artifacts).length;
    return {
      fingerprint: JSON.stringify(job.artifacts),
      hasContent: artifactCount > 0,
      summary: artifactCount > 0 ? `${artifactCount} field(s)` : 'no artifact metadata',
    };
  }

  const normalized = (section === 'stdout' ? job.stdout : job.stderr).trim();
  return {
    fingerprint: normalized,
    hasContent: Boolean(normalized),
    summary: normalized ? summarizeOutputForDiff(normalized) : 'no output',
  };
}

function buildSectionDiff(
  section: CommandDrilldownSection,
  selectedJob: LocalJobRecord,
  lastSuccess: LocalJobRecord | null,
  recommended: boolean
): CommandSectionDiff {
  const heading = getSectionHeading(section);
  const selectedComparable = buildSectionComparable(selectedJob, section);

  if (!lastSuccess) {
    return {
      section,
      state: 'unavailable',
      summary: `Run a successful baseline first to compare ${heading}.`,
      hasContent: selectedComparable.hasContent,
      recommended,
    };
  }

  if (selectedJob.job_id === lastSuccess.job_id) {
    return {
      section,
      state: 'baseline',
      summary: `You are reviewing the pinned success for ${heading}. Select a newer run to see section-level changes.`,
      hasContent: selectedComparable.hasContent,
      recommended,
    };
  }

  const baselineComparable = buildSectionComparable(lastSuccess, section);

  if (!selectedComparable.hasContent && !baselineComparable.hasContent) {
    return {
      section,
      state: 'empty',
      summary: `Neither the selected run nor the pinned success recorded ${heading}.`,
      hasContent: false,
      recommended,
    };
  }

  if (selectedComparable.fingerprint !== baselineComparable.fingerprint) {
    return {
      section,
      state: 'changed',
      summary:
        section === 'artifacts'
          ? `Artifact metadata changed: ${selectedComparable.summary} now vs ${baselineComparable.summary} in the pinned success.`
          : `${heading} changed: ${selectedComparable.summary} now vs ${baselineComparable.summary} in the pinned success.`,
      hasContent: selectedComparable.hasContent,
      recommended,
    };
  }

  return {
    section,
    state: 'stable',
    summary:
      section === 'artifacts'
        ? `Artifact metadata matches the pinned success: both runs recorded ${selectedComparable.summary}.`
        : `${heading} matches the pinned success: both runs recorded ${selectedComparable.summary}.`,
    hasContent: selectedComparable.hasContent,
    recommended,
  };
}

function buildRunDiffSummary(
  selectedJob: LocalJobRecord | null,
  lastSuccess: LocalJobRecord | null,
  latestJob: LocalJobRecord | null
): CommandRunDiffSummary | null {
  if (!selectedJob) {
    return null;
  }
  if (!lastSuccess) {
    return {
      state: 'unavailable',
      summary: 'No passing baseline is recorded yet. Run this action successfully once to unlock selected-vs-baseline diffs.',
      focusHint: null,
      focusSection: null,
      changedItems: [],
      stableItems: [],
    };
  }
  if (selectedJob.job_id === lastSuccess.job_id) {
    return {
      state: 'baseline',
      summary:
        latestJob && latestJob.job_id !== lastSuccess.job_id
          ? `This run is the pinned passing baseline. Compare it against the newer run ${latestJob.job_id} when you want to explain what changed.`
          : 'This run currently serves as both the latest run and the pinned passing baseline.',
      focusHint:
        latestJob && latestJob.job_id !== lastSuccess.job_id
          ? 'Select the newer run to see how it diverged from this passing baseline.'
          : 'Run the action again to create a second snapshot for comparison.',
      focusSection: null,
      changedItems: [],
      stableItems: [
        {
          label: 'Baseline status',
          detail: `Pinned success with exit code ${lastSuccess.exit_code ?? 0}.`,
        },
      ],
    };
  }

  const changedItems: CommandRunDiffItem[] = [];
  const stableItems: CommandRunDiffItem[] = [];

  if (selectedJob.status !== lastSuccess.status) {
    changedItems.push({
      label: 'Run status',
      detail: `${formatRunState(localJobToRunState(selectedJob.status))} now vs ${formatRunState(localJobToRunState(lastSuccess.status))} in the pinned success.`,
    });
  } else {
    stableItems.push({
      label: 'Run status',
      detail: `Both runs finished as ${formatRunState(localJobToRunState(selectedJob.status)).toLowerCase()}.`,
    });
  }

  if ((selectedJob.exit_code ?? null) !== (lastSuccess.exit_code ?? null)) {
    changedItems.push({
      label: 'Exit code',
      detail: `${selectedJob.exit_code ?? 'none'} now vs ${lastSuccess.exit_code ?? 'none'} in the pinned success.`,
    });
  } else {
    stableItems.push({
      label: 'Exit code',
      detail: `Both runs reported exit code ${selectedJob.exit_code ?? 'none'}.`,
    });
  }

  if (selectedJob.command_text !== lastSuccess.command_text) {
    changedItems.push({
      label: 'Command text',
      detail: 'The selected run used a different command text than the pinned success.',
    });
  } else {
    stableItems.push({
      label: 'Command text',
      detail: 'The selected run used the same command text as the pinned success.',
    });
  }

  const selectedStdout = selectedJob.stdout.trim();
  const lastSuccessStdout = lastSuccess.stdout.trim();
  const selectedStdoutSummary = summarizeOutputForDiff(selectedStdout);
  const lastSuccessStdoutSummary = summarizeOutputForDiff(lastSuccessStdout);
  if (selectedStdout !== lastSuccessStdout) {
    changedItems.push({
      label: 'stdout footprint',
      detail: `${selectedStdoutSummary} now vs ${lastSuccessStdoutSummary} in the pinned success.`,
    });
  } else {
    stableItems.push({
      label: 'stdout footprint',
      detail: `Both runs produced ${selectedStdoutSummary}.`,
    });
  }

  const selectedStderr = selectedJob.stderr.trim();
  const lastSuccessStderr = lastSuccess.stderr.trim();
  const selectedStderrSummary = summarizeOutputForDiff(selectedStderr);
  const lastSuccessStderrSummary = summarizeOutputForDiff(lastSuccessStderr);
  if (selectedStderr !== lastSuccessStderr) {
    changedItems.push({
      label: 'stderr footprint',
      detail: `${selectedStderrSummary} now vs ${lastSuccessStderrSummary} in the pinned success.`,
    });
  } else {
    stableItems.push({
      label: 'stderr footprint',
      detail: `Both runs produced ${selectedStderrSummary}.`,
    });
  }

  const selectedArtifactFingerprint = JSON.stringify(selectedJob.artifacts);
  const lastSuccessArtifactFingerprint = JSON.stringify(lastSuccess.artifacts);
  if (selectedArtifactFingerprint !== lastSuccessArtifactFingerprint) {
    changedItems.push({
      label: 'Artifact metadata',
      detail: 'Artifact metadata changed. Use the artifact drilldown to inspect path or payload differences.',
    });
  } else {
    stableItems.push({
      label: 'Artifact metadata',
      detail: `Artifact metadata stayed stable across ${Object.keys(selectedJob.artifacts).length} field(s).`,
    });
  }

  const stderrChanged = selectedStderr !== lastSuccessStderr;
  const stdoutChanged = selectedStdout !== lastSuccessStdout;
  const artifactChanged = selectedArtifactFingerprint !== lastSuccessArtifactFingerprint;

  const focusHint = stderrChanged && selectedStderr
    ? 'Start with stderr drilldown, then compare stdout if you still need more context.'
    : stdoutChanged && selectedStdout
      ? 'Start with stdout drilldown to inspect the changed command output.'
      : artifactChanged && Object.keys(selectedJob.artifacts).length > 0
        ? 'Start with artifact drilldown to inspect the changed metadata.'
        : null;
  const focusSection = stderrChanged && selectedStderr
    ? 'stderr'
    : stdoutChanged && selectedStdout
      ? 'stdout'
      : artifactChanged && Object.keys(selectedJob.artifacts).length > 0
        ? 'artifacts'
        : null;

  return {
    state: 'compared',
    summary:
      changedItems.length > 0
        ? `Comparing selected run ${selectedJob.job_id} against pinned success ${lastSuccess.job_id}.`
        : `Selected run ${selectedJob.job_id} matches the pinned success ${lastSuccess.job_id} across the tracked summary signals.`,
    focusHint,
    focusSection,
    changedItems,
    stableItems,
  };
}

function getCompareHint(
  selectedJob: LocalJobRecord | null,
  latestJob: LocalJobRecord | null,
  lastSuccess: LocalJobRecord | null
): string {
  if (!selectedJob) {
    return '';
  }
  if (latestJob?.job_id === selectedJob.job_id && latestJob.status === 'failed' && lastSuccess) {
    return 'This is the newest failed run. Compare it with the pinned last success to isolate the regression.';
  }
  if (lastSuccess?.job_id === selectedJob.job_id && latestJob && latestJob.job_id !== selectedJob.job_id) {
    return 'This is the pinned passing baseline from recent history. Compare it with the newest run to spot changes quickly.';
  }
  if (latestJob?.job_id === selectedJob.job_id) {
    return 'This is the latest recorded run for this docs action.';
  }
  return 'This historical run stays available for comparison against the latest recorded run.';
}

export function DocActionPanel({ panel }: DocActionPanelProps) {
  const [availability, setAvailability] = useState<LocalBackendStatus | null>(null);
  const [copiedCommandKey, setCopiedCommandKey] = useState<string | null>(null);
  const [failedCommandKey, setFailedCommandKey] = useState<string | null>(null);
  const [commandStates, setCommandStates] = useState<Record<string, CommandExecutionState>>({});
  const [commandHistory, setCommandHistory] = useState<Record<string, CommandHistoryState>>({});
  const [selectedJobIds, setSelectedJobIds] = useState<Record<string, string>>({});
  const [drilldowns, setDrilldowns] = useState<Record<string, CommandDrilldownState>>({});
  const [historyFilters, setHistoryFilters] = useState<Record<string, CommandHistoryFilter>>({});

  const hasBackendCommand = useMemo(
    () => panel.commands.some((command) => command.executionMode === 'backend-job' && command.actionId),
    [panel.commands]
  );

  useEffect(() => {
    if (!hasBackendCommand) return undefined;
    let cancelled = false;

    async function loadAvailability() {
      try {
        const response = await fetch('/api/local/status', { cache: 'no-store' });
        const payload = (await response.json()) as LocalBackendStatus;
        if (!cancelled) setAvailability(payload);
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
  }, [hasBackendCommand]);

  useEffect(() => {
    if (!hasBackendCommand) {
      setCommandHistory({});
      return undefined;
    }
    let cancelled = false;

    async function loadHistory() {
      try {
        const searchParams = new URLSearchParams({
          doc_kind: panel.docKind,
          doc_id: panel.docId,
          limit: '5',
        });
        const response = await fetch(`/api/local/docs/actions/history?${searchParams.toString()}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalDocsActionHistoryPayload;
        if (!response.ok || cancelled) return;
        const nextHistory: Record<string, CommandHistoryState> = {};
        for (const action of payload.actions) {
          nextHistory[action.action_id] = {
            recentRuns: sortJobs(action.recent_runs),
            lastSuccess: action.last_success,
          };
        }
        setCommandHistory(nextHistory);
      } catch {
        // Keep docs action history best-effort.
      }
    }

    void loadHistory();
    return () => {
      cancelled = true;
    };
  }, [hasBackendCommand, panel.docId, panel.docKind]);

  useEffect(() => {
    if (!copiedCommandKey && !failedCommandKey) return undefined;
    const timeoutId = window.setTimeout(() => {
      setCopiedCommandKey(null);
      setFailedCommandKey(null);
    }, 1600);
    return () => window.clearTimeout(timeoutId);
  }, [copiedCommandKey, failedCommandKey]);

  useEffect(() => {
    const runningEntries = Object.entries(commandStates).filter(([, state]) =>
      Boolean(state.job && (state.job.status === 'queued' || state.job.status === 'running'))
    );
    if (runningEntries.length === 0) return undefined;

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      const updates = await Promise.all(
        runningEntries.map(async ([commandKey, state]) => {
          try {
            const response = await fetch(`/api/local/jobs/${state.job?.job_id}`, { cache: 'no-store' });
            const payload = (await response.json()) as LocalJobRecord | { detail?: string };
            if (!response.ok) {
              return {
                commandKey,
                nextState: {
                  status: 'failed' as const,
                  job: state.job,
                  errorMessage:
                    payload && 'detail' in payload ? payload.detail ?? 'Unable to refresh docs action job.' : 'Unable to refresh docs action job.',
                },
              };
            }
            return {
              commandKey,
              nextState: {
                status: localJobToRunState((payload as LocalJobRecord).status),
                job: payload as LocalJobRecord,
                errorMessage: null,
              },
            };
          } catch (error) {
            return {
              commandKey,
              nextState: {
                status: 'failed' as const,
                job: state.job,
                errorMessage: `Unable to refresh docs action job: ${
                  error instanceof Error ? error.message : String(error)
                }`,
              },
            };
          }
        })
      );

      if (cancelled) return;
      setCommandStates((currentStates) => {
        const nextStates = { ...currentStates };
        for (const update of updates) {
          nextStates[update.commandKey] = update.nextState;
        }
        return nextStates;
      });
    }, 700);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [commandStates]);

  useEffect(() => {
    setCommandHistory((currentHistory) => {
      let changed = false;
      const nextHistory = { ...currentHistory };
      for (const command of panel.commands) {
        if (!command.actionId) continue;
        const commandState = commandStates[getCommandKey(command.label, command.command)];
        if (!commandState?.job) continue;
        const historyKey = getHistoryKey(command);
        const merged = mergeHistory(currentHistory[historyKey], commandState.job);
        if (!sameHistory(currentHistory[historyKey], merged)) {
          nextHistory[historyKey] = merged;
          changed = true;
        }
      }
      return changed ? nextHistory : currentHistory;
    });
  }, [commandStates, panel.commands]);

  useEffect(() => {
    setSelectedJobIds((currentSelections) => {
      let changed = false;
      const nextSelections = { ...currentSelections };
      for (const command of panel.commands) {
        if (!command.actionId) continue;
        const historyKey = getHistoryKey(command);
        const currentJob = commandStates[getCommandKey(command.label, command.command)]?.job ?? null;
        const history = commandHistory[historyKey];
        const candidates = sortJobs(
          dedupeJobs([...(currentJob ? [currentJob] : []), ...(history?.recentRuns ?? []), ...(history?.lastSuccess ? [history.lastSuccess] : [])])
        );
        const filter = historyFilters[historyKey] ?? 'all';
        const filteredCandidates = filterHistoryJobs(candidates, filter);
        if (currentSelections[historyKey] && filteredCandidates.some((job) => job.job_id === currentSelections[historyKey])) {
          continue;
        }
        if (filter === 'all' && currentSelections[historyKey] && candidates.some((job) => job.job_id === currentSelections[historyKey])) {
          continue;
        }
        const nextJobId = filteredCandidates[0]?.job_id ?? currentJob?.job_id ?? candidates[0]?.job_id;
        if (nextJobId) {
          nextSelections[historyKey] = nextJobId;
          changed = true;
        }
      }
      return changed ? nextSelections : currentSelections;
    });
  }, [commandHistory, commandStates, historyFilters, panel.commands]);

  async function handleCopyCommand(commandLabel: string, commandText: string): Promise<void> {
    const commandKey = getCommandKey(commandLabel, commandText);
    try {
      await copyCommandText(commandText);
      setCopiedCommandKey(commandKey);
      setFailedCommandKey(null);
    } catch {
      setCopiedCommandKey(null);
      setFailedCommandKey(commandKey);
    }
  }

  async function handleRunCommand(command: DocActionCommand): Promise<void> {
    if (command.executionMode !== 'backend-job' || !command.actionId) return;
    const commandKey = getCommandKey(command.label, command.command);
    setCommandStates((currentStates) => ({
      ...currentStates,
      [commandKey]: {
        status: availability?.available ? 'running' : 'blocked',
        job: null,
        errorMessage: availability?.available ? null : availability?.message ?? 'Backend execution is not available.',
      },
    }));

    try {
      const response = await fetch('/api/local/docs/actions/run', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          doc_kind: panel.docKind,
          doc_id: panel.docId,
          action_id: command.actionId,
        }),
      });
      const payload = (await response.json()) as LocalJobRecord | { detail?: string };
      if (!response.ok) {
        setCommandStates((currentStates) => ({
          ...currentStates,
          [commandKey]: {
            status: 'failed',
            job: null,
            errorMessage:
              payload && 'detail' in payload ? payload.detail ?? 'Docs action execution failed.' : 'Docs action execution failed.',
          },
        }));
        return;
      }
      setCommandStates((currentStates) => ({
        ...currentStates,
        [commandKey]: {
          status: localJobToRunState((payload as LocalJobRecord).status),
          job: payload as LocalJobRecord,
          errorMessage: null,
        },
      }));
      setSelectedJobIds((currentSelections) => ({
        ...currentSelections,
        [getHistoryKey(command)]: (payload as LocalJobRecord).job_id,
      }));
    } catch (error) {
      setCommandStates((currentStates) => ({
        ...currentStates,
        [commandKey]: {
          status: 'failed',
          job: null,
          errorMessage: `Docs action request failed: ${error instanceof Error ? error.message : String(error)}`,
        },
      }));
    }
  }

  function toggleDrilldown(historyKey: string, section: keyof CommandDrilldownState) {
    setDrilldowns((currentDrilldowns) => ({
      ...currentDrilldowns,
      [historyKey]: {
        ...getDrilldownState(currentDrilldowns, historyKey),
        [section]: !getDrilldownState(currentDrilldowns, historyKey)[section],
      },
    }));
  }

  function openDrilldownSection(historyKey: string, section: CommandDrilldownSection) {
    setDrilldowns((currentDrilldowns) => ({
      ...currentDrilldowns,
      [historyKey]: {
        ...getDrilldownState(currentDrilldowns, historyKey),
        [section]: true,
      },
    }));
  }

  function handleHistoryFilterChange(historyKey: string, filter: CommandHistoryFilter, jobs: LocalJobRecord[]) {
    setHistoryFilters((currentFilters) => ({
      ...currentFilters,
      [historyKey]: filter,
    }));
    const filteredJobs = filterHistoryJobs(jobs, filter);
    if (filteredJobs.length === 0) {
      return;
    }
    setSelectedJobIds((currentSelections) => {
      if (currentSelections[historyKey] && filteredJobs.some((job) => job.job_id === currentSelections[historyKey])) {
        return currentSelections;
      }
      return {
        ...currentSelections,
        [historyKey]: filteredJobs[0].job_id,
      };
    });
  }

  return (
    <Card className="p-5" data-testid="doc-action-panel">
      <div className="mb-5">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{panel.title}</h3>
        <p className="text-sm text-muted">{panel.description}</p>
        {hasBackendCommand && availability && (
          <p className="mt-3 text-xs text-muted" data-testid="doc-action-backend-availability">
            {availability.message}
          </p>
        )}
        {panel.commands.length > 1 && (
          <p className="mt-3 text-xs font-medium uppercase tracking-[0.2em] text-muted" data-testid="doc-action-runbook-hint">
            Recommended run order
          </p>
        )}
      </div>

      <div className="space-y-4">
        {panel.commands.map((command, index) => {
          const sequenceMeta = getCommandSequenceMeta(index, panel.commands.length);
          const commandKey = getCommandKey(command.label, command.command);
          const historyKey = getHistoryKey(command);
          const commandState = commandStates[commandKey];
          const history = commandHistory[historyKey];
          const runState = commandState?.status ?? getDefaultRunState(command, availability);
          const canRun =
            command.executionMode === 'backend-job' &&
            Boolean(command.actionId) &&
            runState !== 'checking' &&
            runState !== 'blocked' &&
            runState !== 'running';
          const allRecentRuns = sortJobs(
            dedupeJobs([
              ...(commandState?.job ? [commandState.job] : []),
              ...(history?.recentRuns ?? []),
              ...(history?.lastSuccess ? [history.lastSuccess] : []),
            ])
          );
          const latestJob = allRecentRuns[0] ?? null;
          const historyFilter = historyFilters[historyKey] ?? 'all';
          const filteredRecentRuns = filterHistoryJobs(allRecentRuns, historyFilter);
          const selectedJob = allRecentRuns.find((job) => job.job_id === selectedJobIds[historyKey])
            ?? commandState?.job
            ?? filteredRecentRuns[0]
            ?? history?.recentRuns[0]
            ?? history?.lastSuccess
            ?? null;
          const summaryEntries = selectedJob ? Object.entries(selectedJob.summary) : [];
          const artifactEntries = selectedJob ? Object.entries(selectedJob.artifacts) : [];
          const drilldownState = getDrilldownState(drilldowns, historyKey);
          const hasStdout = Boolean(selectedJob?.stdout.trim());
          const hasStderr = Boolean(selectedJob?.stderr.trim());
          const succeededRunCount = allRecentRuns.filter((job) => job.status === 'succeeded').length;
          const failedRunCount = allRecentRuns.filter((job) => job.status === 'failed').length;
          const artifactSummary = artifactEntries.length
            ? `${artifactEntries.length} artifact field(s) captured for this run.`
            : 'No artifact paths or output metadata were captured for this run.';
          const stdoutSummary = selectedJob && hasStdout ? summarizeOutput(selectedJob.stdout) : 'No stdout captured.';
          const stderrSummary = selectedJob && hasStderr ? summarizeOutput(selectedJob.stderr) : 'No stderr captured.';
          const historySummary = allRecentRuns.length
            ? `Showing ${filteredRecentRuns.length} of ${allRecentRuns.length} recent run(s). ${failedRunCount} failed, ${succeededRunCount} succeeded.`
            : 'No recent runs recorded yet.';
          const compareHint = getCompareHint(selectedJob, latestJob, history?.lastSuccess ?? null);
          const runDiffSummary = buildRunDiffSummary(selectedJob, history?.lastSuccess ?? null, latestJob);
          const artifactDiff =
            selectedJob &&
            buildSectionDiff(
              'artifacts',
              selectedJob,
              history?.lastSuccess ?? null,
              runDiffSummary?.focusSection === 'artifacts'
            );
          const stdoutDiff =
            selectedJob &&
            buildSectionDiff(
              'stdout',
              selectedJob,
              history?.lastSuccess ?? null,
              runDiffSummary?.focusSection === 'stdout'
            );
          const stderrDiff =
            selectedJob &&
            buildSectionDiff(
              'stderr',
              selectedJob,
              history?.lastSuccess ?? null,
              runDiffSummary?.focusSection === 'stderr'
            );
          const quickOpenSections = [artifactDiff, stdoutDiff, stderrDiff].filter(
            (sectionDiff): sectionDiff is CommandSectionDiff =>
              Boolean(sectionDiff) &&
              sectionDiff.hasContent &&
              (sectionDiff.state === 'changed' || sectionDiff.recommended)
          );
          const summarySource =
            selectedJob?.job_id && commandState?.job?.job_id === selectedJob.job_id
              ? 'Viewing the latest in-page run.'
              : selectedJob?.job_id && history?.lastSuccess?.job_id === selectedJob.job_id
                ? 'Viewing the last successful run saved in recent history.'
                : selectedJob
                  ? 'Viewing a recent run from docs action history.'
                  : '';

          return (
            <div key={`${command.label}-${command.command}`} className="rounded-card border border-line/80 bg-paper/70 p-4">
              <div className="mb-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-olive" data-testid={`doc-action-sequence-${index + 1}`}>
                  {sequenceMeta.badge}
                </p>
                <p className="mt-1 text-xs text-muted">{sequenceMeta.description}</p>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">{command.label}</p>
                <div className="flex flex-wrap items-center gap-2">
                  {command.executionMode === 'backend-job' && command.actionId && (
                    <Button type="button" size="sm" className="shrink-0" data-testid={getRunTestId(command.testId)} disabled={!canRun} onClick={() => void handleRunCommand(command)}>
                      {runState === 'running' ? 'Running...' : 'Run here'}
                    </Button>
                  )}
                  <Button type="button" variant="secondary" size="sm" className="shrink-0" data-testid={getCopyTestId(command.testId)} onClick={() => void handleCopyCommand(command.label, command.command)}>
                    {copiedCommandKey === commandKey ? 'Copied' : failedCommandKey === commandKey ? 'Retry copy' : 'Copy'}
                  </Button>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <Chip variant={runStateVariant(runState)} data-testid={getStatusTestId(command.testId)}>
                  {formatRunState(runState)}
                </Chip>
                {command.executionMode === 'backend-job' && command.actionId && availability && (
                  <span className="text-xs text-muted">
                    {runState === 'blocked' ? availability.message : 'This action can run through the backend job bridge from the docs page.'}
                  </span>
                )}
              </div>

              <pre className="mt-2 overflow-x-auto rounded-card border border-line bg-bg px-3 py-3 text-xs leading-6 text-ink whitespace-pre-wrap break-all" data-testid={command.testId}>
                <code>{command.command}</code>
              </pre>

              {command.executionSummary && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3" data-testid={getExecutionSummaryTestId(command.testId)}>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Execution mode</p>
                  <p className="mt-1 text-xs leading-6 text-ink">{command.executionSummary}</p>
                </div>
              )}

              {(command.prerequisites || command.prerequisitesState) && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3" data-testid={getPrerequisitesTestId(command.testId)}>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Prerequisites</p>
                    <Chip variant={prerequisiteStateVariant(command.prerequisitesState)} data-testid={getPrerequisiteStateTestId(command.testId)}>
                      {formatPrerequisiteState(command.prerequisitesState)}
                    </Chip>
                  </div>
                  {command.prerequisites && <p className="mt-1 text-xs leading-6 text-ink">{command.prerequisites}</p>}
                </div>
              )}

              {command.expectedOutcome && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3" data-testid={getOutcomeTestId(command.testId)}>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Expected outcome</p>
                  <p className="mt-1 text-xs leading-6 text-ink">{command.expectedOutcome}</p>
                </div>
              )}

              {command.artifacts && command.artifacts.length > 0 && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3" data-testid={getArtifactsTestId(command.testId)}>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Artifacts and outputs</p>
                  <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                    {command.artifacts.map((artifact) => (
                      <li key={artifact}>- {artifact}</li>
                    ))}
                  </ul>
                </div>
              )}

              {command.executionMode === 'backend-job' && command.actionId && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3" data-testid={getHistoryTestId(command.testId)}>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Recent runs</p>
                    <span className="text-xs text-muted" data-testid={getHistorySummaryTestId(command.testId)}>
                      {historySummary}
                    </span>
                  </div>
                  <div className="mt-3 rounded-card border border-line bg-paper/70 px-3 py-3" data-testid={getLastSuccessTestId(command.testId)}>
                    {history?.lastSuccess ? (
                      <>
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex flex-wrap items-center gap-2">
                            <Chip variant="keyword">Last success</Chip>
                            <span className="text-xs text-muted">{formatJobTimestamp(history.lastSuccess.finished_at ?? history.lastSuccess.created_at)}</span>
                          </div>
                          {selectedJob?.job_id !== history.lastSuccess.job_id && (
                            <Button type="button" variant="ghost" size="sm" onClick={() => setSelectedJobIds((currentSelections) => ({ ...currentSelections, [historyKey]: history.lastSuccess!.job_id }))}>
                              Review
                            </Button>
                          )}
                        </div>
                        <p className="mt-2 text-xs leading-6 text-ink">
                          Job <span className="font-mono">{history.lastSuccess.job_id}</span> completed successfully and stays available for revisit even if the newest run fails.
                        </p>
                      </>
                    ) : (
                      <p className="text-xs text-muted">No successful run recorded yet. The first passing backend run will stay pinned here for revisit.</p>
                    )}
                  </div>
                  {allRecentRuns.length ? (
                    <div className="mt-3 space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        {(['all', 'failed', 'succeeded'] as CommandHistoryFilter[]).map((filter) => {
                          const filterCount = filterHistoryJobs(allRecentRuns, filter).length;
                          return (
                            <Button
                              key={filter}
                              type="button"
                              variant={historyFilter === filter ? 'primary' : 'ghost'}
                              size="sm"
                              data-testid={getHistoryFilterTestId(command.testId, filter)}
                              onClick={() => handleHistoryFilterChange(historyKey, filter, allRecentRuns)}
                            >
                              {getHistoryFilterLabel(filter)} ({filterCount})
                            </Button>
                          );
                        })}
                      </div>
                      {filteredRecentRuns.length ? filteredRecentRuns.map((job, historyIndex) => {
                        const historyStatus = localJobToRunState(job.status);
                        const isSelected = selectedJob?.job_id === job.job_id;
                        const isLastSuccess = history?.lastSuccess?.job_id === job.job_id;
                        const isLatest = latestJob?.job_id === job.job_id;
                        return (
                          <button
                            key={job.job_id}
                            type="button"
                            className={`w-full rounded-card border px-3 py-3 text-left transition-colors ${isSelected ? 'border-olive bg-[#f0f5ea]' : 'border-line bg-paper/70 hover:border-olive/50 hover:bg-[#f8faf5]'}`}
                            onClick={() => setSelectedJobIds((currentSelections) => ({ ...currentSelections, [historyKey]: job.job_id }))}
                            data-testid={getHistoryEntryTestId(command.testId, historyIndex + 1)}
                          >
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <div className="flex flex-wrap items-center gap-2">
                                <Chip variant={runStateVariant(historyStatus)}>{formatRunState(historyStatus)}</Chip>
                                {isLatest && <Chip variant="beta">Latest</Chip>}
                                {isLastSuccess && <Chip variant="keyword">Pinned success</Chip>}
                                <span className="text-xs text-muted">{formatJobTimestamp(job.finished_at ?? job.created_at)}</span>
                              </div>
                              <span className="text-xs text-muted">{isSelected ? 'Currently reviewing this run' : 'Click to review'}</span>
                            </div>
                            <p className="mt-2 text-xs text-ink">
                              <span className="font-mono">{job.job_id}</span> - {formatValue(job.summary.label)}
                            </p>
                          </button>
                        );
                      }) : (
                        <p className="rounded-card border border-line bg-paper/70 px-3 py-3 text-xs text-muted">
                          No {getHistoryFilterLabel(historyFilter).toLowerCase()} runs are available yet. Switch filters to keep comparing recent history.
                        </p>
                      )}
                    </div>
                  ) : (
                    <p className="mt-3 text-xs text-muted">Use Run here to create the first backend record for this docs action.</p>
                  )}
                </div>
              )}

              {commandState?.errorMessage && (
                <div className="mt-3 rounded-card border border-[#f0d4b8] bg-[#fff4e8] px-3 py-3 text-xs text-accent" data-testid={getErrorTestId(command.testId)}>
                  {commandState.errorMessage}
                </div>
              )}

              {selectedJob && (
                <div className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3" data-testid={getSummaryTestId(command.testId)}>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Result summary</p>
                    {summarySource && (
                      <span className="text-xs text-muted" data-testid={getSummarySourceTestId(command.testId)}>
                        {summarySource}
                      </span>
                    )}
                  </div>
                  {compareHint && (
                    <p className="mt-2 text-xs text-muted" data-testid={getCompareHintTestId(command.testId)}>
                      {compareHint}
                    </p>
                  )}
                  {runDiffSummary && (
                    <div
                      className="mt-3 rounded-card border border-dashed border-line bg-paper/70 px-3 py-3"
                      data-testid={getRunDiffSummaryTestId(command.testId)}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Run diff summary</p>
                        <Chip variant={runDiffVariant(runDiffSummary.state)}>
                          {runDiffSummary.state === 'compared'
                            ? 'Compared to pinned success'
                            : runDiffSummary.state === 'baseline'
                              ? 'Pinned success selected'
                              : 'Waiting for baseline'}
                        </Chip>
                      </div>
                      <p className="mt-2 text-xs leading-6 text-ink">{runDiffSummary.summary}</p>
                      {runDiffSummary.focusHint && (
                        <p className="mt-2 text-xs text-muted" data-testid={getRunDiffFocusTestId(command.testId)}>
                          {runDiffSummary.focusHint}
                        </p>
                      )}
                      {quickOpenSections.length > 0 && (
                        <div className="mt-3 flex flex-wrap items-center gap-2">
                          {quickOpenSections.map((sectionDiff) => (
                            <Button
                              key={sectionDiff.section}
                              type="button"
                              variant={sectionDiff.recommended ? 'primary' : 'ghost'}
                              size="sm"
                              data-testid={getRunDiffOpenTestId(command.testId, sectionDiff.section)}
                              onClick={() => openDrilldownSection(historyKey, sectionDiff.section)}
                            >
                              {sectionDiff.recommended
                                ? `Open ${getSectionHeading(sectionDiff.section)} first`
                                : `Open ${getSectionHeading(sectionDiff.section)}`}
                            </Button>
                          ))}
                        </div>
                      )}
                      {runDiffSummary.changedItems.length > 0 && (
                        <div className="mt-3" data-testid={getRunDiffChangedTestId(command.testId)}>
                          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Changed from pinned success</p>
                          <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                            {runDiffSummary.changedItems.map((item) => (
                              <li key={`changed-${item.label}`}>- {item.label}: {item.detail}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {runDiffSummary.stableItems.length > 0 && (
                        <div className="mt-3" data-testid={getRunDiffStableTestId(command.testId)}>
                          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Still aligned with pinned success</p>
                          <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                            {runDiffSummary.stableItems.map((item) => (
                              <li key={`stable-${item.label}`}>- {item.label}: {item.detail}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  <dl className="mt-2 space-y-2 text-xs text-ink">
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Job ID</dt>
                      <dd className="font-mono text-right">{selectedJob.job_id}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Command</dt>
                      <dd className="font-mono text-right break-all">{selectedJob.command_text}</dd>
                    </div>
                    {summaryEntries.map(([key, value]) => (
                      <div key={key} className="flex justify-between gap-3">
                        <dt className="text-muted">{key.replace(/_/g, ' ')}</dt>
                        <dd className="text-right break-all">{formatValue(value)}</dd>
                      </div>
                    ))}
                  </dl>
                  <div className="mt-4 space-y-3">
                    <div
                      className={cn(
                        'rounded-card border border-dashed px-3 py-3',
                        artifactDiff?.state === 'changed'
                          ? 'border-[#e8c9b8] bg-[#fff8ef]'
                          : artifactDiff?.state === 'stable' || artifactDiff?.state === 'baseline'
                            ? 'border-[#c8dbc9] bg-[#f4f8ef]'
                            : 'border-line bg-paper/70',
                        artifactDiff?.recommended && 'ring-1 ring-olive/40'
                      )}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Artifacts</p>
                            {artifactDiff && (
                              <Chip variant={sectionDiffVariant(artifactDiff.state)} data-testid={getArtifactDiffStateTestId(command.testId)}>
                                {getSectionDiffLabel(artifactDiff.state)}
                              </Chip>
                            )}
                            {artifactDiff?.recommended && <Chip variant="keyword">Review first</Chip>}
                          </div>
                          <p className="mt-1 text-xs text-muted">{artifactSummary}</p>
                          {artifactDiff && <p className="mt-1 text-xs text-muted">{artifactDiff.summary}</p>}
                        </div>
                        {artifactEntries.length > 0 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            data-testid={getArtifactToggleTestId(command.testId)}
                            onClick={() => toggleDrilldown(historyKey, 'artifacts')}
                          >
                            {drilldownState.artifacts ? 'Hide details' : 'Review details'}
                          </Button>
                        )}
                      </div>
                      {artifactEntries.length > 0 && drilldownState.artifacts && (
                        <div className="mt-3 space-y-2" data-testid={getArtifactDrilldownTestId(command.testId)}>
                          {artifactEntries.map(([key, value]) => (
                            <div key={key} className="rounded-card border border-line bg-bg px-3 py-3">
                              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                                {key.replace(/_/g, ' ')}
                              </p>
                              <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink">
                                <code>{formatDetailedValue(value)}</code>
                              </pre>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div
                      className={cn(
                        'rounded-card border border-dashed px-3 py-3',
                        stdoutDiff?.state === 'changed'
                          ? 'border-[#e8c9b8] bg-[#fff8ef]'
                          : stdoutDiff?.state === 'stable' || stdoutDiff?.state === 'baseline'
                            ? 'border-[#c8dbc9] bg-[#f4f8ef]'
                            : 'border-line bg-paper/70',
                        stdoutDiff?.recommended && 'ring-1 ring-olive/40'
                      )}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">stdout</p>
                            {stdoutDiff && (
                              <Chip variant={sectionDiffVariant(stdoutDiff.state)} data-testid={getStdoutDiffStateTestId(command.testId)}>
                                {getSectionDiffLabel(stdoutDiff.state)}
                              </Chip>
                            )}
                            {stdoutDiff?.recommended && <Chip variant="keyword">Review first</Chip>}
                          </div>
                          <p className="mt-1 text-xs text-muted">{stdoutSummary}</p>
                          {stdoutDiff && <p className="mt-1 text-xs text-muted">{stdoutDiff.summary}</p>}
                        </div>
                        {hasStdout && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            data-testid={getStdoutToggleTestId(command.testId)}
                            onClick={() => toggleDrilldown(historyKey, 'stdout')}
                          >
                            {drilldownState.stdout ? 'Hide stdout' : 'Review stdout'}
                          </Button>
                        )}
                      </div>
                      {hasStdout && drilldownState.stdout && (
                        <pre
                          className="mt-3 overflow-x-auto rounded-card border border-line bg-bg px-3 py-3 whitespace-pre-wrap break-all text-xs leading-6 text-ink"
                          data-testid={getStdoutDrilldownTestId(command.testId)}
                        >
                          <code>{truncateDetailedOutput(selectedJob.stdout)}</code>
                        </pre>
                      )}
                    </div>

                    <div
                      className={cn(
                        'rounded-card border border-dashed px-3 py-3',
                        stderrDiff?.state === 'changed'
                          ? 'border-[#e8c9b8] bg-[#fff8ef]'
                          : stderrDiff?.state === 'stable' || stderrDiff?.state === 'baseline'
                            ? 'border-[#c8dbc9] bg-[#f4f8ef]'
                            : 'border-line bg-paper/70',
                        stderrDiff?.recommended && 'ring-1 ring-olive/40'
                      )}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">stderr</p>
                            {stderrDiff && (
                              <Chip variant={sectionDiffVariant(stderrDiff.state)} data-testid={getStderrDiffStateTestId(command.testId)}>
                                {getSectionDiffLabel(stderrDiff.state)}
                              </Chip>
                            )}
                            {stderrDiff?.recommended && <Chip variant="keyword">Review first</Chip>}
                          </div>
                          <p className="mt-1 text-xs text-muted">{stderrSummary}</p>
                          {stderrDiff && <p className="mt-1 text-xs text-muted">{stderrDiff.summary}</p>}
                        </div>
                        {hasStderr && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            data-testid={getStderrToggleTestId(command.testId)}
                            onClick={() => toggleDrilldown(historyKey, 'stderr')}
                          >
                            {drilldownState.stderr ? 'Hide stderr' : 'Review stderr'}
                          </Button>
                        )}
                      </div>
                      {hasStderr && drilldownState.stderr && (
                        <pre
                          className="mt-3 overflow-x-auto rounded-card border border-line bg-bg px-3 py-3 whitespace-pre-wrap break-all text-xs leading-6 text-ink"
                          data-testid={getStderrDrilldownTestId(command.testId)}
                        >
                          <code>{truncateDetailedOutput(selectedJob.stderr)}</code>
                        </pre>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {panel.links.length > 0 && (
        <div className="mt-5 border-t border-line pt-5 space-y-2">
          {panel.links.map((link) => (
            <Link key={`${link.href}-${link.label}`} href={link.href} className="block text-sm text-accent hover:underline" data-testid={link.testId}>
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </Card>
  );
}
