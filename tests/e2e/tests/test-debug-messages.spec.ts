import { test, expect } from '@playwright/test';

test.describe('Debug Message Processing', () => {
  test('debug turn_complete message flow', async ({ page }) => {
    // Enable all console logging
    page.on('console', msg => {
      console.log(`[${msg.type()}]`, msg.text());
    });
    
    // Add script to log all message processing
    await page.addInitScript(() => {
      // Intercept console.log to capture all logs
      const originalLog = console.log;
      window.consoleLogs = [];
      console.log = (...args) => {
        window.consoleLogs.push(args.join(' '));
        originalLog(...args);
      };
    });
    
    await page.goto('/');
    
    // Wait for connection
    await page.waitForTimeout(2000);
    
    // Type and submit
    const thoughtInput = page.getByPlaceholder(/what happened|share your thought/i);
    const submitButton = page.getByRole('button', { name: /generate perspective|send/i });
    
    await thoughtInput.fill('I need help with my anxiety');
    await submitButton.click();
    
    // Wait for response
    await page.waitForSelector('.bg-\\[\\#2a2a2a\\]', { timeout: 10000 });
    
    // Get all console logs
    const logs = await page.evaluate(() => window.consoleLogs || []);
    console.log('\n=== ALL CONSOLE LOGS ===');
    logs.forEach((log, i) => console.log(`${i}: ${log}`));
    
    // Check specific things
    const messageProcessingLogs = logs.filter(log => 
      log.includes('Current messages') || 
      log.includes('turn_complete') ||
      log.includes('Latest response')
    );
    
    console.log('\n=== MESSAGE PROCESSING LOGS ===');
    messageProcessingLogs.forEach(log => console.log(log));
    
    // Check button state
    const isDisabled = await submitButton.isDisabled();
    console.log('\n=== BUTTON STATE ===');
    console.log('Button is disabled:', isDisabled);
    
    // Get messages from React state if possible
    const messages = await page.evaluate(() => {
      // Try to find React fiber and extract state
      const rootElement = document.getElementById('root') || document.querySelector('main');
      if (!rootElement) return null;
      
      const key = Object.keys(rootElement).find(key => key.startsWith('__reactFiber'));
      if (!key) return null;
      
      // This is a simplified approach - in reality we'd need to traverse the fiber tree
      return 'Unable to extract React state directly';
    });
    
    console.log('\n=== REACT STATE ===');
    console.log('Messages:', messages);
    
    // Final assertions
    expect(isDisabled).toBe(false);
  });
});