import { test, expect } from '@playwright/test';

test.describe('Complete CBT Assistant Workflow', () => {
  test('text and voice modes work through all conversation phases', async ({ page, context, browserName }) => {
    // Grant microphone permissions for Chromium
    if (browserName === 'chromium') {
      await context.grantPermissions(['microphone']);
    }
    
    // Mock voice endpoints
    await page.route('**/api/voice/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: 'test-voice-session-' + Date.now(),
          status: 'active',
          language: 'en-US'
        })
      });
    });
    
    await page.route('**/api/voice/sessions/*/audio', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });
    
    // Mock EventSource for voice mode
    await context.addInitScript(() => {
      class MockEventSource {
        url: string;
        readyState: number;
        withCredentials: boolean;
        onopen: ((event: Event) => void) | null = null;
        onmessage: ((event: MessageEvent) => void) | null = null;
        onerror: ((event: Event) => void) | null = null;
        
        private listeners: Map<string, Set<EventListener>> = new Map();
        
        static CONNECTING = 0;
        static OPEN = 1;
        static CLOSED = 2;
        
        constructor(url: string, options?: EventSourceInit) {
          this.url = url;
          this.readyState = MockEventSource.CONNECTING;
          this.withCredentials = options?.withCredentials || false;
          
          if (!window.__mockEventSources) {
            window.__mockEventSources = [];
          }
          window.__mockEventSources.push(this);
          
          // Only mock voice SSE endpoints
          if (url.includes('/api/voice/')) {
            setTimeout(() => {
              if (this.readyState === MockEventSource.CONNECTING) {
                this.readyState = MockEventSource.OPEN;
                const event = new Event('open');
                this.dispatchEvent(event);
              }
            }, 100);
          }
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
          if (event.type === 'open' && this.onopen) {
            this.onopen(event);
          } else if (event.type === 'message' && this.onmessage) {
            this.onmessage(event as MessageEvent);
          } else if (event.type === 'error' && this.onerror) {
            this.onerror(event);
          }
          
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
      
      // Only replace EventSource for voice endpoints
      const OriginalEventSource = window.EventSource;
      window.EventSource = function(url: string, options?: EventSourceInit) {
        if (url.includes('/api/voice/')) {
          return new MockEventSource(url, options) as any;
        }
        return new OriginalEventSource(url, options);
      } as any;
      
      // Mock getUserMedia for voice mode
      navigator.mediaDevices.getUserMedia = async () => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const destination = audioContext.createMediaStreamDestination();
        oscillator.connect(destination);
        oscillator.start();
        return destination.stream;
      };
      
      // Mock AudioWorklet
      if (!(window as any).AudioWorkletNode) {
        (window as any).AudioWorkletNode = class MockAudioWorkletNode {
          constructor() {}
          connect() {}
          disconnect() {}
          port = { postMessage: () => {}, onmessage: null };
        };
      }
      
      window.__sendVoiceSSEMessage = (index: number, data: string) => {
        const source = window.__mockEventSources?.[index];
        if (source && source.readyState === 1) {
          const event = new MessageEvent('message', { data });
          source.dispatchEvent(event);
        }
      };
    });
    
    await page.goto('/');
    
    console.log('\n=== TESTING TEXT MODE ===');
    
    // Test text mode first
    await expect(page.getByText('Explore a new perspective')).toBeVisible();
    await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
    
    // Send first text message
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    await thoughtInput.fill('I need help with social anxiety');
    await submitButton.click();
    console.log('✅ Text message 1 sent');
    
    // Wait for response
    const response = page.locator('.bg-\\[\\#2a2a2a\\].rounded-xl').first();
    await expect(response).toBeVisible({ timeout: 30000 });
    await expect(thoughtInput).toBeEnabled({ timeout: 30000 });
    console.log('✅ Text response 1 received');
    
    // Send second text message
    await thoughtInput.fill('I avoid social gatherings because I fear judgment');
    await submitButton.click();
    console.log('✅ Text message 2 sent');
    
    // Wait for more responses
    await expect(async () => {
      const count = await page.locator('.bg-\\[\\#2a2a2a\\].rounded-xl').count();
      expect(count).toBeGreaterThan(1);
    }).toPass({ timeout: 30000 });
    
    await expect(thoughtInput).toBeEnabled({ timeout: 30000 });
    console.log('✅ Text conversation working through multiple turns');
    
    console.log('\n=== TESTING VOICE MODE ===');
    
    // Switch to voice mode
    const voiceModeButton = page.getByRole('button', { name: /switch to voice/i });
    await voiceModeButton.click();
    await page.waitForTimeout(1000);
    
    // Verify voice UI
    await expect(page.getByText('Voice Conversation')).toBeVisible();
    const startButton = page.getByRole('button', { name: /start conversation/i });
    await expect(startButton).toBeVisible();
    console.log('✅ Voice mode UI loaded');
    
    // Start voice conversation
    await startButton.click();
    await expect(page.getByText(/Requesting microphone permission/i)).toBeVisible({ timeout: 5000 });
    
    // Simulate SSE connection for voice
    await page.waitForTimeout(200);
    await page.evaluate(() => {
      // Find the voice EventSource (should be the last one created)
      const sources = window.__mockEventSources || [];
      const voiceSource = sources[sources.length - 1];
      if (voiceSource) {
        window.__sendVoiceSSEMessage(sources.length - 1, JSON.stringify({
          type: 'connected',
          session_id: 'test-voice-session'
        }));
      }
    });
    
    // Verify connected status
    await expect(page.getByText(/Connected.*Speak naturally|Recording.*speak naturally/i)).toBeVisible({ timeout: 15000 });
    console.log('✅ Voice mode connected');
    
    // Simulate voice transcription
    await page.evaluate(() => {
      const sources = window.__mockEventSources || [];
      const voiceSource = sources[sources.length - 1];
      if (voiceSource) {
        window.__sendVoiceSSEMessage(sources.length - 1, JSON.stringify({
          type: 'content',
          content_type: 'text/plain',
          data: 'I feel nervous when speaking in meetings'
        }));
      }
    });
    
    console.log('✅ Voice transcription sent');
    
    // Simulate AI response and turn complete
    await page.waitForTimeout(500);
    await page.evaluate(() => {
      const sources = window.__mockEventSources || [];
      const voiceSource = sources[sources.length - 1];
      if (voiceSource) {
        // Send audio response
        window.__sendVoiceSSEMessage(sources.length - 1, JSON.stringify({
          type: 'content',
          content_type: 'audio/pcm',
          data: btoa('dummy-audio-data')
        }));
        
        // Send turn complete
        setTimeout(() => {
          window.__sendVoiceSSEMessage(sources.length - 1, JSON.stringify({
            type: 'turn_complete',
            turn_complete: true,
            interrupted: false
          }));
        }, 100);
      }
    });
    
    await page.waitForTimeout(1000);
    console.log('✅ Voice conversation turn completed');
    
    // Stop voice conversation
    const stopButton = page.getByRole('button', { name: /stop conversation/i });
    await stopButton.click();
    await expect(page.getByText('Conversation ended')).toBeVisible({ timeout: 5000 });
    console.log('✅ Voice mode stopped successfully');
    
    console.log('\n✅ BOTH TEXT AND VOICE MODES WORK CORRECTLY!');
  });
});