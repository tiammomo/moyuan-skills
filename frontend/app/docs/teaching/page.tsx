import Link from 'next/link';
import { getDocsCatalog } from '@/lib/data';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';

export const revalidate = 300;

export default async function TeachingPage() {
  const docsCatalog = await getDocsCatalog();
  const teachingDocs = docsCatalog.teaching_docs;

  return (
    <Shell maxWidth="2xl" className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink mb-2">Teaching Library</h1>
        <p className="text-muted">
          Browse the repo-backed teaching path for onboarding, authoring, maintenance, and market evolution.
        </p>
      </div>

      <div className="space-y-4">
        {teachingDocs.map((doc, index) => (
          <section key={doc.id} className="animate-fade-in" style={{ animationDelay: `${index * 0.05}s` }}>
            <Link href={`/docs/teaching/${doc.id}`} className="block group" data-testid={`teaching-doc-link-${doc.id}`}>
              <Card className="p-6 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <h2 className="text-xl font-semibold text-ink group-hover:text-accent transition-colors">
                      {doc.title}
                    </h2>
                    <p className="text-sm text-muted mt-2">{doc.summary}</p>
                  </div>
                  <span className="text-xs font-medium px-2 py-1 bg-accent-soft text-accent rounded-full whitespace-nowrap">
                    {doc.id}
                  </span>
                </div>
                <p className="text-xs text-muted">{doc.path}</p>
              </Card>
            </Link>
          </section>
        ))}
      </div>
    </Shell>
  );
}
