import Link from 'next/link';
import { getAllSkills } from '@/lib/data';
import { getLocalBackendAvailability } from '@/lib/local-backend';
import { StudioJobPanel } from '@/components/studio/StudioJobPanel';
import { Card } from '@/components/ui/Card';
import { Shell } from '@/components/ui/Shell';
import { buildStudioHref, getStudioWorkspaceOptions, type StudioWorkspaceSearchParams } from '../_shared';

export const dynamic = 'force-dynamic';

interface Props {
  searchParams: Promise<StudioWorkspaceSearchParams & { skill?: string }>;
}

export default async function StudioNewPage({ searchParams }: Props) {
  const params = await searchParams;
  const { skill } = params;
  const workspaceOptions = getStudioWorkspaceOptions(params);
  const [allSkills, backendStatus] = await Promise.all([
    getAllSkills(),
    getLocalBackendAvailability(),
  ]);

  const featuredSkills = Array.from(new Map(allSkills.map((item) => [item.name, item])).values()).slice(0, 6);

  return (
    <Shell maxWidth="2xl" className="py-8">
      <section className="animate-fade-in">
        <Card variant="hero" className="px-8 py-10" data-testid="studio-new-hero">
          <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-olive">Studio / New</p>
              <h1 className="mt-4 text-3xl font-bold text-ink">从 skill 源码构建 submission</h1>
              <p className="mt-4 max-w-3xl text-base text-muted">
                这一步调用 backend 的 `build-submission`，把当前 skill 的 manifest、package、provenance 和 payload archive
                打成标准交接物。你可以输入 skill 名，也可以直接输入 repo 内路径。
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href={buildStudioHref('/studio/submissions', params)}
                  data-testid="studio-new-link-submissions"
                  className="inline-flex items-center rounded-full border border-line bg-paper px-5 py-2.5 text-sm font-medium text-ink transition-colors hover:bg-bg"
                >
                  查看 submissions
                </Link>
              </div>
            </div>

            <div className="rounded-card border border-line bg-paper/80 px-5 py-5">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Backend status</p>
              <p className="mt-3 text-sm text-ink">{backendStatus.message}</p>
              <div className="mt-5 space-y-3 text-sm text-muted">
                <p>
                  推荐顺序：
                  <code className="mx-1 rounded bg-bg/80 px-1.5 py-0.5 text-xs text-ink">
                    doctor-skill -&gt; validate -&gt; build-submission -&gt; upload-submission
                  </code>
                  。
                </p>
                <p>
                  默认输出：
                  <code className="mx-1 rounded bg-bg/80 px-1.5 py-0.5 text-xs text-ink">
                    dist/submissions/&lt;publisher&gt;/&lt;skill&gt;/&lt;version&gt;/submission.json
                  </code>
                  。
                </p>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section className="mt-10 grid gap-6 lg:grid-cols-[1.15fr_0.85fr] animate-fade-in-delay-1">
        <StudioJobPanel
          key={`build:${skill ?? ''}:${workspaceOptions.submissionsRoot ?? 'dist/submissions'}`}
          panelTestId="studio-build-submission"
          title="Build submission"
          description="运行 backend author API，直接触发 build-submission。构建成功后刷新页面并转到 submissions 列表继续 upload。"
          requestPath="/api/author/submissions/build"
          runButtonLabel="Build submission"
          runningLabel="Building submission..."
          footnote="支持 skill 目录名，也支持像 dist/authoring-smoke/my-skill 这样的 repo 内路径。"
          fields={[
            {
              name: 'skill',
              label: 'Skill name or path',
              defaultValue: skill ?? '',
              placeholder: 'release-note-writer 或 dist/authoring-smoke/my-skill',
              required: true,
              description: '直接传给 build-submission 的 skill 参数。',
            },
            {
              name: 'output_dir',
              label: 'Submission output dir',
              defaultValue: workspaceOptions.submissionsRoot ?? 'dist/submissions',
              description: '默认保存在 dist/submissions 下。',
            },
            {
              name: 'market_dir',
              label: 'Market artifact dir',
              defaultValue: 'dist/market',
              description: '会复用 package/install/provenance 产物。',
            },
            {
              name: 'release_notes',
              label: 'Release notes',
              type: 'textarea',
              placeholder: '简要说明这次提交的改动和用途。',
              description: '可选；不填则沿用默认生成文案。',
            },
          ]}
        />

        <Card className="p-6" data-testid="studio-new-featured-skills">
          <h2 className="text-xl font-semibold text-ink">常用 skill 入口</h2>
          <div className="mt-5 space-y-3">
            {featuredSkills.map((entry) => (
              <Link
                key={entry.id}
                href={buildStudioHref('/studio/new', params, { skill: entry.name })}
                data-testid={`studio-featured-skill-${entry.name}`}
                className="block rounded-card border border-line bg-bg/60 px-4 py-4 transition-colors hover:bg-paper"
              >
                <p className="text-sm font-semibold text-ink">{entry.title}</p>
                <p className="mt-1 text-xs text-muted">{entry.name}</p>
                <p className="mt-2 text-sm text-muted">{entry.summary}</p>
              </Link>
            ))}
          </div>
        </Card>
      </section>
    </Shell>
  );
}
