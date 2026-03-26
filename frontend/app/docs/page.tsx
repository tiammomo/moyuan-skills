import Link from 'next/link';
import { getDocsCatalog } from '@/lib/data';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';

export const revalidate = 300;

export default async function DocsPage() {
  const docsCatalog = await getDocsCatalog();

  return (
    <Shell maxWidth="2xl" className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink mb-2">Documentation Center</h1>
        <p className="text-muted">
          Browse live repo-backed skill docs, teaching materials, and project references.
        </p>
      </div>

      <section className="mb-8 animate-fade-in">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Teaching</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {docsCatalog.teaching_docs.slice(0, 6).map((doc) => (
            <Link
              key={doc.id}
              href={`/docs/teaching/${doc.id}`}
              className="block group"
              data-testid={`teaching-doc-card-${doc.id}`}
            >
              <Card className="h-full p-5 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-olive text-paper flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div>
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
      </section>

      <section className="mb-8 animate-fade-in-delay-1">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Skill docs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {docsCatalog.skill_docs.map((doc) => (
            <Link key={doc.id} href={`/docs/${doc.id}`} className="block group" data-testid={`skill-doc-card-${doc.id}`}>
              <Card className="h-full p-5 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-accent text-paper flex items-center justify-center flex-shrink-0 font-semibold">
                    {doc.title.charAt(0)}
                  </div>
                  <div>
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
      </section>

      <section className="animate-fade-in-delay-2">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">Project references</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {docsCatalog.project_docs.slice(0, 6).map((doc) => (
            <Link
              key={doc.id}
              href={`/docs/project/${doc.id}`}
              className="block group"
              data-testid={`project-doc-card-${doc.id}`}
            >
              <Card className="h-full p-5 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-sand text-ink flex items-center justify-center flex-shrink-0 font-semibold">
                    {doc.title.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-ink group-hover:text-accent transition-colors">
                      {doc.title}
                    </h3>
                    <p className="text-sm text-muted mt-1">{doc.summary}</p>
                    <p className="text-xs text-muted mt-2">{doc.path}</p>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>

        <Card className="p-5 mt-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Link href="/skills" className="text-sm text-accent hover:underline">
              Browse all skills
            </Link>
            <Link href="/channels" className="text-sm text-accent hover:underline">
              View channels
            </Link>
            <Link href="/bundles" className="text-sm text-accent hover:underline">
              Explore bundles
            </Link>
          </div>
        </Card>
      </section>
    </Shell>
  );
}
