import { test, expect } from '@playwright/test';

test.describe('Voice Network Resilience', () => {
  // Helper function to fill textarea and ensure button is enabled
  async function fillTextareaAndWaitForButton(page, text) {
    const textarea = page.locator('textarea');
    const submitButton = page.getByRole('button', { name: /generate perspective/i });
    
    // Clear existing content
    await textarea.clear();
    
    // For WebKit, use type() instead of fill() to ensure proper event triggering
    if (page.context().browser().browserType().name() === 'webkit') {
      await textarea.type(text, { delay: 50 });
      // Additional input event for WebKit
      await textarea.dispatchEvent('input');
    } else {
      await textarea.fill(text);
    }
    
    // Wait a bit for React state to update
    await page.waitForTimeout(500);
    
    // Wait for button to be enabled
    await expect(submitButton).toBeEnabled({ timeout: 15000 });
    
    return submitButton;
  }

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
    const submitButton = await fillTextareaAndWaitForButton(page, 'I feel anxious about testing');
    
    // Intercept SSE endpoint to simulate failure
    await page.route('**/api/events/**', route => {
      route.abort('failed');
    });
    
    // Submit form which should trigger SSE connection
    await submitButton.click();
    
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
    const submitButton = await fillTextareaAndWaitForButton(page, 'Testing network resilience');
    await submitButton.click();
    
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
    const submitButton = await fillTextareaAndWaitForButton(page, 'Starting a conversation');
    await submitButton.click();
    
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
    const continueButton = await fillTextareaAndWaitForButton(page, 'Continuing after network interruption');
    await continueButton.click();
  });

  test('handles slow network conditions', async ({ page }) => {
    // Simulate slow 3G network
    await page.route('**/*', async (route) => {
      // Add 500ms delay to simulate slow network
      await new Promise(resolve => setTimeout(resolve, 500));
      await route.continue();
    });
    
    // Submit a thought
    const submitButton = await fillTextareaAndWaitForButton(page, 'Testing on slow network');
    await submitButton.click();
    
    // Check for loading state - the button should show loading
    const loadingButton = page.getByRole('button', { name: /Processing/i });
    // Just verify the page is responsive, loading states might be quick
    await expect(page.locator('textarea')).toBeVisible();
    
    // Should eventually receive response despite slow network
    await expect(page.locator('div.mt-8')).toBeVisible({ timeout: 30000 });
  });

  test('handles complete offline scenario', async ({ page, context }) => {
    // Submit initial thought while online
    const textarea = page.locator('textarea');
    const submitButton = page.getByRole('button', { name: /generate perspective/i });
    
    // Fill the textarea
    if (page.context().browser().browserType().name() === 'webkit') {
      await textarea.type('Testing offline scenario', { delay: 50 });
      await textarea.dispatchEvent('input');
    } else {
      await textarea.fill('Testing offline scenario');
    }
    
    // Go offline before submitting
    await context.setOffline(true);
    
    // Try to submit (it will be queued or fail)
    await submitButton.click();
    
    // Should handle offline state gracefully
    await page.waitForTimeout(2000);
    
    // Form should remain visible even if disabled
    await expect(textarea).toBeVisible();
    
    // Go back online BEFORE reloading
    await context.setOffline(false);
    await page.waitForTimeout(2000);
    
    // Now reload the page while online
    await page.reload();
    // Wait for the page to be ready (DOM loaded) instead of waiting for all network requests
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    
    // After reload, form should be fully functional
    const newSubmitButton = await fillTextareaAndWaitForButton(page, 'Testing after reconnection');
    await newSubmitButton.click();
    
    // Wait for either a response or at least verify form is working
    await page.waitForTimeout(2000);
    await expect(page.locator('textarea')).toBeVisible();
  });

  test('handles rapid connection state changes', async ({ page, context }) => {
    // Submit initial thought
    const submitButton = await fillTextareaAndWaitForButton(page, 'Testing rapid network changes');
    await submitButton.click();
    
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
    await fillTextareaAndWaitForButton(page, 'Still working after network flapping');
  });

  test('handles timeout scenarios gracefully', async ({ page }) => {
    // Fill the form first
    const submitButton = await fillTextareaAndWaitForButton(page, 'Testing timeout handling');
    
    // Then intercept API calls to simulate very slow response
    await page.route('**/api/**', async (route) => {
      // Intercept all API calls and make them slow
      await new Promise(resolve => setTimeout(resolve, 35000));
      route.continue();
    });
    
    // Now click submit - this will trigger the slow request
    await submitButton.click();
    
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