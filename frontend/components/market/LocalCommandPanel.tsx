'use client';

import { useEffect, useState } from 'react';
import type { MarketCommandAction } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';

interface LocalCommandPanelProps {
  title: string;
  description: string;
  actions: MarketCommandAction[];
  panelTestId?: string;
}

async function copyCommandText(value: string): Promise<void> {
  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return;
    } catch {
      // Fall back to in-page copy when clipboard permissions are unavailable.
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

function getCommandKey(label: string, command: string): string {
  return `${label}:${command}`;
}

function getCopyButtonLabel(copiedKey: string | null, failedKey: string | null, commandKey: string): string {
  if (copiedKey === commandKey) {
    return 'Copied';
  }

  if (failedKey === commandKey) {
    return 'Retry copy';
  }

  return 'Copy command';
}

export function LocalCommandPanel({
  title,
  description,
  actions,
  panelTestId = 'local-command-panel',
}: LocalCommandPanelProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [failedKey, setFailedKey] = useState<string | null>(null);

  useEffect(() => {
    if (!copiedKey && !failedKey) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setCopiedKey(null);
      setFailedKey(null);
    }, 1800);

    return () => window.clearTimeout(timeoutId);
  }, [copiedKey, failedKey]);

  async function handleCopy(action: MarketCommandAction): Promise<void> {
    const commandKey = getCommandKey(action.label, action.command);

    try {
      await copyCommandText(action.command);
      setCopiedKey(commandKey);
      setFailedKey(null);
    } catch {
      setCopiedKey(null);
      setFailedKey(commandKey);
    }
  }

  return (
    <Card className="p-5" data-testid={panelTestId}>
      <div className="mb-5">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <Chip variant="keyword">Local CLI only</Chip>
          <Chip variant="internal">Manual step required</Chip>
        </div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{title}</h3>
        <p className="text-sm text-muted">{description}</p>
      </div>

      <div className="space-y-4">
        {actions.map((action) => {
          const commandKey = getCommandKey(action.label, action.command);

          return (
            <div
              key={`${action.label}-${action.command}`}
              className="rounded-card border border-line/80 bg-paper/70 p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">{action.label}</p>
                  <p className="mt-1 text-sm text-ink">{action.description}</p>
                </div>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  className="shrink-0"
                  data-testid={action.testId ? `${action.testId}-copy` : undefined}
                  onClick={() => handleCopy(action)}
                >
                  {getCopyButtonLabel(copiedKey, failedKey, commandKey)}
                </Button>
              </div>
              <pre
                className="mt-3 overflow-x-auto rounded-card border border-line bg-bg px-3 py-3 text-xs leading-6 text-ink whitespace-pre-wrap break-all"
                data-testid={action.testId}
              >
                <code>{action.command}</code>
              </pre>
              {action.expectedOutcome && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Expected outcome</p>
                  <p className="mt-1 text-xs leading-6 text-ink">{action.expectedOutcome}</p>
                </div>
              )}
              {action.artifacts && action.artifacts.length > 0 && (
                <div className="mt-3 rounded-card border border-dashed border-line bg-bg/70 px-3 py-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">
                    Artifacts and outputs
                  </p>
                  <ul className="mt-2 space-y-1 text-xs leading-6 text-ink">
                    {action.artifacts.map((artifact) => (
                      <li key={artifact}>- {artifact}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
