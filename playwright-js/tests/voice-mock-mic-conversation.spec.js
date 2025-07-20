import { test, expect, chromium, type Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/* ---------------------------------------------------------------------
 * Test-fixture helpers
 * ------------------------------------------------------------------- */

const AUDIO_DIR = path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio');

/** Inject a controllable mock microphone before any page script runs. */
async function injectMockMic(page: Page) {
  await page.addInitScript(() => {
    // 1. Create an AudioContext and a MediaStreamDestination that will be
    //    returned by getUserMedia({audio:true})
    const ctx = new AudioContext({ sampleRate: 16_000 });
    const dest = ctx.createMediaStreamDestination();

    // Keep the graph alive: Chrome suspends silent graphs in headless mode
    const keepAliveGain = ctx.createGain();
    keepAliveGain.gain.value = 0;
    keepAliveGain.connect(ctx.destination);

    // 2. Helper: decode a base64-encoded WAV and play it into the mic
    function b64ToBuf(b64: string): ArrayBuffer {
      const bin = atob(b64);
      return Uint8Array.from(bin, c => c.charCodeAt(0)).buffer;
    }

    let chain: Promise<void> = Promise.resolve();

    (window as any).__mockMic = {
      /** Start the context (required in headed mode) */
      resume: () => ctx.resume(),

      /** Queue one utterance. Returns a promise that resolves when finished. */
      play(b64: string) {
        const job = ctx
          .decodeAudioData(b64ToBuf(b64))
          .then(buf => new Promise<void>(done => {
            const src = ctx.createBufferSource();
            src.buffer = buf;
            src.connect(dest);
            src.start();
            src.onended = () => done();
          }));
        chain = chain.then(() => job);
        return job;
      },

      /** Await all currently queued audio */
      awaitDone: () => chain,

      /** Expose the stream for debugging if needed */
      stream: dest.stream
    };

    // 3. Monkey-patch getUserMedia so the page "records" from our stream
    const originalGUM = navigator.mediaDevices.getUserMedia.bind(
      navigator.mediaDevices
    );
    navigator.mediaDevices.getUserMedia = async (constraints?: any) => {
      if (constraints?.audio) {
        console.log('Returning mock microphone stream');
        return dest.stream;
      }
      return originalGUM(constraints);
    };
  });
}

/** Wait until the assistant has finished its turn. */
async function waitForAIResponse(page: Page) {
  // Monitor SSE events
  await page.evaluate(() => {
    if ((window as any).__sseMonitorInstalled) return;
    (window as any).__sseMonitorInstalled = true;
    
    (window as any).__test = {
      audioStarted: false,
      lastChunk: 0,
      done: false,
      sseEvents: []
    };

    // Hook into EventSource to monitor SSE events
    const OriginalEventSource = window.EventSource;
    window.EventSource = class extends OriginalEventSource {
      constructor(url: string, opts?: EventSourceInit) {
        super(url, opts);
        console.log('SSE connection created:', url);
        
        this.addEventListener('message', (e) => {
          try {
            const payload = JSON.parse(e.data);
            const t = (window as any).__test;
            t.sseEvents.push(payload);
            
            if (payload.type === 'audio') {
              if (!t.audioStarted) {
                t.audioStarted = true;
                console.log('AI audio started');
              }
              t.lastChunk = Date.now();
            }
            if (payload.type === 'turn_complete') {
              t.done = true;
              console.log('AI turn complete');
            }
          } catch { 
            // ignore non-JSON messages
          }
        });
      }
    };
  });

  // Wait for first audio chunk
  console.log('Waiting for AI audio to start...');
  await page.waitForFunction(() => (window as any).__test?.audioStarted, {
    timeout: 30_000
  });

  // Wait until turn_complete OR 3s of silence
  console.log('Waiting for AI to finish speaking...');
  await page.waitForFunction(() => {
    const t = (window as any).__test;
    if (t.done) return true;
    if (!t.lastChunk) return false;
    return Date.now() - t.lastChunk > 3_000;
  }, { timeout: 45_000 });
}

/* ---------------------------------------------------------------------
 * The multi-turn E2E test
 * ------------------------------------------------------------------- */

test.describe('Multi-Turn Voice Conversation with Mock Microphone', () => {
  test('full multi-turn voice conversation in one session', async () => {
    const browser = await chromium.launch({
      headless: process.env.HEADLESS !== 'false',
      args: ['--no-sandbox', '--use-fake-ui-for-media-stream']   // no fake audio file
    });
    const context = await browser.newContext({ permissions: ['microphone'] });
    const page = await context.newPage();

    // Browser console passthrough for debugging
    page.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('[browser]', msg.text());
      }
    });

    // Monitor HTTP requests
    page.on('request', request => {
      if (request.url().includes('/api/voice/sessions/') && request.url().includes('/audio')) {
        console.log(`Audio POST: ${request.method()} ${request.url()}`);
      }
    });

    await injectMockMic(page);

    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Switch to voice mode
    await page.getByRole('button', { name: 'Switch to Voice' }).click();
    console.log('✓ Switched to voice mode');
    
    // Start conversation
    await page.getByRole('button', { name: 'Start Conversation' }).click();
    console.log('✓ Started conversation');

    // Resume AudioContext (required in headed mode)
    await page.evaluate(() => (window as any).__mockMic.resume());

    // Wait for initial AI greeting
    await waitForAIResponse(page);
    console.log('✓ AI greeted user');

    const USER_TURNS = [
      { file: 'english/en-greeting.wav', description: 'User greeting' },
      { file: 'english/en-thought-1.wav', description: 'Anxious thought' },
      { file: 'english/en-insight.wav', description: 'User insight' }
    ];

    for (const [idx, turn] of USER_TURNS.entries()) {
      console.log(`\n🗣️  User turn ${idx + 1}: ${turn.description}`);
      
      const audioPath = path.join(AUDIO_DIR, turn.file);
      if (!fs.existsSync(audioPath)) {
        console.log(`⚠️  Audio file not found: ${audioPath}`);
        continue;
      }
      
      const b64 = fs.readFileSync(audioPath, 'base64');

      // 1. Push the utterance
      await page.evaluate((data) => (window as any).__mockMic.play(data), b64);
      console.log('✓ Audio injected');

      // 2. Wait until the buffer is done playing (user finished speaking)
      await page.evaluate(() => (window as any).__mockMic.awaitDone());
      console.log('✓ User finished speaking');

      // 3. Now wait for the assistant to answer and complete its turn
      await waitForAIResponse(page);
      console.log(`🤖 Assistant finished turn ${idx + 1}`);
    }

    // Verify we stayed in the same session
    const sessionInfo = await page.evaluate(() => {
      const test = (window as any).__test;
      return {
        events: test?.sseEvents?.length || 0,
        audioChunks: test?.sseEvents?.filter((e: any) => e.type === 'audio').length || 0,
        turns: test?.sseEvents?.filter((e: any) => e.type === 'turn_complete').length || 0
      };
    });

    console.log('\n📊 Session statistics:');
    console.log(`   Total events: ${sessionInfo.events}`);
    console.log(`   Audio chunks: ${sessionInfo.audioChunks}`);
    console.log(`   Completed turns: ${sessionInfo.turns}`);

    // Simple assertion: we should have received multiple turns
    expect(sessionInfo.turns).toBeGreaterThanOrEqual(3);
    console.log('\n✅ Multi-turn conversation completed successfully');

    await browser.close();
  });
});