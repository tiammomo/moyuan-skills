import fs from 'node:fs';
import path from 'node:path';
import { defineConfig, devices } from '@playwright/test';

const frontendRoot = __dirname;
const repoRoot = path.resolve(frontendRoot, '..');
const pythonCandidates = [
  process.env.PYTHON,
  path.join(repoRoot, '.venv', 'bin', 'python'),
  path.join(repoRoot, '.venv', 'Scripts', 'python.exe'),
  'python',
].filter((candidate): candidate is string => Boolean(candidate));
const pythonCommand =
  pythonCandidates.find((candidate) => candidate === 'python' || fs.existsSync(candidate)) ?? 'python';

export default defineConfig({
  testDir: path.join(frontendRoot, 'tests', 'e2e'),
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { outputFolder: path.join(frontendRoot, 'playwright-report') }]],
  use: {
    baseURL: 'http://127.0.0.1:33003',
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
      command: `${pythonCommand} -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083`,
      cwd: repoRoot,
      url: 'http://127.0.0.1:38083/health',
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        ...process.env,
        MOYUAN_SKILLS_REPO_ROOT: repoRoot,
        MOYUAN_SKILLS_API_CORS: 'http://127.0.0.1:33003,http://localhost:33003',
      },
    },
    {
      command:
        `${pythonCommand} scripts/serve_market_registry_fixture.py --host 127.0.0.1 --port 38765 --output-dir dist/playwright-registry --clean`,
      cwd: repoRoot,
      url: 'http://127.0.0.1:38765/registry.json',
      reuseExistingServer: false,
      timeout: 120000,
    },
    {
      command: 'npm run start:local',
      cwd: frontendRoot,
      url: 'http://127.0.0.1:33003',
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        ...process.env,
        SKILLS_MARKET_API_BASE_URL: 'http://127.0.0.1:38083',
      },
    },
  ],
});
