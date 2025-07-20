import { test, expect } from '@playwright/test';

test.describe('Direct SSE Test', () => {
  test('check SSE connection directly', async ({ page }) => {
    // Mock the SSE endpoint to always succeed
    await page.route('**/api/events/*', async (route) => {
      const sse = route.request().sse();
      
      // Send initial connection success
      await sse.push({ event: 'status', data: JSON.stringify({ type: 'connected' }) });
      
      // Keep connection open
    });
    
    await page.goto('/');
    
    // Wait for any connection attempt
    await page.waitForTimeout(2000);
    
    // Check if the button is enabled after typing
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    await thoughtInput.fill('Test message');
    
    // Check button state
    const isDisabled = await submitButton.isDisabled();
    console.log('Button disabled after typing:', isDisabled);
    
    // Check what the button's disabled attribute is
    const buttonHtml = await submitButton.evaluate(el => el.outerHTML);
    console.log('Button HTML:', buttonHtml);
    
    // Check if there's any isLoading state in the component
    const pageContent = await page.content();
    const hasProcessing = pageContent.includes('Processing');
    console.log('Page has "Processing" text:', hasProcessing);
    
    // Check connection status text
    const connectionTexts = await page.locator('text=/Connected|Disconnected/').allTextContents();
    console.log('Connection status texts:', connectionTexts);
    
    await expect(submitButton).toBeEnabled();
  });
});