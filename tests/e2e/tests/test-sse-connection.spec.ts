import { test, expect } from '@playwright/test';

test.describe('SSE Connection Debug', () => {
  test('debug SSE connection issue', async ({ page }) => {
    // Listen to console logs
    page.on('console', msg => {
      const text = msg.text();
      if (!text.includes('preloaded using link')) {
        console.log('Browser console:', text);
      }
    });
    
    // Listen to network failures
    page.on('requestfailed', request => {
      console.log('Request failed:', request.url(), request.failure()?.errorText);
    });
    
    // Listen to network requests
    page.on('request', request => {
      if (request.url().includes('/api/') || request.url().includes('8000')) {
        console.log('Request:', request.method(), request.url());
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/') || response.url().includes('8000')) {
        console.log('Response:', response.status(), response.url());
      }
    });
    
    // Navigate to the page
    await page.goto('/');
    
    // Wait a bit to see what happens
    await page.waitForTimeout(3000);
    
    // Check what's in the page
    const bodyText = await page.locator('body').textContent();
    console.log('Page contains "Disconnected":', bodyText?.includes('Disconnected'));
    console.log('Page contains "Connected":', bodyText?.includes('Connected'));
    
    // Check window location
    const windowLocation = await page.evaluate(() => window.location.href);
    console.log('Window location:', windowLocation);
    
    // Try to manually trigger SSE connection
    const sseTest = await page.evaluate(async () => {
      // In Next.js, env vars are replaced at build time
      const apiUrl = 'http://localhost:8000';
      const testUrl = `${apiUrl}/api/events/test-session`;
      
      try {
        const eventSource = new EventSource(testUrl);
        
        return new Promise((resolve) => {
          eventSource.onopen = () => resolve({ status: 'opened', url: testUrl });
          eventSource.onerror = (e) => resolve({ status: 'error', url: testUrl, error: e.type });
          
          setTimeout(() => {
            eventSource.close();
            resolve({ status: 'timeout', url: testUrl });
          }, 2000);
        });
      } catch (error) {
        return { status: 'exception', url: testUrl, error: String(error) };
      }
    });
    
    console.log('Manual SSE test result:', sseTest);
    
    // Take screenshot
    await page.screenshot({ path: 'sse-debug.png' });
  });
});