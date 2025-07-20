import { test, expect } from '@playwright/test';

test.describe('Turn Complete with Mock', () => {
  test('frontend handles turn_complete correctly', async ({ page }) => {
    // Track console logs
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      consoleLogs.push(text);
      if (text.includes('turn_complete') || text.includes('Turn complete')) {
        console.log('[CONSOLE]', text);
      }
    });
    
    // Mock the SSE endpoint
    await page.route('**/api/events/*', async (route) => {
      console.log('SSE route intercepted for:', route.request().url());
      const sse = route.request().sse();
      
      // Wait for the actual message to be sent
      setTimeout(async () => {
        console.log('Sending mock response...');
        // Send a text message
        await sse.push({ 
          data: JSON.stringify({ 
            mime_type: 'text/plain',
            data: 'This is a test response from the assistant.'
          }) 
        });
        
        // Send turn_complete after a short delay
        setTimeout(async () => {
          console.log('Sending turn_complete...');
          await sse.push({ 
            data: JSON.stringify({ 
              turn_complete: true,
              interrupted: false
            }) 
          });
        }, 500);
      }, 1000);
    });
    
    await page.goto('/');
    
    // Type and submit
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    await thoughtInput.fill('I need help with my anxiety');
    
    // Check initial state
    const beforeSubmit = await submitButton.isDisabled();
    console.log('Button disabled before submit:', beforeSubmit);
    
    await submitButton.click();
    console.log('Message submitted');
    
    // Wait for response to appear
    await page.waitForSelector('.bg-\\[\\#2a2a2a\\]', { timeout: 10000 });
    console.log('Response appeared');
    
    // Check if button is disabled during loading
    const duringLoading = await submitButton.isDisabled();
    console.log('Button disabled during loading:', duringLoading);
    
    // Wait for turn_complete to re-enable the button
    await expect(submitButton).toBeEnabled({ timeout: 10000 });
    console.log('Button re-enabled!');
    
    // Check console logs for turn_complete
    const hasTurnComplete = consoleLogs.some(log => 
      log.includes('turn_complete') || log.includes('Turn complete')
    );
    console.log('Turn complete found in logs:', hasTurnComplete);
    console.log('Total console logs:', consoleLogs.length);
    
    // Verify we can type again
    await thoughtInput.fill('Another message');
    await expect(submitButton).toBeEnabled();
    
    console.log('✅ Test passed - turn_complete handled correctly');
  });
});