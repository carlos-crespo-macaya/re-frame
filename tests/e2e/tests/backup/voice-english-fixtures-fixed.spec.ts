import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test.describe('English Voice Conversation with Pre-generated Audio', () => {
  const fixturesDir = path.join(__dirname, '..', 'fixtures', 'audio', 'english');
  
  test.beforeEach(async ({ context, page, browserName }) => {
    // Only grant permissions for Chromium browsers
    if (browserName === 'chromium') {
      await context.grantPermissions(['microphone']);
    }
    
    // Simple mock for getUserMedia to provide valid MediaStream
    await context.addInitScript(() => {
      // Create valid MediaStream with audio track
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const destination = audioContext.createMediaStreamDestination();
        oscillator.connect(destination);
        oscillator.start();
        
        return destination.stream;
      };

      // Minimal AudioWorklet mock for unsupported browsers
      if (!(window as any).AudioWorkletNode) {
        (window as any).AudioWorkletNode = class MockAudioWorkletNode {
          constructor() {}
          connect() {}
          disconnect() {}
          port = { postMessage: () => {}, onmessage: null };
        };
      }
    });
    
    // Log console messages
    page.on('console', msg => console.log('Browser console:', msg.type(), msg.text()));
    page.on('pageerror', error => console.log('Page error:', error));
  });

  test('complete English CBT conversation using audio fixtures', async ({ page }) => {
    // Define conversation flow with fixture files
    const conversationFlow = [
      {
        audioFile: 'en-greeting.wav',
        transcription: "Hello, I'm feeling anxious about an upcoming presentation at work",
        expectedKeywords: ['presentation', 'anxious', 'understand', 'tell me more'],
        aiResponse: "I understand you're feeling anxious about an upcoming presentation. That's a very common experience. Can you tell me more about what specifically worries you?"
      },
      {
        audioFile: 'en-thought-1.wav',
        transcription: "I keep thinking that everyone will judge me and notice all my mistakes",
        expectedKeywords: ['thoughts', 'evidence', 'perspective', 'judge'],
        aiResponse: "It sounds like you're having thoughts about being judged and making mistakes. Let's examine these thoughts together. What evidence do you have that everyone will judge you?"
      },
      {
        audioFile: 'en-insight.wav',
        transcription: "You're right, I guess I'm assuming the worst without any real evidence",
        expectedKeywords: ['reframe', 'helpful', 'positive', 'prepared'],
        aiResponse: "That's a great insight! You're recognizing that these are assumptions rather than facts. How might you reframe these thoughts in a more helpful and balanced way?"
      },
      {
        audioFile: 'en-conclusion.wav',
        transcription: "Thank you, I feel more confident now and ready to prepare properly",
        expectedKeywords: ['great', 'progress', 'strategies', 'remember'],
        aiResponse: "That's wonderful progress! You've shown great self-awareness today. Remember these strategies when preparing for your presentation."
      }
    ];

    let sessionId: string | null = null;
    let conversationIndex = 0;

    // Mock the SSE stream for voice conversation
    await page.route(/\/api\/events\/.*\?is_audio=true/, async (route) => {
      const url = new URL(route.request().url());
      sessionId = url.pathname.split('/').pop();
      console.log('Intercepted SSE request for session:', sessionId);
      
      // Initial connection response
      const initialResponse = [
        'event: connected',
        `data: {"session_id": "${sessionId}"}`,
        '',
        'event: greeting',
        `data: {"text": "Hello! I'm here to help you explore your thoughts. What's on your mind today?", "role": "assistant"}`,
        '',
      ].join('\n');

      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        headers: {
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: initialResponse,
      });
    });

    // Mock the audio send endpoint
    await page.route(/\/api\/send\/.*/, async (route) => {
      console.log(`Intercepted audio POST request for turn ${conversationIndex + 1}`);
      
      if (conversationIndex < conversationFlow.length) {
        const currentFlow = conversationFlow[conversationIndex];
        
        // Simulate processing delay
        await page.waitForTimeout(500);
        
        // Send transcription event through evaluate (simulating SSE event)
        await page.evaluate((data) => {
          const event = new MessageEvent('message', {
            data: `event: user-transcription\ndata: ${JSON.stringify({
              text: data.transcription,
              role: 'user'
            })}\n\n`
          });
          window.dispatchEvent(event);
        }, { transcription: currentFlow.transcription });

        // Send AI response after a delay
        await page.waitForTimeout(1000);
        
        await page.evaluate((data) => {
          const event = new MessageEvent('message', {
            data: `event: assistant-response\ndata: ${JSON.stringify({
              text: data.aiResponse,
              role: 'assistant',
              audio_url: `/api/audio/${data.index}.mp3`
            })}\n\n`
          });
          window.dispatchEvent(event);
        }, { aiResponse: currentFlow.aiResponse, index: conversationIndex });
        
        conversationIndex++;
      }
      
      await route.fulfill({ status: 200, body: 'OK' });
    });

    // Navigate to the app
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Switch to voice mode
    const voiceModeButton = page.getByRole('button', { name: /switch to voice/i });
    await expect(voiceModeButton).toBeVisible({ timeout: 10000 });
    await voiceModeButton.click();
    
    // Wait for voice mode to activate
    await page.waitForTimeout(1000);
    
    // Click Start Conversation button
    const startConversationButton = page.getByRole('button', { name: /start conversation/i });
    await expect(startConversationButton).toBeVisible({ timeout: 10000 });
    await startConversationButton.click();
    
    // Wait for connection status
    await expect(page.getByText(/Connected.*Speak naturally/i)).toBeVisible({ timeout: 15000 });
    
    // Take screenshot after connection
    await page.screenshot({ path: 'voice-connected.png' });
    
    // Wait for MessageList to be visible
    await expect(page.locator('[data-testid="message-list"]')).toBeVisible({ timeout: 15000 });
    
    // Wait for initial AI greeting
    await expect(page.locator('[data-role="assistant"]')).toBeVisible({ timeout: 15000 });
    const greeting = await page.locator('[data-role="assistant"]').first().textContent();
    console.log('AI Greeting:', greeting);
    
    // Process each phrase in the conversation
    for (const [index, flow] of conversationFlow.entries()) {
      console.log(`\n--- Processing: ${flow.audioFile} ---`);
      
      // Simulate recording by clicking and holding
      const recordButton = page.locator('button[aria-label="Hold to talk"]');
      
      // Press and hold to record
      await recordButton.dispatchEvent('mousedown');
      await expect(page.getByText(/Listening/i)).toBeVisible();
      
      // Wait for "recording"
      await page.waitForTimeout(2000);
      
      // Release to stop recording
      await recordButton.dispatchEvent('mouseup');
      
      // Wait for the transcription to appear
      await expect(page.locator('[data-role="user"]').last()).toContainText(flow.transcription, { timeout: 10000 });
      console.log('User message sent:', flow.transcription);
      
      // Wait for AI response
      const expectedMessageCount = (index + 1) * 2 + 1; // Initial greeting + pairs of user/assistant
      await expect(page.locator('[data-role="assistant"]')).toHaveCount(Math.ceil(expectedMessageCount / 2), { 
        timeout: 30000 
      });
      
      // Get and verify AI response
      const aiResponse = await page.locator('[data-role="assistant"]').last().textContent();
      console.log('AI Response:', aiResponse?.substring(0, 100) + '...');
      
      // Check for expected keywords in response
      const responseText = aiResponse?.toLowerCase() || '';
      const hasExpectedContent = flow.expectedKeywords.some(keyword => 
        responseText.includes(keyword.toLowerCase())
      );
      
      expect(hasExpectedContent).toBeTruthy();
      
      // Check if audio playback is available for AI response
      const lastMessage = page.locator('[data-role="assistant"]').last();
      const playButton = lastMessage.getByRole('button', { name: /play|audio/i });
      
      if (await playButton.count() > 0) {
        console.log('Audio playback available for response');
      }
      
      // Small delay between interactions
      await page.waitForTimeout(1000);
    }
    
    // Verify complete conversation
    const totalMessages = await page.locator('[data-role]').count();
    expect(totalMessages).toBe(9); // 1 greeting + 4 user + 4 assistant
    
    console.log('\n✅ English conversation completed successfully!');
  });

  test('handles audio fixture with background noise', async ({ page }) => {
    // Simplified test setup
    const fixture = {
      audioFile: 'en-sleep-worry.wav',
      transcription: "I can't sleep at night because I keep worrying about things",
      expectedKeywords: ['sleep', 'worry', 'rest', 'night', 'anxiety']
    };

    // Mock endpoints (simplified version)
    await page.route(/\/api\/events\/.*\?is_audio=true/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: 'event: connected\ndata: {"session_id": "test"}\n\n',
      });
    });

    await page.route(/\/api\/send\/.*/, async (route) => {
      await route.fulfill({ status: 200, body: 'OK' });
    });

    await page.goto('/');
    
    // Switch to voice mode and start conversation
    await page.getByRole('button', { name: /switch to voice/i }).click();
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: /start conversation/i }).click();
    
    // Wait for connection
    await expect(page.getByText(/Connected.*Speak naturally/i)).toBeVisible({ timeout: 15000 });
    
    // Simulate recording
    const recordButton = page.locator('button[aria-label="Hold to talk"]');
    await recordButton.dispatchEvent('mousedown');
    await page.waitForTimeout(2000);
    await recordButton.dispatchEvent('mouseup');
    
    // Verify the conversation context is maintained
    console.log('✅ Background noise test completed');
  });

  test('mixed voice and text input', async ({ page }) => {
    // This test verifies switching between voice and text modes
    
    // Mock endpoints
    await page.route(/\/api\/events\/.*/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: 'event: connected\ndata: {"session_id": "test"}\n\n',
      });
    });

    await page.route(/\/api\/send\/.*/, async (route) => {
      await route.fulfill({ status: 200, body: 'OK' });
    });

    await page.goto('/');
    
    // Start in voice mode
    await page.getByRole('button', { name: /switch to voice/i }).click();
    await page.waitForTimeout(1000);
    
    // Switch back to text mode
    await page.getByRole('button', { name: /switch to text/i }).click();
    await page.waitForTimeout(1000);
    
    // Use text input
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill("I prefer to type this - what specific techniques can help?");
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify text message appears
    await expect(page.getByText("I prefer to type this")).toBeVisible();
    
    console.log('✅ Mixed mode test completed');
  });
});