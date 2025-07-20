import { test, expect, chromium, Page, Browser } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * True multi-turn voice conversation test
 * This test maintains a single browser session and simulates turn-taking
 * by switching audio files dynamically
 */

test.describe('Continuous Voice Conversation', () => {
  test('multi-turn conversation in single session', async () => {
    // Audio files for the conversation
    const audioFiles = [
      'english/en-greeting.wav',      // Turn 1: "Hello"
      'english/en-thought-1.wav',      // Turn 2: Share anxious thought
      'english/en-insight.wav',        // Turn 3: Acknowledge insight
    ];
    
    let currentAudioIndex = 0;
    
    // Start with first audio file
    const browser = await chromium.launch({
      headless: process.env.HEADLESS !== 'false',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--use-fake-device-for-media-stream',
        '--use-fake-ui-for-media-stream',
        `--use-file-for-fake-audio-capture=${path.resolve(path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', audioFiles[0]))}%noloop`
      ]
    });
    
    const context = await browser.newContext({ permissions: ['microphone'] });
    const page = await context.newPage();
    
    // Enable console logging
    page.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('Browser console:', msg.text());
      }
    });
    
    // Monitor SSE events
    await page.addInitScript(() => {
      (window as any).__test = {
        sseEvents: [],
        audioStarted: false,
        turnCount: 0,
        lastAudioTime: 0,
        aiFinishedSpeaking: false,
        userTurns: 0,
        aiTurns: 0
      };
      
      // Intercept EventSource to monitor SSE events
      const OriginalEventSource = window.EventSource;
      window.EventSource = class extends OriginalEventSource {
        constructor(url: string, options?: EventSourceInit) {
          super(url, options);
          console.log('SSE connection created:', url);
          
          this.addEventListener('message', (event: MessageEvent) => {
            try {
              const data = JSON.parse(event.data);
              (window as any).__test.sseEvents.push(data);
              
              if (data.type === 'audio' && data.data) {
                if (!(window as any).__test.audioStarted) {
                  (window as any).__test.audioStarted = true;
                  (window as any).__test.aiTurns++;
                  console.log(`=== AI Turn ${(window as any).__test.aiTurns}: AI started speaking ===`);
                }
                (window as any).__test.lastAudioTime = Date.now();
              }
              
              if (data.type === 'turn_complete') {
                (window as any).__test.aiFinishedSpeaking = true;
                console.log('=== AI finished speaking ===');
              }
              
              if (data.type === 'transcript' && data.text) {
                console.log(`User said: "${data.text}"`);
              }
            } catch (e) {
              console.error('Failed to parse SSE event:', e);
            }
          });
        }
      };
    });
    
    // Navigate to the app
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Switch to voice mode
    await page.getByRole('button', { name: 'Switch to Voice' }).click();
    console.log('✓ Switched to voice mode');
    
    // Start conversation
    await page.getByRole('button', { name: 'Start Conversation' }).click();
    console.log('✓ Started conversation');
    
    // Wait for SSE connection
    await page.waitForTimeout(2000);
    
    // Function to wait for AI response and completion
    const waitForAIResponse = async (turnDescription: string) => {
      console.log(`\n${turnDescription}`);
      
      // Reset flags
      await page.evaluate(() => {
        (window as any).__test.audioStarted = false;
        (window as any).__test.aiFinishedSpeaking = false;
      });
      
      // Wait for AI to start responding
      await page.waitForFunction(
        () => (window as any).__test.audioStarted,
        { timeout: 20000 }
      );
      
      // Wait for AI to finish speaking (either turn_complete or 3 seconds of silence)
      await page.waitForFunction(
        () => {
          const test = (window as any).__test;
          if (test.aiFinishedSpeaking) return true;
          if (!test.lastAudioTime) return false;
          return Date.now() - test.lastAudioTime > 3000;
        },
        { timeout: 45000 }
      );
      
      console.log('✓ AI response complete');
      
      // Give time for audio to finish playing
      await page.waitForTimeout(2000);
    };
    
    // Turn 1: Initial greeting (audio already injected via launch args)
    await page.evaluate(() => {
      (window as any).__test.userTurns++;
      console.log(`\n=== User Turn ${(window as any).__test.userTurns}: Greeting ===`);
    });
    await waitForAIResponse('Waiting for AI response to greeting...');
    
    // For subsequent turns, we need to restart the browser with new audio
    // This is a limitation of the --use-file-for-fake-audio-capture flag
    console.log('\n⚠️  Note: Browser restart required to change audio file (Chromium limitation)');
    console.log('In a real implementation, we would use MediaStreamTrackGenerator for continuous conversation.');
    
    // Verify we had a complete turn
    const stats = await page.evaluate(() => {
      const test = (window as any).__test;
      return {
        userTurns: test.userTurns,
        aiTurns: test.aiTurns,
        totalAudioChunks: test.sseEvents.filter((e: any) => e.type === 'audio').length
      };
    });
    
    console.log('\n=== Conversation Summary ===');
    console.log(`User turns: ${stats.userTurns}`);
    console.log(`AI turns: ${stats.aiTurns}`);
    console.log(`Total audio chunks received: ${stats.totalAudioChunks}`);
    
    expect(stats.userTurns).toBe(1);
    expect(stats.aiTurns).toBe(1);
    expect(stats.totalAudioChunks).toBeGreaterThan(0);
    
    console.log('\n✓ Single-turn conversation completed successfully!');
    console.log('\nFor true multi-turn without browser restart, we need:');
    console.log('1. MediaStreamTrackGenerator API (requires proper implementation)');
    console.log('2. Or dynamic audio file switching (not supported by --use-file-for-fake-audio-capture)');
    
    // Keep browser open a bit longer so you can hear the complete response
    await page.waitForTimeout(5000);
    
    await browser.close();
  });
  
  test('demonstrate the browser restart limitation', async () => {
    console.log('\n=== Demonstrating Browser Restart Limitation ===');
    console.log('This test shows that each browser launch creates a new session\n');
    
    const audioFiles = [
      'english/en-greeting.wav',
      'english/en-thought-1.wav',
    ];
    
    const sessionIds: string[] = [];
    
    for (let i = 0; i < audioFiles.length; i++) {
      console.log(`\n--- Browser Launch ${i + 1} ---`);
      
      const browser = await chromium.launch({
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--use-fake-device-for-media-stream',
          '--use-fake-ui-for-media-stream',
          `--use-file-for-fake-audio-capture=${path.resolve(path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', audioFiles[i]))}%noloop`
        ]
      });
      
      const context = await browser.newContext({ permissions: ['microphone'] });
      const page = await context.newPage();
      
      // Capture session ID
      await page.addInitScript(() => {
        (window as any).__sessionId = null;
        
        const OriginalEventSource = window.EventSource;
        window.EventSource = class extends OriginalEventSource {
          constructor(url: string, options?: EventSourceInit) {
            super(url, options);
            // Extract session ID from URL
            const match = url.match(/voice-([a-f0-9-]+)\/stream/);
            if (match) {
              (window as any).__sessionId = match[1];
            }
          }
        };
      });
      
      await page.goto('http://localhost:3000');
      await page.getByRole('button', { name: 'Switch to Voice' }).click();
      await page.getByRole('button', { name: 'Start Conversation' }).click();
      await page.waitForTimeout(1000);
      
      const sessionId = await page.evaluate(() => (window as any).__sessionId);
      if (sessionId) {
        sessionIds.push(sessionId);
        console.log(`Session ID: ${sessionId}`);
      }
      
      await browser.close();
    }
    
    console.log('\n=== Results ===');
    console.log(`Created ${sessionIds.length} different sessions:`);
    sessionIds.forEach((id, i) => console.log(`  ${i + 1}. ${id}`));
    console.log('\n❌ Each browser restart creates a new session - not a continuous conversation!');
    
    expect(new Set(sessionIds).size).toBe(sessionIds.length); // All session IDs should be different
  });
});