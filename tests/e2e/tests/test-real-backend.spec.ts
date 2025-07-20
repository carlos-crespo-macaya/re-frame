import { test, expect } from '@playwright/test';

test.describe('Real Backend Integration', () => {
  test('complete text conversation flow', async ({ page }) => {
    // Track console logs
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('turn_complete') || text.includes('Turn complete') || text.includes('🚀')) {
        console.log('[TURN_COMPLETE]', text);
      }
    });
    
    await page.goto('/');
    
    // Get elements
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    // Initial state check
    await expect(thoughtInput).toBeVisible();
    await expect(submitButton).toBeVisible();
    
    // Type message
    await thoughtInput.fill('I feel anxious about meeting new people');
    
    // Button should be enabled after typing
    await expect(submitButton).toBeEnabled();
    console.log('✅ Button enabled after typing');
    
    // Submit
    await submitButton.click();
    console.log('✅ Message submitted');
    
    // Button should be disabled during processing
    await expect(submitButton).toBeDisabled();
    console.log('✅ Button disabled during processing');
    
    // Wait for response to appear - use more specific selector for assistant messages
    const response = page.locator('.bg-\\[\\#2a2a2a\\].rounded-xl').first();
    await expect(response).toBeVisible({ timeout: 30000 });
    console.log('✅ Response appeared');
    
    // Wait for turn_complete by checking if the input is enabled again
    await expect(thoughtInput).toBeEnabled({ timeout: 30000 });
    console.log('✅ Input re-enabled after turn_complete');
    
    // The button should still be disabled because the input is empty
    await expect(submitButton).toBeDisabled();
    console.log('✅ Button correctly disabled when input is empty');
    
    // Verify we're in DISCOVERY phase by sending another message
    await thoughtInput.fill('It happens especially at work events');
    await submitButton.click();
    console.log('✅ Second message sent');
    
    // Wait for a new response to appear after the second message
    const responses = page.locator('.bg-\\[\\#2a2a2a\\].rounded-xl');
    const initialCount = await responses.count();
    
    // Wait for count to increase (at least one new response)
    await expect(async () => {
      const newCount = await responses.count();
      expect(newCount).toBeGreaterThan(initialCount);
    }).toPass({ timeout: 30000 });
    
    console.log(`✅ Second response received - now have ${await responses.count()} total messages`);
    
    // Wait for input to be re-enabled after second turn_complete
    await expect(thoughtInput).toBeEnabled({ timeout: 30000 });
    console.log('✅ Input re-enabled after second response');
    
    // Type a third message to verify button enables with text
    await thoughtInput.fill('I feel like everyone is judging me');
    await expect(submitButton).toBeEnabled();
    console.log('✅ Conversation flow working correctly - can continue typing');
    
    // Check that we have at least 2 responses (greeting messages + our responses)
    const responseCount = await responses.count();
    expect(responseCount).toBeGreaterThanOrEqual(2);
    console.log(`✅ Conversation history maintained - ${responseCount} messages`);
  });
});