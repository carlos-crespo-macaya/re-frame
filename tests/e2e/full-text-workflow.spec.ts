import { test, expect } from '@playwright/test';

test.describe('Full Text Conversation Workflow', () => {
  test('complete CBT conversation flow', async ({ page }) => {
    // Start at homepage
    await page.goto('/');
    
    // Wait for the app to load
    await expect(page.getByRole('main')).toBeVisible();
    
    // Phase 1: Greeting - AI should greet first
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 10000 });
    const greetingMessage = await page.getByTestId('assistant-message').first().textContent();
    expect(greetingMessage).toContain('Hello');
    
    // Phase 2: Discovery - Share a thought
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('I have a presentation tomorrow and I feel like everyone will judge me negatively');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for user message to appear
    await expect(page.getByText('I have a presentation tomorrow')).toBeVisible();
    
    // Wait for AI response (should acknowledge and explore)
    const assistantMessages = page.getByTestId('assistant-message');
    await expect(assistantMessages).toHaveCount(2, { timeout: 30000 });
    
    // Continue conversation - provide more context
    await thoughtInput.fill('I keep thinking they will notice every mistake I make and think I am incompetent');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for the conversation to develop
    await expect(assistantMessages).toHaveCount(3, { timeout: 30000 });
    
    // Phase 3: Reframing - AI should offer cognitive reframing
    const reframingResponse = await assistantMessages.nth(2).textContent();
    expect(reframingResponse?.toLowerCase()).toMatch(/(perspective|reframe|think|consider|evidence)/);
    
    // Respond to reframing
    await thoughtInput.fill('That makes sense. I guess not everyone is focused on finding my flaws');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for final messages
    await expect(assistantMessages).toHaveCount(4, { timeout: 30000 });
    
    // Phase 4: Summary - Check if conversation can conclude
    await thoughtInput.fill('Thank you, I feel more prepared now');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for potential summary or conclusion
    await expect(assistantMessages).toHaveCount(5, { timeout: 30000 });
    
    // Verify the conversation structure
    const allMessages = await page.getByTestId('message-bubble').count();
    expect(allMessages).toBeGreaterThanOrEqual(8); // At least 4 user + 4 assistant messages
    
    // Check for proper message ordering (alternating user/assistant)
    const firstMessage = await page.getByTestId('message-bubble').first();
    expect(await firstMessage.getAttribute('data-sender')).toBe('assistant');
  });

  test('handles session continuation', async ({ page }) => {
    // Start a conversation
    await page.goto('/');
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 10000 });
    
    // Send a message
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('I am worried about my job interview');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    
    // Get session ID from the page (if exposed)
    const sessionId = await page.evaluate(() => {
      return window.sessionStorage.getItem('session_id') || 
             window.localStorage.getItem('session_id');
    });
    
    // Reload the page
    await page.reload();
    
    // Check if conversation history is maintained
    const messagesAfterReload = await page.getByTestId('message-bubble').count();
    expect(messagesAfterReload).toBeGreaterThanOrEqual(2);
    
    // Continue the conversation
    await thoughtInput.fill('I think they will ask difficult questions');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify conversation continues with context
    await expect(page.getByTestId('assistant-message')).toHaveCount(3, { timeout: 30000 });
    const latestResponse = await page.getByTestId('assistant-message').last().textContent();
    expect(latestResponse?.toLowerCase()).toMatch(/(interview|question|prepare)/);
  });

  test('handles error scenarios gracefully', async ({ page }) => {
    await page.goto('/');
    
    // Wait for initial load
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 10000 });
    
    // Simulate network interruption by blocking API calls
    await page.route('**/api/v1/conversation/message', route => route.abort());
    
    // Try to send a message
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('Test message during network issue');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Should show error message or retry mechanism
    await expect(page.getByText(/error|retry|connection/i)).toBeVisible({ timeout: 10000 });
    
    // Restore network
    await page.unroute('**/api/v1/conversation/message');
    
    // Retry sending
    const retryButton = page.getByRole('button', { name: /retry|send again/i });
    if (await retryButton.isVisible()) {
      await retryButton.click();
    } else {
      await page.getByRole('button', { name: /send/i }).click();
    }
    
    // Should eventually succeed
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
  });
});