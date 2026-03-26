import fs from 'fs/promises';
import path from 'path';
import type {
  BundleDetailPayload,
  BundleSummary,
  Channel,
  ChannelIndex,
  DocsCatalog,
  DocsCatalogEntry,
  InstallSpec,
  MarketIndex,
  ProjectDocPayload,
  SkillDetailPayload,
  SkillManifest,
  SkillSummary,
  TeachingDocPayload,
} from '@/types/market';

const DATA_ROOT = path.join(process.cwd(), '..');
const API_BASE_URL = process.env.SKILLS_MARKET_API_BASE_URL?.replace(/\/+$/, '');
const REVALIDATE_SECONDS = 300;

type BundleFilePayload = {
  id: string;
  title: string;
  summary: string;
  description: string;
  status: 'draft' | 'published';
  channels: Channel[];
  skills: string[];
  use_cases: string[];
  keywords: string[];
};

export function getRepoRoot(): string {
  return DATA_ROOT;
}

function isApiMode(): boolean {
  return Boolean(API_BASE_URL);
}

export async function readJson<T>(filePath: string): Promise<T> {
  const content = await fs.readFile(filePath, 'utf-8');
  return JSON.parse(content) as T;
}

export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function fetchJson<T>(pathname: string): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error('SKILLS_MARKET_API_BASE_URL is not configured.');
  }

  const response = await fetch(`${API_BASE_URL}${pathname}`, {
    headers: {
      accept: 'application/json',
    },
    next: {
      revalidate: REVALIDATE_SECONDS,
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed for ${pathname}: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

function firstHeading(markdown: string, fallback: string): string {
  for (const line of markdown.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (trimmed.startsWith('#')) {
      return trimmed.replace(/^#+\s*/, '').trim() || fallback;
    }
  }
  return fallback;
}

function firstParagraph(markdown: string): string {
  const lines = markdown.split(/\r?\n/).map((line) => line.trim());
  const buffer: string[] = [];
  let started = false;

  for (const line of lines) {
    if (!line) {
      if (started && buffer.length > 0) {
        break;
      }
      continue;
    }
    if (!started && line.startsWith('#')) {
      continue;
    }
    started = true;
    buffer.push(line);
  }

  return buffer.join(' ').trim();
}

function isInternalIterationDoc(id: string): boolean {
  return id.endsWith('-iteration');
}

export async function getMarketIndex(): Promise<MarketIndex> {
  if (isApiMode()) {
    return fetchJson<MarketIndex>('/api/v1/market/index');
  }

  return readJson<MarketIndex>(path.join(DATA_ROOT, 'dist/market/index.json'));
}

export async function getChannelSkills(channel: Channel): Promise<ChannelIndex> {
  if (isApiMode()) {
    return fetchJson<ChannelIndex>(`/api/v1/market/channels/${channel}`);
  }

  return readJson<ChannelIndex>(path.join(DATA_ROOT, `dist/market/channels/${channel}.json`));
}

export async function getAllSkills(): Promise<SkillSummary[]> {
  if (isApiMode()) {
    const payload = await fetchJson<{ count: number; skills: SkillSummary[] }>('/api/v1/market/skills');
    return payload.skills;
  }

  const channels: Channel[] = ['stable', 'beta', 'internal'];
  const allSkills: SkillSummary[] = [];

  for (const channel of channels) {
    try {
      const payload = await getChannelSkills(channel);
      allSkills.push(...payload.skills);
    } catch {
      // Ignore missing channel files in local mode.
    }
  }

  return allSkills;
}

export async function getInstallSpec(skillName: string, version: string): Promise<InstallSpec | null> {
  if (isApiMode()) {
    try {
      return await fetchJson<InstallSpec>(`/api/v1/market/skills/${skillName}/install-spec`);
    } catch {
      return null;
    }
  }

  const filePath = path.join(DATA_ROOT, `dist/market/install/${skillName}-${version}.json`);
  try {
    return await readJson<InstallSpec>(filePath);
  } catch {
    return null;
  }
}

export async function getSkillManifest(skillName: string): Promise<SkillManifest | null> {
  if (isApiMode()) {
    const detail = await getSkillDetail(skillName);
    return detail?.manifest ?? null;
  }

  const filePath = path.join(DATA_ROOT, `skills/${skillName}/market/skill.json`);
  try {
    return await readJson<SkillManifest>(filePath);
  } catch {
    return null;
  }
}

export async function getSkillDoc(skillName: string): Promise<string | null> {
  if (isApiMode()) {
    try {
      const payload = await fetchJson<{ name: string; markdown: string; path: string }>(
        `/api/v1/market/skills/${skillName}/doc`
      );
      return payload.markdown;
    } catch {
      return null;
    }
  }

  const filePath = path.join(DATA_ROOT, `docs/${skillName}.md`);
  try {
    return await fs.readFile(filePath, 'utf-8');
  } catch {
    return null;
  }
}

export async function getSkillDetail(skillName: string): Promise<SkillDetailPayload | null> {
  if (isApiMode()) {
    try {
      return await fetchJson<SkillDetailPayload>(`/api/v1/market/skills/${skillName}`);
    } catch {
      return null;
    }
  }

  const manifest = await getSkillManifest(skillName);
  if (!manifest) {
    return null;
  }

  const [installSpec, docMarkdown, allSkills] = await Promise.all([
    getInstallSpec(skillName, manifest.version),
    getSkillDoc(skillName),
    getAllSkills(),
  ]);

  const byId = new Map(allSkills.map((skill) => [skill.id, skill]));
  const relatedSkills =
    manifest.search?.related_skills
      ?.map((skillId) => byId.get(skillId))
      .filter((skill): skill is SkillSummary => Boolean(skill)) ?? [];

  return {
    manifest,
    install_spec: installSpec,
    doc_markdown: docMarkdown,
    related_skills: relatedSkills,
  };
}

export async function getAllCategories(): Promise<{ category: string; count: number }[]> {
  if (isApiMode()) {
    const payload = await fetchJson<{ count: number; categories: { category: string; count: number }[] }>(
      '/api/v1/market/categories'
    );
    return payload.categories;
  }

  const skills = await getAllSkills();
  const categoryMap = new Map<string, number>();

  for (const skill of skills) {
    for (const category of skill.categories) {
      categoryMap.set(category, (categoryMap.get(category) || 0) + 1);
    }
  }

  return Array.from(categoryMap.entries())
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count);
}

export async function getAllTags(): Promise<{ tag: string; count: number }[]> {
  if (isApiMode()) {
    const payload = await fetchJson<{ count: number; tags: { tag: string; count: number }[] }>(
      '/api/v1/market/tags'
    );
    return payload.tags;
  }

  const skills = await getAllSkills();
  const tagMap = new Map<string, number>();

  for (const skill of skills) {
    for (const tag of skill.tags) {
      tagMap.set(tag, (tagMap.get(tag) || 0) + 1);
    }
  }

  return Array.from(tagMap.entries())
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count);
}

export async function getBundles(): Promise<BundleSummary[]> {
  if (isApiMode()) {
    const payload = await fetchJson<{ count: number; bundles: BundleSummary[] }>('/api/v1/market/bundles');
    return payload.bundles;
  }

  const [allSkills, bundleFiles] = await Promise.all([
    getAllSkills(),
    fs.readdir(path.join(DATA_ROOT, 'bundles')),
  ]);

  const byId = new Map(allSkills.map((skill) => [skill.id, skill]));
  const bundles: BundleSummary[] = [];

  for (const fileName of bundleFiles.filter((file) => file.endsWith('.json')).sort()) {
    const payload = await readJson<BundleFilePayload>(path.join(DATA_ROOT, 'bundles', fileName));
    bundles.push({
      ...payload,
      skill_count: payload.skills.length,
      path: `bundles/${fileName}`,
      skill_summaries: payload.skills
        .map((skillId) => byId.get(skillId))
        .filter((skill): skill is SkillSummary => Boolean(skill)),
    });
  }

  return bundles;
}

export async function getBundleDetail(bundleId: string): Promise<BundleDetailPayload | null> {
  if (isApiMode()) {
    try {
      return await fetchJson<BundleDetailPayload>(`/api/v1/market/bundles/${bundleId}`);
    } catch {
      return null;
    }
  }

  const bundles = await getBundles();
  const bundle = bundles.find((item) => item.id === bundleId);
  if (!bundle) {
    return null;
  }

  const installSpecs = (
    await Promise.all(bundle.skill_summaries.map((skill) => getInstallSpec(skill.name, skill.version)))
  ).filter((spec): spec is InstallSpec => Boolean(spec));

  return {
    bundle,
    skills: bundle.skill_summaries,
    install_specs: installSpecs,
  };
}

export async function getDocsCatalog(): Promise<DocsCatalog> {
  if (isApiMode()) {
    return fetchJson<DocsCatalog>('/api/v1/docs/catalog');
  }

  const skills = await getAllSkills();
  const skillDocs: DocsCatalogEntry[] = [];

  for (const skill of skills) {
    const markdown = await getSkillDoc(skill.name);
    if (!markdown) {
      continue;
    }

    skillDocs.push({
      id: skill.name,
      kind: 'skill',
      title: firstHeading(markdown, skill.title),
      summary: firstParagraph(markdown) || skill.summary,
      path: `docs/${skill.name}.md`,
    });
  }

  const teachingRoot = path.join(DATA_ROOT, 'docs', 'teaching');
  const teachingDocs: DocsCatalogEntry[] = [];
  for (const fileName of (await fs.readdir(teachingRoot)).filter((file) => file.endsWith('.md')).sort()) {
    const markdown = await fs.readFile(path.join(teachingRoot, fileName), 'utf-8');
    teachingDocs.push({
      id: fileName.replace(/\.md$/, ''),
      kind: 'teaching',
      title: firstHeading(markdown, fileName.replace(/\.md$/, '')),
      summary: firstParagraph(markdown),
      path: `docs/teaching/${fileName}`,
    });
  }

  const skillDocFileNames = new Set(skills.map((skill) => `${skill.name}.md`));
  const docsRoot = path.join(DATA_ROOT, 'docs');
  const projectDocs: DocsCatalogEntry[] = [];
  for (const fileName of (await fs.readdir(docsRoot)).filter((file) => file.endsWith('.md')).sort()) {
    if (fileName === 'README.md' || skillDocFileNames.has(fileName) || isInternalIterationDoc(fileName.replace(/\.md$/, ''))) {
      continue;
    }

    const markdown = await fs.readFile(path.join(docsRoot, fileName), 'utf-8');
    projectDocs.push({
      id: fileName.replace(/\.md$/, ''),
      kind: 'project',
      title: firstHeading(markdown, fileName.replace(/\.md$/, '')),
      summary: firstParagraph(markdown),
      path: `docs/${fileName}`,
    });
  }

  return {
    skill_docs: skillDocs,
    teaching_docs: teachingDocs,
    project_docs: projectDocs,
  };
}

export async function getTeachingDoc(docId: string): Promise<TeachingDocPayload | null> {
  if (isApiMode()) {
    try {
      return await fetchJson<TeachingDocPayload>(`/api/v1/docs/teaching/${docId}`);
    } catch {
      return null;
    }
  }

  const filePath = path.join(DATA_ROOT, 'docs', 'teaching', `${docId}.md`);
  try {
    const markdown = await fs.readFile(filePath, 'utf-8');
    return {
      id: docId,
      kind: 'teaching',
      title: firstHeading(markdown, docId),
      summary: firstParagraph(markdown),
      markdown,
      path: `docs/teaching/${docId}.md`,
    };
  } catch {
    return null;
  }
}

export async function getProjectDoc(docId: string): Promise<ProjectDocPayload | null> {
  if (isInternalIterationDoc(docId)) {
    return null;
  }

  if (isApiMode()) {
    try {
      return await fetchJson<ProjectDocPayload>(`/api/v1/docs/project/${docId}`);
    } catch {
      return null;
    }
  }

  const filePath = path.join(DATA_ROOT, 'docs', `${docId}.md`);
  try {
    const markdown = await fs.readFile(filePath, 'utf-8');
    return {
      id: docId,
      kind: 'project',
      title: firstHeading(markdown, docId),
      summary: firstParagraph(markdown),
      markdown,
      path: `docs/${docId}.md`,
    };
  } catch {
    return null;
  }
}
