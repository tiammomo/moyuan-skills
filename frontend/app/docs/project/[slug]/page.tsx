import Link from 'next/link';
import { notFound } from 'next/navigation';
import {
  getDocHref,
  getDocNeighbors,
  getDocsCatalog,
  getProjectDoc,
  getProjectDocActionPanel,
  getRelatedDocs,
} from '@/lib/data';
import { extractHeadings, parseMarkdown, renderMarkdown } from '@/lib/markdown';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';
import { DocActionPanel } from '../../DocActionPanel';
import { DocContextPanel } from '../../DocContextPanel';
import { RelatedDocs } from '../../RelatedDocs';

export const revalidate = 300;

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const docsCatalog = await getDocsCatalog();
  return docsCatalog.project_docs.map((doc) => ({ slug: doc.id }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const doc = await getProjectDoc(slug);

  if (!doc) {
    return { title: 'Project doc not found' };
  }

  return {
    title: `${doc.title} - Moyuan Skills Market`,
    description: doc.summary,
  };
}

export default async function ProjectDocPage({ params }: Props) {
  const { slug } = await params;
  const [doc, docsCatalog] = await Promise.all([getProjectDoc(slug), getDocsCatalog()]);

  if (!doc) {
    notFound();
  }

  const { content: markdownContent } = parseMarkdown(doc.markdown);
  const headings = extractHeadings(markdownContent);
  const renderedContent = renderMarkdown(markdownContent);
  const currentDoc =
    docsCatalog.project_docs.find((entry) => entry.id === slug) ?? {
      id: doc.id,
      kind: 'project' as const,
      title: doc.title,
      summary: doc.summary,
      path: doc.path,
    };
  const projectNeighbors = getDocNeighbors(currentDoc, docsCatalog);
  const relatedDocs = await getRelatedDocs(currentDoc);
  const actionPanel = getProjectDocActionPanel(currentDoc);
  const contextFacts = [
    {
      label: 'Reference',
      value: `${projectNeighbors.position} of ${projectNeighbors.total}`,
      testId: 'doc-context-project-position',
    },
    {
      label: 'Doc id',
      value: currentDoc.id,
      testId: 'doc-context-project-id',
    },
    {
      label: 'Source path',
      value: currentDoc.path,
      testId: 'doc-context-project-path',
    },
  ];
  const contextLinks = [
    { href: '/docs', label: 'Back to docs center', testId: 'doc-context-project-center' },
    ...(projectNeighbors.previous
      ? [{ href: getDocHref(projectNeighbors.previous), label: `Previous reference: ${projectNeighbors.previous.title}` }]
      : []),
    ...(projectNeighbors.next
      ? [{ href: getDocHref(projectNeighbors.next), label: `Next reference: ${projectNeighbors.next.title}`, testId: 'doc-context-project-next' }]
      : []),
  ];

  return (
    <Shell maxWidth="2xl" className="py-8">
      <nav className="mb-6 text-sm">
        <ol className="flex items-center gap-2 text-muted">
          <li>
            <Link href="/docs" className="hover:text-accent transition-colors">
              Docs
            </Link>
          </li>
          <li>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </li>
          <li>
            <Link href="/docs" className="hover:text-accent transition-colors">
              Project docs
            </Link>
          </li>
          <li>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </li>
          <li className="text-ink">{doc.title}</li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3">
          <Card className="p-6 sm:p-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-ink mb-6">{doc.title}</h1>
            <div className="markdown-content" dangerouslySetInnerHTML={{ __html: renderedContent }} />
          </Card>
          <RelatedDocs currentKind={currentDoc.kind} docs={relatedDocs} />
        </div>

        <div className="space-y-5 self-start mt-6 lg:mt-0 lg:sticky lg:top-24">
          <DocActionPanel panel={actionPanel} />
          <DocContextPanel
            title="Project context"
            description="Use this panel to orient the current reference inside the broader project docs set and jump to the next operational note."
            facts={contextFacts}
            links={contextLinks}
          />
          {headings.length > 0 && (
            <Card className="hidden lg:block p-5">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Contents</h3>
              <nav className="space-y-2">
                {headings.map((heading) => (
                  <a
                    key={heading.id}
                    href={`#${heading.id}`}
                    className={`block text-sm text-muted hover:text-accent transition-colors ${
                      heading.level === 2 ? '' : 'pl-3'
                    }`}
                  >
                    {heading.title}
                  </a>
                ))}
              </nav>
            </Card>
          )}
        </div>
      </div>
    </Shell>
  );
}
