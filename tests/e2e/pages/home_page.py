"""
Home Page Object for the main CBT Assistant interface.
"""
from typing import Optional
from playwright.async_api import Page, expect
from .base_page import BasePage


class HomePage(BasePage):
    """Page object for the home page."""
    
    # Selectors
    SWITCH_TO_VOICE_BUTTON = 'button:has-text("Switch to Voice")'
    SWITCH_TO_TEXT_BUTTON = 'button:has-text("Switch to Text")'
    THOUGHT_INPUT = 'textarea'
    SUBMIT_BUTTON = 'button:has-text("Generate perspective")'
    CLEAR_BUTTON = 'button:has-text("Clear")'
    RESPONSE_CONTAINER = '.prose'
    TRANSPARENCY_SECTION = 'div:has(h3:has-text("Transparency"))'
    LANGUAGE_SELECTOR = 'select'
    LOADING_INDICATOR = '[role="status"]'
    ERROR_MESSAGE = '.text-red-500'
    
    # Voice mode selectors
    START_CONVERSATION_BUTTON = 'button:has-text("Start Conversation")'
    STOP_CONVERSATION_BUTTON = 'button:has-text("Stop Conversation")'
    VOICE_STATUS = '.text-muted-foreground'
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    async def select_text_mode(self) -> None:
        """Select text mode - only click if in voice mode."""
        # Check if we need to switch from voice to text
        if await self.is_visible(self.SWITCH_TO_TEXT_BUTTON, timeout=1000):
            await self.click_and_wait(self.SWITCH_TO_TEXT_BUTTON)
    
    async def select_voice_mode(self) -> None:
        """Select voice mode - only click if in text mode."""
        # Check if we need to switch from text to voice
        if await self.is_visible(self.SWITCH_TO_VOICE_BUTTON, timeout=1000):
            await self.click_and_wait(self.SWITCH_TO_VOICE_BUTTON)
    
    async def enter_thought(self, thought: str) -> None:
        """Enter a thought in the text input."""
        await self.fill_input(self.THOUGHT_INPUT, thought)
    
    async def submit_thought(self) -> None:
        """Submit the thought form."""
        await self.page.click(self.SUBMIT_BUTTON)
        # The app may not show a loading indicator, just wait a bit
        await self.page.wait_for_timeout(500)
    
    async def clear_form(self) -> None:
        """Clear the form."""
        await self.page.click(self.CLEAR_BUTTON)
        # Verify input is cleared
        input_element = self.page.locator(self.THOUGHT_INPUT)
        await expect(input_element).to_have_value("")
    
    async def wait_for_response(self, timeout: int = 30000) -> str:
        """Wait for and return the reframed response."""
        # The app displays responses in a div with these classes
        response_selector = 'div.mt-8.p-6.bg-\\[\\#2a2a2a\\]'
        
        # Wait for response element to appear
        response_element = await self.wait_for_element(response_selector, timeout=timeout)
        
        # Get the text content from the prose div inside
        prose_element = response_element.locator(self.RESPONSE_CONTAINER)
        await prose_element.wait_for(state='visible', timeout=5000)
        
        # Wait for the response to stabilize (no more updates)
        # This ensures we get the complete response, not a partial one
        previous_text = ""
        stable_count = 0
        check_interval = 500  # Check every 500ms
        
        while stable_count < 2:  # Need 2 consecutive checks with same text
            await self.page.wait_for_timeout(check_interval)
            current_text = await prose_element.text_content() or ""
            
            if current_text == previous_text:
                stable_count += 1
            else:
                stable_count = 0
                previous_text = current_text
            
            # Safety check to avoid infinite loop
            if stable_count == 0 and check_interval * 10 > timeout:
                break
        
        # Also wait for loading indicator to be hidden if it's present
        try:
            await self.page.wait_for_selector(self.LOADING_INDICATOR, state='hidden', timeout=2000)
        except:
            # Loading indicator might not be visible
            pass
        
        return await prose_element.text_content() or ""
    
    async def get_transparency_info(self) -> Optional[str]:
        """Get transparency information if available."""
        if await self.is_visible(self.TRANSPARENCY_SECTION):
            return await self.get_text(self.TRANSPARENCY_SECTION)
        return None
    
    async def select_language(self, language_code: str) -> None:
        """Select a language from the dropdown."""
        await self.page.select_option(self.LANGUAGE_SELECTOR, language_code)
    
    async def get_selected_language(self) -> str:
        """Get the currently selected language."""
        return await self.page.input_value(self.LANGUAGE_SELECTOR)
    
    async def wait_for_connection(self, timeout: int = 10000) -> None:
        """Wait for the SSE connection to be established."""
        # For text mode, connection should happen automatically
        await self.page.wait_for_function(
            """
            () => {
                // Check if the chat context indicates connection
                return document.body.textContent.includes('Connecting...') === false;
            }
            """,
            timeout=timeout
        )
    
    # Voice mode methods
    async def start_voice_conversation(self) -> None:
        """Start a voice conversation."""
        await self.page.click(self.START_CONVERSATION_BUTTON)
        # Wait for button to change to "Stop Conversation"
        await self.wait_for_element(self.STOP_CONVERSATION_BUTTON)
    
    async def stop_voice_conversation(self) -> None:
        """Stop a voice conversation."""
        await self.page.click(self.STOP_CONVERSATION_BUTTON)
        # Wait for button to change back to "Start Conversation"
        await self.wait_for_element(self.START_CONVERSATION_BUTTON)
    
    async def get_voice_status(self) -> str:
        """Get the current voice status message."""
        return await self.get_text(self.VOICE_STATUS)
    
    async def grant_microphone_permission(self) -> None:
        """Grant microphone permission to the page."""
        await self.page.context.grant_permissions(['microphone'])
    
    async def wait_for_error(self, timeout: int = 5000) -> Optional[str]:
        """Wait for and return any error message."""
        try:
            error_element = await self.wait_for_element(self.ERROR_MESSAGE, timeout=timeout)
            return await error_element.text_content()
        except:
            return None
    
    async def is_loading(self) -> bool:
        """Check if the page is in loading state."""
        return await self.is_visible(self.LOADING_INDICATOR, timeout=1000)
    
    async def verify_crisis_response(self) -> bool:
        """Verify crisis response is shown."""
        # Crisis response typically includes specific hotline numbers
        content = await self.page.content()
        crisis_indicators = ['988', 'crisis', 'immediate help', 'emergency']
        return any(indicator in content.lower() for indicator in crisis_indicators)