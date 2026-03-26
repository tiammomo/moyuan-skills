import Link from 'next/link';
import { getMarketIndex } from '@/lib/data';
import { Shell } from '@/components/ui/Shell';
import { Card } from '@/components/ui/Card';
import type { Channel } from '@/types/market';

export const revalidate = 300;

export default async function ChannelsPage() {
  const marketIndex = await getMarketIndex();

  const channels: { channel: Channel; count: number; description: string; title: string }[] = [
    {
      channel: 'stable',
      count: marketIndex.channels.stable?.count || 0,
      title: '稳定版',
      description: '经过审核和测试的生产级技能。推荐用于大多数使用场景。',
    },
    {
      channel: 'beta',
      count: marketIndex.channels.beta?.count || 0,
      title: '测试版',
      description: '可供测试和反馈的预发布技能。可能包含仍在开发中的新功能。',
    },
    {
      channel: 'internal',
      count: marketIndex.channels.internal?.count || 0,
      title: '内部版',
      description: '不对公众开放的组织内部技能。访问受限。',
    },
  ];

  return (
    <Shell maxWidth="2xl" className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink mb-2">发行频道</h1>
        <p className="text-muted">
          技能根据其成熟度和可用性分布在不同的频道中。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {channels.map(({ channel, count, description, title }) => (
          <Link key={channel} href={`/channels/${channel}`} className="block group">
            <Card className="h-full p-6 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl ${
                    channel === 'stable'
                      ? 'bg-olive text-paper'
                      : channel === 'beta'
                      ? 'bg-accent text-paper'
                      : 'bg-line text-muted'
                  }`}
                >
                  {channel === 'stable' ? '✓' : channel === 'beta' ? 'β' : '∅'}
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-ink">{title}</h2>
                  <p className="text-sm text-muted">{count} 个技能</p>
                </div>
              </div>
              <p className="text-sm text-muted mb-4">{description}</p>
              <span className="text-sm font-medium text-accent flex items-center gap-1 group-hover:underline">
                浏览{title}技能
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </Card>
          </Link>
        ))}
      </div>
    </Shell>
  );
}
