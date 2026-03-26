import Link from 'next/link';
import type { DocActionPanelData } from '@/types/market';
import { Card } from '@/components/ui/Card';

interface DocActionPanelProps {
  panel: DocActionPanelData;
}

export function DocActionPanel({ panel }: DocActionPanelProps) {
  return (
    <Card className="p-5" data-testid="doc-action-panel">
      <div className="mb-5">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{panel.title}</h3>
        <p className="text-sm text-muted">{panel.description}</p>
      </div>

      <div className="space-y-4">
        {panel.commands.map((command) => (
          <div key={`${command.label}-${command.command}`}>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">{command.label}</p>
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
