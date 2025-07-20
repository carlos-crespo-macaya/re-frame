import { test, expect } from '@playwright/test';

test.describe('Basic Form Test', () => {
  test('form should work without SSE connection', async ({ page }) => {
    await page.goto('/');
    
    // Check initial state
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    // Wait for elements to be visible
    await expect(thoughtInput).toBeVisible();
    await expect(submitButton).toBeVisible();
    
    // Check initial button state
    const initialDisabled = await submitButton.isDisabled();
    console.log('Initial button disabled:', initialDisabled);
    
    // Type in the textarea
    await thoughtInput.fill('I need help with my anxiety');
    
    // Check button state after typing
    const afterTypingDisabled = await submitButton.isDisabled();
    console.log('After typing - button disabled:', afterTypingDisabled);
    
    // Try to check if there's any loading state
    const loadingText = await page.locator('text=Processing').count();
    console.log('Loading indicators found:', loadingText);
    
    // Check for any connection status
    const connectionStatus = await page.locator('text=/Connected|Disconnected/').allTextContents();
    console.log('Connection status:', connectionStatus);
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'test-form-state.png' });
    
    // The button should be enabled after typing (if not loading)
    await expect(submitButton).toBeEnabled();
  });
});