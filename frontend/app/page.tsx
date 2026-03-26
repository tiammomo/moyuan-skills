import Link from 'next/link';
import { getMarketIndex, getChannelSkills, getAllSkills, getAllCategories } from '@/lib/data';
import { Shell } from '@/components/ui/Shell';
import { Card } from '@/components/ui/Card';
import { SkillCard } from '@/components/market/SkillCard';
import { ChannelStrip } from '@/components/market/ChannelStrip';
import { CategoryList } from '@/components/market/CategoryList';

export const revalidate = 300;

export default async function HomePage() {
  const [marketIndex, stableSkills, betaSkills, , categories] = await Promise.all([
    getMarketIndex(),
    getChannelSkills('stable').catch(() => ({ skills: [] })),
    getChannelSkills('beta').catch(() => ({ skills: [] })),
    getAllSkills(),
    getAllCategories(),
  ]);

  const stats = [
    { channel: 'stable' as const, count: marketIndex.channels.stable?.count || 0 },
    { channel: 'beta' as const, count: marketIndex.channels.beta?.count || 0 },
    { channel: 'internal' as const, count: marketIndex.channels.internal?.count || 0 },
  ];

  const featuredSkills = [...stableSkills.skills.slice(0, 3), ...betaSkills.skills.slice(0, 3)];

  return (
    <Shell maxWidth="2xl" className="py-8">
      {/* Hero Section */}
      <section className="mb-12 animate-fade-in">
        <Card variant="hero" className="px-8 py-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-olive to-accent text-paper font-bold text-2xl shadow-lg mb-6">
            M
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-ink mb-4">
            Moyuan 技能市场
          </h1>
          <p className="text-lg text-muted max-w-2xl mx-auto mb-8">
            发现、安装和分享可复用的技能，扩展你的 Moyuan 工作流。
            浏览我们精心策划的生产级技能集合。
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/skills"
              className="inline-flex items-center gap-2 px-6 py-3 bg-accent text-paper rounded-full font-medium hover:opacity-90 transition-opacity"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              浏览技能
            </Link>
            <Link
              href="/docs"
              className="inline-flex items-center gap-2 px-6 py-3 bg-paper border border-line text-ink rounded-full font-medium hover:bg-bg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              查看文档
            </Link>
          </div>
        </Card>
      </section>

      {/* Channel Stats */}
      <section className="mb-12 animate-fade-in-delay-1">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-olive mb-4">
          发行频道
        </h2>
        <ChannelStrip stats={stats} />
      </section>

      {/* Featured Skills */}
      <section className="mb-12 animate-fade-in-delay-2">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-ink">精选技能</h2>
          <Link
            href="/skills"
            className="text-sm font-medium text-accent hover:underline flex items-center gap-1"
          >
            查看全部
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredSkills.map((skill) => (
            <SkillCard key={skill.id} skill={skill} featured />
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="mb-12 animate-fade-in-delay-3">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-ink">分类</h2>
        </div>
        <Card className="p-6">
          <CategoryList categories={categories} />
        </Card>
      </section>

      {/* Quick Start */}
      <section className="mb-12 animate-fade-in-delay-3">
        <h2 className="text-xl font-semibold text-ink mb-6">快速开始</h2>
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-olive text-paper flex items-center justify-center font-semibold text-sm">
                1
              </div>
              <div>
                <h3 className="font-medium text-ink mb-1">浏览技能</h3>
                <p className="text-sm text-muted">
                  按分类和频道浏览我们的技能集合。
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-olive text-paper flex items-center justify-center font-semibold text-sm">
                2
              </div>
              <div>
                <h3 className="font-medium text-ink mb-1">阅读文档</h3>
                <p className="text-sm text-muted">
                  每个技能都包含详细的文档和使用示例。
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-olive text-paper flex items-center justify-center font-semibold text-sm">
                3
              </div>
              <div>
                <h3 className="font-medium text-ink mb-1">安装使用</h3>
                <p className="text-sm text-muted">
                  复制安装命令并在你的 Moyuan 环境中运行。
                </p>
              </div>
            </div>
          </div>
        </Card>
      </section>
    </Shell>
  );
}
