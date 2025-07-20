import { test, expect, type Page } from '@playwright/test';

/** Helper to get the last AI message */
function getLastAIMessage(page: Page) {
  return page.locator('[data-role="ai"]').last();
}

/** Helper to wait for new AI message */
async function waitForNewAIMessage(page: Page, previousCount: number) {
  await page.waitForFunction(
    (count) => {
      const messages = document.querySelectorAll('[data-role="ai"]');
      return messages.length > count;
    },
    previousCount,
    { timeout: 30000 }
  );
}

test.describe('Text Mode Multi-Turn Conversation', () => {
  test('complete CBT conversation with three turns', async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify we're in text mode (default)
    await expect(page.getByRole('button', { name: 'Switch to Voice' })).toBeVisible();
    console.log('✓ App loaded in text mode');
    
    // Wait for any initial greeting
    await page.waitForTimeout(2000);
    
    // Count initial AI messages
    const initialAICount = await page.locator('[data-role="ai"]').count();
    console.log(`Initial AI messages: ${initialAICount}`);
    
    // Turn 1: Initial anxious thought
    console.log('\n🗣️  Turn 1: Initial anxious thought');
    const thought1 = "I'm feeling really anxious about the upcoming presentation at work. Everyone will judge me and think I'm incompetent.";
    
    const textarea1 = page.locator('textarea[placeholder*="What happened"]');
    await textarea1.fill(thought1);
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for AI response
    await waitForNewAIMessage(page, initialAICount);
    const response1 = await getLastAIMessage(page).textContent();
    console.log(`🤖 AI response 1: "${response1?.substring(0, 100)}..."`);
    
    // Clear textarea for next message
    await textarea1.clear();
    
    // Turn 2: Catastrophizing
    console.log('\n🗣️  Turn 2: Catastrophizing');
    const thought2 = "But what if I forget everything? What if they ask questions I can't answer? I'll look like a complete fool.";
    
    const currentCount2 = await page.locator('[data-role="ai"]').count();
    await textarea1.fill(thought2);
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for AI response
    await waitForNewAIMessage(page, currentCount2);
    const response2 = await getLastAIMessage(page).textContent();
    console.log(`🤖 AI response 2: "${response2?.substring(0, 100)}..."`);
    
    // Clear textarea for next message
    await textarea1.clear();
    
    // Turn 3: Recognition and insight
    console.log('\n🗣️  Turn 3: Recognition and insight');
    const thought3 = "You're right, I am catastrophizing. I guess I'm worried because the last presentation didn't go well. But that was different circumstances.";
    
    const currentCount3 = await page.locator('[data-role="ai"]').count();
    await textarea1.fill(thought3);
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for AI response
    await waitForNewAIMessage(page, currentCount3);
    const response3 = await getLastAIMessage(page).textContent();
    console.log(`🤖 AI response 3: "${response3?.substring(0, 100)}..."`);
    
    // Verify we had a complete conversation
    const finalAICount = await page.locator('[data-role="ai"]').count();
    const userMessageCount = await page.locator('[data-role="user"]').count();
    
    console.log('\n📊 Conversation statistics:');
    console.log(`   AI messages: ${finalAICount}`);
    console.log(`   User messages: ${userMessageCount}`);
    console.log(`   Total exchanges: ${Math.min(finalAICount - initialAICount, userMessageCount)}`);
    
    // Assertions
    expect(finalAICount - initialAICount).toBeGreaterThanOrEqual(3);
    expect(userMessageCount).toBeGreaterThanOrEqual(3);
    
    // Optional: Test PDF download
    const downloadButton = page.getByRole('button', { name: /download.*pdf/i });
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
  
  test('conversation maintains context across turns', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');
    
    // Wait for initial load
    await page.waitForTimeout(2000);
    const textarea = page.locator('textarea[placeholder*="What happened"]');
    
    // Turn 1: Introduce a specific topic
    console.log('\n🗣️  Turn 1: Introducing topic');
    await textarea.fill("I have a big job interview next week and I'm terrified.");
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for response
    await page.waitForFunction(
      () => document.querySelectorAll('[data-role="ai"]').length >= 1,
      { timeout: 30000 }
    );
    
    // Turn 2: Reference the previous topic without mentioning it explicitly
    console.log('\n🗣️  Turn 2: Testing context retention');
    await textarea.clear();
    await textarea.fill("What if they think I'm not qualified enough?");
    await page.getByRole('button', { name: /generate perspective/i }).click();
    
    // Wait for response
    await page.waitForFunction(
      () => document.querySelectorAll('[data-role="ai"]').length >= 2,
      { timeout: 30000 }
    );
    
    // Get the second response and verify it maintains context
    const response = await page.locator('[data-role="ai"]').nth(1).textContent();
    console.log(`🤖 Assistant response shows context awareness: ${response?.includes('interview') || response?.includes('job')}`);
    
    // The response should reference the interview context
    expect(response?.toLowerCase()).toMatch(/interview|job|qualification|qualified/);
    
    console.log('\n✅ Context maintained across conversation turns');
  });
});