import { test, expect } from '@playwright/test';

test.describe('Full Voice Conversation Workflow', () => {
  test.beforeEach(async ({ context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
  });

  test('complete voice conversation flow', async ({ page }) => {
    await page.goto('/');
    
    // Wait for initial greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 10000 });
    
    // Check if audio playback is available for greeting
    const playButton = page.getByTestId('assistant-message').first()
      .getByRole('button', { name: /play|audio/i });
    
    if (await playButton.isVisible()) {
      // Test audio playback
      await playButton.click();
      
      // Check for audio playing indicator
      await expect(page.getByTestId('audio-playing-indicator')).toBeVisible();
      
      // Wait a moment for audio to play
      await page.waitForTimeout(2000);
      
      // Stop audio if there's a stop button
      const stopButton = page.getByRole('button', { name: /stop|pause/i });
      if (await stopButton.isVisible()) {
        await stopButton.click();
      }
    }
    
    // Start voice recording
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await expect(voiceButton).toBeVisible();
    await voiceButton.click();
    
    // Verify recording state
    await expect(page.getByRole('button', { name: /stop.*recording|recording/i })).toBeVisible();
    
    // Check for visual feedback
    const recordingIndicator = page.locator('[data-testid="recording-indicator"], .recording-active');
    await expect(recordingIndicator).toBeVisible();
    
    // Simulate recording for 3 seconds
    await page.waitForTimeout(3000);
    
    // Stop recording
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Wait for transcription and message to appear
    // Note: In real scenario, this would transcribe actual audio
    await expect(page.getByTestId('user-message')).toBeVisible({ timeout: 10000 });
    
    // Wait for AI voice response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    
    // Check if voice response auto-plays
    const newPlayButton = page.getByTestId('assistant-message').last()
      .getByRole('button', { name: /play|audio/i });
    
    if (await newPlayButton.isVisible()) {
      // Voice response is available
      expect(await newPlayButton.isEnabled()).toBeTruthy();
    }
    
    // Test multiple voice interactions
    for (let i = 0; i < 2; i++) {
      // Start another recording
      await voiceButton.click();
      await expect(recordingIndicator).toBeVisible();
      await page.waitForTimeout(2000);
      await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
      
      // Wait for response
      await expect(page.getByTestId('assistant-message')).toHaveCount(3 + i, { timeout: 30000 });
    }
    
    // Verify conversation flow maintained voice context
    const allMessages = await page.getByTestId('message-bubble').count();
    expect(allMessages).toBeGreaterThanOrEqual(6);
  });

  test('voice recording with text fallback', async ({ page }) => {
    await page.goto('/');
    
    // Wait for initial greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 10000 });
    
    // Start with voice
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await voiceButton.click();
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Wait for any response
    await page.waitForTimeout(2000);
    
    // Switch to text input
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('I prefer to type this thought instead');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify text message appears
    await expect(page.getByText('I prefer to type this thought instead')).toBeVisible();
    
    // Wait for response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    
    // Switch back to voice
    await voiceButton.click();
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Verify mixed mode conversation works
    const messages = await page.getByTestId('message-bubble').count();
    expect(messages).toBeGreaterThanOrEqual(3);
  });

  test('audio playback controls', async ({ page }) => {
    await page.goto('/');
    
    // Send a text message to get a response with audio
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill('Tell me something encouraging');
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for AI response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    
    // Find audio controls if available
    const audioMessage = page.getByTestId('assistant-message').last();
    const playButton = audioMessage.getByRole('button', { name: /play|audio/i });
    
    if (await playButton.isVisible()) {
      // Test play
      await playButton.click();
      
      // Check for playback controls
      const playbackControls = page.getByTestId('playback-controls');
      if (await playbackControls.isVisible()) {
        // Test pause
        const pauseButton = playbackControls.getByRole('button', { name: /pause/i });
        if (await pauseButton.isVisible()) {
          await pauseButton.click();
          await expect(playbackControls.getByRole('button', { name: /play|resume/i })).toBeVisible();
        }
        
        // Test skip if available
        const skipButton = playbackControls.getByRole('button', { name: /skip|forward/i });
        if (await skipButton.isVisible()) {
          await skipButton.click();
        }
        
        // Test volume if available
        const volumeSlider = playbackControls.getByRole('slider', { name: /volume/i });
        if (await volumeSlider.isVisible()) {
          await volumeSlider.fill('0.5');
        }
      }
    }
  });

  test('voice error handling', async ({ page, context }) => {
    // Revoke microphone permission to simulate error
    await context.clearPermissions();
    
    await page.goto('/');
    
    // Try to use voice without permission
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await voiceButton.click();
    
    // Should show permission error
    await expect(page.getByText(/permission|microphone|access/i)).toBeVisible({ timeout: 5000 });
    
    // Grant permission and retry
    await context.grantPermissions(['microphone']);
    
    // Dismiss error if there's a button
    const dismissButton = page.getByRole('button', { name: /dismiss|ok|close/i });
    if (await dismissButton.isVisible()) {
      await dismissButton.click();
    }
    
    // Try voice again
    await voiceButton.click();
    await expect(page.getByRole('button', { name: /stop.*recording|recording/i })).toBeVisible();
  });
});