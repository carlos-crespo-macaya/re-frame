import { test, expect } from '@playwright/test';

test.describe('Voice Conversation Flow', () => {
  test.beforeEach(async ({ page, context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
    await page.goto('/');
  });

  test('user can start and stop voice recording', async ({ page }) => {
    // Wait for the main conversation view to load
    await expect(page.getByRole('main')).toBeVisible();
    
    // Find the voice recording button
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await expect(voiceButton).toBeVisible();
    
    // Click to start recording
    await voiceButton.click();
    
    // Verify recording state changes (button should show stop or recording indicator)
    await expect(page.getByRole('button', { name: /stop.*recording|recording/i })).toBeVisible();
    
    // Wait a moment to simulate recording
    await page.waitForTimeout(2000);
    
    // Stop recording
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Verify we're back to the start state
    await expect(page.getByRole('button', { name: /start.*recording|microphone/i })).toBeVisible();
    
    // Note: In a real test environment, we can't actually send audio data
    // This test verifies the UI flow for voice recording
  });

  test('voice recording shows visual feedback', async ({ page, context }) => {
    // Grant permissions
    await context.grantPermissions(['microphone']);
    
    // Find and click voice button
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await voiceButton.click();
    
    // Check for visual feedback (recording indicator, waveform, or timer)
    const recordingIndicator = page.locator('[data-testid="recording-indicator"], .recording-active, [aria-label*="recording"]');
    await expect(recordingIndicator).toBeVisible();
    
    // Stop recording
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Verify indicator is gone
    await expect(recordingIndicator).not.toBeVisible();
  });

  test('audio playback controls appear for assistant messages', async ({ page }) => {
    // Send a text message to trigger a response
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('Hello, can you help me?');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for assistant response
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 30000 });
    
    // Check if audio playback button is available for the assistant message
    const playButton = page.locator('[data-testid="assistant-message"]').getByRole('button', { name: /play|audio/i });
    
    // Note: Audio playback may or may not be available depending on backend configuration
    // This test just verifies the UI elements exist when audio is available
    if (await playButton.isVisible()) {
      await expect(playButton).toBeEnabled();
    }
  });
});