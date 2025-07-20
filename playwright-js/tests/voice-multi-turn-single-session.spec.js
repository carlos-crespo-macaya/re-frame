import { test, expect, chromium, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Multi-turn voice conversation test using AudioContext injection
 * This maintains a single browser session and allows programmatic audio injection
 */

// Helper to inject audio mock into the page
async function injectAudioMock(page: Page) {
  await page.addInitScript(() => {
    // 1. Build microphone stub ----------------------------------------
    const ctx = new AudioContext({ sampleRate: 16_000 });
    const dest = ctx.createMediaStreamDestination();
    // this stream will look like a live microphone
    const micStream = dest.stream;
    
    // Monitor the MediaStreamTrack
    const track = micStream.getAudioTracks()[0];
    console.log('Mock microphone track:', track.label, 'enabled:', track.enabled, 'readyState:', track.readyState);

    // 2. Library utilities --------------------------------------------
    async function wavToAudioBuffer(b64: string): Promise<AudioBuffer> {
      const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
      return ctx.decodeAudioData(bytes.buffer);
    }

    // 3. Queue & state -------------------------------------------------
    const queue: Promise<void>[] = [];
    let playing = Promise.resolve();

    // 4. Public APIs exposed to Node ----------------------------------
    // enqueue a user utterance (one WAV) and return when appended
    (window as any).enqueueWav = (b64: string) => {
      const job = wavToAudioBuffer(b64).then(buf => {
        console.log(`Decoded audio buffer: ${buf.duration}s, ${buf.sampleRate}Hz, ${buf.numberOfChannels} channels`);
        return new Promise<void>(done => {
          const src = ctx.createBufferSource();
          src.buffer = buf;
          src.connect(dest);   // pipe into the "microphone"
          console.log('Starting audio playback into microphone stream');
          src.start();
          src.onended = () => {
            console.log('Audio playback ended');
            done();
          };
        });
      }).catch(error => {
        console.error('Failed to decode audio:', error);
        throw error;
      });
      // serialise playbacks
      playing = playing.then(() => job);
      queue.push(job);
      return job;
    };

    // wait until everything currently queued has finished
    (window as any).awaitPlayback = () => playing;
    
    // 5. Override getUserMedia ----------------------------------------
    const orig = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
    navigator.mediaDevices.getUserMedia = async (constraints?: any) => {
      if (constraints?.audio) {
        console.log('Returning mock microphone stream');
        return micStream;
      }
      return orig(constraints);
    };
  });
}

test.describe('Multi-Turn Voice Conversation - Single Session', () => {
  test('complete CBT conversation with three turns', async () => {
    const browser = await chromium.launch({
      headless: process.env.HEADLESS !== 'false',
      args: ['--no-sandbox', '--use-fake-ui-for-media-stream']
    });
    const context = await browser.newContext({ permissions: ['microphone'] });
    const page = await context.newPage();

    // Enable console logging
    page.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('Browser console:', msg.text());
      }
    });
    
    // Monitor HTTP requests and responses
    page.on('request', request => {
      if (request.url().includes('/api/voice/sessions/') && request.url().includes('/audio')) {
        console.log(`Audio request: ${request.method()} ${request.url()}`);
        // Log request body size to verify audio data is being sent
        const contentLength = request.headers()['content-length'];
        console.log(`Request body size: ${contentLength} bytes`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/voice/sessions/') && response.url().includes('/audio')) {
        console.log(`Audio response: ${response.status()} ${response.statusText()}`);
      }
    });

    // 1. Inject microphone stub before any page code runs
    await injectAudioMock(page);

    // Monitor SSE events and AudioWorklet
    await page.addInitScript(() => {
      (window as any).__test = {
        sseEvents: [],
        audioStarted: false,
        turnCount: 0,
        lastAudioTime: 0,
        aiFinishedSpeaking: false,
        userTurns: 0,
        aiTurns: 0,
        audioWorkletMessages: [],
        audioDataSent: 0
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
                console.log('=== AI finished speaking (turn_complete) ===');
              }
              
              if (data.type === 'connected') {
                console.log('=== Session connected ===');
              }
              
              if (data.type === 'transcript' && data.text) {
                console.log(`User transcript: "${data.text}"`);
              }
            } catch (e) {
              console.error('Failed to parse SSE event:', e);
            }
          });
        }
      };
      
      // Monitor AudioWorklet messages
      const originalAddModule = AudioWorkletNode.prototype.constructor;
      AudioWorkletNode.prototype.constructor = function(...args) {
        const node = originalAddModule.apply(this, args);
        console.log('AudioWorkletNode created');
        
        // Intercept port messages
        const originalPostMessage = node.port.postMessage;
        node.port.postMessage = function(message) {
          console.log('AudioWorklet message:', message);
          (window as any).__test.audioWorkletMessages.push(message);
          return originalPostMessage.apply(this, arguments);
        };
        
        return node;
      };
      
      // Monitor fetch calls for audio data
      const originalFetch = window.fetch;
      window.fetch = async function(...args) {
        const [url, options] = args;
        if (typeof url === 'string' && url.includes('/audio')) {
          console.log('Fetch to audio endpoint:', url);
          if (options?.body) {
            const bodySize = options.body instanceof Blob ? options.body.size : 
                            options.body instanceof ArrayBuffer ? options.body.byteLength : 
                            JSON.stringify(options.body).length;
            console.log('Audio data size:', bodySize, 'bytes');
            (window as any).__test.audioDataSent += bodySize;
          }
        }
        return originalFetch.apply(this, args);
      };
    });

    // 2. Normal UI flow --------------------------------------------------
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Switch to voice mode
    await page.getByRole('button', { name: 'Switch to Voice' }).click();
    console.log('✓ Switched to voice mode');
    
    // Start conversation
    await page.getByRole('button', { name: 'Start Conversation' }).click();
    console.log('✓ Started conversation');
    
    // Wait for SSE connection to establish and initial setup to complete
    await page.waitForTimeout(2000);
    
    // Wait for any initial AI greeting or setup to complete
    await page.waitForFunction(
      () => {
        const test = (window as any).__test;
        // Check if we've received the initial turn_complete event
        return test.sseEvents.some((e: any) => e.type === 'turn_complete');
      },
      { timeout: 5000 }
    );
    console.log('✓ Conversation ready for user input');

    // Helper function to wait for AI response
    async function waitForAIResponse(turnDescription: string) {
      console.log(`\n${turnDescription}`);
      
      // Reset flags
      await page.evaluate(() => {
        (window as any).__test.audioStarted = false;
        (window as any).__test.aiFinishedSpeaking = false;
      });
      
      // Wait for AI to start responding
      await page.waitForFunction(
        () => (window as any).__test.audioStarted,
        { timeout: 30000 }
      );
      
      console.log('✓ AI started responding');
      
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
    }

    // 3. Three user turns ------------------------------------------------
    const prompts = [
      'english/en-greeting.wav',      // "Hello"
      'english/en-thought-1.wav',      // Anxious thought about party
      'english/en-insight.wav'         // Acknowledgment of cognitive distortion
    ];

    for (const [i, file] of prompts.entries()) {
      console.log(`\n=== User Turn ${i + 1}: ${file} ===`);
      
      // Read WAV file and convert to base64
      const wavPath = path.resolve(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', file);
      const wavBuffer = fs.readFileSync(wavPath);
      const wavB64 = wavBuffer.toString('base64');
      console.log(`WAV file size: ${wavBuffer.length} bytes`);
      
      // Inject audio into the page
      await page.evaluate((d) => (window as any).enqueueWav(d), wavB64);
      console.log('✓ Audio enqueued');
      
      // Increment user turn counter
      await page.evaluate(() => {
        (window as any).__test.userTurns++;
      });

      // Wait until buffer finished playing
      await page.evaluate(() => (window as any).awaitPlayback());
      console.log('✓ Audio playback complete');
      
      // Wait for the silence detection to trigger turn_complete
      console.log('Waiting for silence detection...');
      await page.waitForTimeout(2000);
      
      // Check if we need to manually send turn_complete
      const needsTurnComplete = await page.evaluate(() => {
        const events = (window as any).__test.sseEvents;
        const recentEvents = events.slice(-10);
        console.log('Recent SSE events:', recentEvents.map((e: any) => e.type).join(', '));
        return true; // Always wait for natural turn completion
      });

      // Wait for AI turn to complete
      await waitForAIResponse(`Waiting for AI response to turn ${i + 1}...`);
    }

    // Verify we had a complete multi-turn conversation
    const stats = await page.evaluate(() => {
      const test = (window as any).__test;
      return {
        userTurns: test.userTurns,
        aiTurns: test.aiTurns,
        totalAudioChunks: test.sseEvents.filter((e: any) => e.type === 'audio').length,
        transcripts: test.sseEvents.filter((e: any) => e.type === 'transcript').map((e: any) => e.text),
        audioWorkletMessages: test.audioWorkletMessages,
        audioDataSent: test.audioDataSent
      };
    });
    
    console.log('\n=== Conversation Summary ===');
    console.log(`User turns: ${stats.userTurns}`);
    console.log(`AI turns: ${stats.aiTurns}`);
    console.log(`Total audio chunks received: ${stats.totalAudioChunks}`);
    console.log(`Transcripts: ${stats.transcripts.join(', ')}`);
    console.log(`AudioWorklet messages: ${stats.audioWorkletMessages.length}`);
    console.log(`Audio data sent: ${stats.audioDataSent} bytes`);
    
    // Assertions
    expect(stats.userTurns).toBe(3);
    expect(stats.aiTurns).toBe(3);
    expect(stats.totalAudioChunks).toBeGreaterThan(0);
    
    console.log('\n✓ Multi-turn conversation completed successfully in single session!');
    
    // Keep browser open a bit longer if not headless
    if (process.env.HEADLESS !== 'false') {
      await page.waitForTimeout(5000);
    }

    await browser.close();
  });

  test('verify session continuity', async () => {
    const browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--use-fake-ui-for-media-stream']
    });
    const context = await browser.newContext({ permissions: ['microphone'] });
    const page = await context.newPage();

    await injectAudioMock(page);

    // Capture session ID
    let sessionId: string | null = null;
    await page.addInitScript(() => {
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

    sessionId = await page.evaluate(() => (window as any).__sessionId);
    console.log(`Session ID: ${sessionId}`);

    // Perform multiple turns and verify same session
    const prompts = ['english/en-greeting.wav', 'english/en-thought-1.wav'];
    
    for (const file of prompts) {
      const wavPath = path.resolve(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', file);
      const wavB64 = fs.readFileSync(wavPath, 'base64');
      await page.evaluate((d) => (window as any).enqueueWav(d), wavB64);
      await page.evaluate(() => (window as any).awaitPlayback());
      await page.waitForTimeout(3000); // Wait for response
    }

    // Verify session ID hasn't changed
    const finalSessionId = await page.evaluate(() => (window as any).__sessionId);
    expect(finalSessionId).toBe(sessionId);
    console.log('✓ Session ID remained consistent across turns');

    await browser.close();
  });
});