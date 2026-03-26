export type Channel = 'stable' | 'beta' | 'internal';

export interface SkillSummary {
  id: string;
  name: string;
  title: string;
  version: string;
  summary: string;
  categories: string[];
  tags: string[];
  channel: Channel;
  install_spec: string;
  review_status: string;
}

export interface Compatibility {
  codex_min_version: string;
  python: string;
  platforms: ('windows' | 'macos' | 'linux')[];
}

export interface Permissions {
  workspace: 'none' | 'read' | 'write';
  network: 'none' | 'limited' | 'full';
  shell: 'none' | 'limited' | 'full';
  secrets: 'none' | 'read' | 'write';
  human_review_required: boolean;
}

export interface Quality {
  checker: string;
  eval: string;
  review_status: 'draft' | 'reviewed' | 'deprecated';
}

export interface Lifecycle {
  status: 'active' | 'deprecated' | 'blocked' | 'archived';
  replacement_skill_id?: string;
  sunset_at?: string;
  notes?: string;
}

export interface Artifacts {
  source_dir: string;
  entrypoint: string;
  docs: string;
}

export interface SearchInfo {
  keywords: string[];
  related_skills: string[];
}

export interface Distribution {
  capabilities: string[];
  starter_bundle_ids: string[];
}

export interface SkillManifest extends SkillSummary {
  publisher: string;
  description: string;
  compatibility: Compatibility;
  permissions: Permissions;
  quality: Quality;
  lifecycle: Lifecycle;
  artifacts: Artifacts;
  search: SearchInfo;
  distribution: Distribution;
}

export interface InstallSpec {
  skill_id: string;
  skill_name: string;
  version: string;
  channel: Channel;
  package_type: string;
  package_path: string;
  checksum_sha256: string;
  entrypoint: string;
  install_target: string;
}

export interface ChannelIndex {
  channel: Channel;
  generated_at: string;
  skills: SkillSummary[];
}

export interface MarketIndex {
  generated_at: string;
  channels: {
    [key in Channel]: {
      count: number;
      path: string;
    };
  };
}

export interface Bundle {
  id: string;
  title: string;
  summary: string;
  description: string;
  status: 'draft' | 'published';
  channels: Channel[];
  skills: string[];
  use_cases: string[];
  keywords: string[];
}

export interface BundleSummary extends Bundle {
  skill_count: number;
  path: string;
  skill_summaries: SkillSummary[];
}

export interface BundleDetailPayload {
  bundle: BundleSummary;
  skills: SkillSummary[];
  install_specs: InstallSpec[];
}

export interface SkillDetailPayload {
  manifest: SkillManifest;
  install_spec: InstallSpec | null;
  doc_markdown: string | null;
  related_skills: SkillSummary[];
}

export interface DocsCatalogEntry {
  id: string;
  kind: 'skill' | 'teaching' | 'project';
  title: string;
  summary: string;
  path: string;
}

export interface DocsCatalog {
  skill_docs: DocsCatalogEntry[];
  teaching_docs: DocsCatalogEntry[];
  project_docs: DocsCatalogEntry[];
  all_docs: DocsCatalogEntry[];
}

export interface TeachingDocPayload extends DocsCatalogEntry {
  markdown: string;
}

export interface ProjectDocPayload extends DocsCatalogEntry {
  markdown: string;
}

export interface DocActionCommand {
  label: string;
  command: string;
  testId?: string;
}

export interface DocActionLink {
  label: string;
  href: string;
  testId?: string;
}

export interface DocActionPanelData {
  title: string;
  description: string;
  commands: DocActionCommand[];
  links: DocActionLink[];
}
