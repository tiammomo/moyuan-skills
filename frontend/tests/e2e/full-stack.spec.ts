import { expect, test } from '@playwright/test';

test('frontend works against the Python backend across core market flows', async ({ page }) => {
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
  await expect(page.getByTestId('skill-registry-execution')).toBeVisible();
  await page.getByTestId('skill-registry-execution-field-registry_url').fill('http://127.0.0.1:38765');
  await page.getByTestId('skill-registry-execution-run').click();
  await expect(page.getByTestId('skill-registry-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('skill-registry-execution-summary')).toContainText('moyuan.release-note-writer');
  await expect(page.getByTestId('skill-registry-execution-summary')).toContainText('http://127.0.0.1:38765');

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
  await expect(page.getByTestId('bundle-registry-execution')).toBeVisible();
  await page.getByTestId('bundle-registry-execution-field-registry_url').fill('http://127.0.0.1:38765');
  await page.getByTestId('bundle-registry-execution-run').click();
  await expect(page.getByTestId('bundle-registry-execution-status')).toContainText('Succeeded', { timeout: 20000 });
  await expect(page.getByTestId('bundle-registry-execution-summary')).toContainText('release-engineering-starter');
  await expect(page.getByTestId('bundle-registry-execution-summary')).toContainText('http://127.0.0.1:38765');

  await page.goto('/docs');
  await page.getByTestId('docs-filter-project').click();
  await page.getByTestId('docs-search-input').fill('frontend backend');
  await expect(page.getByTestId('docs-result-project-frontend-backend-integration')).toBeVisible();
  await expect(page.getByTestId('docs-results-count')).toContainText('Showing 1');
  await Promise.all([
    page.waitForURL(/\/docs\/project\/frontend-backend-integration$/),
    page.getByTestId('docs-result-project-frontend-backend-integration').click(),
  ]);
  await expect(page.getByRole('heading', { name: /frontend \/ backend integration/i }).first()).toBeVisible();
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
  await page.getByTestId('doc-context-project-center').click();
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
