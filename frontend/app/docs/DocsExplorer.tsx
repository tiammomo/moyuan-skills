'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import type { DocsCatalogEntry, DocsCatalog } from '@/types/market';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

type DocKindFilter = 'all' | DocsCatalogEntry['kind'];

interface DocsExplorerProps {
  docsCatalog: DocsCatalog;
}

function docHref(doc: DocsCatalogEntry): string {
  if (doc.kind === 'skill') {
    return `/docs/${doc.id}`;
  }
  if (doc.kind === 'teaching') {
    return `/docs/teaching/${doc.id}`;
  }
  return `/docs/project/${doc.id}`;
}

function docKindLabel(kind: DocsCatalogEntry['kind']): string {
  if (kind === 'skill') {
    return 'Skill doc';
  }
  if (kind === 'teaching') {
    return 'Teaching';
  }
  return 'Project';
}

function docKindClasses(kind: DocsCatalogEntry['kind']): string {
  if (kind === 'skill') {
    return 'bg-accent text-paper';
  }
  if (kind === 'teaching') {
    return 'bg-olive text-paper';
  }
  return 'bg-sand text-ink';
}

function normalizeSearchText(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

export function DocsExplorer({ docsCatalog }: DocsExplorerProps) {
  const [query, setQuery] = useState('');
  const [kindFilter, setKindFilter] = useState<DocKindFilter>('all');

  const filteredDocs = useMemo(() => {
    const tokens = normalizeSearchText(query)
      .split(/\s+/)
      .filter(Boolean);
    return docsCatalog.all_docs.filter((doc) => {
      if (kindFilter !== 'all' && doc.kind !== kindFilter) {
        return false;
      }
      if (tokens.length === 0) {
        return true;
      }
      const haystack = normalizeSearchText(`${doc.title} ${doc.summary} ${doc.path} ${doc.kind}`);
      return tokens.every((token) => haystack.includes(token));
    });
  }, [docsCatalog.all_docs, kindFilter, query]);

  const counts = {
    all: docsCatalog.all_docs.length,
    skill: docsCatalog.skill_docs.length,
    teaching: docsCatalog.teaching_docs.length,
    project: docsCatalog.project_docs.length,
  };

  return (
    <section className="mb-8 animate-fade-in">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">Docs explorer</h2>
          <p className="text-sm text-muted">
            Search and filter all live repo-backed docs across skill, teaching, and project references.
          </p>
        </div>
        <div className="w-full lg:max-w-md">
          <Input
            id="docs-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search docs, teaching, or project references..."
            data-testid="docs-search-input"
          />
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <Button
          variant={kindFilter === 'all' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setKindFilter('all')}
          data-testid="docs-filter-all"
        >
          All ({counts.all})
        </Button>
        <Button
          variant={kindFilter === 'skill' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setKindFilter('skill')}
          data-testid="docs-filter-skill"
        >
          Skill ({counts.skill})
        </Button>
        <Button
          variant={kindFilter === 'teaching' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setKindFilter('teaching')}
          data-testid="docs-filter-teaching"
        >
          Teaching ({counts.teaching})
        </Button>
        <Button
          variant={kindFilter === 'project' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setKindFilter('project')}
          data-testid="docs-filter-project"
        >
          Project ({counts.project})
        </Button>
      </div>

      <Card className="p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <p className="text-sm text-muted" data-testid="docs-results-count">
            Showing {filteredDocs.length} of {docsCatalog.all_docs.length} docs
          </p>
          {(query || kindFilter !== 'all') && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setQuery('');
                setKindFilter('all');
              }}
              data-testid="docs-clear-filters"
            >
              Clear filters
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredDocs.map((doc) => (
            <Link
              key={`${doc.kind}-${doc.id}`}
              href={docHref(doc)}
              className="block group"
              data-testid={`docs-result-${doc.kind}-${doc.id}`}
            >
              <Card className="h-full p-5 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 text-xs font-semibold uppercase ${docKindClasses(doc.kind)}`}
                  >
                    {doc.kind.slice(0, 1)}
                  </div>
                  <div className="min-w-0">
                    <div className="mb-2 flex flex-wrap items-center gap-2">
                      <span className="text-xs font-medium uppercase tracking-wide text-muted">
                        {docKindLabel(doc.kind)}
                      </span>
                      <span className="text-xs text-muted">{doc.path}</span>
                    </div>
                    <h3 className="font-semibold text-ink group-hover:text-accent transition-colors">
                      {doc.title}
                    </h3>
                    <p className="text-sm text-muted mt-1">{doc.summary}</p>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>

        {filteredDocs.length === 0 && (
          <div className="rounded-card border border-dashed border-line bg-bg px-5 py-8 text-center">
            <p className="text-sm font-medium text-ink">No docs matched the current filters.</p>
            <p className="text-sm text-muted mt-2">
              Try a broader keyword or switch back to “All” to explore the full library.
            </p>
          </div>
        )}
      </Card>
    </section>
  );
}
