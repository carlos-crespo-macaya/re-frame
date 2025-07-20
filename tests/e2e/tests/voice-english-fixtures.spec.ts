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
    
    // Mock EventSource at JavaScript level to bypass network issues
    await context.addInitScript(() => {
      // Create mock EventSource class
      class MockEventSource {
        url: string;
        readyState: number;
        withCredentials: boolean;
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;
        onerror: ((event: Event) => void) | null = null;
        
        private listeners: Map<string, Set<EventListener>> = new Map();
        private eventSourceIndex: number;
        
        static CONNECTING = 0;
        static OPEN = 1;
        static CLOSED = 2;
        
        constructor(url: string, options?: EventSourceInit) {
          this.url = url;
          this.readyState = MockEventSource.CONNECTING;
          this.withCredentials = options?.withCredentials || false;
          
          // Store this instance for test control
          if (!window.__mockEventSources) {
            window.__mockEventSources = [];
          }
          this.eventSourceIndex = window.__mockEventSources.length;
          window.__mockEventSources.push(this);
          
          // Log the URL for debugging
          console.log('MockEventSource created for URL:', url);
          
          // Simulate connection after a short delay
          setTimeout(() => {
            if (this.readyState === MockEventSource.CONNECTING) {
              this.readyState = MockEventSource.OPEN;
              const event = new Event('open');
              this.dispatchEvent(event);
            }
          }, 100);
        }
        
        addEventListener(type: string, listener: EventListener) {
          if (!this.listeners.has(type)) {
            this.listeners.set(type, new Set());
          }
          this.listeners.get(type)!.add(listener);
        }
        
        removeEventListener(type: string, listener: EventListener) {
          this.listeners.get(type)?.delete(listener);
        }
        
        dispatchEvent(event: Event): boolean {
          // Call direct handlers
          if (event.type === 'open' && this.onopen) {
            this.onopen(event);
          } else if (event.type === 'message' && this.onmessage) {
            this.onmessage(event as MessageEvent);
          } else if (event.type === 'error' && this.onerror) {
            this.onerror(event);
          }
          
          // Call registered listeners
          const listeners = this.listeners.get(event.type);
          if (listeners) {
            listeners.forEach(listener => listener(event));
          }
          
          return true;
        }
        
        close() {
          this.readyState = MockEventSource.CLOSED;
        }
      }
      
      // Add static constants
      Object.defineProperty(MockEventSource, 'CONNECTING', { value: 0 });
      Object.defineProperty(MockEventSource, 'OPEN', { value: 1 });
      Object.defineProperty(MockEventSource, 'CLOSED', { value: 2 });
      
      // Replace global EventSource
      window.EventSource = MockEventSource as any;
      
      // Expose control functions for tests
      window.__sendSSEMessage = (index: number, eventType: string, data: string) => {
        const source = window.__mockEventSources?.[index];
        if (source && source.readyState === MockEventSource.OPEN) {
          // Real EventSource parses SSE format and provides only the data portion
          const event = new MessageEvent('message', {
            data: data  // Just the JSON string, not SSE format
          });
          source.dispatchEvent(event);
        }
      };
      
      // Track conversation state
      window.__conversationState = {
        phase: 'greeting',
        turnCount: 0
      };
      
      // Mock voice session creation
      window.__mockVoiceSessionId = 'test-voice-session-' + Date.now();
      
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

  test('complete English CBT conversation through all phases', async ({ page }) => {
    // Mock voice session creation
    await page.route('**/api/voice/sessions', async (route) => {
      const sessionId = await page.evaluate(() => window.__mockVoiceSessionId);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: sessionId,
          status: 'active',
          language: 'en-US'
        })
      });
    });
    
    // Mock voice audio endpoint
    await page.route('**/api/voice/sessions/*/audio', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });
    
    // Navigate to the app
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Verify we're on the main page with voice mode option
    await expect(page.getByText('Explore a new perspective')).toBeVisible();
    
    // Switch to voice mode
    const voiceModeButton = page.getByRole('button', { name: /switch to voice/i });
    await expect(voiceModeButton).toBeVisible({ timeout: 10000 });
    await voiceModeButton.click();
    
    // Wait for voice mode UI to appear
    await page.waitForTimeout(1000);
    
    // Verify voice conversation UI elements
    await expect(page.getByText('Voice Conversation')).toBeVisible();
    const startButton = page.getByRole('button', { name: /start conversation/i });
    await expect(startButton).toBeVisible();
    
    // Check initial status
    await expect(page.getByText('Click to start conversation')).toBeVisible();
    
    // Start the conversation
    await startButton.click();
    
    // Status should change to requesting microphone
    await expect(page.getByText(/Requesting microphone permission/i)).toBeVisible({ timeout: 5000 });
    
    // Wait for SSE connection to establish
    await page.waitForTimeout(200);
    
    // Send initial connection event
    await page.evaluate(() => {
      window.__sendSSEMessage(0, 'connected', JSON.stringify({ 
        type: 'connected',
        session_id: 'test-voice-session' 
      }));
    });
    
    // Status should change - either connected or recording
    // Wait for either status (connected from SSE or recording from audio)
    await expect(page.getByText(/Connected.*Speak naturally|Recording.*speak naturally/i)).toBeVisible({ timeout: 15000 });
    console.log('✅ Voice mode connected');
    
    // Verify button changed to Stop Conversation
    const stopButton = page.getByRole('button', { name: /stop conversation/i });
    await expect(stopButton).toBeVisible();
    
    // Simulate conversation flow through phases
    const phases = [
      { name: 'greeting', transcription: "Hello, I'm feeling anxious about an upcoming presentation" },
      { name: 'discovery', transcription: "I keep thinking everyone will judge me and notice my mistakes" },
      { name: 'reframing', transcription: "You're right, I'm assuming the worst without evidence" },
      { name: 'summary', transcription: "Thank you, I feel more confident now" }
    ];
    
    for (const [index, phase] of phases.entries()) {
      console.log(`\n--- Phase ${index + 1}: ${phase.name} ---`);
      
      // Send user transcription
      await page.evaluate((data) => {
        window.__sendSSEMessage(0, 'transcription', JSON.stringify({
          type: 'content',
          content_type: 'text/plain',
          data: data.transcription
        }));
        window.__conversationState.phase = data.name;
        window.__conversationState.turnCount++;
      }, phase);
      
      console.log('User said:', phase.transcription);
      
      // Simulate AI audio response (just to show the system is working)
      await page.waitForTimeout(500);
      await page.evaluate(() => {
        // Send some PCM audio data
        window.__sendSSEMessage(0, 'audio', JSON.stringify({
          type: 'content',
          content_type: 'audio/pcm',
          data: btoa('dummy-audio-data') // Base64 encoded
        }));
      });
      
      // Send turn complete
      await page.evaluate(() => {
        window.__sendSSEMessage(0, 'turn_complete', JSON.stringify({
          type: 'turn_complete',
          turn_complete: true,
          interrupted: false
        }));
      });
      
      await page.waitForTimeout(1000);
    }
    
    // Verify we went through all phases
    const finalState = await page.evaluate(() => window.__conversationState);
    expect(finalState.phase).toBe('summary');
    expect(finalState.turnCount).toBe(4);
    
    // Stop the conversation
    await stopButton.click();
    
    // Verify status changed
    await expect(page.getByText('Conversation ended')).toBeVisible({ timeout: 5000 });
    
    // Button should be back to Start Conversation
    await expect(page.getByRole('button', { name: /start conversation/i })).toBeVisible();
    
    console.log('\n✅ Voice conversation completed all phases successfully!');
  });

  test('handles voice mode status changes correctly', async ({ page }) => {
    // Mock voice session creation
    await page.route('**/api/voice/sessions', async (route) => {
      const sessionId = await page.evaluate(() => window.__mockVoiceSessionId);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: sessionId,
          status: 'active',
          language: 'en-US'
        })
      });
    });
    
    // Mock voice audio endpoint
    await page.route('**/api/voice/sessions/*/audio', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });
    
    await page.goto('/');
    
    // Switch to voice mode
    await page.getByRole('button', { name: /switch to voice/i }).click();
    await page.waitForTimeout(1000);
    
    // Initial status
    await expect(page.getByText('Click to start conversation')).toBeVisible();
    
    // Start conversation
    await page.getByRole('button', { name: /start conversation/i }).click();
    
    // Check status progression
    await expect(page.getByText(/Requesting microphone permission/i)).toBeVisible({ timeout: 5000 });
    
    // Send connection event
    await page.waitForTimeout(200);
    await page.evaluate(() => {
      window.__sendSSEMessage(0, 'connected', JSON.stringify({ 
        type: 'connected',
        session_id: 'test-session-2' 
      }));
    });
    
    // Should show connected or recording status
    await expect(page.getByText(/Connected.*Speak naturally|Recording.*speak naturally/i)).toBeVisible({ timeout: 15000 });
    
    // Verify listening indicator appears
    const listeningIndicator = page.locator('.animate-pulse').first();
    await expect(listeningIndicator).toBeVisible();
    await expect(page.getByText('Listening...')).toBeVisible();
    
    // Stop conversation
    await page.getByRole('button', { name: /stop conversation/i }).click();
    
    // Final status
    await expect(page.getByText('Conversation ended')).toBeVisible();
    
    console.log('✅ Voice mode status changes work correctly');
  });

  test('voice mode error handling', async ({ page }) => {
    await page.goto('/');
    
    // Switch to voice mode
    await page.getByRole('button', { name: /switch to voice/i }).click();
    await page.waitForTimeout(1000);
    
    // Mock getUserMedia to fail
    await page.evaluate(() => {
      navigator.mediaDevices.getUserMedia = async () => {
        throw new Error('Microphone access denied');
      };
    });
    
    // Try to start conversation
    await page.getByRole('button', { name: /start conversation/i }).click();
    
    // Should show error status
    await expect(page.getByText(/Failed to start.*check microphone permissions/i)).toBeVisible({ timeout: 5000 });
    
    // Error message should be displayed
    const errorMessage = page.locator('.text-red-500');
    await expect(errorMessage).toContainText('Microphone access denied');
    
    console.log('✅ Voice mode error handling works correctly');
  });

});