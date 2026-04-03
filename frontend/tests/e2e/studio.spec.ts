import { promises as fs } from 'node:fs';
import * as path from 'node:path';
import { expect, test } from '@playwright/test';

const repoRoot = path.resolve(process.cwd(), '..');

function toRepoPath(...segments: string[]): string {
  return path.join(...segments).split(path.sep).join('/');
}

test.setTimeout(120_000);

test('studio author flow works against isolated submission roots', async ({ page }) => {
  const studioRoot = path.join(repoRoot, 'dist', 'frontend-studio-e2e');
  const submissionsRoot = path.join(studioRoot, 'submissions');
  const inboxRoot = path.join(studioRoot, 'incoming');
  const stagedSkillsRoot = path.join(studioRoot, 'staged-skills');
  const stagedDocsRoot = path.join(studioRoot, 'staged-docs');

  await fs.rm(studioRoot, { recursive: true, force: true });

  const submissionsRootRepoPath = toRepoPath('dist', 'frontend-studio-e2e', 'submissions');
  const inboxRootRepoPath = toRepoPath('dist', 'frontend-studio-e2e', 'incoming');
  const stagedSkillsRootRepoPath = toRepoPath('dist', 'frontend-studio-e2e', 'staged-skills');
  const stagedDocsRootRepoPath = toRepoPath('dist', 'frontend-studio-e2e', 'staged-docs');
  const submissionPathRepoPath = `${submissionsRootRepoPath}/moyuan/release-note-writer/0.1.0/submission.json`;
  const inboxSubmissionPathRepoPath = `${inboxRootRepoPath}/moyuan/release-note-writer/0.1.0/submission.json`;

  const workspaceQuery = new URLSearchParams({
    submissions_root: submissionsRootRepoPath,
    inbox_root: inboxRootRepoPath,
  }).toString();

  await page.goto(`/studio?${workspaceQuery}`);
  await expect(page.getByTestId('studio-overview-hero')).toBeVisible();
  await expect(page.getByTestId('studio-overview-backend')).toContainText('Backend execution is ready');
  await expect(page.getByTestId('studio-overview-backend')).toContainText(submissionsRootRepoPath);
  await expect(page.getByTestId('studio-overview-stat-built')).toContainText('0');
  await expect(page.getByTestId('studio-overview-stat-approved')).toContainText('0');

  await page.goto(`/studio/new?${workspaceQuery}&skill=release-note-writer`);
  await expect(page.getByTestId('studio-new-hero')).toBeVisible();
  await expect(page.getByTestId('studio-build-submission-field-skill')).toHaveValue('release-note-writer');
  await expect(page.getByTestId('studio-build-submission-field-output_dir')).toHaveValue(submissionsRootRepoPath);
  await page
    .getByTestId('studio-build-submission-field-release_notes')
    .fill('Playwright studio author flow build.');
  await page.getByTestId('studio-build-submission-run').click();
  await expect(page.getByTestId('studio-build-submission-status')).toContainText('Succeeded', {
    timeout: 20_000,
  });
  await expect(fs.stat(path.join(submissionsRoot, 'moyuan', 'release-note-writer', '0.1.0', 'submission.json'))).resolves.toBeTruthy();

  await page.goto(`/studio/submissions?${workspaceQuery}`);
  await expect(page.getByTestId('studio-submissions-hero')).toBeVisible();
  await expect(page.getByTestId('studio-submissions-backend')).toContainText('Backend execution is ready');
  await expect(page.getByTestId('studio-submissions-count-built')).toContainText('1');
  await expect(page.getByTestId('studio-upload-submission-field-path')).toHaveValue(submissionPathRepoPath);
  await expect(page.getByTestId('studio-upload-submission-field-inbox_dir')).toHaveValue(inboxRootRepoPath);
  await page.getByTestId('studio-upload-submission-run').click();
  await expect(page.getByTestId('studio-upload-submission-status')).toContainText('Succeeded', {
    timeout: 20_000,
  });
  await expect(fs.stat(path.join(inboxRoot, 'moyuan', 'release-note-writer', '0.1.0', 'submission.json'))).resolves.toBeTruthy();

  await page.goto(
    `/studio/submissions?${workspaceQuery}&review=${encodeURIComponent(inboxSubmissionPathRepoPath)}`
  );
  await expect(page.getByTestId('studio-review-submission-field-path')).toHaveValue(inboxSubmissionPathRepoPath);
  await page.getByTestId('studio-review-submission-field-reviewer').fill('Playwright Maintainer');
  await page
    .getByTestId('studio-review-submission-field-summary')
    .fill('Approved from Playwright studio coverage.');
  await page.getByTestId('studio-review-submission-run').click();
  await expect(page.getByTestId('studio-review-submission-status')).toContainText('Succeeded', {
    timeout: 20_000,
  });
  await expect(fs.stat(path.join(inboxRoot, 'moyuan', 'release-note-writer', '0.1.0', 'review.json'))).resolves.toBeTruthy();

  await page.goto(
    `/studio/submissions?${workspaceQuery}&ingest=${encodeURIComponent(inboxSubmissionPathRepoPath)}`
  );
  await expect(page.getByTestId('studio-ingest-submission-field-path')).toHaveValue(inboxSubmissionPathRepoPath);
  await page.getByTestId('studio-ingest-submission-field-skills_dir').fill(stagedSkillsRootRepoPath);
  await page.getByTestId('studio-ingest-submission-field-docs_dir').fill(stagedDocsRootRepoPath);
  await page.getByTestId('studio-ingest-submission-run').click();
  await expect(page.getByTestId('studio-ingest-submission-status')).toContainText('Succeeded', {
    timeout: 20_000,
  });
  await expect(fs.stat(path.join(stagedSkillsRoot, 'release-note-writer', 'market', 'skill.json'))).resolves.toBeTruthy();
  await expect(
    fs.stat(path.join(stagedDocsRoot, 'skills', 'release-note-writer.md'))
  ).resolves.toBeTruthy();

  await page.goto(`/studio/submissions?${workspaceQuery}`);
  await expect(page.getByTestId('studio-submissions-count-inbox')).toContainText('1');
  await expect(page.getByTestId('studio-submissions-count-approved')).toContainText('1');
  await expect(page.getByTestId('studio-submissions-count-ingested')).toContainText('1');
  await expect(page.getByTestId('studio-inbox-submissions')).toContainText('review: approved');
  await expect(page.getByTestId('studio-inbox-submissions')).toContainText(
    `${stagedSkillsRootRepoPath}/release-note-writer`
  );

  await page.goto(`/studio?${workspaceQuery}`);
  await expect(page.getByTestId('studio-overview-stat-built')).toContainText('1');
  await expect(page.getByTestId('studio-overview-stat-approved')).toContainText('1');
  await expect(page.getByTestId('studio-overview-stat-ingested')).toContainText('1');
  await expect(page.getByTestId('studio-overview-recent-built')).toContainText('release-note-writer');
  await expect(page.getByTestId('studio-overview-recent-inbox')).toContainText('approved');
  await expect(page.getByTestId('studio-overview-recent-jobs')).toContainText('author-submission-ingest');
});
