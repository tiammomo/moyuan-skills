import fs from 'node:fs/promises';
import path from 'node:path';
import { expect, test } from '@playwright/test';

const screenshotDir = path.resolve(process.cwd(), '..', 'docs', 'assets', 'readme');

test('capture README screenshots for the live skills market flow @readme-screenshots', async ({ page }) => {
  await fs.mkdir(screenshotDir, { recursive: true });
  await page.setViewportSize({ width: 1440, height: 960 });

  await page.goto('/');
  await expect(page.locator('[data-testid^="skill-card-"]').first()).toBeVisible();
  await page.screenshot({
    path: path.join(screenshotDir, 'playwright-home-overview.png'),
    fullPage: false,
  });

  await page.goto('/skills');
  await page.getByTestId('skill-search-input').fill('release');
  await expect(page.getByTestId('skill-card-release-note-writer')).toBeVisible();
  await page.screenshot({
    path: path.join(screenshotDir, 'playwright-skill-search.png'),
    fullPage: false,
  });

  await page.goto('/skills/release-note-writer');
  await expect(page.getByTestId('install-command')).toContainText('release-note-writer-0.1.0.json');
  await page.screenshot({
    path: path.join(screenshotDir, 'playwright-skill-detail.png'),
    fullPage: false,
  });

  await page.goto('/docs/release-note-writer');
  await expect(page.getByTestId('doc-action-panel')).toBeVisible();
  await expect(page.getByTestId('doc-action-skill-install')).toContainText('python scripts/skills_market.py install');
  await page.screenshot({
    path: path.join(screenshotDir, 'playwright-skill-runbook.png'),
    fullPage: false,
  });
});
