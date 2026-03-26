import Link from 'next/link';

export function Footer() {
  return (
    <footer className="mt-20 border-t border-line bg-paper/50">
      <div className="max-w-screen-2xl mx-auto px-5 sm:px-8 lg:px-10 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-olive to-accent flex items-center justify-center text-paper font-bold text-lg">
                M
              </div>
              <div>
                <div className="text-lg font-semibold text-ink">Moyuan 技能市场</div>
                <div className="text-xs text-muted">发现、安装和分享技能</div>
              </div>
            </div>
            <p className="text-muted text-sm max-w-md">
              一个用于扩展 Moyuan 工作流的可复用、可组合技能市场。
              找到适合你需求的完美技能，或与社区分享你的创作。
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-ink mb-4">市场</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/skills" className="text-sm text-muted hover:text-accent transition-colors">
                  浏览技能
                </Link>
              </li>
              <li>
                <Link href="/channels" className="text-sm text-muted hover:text-accent transition-colors">
                  发行频道
                </Link>
              </li>
              <li>
                <Link href="/bundles" className="text-sm text-muted hover:text-accent transition-colors">
                  入门套餐
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-ink mb-4">资源</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/docs" className="text-sm text-muted hover:text-accent transition-colors">
                  文档中心
                </Link>
              </li>
              <li>
                <Link href="/docs/teaching" className="text-sm text-muted hover:text-accent transition-colors">
                  学习路径
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/moyuan/moyuan-skills"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-muted hover:text-accent transition-colors"
                >
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-line flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-muted">
            Moyuan 技能市场 · 使用 Next.js 16 构建
          </p>
          <div className="flex items-center gap-4">
            <span className="text-xs text-muted">
              版本 0.1.0
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
