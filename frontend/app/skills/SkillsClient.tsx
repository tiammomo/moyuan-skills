'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import type { SkillSummary, Channel } from '@/types/market';
import { SearchBar } from '@/components/market/SearchBar';
import { SkillGrid } from '@/components/market/SkillGrid';
import { Chip } from '@/components/ui/Chip';
import { Shell } from '@/components/ui/Shell';
import { Button } from '@/components/ui/Button';

interface SkillsClientProps {
  skills: SkillSummary[];
  categories: { category: string; count: number }[];
  tags: { tag: string; count: number }[];
}

export function SkillsClient({ skills, categories, tags }: SkillsClientProps) {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [selectedChannels, setSelectedChannels] = useState<Channel[]>(
    searchParams.get('channel')?.split(',').filter(Boolean) as Channel[] || []
  );
  const [selectedCategories, setSelectedCategories] = useState<string[]>(
    searchParams.get('category')?.split(',').filter(Boolean) || []
  );
  const [selectedTags, setSelectedTags] = useState<string[]>(
    searchParams.get('tag')?.split(',').filter(Boolean) || []
  );
  const [sortBy, setSortBy] = useState<'alpha' | 'channel'>('alpha');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    setQuery(searchParams.get('q') || '');
    setSelectedChannels((searchParams.get('channel')?.split(',').filter(Boolean) as Channel[]) || []);
    setSelectedCategories(searchParams.get('category')?.split(',').filter(Boolean) || []);
    setSelectedTags(searchParams.get('tag')?.split(',').filter(Boolean) || []);
  }, [searchParams]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (selectedChannels.length) params.set('channel', selectedChannels.join(','));
    if (selectedCategories.length) params.set('category', selectedCategories.join(','));
    if (selectedTags.length) params.set('tag', selectedTags.join(','));

    const nextQueryString = params.toString();
    const currentQueryString = searchParams.toString();

    if (nextQueryString === currentQueryString) {
      return;
    }

    const nextPath = nextQueryString ? `/skills?${nextQueryString}` : '/skills';
    router.replace(nextPath, { scroll: false });
  }, [query, searchParams, selectedChannels, selectedCategories, selectedTags, router]);

  const filteredSkills = skills.filter((skill) => {
    // Text search
    if (query) {
      const searchText = `${skill.title} ${skill.summary} ${skill.tags.join(' ')} ${skill.categories.join(' ')}`.toLowerCase();
      if (!searchText.includes(query.toLowerCase())) return false;
    }

    // Channel filter
    if (selectedChannels.length && !selectedChannels.includes(skill.channel)) return false;

    // Category filter
    if (selectedCategories.length && !skill.categories.some((c) => selectedCategories.includes(c))) return false;

    // Tag filter
    if (selectedTags.length && !skill.tags.some((t) => selectedTags.includes(t))) return false;

    return true;
  });

  const sortedSkills = [...filteredSkills].sort((a, b) => {
    if (sortBy === 'alpha') {
      return a.title.localeCompare(b.title);
    }
    return 0;
  });

  const toggleChannel = (channel: Channel) => {
    setSelectedChannels((prev) =>
      prev.includes(channel) ? prev.filter((c) => c !== channel) : [...prev, channel]
    );
  };

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    );
  };

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const clearFilters = () => {
    setQuery('');
    setSelectedChannels([]);
    setSelectedCategories([]);
    setSelectedTags([]);
  };

  const hasActiveFilters = query || selectedChannels.length || selectedCategories.length || selectedTags.length;

  const channelLabels: Record<Channel, string> = {
    stable: '稳定版',
    beta: '测试版',
    internal: '内部版',
  };

  return (
    <Shell maxWidth="2xl" className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink mb-2">浏览技能</h1>
        <p className="text-muted">
          共 {skills.length} 个技能，分布在所有频道
        </p>
      </div>

      {/* Search and Filter Toggle */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <SearchBar className="flex-1" placeholder="搜索技能..." value={query} onChange={setQuery} />
        <Button
          variant="secondary"
          onClick={() => setShowFilters(!showFilters)}
          className="sm:w-auto"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          筛选
          {hasActiveFilters && (
            <span className="ml-2 w-5 h-5 rounded-full bg-accent text-paper text-xs flex items-center justify-center">
              {(selectedChannels.length || selectedCategories.length || selectedTags.length) + (query ? 1 : 0)}
            </span>
          )}
        </Button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="mb-8 p-6 border border-line rounded-card-xl bg-paper animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Channels */}
            <div>
              <h3 className="text-sm font-semibold text-ink mb-3">频道</h3>
              <div className="space-y-2">
                {(['stable', 'beta', 'internal'] as Channel[]).map((channel) => (
                  <label key={channel} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedChannels.includes(channel)}
                      onChange={() => toggleChannel(channel)}
                      className="w-4 h-4 rounded border-line text-olive focus:ring-olive"
                    />
                    <span className="text-sm text-ink">{channelLabels[channel]}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Categories */}
            <div>
              <h3 className="text-sm font-semibold text-ink mb-3">分类</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {categories.map(({ category }) => (
                  <label key={category} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(category)}
                      onChange={() => toggleCategory(category)}
                      className="w-4 h-4 rounded border-line text-olive focus:ring-olive"
                    />
                    <span className="text-sm text-ink">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Tags */}
            <div>
              <h3 className="text-sm font-semibold text-ink mb-3">标签</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {tags.map(({ tag }) => (
                  <label key={tag} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedTags.includes(tag)}
                      onChange={() => toggleTag(tag)}
                      className="w-4 h-4 rounded border-line text-olive focus:ring-olive"
                    />
                    <span className="text-sm text-ink">{tag}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {hasActiveFilters && (
            <div className="mt-4 pt-4 border-t border-line flex justify-end">
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                清除所有筛选
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="mb-6 flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted">当前筛选：</span>
          {query && (
            <Chip variant="keyword" className="cursor-pointer" onClick={() => setQuery('')}>
              &quot;{query}&quot; ×
            </Chip>
          )}
          {selectedChannels.map((channel) => (
            <Chip key={channel} variant={channel as 'stable' | 'beta' | 'internal'} className="cursor-pointer" onClick={() => toggleChannel(channel)}>
              {channelLabels[channel]} ×
            </Chip>
          ))}
          {selectedCategories.map((category) => (
            <Chip key={category} variant="category" className="cursor-pointer" onClick={() => toggleCategory(category)}>
              {category} ×
            </Chip>
          ))}
          {selectedTags.map((tag) => (
            <Chip key={tag} variant="tag" className="cursor-pointer" onClick={() => toggleTag(tag)}>
              {tag} ×
            </Chip>
          ))}
        </div>
      )}

      {/* Sort */}
      <div className="mb-6 flex items-center justify-between">
        <p className="text-sm text-muted">
          找到 {sortedSkills.length} 个技能
        </p>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted">排序：</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'alpha' | 'channel')}
            className="text-sm border border-line rounded-lg px-3 py-1.5 bg-paper text-ink focus:outline-none focus:ring-2 focus:ring-olive"
          >
            <option value="alpha">按名称</option>
            <option value="channel">按频道</option>
          </select>
        </div>
      </div>

      {/* Results */}
      <SkillGrid
        skills={sortedSkills}
        emptyMessage="没有符合条件的技能，请调整筛选条件"
      />
    </Shell>
  );
}
