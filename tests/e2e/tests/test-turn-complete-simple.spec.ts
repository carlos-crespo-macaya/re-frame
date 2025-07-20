import { test, expect } from '@playwright/test';

test.describe('Simple Turn Complete Test', () => {
  test('turn_complete event properly re-enables input', async ({ page }) => {
    // Enable console logging
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('turn_complete') || text.includes('Turn complete') || text.includes('🎯') || text.includes('🚀')) {
        console.log('[TURN_COMPLETE]', text);
      }
    });
    
    await page.goto('/');
    
    // Wait for connection
    await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
    console.log('✅ Connected to SSE');
    
    // Get initial state
    const initialButtonState = await page.getByRole('button', { name: /generate perspective|send/i }).isDisabled();
    const initialTextareaState = await page.getByPlaceholder(/what happened|share your thought/i).isDisabled();
    console.log('Initial state - Button disabled:', initialButtonState, 'Textarea disabled:', initialTextareaState);
    
    // Type a message
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    await thoughtInput.fill("I need help with my anxiety");
    
    // Submit
    await page.getByRole('button', { name: /generate perspective|send/i }).click();
    console.log('✅ Message submitted');
    
    // Wait for response to appear
    await page.waitForSelector('.bg-\\[\\#2a2a2a\\]', { timeout: 10000 });
    console.log('✅ Response appeared');
    
    // Check state during loading
    const loadingButtonState = await page.getByRole('button', { name: /generate perspective|send/i }).isDisabled();
    const loadingTextareaState = await page.getByPlaceholder(/what happened|share your thought/i).isDisabled();
    console.log('During loading - Button disabled:', loadingButtonState, 'Textarea disabled:', loadingTextareaState);
    
    // Wait for turn_complete by checking if input is re-enabled
    let attempts = 0;
    let inputEnabled = false;
    
    while (attempts < 30 && !inputEnabled) { // 15 seconds timeout
      await page.waitForTimeout(500);
      
      const buttonDisabled = await page.getByRole('button', { name: /generate perspective|send/i }).isDisabled();
      const textareaDisabled = await page.getByPlaceholder(/what happened|share your thought/i).isDisabled();
      
      console.log(`Attempt ${attempts + 1} - Button disabled: ${buttonDisabled}, Textarea disabled: ${textareaDisabled}`);
      
      inputEnabled = !buttonDisabled && !textareaDisabled;
      attempts++;
    }
    
    if (!inputEnabled) {
      console.log('❌ FAILURE: Input never re-enabled after 15 seconds');
      
      // Log page state for debugging
      const responseCount = await page.locator('.bg-\\[\\#2a2a2a\\]').count();
      console.log('Number of responses:', responseCount);
      
      // Check if turn_complete was logged
      const logs = await page.evaluate(() => (window as any).consoleLogs || []);
      const hasTurnComplete = logs.some((log: string) => log.includes('turn_complete'));
      console.log('Turn complete in logs:', hasTurnComplete);
    }
    
    // Final assertion
    await expect(page.getByRole('button', { name: /generate perspective|send/i })).toBeEnabled();
    await expect(page.getByPlaceholder(/what happened|share your thought/i)).toBeEnabled();
    
    console.log('✅ SUCCESS: Input re-enabled after turn_complete');
  });
});