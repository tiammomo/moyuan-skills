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

  await page.goto('/docs');
  await expect(page.getByTestId('skill-doc-card-release-note-writer')).toBeVisible();
  await page.getByTestId('skill-doc-card-release-note-writer').click();
  await expect(page.getByRole('heading', { name: /release note writer/i }).first()).toBeVisible();

  await page.goto('/docs/teaching');
  await expect(page.getByTestId('teaching-doc-link-14-first-hour-onboarding')).toBeVisible();
  await page.getByTestId('teaching-doc-link-14-first-hour-onboarding').click();
  await expect(page.getByRole('heading', { name: /first hour|onboarding/i }).first()).toBeVisible();

  await page.goto('/docs');
  await expect(page.getByTestId('project-doc-card-frontend-backend-integration')).toBeVisible();
});
