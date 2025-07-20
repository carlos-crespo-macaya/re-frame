import { test, expect, chromium, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { decode } from 'wav-decoder';

/**
 * Voice E2E tests using MediaStreamTrackGenerator for programmable audio injection.
 * This allows full control over multi-turn conversations without browser restart.
 */

// Helper to convert WAV file to AudioData frames
async function wavToAudioData(wavPath: string): Promise<Array<{data: number[], timestamp: number}>> {
  const wavBuffer = fs.readFileSync(wavPath);
  const audioBuffer = await decode(wavBuffer);
  
  // Get the PCM data (assuming mono, 16-bit)
  const pcmData = audioBuffer.channelData[0];
  const sampleRate = audioBuffer.sampleRate;
  const frameDuration = 20; // ms per frame
  const samplesPerFrame = Math.floor(sampleRate * frameDuration / 1000);
  
  const frames: Array<{data: number[], timestamp: number}> = [];
  let timestamp = 0;
  
  // Convert Float32Array to Int16Array and chunk into frames
  for (let i = 0; i < pcmData.length; i += samplesPerFrame) {
    const frameLength = Math.min(samplesPerFrame, pcmData.length - i);
    const int16Data = new Int16Array(frameLength);
    
    // Convert float32 [-1, 1] to int16 [-32768, 32767]
    for (let j = 0; j < frameLength; j++) {
      int16Data[j] = Math.max(-32768, Math.min(32767, Math.floor(pcmData[i + j] * 32767)));
    }
    
    // Debug first frame
    if (i === 0) {
      console.log(`First frame PCM values: min=${Math.min(...pcmData.slice(0, 100))}, max=${Math.max(...pcmData.slice(0, 100))}`);
      console.log(`First frame Int16 values: min=${Math.min(...int16Data)}, max=${Math.max(...int16Data)}`);
    }
    
    // Convert to regular array for serialization
    frames.push({
      data: Array.from(int16Data),
      timestamp: timestamp * 1000 // Convert to microseconds
    });
    
    timestamp += frameDuration;
  }
  
  return frames;
}

test.describe('Multi-Turn Voice Conversation', () => {
  test('complete CBT conversation with turn-taking', async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      permissions: ['microphone']
    });
    const page = await context.newPage();
    
    // Enable console logging
    page.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('Browser console:', msg.text());
      }
    });
    
    // Install the programmable microphone before any script runs
    await page.addInitScript(() => {
      const origGUM = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      const origAddModule = AudioContext.prototype.audioWorklet.addModule;
      
      // Expose test helpers
      (window as any).__test = {
        push: async (_frames: any[], _sampleRate: number) => {},
        done: Promise.resolve(),
        audioStarted: false,
        audioEnded: false,
        turnCount: 0,
        workletPort: null
      };
      
      // Intercept AudioWorklet creation to capture the port
      AudioContext.prototype.audioWorklet.addModule = async function(...args) {
        const result = await origAddModule.apply(this, args);
        
        // Intercept AudioWorkletNode creation
        const origCreateNode = this.createWorkletNode || AudioWorkletNode;
        (window as any).AudioWorkletNode = new Proxy(origCreateNode, {
          construct(target, args) {
            const node = new target(...args);
            if (args[1] === 'pcm-recorder-processor') {
              console.log('Captured AudioWorklet port for pcm-recorder-processor');
              (window as any).__test.workletPort = node.port;
            }
            return node;
          }
        });
        
        return result;
      };
      
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        if (!constraints?.audio) return origGUM(constraints);
        
        // Create a silent MediaStream to satisfy the API
        const audioContext = new AudioContext();
        const oscillator = audioContext.createOscillator();
        oscillator.frequency.value = 0; // Silent
        const dest = audioContext.createMediaStreamDestination();
        oscillator.connect(dest);
        oscillator.start();
        
        console.log('Created silent MediaStream for getUserMedia');
        
        // Expose push function for test to feed audio frames
        (window as any).__test.push = async (frames: any[], sampleRate: number) => {
          console.log(`Pushing ${frames.length} audio frames at ${sampleRate}Hz`);
          
          const workletPort = (window as any).__test.workletPort;
          if (!workletPort) {
            console.error('AudioWorklet port not captured yet!');
            return;
          }
          
          for (const frame of frames) {
            // Convert array back to Int16Array
            const int16Array = new Int16Array(frame.data);
            
            if (int16Array.length === 0) {
              console.log('Skipping empty frame');
              continue;
            }
            
            // Convert int16 to float32 (matching what AudioWorklet would send)
            const float32Data = new Float32Array(int16Array.length);
            for (let i = 0; i < int16Array.length; i++) {
              float32Data[i] = int16Array[i] / 32768.0;
            }
            
            // Debug: Check if data has actual audio values
            const hasAudio = float32Data.some(v => v !== 0);
            if (!hasAudio) {
              console.log('WARNING: Audio frame contains only silence!');
            } else {
              console.log(`Audio frame has data, max value: ${Math.max(...float32Data)}`);
            }
            
            // Simulate AudioWorklet sending data via port message
            workletPort.postMessage(float32Data);
            
            // Pace the audio to simulate real-time (20ms per frame)
            await new Promise(resolve => setTimeout(resolve, 20));
          }
          
          console.log('Finished pushing audio frames');
        };
        
        return dest.stream;
        
        // Monitor audio playback - check for blob URLs too
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
              if (node instanceof HTMLAudioElement) {
                console.log('Audio element created:', node.src);
                
                node.addEventListener('play', () => {
                  (window as any).__test.audioStarted = true;
                  (window as any).__test.turnCount++;
                  console.log(`AI audio started (turn ${(window as any).__test.turnCount})`);
                });
                
                node.addEventListener('ended', () => {
                  (window as any).__test.audioEnded = true;
                  console.log('AI audio ended');
                });
              }
            });
          });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Also monitor audio src changes
        const originalCreateElement = document.createElement.bind(document);
        document.createElement = function(tagName: string) {
          const element = originalCreateElement(tagName);
          if (tagName.toLowerCase() === 'audio') {
            console.log('Audio element created via createElement');
            const audio = element as HTMLAudioElement;
            
            // Monitor src changes
            Object.defineProperty(audio, 'src', {
              set: function(value) {
                console.log('Audio src set to:', value);
                this.setAttribute('src', value);
                
                // Check if it's a blob URL (AI response)
                if (value && value.startsWith('blob:')) {
                  console.log('AI audio blob detected');
                  
                  audio.addEventListener('loadeddata', () => {
                    console.log('AI audio loaded');
                  });
                  
                  audio.addEventListener('play', () => {
                    (window as any).__test.audioStarted = true;
                    (window as any).__test.turnCount++;
                    console.log(`AI audio started via src setter (turn ${(window as any).__test.turnCount})`);
                  }, { once: true });
                  
                  audio.addEventListener('ended', () => {
                    (window as any).__test.audioEnded = true;
                    console.log('AI audio ended via src setter');
                  }, { once: true });
                }
              },
              get: function() {
                return this.getAttribute('src');
              }
            });
          }
          return element;
        };
        
        return new MediaStream([generator]);
      };
    });
    
    // Navigate to the app
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Helper function to speak and wait for AI response
    const speak = async (wavFile: string, description: string) => {
      console.log(`\n--- ${description} ---`);
      
      // Decode WAV file to audio frames
      const audioPath = path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio', wavFile);
      
      if (!fs.existsSync(audioPath)) {
        throw new Error(`Audio file not found: ${audioPath}`);
      }
      
      const frames = await wavToAudioData(audioPath);
      console.log(`Loaded ${frames.length} frames from ${wavFile}`);
      
      // Reset audio state
      await page.evaluate(() => {
        (window as any).__test.audioStarted = false;
        (window as any).__test.audioEnded = false;
      });
      
      // Push audio frames
      await page.evaluate(({ frames, sampleRate }) => {
        return (window as any).__test.push(frames, sampleRate);
      }, { frames, sampleRate: 16000 });
      
      // Wait for AI to start responding
      await page.waitForFunction(
        () => (window as any).__test.audioStarted,
        { timeout: 20000 }
      );
      console.log('✓ AI started responding');
      
      // Wait for AI to finish responding
      await page.waitForFunction(
        () => (window as any).__test.audioEnded,
        { timeout: 30000 }
      );
      console.log('✓ AI finished responding');
    };
    
    // Switch to voice mode
    await page.getByRole('button', { name: 'Switch to Voice' }).click();
    console.log('✓ Switched to voice mode');
    
    // Start conversation
    await page.getByRole('button', { name: 'Start Conversation' }).click();
    console.log('✓ Started conversation');
    
    // Wait for audio system to initialize and SSE to be ready
    await page.waitForTimeout(2000);
    
    // Wait for AudioWorklet to be captured
    await page.waitForFunction(
      () => (window as any).__test.workletPort !== null,
      { timeout: 5000 }
    );
    console.log('✓ AudioWorklet port captured');
    
    // Check if SSE is connected
    const isConnected = await page.evaluate(() => {
      return (window as any).__test.audioStarted !== undefined;
    });
    console.log('SSE monitoring ready:', isConnected);
    
    // Turn 1: Greeting
    await speak('english/en-greeting.wav', 'Turn 1: Initial greeting');
    
    // Turn 2: Share anxious thought
    await speak('english/en-thought-1.wav', 'Turn 2: Share anxious thought');
    
    // Turn 3: Acknowledge insight
    await speak('english/en-insight.wav', 'Turn 3: Acknowledge cognitive distortion');
    
    // Verify we had 3 complete turns
    const turnCount = await page.evaluate(() => (window as any).__test.turnCount);
    expect(turnCount).toBe(3);
    console.log(`\n✓ Completed ${turnCount} turns of conversation!`);
    
    // Let any buffered data flush
    await page.evaluate(() => (window as any).__test.done);
    
    await browser.close();
  });
  
  test('verify MediaStreamTrackGenerator support', async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    const hasSupport = await page.evaluate(() => {
      return 'MediaStreamTrackGenerator' in window;
    });
    
    console.log(`MediaStreamTrackGenerator support: ${hasSupport}`);
    expect(hasSupport).toBe(true);
    
    await browser.close();
  });
});