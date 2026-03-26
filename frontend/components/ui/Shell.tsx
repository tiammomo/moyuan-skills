import { cn } from '@/lib/utils';

interface ShellProps extends React.HTMLAttributes<HTMLDivElement> {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

export function Shell({
  className,
  maxWidth = '2xl',
  children,
  ...props
}: ShellProps) {
  return (
    <div
      className={cn(
        'w-full mx-auto px-5 sm:px-8 lg:px-10',
        {
          'max-w-screen-sm': maxWidth === 'sm',
          'max-w-screen-md': maxWidth === 'md',
          'max-w-screen-lg': maxWidth === 'lg',
          'max-w-screen-xl': maxWidth === 'xl',
          'max-w-screen-2xl': maxWidth === '2xl',
          'max-w-full': maxWidth === 'full',
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
