import { defineConfig } from '@playwright/test';

const port = process.env.FRONTEND_TEST_PORT ?? '8765';
export default defineConfig({
  testDir: './test',
  globalSetup: './test/setup.ts',
  fullyParallel: true,
  // The synthetic chapter has one global poll; transaction scenarios must not race reads.
  workers: 1,
  use: {
    baseURL: process.env.FRONTEND_TEST_URL ?? `http://127.0.0.1:${port}`,
    trace: 'retain-on-failure',
    launchOptions: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE
      ? {
          executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
        }
      : {},
  },
  webServer: process.env.FRONTEND_TEST_URL
    ? undefined
    : {
        command: `${process.env.PYTHON_EXECUTABLE ?? 'python'} ../tools/testing/serve_frontend.py`,
        url: `http://127.0.0.1:${port}/api/v1/status/`,
        reuseExistingServer: false,
        timeout: 60000,
      },
});
