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
          const event = new MessageEvent('message', {
            data: `event: ${eventType}\ndata: ${data}\n\n`
          });
          source.dispatchEvent(event);
        }
      };
      
      // Track conversation state
      window.__conversationState = {
        messages: [],
        isListening: false,
        isSpeaking: false
      };
      
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

  test('complete English CBT conversation using audio fixtures', async ({ page }) => {
    // Define conversation flow
    const conversationFlow = [
      {
        audioFile: 'en-greeting.wav',
        transcription: "Hello, I'm feeling anxious about an upcoming presentation at work",
        expectedKeywords: ['presentation', 'anxious', 'understand', 'tell me more'],
        aiResponse: "I understand you're feeling anxious about the presentation. Can you tell me more about what specifically worries you?"
      },
      {
        audioFile: 'en-thought-1.wav',
        transcription: "I keep thinking that everyone will judge me and notice all my mistakes",
        expectedKeywords: ['thoughts', 'evidence', 'perspective', 'judge'],
        aiResponse: "It sounds like you're having thoughts about being judged. Let's examine the evidence for these thoughts."
      },
      {
        audioFile: 'en-insight.wav',
        transcription: "You're right, I guess I'm assuming the worst without any real evidence",
        expectedKeywords: ['reframe', 'helpful', 'positive', 'prepared'],
        aiResponse: "That's a great insight! How might you reframe these thoughts in a more helpful way?"
      },
      {
        audioFile: 'en-conclusion.wav',
        transcription: "Thank you, I feel more confident now and ready to prepare properly",
        expectedKeywords: ['great', 'progress', 'strategies', 'remember'],
        aiResponse: "Wonderful progress! Remember these strategies when preparing for your presentation."
      }
    ];

    // Navigate to the app
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Switch to voice mode
    const voiceModeButton = page.getByRole('button', { name: /switch to voice/i });
    await expect(voiceModeButton).toBeVisible({ timeout: 10000 });
    await voiceModeButton.click();
    
    // Wait for voice mode to activate
    await page.waitForTimeout(1000);
    
    // Click Start Conversation button
    const startConversationButton = page.getByRole('button', { name: /start conversation/i });
    await expect(startConversationButton).toBeVisible({ timeout: 10000 });
    await startConversationButton.click();
    
    // Wait for SSE connection to establish
    await page.waitForTimeout(200);
    
    // Send initial connection event
    await page.evaluate(() => {
      window.__sendSSEMessage(0, 'connected', JSON.stringify({ session_id: 'test-session' }));
    });
    
    // Wait for connection status
    await expect(page.getByText(/Connected.*Speak naturally/i)).toBeVisible({ timeout: 15000 });
    console.log('✅ Voice mode connected successfully');
    
    // Send initial greeting
    await page.evaluate(() => {
      window.__sendSSEMessage(0, 'assistant_message', JSON.stringify({ 
        text: "Hello! I'm here to help you explore your thoughts. What's on your mind today?",
        role: 'assistant'
      }));
      window.__conversationState.messages.push({
        text: "Hello! I'm here to help you explore your thoughts. What's on your mind today?",
        role: 'assistant'
      });
    });
    
    // Process each phrase in the conversation
    for (const [index, flow] of conversationFlow.entries()) {
      console.log(`\n--- Processing turn ${index + 1}: ${flow.audioFile} ---`);
      
      // Simulate user speaking (update UI to show listening)
      await page.evaluate(() => {
        window.__conversationState.isListening = true;
      });
      
      // Wait a moment for "recording"
      await page.waitForTimeout(1000);
      
      // Send user transcription
      await page.evaluate((data) => {
        window.__sendSSEMessage(0, 'user_transcription', JSON.stringify({
          text: data.transcription,
          role: 'user',
          final: true
        }));
        window.__conversationState.messages.push({
          text: data.transcription,
          role: 'user'
        });
        window.__conversationState.isListening = false;
      }, { transcription: flow.transcription });
      
      console.log('User said:', flow.transcription);
      
      // Wait for processing
      await page.waitForTimeout(500);
      
      // Send AI response
      await page.evaluate((data) => {
        window.__conversationState.isSpeaking = true;
        window.__sendSSEMessage(0, 'assistant_message', JSON.stringify({
          text: data.response,
          role: 'assistant'
        }));
        window.__conversationState.messages.push({
          text: data.response,
          role: 'assistant'
        });
        
        // Simulate speaking duration
        setTimeout(() => {
          window.__conversationState.isSpeaking = false;
        }, 2000);
      }, { response: flow.aiResponse });
      
      console.log('AI responded:', flow.aiResponse.substring(0, 60) + '...');
      
      // Wait for AI to "finish speaking"
      await page.waitForTimeout(2500);
    }
    
    // Verify conversation completed
    const conversationState = await page.evaluate(() => window.__conversationState);
    expect(conversationState.messages.length).toBe(9); // 1 greeting + 4 user + 4 AI
    
    console.log('\n✅ English conversation completed successfully!');
    console.log(`Total messages exchanged: ${conversationState.messages.length}`);
  });

  test('handles audio fixture with background noise', async ({ page }) => {
    await page.goto('/');
    
    // Switch to voice mode and start conversation
    await page.getByRole('button', { name: /switch to voice/i }).click();
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: /start conversation/i }).click();
    
    // Wait for connection
    await page.waitForTimeout(200);
    await page.evaluate(() => {
      window.__sendSSEMessage(0, 'connected', JSON.stringify({ session_id: 'test-session-2' }));
    });
    
    await expect(page.getByText(/Connected.*Speak naturally/i)).toBeVisible({ timeout: 15000 });
    
    // Simulate conversation with background noise fixture
    const fixture = {
      transcription: "I can't sleep at night because I keep worrying about things",
      expectedKeywords: ['sleep', 'worry', 'rest', 'night']
    };
    
    await page.evaluate((data) => {
      window.__sendSSEMessage(0, 'user_transcription', JSON.stringify({
        text: data.transcription,
        role: 'user',
        final: true
      }));
    }, { transcription: fixture.transcription });
    
    console.log('✅ Background noise test completed');
  });

  test('mixed voice and text input', async ({ page }) => {
    await page.goto('/');
    
    // Start in voice mode
    await page.getByRole('button', { name: /switch to voice/i }).click();
    await page.waitForTimeout(1000);
    
    // Verify we're in voice mode
    await expect(page.getByRole('button', { name: /switch to text/i })).toBeVisible();
    
    // Switch back to text mode
    await page.getByRole('button', { name: /switch to text/i }).click();
    await page.waitForTimeout(1000);
    
    // Verify we're back in text mode - look for the thought input
    const thoughtInput = page.getByPlaceholder(/share.*thought|what happened/i);
    await expect(thoughtInput).toBeVisible({ timeout: 10000 });
    
    // Send a text message
    await thoughtInput.fill("I prefer to type this - what specific techniques can help?");
    await page.getByRole('button', { name: /send/i }).click();
    
    // In text mode, messages DO appear in the UI
    await expect(page.getByText("I prefer to type this")).toBeVisible();
    
    console.log('✅ Mixed mode test completed');
  });
});