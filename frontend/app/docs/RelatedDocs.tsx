import Link from 'next/link';
import type { DocsCatalogEntry } from '@/types/market';
import { getDocHref } from '@/lib/data';
import { Card } from '@/components/ui/Card';

interface RelatedDocsProps {
  currentKind: DocsCatalogEntry['kind'];
  docs: DocsCatalogEntry[];
}

function kindLabel(kind: DocsCatalogEntry['kind']): string {
  if (kind === 'skill') {
    return 'Skill doc';
  }
  if (kind === 'teaching') {
    return 'Teaching';
  }
  return 'Project';
}

function kindBadgeClasses(kind: DocsCatalogEntry['kind']): string {
  if (kind === 'skill') {
    return 'bg-accent text-paper';
  }
  if (kind === 'teaching') {
    return 'bg-olive text-paper';
  }
  return 'bg-sand text-ink';
}

function sectionSummary(currentKind: DocsCatalogEntry['kind']): string {
  if (currentKind === 'skill') {
    return 'Jump to adjacent business or teaching references that build on the current skill.';
  }
  if (currentKind === 'teaching') {
    return 'Keep moving through the learning path with nearby teaching, skill, and project references.';
  }
  return 'Continue from this project reference into the next docs, teaching notes, or skill walkthroughs.';
}

export function RelatedDocs({ currentKind, docs }: RelatedDocsProps) {
  if (docs.length === 0) {
    return null;
  }

  return (
    <Card className="p-6 sm:p-8 mt-6">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-ink">Continue exploring</h2>
        <p className="text-sm text-muted mt-2">{sectionSummary(currentKind)}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {docs.map((doc) => (
          <Link
            key={`${doc.kind}-${doc.id}`}
            href={getDocHref(doc)}
            className="block group"
            data-testid={`related-doc-link-${doc.kind}-${doc.id}`}
          >
            <div className="rounded-card border border-line bg-bg px-4 py-4 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-card">
              <div className="flex items-center gap-2 mb-2">
                <span
                  className={`inline-flex items-center rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-wide ${kindBadgeClasses(doc.kind)}`}
                >
                  {kindLabel(doc.kind)}
                </span>
                <span className="text-xs text-muted">{doc.path}</span>
              </div>
              <h3 className="font-semibold text-ink group-hover:text-accent transition-colors">{doc.title}</h3>
              <p className="text-sm text-muted mt-1">{doc.summary}</p>
            </div>
          </Link>
        ))}
      </div>
    </Card>
  );
}
