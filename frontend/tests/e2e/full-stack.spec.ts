import { execFile } from 'node:child_process';
import { promises as fs } from 'node:fs';
import * as path from 'node:path';
import { promisify } from 'node:util';
import { expect, test } from '@playwright/test';

const repoRoot = path.resolve(process.cwd(), '..');
const execFileAsync = promisify(execFile);

test.setTimeout(120_000);

test('frontend works against the Python backend across core market flows', async ({ page }) => {
  const skillTargetRoot = path.join(repoRoot, 'dist', 'frontend-local-execution', 'skills', 'release-note-writer');
  const bundleTargetRoot = path.join(repoRoot, 'dist', 'frontend-local-execution', 'bundles', 'release-engineering-starter');
  const remoteSkillTargetRoot = path.join(repoRoot, 'dist', 'frontend-remote-execution', 'skills', 'release-note-writer');
  const remoteBundleTargetRoot = path.join(repoRoot, 'dist', 'frontend-remote-execution', 'bundles', 'release-engineering-starter');
  const remoteCacheRoot = path.join(repoRoot, 'dist', 'frontend-remote-execution', 'cache');
  await fs.rm(skillTargetRoot, { recursive: true, force: true });
  await fs.rm(bundleTargetRoot, { recursive: true, force: true });
  await fs.rm(remoteSkillTargetRoot, { recursive: true, force: true });
  await fs.rm(remoteBundleTargetRoot, { recursive: true, force: true });
  await fs.rm(remoteCacheRoot, { recursive: true, force: true });

  await page.goto('/');

  await expect(page.locator('[data-testid^="skill-card-"]').first()).toBeVisible();

  await page.goto('/skills');
  await page.getByTestId('skill-search-input').fill('release');
  await expect(page.locator('[data-testid="skill-card-release-note-writer"]')).toBeVisible();

  await Promise.all([
    page.waitForURL(/\/skills\/release-note-writer$/),
    page.locator('[data-testid="skill-card-release-note-writer"]').first().click(),
  ]);
  await expect(page.getByTestId('install-command-mode-note')).toContainText('Copy install command');
  await expect(page.getByTestId('install-command-honesty-note')).toContainText(
    'Use the backend execution panel'
  );
  await expect(page.getByTestId('install-command')).toContainText('release-note-writer-0.1.0.json');
  await expect(page.getByTestId('install-command-copy')).toContainText('Copy install command');
  await expect(page.getByTestId('skill-backend-execution')).toBeVisible();
  await expect(page.getByTestId('skill-backend-execution-availability')).toContainText('Backend execution is ready');
  await page.getByTestId('skill-backend-execution-run').click();
  await expect(page.getByTestId('skill-backend-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('skill-backend-execution-summary')).toContainText('release-note-writer');
  await expect(page.getByTestId('skill-installed-state')).toBeVisible();
  await page.getByTestId('skill-installed-state-refresh').click();
  await expect(page.getByTestId('skill-installed-state-status')).toContainText('Installed in target root', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-summary')).toContainText('release-note-writer');
  await expect(page.getByTestId('skill-installed-state-baseline-status')).toContainText('No baseline yet');
  await expect(page.getByTestId('skill-installed-state-baseline-capture')).toBeDisabled();
  const staleBundleReport = path.join(skillTargetRoot, 'bundle-reports', 'stale-bundle.json');
  await fs.mkdir(path.join(skillTargetRoot, 'orphan-skill'), { recursive: true });
  await fs.mkdir(path.dirname(staleBundleReport), { recursive: true });
  await fs.writeFile(
    staleBundleReport,
    JSON.stringify(
      {
        bundle_id: 'stale-bundle',
        title: 'Stale bundle',
        generated_at: '2026-03-27T00:00:00+00:00',
        results: [
          {
            skill_id: 'moyuan.release-note-writer',
            status: 'installed',
          },
        ],
      },
      null,
      2
    ) + '\n',
    'utf-8'
  );
  await page.getByTestId('skill-installed-state-doctor-run').click();
  await expect(page.getByTestId('skill-installed-state-doctor-status')).toContainText('Repairable drift', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-doctor-orphan-directories')).toContainText('orphan-skill');
  await expect(page.getByTestId('skill-installed-state-doctor-stale-bundle-reports')).toContainText('stale-bundle');
  await page.getByTestId('skill-installed-state-doctor-repair').click();
  await expect(page.getByTestId('skill-installed-state-doctor-repair-summary')).toContainText('Applied changes', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-doctor-status')).toContainText('Healthy', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-baseline-capture')).toBeEnabled();
  await page.getByTestId('skill-installed-state-baseline-capture').click();
  await expect(page.getByTestId('skill-installed-state-baseline-capture-summary')).toContainText('History entries', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-baseline-status')).toContainText('Baseline recorded', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-baseline-summary')).toContainText('baseline-history.json');
  await expect(page.getByTestId('skill-installed-state-baseline-history')).toContainText('#1');
  await expect(page.getByTestId('skill-installed-state-governance-status')).toContainText(
    'Governance review pending'
  );
  await page.getByTestId('skill-installed-state-governance-refresh').click();
  await expect(page.getByTestId('skill-installed-state-governance-refresh-summary')).toContainText(
    'source-reconcile-review-handoff',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-governance-status')).toContainText(
    'Governance summary available',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-governance-audit')).toContainText('Audit findings');
  await expect(page.getByTestId('skill-installed-state-governance-gate')).toContainText(
    'Source Reconcile Review Handoff'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-status')).toContainText(
    'Apply handoff not prepared',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-summary')).toBeVisible({
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-waiver-apply-prepare')).toBeEnabled({
    timeout: 20000,
  });
  await page
    .getByTestId('skill-installed-state-waiver-apply-prepare')
    .evaluate((element: HTMLButtonElement) => element.click());
  await expect(page.getByTestId('skill-installed-state-waiver-apply-prepare-summary')).toContainText(
    'needs_execution',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-status')).toContainText(
    'Apply handoff prepared',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-handoff-status')).toContainText(
    'Write handoff pending',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-actions')).toContainText('retarget_or_remove');
  await expect(page.getByTestId('skill-installed-state-waiver-apply-follow-ups')).toContainText(
    'Write approved governance changes'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-stage')).toBeEnabled({
    timeout: 20000,
  });
  await page.getByTestId('skill-installed-state-waiver-apply-stage').click();
  await expect(page.getByTestId('skill-installed-state-waiver-apply-stage-summary')).toContainText('Stage refreshed', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-waiver-apply-status')).toContainText(
    'Staged apply verified',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-handoff-status')).toContainText(
    'Ready for CLI write',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-command')).toContainText(
    'execute_source_reconcile_gate_waiver_apply.py'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-command')).toContainText('--write');
  await expect(page.getByTestId('skill-installed-state-waiver-apply-verify-command')).toContainText(
    'verify_source_reconcile_gate_waiver_apply.py'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-handoff-sources')).toContainText(
    'governance'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-evidence-summary')).toContainText(
    'ready to support an explicit CLI write approval'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-actions')).toContainText(
    'matches_staged_target'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-approval-checkbox')).toBeEnabled({
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-approval-state')).toContainText(
    'Waiting for explicit approval capture',
    {
      timeout: 20000,
    }
  );
  await page.getByTestId('skill-installed-state-waiver-apply-write-approval-checkbox').check();
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-approval-state')).toContainText(
    'Approval captured in this browser',
    {
      timeout: 20000,
    }
  );

  const baselineHistoryPath = path.join(skillTargetRoot, 'snapshots', 'baseline-history.json');
  const waiverApplyDir = path.join(skillTargetRoot, 'snapshots', 'governance', 'waiver-apply');
  const applyExecuteSummaryPath = path.join(
    waiverApplyDir,
    'source-reconcile-gate-waiver-apply-execute-summary.json'
  );
  const governanceWriteMirrorRoot = path.join(skillTargetRoot, 'governance-write-root');
  const governanceWriteMirrorRootDisplay = path.relative(repoRoot, governanceWriteMirrorRoot).split(path.sep).join('/');
  await fs.rm(governanceWriteMirrorRoot, { recursive: true, force: true });
  await fs.mkdir(governanceWriteMirrorRoot, { recursive: true });
  await fs.cp(path.join(repoRoot, 'governance'), path.join(governanceWriteMirrorRoot, 'governance'), {
    recursive: true,
  });

  await execFileAsync(
    'python',
    [
      'scripts/execute_source_reconcile_gate_waiver_apply.py',
      baselineHistoryPath,
      '--output-dir',
      waiverApplyDir,
      '--target-root',
      governanceWriteMirrorRoot,
      '--write',
      '--json',
    ],
    {
      cwd: repoRoot,
      encoding: 'utf-8',
      windowsHide: true,
    }
  );
  await execFileAsync(
    'python',
    [
      'scripts/verify_source_reconcile_gate_waiver_apply.py',
      baselineHistoryPath,
      '--output-dir',
      waiverApplyDir,
      '--target-root',
      governanceWriteMirrorRoot,
      '--apply-execute-summary-path',
      applyExecuteSummaryPath,
      '--json',
    ],
    {
      cwd: repoRoot,
      encoding: 'utf-8',
      windowsHide: true,
    }
  );
  await execFileAsync(
    'python',
    [
      'scripts/report_source_reconcile_gate_waiver_apply.py',
      baselineHistoryPath,
      '--output-dir',
      waiverApplyDir,
      '--target-root',
      governanceWriteMirrorRoot,
      '--apply-execute-summary-path',
      applyExecuteSummaryPath,
      '--json',
    ],
    {
      cwd: repoRoot,
      encoding: 'utf-8',
      windowsHide: true,
    }
  );

  await page.getByTestId('skill-installed-state-waiver-apply-reload').click();
  await expect(page.getByTestId('skill-installed-state-waiver-apply-status')).toContainText(
    'Written apply verified',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-handoff-status')).toContainText(
    'CLI write already verified',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-evidence')).toContainText(
    'Post-write evidence ready'
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-evidence-summary')).toContainText(
    'recorded 1 written change',
    {
      timeout: 20000,
    }
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-evidence')).toContainText(
    governanceWriteMirrorRootDisplay
  );
  await expect(page.getByTestId('skill-installed-state-waiver-apply-write-approval-state')).toContainText(
    'Approval captured in this browser',
    {
      timeout: 20000,
    }
  );
  await page.getByTestId('skill-remove-execution-run').click();
  await expect(page.getByTestId('skill-remove-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('skill-installed-state-status')).toContainText('Not installed yet', {
    timeout: 20000,
  });
  await expect(page.getByTestId('skill-registry-execution')).toBeVisible();
  await expect(page.getByTestId('skill-registry-execution-trust')).toContainText(
    'Moyuan Skills Team (official verified)'
  );
  await expect(page.getByTestId('skill-registry-execution-policy-gate-state')).toContainText(
    /Ready|Needs review/
  );
  await expect(page.getByTestId('skill-registry-execution-approval-state')).toContainText(
    'Waiting for explicit approval'
  );
  await expect(page.getByTestId('skill-registry-execution-run')).toBeDisabled();
  await page.getByTestId('skill-registry-execution-field-registry_url').fill('http://127.0.0.1:38766');
  await page.getByTestId('skill-registry-execution-approval-checkbox').check();
  await expect(page.getByTestId('skill-registry-execution-approval-state')).toContainText(
    'Approval captured for remote execution'
  );
  await page.getByTestId('skill-registry-execution-run').click();
  await expect(page.getByTestId('skill-registry-execution-status')).toContainText('Failed', { timeout: 20000 });
  await expect(page.getByTestId('skill-registry-execution-recovery-kind')).toContainText('download');
  await expect(page.getByTestId('skill-registry-execution-recovery-summary')).toContainText(
    'could not resolve or download'
  );
  await expect(page.getByTestId('skill-registry-execution-retry')).toBeVisible();
  await expect(page.getByTestId('skill-registry-execution-cleanup')).toBeVisible();
  await expect(page.getByTestId('skill-registry-execution-rollback')).toBeVisible();
  await page.getByTestId('skill-registry-execution-cleanup').click();
  await expect(page.getByTestId('skill-registry-execution-cleanup-status')).toContainText('Succeeded', {
    timeout: 20000,
  });
  await page.getByTestId('skill-registry-execution-field-registry_url').fill('http://127.0.0.1:38765');
  await page.getByTestId('skill-registry-execution-retry').click();
  await expect(page.getByTestId('skill-registry-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('skill-registry-execution-summary')).toContainText('moyuan.release-note-writer');
  await expect(page.getByTestId('skill-registry-execution-summary')).toContainText('http://127.0.0.1:38765');
  await expect(await fs.stat(remoteSkillTargetRoot).then(() => true).catch(() => false)).toBeTruthy();
  await page.getByTestId('skill-registry-execution-field-registry_url').fill('http://127.0.0.1:38766');
  await page.getByTestId('skill-registry-execution-run').click();
  await expect(page.getByTestId('skill-registry-execution-status')).toContainText('Failed', { timeout: 20000 });
  await page.getByTestId('skill-registry-execution-rollback').click();
  await expect(page.getByTestId('skill-registry-execution-rollback-status')).toContainText('Succeeded', {
    timeout: 20000,
  });
  await expect(await fs.stat(remoteSkillTargetRoot).then(() => true).catch(() => false)).toBeFalsy();
  await expect(await fs.stat(remoteCacheRoot).then(() => true).catch(() => false)).toBeFalsy();
  await page.getByTestId('skill-registry-execution-field-registry_url').fill('http://127.0.0.1:38765');
  await page.getByTestId('skill-registry-execution-retry').click();
  await expect(page.getByTestId('skill-registry-execution-status')).toContainText('Succeeded', { timeout: 20000 });

  await page.goto('/skills/harness-engineering');
  await expect(page.getByTestId('skill-registry-execution-policy-gate-state')).toContainText('Blocked');
  await expect(page.getByTestId('skill-registry-execution-policy-gate-summary')).toContainText(
    'Lifecycle status is archived'
  );
  await expect(page.getByTestId('skill-registry-execution-policy-gate-blocked')).toContainText(
    'Remote execution stays disabled'
  );
  await page.getByTestId('skill-registry-execution-field-registry_url').fill('http://127.0.0.1:38765');
  await expect(page.getByTestId('skill-registry-execution-run')).toBeDisabled();
  await expect(page.getByTestId('skill-registry-execution-dry-run')).toBeDisabled();

  await page.goto('/bundles');
  await expect(page.getByTestId('bundle-card-release-engineering-starter')).toBeVisible();
  await Promise.all([
    page.waitForURL(/\/bundles\/release-engineering-starter$/),
    page.getByTestId('bundle-link-release-engineering-starter').click(),
  ]);
  await expect(page.getByTestId('bundle-local-command-panel')).toBeVisible();
  await expect(page.getByTestId('bundle-action-install')).toContainText(
    'python scripts/skills_market.py install-bundle release-engineering-starter'
  );
  await expect(page.getByTestId('bundle-action-update')).toContainText(
    'python scripts/skills_market.py update-bundle release-engineering-starter'
  );
  await expect(page.getByTestId('bundle-action-remove')).toContainText(
    'python scripts/skills_market.py remove-bundle release-engineering-starter'
  );
  await expect(page.getByTestId('install-command').first()).toContainText('release-note-writer-0.1.0.json');
  await expect(page.getByTestId('bundle-backend-execution')).toBeVisible();
  await expect(page.getByTestId('bundle-backend-execution-availability')).toContainText('Backend execution is ready');
  await page.getByTestId('bundle-backend-execution-run').click();
  await expect(page.getByTestId('bundle-backend-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('bundle-backend-execution-summary')).toContainText('release-engineering-starter');
  await expect(page.getByTestId('bundle-installed-state')).toBeVisible();
  await page.getByTestId('bundle-installed-state-refresh').click();
  await expect(page.getByTestId('bundle-installed-state-status')).toContainText('Installed in target root', {
    timeout: 20000,
  });
  await expect(page.getByTestId('bundle-installed-state-summary')).toContainText('release-engineering-starter');
  await expect(page.getByTestId('bundle-installed-state-doctor')).toBeVisible();
  await page.getByTestId('bundle-remove-execution-run').click();
  await expect(page.getByTestId('bundle-remove-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('bundle-installed-state-status')).toContainText('Not installed yet', {
    timeout: 20000,
  });
  await expect(page.getByTestId('bundle-registry-execution')).toBeVisible();
  await expect(page.getByTestId('bundle-registry-execution-trust')).toContainText(
    '3 of 3 skills reviewed'
  );
  await expect(page.getByTestId('bundle-registry-execution-policy-gate-state')).toContainText(
    /Ready|Needs review/
  );
  await expect(page.getByTestId('bundle-registry-execution-approval-state')).toContainText(
    'Waiting for explicit approval'
  );
  await expect(page.getByTestId('bundle-registry-execution-run')).toBeDisabled();
  await page.getByTestId('bundle-registry-execution-field-registry_url').fill('http://127.0.0.1:38765');
  await page.getByTestId('bundle-registry-execution-approval-checkbox').check();
  await expect(page.getByTestId('bundle-registry-execution-approval-state')).toContainText(
    'Approval captured for remote execution'
  );
  await page.getByTestId('bundle-registry-execution-run').click();
  await expect(page.getByTestId('bundle-registry-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('bundle-registry-execution-summary')).toContainText('release-engineering-starter');
  await expect(page.getByTestId('bundle-registry-execution-summary')).toContainText('http://127.0.0.1:38765');

  await page.goto('/docs');
  await expect(page.getByTestId('docs-filter-project')).toBeVisible();
  await page.getByTestId('docs-filter-project').click({ force: true });
  await page.getByTestId('docs-search-input').fill('frontend backend');
  await expect(page.getByTestId('docs-result-project-frontend-backend-integration')).toBeVisible();
  await expect(page.getByTestId('docs-results-count')).toContainText('Showing 1');
  await Promise.all([
    page.waitForURL(/\/docs\/project\/frontend-backend-integration$/),
    page.getByTestId('docs-result-project-frontend-backend-integration').click(),
  ]);
  await expect(page.getByRole('heading', { name: /前端\s*\/\s*后端集成/i }).first()).toBeVisible();
  await expect(page.getByTestId('doc-action-panel')).toBeVisible();
  await expect(page.getByTestId('doc-action-runbook-hint')).toContainText('Recommended run order');
  await expect(page.getByTestId('doc-action-sequence-1')).toContainText('Step 1 - Start here');
  await expect(page.getByTestId('doc-action-sequence-2')).toContainText('Step 2 - Finish by verifying');
  await expect(page.getByTestId('doc-action-project-primary')).toContainText('python scripts/check_python_market_backend.py');
  await expect(page.getByTestId('doc-action-prerequisites-project-primary')).toContainText(
    'Install backend dependencies'
  );
  await expect(page.getByTestId('doc-action-outcome-project-primary')).toContainText(
    'The Python market backend check passes'
  );
  await expect(page.getByTestId('doc-action-artifacts-project-primary')).toContainText(
    'Backend payload-count summary printed in terminal output'
  );
  await expect(page.getByTestId('doc-action-project-secondary')).toContainText('npm run e2e --prefix frontend');
  await page.getByTestId('doc-action-copy-project-primary').click();
  await expect(page.getByTestId('doc-action-copy-project-primary')).toContainText('Copied');
  await expect(page.getByTestId('doc-context-panel')).toBeVisible();
  await expect(page.getByTestId('doc-context-project-path')).toContainText('docs/frontend-backend-integration.md');
  const firstRelatedDoc = page.locator('[data-testid^="related-doc-link-"]').first();
  await expect(firstRelatedDoc).toBeVisible();
  const relatedHref = await firstRelatedDoc.getAttribute('href');
  expect(relatedHref).toBeTruthy();
  await firstRelatedDoc.click();
  await expect(page).toHaveURL(new RegExp((relatedHref ?? '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  await expect(page.locator('h1').first()).toBeVisible();

  await page.goto('/docs/project/frontend-backend-integration');
  await expect(page.getByTestId('doc-context-project-center')).toHaveAttribute('href', '/docs');
  await page.goto('/docs');
  await expect(page.getByTestId('docs-search-input')).toBeVisible();

  await page.goto('/docs');
  await expect(page.getByTestId('skill-doc-card-release-note-writer')).toBeVisible();
  await Promise.all([
    page.waitForURL(/\/docs\/release-note-writer$/),
    page.getByTestId('skill-doc-card-release-note-writer').click(),
  ]);
  await expect(page.getByRole('heading', { name: /release note writer/i }).first()).toBeVisible();
  await expect(page.getByTestId('doc-action-skill-install')).toContainText('python scripts/skills_market.py install');
  await expect(page.getByTestId('doc-action-skill-checker')).toContainText('check_release_note_writer.py');
  await expect(page.getByTestId('doc-context-skill-entrypoint')).toContainText('release-note-writer/SKILL.md');

  await page.goto('/docs/teaching');
  await expect(page.getByTestId('teaching-doc-link-14-first-hour-onboarding')).toBeVisible();
  await Promise.all([
    page.waitForURL(/\/docs\/teaching\/14-first-hour-onboarding$/),
    page.getByTestId('teaching-doc-link-14-first-hour-onboarding').click(),
  ]);
  await expect(page.getByRole('heading', { name: /first hour|onboarding/i }).first()).toBeVisible();
  await expect(page.getByTestId('doc-action-teaching-primary')).toContainText('python scripts/check_progressive_skills.py');
  await expect(page.getByTestId('doc-context-teaching-position')).toBeVisible();

  await page.goto('/docs');
  await expect(page.getByTestId('project-doc-card-frontend-backend-integration')).toBeVisible();
});
