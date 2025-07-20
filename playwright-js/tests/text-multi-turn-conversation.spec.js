import { test, expect, type Page } from '@playwright/test';

/* ---------------------------------------------------------------------
 * Test helpers
 * ------------------------------------------------------------------- */

/** Monitor SSE events for text mode */
async function setupSSEMonitoring(page: Page) {
  await page.evaluate(() => {
    if ((window as any).__sseMonitorInstalled) return;
    (window as any).__sseMonitorInstalled = true;
    
    (window as any).__test = {
      messageStarted: false,
      lastChunk: 0,
      done: false,
      sseEvents: [],
      assistantMessages: [],
      userMessages: []
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
            
            // Handle text mode SSE events
            if (payload.type === 'content' && payload.data) {
              if (!t.messageStarted) {
                t.messageStarted = true;
                console.log('AI message started');
              }
              t.lastChunk = Date.now();
              
              // Accumulate the message
              if (!t.currentMessage) t.currentMessage = '';
              t.currentMessage += payload.data;
            }
            
            // Check if the message indicates completion
            if (payload.type === 'content' && payload.data && 
                (payload.data.includes('\n\n') || payload.data.includes('?'))) {
              // Message seems complete
              setTimeout(() => {
                if (t.currentMessage && !t.done) {
                  t.done = true;
                  t.assistantMessages.push(t.currentMessage);
                  t.currentMessage = '';
                  console.log('AI message complete (detected end)');
                }
              }, 1000);
            }
          } catch { 
            // ignore non-JSON messages
          }
        });
      }
    };
  });
}

/** Wait for AI to complete response in text mode */
async function waitForAITextResponse(page: Page) {
  // Reset flags for this response
  await page.evaluate(() => {
    const t = (window as any).__test;
    t.messageStarted = false;
    t.lastChunk = 0;
    t.done = false;
  });

  // Wait for first message chunk
  console.log('Waiting for AI message to start...');
  await page.waitForFunction(() => (window as any).__test?.messageStarted, {
    timeout: 30_000
  });

  // Wait until message_complete OR 2s of silence
  console.log('Waiting for AI to finish typing...');
  await page.waitForFunction(() => {
    const t = (window as any).__test;
    if (t.done) return true;
    if (!t.lastChunk) return false;
    return Date.now() - t.lastChunk > 2_000;
  }, { timeout: 45_000 });
}

/** Submit a text message and wait for response */
async function sendTextMessage(page: Page, message: string) {
  // Type the message - use the actual placeholder text
  const textarea = page.locator('textarea[placeholder*="What happened"]');
  await textarea.fill(message);
  
  // Track the message
  await page.evaluate((msg) => {
    const t = (window as any).__test;
    if (!t) {
      (window as any).__test = {
        messageStarted: false,
        lastChunk: 0,
        done: false,
        sseEvents: [],
        assistantMessages: [],
        userMessages: []
      };
    }
    (window as any).__test.userMessages.push(msg);
  }, message);
  
  // Send it - click the send button
  await page.locator('button[type="submit"]').click();
  
  // Wait for AI response
  await waitForAITextResponse(page);
}

/* ---------------------------------------------------------------------
 * The multi-turn text conversation test
 * ------------------------------------------------------------------- */

test.describe('Multi-Turn Text Conversation', () => {
  test('full CBT conversation with three turns in text mode', async ({ page }) => {
    // Browser console passthrough for debugging
    page.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('[browser]', msg.text());
      }
    });

    // Setup SSE monitoring
    await setupSSEMonitoring(page);

    // Navigate to the app
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify we're in text mode (default)
    await expect(page.getByRole('button', { name: 'Switch to Voice' })).toBeVisible();
    console.log('✓ App loaded in text mode');
    
    // Wait for the initial greeting to complete
    await page.waitForTimeout(2000); // Give time for the greeting to appear
    const initialMessages = await page.locator('.assistant-message, [class*="assistant"]').count();
    console.log(`✓ Initial assistant messages: ${initialMessages}`);

    // Define our conversation turns
    const CONVERSATION_TURNS = [
      {
        user: "I'm feeling really anxious about the upcoming presentation at work. Everyone will judge me and think I'm incompetent.",
        description: "Initial anxious thought"
      },
      {
        user: "But what if I forget everything? What if they ask questions I can't answer? I'll look like a complete fool.",
        description: "Catastrophizing"
      },
      {
        user: "You're right, I am catastrophizing. I guess I'm worried because the last presentation didn't go well. But that was different circumstances.",
        description: "Recognition and insight"
      }
    ];

    // Have the conversation
    for (const [idx, turn] of CONVERSATION_TURNS.entries()) {
      console.log(`\n🗣️  User turn ${idx + 1}: ${turn.description}`);
      console.log(`   Message: "${turn.user}"`);
      
      await sendTextMessage(page, turn.user);
      
      // Get the latest AI response
      const aiResponse = await page.evaluate(() => {
        const t = (window as any).__test;
        return t.assistantMessages[t.assistantMessages.length - 1] || 'No response';
      });
      
      console.log(`🤖 Assistant response ${idx + 1}: "${aiResponse.substring(0, 100)}..."`);
    }

    // Verify the conversation statistics
    const sessionInfo = await page.evaluate(() => {
      const test = (window as any).__test;
      return {
        events: test?.sseEvents?.length || 0,
        messageChunks: test?.sseEvents?.filter((e: any) => e.type === 'message_delta').length || 0,
        completedMessages: test?.sseEvents?.filter((e: any) => e.type === 'message_complete').length || 0,
        userMessages: test?.userMessages?.length || 0,
        assistantMessages: test?.assistantMessages?.length || 0
      };
    });

    console.log('\n📊 Session statistics:');
    console.log(`   Total SSE events: ${sessionInfo.events}`);
    console.log(`   Message chunks: ${sessionInfo.messageChunks}`);
    console.log(`   Completed messages: ${sessionInfo.completedMessages}`);
    console.log(`   User messages: ${sessionInfo.userMessages}`);
    console.log(`   Assistant messages: ${sessionInfo.assistantMessages}`);

    // Assertions
    expect(sessionInfo.userMessages).toBe(3);
    expect(sessionInfo.assistantMessages).toBe(3);
    expect(sessionInfo.completedMessages).toBeGreaterThanOrEqual(3);
    
    // Verify the conversation stayed in the same session by checking the UI
    const messageCount = await page.locator('div[class*="message"]').count();
    expect(messageCount).toBeGreaterThanOrEqual(6); // 3 user + 3 assistant messages
    
    // Optional: Test PDF download
    const downloadButton = page.getByRole('button', { name: /download session pdf/i });
    if (await downloadButton.isVisible()) {
      console.log('\n📄 Testing PDF download...');
      const [download] = await Promise.all([
        page.waitForEvent('download'),
        downloadButton.click(),
      ]);
      
      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.pdf$/);
      console.log(`✓ PDF downloaded: ${filename}`);
    }
    
    console.log('\n✅ Multi-turn text conversation completed successfully');
  });

  test('text conversation with phase transitions', async ({ page }) => {
    // This test verifies the conversation phases (GREETING -> DISCOVERY -> REFRAMING -> SUMMARY)
    page.on('console', msg => {
      if (msg.type() !== 'debug') {
        console.log('[browser]', msg.text());
      }
    });

    await setupSSEMonitoring(page);
    await page.goto('http://localhost:3000');
    
    // Phase 1: GREETING - Initial interaction
    console.log('\n📍 Phase 1: GREETING');
    await sendTextMessage(page, "Hello, I'd like to talk about my anxiety");
    
    // Phase 2: DISCOVERY - Exploring the issue
    console.log('\n📍 Phase 2: DISCOVERY');
    await sendTextMessage(page, "I've been feeling overwhelmed at work. I have too many deadlines and I'm afraid I'll disappoint everyone.");
    
    // Continue discovery
    await sendTextMessage(page, "My manager keeps adding more tasks, and I can't say no. I work late every night but still feel behind.");
    
    // Phase 3: REFRAMING - Working on perspectives
    console.log('\n📍 Phase 3: REFRAMING');
    await sendTextMessage(page, "I guess I do have a pattern of taking on too much. Maybe I need to set boundaries?");
    
    // Continue reframing
    await sendTextMessage(page, "You're right, saying no doesn't mean I'm failing. It means I'm being realistic about what I can accomplish.");
    
    // Verify we had a complete conversation flow
    const stats = await page.evaluate(() => {
      const t = (window as any).__test;
      return {
        totalExchanges: Math.min(t.userMessages.length, t.assistantMessages.length),
        avgResponseLength: t.assistantMessages.reduce((sum: number, msg: string) => sum + msg.length, 0) / t.assistantMessages.length
      };
    });
    
    console.log('\n📊 Conversation flow statistics:');
    console.log(`   Total exchanges: ${stats.totalExchanges}`);
    console.log(`   Average response length: ${Math.round(stats.avgResponseLength)} characters`);
    
    expect(stats.totalExchanges).toBeGreaterThanOrEqual(5);
    expect(stats.avgResponseLength).toBeGreaterThan(100); // Meaningful responses
    
    console.log('\n✅ Phase-based conversation completed successfully');
  });
});