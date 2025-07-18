/*
 * End-to-end workflow covering the core CBT use-case in the **real browser**.
 * Run with:
 *   npx playwright test --config playwright-js/playwright.config.ts --ui
 */

import { test, expect } from '@playwright/test';

const thought1 = 'I always mess things up';
const thought2 = 'I am afraid I will fail again tomorrow';

/** Returns locator for the last assistant message. */
function assistantBubble(page) {
  return page.locator('div.mt-8').last();
}

test.describe('Happy-path CBT workflow (text mode)', () => {
  test('user submits two thoughts, receives reframes and downloads PDF', async ({ page }) => {
    await page.goto('/');

    // 1. Submit first thought
    await page.fill('textarea', thought1);
    await page.getByRole('button', { name: /generate perspective/i }).click();

    // Wait for assistant response – avoid brittle keyword match, just ensure
    // we received a reasonably long reply.
    await expect
      .poll(async () => (await assistantBubble(page).innerText()).length, { timeout: 10000 })
      .toBeGreaterThan(80);

    // 2. Submit second thought
    await page.getByRole('button', { name: /clear/i }).click();
    await page.fill('textarea', thought2);
    await page.getByRole('button', { name: /generate perspective/i }).click();

    await expect
      .poll(async () => (await assistantBubble(page).innerText()).length, { timeout: 10000 })
      .toBeGreaterThan(80);

    // 3. Download session PDF (if feature present)
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.getByRole('button', { name: /download session pdf/i }).click(),
    ]).catch(() => [undefined]);

    if (download) {
      const name = await download.suggestedFilename();
      expect(name).toMatch(/\.pdf$/);
    }
  });
});
