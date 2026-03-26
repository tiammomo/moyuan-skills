import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getChannelSkills } from '@/lib/data';
import { Shell } from '@/components/ui/Shell';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SkillGrid } from '@/components/market/SkillGrid';
import type { Channel } from '@/types/market';

export const revalidate = 300;

interface Props {
  params: Promise<{ channel: string }>;
}

const validChannels: Channel[] = ['stable', 'beta', 'internal'];

export async function generateStaticParams() {
  return validChannels.map((channel) => ({ channel }));
}

const channelInfo: Record<Channel, { title: string; description: string }> = {
  stable: {
    title: '稳定版频道',
    description: '经过审核和测试的生产级技能。',
  },
  beta: {
    title: '测试版频道',
    description: '可供测试和反馈的预发布技能。',
  },
  internal: {
    title: '内部版频道',
    description: '组织内部技能，不对公众开放。',
  },
};

export async function generateMetadata({ params }: Props) {
  const { channel } = await params;
  const info = channelInfo[channel as Channel];
  if (!info) return { title: '频道未找到' };
  return {
    title: `${info.title} - Moyuan 技能市场`,
    description: info.description,
  };
}

export default async function ChannelPage({ params }: Props) {
  const { channel } = await params;

  if (!validChannels.includes(channel as Channel)) {
    notFound();
  }

  const channelData = await getChannelSkills(channel as Channel);
  const info = channelInfo[channel as Channel];

  return (
    <Shell maxWidth="2xl" className="py-8">
      {/* Breadcrumb */}
      <nav className="mb-6 text-sm">
        <ol className="flex items-center gap-2 text-muted">
          <li>
            <Link href="/channels" className="hover:text-accent transition-colors">
              频道
            </Link>
          </li>
          <li>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </li>
          <li className="text-ink">{info.title.replace('频道', '')}</li>
        </ol>
      </nav>

      {/* Header */}
      <section className="mb-8 animate-fade-in">
        <Card className="p-6 sm:p-8">
          <div className="flex items-center gap-4 mb-4">
            <Badge channel={channel as Channel} />
            <span className="text-2xl font-bold text-ink">{info.title}</span>
          </div>
          <p className="text-muted">{info.description}</p>
          <p className="text-sm text-muted mt-2">
            共 {channelData.skills.length} 个技能可用
          </p>
        </Card>
      </section>

      {/* Skills Grid */}
      <section className="animate-fade-in-delay-1">
        <SkillGrid skills={channelData.skills} />
      </section>
    </Shell>
  );
}
