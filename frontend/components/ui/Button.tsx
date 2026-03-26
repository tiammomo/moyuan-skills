import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  className,
  variant = 'primary',
  size = 'md',
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-full',
        'hover:opacity-90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed',
        {
          'bg-accent text-paper px-5 py-2.5': variant === 'primary',
          'bg-paper border border-line text-ink px-5 py-2.5 hover:bg-bg': variant === 'secondary',
          'bg-transparent text-ink px-3 py-2 hover:bg-paper': variant === 'ghost',
          'text-sm px-3 py-1.5': size === 'sm',
          'text-base px-5 py-2.5': size === 'md',
          'text-lg px-6 py-3': size === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
