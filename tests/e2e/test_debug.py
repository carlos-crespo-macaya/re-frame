"""Debug test to check page content"""
import pytest
from playwright.async_api import Page

@pytest.mark.asyncio
async def test_page_content(page: Page):
    """Check what's actually on the page"""
    await page.goto("http://localhost:3000")
    await page.wait_for_timeout(3000)
    
    # Take screenshot
    await page.screenshot(path="debug_screenshot.png")
    
    # Get page content
    content = await page.content()
    
    # Look for buttons
    buttons = await page.locator("button").all()
    print(f"\nFound {len(buttons)} buttons")
    
    for i, button in enumerate(buttons):
        text = await button.text_content()
        print(f"Button {i}: '{text}'")
    
    # Look for mode-related elements
    mode_elements = await page.locator("*:has-text('mode')").all()
    print(f"\nFound {len(mode_elements)} elements with 'mode'")
    
    # Check for voice/text switching
    switch_elements = await page.locator("*:has-text('Switch')").all()
    print(f"\nFound {len(switch_elements)} elements with 'Switch'")
    
    for elem in switch_elements[:3]:
        text = await elem.text_content()
        print(f"Switch element: '{text}'")