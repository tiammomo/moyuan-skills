'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { DocActionPanelData } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface DocActionPanelProps {
  panel: DocActionPanelData;
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

function getArtifactsTestId(testId?: string): string | undefined {
  if (!testId) {
    return undefined;
  }
  if (testId.startsWith('doc-action-')) {
    return testId.replace('doc-action-', 'doc-action-artifacts-');
  }
  return `${testId}-artifacts`;
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

export function DocActionPanel({ panel }: DocActionPanelProps) {
  const [copiedCommandKey, setCopiedCommandKey] = useState<string | null>(null);
  const [failedCommandKey, setFailedCommandKey] = useState<string | null>(null);

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

  return (
    <Card className="p-5" data-testid="doc-action-panel">
      <div className="mb-5">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{panel.title}</h3>
        <p className="text-sm text-muted">{panel.description}</p>
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
              <div className="flex items-center justify-between gap-3">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">{command.label}</p>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  className="shrink-0"
                  data-testid={getCopyTestId(command.testId)}
                  onClick={() => handleCopyCommand(command.label, command.command)}
                >
                  {copiedCommandKey === commandKey
                    ? 'Copied'
                    : failedCommandKey === commandKey
                      ? 'Retry copy'
                      : 'Copy'}
                </Button>
              </div>
              <pre
                className="mt-2 overflow-x-auto rounded-card border border-line bg-bg px-3 py-3 text-xs leading-6 text-ink whitespace-pre-wrap break-all"
                data-testid={command.testId}
              >
                <code>{command.command}</code>
              </pre>
              {command.prerequisites && (
                <div
                  className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3"
                  data-testid={getPrerequisitesTestId(command.testId)}
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Prerequisites</p>
                  <p className="mt-1 text-xs leading-6 text-ink">{command.prerequisites}</p>
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
