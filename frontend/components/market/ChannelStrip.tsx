import Link from 'next/link';
import type { Channel } from '@/types/market';

interface ChannelStats {
  channel: Channel;
  count: number;
}

interface ChannelStripProps {
  stats: ChannelStats[];
}

export function ChannelStrip({ stats }: ChannelStripProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {stats.map(({ channel, count }) => (
        <Link
          key={channel}
          href={`/channels/${channel}`}
          className="group"
        >
          <div className="border border-line rounded-card-xl bg-paper/70 p-6 text-center hover:shadow-card transition-all duration-200 hover:-translate-y-0.5">
            <div className="text-3xl font-bold text-ink mb-1">{count}</div>
            <div
              className={`text-sm font-medium uppercase tracking-wider ${
                channel === 'stable'
                  ? 'text-olive'
                  : channel === 'beta'
                  ? 'text-accent'
                  : 'text-muted'
              }`}
            >
              {channel}
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
