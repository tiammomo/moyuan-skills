import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'hero' | 'panel';
}

export function Card({
  className,
  variant = 'default',
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        'border border-line rounded-card bg-paper/80 shadow-card transition-all duration-200',
        variant === 'hero' && 'rounded-card-xl bg-gradient-to-br from-paper/98 to-paper/90 border-line',
        variant === 'panel' && 'rounded-card bg-paper border-line p-5',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
