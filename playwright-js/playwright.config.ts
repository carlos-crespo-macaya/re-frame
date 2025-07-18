import { defineConfig, devices } from '@playwright/test';

/*
 * Re-frame – JavaScript Playwright configuration
 * ------------------------------------------------
 * This config is **self-contained**: it never touches the Python test-suite
 * and can be executed locally with
 *   npx playwright test --config playwright-js/playwright.config.ts --ui
 */

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  timeout: 45_000,
  retries: process.env.CI ? 1 : 0,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1280, height: 720 },
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],

  /*
   * If you do **not** have the stack running manually you can let Playwright
   * start it.  Uncomment the following block – it launches the same
   * docker-compose files used in CI and waits for the frontend.
   */
  /*
  webServer: {
    command: 'docker-compose up -d --build',
    timeout: 3 * 60 * 1000,
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
  */
});

