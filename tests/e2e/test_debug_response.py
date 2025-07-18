"""Debug test to understand response rendering"""
import pytest
from playwright.async_api import Page

@pytest.mark.asyncio
async def test_response_structure(page: Page, backend_ready):
    """Debug test to see how responses are rendered"""
    await page.goto("http://localhost:3000")
    await page.wait_for_timeout(2000)
    
    # Enter text
    textarea = page.locator('textarea')
    await textarea.fill("I feel anxious")
    
    # Submit
    submit_button = page.locator('button:has-text("Generate perspective")')
    await submit_button.click()
    
    # Wait a bit for response
    await page.wait_for_timeout(5000)
    
    # Take screenshot
    await page.screenshot(path="response_debug.png")
    
    # Find all divs with meaningful content
    print("\n=== Looking for response content ===")
    
    # Check for any prose containers
    prose_elements = await page.locator('.prose').all()
    print(f"Found {len(prose_elements)} prose elements")
    for i, elem in enumerate(prose_elements):
        text = await elem.text_content()
        print(f"Prose {i}: '{text}'")
    
    # Check for styled response divs
    response_divs = await page.locator('div[class*="bg-"]').all()
    print(f"\nFound {len(response_divs)} styled divs")
    for i, div in enumerate(response_divs[:5]):  # First 5 only
        classes = await div.get_attribute("class")
        text = await div.text_content()
        if text and len(text.strip()) > 20:
            print(f"Div {i} (classes: {classes}): '{text[:100]}...'")
    
    # Check page structure after submission
    page_content = await page.content()
    
    # Look for specific patterns in the HTML
    if "prose" in page_content:
        print("\n✓ Found 'prose' class in page")
    if "bg-[#2a2a2a]" in page_content:
        print("✓ Found specific background color")
    if "Okay" in page_content or "hear" in page_content:
        print("✓ Found response text in page")
        
    # Check console logs
    console_logs = []
    page.on("console", lambda msg: console_logs.append(msg))
    await page.wait_for_timeout(1000)
    
    print(f"\nConsole logs: {len(console_logs)}")