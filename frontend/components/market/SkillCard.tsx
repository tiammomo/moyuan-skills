import Link from 'next/link';
import type { SkillSummary } from '@/types/market';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { Badge } from '@/components/ui/Badge';

interface SkillCardProps {
  skill: SkillSummary;
  featured?: boolean;
}

export function SkillCard({ skill, featured }: SkillCardProps) {
  return (
    <Link href={`/skills/${skill.name}`} className="block group" data-testid={`skill-card-${skill.name}`}>
      <Card
        className={`h-full p-5 hover:shadow-card-lg hover:-translate-y-1 transition-all duration-300 ${
          featured ? 'border-accent/20' : ''
        }`}
      >
        <div className="flex items-start justify-between gap-3 mb-3">
          <Badge channel={skill.channel} />
          <span className="text-xs text-muted">v{skill.version}</span>
        </div>

        <h3 className="text-lg font-semibold text-ink mb-2 group-hover:text-accent transition-colors line-clamp-1">
          {skill.title}
        </h3>

        <p className="text-sm text-muted mb-4 line-clamp-2">
          {skill.summary}
        </p>

        <div className="flex flex-wrap gap-1.5 mb-3">
          {skill.categories.slice(0, 3).map((category) => (
            <Chip key={category} variant="category">
              {category}
            </Chip>
          ))}
        </div>

        <div className="flex flex-wrap gap-1.5">
          {skill.tags.slice(0, 4).map((tag) => (
            <Chip key={tag} variant="tag">
              {tag}
            </Chip>
          ))}
        </div>

        {featured && (
          <div className="mt-4 pt-4 border-t border-line">
            <span className="text-xs text-accent font-medium flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              查看详情
            </span>
          </div>
        )}
      </Card>
    </Link>
  );
}
