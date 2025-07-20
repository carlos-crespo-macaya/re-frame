import { test, expect } from '@playwright/test';

test.describe('Text Conversation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('user can have a text conversation', async ({ page }) => {
    // Wait for the main conversation view to load
    await expect(page.getByRole('main')).toBeVisible();
    
    // Find and fill the thought input form
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await expect(thoughtInput).toBeVisible();
    
    // Type a test message
    await thoughtInput.fill('I feel anxious about my upcoming presentation');
    
    // Submit the form
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for the message to appear in the conversation
    await expect(page.getByText('I feel anxious about my upcoming presentation')).toBeVisible();
    
    // Wait for AI response (checking for any assistant message bubble)
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 30000 });
    
    // Verify the conversation continues
    await thoughtInput.fill('What techniques can help me feel more confident?');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify second message appears
    await expect(page.getByText('What techniques can help me feel more confident?')).toBeVisible();
    
    // Verify we get another AI response
    const assistantMessages = page.getByTestId('assistant-message');
    await expect(assistantMessages).toHaveCount(2, { timeout: 30000 });
  });

  test('user can see message timestamps', async ({ page }) => {
    // Send a message
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('Test message');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Check that timestamp is visible
    await expect(page.getByTestId('message-timestamp')).toBeVisible();
  });
});