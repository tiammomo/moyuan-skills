import Link from 'next/link';
import { Shell } from '@/components/ui/Shell';
import { Card } from '@/components/ui/Card';

export const revalidate = 300;

const learningPaths = [
  {
    id: 'newcomer',
    title: '新手路径',
    description: '一小时内快速上手 Moyuan 技能',
    duration: '1 小时',
    steps: [
      { title: '欢迎与概述', file: '14-first-hour-onboarding.md' },
      { title: '如何阅读仓库', file: '02-read-the-repo.md' },
      { title: '学习地图', file: '01-learning-map.md' },
    ],
  },
  {
    id: 'skill-author',
    title: '技能编写者路径',
    description: '学习构建和发布你自己的技能',
    duration: '2-3 小时',
    steps: [
      { title: '构建你的第一个技能', file: '03-build-your-first-skill.md' },
      { title: '技能规范', file: '05-skill-structure.md' },
      { title: '渐进式披露', file: '04-progressive-disclosure-workshop.md' },
    ],
  },
  {
    id: 'maintainer',
    title: '维护者路径',
    description: '维护和改进现有技能',
    duration: '1-2 小时',
    steps: [
      { title: '技能设计模板', file: '08-skill-design-template.md' },
      { title: '技能编写指南', file: 'skill-authoring.md' },
    ],
  },
];

export default async function TeachingPage() {
  return (
    <Shell maxWidth="2xl" className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink mb-2">学习与教学</h1>
        <p className="text-muted">
          精心策划的学习路径，帮助你充分利用 Moyuan 技能。
        </p>
      </div>

      <div className="space-y-6">
        {learningPaths.map((path, pathIndex) => (
          <section
            key={path.id}
            className="animate-fade-in"
            style={{ animationDelay: `${pathIndex * 0.1}s` }}
          >
            <Card className="p-6">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-ink mb-1">{path.title}</h2>
                  <p className="text-sm text-muted">{path.description}</p>
                </div>
                <span className="text-xs font-medium px-2 py-1 bg-accent-soft text-accent rounded-full whitespace-nowrap">
                  {path.duration}
                </span>
              </div>

              <div className="border-t border-line pt-4">
                <h3 className="text-sm font-medium text-muted mb-3">推荐步骤</h3>
                <div className="space-y-2">
                  {path.steps.map((step, stepIndex) => (
                    <div key={step.file} className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full bg-olive text-paper flex items-center justify-center text-xs font-semibold flex-shrink-0">
                        {stepIndex + 1}
                      </div>
                      <span className="text-ink">{step.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </section>
        ))}
      </div>

      <section className="mt-8">
        <Card className="p-6 text-center">
          <p className="text-muted">
            所有教学材料均可访问{' '}
            <Link href="https://github.com/moyuan/moyuan-skills" className="text-accent hover:underline">
              Moyuan Skills 仓库
            </Link>
            。
          </p>
        </Card>
      </section>
    </Shell>
  );
}
