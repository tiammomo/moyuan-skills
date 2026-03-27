import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getBundleDetail, getBundles } from '@/lib/data';
import { InstallButton } from '@/components/market/InstallButton';
import { LocalExecutionCard } from '@/components/market/LocalExecutionCard';
import { LocalCommandPanel } from '@/components/market/LocalCommandPanel';
import { SkillCard } from '@/components/market/SkillCard';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { Shell } from '@/components/ui/Shell';

export const revalidate = 300;

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateStaticParams() {
  const bundles = await getBundles();
  return bundles.map((bundle) => ({ id: bundle.id }));
}

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const detail = await getBundleDetail(id);

  if (!detail) {
    return { title: 'Bundle not found' };
  }

  return {
    title: `${detail.bundle.title} - Moyuan Skills Market`,
    description: detail.bundle.summary,
  };
}

export default async function BundleDetailPage({ params }: Props) {
  const { id } = await params;
  const detail = await getBundleDetail(id);

  if (!detail) {
    notFound();
  }

  const { bundle, skills, install_specs: installSpecs } = detail;
  const installedTargetRoot = 'dist/installed-market';
  const bundleActions = [
    {
      label: 'Install bundle locally',
      command: `python scripts/skills_market.py install-bundle ${bundle.id} --market-dir dist/market --target-root ${installedTargetRoot}`,
      description: 'Install the current bundle into a local target root from the built market directory.',
      expectedOutcome: 'The bundle installs under the chosen target root and updates the local lock state.',
      artifacts: [`${installedTargetRoot}/skills.lock.json`, `${installedTargetRoot}/bundles/`],
      testId: 'bundle-action-install',
    },
    {
      label: 'Update bundle locally',
      command: `python scripts/skills_market.py update-bundle ${bundle.id} --market-dir dist/market --target-root ${installedTargetRoot}`,
      description: 'Refresh the installed bundle membership from the local market artifacts.',
      expectedOutcome: 'Changed bundle members are reconciled without retyping per-skill commands.',
      artifacts: [`${installedTargetRoot}/skills.lock.json`, `${installedTargetRoot}/bundles/`],
      testId: 'bundle-action-update',
    },
    {
      label: 'Remove bundle locally',
      command: `python scripts/skills_market.py remove-bundle ${bundle.id} --target-root ${installedTargetRoot}`,
      description: 'Remove bundle-owned skills while keeping direct installs untouched.',
      expectedOutcome: 'Bundle-only ownership is removed and the local bundle report is updated.',
      artifacts: [`${installedTargetRoot}/skills.lock.json`, `${installedTargetRoot}/bundles/`],
      testId: 'bundle-action-remove',
    },
  ];

  return (
    <Shell maxWidth="2xl" className="py-8">
      <nav className="mb-6 text-sm">
        <ol className="flex items-center gap-2 text-muted">
          <li>
            <Link href="/bundles" className="hover:text-accent transition-colors">
              Bundles
            </Link>
          </li>
          <li>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </li>
          <li className="text-ink">{bundle.title}</li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section className="animate-fade-in">
            <Card className="p-6 sm:p-8">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-olive to-accent flex items-center justify-center text-paper font-bold text-xl mb-4">
                {bundle.skill_count}
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-ink mb-3">{bundle.title}</h1>
              <p className="text-muted mb-4">{bundle.description}</p>
              <div className="flex flex-wrap gap-2">
                {bundle.use_cases.map((useCase) => (
                  <Chip key={useCase} variant="keyword">
                    {useCase}
                  </Chip>
                ))}
              </div>
            </Card>
          </section>

          <section className="animate-fade-in-delay-1">
            <h2 className="text-xl font-semibold text-ink mb-4">Included skills</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {skills.map((skill) => (
                <SkillCard key={skill.id} skill={skill} />
              ))}
            </div>
          </section>
        </div>

        <div className="space-y-6">
          <section className="animate-fade-in">
            <LocalCommandPanel
              panelTestId="bundle-local-command-panel"
              title="Bundle local commands"
              description="These actions still run through the local CLI. Keep using them when you want explicit copy-first control or when you need bundle update/remove flows that are not wired to the backend yet."
              actions={bundleActions}
            />
          </section>

          <section className="animate-fade-in-delay-1">
            <LocalExecutionCard
              panelTestId="bundle-backend-execution"
              title="Run bundle install through the backend"
              description="This uses the FastAPI mutation layer to execute the current bundle install and poll the background job until it finishes."
              requestPath="/api/local/bundles/install"
              requestBody={{
                bundle_id: bundle.id,
                target_root: `dist/frontend-local-execution/bundles/${bundle.id}`,
                market_dir: 'dist/market',
              }}
              fallbackNote="Bundle update and remove remain copy-first CLI actions for now; only bundle install is wired to backend execution in this pass."
            />
          </section>

          <section className="animate-fade-in-delay-2">
            <LocalExecutionCard
              panelTestId="bundle-registry-execution"
              title="Run bundle install from a remote registry"
              description="This path downloads the bundle members from a hosted registry URL through the backend, stages the remote artifacts into the cache root, and then applies the normal bundle installer locally."
              requestPath="/api/registry/bundles/install"
              requestBody={{
                bundle_id: bundle.id,
                target_root: `dist/frontend-remote-execution/bundles/${bundle.id}`,
                cache_root: 'dist/frontend-remote-execution/cache',
              }}
              modeLabel="Registry-backed execution"
              badges={['Remote download via backend', 'Copy-first bundle commands still stay visible']}
              fields={[
                {
                  name: 'registry_url',
                  label: 'Registry URL',
                  description:
                    'Point this at a hosted registry base URL or directly at registry.json before starting the remote bundle job.',
                  placeholder: 'http://127.0.0.1:38765',
                  required: true,
                },
              ]}
              fallbackNote="This first frontend remote pass only covers bundle install. Update, remove, trust approval, and deeper recovery UI still live in later roadmap phases."
            />
          </section>

          <section className="animate-fade-in-delay-2">
            <Card className="p-5">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">
                Per-skill local install commands
              </h3>
              <p className="text-sm text-muted mb-4">
                Each command below comes from the generated market install specs for this bundle.
              </p>
              <div className="space-y-3">
                {installSpecs.map((spec) => (
                  <div key={spec.skill_name} className="p-3 bg-bg rounded-lg">
                    <div className="text-sm font-medium text-ink mb-2">{spec.skill_name}</div>
                    <InstallButton installSpec={spec} />
                  </div>
                ))}
              </div>
            </Card>
          </section>

          <section className="animate-fade-in-delay-3">
            <Card className="p-5">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">
                Bundle info
              </h3>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm text-muted">Skills</dt>
                  <dd className="text-sm text-ink">{bundle.skill_count}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted">Use cases</dt>
                  <dd className="text-sm text-ink">{bundle.use_cases.length}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted">Channels</dt>
                  <dd className="text-sm text-ink">{bundle.channels.join(', ')}</dd>
                </div>
              </dl>
            </Card>
          </section>

          <section className="animate-fade-in-delay-3">
            <Link href="/bundles" className="flex items-center gap-2 text-sm text-accent hover:underline">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to bundles
            </Link>
          </section>
        </div>
      </div>
    </Shell>
  );
}
