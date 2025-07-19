import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test.describe('English Voice Conversation with Pre-generated Audio', () => {
  const fixturesDir = path.join(__dirname, 'fixtures', 'audio', 'english');
  
  test.beforeEach(async ({ context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
  });

  test('complete English CBT conversation using audio fixtures', async ({ page }) => {
    // Define conversation flow with fixture files
    const conversationFlow = [
      {
        audioFile: 'en-greeting.wav',
        transcription: "Hello, I'm feeling anxious about an upcoming presentation at work",
        expectedKeywords: ['presentation', 'anxious', 'understand', 'tell me more']
      },
      {
        audioFile: 'en-thought-1.wav',
        transcription: "I keep thinking that everyone will judge me and notice all my mistakes",
        expectedKeywords: ['thoughts', 'evidence', 'perspective', 'judge']
      },
      {
        audioFile: 'en-insight.wav',
        transcription: "You're right, I guess I'm assuming the worst without any real evidence",
        expectedKeywords: ['reframe', 'helpful', 'positive', 'prepared']
      },
      {
        audioFile: 'en-conclusion.wav',
        transcription: "Thank you, I feel more confident now and ready to prepare properly",
        expectedKeywords: ['great', 'progress', 'strategies', 'remember']
      }
    ];

    // Mock MediaRecorder to use our pre-generated audio files
    await page.addInitScript((audioFixtures) => {
      window.audioFixtures = audioFixtures;
      window.currentFixtureIndex = 0;
      
      // Override MediaRecorder
      window.MediaRecorder = class MockMediaRecorder {
        constructor(stream, options) {
          this.stream = stream;
          this.options = options;
          this.state = 'inactive';
          this.chunks = [];
        }
        
        async start() {
          this.state = 'recording';
          
          // Load the current audio fixture
          const fixture = window.audioFixtures[window.currentFixtureIndex];
          if (fixture && fixture.audioData) {
            setTimeout(() => {
              if (this.state === 'recording') {
                // Convert base64 to blob
                const binaryString = atob(fixture.audioData);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                  bytes[i] = binaryString.charCodeAt(i);
                }
                
                const blob = new Blob([bytes], { type: 'audio/wav' });
                this.chunks.push(blob);
                
                if (this.ondataavailable) {
                  this.ondataavailable({ data: blob });
                }
              }
            }, 1500); // Simulate recording delay
          }
        }
        
        stop() {
          this.state = 'inactive';
          window.currentFixtureIndex++;
          
          setTimeout(() => {
            if (this.onstop) {
              this.onstop();
            }
          }, 100);
        }
      };
    }, await loadAudioFixtures(conversationFlow));

    await page.goto('/');
    
    // Wait for initial AI greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    const greeting = await page.getByTestId('assistant-message').first().textContent();
    console.log('AI Greeting:', greeting);
    
    // Process each phrase
    for (const [index, flow] of conversationFlow.entries()) {
      console.log(`\n--- Processing: ${flow.audioFile} ---`);
      
      // Click record button
      const recordButton = page.getByRole('button', { name: /start.*recording|microphone/i });
      await recordButton.click();
      
      // Verify recording state
      await expect(page.getByRole('button', { name: /stop.*recording|recording/i })).toBeVisible();
      const recordingIndicator = page.locator('[data-testid="recording-indicator"], .recording-active');
      await expect(recordingIndicator).toBeVisible();
      
      // Wait for "recording"
      await page.waitForTimeout(2000);
      
      // Stop recording
      await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
      
      // Wait for the transcription to appear
      await expect(page.getByText(flow.transcription)).toBeVisible({ timeout: 10000 });
      console.log('User message sent:', flow.transcription);
      
      // Wait for AI response
      const expectedMessageCount = index + 2; // Initial greeting + responses
      await expect(page.getByTestId('assistant-message')).toHaveCount(expectedMessageCount, { 
        timeout: 30000 
      });
      
      // Get and verify AI response
      const aiResponse = await page.getByTestId('assistant-message').last().textContent();
      console.log('AI Response:', aiResponse?.substring(0, 100) + '...');
      
      // Check for expected keywords in response
      const responseText = aiResponse?.toLowerCase() || '';
      const hasExpectedContent = flow.expectedKeywords.some(keyword => 
        responseText.includes(keyword.toLowerCase())
      );
      
      expect(hasExpectedContent).toBeTruthy();
      
      // Check if audio playback is available for AI response
      const lastMessage = page.getByTestId('assistant-message').last();
      const playButton = lastMessage.getByRole('button', { name: /play|audio/i });
      
      if (await playButton.count() > 0) {
        console.log('Audio playback available for response');
        // Optionally test playback
        await playButton.click();
        await page.waitForTimeout(1000);
        
        // Check for audio playing indicator
        const playingIndicator = page.locator('[data-testid="audio-playing"]');
        if (await playingIndicator.count() > 0) {
          console.log('Audio is playing');
        }
      }
      
      // Small delay between interactions
      await page.waitForTimeout(1000);
    }
    
    // Verify complete conversation
    const totalMessages = await page.getByTestId('message-bubble').count();
    expect(totalMessages).toBe(9); // 1 greeting + 4 user + 4 assistant
    
    console.log('\n✅ English conversation completed successfully!');
  });

  test('handles audio fixture with background noise', async ({ page }) => {
    // Use the sleep/worry fixture
    const fixture = {
      audioFile: 'en-sleep-worry.wav',
      transcription: "I can't sleep at night because I keep worrying about things",
      expectedKeywords: ['sleep', 'worry', 'rest', 'night', 'anxiety']
    };

    await page.addInitScript((audioFixture) => {
      window.audioFixtures = [audioFixture];
      window.currentFixtureIndex = 0;
    }, await loadAudioFixtures([fixture]));

    await page.goto('/');
    
    // Wait for greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    
    // Send audio
    const recordButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await recordButton.click();
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Verify response addresses sleep/worry
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    const response = await page.getByTestId('assistant-message').last().textContent();
    
    const hasRelevantContent = fixture.expectedKeywords.some(keyword =>
      response?.toLowerCase().includes(keyword)
    );
    expect(hasRelevantContent).toBeTruthy();
  });

  test('mixed voice and text input', async ({ page }) => {
    // First use voice fixture
    const voiceFixture = {
      audioFile: 'en-greeting.wav',
      transcription: "Hello, I'm feeling anxious about an upcoming presentation at work"
    };

    await page.addInitScript((audioFixture) => {
      window.audioFixtures = [audioFixture];
      window.currentFixtureIndex = 0;
    }, await loadAudioFixtures([voiceFixture]));

    await page.goto('/');
    
    // Wait for greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    
    // Send voice message
    const recordButton = page.getByRole('button', { name: /start.*recording|microphone/i });
    await recordButton.click();
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: /stop.*recording|recording/i }).click();
    
    // Wait for response
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    
    // Now use text input
    const thoughtInput = page.getByPlaceholder(/share.*thought/i);
    await thoughtInput.fill("I prefer to type this - what specific techniques can help?");
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify text message appears
    await expect(page.getByText("I prefer to type this")).toBeVisible();
    
    // Wait for another AI response
    await expect(page.getByTestId('assistant-message')).toHaveCount(3, { timeout: 30000 });
    
    // Verify conversation maintains context
    const lastResponse = await page.getByTestId('assistant-message').last().textContent();
    expect(lastResponse?.toLowerCase()).toMatch(/(technique|strategy|practice|prepare)/);
  });
});

// Helper function to load audio fixtures as base64
async function loadAudioFixtures(flows: Array<{audioFile: string, transcription: string}>) {
  const fixturesDir = path.join(__dirname, 'fixtures', 'audio', 'english');
  const fixtures = [];
  
  for (const flow of flows) {
    const audioPath = path.join(fixturesDir, flow.audioFile);
    let audioData = '';
    
    // Check if file exists, if not create a placeholder
    if (fs.existsSync(audioPath)) {
      const audioBuffer = fs.readFileSync(audioPath);
      audioData = audioBuffer.toString('base64');
    } else {
      console.warn(`Audio fixture not found: ${audioPath}`);
      // Create a simple placeholder audio
      audioData = createPlaceholderAudio();
    }
    
    fixtures.push({
      audioFile: flow.audioFile,
      transcription: flow.transcription,
      audioData
    });
  }
  
  return fixtures;
}

// Create placeholder audio data if fixture doesn't exist
function createPlaceholderAudio(): string {
  const sampleRate = 16000;
  const duration = 2;
  const numSamples = sampleRate * duration;
  
  const header = Buffer.alloc(44);
  header.write('RIFF', 0);
  header.writeUInt32LE(36 + numSamples * 2, 4);
  header.write('WAVE', 8);
  header.write('fmt ', 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20);
  header.writeUInt16LE(1, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(sampleRate * 2, 28);
  header.writeUInt16LE(2, 32);
  header.writeUInt16LE(16, 34);
  header.write('data', 36);
  header.writeUInt32LE(numSamples * 2, 40);
  
  const audioData = Buffer.alloc(numSamples * 2);
  for (let i = 0; i < numSamples; i++) {
    const sample = Math.sin(2 * Math.PI * 440 * i / sampleRate) * 0.3;
    audioData.writeInt16LE(Math.floor(sample * 32767), i * 2);
  }
  
  return Buffer.concat([header, audioData]).toString('base64');
}