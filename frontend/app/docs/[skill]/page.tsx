import Link from 'next/link';
import { notFound } from 'next/navigation';
import {
  getDocHref,
  getDocNeighbors,
  getDocsCatalog,
  getRelatedDocs,
  getSkillDetail,
  getSkillDocActionPanel,
} from '@/lib/data';
import { extractHeadings, parseMarkdown, renderMarkdown } from '@/lib/markdown';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';
import { DocActionPanel } from '../DocActionPanel';
import { DocContextPanel } from '../DocContextPanel';
import { RelatedDocs } from '../RelatedDocs';

export const revalidate = 300;

interface Props {
  params: Promise<{ skill: string }>;
}

export async function generateStaticParams() {
  const docsCatalog = await getDocsCatalog();
  return docsCatalog.skill_docs.map((doc) => ({ skill: doc.id }));
}

export async function generateMetadata({ params }: Props) {
  const { skill } = await params;
  const detail = await getSkillDetail(skill);
  const title = detail?.manifest.title || skill;

  return {
    title: `${title} - Moyuan Skills Market`,
    description: `${title} documentation`,
  };
}

export default async function SkillDocPage({ params }: Props) {
  const { skill } = await params;
  const [detail, docsCatalog] = await Promise.all([getSkillDetail(skill), getDocsCatalog()]);
  const docContent = detail?.doc_markdown;

  if (!docContent) {
    notFound();
  }

  const { content: markdownContent } = parseMarkdown(docContent);
  const headings = extractHeadings(markdownContent);
  const renderedContent = renderMarkdown(markdownContent);
  const title = detail?.manifest.title || skill;
  const currentDoc =
    docsCatalog.skill_docs.find((doc) => doc.id === skill) ?? {
      id: skill,
      kind: 'skill' as const,
      title,
      summary: `${title} documentation`,
      path: detail?.manifest.artifacts.docs ?? `docs/skills/${skill}.md`,
    };
  const skillNeighbors = getDocNeighbors(currentDoc, docsCatalog);
  const relatedDocs = await getRelatedDocs(currentDoc, {
    preferredIds: detail?.related_skills.map((relatedSkill) => relatedSkill.name) ?? [],
  });
  const actionPanel = getSkillDocActionPanel(skill, detail, {
    channelHref: `/channels/${detail?.manifest.channel ?? 'stable'}`,
  });
  const contextFacts = [
    {
      label: 'Channel',
      value: detail?.manifest.channel ?? 'unknown',
      channel: detail?.manifest.channel,
      testId: 'doc-context-skill-channel',
    },
    {
      label: 'Version',
      value: detail?.manifest.version ?? 'unknown',
      testId: 'doc-context-skill-version',
    },
    {
      label: 'Entrypoint',
      value: detail?.install_spec?.entrypoint ?? detail?.manifest.artifacts.entrypoint ?? 'n/a',
      testId: 'doc-context-skill-entrypoint',
    },
    {
      label: 'Package',
      value: detail?.install_spec?.package_path ?? 'n/a',
      testId: 'doc-context-skill-package',
    },
  ];
  const contextLinks = [
    { href: `/skills/${skill}`, label: 'Open market skill page', testId: 'doc-context-skill-link' },
    { href: `/channels/${detail?.manifest.channel ?? 'stable'}`, label: 'View release channel', testId: 'doc-context-channel-link' },
    ...(skillNeighbors.previous
      ? [{ href: getDocHref(skillNeighbors.previous), label: `Previous skill doc: ${skillNeighbors.previous.title}` }]
      : []),
    ...(skillNeighbors.next
      ? [{ href: getDocHref(skillNeighbors.next), label: `Next skill doc: ${skillNeighbors.next.title}` }]
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
          <li className="text-ink">{title}</li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3">
          <Card className="p-6 sm:p-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-ink mb-6">{title}</h1>
            <div className="markdown-content" dangerouslySetInnerHTML={{ __html: renderedContent }} />
          </Card>
          <RelatedDocs currentKind={currentDoc.kind} docs={relatedDocs} />
        </div>

        <div className="space-y-5 self-start mt-6 lg:mt-0 lg:sticky lg:top-24">
          <DocActionPanel panel={actionPanel} />
          <DocContextPanel
            title="Skill context"
            description="Use the market metadata here to understand where this skill lives, how it installs, and which skill docs to read next."
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
