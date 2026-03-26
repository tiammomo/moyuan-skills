import { cn } from '@/lib/utils';
import type { Channel } from '@/types/market';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  channel?: Channel;
}

export function Badge({ className, channel, children, ...props }: BadgeProps) {
  if (channel) {
    return (
      <span
        className={cn(
          'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider',
          {
            'bg-[#ddeee0] text-olive border border-[#87a88c]': channel === 'stable',
            'bg-[#fff4e8] text-accent border border-[#e8c9b8]': channel === 'beta',
            'bg-[#f3efe4] text-muted border border-line': channel === 'internal',
          },
          className
        )}
        {...props}
      >
        {channel}
      </span>
    );
  }

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-accent-soft text-accent',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
