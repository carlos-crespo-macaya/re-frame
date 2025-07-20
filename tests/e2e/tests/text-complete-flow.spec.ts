import { test, expect } from '@playwright/test';

test.describe('Complete Text Conversation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Log console messages
    page.on('console', msg => console.log('Browser:', msg.type(), msg.text()));
    page.on('pageerror', error => console.log('Page error:', error));
  });

  test('complete text CBT conversation through all phases', async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    
    // Wait for connection to establish
    await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
    console.log('✅ Connected to text mode');
    
    // Track conversation phases
    const phases = [
      { 
        phase: 'greeting',
        input: "I'm feeling really anxious about an upcoming presentation at work",
        expectedResponse: /CBT Assistant|help.*reframe|thinking patterns/i
      },
      { 
        phase: 'discovery',
        input: "I keep thinking everyone will judge me and notice all my mistakes",
        expectedResponse: /tell me more|sounds like|thinking patterns|catastrophizing/i
      },
      { 
        phase: 'reframing',
        input: "You're right, I am assuming the worst without any evidence",
        expectedResponse: /alternative|perspective|evidence|balanced/i
      },
      { 
        phase: 'summary',
        input: "Thank you, I feel more confident about approaching this differently",
        expectedResponse: /summary|remember|practice|helpful/i
      }
    ];
    
    for (const [index, phase] of phases.entries()) {
      console.log(`\n--- Phase ${index + 1}: ${phase.phase} ---`);
      
      // Find input field
      const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
      await expect(thoughtInput).toBeVisible();
      
      // Type the message
      await thoughtInput.fill(phase.input);
      console.log('User input:', phase.input);
      
      // Submit
      const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
      await submitButton.click();
      
      // Wait for response
      await page.waitForTimeout(2000);
      
      // Check for AI response - wait for markdown content inside the response container
      await page.waitForSelector('.bg-\\[\\#2a2a2a\\] .prose', { timeout: 5000 });
      
      // Get all response elements with actual content
      const responseElements = await page.locator('.bg-\\[\\#2a2a2a\\]').filter({ has: page.locator('.prose') }).all();
      expect(responseElements.length).toBeGreaterThan(index);
      
      // Get the latest response text from the markdown content
      const latestResponse = responseElements[responseElements.length - 1];
      const responseText = await latestResponse.locator('.prose').textContent();
      console.log('AI response preview:', responseText?.substring(0, 100) + '...');
      
      // Verify response matches expected pattern
      expect(responseText).toMatch(phase.expectedResponse);
      
      // Clear input for next phase
      await thoughtInput.clear();
    }
    
    console.log('\n✅ Text conversation completed all phases successfully!');
    
    // Verify we went through all phases
    const allResponses = await page.locator('.bg-\\[\\#2a2a2a\\], .assistant-message, [data-testid="assistant-message"]').count();
    expect(allResponses).toBeGreaterThanOrEqual(phases.length);
  });

  test('text mode handles turn_complete events correctly', async ({ page }) => {
    await page.goto('/');
    
    // Wait for connection
    await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
    
    // Send a message
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    await thoughtInput.fill("I need help with my anxiety");
    await page.getByRole('button', { name: /generate perspective|send/i }).click();
    
    // Wait for response and turn complete
    await page.waitForSelector('.bg-\\[\\#2a2a2a\\] .prose', { timeout: 5000 });
    
    // Wait for input to be re-enabled after turn complete
    await expect(thoughtInput).toBeEnabled({ timeout: 10000 });
    
    // Verify we can send another message
    await thoughtInput.fill("Can you explain more about CBT?");
    await page.getByRole('button', { name: /generate perspective|send/i }).click();
    
    // Wait for second response
    await page.waitForTimeout(2000);
    
    // Verify we have multiple responses
    const responses = await page.locator('.bg-\\[\\#2a2a2a\\], .assistant-message, [data-testid="assistant-message"]').count();
    expect(responses).toBeGreaterThanOrEqual(2);
    
    console.log('✅ Text mode turn_complete handling works correctly');
  });

  test('text mode error handling', async ({ page }) => {
    await page.goto('/');
    
    // Wait for connection
    await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
    
    // Try to send an empty message
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    await thoughtInput.clear();
    
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    // Check if button is disabled for empty input
    const isDisabled = await submitButton.isDisabled();
    if (isDisabled) {
      console.log('✅ Submit button correctly disabled for empty input');
    } else {
      // If not disabled, try clicking and check for validation
      await submitButton.click();
      
      // Check for any error message
      const errorMessage = await page.locator('.text-red-500, .error-message, [role="alert"]').first();
      if (await errorMessage.isVisible()) {
        console.log('✅ Error message shown for empty input');
      }
    }
    
    // Test with very long input
    const longText = 'This is a very long message. '.repeat(100);
    await thoughtInput.fill(longText);
    await submitButton.click();
    
    // Should still get a response
    await page.waitForTimeout(2000);
    const hasResponse = await page.locator('.bg-\\[\\#2a2a2a\\], .assistant-message').count() > 0;
    expect(hasResponse).toBeTruthy();
    
    console.log('✅ Text mode handles edge cases correctly');
  });
});