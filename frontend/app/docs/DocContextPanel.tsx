import Link from 'next/link';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import type { Channel } from '@/types/market';

interface ContextFact {
  label: string;
  value: string;
  testId?: string;
  channel?: Channel;
}

interface ContextLink {
  href: string;
  label: string;
  testId?: string;
}

interface DocContextPanelProps {
  title: string;
  description: string;
  facts: ContextFact[];
  links: ContextLink[];
}

export function DocContextPanel({ title, description, facts, links }: DocContextPanelProps) {
  return (
    <Card className="p-5" data-testid="doc-context-panel">
      <div className="mb-5">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{title}</h3>
        <p className="text-sm text-muted">{description}</p>
      </div>

      <div className="space-y-3">
        {facts.map((fact) => (
          <div key={`${fact.label}-${fact.value}`} className="border-b border-line pb-3 last:border-b-0 last:pb-0">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">{fact.label}</p>
            <div className="mt-1">
              {fact.channel ? (
                <Badge channel={fact.channel} data-testid={fact.testId}>
                  {fact.value}
                </Badge>
              ) : (
                <p className="text-sm text-ink break-all" data-testid={fact.testId}>
                  {fact.value}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {links.length > 0 && (
        <div className="mt-5 pt-5 border-t border-line space-y-2">
          {links.map((link) => (
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
