import { cn } from '@/lib/utils';

interface ChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'category' | 'tag' | 'keyword' | 'stable' | 'beta' | 'internal';
}

export function Chip({
  className,
  variant = 'tag',
  children,
  ...props
}: ChipProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium',
        {
          'bg-[#edf4ea] text-olive border border-[#c8dbc9]': variant === 'category',
          'bg-[#fff4e8] text-[#b5482c] border border-[#f0d4b8]': variant === 'tag',
          'bg-accent-soft text-accent border border-[#e8c9b8]': variant === 'keyword',
          'bg-[#ddeee0] text-olive border border-[#87a88c]': variant === 'stable',
          'bg-[#fff4e8] text-accent border border-[#e8c9b8]': variant === 'beta',
          'bg-[#f3efe4] text-muted border border-line': variant === 'internal',
        },
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
