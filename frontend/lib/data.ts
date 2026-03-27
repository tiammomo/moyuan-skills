import fs from 'fs/promises';
import path from 'path';
import type {
  BundleDetailPayload,
  BundleSummary,
  Channel,
  ChannelIndex,
  DocsCatalog,
  DocsCatalogEntry,
  DocActionCommand,
  DocActionLink,
  DocActionPanelData,
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
const DOC_STOPWORDS = new Set([
  'a',
  'an',
  'and',
  'docs',
  'doc',
  'documentation',
  'for',
  'from',
  'guide',
  'how',
  'in',
  'into',
  'market',
  'moyuan',
  'of',
  'project',
  'repo',
  'skill',
  'skills',
  'teaching',
  'the',
  'to',
  'with',
]);

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

function normalizeDocSearchText(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function tokenizeDocSearchText(value: string): string[] {
  return normalizeDocSearchText(value)
    .split(/\s+/)
    .filter((token) => token.length > 2 && !DOC_STOPWORDS.has(token));
}

function docSearchText(doc: DocsCatalogEntry): string {
  return `${doc.title} ${doc.summary} ${doc.path} ${doc.kind}`;
}

function dedupeCommands(commands: DocActionCommand[]): DocActionCommand[] {
  const seen = new Set<string>();
  const result: DocActionCommand[] = [];
  for (const command of commands) {
    const key = `${command.label}:${command.command}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    result.push(command);
  }
  return result;
}

function dedupeLinks(links: DocActionLink[]): DocActionLink[] {
  const seen = new Set<string>();
  const result: DocActionLink[] = [];
  for (const link of links) {
    const key = `${link.label}:${link.href}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    result.push(link);
  }
  return result;
}

function getDocFamilyDocs(docsCatalog: DocsCatalog, kind: DocsCatalogEntry['kind']): DocsCatalogEntry[] {
  if (kind === 'skill') {
    return docsCatalog.skill_docs;
  }
  if (kind === 'teaching') {
    return docsCatalog.teaching_docs;
  }
  return docsCatalog.project_docs;
}

export function getDocNeighbors(
  currentDoc: DocsCatalogEntry,
  docsCatalog: DocsCatalog
): {
  previous: DocsCatalogEntry | null;
  next: DocsCatalogEntry | null;
  position: number;
  total: number;
} {
  const familyDocs = getDocFamilyDocs(docsCatalog, currentDoc.kind);
  const currentIndex = familyDocs.findIndex((doc) => doc.id === currentDoc.id);

  if (currentIndex === -1) {
    return {
      previous: null,
      next: null,
      position: 0,
      total: familyDocs.length,
    };
  }

  return {
    previous: familyDocs[currentIndex - 1] ?? null,
    next: familyDocs[currentIndex + 1] ?? null,
    position: currentIndex + 1,
    total: familyDocs.length,
  };
}

function getFallbackNeighborDocs(currentDoc: DocsCatalogEntry, docsCatalog: DocsCatalog): DocsCatalogEntry[] {
  const familyDocs = getDocFamilyDocs(docsCatalog, currentDoc.kind);
  const currentIndex = familyDocs.findIndex((doc) => doc.id === currentDoc.id);

  if (currentIndex === -1) {
    return [];
  }

  const neighbors: DocsCatalogEntry[] = [];
  for (let offset = 1; offset < familyDocs.length; offset += 1) {
    const nextDoc = familyDocs[currentIndex + offset];
    const previousDoc = familyDocs[currentIndex - offset];

    if (nextDoc) {
      neighbors.push(nextDoc);
    }
    if (previousDoc) {
      neighbors.push(previousDoc);
    }
  }

  return neighbors;
}

function scoreRelatedDoc(
  currentDoc: DocsCatalogEntry,
  candidate: DocsCatalogEntry,
  currentTokens: Set<string>,
  preferredIds: Set<string>
): number {
  let score = 0;

  if (preferredIds.has(candidate.id) && candidate.kind === 'skill') {
    score += 100;
  }

  if (candidate.kind === currentDoc.kind) {
    score += 20;
  }

  const candidateTokens = tokenizeDocSearchText(docSearchText(candidate));
  let sharedTokenCount = 0;
  for (const token of candidateTokens) {
    if (currentTokens.has(token)) {
      sharedTokenCount += 1;
    }
  }
  score += sharedTokenCount * 5;

  return score;
}

export function getDocHref(doc: DocsCatalogEntry): string {
  if (doc.kind === 'skill') {
    return `/docs/${doc.id}`;
  }
  if (doc.kind === 'teaching') {
    return `/docs/teaching/${doc.id}`;
  }
  return `/docs/project/${doc.id}`;
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
    all_docs: [...skillDocs, ...teachingDocs, ...projectDocs].sort((a, b) =>
      a.title.localeCompare(b.title) || a.id.localeCompare(b.id)
    ),
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

export async function getRelatedDocs(
  currentDoc: DocsCatalogEntry,
  options?: { limit?: number; preferredIds?: string[] }
): Promise<DocsCatalogEntry[]> {
  const limit = options?.limit ?? 4;
  const preferredIds = new Set(options?.preferredIds ?? []);
  const docsCatalog = await getDocsCatalog();
  const currentTokens = new Set(tokenizeDocSearchText(docSearchText(currentDoc)));
  const selected = new Set<string>();
  const results: DocsCatalogEntry[] = [];

  const scoredDocs = docsCatalog.all_docs
    .filter((doc) => !(doc.kind === currentDoc.kind && doc.id === currentDoc.id))
    .map((doc) => ({
      doc,
      score: scoreRelatedDoc(currentDoc, doc, currentTokens, preferredIds),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || a.doc.title.localeCompare(b.doc.title) || a.doc.id.localeCompare(b.doc.id));

  for (const item of scoredDocs) {
    const key = `${item.doc.kind}:${item.doc.id}`;
    if (selected.has(key)) {
      continue;
    }
    selected.add(key);
    results.push(item.doc);
    if (results.length >= limit) {
      return results;
    }
  }

  for (const doc of getFallbackNeighborDocs(currentDoc, docsCatalog)) {
    const key = `${doc.kind}:${doc.id}`;
    if (selected.has(key)) {
      continue;
    }
    selected.add(key);
    results.push(doc);
    if (results.length >= limit) {
      return results;
    }
  }

  for (const doc of docsCatalog.all_docs) {
    const key = `${doc.kind}:${doc.id}`;
    if ((doc.kind === currentDoc.kind && doc.id === currentDoc.id) || selected.has(key)) {
      continue;
    }
    selected.add(key);
    results.push(doc);
    if (results.length >= limit) {
      break;
    }
  }

  return results;
}

export function getSkillDocActionPanel(
  skillName: string,
  detail: SkillDetailPayload | null,
  options?: { channelHref?: string }
): DocActionPanelData {
  const version = detail?.manifest.version ?? 'latest';
  const installSpecPath = `dist/market/install/${skillName}-${version}.json`;

  return {
    title: 'Run this skill',
    description:
      'Use these commands to install, validate, and evaluate the current skill without leaving the doc detail page.',
    commands: dedupeCommands([
      {
        label: 'Install locally',
        command: `python scripts/skills_market.py install ${installSpecPath} --target-root dist/installed-skills`,
        prerequisites: 'Generate the install spec first and run the command from the repo root.',
        expectedOutcome: 'The skill installs into dist/installed-skills and the local lockfile records the new entry.',
        artifacts: [
          'Updated dist/installed-skills/skills.lock.json entry for the installed skill',
          `Installed skill files under dist/installed-skills/${skillName}/`,
        ],
        testId: 'doc-action-skill-install',
      },
      {
        label: 'Run checker',
        command: detail?.manifest.quality.checker ?? `python skills/${skillName}/scripts/check_${skillName.replace(/-/g, '_')}.py`,
        prerequisites: 'Keep the repo checkout intact so the skill assets and sample inputs are available.',
        expectedOutcome: `${detail?.manifest.title ?? skillName} checker finishes with a passed status and no structural errors.`,
        artifacts: ['Checker pass/fail summary printed in the terminal output'],
        testId: 'doc-action-skill-checker',
      },
      {
        label: 'Run eval',
        command: detail?.manifest.quality.eval ?? `python scripts/run_eval_harness.py --skills ${skillName}`,
        prerequisites: 'Make sure the eval fixtures and baseline files are present in examples/eval-harness.',
        expectedOutcome: 'The eval harness reports the targeted cases as passed without a regression warning.',
        artifacts: ['Eval pass/fail summary and grader results printed in the terminal output'],
        testId: 'doc-action-skill-eval',
      },
    ]),
    links: dedupeLinks([
      { href: '/docs/project/repo-commands', label: 'Open repo command reference', testId: 'doc-action-skill-repo-commands' },
      { href: `/skills/${skillName}`, label: 'Open market skill page', testId: 'doc-action-skill-market-page' },
      ...(options?.channelHref ? [{ href: options.channelHref, label: 'Inspect this release channel' }] : []),
    ]),
  };
}

export function getTeachingDocActionPanel(doc: DocsCatalogEntry): DocActionPanelData {
  const id = doc.id;
  const commands: DocActionCommand[] = [];

  if (
    id.includes('build') ||
    id.includes('skill-author') ||
    id.includes('learner') ||
    id.includes('read-the-repo')
  ) {
    commands.push(
      {
        label: 'Check progressive structure',
        command: 'python scripts/check_progressive_skills.py',
        prerequisites: 'Run from the repo root so the checker can scan docs, templates, and skill bundles together.',
        expectedOutcome: 'Progressive skill validation passes, confirming the teaching flow still matches repo conventions.',
        artifacts: ['Repository-wide structural validation summary in terminal output'],
        testId: 'doc-action-teaching-primary',
      },
      {
        label: 'Run build-skills checker',
        command: 'python skills/build-skills/scripts/check_build_skills.py',
        prerequisites: 'Keep the teaching bundle assets in place under skills/build-skills/.',
        expectedOutcome: 'The build-skills teaching bundle check passes for the current lesson assets.',
        artifacts: ['build-skills checker summary in terminal output'],
        testId: 'doc-action-teaching-secondary',
      }
    );
  } else if (id.includes('progressive-disclosure')) {
    commands.push(
      {
        label: 'Check progressive structure',
        command: 'python scripts/check_progressive_skills.py',
        prerequisites: 'Run from the repo root so the checker can compare the disclosure assets against repo conventions.',
        expectedOutcome: 'Progressive skill validation passes before you verify the disclosure-specific example.',
        artifacts: ['Repository-wide structural validation summary in terminal output'],
        testId: 'doc-action-teaching-primary',
      },
      {
        label: 'Run progressive-disclosure checker',
        command: 'python skills/progressive-disclosure/scripts/check_progressive_disclosure.py',
        prerequisites: 'Keep the progressive-disclosure teaching files and reference splits available in the repo.',
        expectedOutcome: 'The progressive-disclosure teaching bundle check passes for the current split-context assets.',
        artifacts: ['progressive-disclosure checker summary in terminal output'],
        testId: 'doc-action-teaching-secondary',
      }
    );
  } else if (id.includes('harness') || id.includes('evals-and-prototypes')) {
    commands.push(
      {
        label: 'Check harness prototypes',
        command: 'python scripts/check_harness_prototypes.py',
        prerequisites: 'Leave the prototype schemas, examples, and templates in their default repo locations.',
        expectedOutcome: 'Harness prototype validation passes, confirming schemas and runtime blueprints still line up.',
        artifacts: ['Prototype validation summary in terminal output'],
        testId: 'doc-action-teaching-primary',
      },
      {
        label: 'Run harness runtime',
        command:
          'python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml',
        prerequisites: 'Start from the repo root so the runtime can resolve the referenced blueprint and sample assets.',
        expectedOutcome: 'The runtime demo completes with PASS for the release-note-publication blueprint.',
        artifacts: ['Runtime execution report emitted under the command-selected dist output directory'],
        testId: 'doc-action-teaching-secondary',
      }
    );
  } else if (id.includes('market') || id.includes('registry') || id.includes('project-learning-roadmap')) {
    commands.push(
      {
        label: 'Run market smoke',
        command: 'python scripts/check_market_pipeline.py',
        prerequisites: 'Keep dist/, governance/, and market packaging scripts available in the current repo checkout.',
        expectedOutcome: 'The market pipeline smoke test passes, including packaging, indexing, install, and governance checks.',
        artifacts: ['Smoke output directory under dist/market-smoke-* plus terminal summary'],
        testId: 'doc-action-teaching-primary',
      },
      {
        label: 'Check frontend/backend integration',
        command: 'python scripts/check_python_market_backend.py',
        prerequisites: 'Install backend dependencies and keep the generated market assets available under dist/market.',
        expectedOutcome: 'The Python market backend check passes for the repo-backed API payloads.',
        artifacts: ['Backend payload-count summary printed in terminal output'],
        testId: 'doc-action-teaching-secondary',
      }
    );
  } else {
    commands.push(
      {
        label: 'Check progressive structure',
        command: 'python scripts/check_progressive_skills.py',
        prerequisites: 'Run from the repo root so docs, templates, and skills are checked together.',
        expectedOutcome: 'Progressive skill validation passes so the lesson can build on a clean repo state.',
        artifacts: ['Repository-wide structural validation summary in terminal output'],
        testId: 'doc-action-teaching-primary',
      },
      {
        label: 'Check docs links',
        command: 'python scripts/check_docs_links.py',
        prerequisites: 'Keep the docs tree and relative markdown links in their repo locations.',
        expectedOutcome: 'Documentation link checking passes with no broken relative links.',
        artifacts: ['Docs link validation summary in terminal output'],
        testId: 'doc-action-teaching-secondary',
      }
    );
  }

  return {
    title: 'Try the learning step',
    description:
      'These commands give you one concrete practice step so the teaching doc turns into a hands-on path instead of a passive note.',
    commands: dedupeCommands(commands),
    links: dedupeLinks([
      { href: '/docs/project/repo-commands', label: 'Open repo command reference', testId: 'doc-action-teaching-repo-commands' },
      { href: '/docs/teaching', label: 'Back to teaching library', testId: 'doc-action-teaching-library' },
    ]),
  };
}

export function getProjectDocActionPanel(doc: DocsCatalogEntry): DocActionPanelData {
  const id = doc.id;
  const commands: DocActionCommand[] = [];

  if (id === 'frontend-backend-integration') {
    commands.push(
      {
        label: 'Check backend repository layer',
        command: 'python scripts/check_python_market_backend.py',
        prerequisites: 'Install backend dependencies and keep the repo-backed market assets available under dist/market.',
        expectedOutcome: 'The Python market backend check passes and confirms the API payloads still match repo assets.',
        artifacts: ['Backend payload-count summary printed in terminal output'],
        testId: 'doc-action-project-primary',
      },
      {
        label: 'Run frontend end-to-end check',
        command: 'npm run e2e --prefix frontend',
        prerequisites: 'Install frontend dependencies and build the Next.js app before starting the Playwright run.',
        expectedOutcome: 'Playwright reports the full-stack market flow as passed against the live frontend and backend.',
        artifacts: ['Playwright pass/fail report printed in terminal output'],
        testId: 'doc-action-project-secondary',
      }
    );
  } else if (id === 'dev-setup') {
    commands.push(
      {
        label: 'Compile backend',
        command: 'python -m compileall backend',
        prerequisites: 'Have a working Python interpreter available from the repo root.',
        expectedOutcome: 'Python compiles the backend package tree without syntax errors.',
        artifacts: ['Compiled bytecode under backend/__pycache__/ and nested package cache directories'],
        testId: 'doc-action-project-primary',
      },
      {
        label: 'Build frontend',
        command: 'npm run build --prefix frontend',
        prerequisites: 'Install the frontend npm dependencies before running the build.',
        expectedOutcome: 'Next.js finishes a production build without type or route-generation failures.',
        artifacts: ['Production build artifacts under frontend/.next/'],
        testId: 'doc-action-project-secondary',
      }
    );
  } else if (id === 'repo-commands') {
    commands.push(
      {
        label: 'Check progressive structure',
        command: 'python scripts/check_progressive_skills.py',
        prerequisites: 'Run from the repo root so the checker can inspect every skill and doc family together.',
        expectedOutcome: 'Progressive skill validation passes before you verify the rest of the repository references.',
        artifacts: ['Repository-wide structural validation summary in terminal output'],
        testId: 'doc-action-project-primary',
      },
      {
        label: 'Check docs links',
        command: 'python scripts/check_docs_links.py',
        prerequisites: 'Keep the markdown docs and templates in place so relative links resolve correctly.',
        expectedOutcome: 'Documentation link checking passes with no broken repo references.',
        artifacts: ['Docs link validation summary in terminal output'],
        testId: 'doc-action-project-secondary',
      }
    );
  } else if (
    id.includes('market') ||
    id.includes('consumer-guide') ||
    id.includes('publisher-guide')
  ) {
    commands.push(
      {
        label: 'Validate market manifests',
        command: 'python scripts/validate_market_manifest.py',
        prerequisites: 'Keep the skill market manifests and schema files present in their default repo locations.',
        expectedOutcome: 'Market manifest validation passes for all packaged skills in the repo.',
        artifacts: ['Manifest validation summary in terminal output'],
        testId: 'doc-action-project-primary',
      },
      {
        label: 'Run market smoke',
        command: 'python scripts/check_market_pipeline.py',
        prerequisites: 'Leave the dist/, governance/, bundle, and market script directories available to the smoke run.',
        expectedOutcome: 'The market smoke run completes successfully across packaging, install, and governance checkpoints.',
        artifacts: ['Smoke output directory under dist/market-smoke-* plus terminal summary'],
        testId: 'doc-action-project-secondary',
      }
    );
  } else if (id.includes('harness')) {
    commands.push(
      {
        label: 'Check harness prototypes',
        command: 'python scripts/check_harness_prototypes.py',
        prerequisites: 'Keep the prototype examples, schemas, and templates available from the repo root.',
        expectedOutcome: 'Harness prototype validation passes for schemas, examples, and runtime assets.',
        artifacts: ['Prototype validation summary in terminal output'],
        testId: 'doc-action-project-primary',
      },
      {
        label: 'Run harness runtime',
        command:
          'python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml',
        prerequisites: 'Run from the repo root so the runtime can resolve the blueprint and sample artifacts.',
        expectedOutcome: 'The harness runtime demo ends in PASS and writes the expected runtime report artifacts.',
        artifacts: ['Runtime execution report emitted under the command-selected dist output directory'],
        testId: 'doc-action-project-secondary',
      }
    );
  } else {
    commands.push(
      {
        label: 'Check docs links',
        command: 'python scripts/check_docs_links.py',
        prerequisites: 'Keep the docs tree in place so the relative markdown links can be resolved.',
        expectedOutcome: 'Documentation link checking passes, confirming the reference is still safe to share.',
        artifacts: ['Docs link validation summary in terminal output'],
        testId: 'doc-action-project-primary',
      },
      {
        label: 'Check progressive structure',
        command: 'python scripts/check_progressive_skills.py',
        prerequisites: 'Run from the repo root so the structural checks can inspect the full teaching and skill set.',
        expectedOutcome: 'Progressive skill validation passes so the wider repo remains structurally consistent.',
        artifacts: ['Repository-wide structural validation summary in terminal output'],
        testId: 'doc-action-project-secondary',
      }
    );
  }

  return {
    title: 'Take the next step',
    description:
      'Use these commands to turn the current project reference into a concrete maintenance or verification action.',
    commands: dedupeCommands(commands),
    links: dedupeLinks([
      { href: '/docs/project/repo-commands', label: 'Open repo command reference', testId: 'doc-action-project-repo-commands' },
      { href: '/docs', label: 'Back to docs center', testId: 'doc-action-project-docs-center' },
    ]),
  };
}
