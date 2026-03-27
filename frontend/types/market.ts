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

export interface LocalBackendStatus {
  available: boolean;
  configured: boolean;
  message: string;
}

export type LocalJobStatus = 'queued' | 'running' | 'succeeded' | 'failed';

export interface LocalJobRecord {
  job_id: string;
  kind: string;
  status: LocalJobStatus;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  command: string[];
  command_text: string;
  summary: Record<string, unknown>;
  artifacts: Record<string, unknown>;
  request: Record<string, unknown>;
  stdout: string;
  stderr: string;
  exit_code: number | null;
  error: string | null;
}

export interface LocalInstalledSkillRecord {
  skill_id: string;
  skill_name: string;
  publisher: string;
  version: string;
  channel: Channel;
  install_target: string;
  review_status: string;
  lifecycle_status: string;
  install_spec: string;
  provenance_path: string;
  installed_at: string;
  sources: Array<{
    kind: string;
    id: string;
  }>;
}

export interface LocalInstalledBundleRecord {
  bundle_id: string;
  title: string;
  generated_at: string;
  report_path: string;
  target_root: string;
  skill_count: number;
  active_skill_ids: string[];
}

export interface LocalInstalledState {
  target_root: string;
  lock_path: string;
  installed_count: number;
  bundle_count: number;
  installed: LocalInstalledSkillRecord[];
  bundles: LocalInstalledBundleRecord[];
}

export interface LocalInstalledDoctorFinding {
  kind: string;
  severity: string;
  skill_id?: string;
  bundle_id?: string;
  message: string;
}

export interface LocalInstalledDoctorSnapshot {
  generated_at: string;
  target_root: string;
  lock_path: string;
  summary: {
    installed_count: number;
    bundle_count: number;
    doctor_finding_count: number;
    repairable_finding_count: number;
    skipped_finding_count: number;
  };
  counts: {
    channels: Record<string, number>;
    lifecycle_statuses: Record<string, number>;
    source_kinds: Record<string, number>;
    finding_severities: Record<string, number>;
  };
  doctor: {
    target_root: string;
    lock_path: string;
    installed_count: number;
    bundle_report_count: number;
    finding_count: number;
    findings: LocalInstalledDoctorFinding[];
    infos: string[];
  };
  repair_preview: {
    repairable_finding_count: number;
    orphan_directories: string[];
    stale_bundle_reports: Array<{
      bundle_id: string;
      path: string;
      title: string;
    }>;
    skipped_finding_count: number;
    skipped_findings: LocalInstalledDoctorFinding[];
  };
}

export interface LocalInstalledRepairPayload {
  target_root: string;
  dry_run: boolean;
  doctor_finding_count: number;
  repairable_finding_count: number;
  repairable_findings: LocalInstalledDoctorFinding[];
  orphan_directories: string[];
  stale_bundle_reports: Array<{
    bundle_id: string;
    path: string;
    title: string;
  }>;
  skipped_finding_count: number;
  skipped_findings: LocalInstalledDoctorFinding[];
  applied: {
    removed_orphan_directories: string[];
    removed_bundle_reports: string[];
  };
  applied_count: number;
}

export interface LocalInstalledBaselineHistoryEntry {
  sequence: number;
  promoted_at: string;
  target_root: string;
  baseline_path: string;
  baseline_markdown_path: string;
  summary: {
    installed_count: number;
    bundle_count: number;
    doctor_finding_count: number;
    repairable_finding_count: number;
    skipped_finding_count: number;
  };
  replaced_existing_baseline: boolean;
  transition_diff_path: string | null;
  transition_diff_markdown_path: string | null;
  transition_summary_delta: Record<string, { before: number; after: number }>;
  archived_baseline_path: string;
  archived_baseline_markdown_path: string;
  archived_transition_diff_path: string | null;
  archived_transition_diff_markdown_path: string | null;
}

export interface LocalInstalledBaselineState {
  target_root: string;
  snapshots_dir: string;
  baseline_path: string;
  baseline_markdown_path: string;
  history_path: string;
  history_markdown_path: string;
  archive_dir: string;
  baseline_exists: boolean;
  history_exists: boolean;
  history_entry_count: number;
  next_sequence: number;
  current_baseline: {
    generated_at: string;
    target_root: string;
    summary: {
      installed_count: number;
      bundle_count: number;
      doctor_finding_count: number;
      repairable_finding_count: number;
      skipped_finding_count: number;
    };
  } | null;
  latest_entry: LocalInstalledBaselineHistoryEntry | null;
  entries: LocalInstalledBaselineHistoryEntry[];
}

export interface LocalInstalledBaselinePromotePayload {
  baseline_path: string;
  target_root: string;
  replaced_existing_baseline: boolean;
  current_summary: {
    installed_count: number;
    bundle_count: number;
    doctor_finding_count: number;
    repairable_finding_count: number;
    skipped_finding_count: number;
  };
  transition_diff_present: boolean;
  transition_summary_delta: Record<string, { before: number; after: number }>;
  baseline_markdown_path: string;
  transition_diff_path: string | null;
  transition_diff_markdown_path: string | null;
  history_path: string;
  history_markdown_path: string;
  history_entry_count: number;
  archive_dir: string;
}

export interface MarketCommandAction {
  label: string;
  command: string;
  description: string;
  expectedOutcome?: string;
  artifacts?: string[];
  testId?: string;
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

export interface RemoteTrustEntry {
  label: string;
  value: string;
  tone?: 'default' | 'positive' | 'warning' | 'critical';
}

export interface RemoteExecutionTrustSummary {
  title: string;
  entries: RemoteTrustEntry[];
  warnings: string[];
  approval_required: boolean;
  approval_label: string;
  approval_help: string;
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
  prerequisites?: string;
  expectedOutcome?: string;
  artifacts?: string[];
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
