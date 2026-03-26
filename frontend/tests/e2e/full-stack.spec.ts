import { expect, test } from '@playwright/test';

test('frontend works against the Python backend across core market flows', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('[data-testid^="skill-card-"]').first()).toBeVisible();

  await page.goto('/skills');
  await page.getByTestId('skill-search-input').fill('release');
  await expect(page.locator('[data-testid="skill-card-release-note-writer"]')).toBeVisible();

  await page.locator('[data-testid="skill-card-release-note-writer"]').first().click();
  await expect(page.getByTestId('install-command')).toContainText('release-note-writer-0.1.0.json');

  await page.goto('/bundles');
  await expect(page.getByTestId('bundle-card-release-engineering-starter')).toBeVisible();
  await page.getByTestId('bundle-link-release-engineering-starter').click();
  await expect(page.getByTestId('install-command').first()).toContainText('release-note-writer-0.1.0.json');

  await page.goto('/docs');
  await page.getByTestId('docs-filter-project').click();
  await page.getByTestId('docs-search-input').fill('frontend backend');
  await expect(page.getByTestId('docs-result-project-frontend-backend-integration')).toBeVisible();
  await expect(page.getByTestId('docs-results-count')).toContainText('Showing 1');
  await page.getByTestId('docs-result-project-frontend-backend-integration').click();
  await expect(page.getByRole('heading', { name: /frontend \/ backend integration/i }).first()).toBeVisible();
  await expect(page.getByTestId('doc-action-panel')).toBeVisible();
  await expect(page.getByTestId('doc-action-runbook-hint')).toContainText('Recommended run order');
  await expect(page.getByTestId('doc-action-sequence-1')).toContainText('Step 1 - Start here');
  await expect(page.getByTestId('doc-action-sequence-2')).toContainText('Step 2 - Finish by verifying');
  await expect(page.getByTestId('doc-action-project-primary')).toContainText('python scripts/check_python_market_backend.py');
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
  await page.getByTestId('skill-doc-card-release-note-writer').click();
  await expect(page.getByRole('heading', { name: /release note writer/i }).first()).toBeVisible();
  await expect(page.getByTestId('doc-action-skill-install')).toContainText('python scripts/skills_market.py install');
  await expect(page.getByTestId('doc-action-skill-checker')).toContainText('check_release_note_writer.py');
  await expect(page.getByTestId('doc-context-skill-entrypoint')).toContainText('skills/release-note-writer/SKILL.md');

  await page.goto('/docs/teaching');
  await expect(page.getByTestId('teaching-doc-link-14-first-hour-onboarding')).toBeVisible();
  await page.getByTestId('teaching-doc-link-14-first-hour-onboarding').click();
  await expect(page.getByRole('heading', { name: /first hour|onboarding/i }).first()).toBeVisible();
  await expect(page.getByTestId('doc-action-teaching-primary')).toContainText('python scripts/check_progressive_skills.py');
  await expect(page.getByTestId('doc-context-teaching-position')).toBeVisible();

  await page.goto('/docs');
  await expect(page.getByTestId('project-doc-card-frontend-backend-integration')).toBeVisible();
});
