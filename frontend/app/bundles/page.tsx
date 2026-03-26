import Link from 'next/link';
import { getBundles } from '@/lib/data';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { Shell } from '@/components/ui/Shell';

export const revalidate = 300;

export default async function BundlesPage() {
  const bundles = await getBundles();

  return (
    <Shell maxWidth="2xl" className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink mb-2">Starter Bundles</h1>
        <p className="text-muted">
          Curated groups of skills that map to real workflows, onboarding paths, and operating tasks.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bundles.map((bundle) => (
          <Card
            key={bundle.id}
            data-testid={`bundle-card-${bundle.id}`}
            className="p-6 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-olive to-accent flex items-center justify-center text-paper font-bold text-lg mb-4">
              {bundle.skill_count}
            </div>
            <h2 className="text-lg font-semibold text-ink mb-2">{bundle.title}</h2>
            <p className="text-sm text-muted mb-4">{bundle.summary}</p>
            <div className="flex flex-wrap gap-1.5 mb-4">
              {bundle.skill_summaries.map((skill) => (
                <Link key={skill.id} href={`/skills/${skill.name}`}>
                  <Chip variant="category" className="hover:bg-olive hover:text-paper transition-colors cursor-pointer">
                    {skill.title}
                  </Chip>
                </Link>
              ))}
            </div>
            <Link
              href={`/bundles/${bundle.id}`}
              data-testid={`bundle-link-${bundle.id}`}
              className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
            >
              View bundle
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </Card>
        ))}
      </div>

      <section className="mt-12">
        <Card className="p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent-soft flex items-center justify-center">
            <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-ink mb-2">Need a new bundle?</h3>
          <p className="text-sm text-muted max-w-md mx-auto mb-4">
            Bundles work best when they mirror a real team task. Start from the docs if you want to define a new one.
          </p>
          <Link
            href="/docs"
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent text-paper rounded-full text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Read the docs
          </Link>
        </Card>
      </section>
    </Shell>
  );
}
