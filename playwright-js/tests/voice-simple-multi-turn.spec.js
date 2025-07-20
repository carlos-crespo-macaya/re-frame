import { test, expect, chromium, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Simple multi-turn voice test using browser restart between turns
 * This verifies that the basic audio injection works and backend responds
 */

async function launchBrowserWithAudio(audioFilePath: string, headless: boolean = true) {
  const absolutePath = path.resolve(audioFilePath);
  
  const browser = await chromium.launch({
    headless,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--use-fake-device-for-media-stream',
      '--use-fake-ui-for-media-stream',
      `--use-file-for-fake-audio-capture=${absolutePath}%noloop`
    ]
  });
  
  return browser;
}

async function setupVoiceConversation(page: Page): Promise<{ sessionId: string }> {
  // Monitor HTTP requests
  const audioRequests: any[] = [];
  page.on('request', request => {
    if (request.url().includes('/api/voice/sessions/') && request.url().includes('/audio')) {
      audioRequests.push({
        url: request.url(),
        method: request.method(),
        postData: request.postData()
      });
      console.log(`Audio request: ${request.method()} ${request.url()}`);
    }
  });

  // Monitor SSE events
  const sseEvents: any[] = [];
  await page.addInitScript(() => {
    (window as any).__test = {
      sseEvents: [],
      audioStarted: false,
      turnCount: 0,
      lastAudioTime: 0,
      aiFinishedSpeaking: false
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
            console.log('SSE event:', data.type);
            
            if (data.type === 'audio' && data.data) {
              if (!(window as any).__test.audioStarted) {
                (window as any).__test.audioStarted = true;
                (window as any).__test.turnCount++;
                console.log(`AI started speaking (turn ${(window as any).__test.turnCount})`);
              }
              (window as any).__test.lastAudioTime = Date.now();
              console.log('AI audio chunk received');
            }
            
            if (data.type === 'turn_complete') {
              (window as any).__test.aiFinishedSpeaking = true;
              console.log('AI finished speaking');
            }
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        });
      }
    };
  });

  // Navigate and start conversation
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
  
  // Extract session ID from page
  const sessionId = await page.evaluate(() => {
    const testData = (window as any).__test;
    if (!testData || !testData.sseEvents) {
      console.log('No test data found');
      return null;
    }
    const events = testData.sseEvents;
    console.log(`Found ${events.length} SSE events`);
    for (const event of events) {
      if (event.type === 'connected' && event.session_id) {
        return event.session_id;
      }
    }
    return null;
  });
  
  return { sessionId: sessionId || 'unknown' };
}

test.describe('Simple Multi-Turn Voice Test', () => {
  test('sequential conversation with browser restart', async () => {
    console.log('\n=== Turn 1: Greeting ===');
    
    // Launch browser with greeting audio
    const browser1 = await launchBrowserWithAudio(
      path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', 'english', 'en-greeting.wav'),
      process.env.HEADLESS !== 'false'
    );
    
    const context1 = await browser1.newContext({ permissions: ['microphone'] });
    const page1 = await context1.newPage();
    
    // Enable console logging
    page1.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('Browser console:', msg.text());
      }
    });
    
    const { sessionId } = await setupVoiceConversation(page1);
    console.log('Session ID:', sessionId);
    
    // Wait for AI to start responding
    await page1.waitForFunction(
      () => (window as any).__test.audioStarted,
      { timeout: 20000 }
    );
    console.log('✓ AI started responding to greeting');
    
    // Wait for AI to finish speaking (no audio for 2 seconds or turn_complete)
    await page1.waitForFunction(
      () => {
        const test = (window as any).__test;
        if (test.aiFinishedSpeaking) return true;
        if (!test.lastAudioTime) return false;
        return Date.now() - test.lastAudioTime > 2000;
      },
      { timeout: 30000 }
    );
    console.log('✓ AI finished speaking');
    
    // Check audio chunk count
    const audioChunks1 = await page1.evaluate(() => {
      return (window as any).__test.sseEvents.filter((e: any) => e.type === 'audio').length;
    });
    console.log(`Received ${audioChunks1} audio chunks`);
    
    // Give a moment for audio to finish playing
    await page1.waitForTimeout(1000);
    
    await browser1.close();
    
    console.log('\n=== Turn 2: Share anxious thought ===');
    
    // Launch browser with anxious thought audio
    const browser2 = await launchBrowserWithAudio(
      path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', 'english', 'en-thought-1.wav'),
      process.env.HEADLESS !== 'false'
    );
    
    const context2 = await browser2.newContext({ permissions: ['microphone'] });
    const page2 = await context2.newPage();
    
    page2.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('Browser console:', msg.text());
      }
    });
    
    await setupVoiceConversation(page2);
    
    // Wait for AI to start responding
    await page2.waitForFunction(
      () => (window as any).__test.audioStarted,
      { timeout: 20000 }
    );
    console.log('✓ AI started responding to anxious thought');
    
    // Wait for AI to finish speaking
    await page2.waitForFunction(
      () => {
        const test = (window as any).__test;
        if (test.aiFinishedSpeaking) return true;
        if (!test.lastAudioTime) return false;
        return Date.now() - test.lastAudioTime > 2000;
      },
      { timeout: 30000 }
    );
    console.log('✓ AI finished speaking');
    
    // Check audio chunk count
    const audioChunks2 = await page2.evaluate(() => {
      return (window as any).__test.sseEvents.filter((e: any) => e.type === 'audio').length;
    });
    console.log(`Received ${audioChunks2} audio chunks`);
    
    // Give a moment for audio to finish playing
    await page2.waitForTimeout(1000);
    
    await browser2.close();
    
    console.log('\n✓ Multi-turn conversation completed successfully!');
  });
});