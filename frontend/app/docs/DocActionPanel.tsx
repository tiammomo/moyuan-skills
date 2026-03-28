'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import type {
  DocActionCommand,
  DocActionPanelData,
  LocalBackendStatus,
  LocalJobRecord,
} from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface DocActionPanelProps {
  panel: DocActionPanelData;
}

type DocActionRunState = 'copy' | 'checking' | 'ready' | 'blocked' | 'running' | 'succeeded' | 'failed';

interface CommandExecutionState {
  status: DocActionRunState;
  job: LocalJobRecord | null;
  errorMessage: string | null;
}

interface CommandSequenceMeta {
  badge: string;
  description: string;
}

function getCommandKey(label: string, command: string): string {
  return `${label}:${command}`;
}

function getCopyTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-copy-');
  }
  return `${testId}-copy`;
}

function getRunTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-run-');
  }
  return `${testId}-run`;
}

function getStatusTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-status-');
  }
  return `${testId}-status`;
}

function getSummaryTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-summary-');
  }
  return `${testId}-summary`;
}

function getErrorTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-error-');
  }
  return `${testId}-error`;
}

function getOutcomeTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-outcome-');
  }
  return `${testId}-outcome`;
}

function getPrerequisitesTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-prerequisites-');
  }
  return `${testId}-prerequisites`;
}

function getPrerequisiteStateTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-prerequisites-state-');
  }
  return `${testId}-prerequisites-state`;
}

function getArtifactsTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-artifacts-');
  }
  return `${testId}-artifacts`;
}

function getExecutionSummaryTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-execution-summary-');
  }
  return `${testId}-execution-summary`;
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
    return {
      badge: 'Step 1',
      description: 'Run this command for the current doc flow.',
    };
  }

  if (index === 0) {
    return {
      badge: 'Step 1 - Start here',
      description: 'Use this first so the rest of the runbook has the right baseline.',
    };
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

function truncateOutput(value: string): string {
  const normalized = value.trim();
  if (normalized.length <= 800) {
    return normalized;
  }
  return `...${normalized.slice(-800)}`;
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

function formatRunState(status: DocActionRunState): string {
  if (status === 'copy') {
    return 'Copy only';
  }
  if (status === 'checking') {
    return 'Checking backend';
  }
  if (status === 'ready') {
    return 'Ready';
  }
  if (status === 'blocked') {
    return 'Blocked';
  }
  if (status === 'running') {
    return 'Running';
  }
  if (status === 'succeeded') {
    return 'Succeeded';
  }
  return 'Failed';
}

function runStateVariant(status: DocActionRunState): 'keyword' | 'tag' | 'beta' | 'internal' {
  if (status === 'ready' || status === 'succeeded') {
    return 'keyword';
  }
  if (status === 'running') {
    return 'beta';
  }
  if (status === 'blocked' || status === 'failed') {
    return 'internal';
  }
  return 'tag';
}

function formatPrerequisiteState(state?: DocActionCommand['prerequisitesState']): string {
  if (state === 'ready') {
    return 'Ready in-page';
  }
  if (state === 'blocked') {
    return 'Blocked';
  }
  return 'Manual check';
}

function prerequisiteStateVariant(
  state?: DocActionCommand['prerequisitesState']
): 'keyword' | 'tag' | 'internal' {
  if (state === 'ready') {
    return 'keyword';
  }
  if (state === 'blocked') {
    return 'internal';
  }
  return 'tag';
}

function localJobToRunState(status: LocalJobRecord['status']): DocActionRunState {
  if (status === 'queued' || status === 'running') {
    return 'running';
  }
  if (status === 'succeeded') {
    return 'succeeded';
  }
  return 'failed';
}

function getDefaultRunState(command: DocActionCommand, availability: LocalBackendStatus | null): DocActionRunState {
  if (command.executionMode !== 'backend-job' || !command.actionId) {
    return 'copy';
  }
  if (!availability) {
    return 'checking';
  }
  if (!availability.available || command.prerequisitesState === 'blocked') {
    return 'blocked';
  }
  return 'ready';
}

export function DocActionPanel({ panel }: DocActionPanelProps) {
  const [availability, setAvailability] = useState<LocalBackendStatus | null>(null);
  const [copiedCommandKey, setCopiedCommandKey] = useState<string | null>(null);
  const [failedCommandKey, setFailedCommandKey] = useState<string | null>(null);
  const [commandStates, setCommandStates] = useState<Record<string, CommandExecutionState>>({});

  const hasBackendCommand = useMemo(
    () => panel.commands.some((command) => command.executionMode === 'backend-job' && command.actionId),
    [panel.commands]
  );

  useEffect(() => {
    if (!hasBackendCommand) {
      return undefined;
    }

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
  }, [hasBackendCommand]);

  useEffect(() => {
    if (!copiedCommandKey && !failedCommandKey) {
      return undefined;
    }

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

    if (runningEntries.length === 0) {
      return undefined;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      const updates = await Promise.all(
        runningEntries.map(async ([commandKey, state]) => {
          try {
            const response = await fetch(`/api/local/jobs/${state.job?.job_id}`, {
              cache: 'no-store',
            });
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

      if (cancelled) {
        return;
      }

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
    if (command.executionMode !== 'backend-job' || !command.actionId) {
      return;
    }

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
        headers: {
          'content-type': 'application/json',
        },
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
          const commandState = commandStates[commandKey];
          const runState = commandState?.status ?? getDefaultRunState(command, availability);
          const canRun =
            command.executionMode === 'backend-job' &&
            Boolean(command.actionId) &&
            runState !== 'checking' &&
            runState !== 'blocked' &&
            runState !== 'running';
          const summaryEntries = commandState?.job
            ? [...Object.entries(commandState.job.summary), ...Object.entries(commandState.job.artifacts)]
            : [];

          return (
            <div
              key={`${command.label}-${command.command}`}
              className="rounded-card border border-line/80 bg-paper/70 p-4"
            >
              <div className="mb-3">
                <p
                  className="text-[11px] font-semibold uppercase tracking-[0.18em] text-olive"
                  data-testid={`doc-action-sequence-${index + 1}`}
                >
                  {sequenceMeta.badge}
                </p>
                <p className="mt-1 text-xs text-muted">{sequenceMeta.description}</p>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">{command.label}</p>
                <div className="flex flex-wrap items-center gap-2">
                  {command.executionMode === 'backend-job' && command.actionId && (
                    <Button
                      type="button"
                      size="sm"
                      className="shrink-0"
                      data-testid={getRunTestId(command.testId)}
                      disabled={!canRun}
                      onClick={() => void handleRunCommand(command)}
                    >
                      {runState === 'running' ? 'Running...' : 'Run here'}
                    </Button>
                  )}
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    className="shrink-0"
                    data-testid={getCopyTestId(command.testId)}
                    onClick={() => void handleCopyCommand(command.label, command.command)}
                  >
                    {copiedCommandKey === commandKey
                      ? 'Copied'
                      : failedCommandKey === commandKey
                        ? 'Retry copy'
                        : 'Copy'}
                  </Button>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <Chip variant={runStateVariant(runState)} data-testid={getStatusTestId(command.testId)}>
                  {formatRunState(runState)}
                </Chip>
                {command.executionMode === 'backend-job' && command.actionId && availability && (
                  <span className="text-xs text-muted">
                    {runState === 'blocked'
                      ? availability.message
                      : 'This action can run through the backend job bridge from the docs page.'}
                  </span>
                )}
              </div>

              <pre
                className="mt-2 overflow-x-auto rounded-card border border-line bg-bg px-3 py-3 text-xs leading-6 text-ink whitespace-pre-wrap break-all"
                data-testid={command.testId}
              >
                <code>{command.command}</code>
              </pre>

              {command.executionSummary && (
                <div
                  className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3"
                  data-testid={getExecutionSummaryTestId(command.testId)}
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Execution mode</p>
                  <p className="mt-1 text-xs leading-6 text-ink">{command.executionSummary}</p>
                </div>
              )}

              {(command.prerequisites || command.prerequisitesState) && (
                <div
                  className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3"
                  data-testid={getPrerequisitesTestId(command.testId)}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Prerequisites</p>
                    <Chip
                      variant={prerequisiteStateVariant(command.prerequisitesState)}
                      data-testid={getPrerequisiteStateTestId(command.testId)}
                    >
                      {formatPrerequisiteState(command.prerequisitesState)}
                    </Chip>
                  </div>
                  {command.prerequisites && <p className="mt-1 text-xs leading-6 text-ink">{command.prerequisites}</p>}
                </div>
              )}

              {command.expectedOutcome && (
                <div
                  className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3"
                  data-testid={getOutcomeTestId(command.testId)}
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Expected outcome</p>
                  <p className="mt-1 text-xs leading-6 text-ink">{command.expectedOutcome}</p>
                </div>
              )}

              {command.artifacts && command.artifacts.length > 0 && (
                <div
                  className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3"
                  data-testid={getArtifactsTestId(command.testId)}
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                    Artifacts and outputs
                  </p>
                  <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                    {command.artifacts.map((artifact) => (
                      <li key={artifact}>- {artifact}</li>
                    ))}
                  </ul>
                </div>
              )}

              {commandState?.errorMessage && (
                <div
                  className="mt-3 rounded-card border border-[#f0d4b8] bg-[#fff4e8] px-3 py-3 text-xs text-accent"
                  data-testid={getErrorTestId(command.testId)}
                >
                  {commandState.errorMessage}
                </div>
              )}

              {commandState?.job && (
                <div
                  className="mt-3 rounded-card border border-line bg-bg/70 px-3 py-3"
                  data-testid={getSummaryTestId(command.testId)}
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Result summary</p>
                  <dl className="mt-2 space-y-2 text-xs text-ink">
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Job ID</dt>
                      <dd className="font-mono text-right">{commandState.job.job_id}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Command</dt>
                      <dd className="font-mono text-right break-all">{commandState.job.command_text}</dd>
                    </div>
                    {summaryEntries.map(([key, value]) => (
                      <div key={key} className="flex justify-between gap-3">
                        <dt className="text-muted">{key.replace(/_/g, ' ')}</dt>
                        <dd className="text-right break-all">{formatValue(value)}</dd>
                      </div>
                    ))}
                  </dl>

                  {commandState.job.stdout.trim() && (
                    <div className="mt-3">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">stdout snippet</p>
                      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink">
                        <code>{truncateOutput(commandState.job.stdout)}</code>
                      </pre>
                    </div>
                  )}

                  {commandState.job.stderr.trim() && (
                    <div className="mt-3">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">stderr snippet</p>
                      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-ink">
                        <code>{truncateOutput(commandState.job.stderr)}</code>
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {panel.links.length > 0 && (
        <div className="mt-5 border-t border-line pt-5 space-y-2">
          {panel.links.map((link) => (
            <Link
              key={`${link.href}-${link.label}`}
              href={link.href}
              className="block text-sm text-accent hover:underline"
              data-testid={link.testId}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </Card>
  );
}
