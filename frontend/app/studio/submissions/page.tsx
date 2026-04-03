import Link from 'next/link';
import { getAuthorSubmissions } from '@/lib/data';
import { getLocalBackendAvailability } from '@/lib/local-backend';
import { StudioJobPanel } from '@/components/studio/StudioJobPanel';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';
import { buildStudioHref, getStudioWorkspaceOptions, type StudioWorkspaceSearchParams } from '../_shared';

export const dynamic = 'force-dynamic';

interface Props {
  searchParams: Promise<StudioWorkspaceSearchParams & {
    upload?: string;
    review?: string;
    ingest?: string;
  }>;
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

function reviewTone(reviewStatus: string | undefined): string {
  if (reviewStatus === 'approved') {
    return 'text-olive';
  }
  if (reviewStatus === 'rejected' || reviewStatus === 'needs-changes') {
    return 'text-accent';
  }
  return 'text-muted';
}

export default async function StudioSubmissionsPage({ searchParams }: Props) {
  const params = await searchParams;
  const workspaceOptions = getStudioWorkspaceOptions(params);
  const [payload, backendStatus] = await Promise.all([
    getAuthorSubmissions(workspaceOptions),
    getLocalBackendAvailability(),
  ]);

  const uploadDefault = params.upload ?? payload.built[0]?.submission_path ?? '';
  const reviewDefault = params.review ?? payload.inbox[0]?.submission_path ?? '';
  const ingestDefault = params.ingest ?? payload.inbox[0]?.submission_path ?? '';

  return (
    <Shell maxWidth="2xl" className="py-8">
      <section className="animate-fade-in">
        <Card variant="hero" className="px-8 py-10" data-testid="studio-submissions-hero">
          <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-olive">Studio / Submissions</p>
              <h1 className="mt-4 text-3xl font-bold text-ink">管理 build、upload、review 和 ingest</h1>
              <p className="mt-4 max-w-3xl text-base text-muted">
                这里把 `dist/submissions/` 和 `incoming/submissions/` 的状态集中展示出来，同时提供 3 个 backend job 面板，
                方便直接从页面推进 Week 5 的 maintainer 流程。
              </p>
            </div>

            <div className="rounded-card border border-line bg-paper/80 px-5 py-5" data-testid="studio-submissions-backend">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Backend status</p>
              <p className="mt-3 text-sm text-ink">{backendStatus.message}</p>
              <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-card bg-bg/60 px-4 py-3" data-testid="studio-submissions-count-built">
                  <p className="text-xs uppercase tracking-wide text-muted">Built</p>
                  <p className="mt-2 text-2xl font-bold text-accent">{payload.counts.built}</p>
                </div>
                <div className="rounded-card bg-bg/60 px-4 py-3" data-testid="studio-submissions-count-inbox">
                  <p className="text-xs uppercase tracking-wide text-muted">Inbox</p>
                  <p className="mt-2 text-2xl font-bold text-olive">{payload.counts.inbox}</p>
                </div>
                <div className="rounded-card bg-bg/60 px-4 py-3" data-testid="studio-submissions-count-approved">
                  <p className="text-xs uppercase tracking-wide text-muted">Approved</p>
                  <p className="mt-2 text-2xl font-bold text-olive">{payload.counts.approved}</p>
                </div>
                <div className="rounded-card bg-bg/60 px-4 py-3" data-testid="studio-submissions-count-ingested">
                  <p className="text-xs uppercase tracking-wide text-muted">Ingested</p>
                  <p className="mt-2 text-2xl font-bold text-accent">{payload.counts.ingested}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section className="mt-10 grid gap-6 xl:grid-cols-[1.15fr_0.85fr] animate-fade-in-delay-1">
        <div className="space-y-6">
          <Card className="p-6" data-testid="studio-built-submissions">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-semibold text-ink">Built submissions</h2>
              <p className="text-xs text-muted">{payload.workspace.submissions_root}</p>
            </div>
            <div className="mt-5 space-y-4">
              {payload.built.length > 0 ? (
                payload.built.map((record) => (
                  <div
                    key={record.submission_path}
                    className="rounded-card border border-line bg-bg/60 px-4 py-4"
                    data-testid="studio-built-record"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
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
                        使用此路径上传
                      </Link>
                    </div>
                    <p className="mt-2 text-xs text-muted">{record.submission_path}</p>
                    <p className="mt-2 text-xs text-muted">创建时间：{formatTimestamp(record.created_at)}</p>
                    <p className="mt-2 text-sm text-muted">{record.release_notes || 'No release notes.'}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted">还没有 build 产物。先去 `/studio/new` 生成 submission。</p>
              )}
            </div>
          </Card>

          <Card className="p-6" data-testid="studio-inbox-submissions">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-semibold text-ink">Inbox submissions</h2>
              <p className="text-xs text-muted">{payload.workspace.inbox_root}</p>
            </div>
            <div className="mt-5 space-y-4">
              {payload.inbox.length > 0 ? (
                payload.inbox.map((record) => (
                  <div
                    key={record.submission_path}
                    className="rounded-card border border-line bg-paper px-4 py-4"
                    data-testid="studio-inbox-record"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-ink">{record.skill_name}</p>
                        <p className="text-xs text-muted">{record.submission_id}</p>
                      </div>
                      <div className="flex flex-wrap gap-3 text-sm">
                        <Link
                          href={buildStudioHref('/studio/submissions', params, {
                            review: record.submission_path,
                          })}
                          className="font-medium text-accent hover:underline"
                        >
                          Review
                        </Link>
                        <Link
                          href={buildStudioHref('/studio/submissions', params, {
                            ingest: record.submission_path,
                          })}
                          className="font-medium text-accent hover:underline"
                        >
                          Ingest
                        </Link>
                      </div>
                    </div>
                    <p className="mt-2 text-xs text-muted">{record.submission_path}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-4 text-xs">
                      <span className={reviewTone(record.review?.review_status)}>
                        review: {record.review?.review_status || 'pending'}
                      </span>
                      <span className="text-muted">
                        ingest: {record.ingest ? record.ingest.target_source_dir : 'not-ingested'}
                      </span>
                    </div>
                    {record.review && (
                      <p className="mt-2 text-xs text-muted">
                        {record.review.reviewer} 于 {formatTimestamp(record.review.reviewed_at)} 记录了 review
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted">inbox 还没有 submission。先从 built 列表里触发 upload。</p>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <StudioJobPanel
            key={`upload:${uploadDefault}:${workspaceOptions.inboxRoot ?? 'incoming/submissions'}`}
            panelTestId="studio-upload-submission"
            title="Upload submission"
            description="把 dist/submissions 下的交接物复制到 maintainer inbox，并重写成 inbox 内自洽路径。"
            requestPath="/api/author/submissions/upload"
            runButtonLabel="Upload to inbox"
            runningLabel="Uploading..."
            fields={[
              {
                name: 'path',
                label: 'Submission path',
                defaultValue: uploadDefault,
                placeholder: 'dist/submissions/moyuan/my-skill/0.1.0/submission.json',
                required: true,
              },
              {
                name: 'inbox_dir',
                label: 'Inbox dir',
                defaultValue: workspaceOptions.inboxRoot ?? 'incoming/submissions',
                description: '默认使用 repo 内 maintainer inbox。',
              },
            ]}
          />

          <StudioJobPanel
            key={`review:${reviewDefault}`}
            panelTestId="studio-review-submission"
            title="Review submission"
            description="写入标准 review.json，并可选在 review 前运行 inbox 内 checker。"
            requestPath="/api/author/submissions/review"
            requestBody={{ run_checker: true }}
            runButtonLabel="Write review"
            runningLabel="Reviewing..."
            fields={[
              {
                name: 'path',
                label: 'Inbox submission path',
                defaultValue: reviewDefault,
                placeholder: 'incoming/submissions/moyuan/my-skill/0.1.0/submission.json',
                required: true,
              },
              {
                name: 'review_status',
                label: 'Review status',
                type: 'select',
                defaultValue: 'approved',
                options: [
                  { label: 'Approved', value: 'approved' },
                  { label: 'Needs changes', value: 'needs-changes' },
                  { label: 'Rejected', value: 'rejected' },
                  { label: 'Pending', value: 'pending' },
                ],
              },
              {
                name: 'reviewer',
                label: 'Reviewer',
                defaultValue: 'Market Maintainer',
              },
              {
                name: 'summary',
                label: 'Summary',
                type: 'textarea',
                defaultValue: 'Submission passed inbox review.',
                required: true,
              },
            ]}
          />

          <StudioJobPanel
            key={`ingest:${ingestDefault}`}
            panelTestId="studio-ingest-submission"
            title="Ingest submission"
            description="把 approved inbox submission 先写到 staging ingest 目录做预演；确认后再切回 canonical skills/docs。"
            requestPath="/api/author/submissions/ingest"
            runButtonLabel="Ingest submission"
            runningLabel="Ingesting..."
            footnote="默认先写到 dist/backend-author-ingested。确认内容无误后，再把目标改成 skills / docs 做正式 ingest。"
            fields={[
              {
                name: 'path',
                label: 'Inbox submission path',
                defaultValue: ingestDefault,
                placeholder: 'incoming/submissions/moyuan/my-skill/0.1.0/submission.json',
                required: true,
              },
              {
                name: 'skills_dir',
                label: 'Skills target dir',
                defaultValue: 'dist/backend-author-ingested/skills',
                description: '默认 staging 目录；正式 ingest 时再改成 skills。',
              },
              {
                name: 'docs_dir',
                label: 'Docs target dir',
                defaultValue: 'dist/backend-author-ingested/docs',
                description: '默认 staging 目录；正式 ingest 时再改成 docs。',
              },
            ]}
          />
        </div>
      </section>
    </Shell>
  );
}
