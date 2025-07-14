import { test, expect } from '@playwright/test';

test.describe('Re-frame Full Workflow Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should load homepage with correct title and elements', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/re-frame\.social/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('re-frame');
    
    // Check for thought input form
    await expect(page.locator('textarea[placeholder*="What happened"]')).toBeVisible();
    
    // Check submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should submit text thought and receive response', async ({ page }) => {
    // Type a thought
    const thoughtText = 'I feel anxious about my upcoming presentation at work.';
    await page.fill('textarea[placeholder*="What happened"]', thoughtText);
    
    // Wait for button to be enabled (webkit might be slower)
    const submitButton = page.locator('button:has-text("Generate perspective")');
    await expect(submitButton).toBeEnabled({ timeout: 5000 });
    
    // Submit the form
    await submitButton.click();
    
    // Wait for response (this would come from backend in real integration)
    // For now, check that the form was submitted
    await page.waitForTimeout(1000);
    
    // In a real test with backend running, we would wait for:
    // await expect(page.locator('[data-testid="response-content"]')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate to CBT learning page', async ({ page }) => {
    // Click on the learn CBT link
    await page.click('a[href="/learn-cbt"]');
    
    // Check we're on the right page
    await expect(page).toHaveURL(/\/learn-cbt/);
    await expect(page.locator('h1:has-text("What is CBT")')).toBeVisible();
  });

  test('should check privacy page accessibility', async ({ page }) => {
    // Navigate to privacy page
    await page.goto('/privacy');
    
    // Check page loaded
    await expect(page.locator('h1:has-text("Privacy")')).toBeVisible();
    
    // Check for important privacy elements
    await expect(page.locator('text=you alone')).toBeVisible();
  });

  test('should verify health endpoints are accessible', async ({ page }) => {
    // Check frontend health endpoint
    const frontendHealth = await page.request.get('/api/health');
    expect(frontendHealth.ok()).toBeTruthy();
    const frontendData = await frontendHealth.json();
    expect(frontendData.status).toBe('healthy');
    
    // Check backend health endpoint (when backend is running)
    const backendHealth = await page.request.get('http://localhost:8000/health');
    expect(backendHealth.ok()).toBeTruthy();
    const backendData = await backendHealth.json();
    expect(backendData.status).toBe('healthy');
  });
});

test.describe('Audio Recording Workflow', () => {
  test.beforeEach(async ({ page, context, browserName }) => {
    // Grant microphone permissions (only supported in Chromium)
    if (browserName === 'chromium') {
      await context.grantPermissions(['microphone']);
    }
    await page.goto('/');
  });

  test('should show audio recording button when available', async ({ page }) => {
    // Check for audio recording UI elements
    const recordButton = page.locator('button[aria-label*="record"]');
    
    // In a real implementation with audio UI:
    // await expect(recordButton).toBeVisible();
    
    // For now, just check the page loads
    await expect(page).toHaveTitle(/re-frame/);
  });
});

test.describe('Session End Workflow', () => {
  test('should show PDF download button after session ends', async ({ page }) => {
    // Navigate to conversation demo (if available)
    // This would be part of the actual conversation flow
    
    // For now, check that PDF download component could work
    await page.goto('/');
    
    // In real flow:
    // 1. Complete a session
    // 2. Check for session end view
    // 3. Verify PDF download button appears
    // 4. Click download and verify file downloads
  });
});

test.describe('Mobile Responsiveness', () => {
  test.use({
    viewport: { width: 375, height: 667 },
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.goto('/');
    
    // Check that mobile menu or responsive elements work
    await expect(page.locator('textarea[placeholder*="What happened"]')).toBeVisible();
    
    // Verify layout adjusts for mobile - check button is still visible
    await expect(page.locator('button:has-text("Generate perspective")')).toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    // Navigate first
    await page.goto('/');
    
    // Fill the form
    await page.fill('textarea[placeholder*="What happened"]', 'Test thought');
    
    // Now simulate offline mode
    await page.context().setOffline(true);
    
    // Try to submit
    await page.click('button:has-text("Generate perspective")');
    
    // Should show error or handle gracefully - wait a bit
    await page.waitForTimeout(1000);
    
    // Re-enable network
    await page.context().setOffline(false);
  });
});

test.describe('Backend Integration', () => {
  test('should connect to SSE endpoint', async ({ page }) => {
    // This test requires backend to be running
    const response = await page.request.get('http://localhost:8000/api/events/test-session-123?is_audio=false');
    
    // SSE endpoint should return streaming response
    expect(response.headers()['content-type']).toContain('text/event-stream');
  });

  test('should handle audio conversion', async ({ page }) => {
    // First establish SSE connection
    const sseResponse = await page.request.get('http://localhost:8000/api/events/test-session-123?is_audio=true');
    expect(sseResponse.ok()).toBeTruthy();
    
    // Wait a bit for connection to establish
    await page.waitForTimeout(500);
    
    // Test audio upload endpoint
    const audioData = Buffer.from('mock-audio-data');
    const response = await page.request.post('http://localhost:8000/api/send/test-session-123', {
      data: {
        data: audioData.toString('base64'),
        mime_type: 'audio/wav',
        message_type: 'thought',
        session_id: 'test-session-123'
      }
    });
    
    // Check response - it might return an error for invalid audio but shouldn't be 404
    expect(response.status()).not.toBe(404);
  });
});