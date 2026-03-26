import Link from 'next/link';
import { Shell } from '@/components/ui/Shell';
import { Card } from '@/components/ui/Card';

export default function NotFound() {
  return (
    <Shell maxWidth="sm" className="py-16">
      <Card className="p-8 text-center">
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-accent-soft flex items-center justify-center">
          <span className="text-4xl">🔍</span>
        </div>
        <h1 className="text-2xl font-bold text-ink mb-2">页面未找到</h1>
        <p className="text-muted mb-6">
          你要查找的页面不存在或已被移动。
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-accent text-paper rounded-full font-medium hover:opacity-90 transition-opacity"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          返回首页
        </Link>
      </Card>
    </Shell>
  );
}
