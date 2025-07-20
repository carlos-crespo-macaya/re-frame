import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('Voice Workflow with Audio Simulation', () => {
  test.beforeEach(async ({ context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
  });

  test('voice conversation with mocked audio input', async ({ page }) => {
    // Method 1: Mock the MediaRecorder API to return pre-recorded audio
    await page.addInitScript(() => {
      // Mock getUserMedia to return a fake audio stream
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        // Create a mock MediaStream
        const audioContext = new AudioContext();
        const oscillator = audioContext.createOscillator();
        const destination = audioContext.createMediaStreamDestination();
        oscillator.connect(destination);
        oscillator.start();
        
        return destination.stream;
      };

      // Mock MediaRecorder to simulate recording
      window.MediaRecorder = class MockMediaRecorder {
        constructor(stream, options) {
          this.stream = stream;
          this.options = options;
          this.state = 'inactive';
          this.chunks = [];
        }

        start() {
          this.state = 'recording';
          // Simulate audio data after 2 seconds
          setTimeout(() => {
            if (this.state === 'recording') {
              // Create a mock audio blob with actual audio data
              // This could be a pre-recorded WAV file converted to blob
              const mockAudioData = new Blob(
                [new ArrayBuffer(44100 * 2 * 2)], // 2 seconds of silence
                { type: 'audio/wav' }
              );
              this.chunks.push(mockAudioData);
              
              if (this.ondataavailable) {
                this.ondataavailable({ data: mockAudioData });
              }
            }
          }, 2000);
        }

        stop() {
          this.state = 'inactive';
          if (this.onstop) {
            this.onstop();
          }
        }
      };
    });

    await page.goto('/');
    
    // Wait for initial greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 10000 });
    
    // Start voice recording
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await voiceButton.click();
    
    // Wait for mock recording
    await page.waitForTimeout(2500);
    
    // Stop recording
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // The app should process the mock audio
    // In a real implementation, you'd need to mock the transcription response too
    await expect(page.getByTestId('user-message')).toBeVisible({ timeout: 10000 });
  });

  test('voice with pre-recorded audio file upload', async ({ page }) => {
    // Method 2: Use a pre-recorded audio file
    await page.goto('/');
    
    // If your app supports file upload for audio
    const fileInput = page.locator('input[type="file"][accept*="audio"]');
    if (await fileInput.isVisible()) {
      const audioFile = path.join(__dirname, 'fixtures', 'test-audio.wav');
      await fileInput.setInputFiles(audioFile);
      
      // Wait for processing
      await expect(page.getByTestId('user-message')).toBeVisible({ timeout: 10000 });
    }
  });

  test('voice with API mocking', async ({ page }) => {
    // Method 3: Mock the API responses directly
    
    // Mock the transcription endpoint
    await page.route('**/api/v1/conversation/transcribe', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          text: 'This is a simulated voice transcription',
          success: true
        })
      });
    });
    
    // Mock the audio generation endpoint for AI responses
    await page.route('**/api/v1/conversation/synthesize', async (route) => {
      // Return a mock audio file
      const mockAudio = Buffer.alloc(44100 * 2); // 1 second of silence
      await route.fulfill({
        status: 200,
        contentType: 'audio/wav',
        body: mockAudio
      });
    });
    
    await page.goto('/');
    
    // Start recording
    const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await voiceButton.click();
    
    // Simulate recording
    await page.waitForTimeout(2000);
    
    // Stop recording - this should trigger the mocked transcription
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Check that the transcribed text appears
    await expect(page.getByText('This is a simulated voice transcription')).toBeVisible();
    
    // Wait for AI response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
  });

  test('full voice conversation with WebRTC mocking', async ({ page }) => {
    // Method 4: More sophisticated WebRTC mocking
    await page.addInitScript(() => {
      // Store original APIs
      const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
      
      // Mock WebRTC APIs
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        if (constraints.audio) {
          // Create a more realistic audio stream
          const audioContext = new AudioContext();
          const bufferSize = 4096;
          const numberOfChannels = 1;
          
          // Create a script processor to generate audio samples
          const scriptProcessor = audioContext.createScriptProcessor(
            bufferSize,
            numberOfChannels,
            numberOfChannels
          );
          
          // Generate speech-like waveform
          let phase = 0;
          scriptProcessor.onaudioprocess = (e) => {
            const output = e.outputBuffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
              // Simulate speech frequencies (100-400 Hz)
              output[i] = Math.sin(phase) * 0.3 + 
                         Math.sin(phase * 2.5) * 0.2 +
                         Math.sin(phase * 3.7) * 0.1;
              phase += 2 * Math.PI * 200 / audioContext.sampleRate;
            }
          };
          
          const destination = audioContext.createMediaStreamDestination();
          scriptProcessor.connect(destination);
          
          return destination.stream;
        }
        return originalGetUserMedia.call(navigator.mediaDevices, constraints);
      };
    });
    
    await page.goto('/');
    
    // Intercept and mock the conversation API
    await page.route('**/api/v1/conversation/message', async (route, request) => {
      const body = await request.postDataJSON();
      
      // Simulate different responses based on message count
      const responses = [
        "I hear you're testing the voice feature. How can I help you today?",
        "That's interesting. Can you tell me more about what you're experiencing?",
        "I understand. Let's explore this thought together.",
        "Thank you for sharing. Here's a different perspective to consider..."
      ];
      
      const messageCount = await page.getByTestId('assistant-message').count();
      const responseText = responses[Math.min(messageCount, responses.length - 1)];
      
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: `data: ${JSON.stringify({ 
          type: 'token', 
          content: responseText 
        })}\n\ndata: ${JSON.stringify({ 
          type: 'complete',
          audio_url: '/mock-audio.wav'
        })}\n\n`
      });
    });
    
    // Run through multiple voice interactions
    for (let i = 0; i < 3; i++) {
      const voiceButton = page.getByRole('button', { name: /start.*recording|microphone/i });
      await voiceButton.click();
      await page.waitForTimeout(2000);
      await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
      
      // Wait for response
      await expect(page.getByTestId('assistant-message')).toHaveCount(i + 2, { timeout: 30000 });
    }
  });
});