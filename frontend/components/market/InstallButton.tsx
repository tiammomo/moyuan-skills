'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Chip } from '@/components/ui/Chip';
import type { InstallSpec } from '@/types/market';

interface InstallButtonProps {
  installSpec: InstallSpec;
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

export function InstallButton({ installSpec }: InstallButtonProps) {
  const [copied, setCopied] = useState(false);
  const [copyFailed, setCopyFailed] = useState(false);

  const installCommand = `python scripts/skills_market.py install dist/market/install/${installSpec.skill_name}-${installSpec.version}.json`;

  useEffect(() => {
    if (!copied && !copyFailed) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setCopied(false);
      setCopyFailed(false);
    }, 1800);

    return () => window.clearTimeout(timeoutId);
  }, [copied, copyFailed]);

  const handleCopy = async () => {
    try {
      await copyCommandText(installCommand);
      setCopied(true);
      setCopyFailed(false);
    } catch (err) {
      console.error('Failed to copy install command:', err);
      setCopied(false);
      setCopyFailed(true);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <Chip variant="keyword" data-testid="install-command-mode-note">
          Copy install command
        </Chip>
        <Chip variant="internal">CLI fallback</Chip>
      </div>
      <p data-testid="install-command-honesty-note" className="text-sm text-muted">
        This card only copies the local install command. Use the backend execution panel if you want the frontend to run
        the install for you.
      </p>
      <div className="flex items-center gap-2">
        <code
          data-testid="install-command"
          className="flex-1 bg-[#1d261f] text-[#f7f4ea] px-4 py-3 rounded-xl text-sm font-mono overflow-x-auto"
        >
          {installCommand}
        </code>
        <Button data-testid="install-command-copy" onClick={handleCopy} variant="secondary" size="sm">
          {copied ? 'Copied' : copyFailed ? 'Retry copy' : 'Copy install command'}
        </Button>
      </div>
      <p data-testid="install-package-meta" className="text-xs text-muted">
        Package: {installSpec.package_path.split('/').pop()} ({installSpec.checksum_sha256.slice(0, 12)}...)
      </p>
    </div>
  );
}
