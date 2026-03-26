'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import type { InstallSpec } from '@/types/market';

interface InstallButtonProps {
  installSpec: InstallSpec;
}

export function InstallButton({ installSpec }: InstallButtonProps) {
  const [copied, setCopied] = useState(false);

  const installCommand = `python scripts/skills_market.py install dist/market/install/${installSpec.skill_name}-${installSpec.version}.json`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(installCommand);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <code
          data-testid="install-command"
          className="flex-1 bg-[#1d261f] text-[#f7f4ea] px-4 py-3 rounded-xl text-sm font-mono overflow-x-auto"
        >
          {installCommand}
        </code>
        <Button data-testid="install-command-copy" onClick={handleCopy} variant="secondary" size="sm">
          {copied ? (
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4 text-olive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              已复制
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              复制
            </span>
          )}
        </Button>
      </div>
      <p data-testid="install-package-meta" className="text-xs text-muted">
        包: {installSpec.package_path.split('/').pop()} ({installSpec.checksum_sha256.slice(0, 12)}...)
      </p>
    </div>
  );
}
