import Link from 'next/link';
import { getAuthorStudioOverview } from '@/lib/data';
import { getLocalBackendAvailability } from '@/lib/local-backend';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';
import { buildStudioHref, getStudioWorkspaceOptions, type StudioWorkspaceSearchParams } from './_shared';

export const dynamic = 'force-dynamic';

interface Props {
  searchParams: Promise<StudioWorkspaceSearchParams>;
}

function formatTimestamp(value: string): string {
  if (!value) {
    return '-';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

export default async function StudioPage({ searchParams }: Props) {
  const params = await searchParams;
  const workspaceOptions = getStudioWorkspaceOptions(params);
  const [overview, backendStatus] = await Promise.all([
    getAuthorStudioOverview(workspaceOptions),
    getLocalBackendAvailability(),
  ]);

  const stats = [
    { id: 'skill-manifests', label: 'Skill manifests', value: overview.counts.skill_manifests, tone: 'olive' },
    { id: 'built', label: 'Built submissions', value: overview.counts.built, tone: 'accent' },
    { id: 'approved', label: 'Inbox approvals', value: overview.counts.approved, tone: 'olive' },
    { id: 'ingested', label: 'Ingested', value: overview.counts.ingested, tone: 'accent' },
  ];

  return (
    <Shell maxWidth="2xl" className="py-8">
      <section className="animate-fade-in">
        <Card variant="hero" className="px-8 py-10" data-testid="studio-overview-hero">
          <div className="grid gap-8 lg:grid-cols-[1.5fr_1fr]">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-olive">Author Studio</p>
              <h1 className="mt-4 text-3xl font-bold text-ink sm:text-4xl">把 skill 从源码推进到 inbox 和 ingest</h1>
              <p className="mt-4 max-w-3xl text-base text-muted">
                这块工作台把 Week 4 和 Week 5 的 submission 能力接到前端：你可以在页面里触发 build、upload、review、ingest，
                但仍然保留 repo-backed 的路径和工件可见性。
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href={buildStudioHref('/studio/new', params)}
                  data-testid="studio-overview-link-new"
                  className="inline-flex items-center rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-paper transition-opacity hover:opacity-90"
                >
                  新建 Submission
                </Link>
                <Link
                  href={buildStudioHref('/studio/submissions', params)}
                  data-testid="studio-overview-link-submissions"
                  className="inline-flex items-center rounded-full border border-line bg-paper px-5 py-2.5 text-sm font-medium text-ink transition-colors hover:bg-bg"
                >
                  管理 Submissions
                </Link>
              </div>
            </div>

            <div className="rounded-card border border-line bg-paper/80 px-5 py-5" data-testid="studio-overview-backend">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Backend status</p>
              <p className="mt-3 text-sm text-ink">{backendStatus.message}</p>
              <div className="mt-4 grid gap-3 text-xs text-muted">
                <div>
                  <p className="font-semibold text-ink">Workspace</p>
                  <p>{overview.workspace.submissions_root}</p>
                  <p>{overview.workspace.inbox_root}</p>
                </div>
                <div>
                  <p className="font-semibold text-ink">Canonical targets</p>
                  <p>{overview.workspace.skills_root}</p>
                  <p>{overview.workspace.docs_root}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4 animate-fade-in-delay-1">
        {stats.map((stat) => (
          <Card key={stat.label} className="px-5 py-5" data-testid={`studio-overview-stat-${stat.id}`}>
            <p className="text-xs uppercase tracking-[0.16em] text-muted">{stat.label}</p>
            <p className={`mt-3 text-3xl font-bold ${stat.tone === 'olive' ? 'text-olive' : 'text-accent'}`}>
              {stat.value}
            </p>
          </Card>
        ))}
      </section>

      <section className="mt-10 grid gap-6 lg:grid-cols-[1.2fr_0.8fr] animate-fade-in-delay-2">
        <Card className="p-6" data-testid="studio-overview-recent-built">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-xl font-semibold text-ink">最近构建</h2>
            <Link
              href={buildStudioHref('/studio/submissions', params)}
              className="text-sm font-medium text-accent hover:underline"
            >
              查看全部
            </Link>
          </div>
          <div className="mt-5 space-y-4">
            {overview.recent_built.length > 0 ? (
              overview.recent_built.map((record) => (
                <div
                  key={record.submission_path}
                  className="rounded-card border border-line bg-bg/60 px-4 py-4"
                  data-testid="studio-overview-built-record"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-ink">{record.skill_name}</p>
                      <p className="text-xs text-muted">{record.submission_id}</p>
                    </div>
                    <Link
                      href={buildStudioHref('/studio/submissions', params, {
                        upload: record.submission_path,
                      })}
                      className="text-sm font-medium text-accent hover:underline"
                    >
                      去上传
                    </Link>
                  </div>
                  <p className="mt-2 text-xs text-muted">{record.submission_path}</p>
                  <p className="mt-2 text-xs text-muted">创建时间：{formatTimestamp(record.created_at)}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">还没有构建好的 submission。先去 `/studio/new` 触发一次 build。</p>
            )}
          </div>
        </Card>

        <Card className="p-6" data-testid="studio-overview-recent-inbox">
          <h2 className="text-xl font-semibold text-ink">最近 inbox</h2>
          <div className="mt-5 space-y-4">
            {overview.recent_inbox.length > 0 ? (
              overview.recent_inbox.map((record) => (
                <div
                  key={record.submission_path}
                  className="rounded-card border border-line bg-paper px-4 py-4"
                  data-testid="studio-overview-inbox-record"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-ink">{record.skill_name}</p>
                      <p className="text-xs text-muted">{record.review?.review_status || 'waiting-review'}</p>
                    </div>
                    <Link
                      href={buildStudioHref('/studio/submissions', params, {
                        review: record.submission_path,
                      })}
                      className="text-sm font-medium text-accent hover:underline"
                    >
                      去处理
                    </Link>
                  </div>
                  <p className="mt-2 text-xs text-muted">{record.submission_path}</p>
                  <p className="mt-2 text-xs text-muted">
                    {record.ingest ? `已 ingest 到 ${record.ingest.target_source_dir}` : '尚未 ingest'}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">inbox 目前为空。可以先从 build 产物触发 upload。</p>
            )}
          </div>
        </Card>
      </section>

      <section className="mt-10 animate-fade-in-delay-3">
        <Card className="p-6" data-testid="studio-overview-recent-jobs">
          <h2 className="text-xl font-semibold text-ink">最近 author jobs</h2>
          <div className="mt-5 space-y-3">
            {overview.recent_jobs.length > 0 ? (
              overview.recent_jobs.map((job) => (
                <div
                  key={job.job_id}
                  className="flex flex-wrap items-center justify-between gap-3 border-b border-line/60 pb-3 last:border-b-0 last:pb-0"
                  data-testid="studio-overview-job-record"
                >
                  <div>
                    <p className="text-sm font-medium text-ink">{job.kind}</p>
                    <p className="text-xs text-muted">{job.command_text}</p>
                  </div>
                  <div className="text-right text-xs text-muted">
                    <p>{job.status}</p>
                    <p>{formatTimestamp(job.created_at)}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">还没有 author submission job 记录。</p>
            )}
          </div>
        </Card>
      </section>
    </Shell>
  );
}
