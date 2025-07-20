// Test turn_complete handling in frontend
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => console.log('Browser:', msg.text()));
  
  try {
    await page.goto('http://localhost:3001');
    
    // Wait for connection
    await page.waitForSelector('text=Connected', { timeout: 10000 });
    console.log('✅ Connected');
    
    // Get initial button state
    const buttonInitial = await page.evaluate(() => {
      const button = document.querySelector('[type="submit"]');
      const textarea = document.querySelector('textarea');
      return {
        buttonDisabled: button?.disabled,
        buttonText: button?.textContent,
        textareaDisabled: textarea?.disabled
      };
    });
    console.log('Initial state:', buttonInitial);
    
    // Type a message
    const textarea = page.locator('textarea');
    await textarea.fill('I need help with anxiety');
    
    // Get state after typing
    const buttonAfterTyping = await page.evaluate(() => {
      const button = document.querySelector('[type="submit"]');
      const textarea = document.querySelector('textarea');
      return {
        buttonDisabled: button?.disabled,
        buttonText: button?.textContent,
        textareaDisabled: textarea?.disabled
      };
    });
    console.log('After typing:', buttonAfterTyping);
    
    // Submit
    await page.click('[type="submit"]');
    console.log('✅ Submitted');
    
    // Get state during loading
    await page.waitForTimeout(500);
    const buttonDuringLoading = await page.evaluate(() => {
      const button = document.querySelector('[type="submit"]');
      const textarea = document.querySelector('textarea');
      return {
        buttonDisabled: button?.disabled,
        buttonText: button?.textContent,
        textareaDisabled: textarea?.disabled
      };
    });
    console.log('During loading:', buttonDuringLoading);
    
    // Wait for response to appear
    await page.waitForSelector('.bg-\\[\\#2a2a2a\\]', { timeout: 10000 });
    console.log('✅ Response appeared');
    
    // Wait a bit more and check final state
    await page.waitForTimeout(2000);
    const buttonFinal = await page.evaluate(() => {
      const button = document.querySelector('[type="submit"]');
      const textarea = document.querySelector('textarea');
      return {
        buttonDisabled: button?.disabled,
        buttonText: button?.textContent,
        textareaDisabled: textarea?.disabled
      };
    });
    console.log('Final state:', buttonFinal);
    
    // Check if we received turn_complete by looking at console logs
    const logs = await page.evaluate(() => window.consoleLogs || []);
    const hasTurnComplete = logs.some(log => log.includes('Turn complete'));
    console.log('Turn complete in logs:', hasTurnComplete);
    
    // Conclusion
    if (!buttonFinal.buttonDisabled && !buttonFinal.textareaDisabled) {
      console.log('\n✅ SUCCESS: Input re-enabled after response!');
    } else {
      console.log('\n❌ FAILURE: Input still disabled after response!');
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    await browser.close();
  }
})();