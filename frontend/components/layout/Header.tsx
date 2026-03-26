'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: '首页' },
  { href: '/skills', label: '技能' },
  { href: '/channels', label: '频道' },
  { href: '/bundles', label: '套餐' },
  { href: '/docs', label: '文档' },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-bg/80 backdrop-blur-md border-b border-line">
      <div className="max-w-screen-2xl mx-auto px-5 sm:px-8 lg:px-10">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-olive to-accent flex items-center justify-center text-paper font-bold text-lg shadow-md group-hover:scale-105 transition-transform">
              M
            </div>
            <div className="hidden sm:block">
              <div className="text-lg font-semibold text-ink">Moyuan 技能</div>
              <div className="text-xs text-muted -mt-0.5">市场</div>
            </div>
          </Link>

          <nav className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href ||
                (item.href !== '/' && pathname.startsWith(item.href));

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'px-4 py-2 rounded-full text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-olive text-paper shadow-sm'
                      : 'text-ink hover:bg-paper'
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
