import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getAllSkills, getSkillDetail } from '@/lib/data';
import { extractHeadings, parseMarkdown, renderMarkdown } from '@/lib/markdown';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { Shell } from '@/components/ui/Shell';
import { InstallButton } from '@/components/market/InstallButton';
import { InstalledStatePanel } from '@/components/market/InstalledStatePanel';
import { LocalExecutionCard } from '@/components/market/LocalExecutionCard';
import { PermissionsList } from '@/components/market/PermissionsList';
import { SkillCard } from '@/components/market/SkillCard';

export const revalidate = 300;

interface Props {
  params: Promise<{ name: string }>;
}

export async function generateStaticParams() {
  const skills = await getAllSkills();
  return skills.map((skill) => ({ name: skill.name }));
}

export async function generateMetadata({ params }: Props) {
  const { name } = await params;
  const detail = await getSkillDetail(name);
  const manifest = detail?.manifest;

  if (!manifest) {
    return { title: 'Skill not found' };
  }

  return {
    title: `${manifest.title} - Moyuan Skills Market`,
    description: manifest.summary,
  };
}

const reviewStatusMap: Record<string, string> = {
  reviewed: 'Reviewed',
  draft: 'Draft',
  deprecated: 'Deprecated',
};

const platformMap: Record<string, string> = {
  windows: 'Windows',
  macos: 'macOS',
  linux: 'Linux',
};

export default async function SkillDetailPage({ params }: Props) {
  const { name } = await params;
  const detail = await getSkillDetail(name);

  if (!detail?.manifest) {
    notFound();
  }

  const {
    manifest,
    install_spec: installSpec,
    doc_markdown: docContent,
    related_skills: relatedSkills,
  } = detail;
  const localTargetRoot = `dist/frontend-local-execution/skills/${manifest.name}`;

  const { content: markdownContent } = docContent ? parseMarkdown(docContent) : { content: '' };
  const headings = extractHeadings(markdownContent);
  const renderedContent = renderMarkdown(markdownContent);

  return (
    <Shell maxWidth="2xl" className="py-8">
      <nav className="mb-6 text-sm">
        <ol className="flex items-center gap-2 text-muted">
          <li>
            <Link href="/skills" className="hover:text-accent transition-colors">
              Skills
            </Link>
          </li>
          <li>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </li>
          <li className="text-ink">{manifest.title}</li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section className="animate-fade-in">
            <Card className="p-6 sm:p-8">
              <div className="flex items-start justify-between gap-4 mb-4">
                <Badge channel={manifest.channel} />
                <span className="text-sm text-muted">v{manifest.version}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-ink mb-3">{manifest.title}</h1>
              <p className="text-muted mb-6">{manifest.summary}</p>

              <div className="flex flex-wrap gap-2 mb-6">
                {manifest.categories.map((category) => (
                  <Link key={category} href={`/skills?category=${encodeURIComponent(category)}`}>
                    <Chip variant="category" className="hover:bg-olive hover:text-paper transition-colors cursor-pointer">
                      {category}
                    </Chip>
                  </Link>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                {manifest.tags.map((tag) => (
                  <Chip key={tag} variant="tag">
                    {tag}
                  </Chip>
                ))}
              </div>
            </Card>
          </section>

          <section className="animate-fade-in-delay-1">
            <Card className="p-6 sm:p-8">
              <h2 className="text-lg font-semibold text-ink mb-4">About this skill</h2>
              <p className="text-muted leading-relaxed">{manifest.description}</p>
            </Card>
          </section>

          {renderedContent && (
            <section className="animate-fade-in-delay-2">
              <Card className="p-6 sm:p-8">
                <h2 className="text-lg font-semibold text-ink mb-6">Documentation</h2>
                <div className="markdown-content" dangerouslySetInnerHTML={{ __html: renderedContent }} />
              </Card>
            </section>
          )}

          {installSpec && (
            <section className="animate-fade-in-delay-3">
              <Card className="p-6 sm:p-8">
                <h2 className="text-lg font-semibold text-ink mb-4">Install options</h2>
                <div className="space-y-5">
                  <InstallButton installSpec={installSpec} />
                  <LocalExecutionCard
                    panelTestId="skill-backend-execution"
                    title="Run this install through the backend"
                    description="This executes the existing local installer through the FastAPI mutation layer and keeps the copy-command fallback visible above."
                    requestPath="/api/local/skills/install"
                    requestBody={{
                      name: manifest.name,
                      target_root: localTargetRoot,
                    }}
                    fallbackNote="This path only runs the local install spec already packaged in the repo. Use the registry-backed card below when you want the backend to fetch the skill remotely first."
                  />
                  <LocalExecutionCard
                    panelTestId="skill-registry-execution"
                    title="Run this install from a remote registry"
                    description="This path asks the backend to fetch the packaged skill from a hosted registry URL, stage the install spec and package locally, then run the normal installer."
                    requestPath="/api/registry/skills/install"
                    requestBody={{
                      skill: manifest.id,
                      channel: manifest.channel,
                      target_root: `dist/frontend-remote-execution/skills/${manifest.name}`,
                      cache_root: 'dist/frontend-remote-execution/cache',
                    }}
                    modeLabel="Registry-backed execution"
                    badges={['Remote download via backend', 'Local install spec still available above']}
                    fields={[
                      {
                        name: 'registry_url',
                        label: 'Registry URL',
                        description:
                          'Point this at a hosted registry base URL or directly at registry.json before starting the remote install job.',
                        placeholder: 'http://127.0.0.1:38765',
                        required: true,
                      },
                    ]}
                    fallbackNote="This is the first frontend pass for remote install. Trust, approval, and recovery hardening still live in later roadmap phases."
                  />
                </div>
              </Card>
            </section>
          )}

          <section className="animate-fade-in-delay-3">
            <InstalledStatePanel
              panelTestId="skill-installed-state"
              title="Local lifecycle state"
              description="This panel reads the backend installed-state snapshot for the local frontend target root and lets you run update or remove without leaving the detail page."
              targetRoot={localTargetRoot}
              skillId={manifest.id}
              skillName={manifest.name}
              actions={[
                {
                  panelTestId: 'skill-update-execution',
                  title: 'Update this installed skill through the backend',
                  description:
                    'This resolves the latest install spec from the current channel index and reruns the normal skill installer against the existing frontend target root.',
                  requestPath: '/api/local/skills/update',
                  requestBody: {
                    skill: manifest.id,
                    target_root: localTargetRoot,
                    index: `dist/market/channels/${manifest.channel}.json`,
                  },
                  fallbackNote:
                    'This is the first installed-state lifecycle pass. Doctor, repair, and baseline governance still live in later frontend iterations.',
                  modeLabel: 'Installed-state execution',
                  badges: ['Updates the current local target root', 'Copy-first commands stay available above'],
                  runButtonLabel: 'Update via backend',
                  dryRunButtonLabel: 'Dry run update',
                  runningLabel: 'Running update...',
                  dryRunRunningLabel: 'Running update dry run...',
                },
                {
                  panelTestId: 'skill-remove-execution',
                  title: 'Remove this installed skill through the backend',
                  description:
                    'This removes the installed skill from the current frontend target root and updates the lock state without asking you to retype the CLI command.',
                  requestPath: '/api/local/skills/remove',
                  requestBody: {
                    skill: manifest.id,
                    target_root: localTargetRoot,
                  },
                  fallbackNote:
                    'Removal is scoped to the current frontend local target root. Other installs or remote execution targets are not touched by this action.',
                  modeLabel: 'Installed-state execution',
                  badges: ['Local remove flow', 'Scoped to this target root'],
                  runButtonLabel: 'Remove via backend',
                  dryRunButtonLabel: 'Preview remove',
                  runningLabel: 'Running remove...',
                  dryRunRunningLabel: 'Running remove dry run...',
                },
              ]}
            />
          </section>
        </div>

        <div className="space-y-6">
          <section className="animate-fade-in">
            <Card className="p-5">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Quick facts</h3>
              <dl className="space-y-3">
                <div className="flex justify-between gap-4">
                  <dt className="text-sm text-muted">Skill ID</dt>
                  <dd className="text-sm text-ink font-mono text-right">{manifest.id}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-sm text-muted">Publisher</dt>
                  <dd className="text-sm text-ink text-right">{manifest.publisher}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-sm text-muted">Version</dt>
                  <dd className="text-sm text-ink text-right">{manifest.version}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-sm text-muted">Channel</dt>
                  <dd className="text-sm">
                    <Badge channel={manifest.channel} />
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-sm text-muted">Review status</dt>
                  <dd className="text-sm text-ink text-right">
                    {reviewStatusMap[manifest.review_status] || manifest.review_status}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-sm text-muted">Platforms</dt>
                  <dd className="text-sm text-ink text-right">
                    {manifest.compatibility?.platforms?.map((item) => platformMap[item] || item).join(', ') || 'All'}
                  </dd>
                </div>
              </dl>
            </Card>
          </section>

          {manifest.permissions && (
            <section className="animate-fade-in-delay-1">
              <Card className="p-5">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Permissions</h3>
                <PermissionsList permissions={manifest.permissions} />
              </Card>
            </section>
          )}

          {manifest.distribution?.capabilities?.length > 0 && (
            <section className="animate-fade-in-delay-1">
              <Card className="p-5">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Capabilities</h3>
                <div className="flex flex-wrap gap-1.5">
                  {manifest.distribution.capabilities.map((capability) => (
                    <Chip key={capability} variant="keyword">
                      {capability}
                    </Chip>
                  ))}
                </div>
              </Card>
            </section>
          )}

          {headings.length > 0 && (
            <section className="animate-fade-in-delay-2">
              <Card className="p-5">
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
            </section>
          )}

          {relatedSkills.length > 0 && (
            <section className="animate-fade-in-delay-3">
              <Card className="p-5">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Related skills</h3>
                <div className="space-y-3">
                  {relatedSkills.map((skill) => (
                    <SkillCard key={skill.id} skill={skill} />
                  ))}
                </div>
              </Card>
            </section>
          )}
        </div>
      </div>
    </Shell>
  );
}
