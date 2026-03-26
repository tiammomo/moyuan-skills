import { Suspense } from 'react';
import { getAllSkills, getAllCategories, getAllTags } from '@/lib/data';
import { SkillsClient } from './SkillsClient';

export const revalidate = 300;

export default async function SkillsPage() {
  const [skills, categories, tags] = await Promise.all([
    getAllSkills(),
    getAllCategories(),
    getAllTags(),
  ]);

  return (
    <Suspense fallback={<div className="min-h-screen bg-bg" />}>
      <SkillsClient skills={skills} categories={categories} tags={tags} />
    </Suspense>
  );
}
