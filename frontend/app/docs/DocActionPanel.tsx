'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { DocActionPanelData } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface DocActionPanelProps {
  panel: DocActionPanelData;
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
      </div>

      <div className="space-y-4">
        {panel.commands.map((command) => (
          <div key={`${command.label}-${command.command}`}>
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
                {copiedCommandKey === getCommandKey(command.label, command.command)
                  ? 'Copied'
                  : failedCommandKey === getCommandKey(command.label, command.command)
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
          </div>
        ))}
      </div>

      {panel.links.length > 0 && (
        <div className="mt-5 pt-5 border-t border-line space-y-2">
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
