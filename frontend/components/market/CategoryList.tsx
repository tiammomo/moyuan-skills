import Link from 'next/link';
import { Chip } from '@/components/ui/Chip';

interface CategoryListProps {
  categories: { category: string; count: number }[];
}

export function CategoryList({ categories }: CategoryListProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {categories.map(({ category, count }) => (
        <Link
          key={category}
          href={`/skills?category=${encodeURIComponent(category)}`}
          className="inline-flex items-center gap-1.5 group"
        >
          <Chip variant="category" className="group-hover:bg-olive group-hover:text-paper transition-colors">
            {category}
          </Chip>
          <span className="text-xs text-muted group-hover:text-ink transition-colors">
            ({count})
          </span>
        </Link>
      ))}
    </div>
  );
}
