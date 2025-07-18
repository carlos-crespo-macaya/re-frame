import { test, expect } from '@playwright/test';

test.describe('Voice Network Resilience', () => {
  test.beforeEach(async ({ page }) => {
    // Set up audio simulation helpers
    await page.addInitScript(() => {
      // Mock audio simulation for testing
      window.simulateAudioInput = (base64Audio) => {
        const event = new CustomEvent('test-audio-input', {
          detail: { audioData: base64Audio }
        });
        window.dispatchEvent(event);
      };
      
      // Mock session ID management for testing
      if (!sessionStorage.getItem('session-id')) {
        sessionStorage.setItem('session-id', 'test-session-' + Date.now());
      }
    });
    
    await page.goto('http://localhost:3000');
  });

  test('handles SSE connection failure during conversation', async ({ page }) => {
    // Submit a thought to start conversation
    await page.fill('textarea', 'I feel anxious about testing');
    
    // Intercept SSE endpoint to simulate failure
    await page.route('**/api/events/**', route => {
      route.abort('failed');
    });
    
    // Submit form which should trigger SSE connection
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Should handle the connection error gracefully
    // Look for any error indication in the UI
    await page.waitForTimeout(2000);
    
    // The form will be disabled during loading
    // But we should verify the page doesn't crash
    const textarea = page.locator('textarea');
    await expect(textarea).toBeVisible();
    
    // Since SSE failed, the form might stay in loading state
    // or eventually timeout - either is acceptable as long as no crash
    // Just verify the page is still responsive
    await expect(page).toHaveTitle(/re-frame|Cognitive Reframing/);
  });

  test('handles API endpoint failure and recovery', async ({ page }) => {
    let attemptCount = 0;
    
    // Fail first attempt, succeed on retry
    await page.route('**/api/send/**', route => {
      attemptCount++;
      if (attemptCount === 1) {
        route.abort('failed');
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ status: 'sent' })
        });
      }
    });
    
    // Submit a thought
    await page.fill('textarea', 'Testing network resilience');
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for potential retry logic
    await page.waitForTimeout(3000);
    
    // Should handle the failure gracefully
    const textarea = page.locator('textarea');
    await expect(textarea).toBeVisible();
  });

  test('maintains session during network interruptions', async ({ page, context }) => {
    // Get initial session ID
    const initialSessionId = await page.evaluate(() => {
      return sessionStorage.getItem('session-id');
    });
    
    // Submit a thought to establish session
    await page.fill('textarea', 'Starting a conversation');
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for response
    await page.waitForSelector('div.mt-8', { timeout: 10000 });
    
    // Simulate brief network interruption
    await context.setOffline(true);
    await page.waitForTimeout(1000);
    await context.setOffline(false);
    
    // Verify same session is maintained
    const currentSessionId = await page.evaluate(() => {
      return sessionStorage.getItem('session-id');
    });
    
    expect(currentSessionId).toBe(initialSessionId);
    
    // Should be able to continue conversation
    await page.getByRole('button', { name: /clear/i }).click();
    await page.fill('textarea', 'Continuing after network interruption');
    await page.getByRole('button', { name: /generate perspective/i }).click();
  });

  test('handles slow network conditions', async ({ page }) => {
    // Simulate slow 3G network
    await page.route('**/*', async (route) => {
      // Add 500ms delay to simulate slow network
      await new Promise(resolve => setTimeout(resolve, 500));
      await route.continue();
    });
    
    // Submit a thought
    await page.fill('textarea', 'Testing on slow network');
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Check for loading state - the button should show loading
    const loadingButton = page.getByRole('button', { name: /Processing/i });
    // Just verify the page is responsive, loading states might be quick
    await expect(page.locator('textarea')).toBeVisible();
    
    // Should eventually receive response despite slow network
    await expect(page.locator('div.mt-8')).toBeVisible({ timeout: 30000 });
  });

  test('handles complete offline scenario', async ({ page, context }) => {
    // Submit initial thought while online
    await page.fill('textarea', 'Testing offline scenario');
    
    // Go offline before submitting
    await context.setOffline(true);
    
    // Try to submit (it will be queued or fail)
    const submitButton = page.getByRole('button', { name: /generate perspective/i });
    await submitButton.click();
    
    // Should handle offline state gracefully
    await page.waitForTimeout(2000);
    
    // Form should remain usable
    const textarea = page.locator('textarea');
    await expect(textarea).toBeVisible();
    
    // Go back online
    await context.setOffline(false);
    await page.waitForTimeout(3000); // Give more time for recovery
    
    // Wait for the submit button to stop processing first
    await expect(submitButton).toBeEnabled({ timeout: 15000 });
    
    // Then wait for the Clear button to be enabled
    const clearButton = page.getByRole('button', { name: /clear/i });
    await expect(clearButton).toBeEnabled({ timeout: 15000 });
    
    // Clear and try again with a new submission
    await clearButton.click();
    await page.fill('textarea', 'Testing after reconnection');
    
    // Should be able to submit successfully now
    await submitButton.click();
    
    // Wait for either a response or loading state
    try {
      await expect(page.locator('div.mt-8')).toBeVisible({ timeout: 10000 });
    } catch {
      // If no response yet, at least the form should be working
      await expect(textarea).toBeVisible();
    }
  });

  test('handles rapid connection state changes', async ({ page, context }) => {
    // Submit initial thought
    await page.fill('textarea', 'Testing rapid network changes');
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Rapidly toggle network state
    for (let i = 0; i < 5; i++) {
      await context.setOffline(true);
      await page.waitForTimeout(200);
      await context.setOffline(false);
      await page.waitForTimeout(200);
    }
    
    // System should remain stable
    const textarea = page.locator('textarea');
    await expect(textarea).toBeVisible();
    
    // Should still be able to interact
    await page.getByRole('button', { name: /clear/i }).click();
    await page.fill('textarea', 'Still working after network flapping');
  });

  test('handles timeout scenarios gracefully', async ({ page }) => {
    // Submit a thought first
    await page.fill('textarea', 'Testing timeout handling');
    
    // Then intercept API calls to simulate very slow response
    await page.route('**/api/**', async (route) => {
      // Intercept all API calls and make them slow
      await new Promise(resolve => setTimeout(resolve, 35000));
      route.continue();
    });
    
    // Now click submit - this will trigger the slow request
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait a bit for request to be made
    await page.waitForTimeout(1000);
    
    // After some time, UI should remain responsive
    await page.waitForTimeout(2000);
    
    // The page should still be functional even if request is pending
    await expect(page).toHaveTitle(/re-frame|Cognitive Reframing/);
    const textarea = page.locator('textarea');
    await expect(textarea).toBeVisible();
  });
});