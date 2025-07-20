import { test, expect } from '@playwright/test';
import { GoogleGenerativeAI } from '@google/generative-ai';

test.describe('English Voice Conversation with Synthetic Audio', () => {
  let genAI: GoogleGenerativeAI;
  
  test.beforeAll(() => {
    // Initialize Gemini AI
    genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  });

  test.beforeEach(async ({ context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
  });

  test('complete English CBT conversation with synthetic voice', async ({ page }) => {
    // Test conversation flow
    const conversationPhrases = [
      {
        text: "Hello, I'm feeling anxious about an upcoming presentation at work",
        expectedResponseKeywords: ['presentation', 'anxious', 'understand', 'tell me more']
      },
      {
        text: "I keep thinking that everyone will judge me and notice all my mistakes",
        expectedResponseKeywords: ['thoughts', 'evidence', 'perspective', 'judge']
      },
      {
        text: "You're right, I guess I'm assuming the worst without any real evidence",
        expectedResponseKeywords: ['reframe', 'helpful', 'positive', 'prepared']
      },
      {
        text: "Thank you, I feel more confident now and ready to prepare properly",
        expectedResponseKeywords: ['great', 'progress', 'strategies', 'remember']
      }
    ];

    await page.goto('/');
    
    // Wait for initial AI greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    const greeting = await page.getByTestId('assistant-message').first().textContent();
    console.log('AI Greeting:', greeting);
    
    // Process each phrase in the conversation
    for (const [index, phrase] of conversationPhrases.entries()) {
      console.log(`\n--- English Phrase ${index + 1} ---`);
      console.log('Sending:', phrase.text);
      
      // Generate synthetic audio using Gemini (mock for now)
      // In a real implementation, you would use Google Cloud Text-to-Speech
      await page.evaluate(async (phraseText) => {
        // Simulate audio generation
        const audioContext = new AudioContext();
        const sampleRate = 16000;
        const duration = 3; // seconds
        const numSamples = sampleRate * duration;
        
        // Create a more speech-like waveform
        const audioBuffer = audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = audioBuffer.getChannelData(0);
        
        // Generate speech-like frequencies
        for (let i = 0; i < numSamples; i++) {
          const t = i / sampleRate;
          // Mix of frequencies common in speech (100-400 Hz for fundamental)
          channelData[i] = 
            Math.sin(2 * Math.PI * 150 * t) * 0.3 +
            Math.sin(2 * Math.PI * 250 * t) * 0.2 +
            Math.sin(2 * Math.PI * 350 * t) * 0.1 +
            (Math.random() - 0.5) * 0.05; // Add some noise
        }
        
        // Store the audio data for the recording mock
        window.testAudioBuffer = audioBuffer;
        window.testTranscription = phraseText;
      }, phrase.text);
      
      // Mock the MediaRecorder to use our synthetic audio
      await page.addInitScript(() => {
        if (!window.MediaRecorderMocked) {
          window.MediaRecorderMocked = true;
          
          const OriginalMediaRecorder = window.MediaRecorder;
          window.MediaRecorder = class MockMediaRecorder extends OriginalMediaRecorder {
            constructor(stream, options) {
              super(stream, options);
              this.mockChunks = [];
            }
            
            start() {
              super.start();
              // Simulate receiving audio data
              setTimeout(() => {
                if (window.testAudioBuffer && this.state === 'recording') {
                  // Convert AudioBuffer to WAV format
                  const buffer = window.testAudioBuffer;
                  const length = buffer.length * buffer.numberOfChannels * 2 + 44;
                  const arrayBuffer = new ArrayBuffer(length);
                  const view = new DataView(arrayBuffer);
                  
                  // WAV header
                  const writeString = (offset, string) => {
                    for (let i = 0; i < string.length; i++) {
                      view.setUint8(offset + i, string.charCodeAt(i));
                    }
                  };
                  
                  writeString(0, 'RIFF');
                  view.setUint32(4, length - 8, true);
                  writeString(8, 'WAVE');
                  writeString(12, 'fmt ');
                  view.setUint32(16, 16, true);
                  view.setUint16(20, 1, true);
                  view.setUint16(22, buffer.numberOfChannels, true);
                  view.setUint32(24, buffer.sampleRate, true);
                  view.setUint32(28, buffer.sampleRate * 2, true);
                  view.setUint16(32, 2, true);
                  view.setUint16(34, 16, true);
                  writeString(36, 'data');
                  view.setUint32(40, length - 44, true);
                  
                  // Convert float samples to 16-bit PCM
                  let offset = 44;
                  const channelData = buffer.getChannelData(0);
                  for (let i = 0; i < buffer.length; i++) {
                    const sample = Math.max(-1, Math.min(1, channelData[i]));
                    view.setInt16(offset, sample * 0x7FFF, true);
                    offset += 2;
                  }
                  
                  const blob = new Blob([arrayBuffer], { type: 'audio/wav' });
                  this.mockChunks.push(blob);
                  
                  if (this.ondataavailable) {
                    this.ondataavailable({ data: blob });
                  }
                }
              }, 1000);
            }
            
            stop() {
              super.stop();
              setTimeout(() => {
                if (this.onstop) {
                  this.onstop();
                }
              }, 100);
            }
          };
        }
      });
      
      // Also mock the transcription response if the backend expects it
      await page.route('**/api/v1/conversation/transcribe', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            text: phrase.text,
            language: 'en',
            confidence: 0.95
          })
        });
      });
      
      // Click record button
      const recordButton = page.getByRole('button', { name: /start.*recording|microphone/i });
      await recordButton.click();
      
      // Verify recording state
      await expect(page.getByRole('button', { name: /stop.*recording|recording/i })).toBeVisible();
      
      // Wait for "recording"
      await page.waitForTimeout(2000);
      
      // Stop recording
      await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
      
      // Wait for the user message to appear
      await expect(page.getByText(phrase.text)).toBeVisible({ timeout: 10000 });
      
      // Wait for AI response
      const previousMessageCount = index + 1; // Initial greeting + previous responses
      await expect(page.getByTestId('assistant-message')).toHaveCount(previousMessageCount + 1, { 
        timeout: 30000 
      });
      
      // Get the AI response
      const aiResponse = await page.getByTestId('assistant-message').last().textContent();
      console.log('AI Response:', aiResponse);
      
      // Verify response contains expected keywords
      const responseText = aiResponse?.toLowerCase() || '';
      const hasExpectedContent = phrase.expectedResponseKeywords.some(keyword => 
        responseText.includes(keyword.toLowerCase())
      );
      
      expect(hasExpectedContent).toBeTruthy();
      
      // Small delay between conversations
      await page.waitForTimeout(1000);
    }
    
    // Verify complete conversation
    const totalMessages = await page.getByTestId('message-bubble').count();
    expect(totalMessages).toBe(9); // 1 greeting + 4 user + 4 assistant
    
    console.log('\n✅ English conversation completed successfully!');
  });

  test('handles English voice with background noise', async ({ page }) => {
    await page.goto('/');
    
    // Wait for greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    
    // Simulate noisy audio
    await page.evaluate(() => {
      const audioContext = new AudioContext();
      const sampleRate = 16000;
      const duration = 3;
      const numSamples = sampleRate * duration;
      
      const audioBuffer = audioContext.createBuffer(1, numSamples, sampleRate);
      const channelData = audioBuffer.getChannelData(0);
      
      // Speech with background noise
      for (let i = 0; i < numSamples; i++) {
        const t = i / sampleRate;
        // Speech frequencies
        const speech = 
          Math.sin(2 * Math.PI * 200 * t) * 0.3 +
          Math.sin(2 * Math.PI * 300 * t) * 0.2;
        // Background noise
        const noise = (Math.random() - 0.5) * 0.2;
        
        channelData[i] = speech + noise;
      }
      
      window.testAudioBuffer = audioBuffer;
      window.testTranscription = "I can't sleep at night because of worry";
    });
    
    // Record and send
    const recordButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await recordButton.click();
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Verify response addresses sleep/worry
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    const response = await page.getByTestId('assistant-message').last().textContent();
    
    expect(response?.toLowerCase()).toMatch(/(sleep|worry|rest|night|anxiety)/);
  });

  test('English voice error recovery', async ({ page }) => {
    await page.goto('/');
    
    // Wait for greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    
    // Simulate very short/empty audio
    await page.evaluate(() => {
      const audioContext = new AudioContext();
      const audioBuffer = audioContext.createBuffer(1, 8000, 16000); // 0.5 seconds
      // Leave it mostly silent
      const channelData = audioBuffer.getChannelData(0);
      for (let i = 0; i < 8000; i++) {
        channelData[i] = (Math.random() - 0.5) * 0.01; // Very quiet
      }
      window.testAudioBuffer = audioBuffer;
      window.testTranscription = ""; // Empty transcription
    });
    
    // Try to record
    const recordButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await recordButton.click();
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Should show error or allow retry
    const errorMessage = page.getByText(/couldn't hear|try again|speak louder/i);
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    
    // Either shows error or falls back to text input
    await expect(
      errorMessage.or(thoughtInput)
    ).toBeVisible({ timeout: 5000 });
    
    // Use text input as fallback
    await thoughtInput.fill("Sorry, my microphone isn't working well");
    await page.getByRole('button', { name: /send/i }).click();
    
    // Should get a response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
  });
});