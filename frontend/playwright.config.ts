import path from 'node:path';
import { defineConfig, devices } from '@playwright/test';

const frontendRoot = __dirname;
const repoRoot = path.resolve(frontendRoot, '..');

export default defineConfig({
  testDir: path.join(frontendRoot, 'tests', 'e2e'),
  fullyParallel: false,
  reporter: [['list'], ['html', { outputFolder: path.join(frontendRoot, 'playwright-report') }]],
  use: {
    baseURL: 'http://127.0.0.1:3210',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8210',
      cwd: repoRoot,
      url: 'http://127.0.0.1:8210/health',
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        ...process.env,
        MOYUAN_SKILLS_REPO_ROOT: repoRoot,
        MOYUAN_SKILLS_API_CORS: 'http://127.0.0.1:3210',
      },
    },
    {
      command: 'npm run start -- --hostname 127.0.0.1 --port 3210',
      cwd: frontendRoot,
      url: 'http://127.0.0.1:3210',
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        ...process.env,
        SKILLS_MARKET_API_BASE_URL: 'http://127.0.0.1:8210',
      },
    },
  ],
});
