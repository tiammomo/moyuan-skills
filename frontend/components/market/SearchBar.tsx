'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  className?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export function SearchBar({
  className,
  placeholder = 'Search skills...',
  value,
  onChange,
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState(value ?? '');

  useEffect(() => {
    if (value !== undefined) {
      setInternalValue(value);
    }
  }, [value]);

  const resolvedValue = value ?? internalValue;

  const updateValue = (nextValue: string) => {
    if (value === undefined) {
      setInternalValue(nextValue);
    }
    onChange?.(nextValue);
  };

  return (
    <div className={cn('relative', className)}>
      <svg
        className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted pointer-events-none"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <input
        data-testid="skill-search-input"
        type="text"
        value={resolvedValue}
        onChange={(event) => updateValue(event.target.value)}
        placeholder={placeholder}
        className="w-full pl-12 pr-4 py-3 rounded-full border border-line bg-paper text-ink placeholder:text-muted/60 focus:outline-none focus:ring-2 focus:ring-olive/30 focus:border-olive transition-all"
      />
      {resolvedValue && (
        <button
          type="button"
          data-testid="skill-search-clear"
          onClick={() => updateValue('')}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-muted hover:text-ink transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
