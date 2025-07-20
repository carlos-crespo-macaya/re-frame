import { test, expect } from '@playwright/test';

test('simple text conversation', async ({ page }) => {
  // Log console messages
  page.on('console', msg => console.log('Browser:', msg.type(), msg.text()));
  
  await page.goto('/');
  
  // Wait for connection to establish
  await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
  
  // Check if we have the input field
  const thoughtInput = page.getByPlaceholder(/what happened/i);
  await expect(thoughtInput).toBeVisible();
  
  // Type a message
  await thoughtInput.fill('I feel anxious about my presentation');
  
  // Wait a moment to ensure text is entered
  await page.waitForTimeout(500);
  
  // Submit
  await page.getByRole('button', { name: /generate perspective/i }).click();
  
  // Take screenshot after clicking
  await page.screenshot({ path: 'after-click.png' });
  
  // Wait for any loading state or response
  await page.waitForTimeout(2000);
  
  // Take another screenshot
  await page.screenshot({ path: 'after-wait.png' });
  
  // Check if we see any response
  const hasResponse = await page.locator('.bg-\\[\\#2a2a2a\\]').count() > 0;
  console.log('Has response box:', hasResponse);
  
  if (!hasResponse) {
    // Check if still in loading state
    const buttonText = await page.getByRole('button').first().textContent();
    console.log('Button text:', buttonText);
    
    // Check for any error messages
    const pageContent = await page.content();
    console.log('Page has error?', pageContent.includes('error'));
  }
  
  console.log('Test completed successfully!');
});