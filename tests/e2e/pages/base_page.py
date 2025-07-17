"""
Base Page Object class for all pages.
"""
from typing import Optional
from playwright.async_api import Page, Locator, expect


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://localhost:3000"
        self.api_url = "http://localhost:8000"
    
    async def navigate(self, path: str = "") -> None:
        """Navigate to a specific path."""
        url = f"{self.base_url}{path}"
        await self.page.goto(url)
        await self.page.wait_for_load_state('domcontentloaded')
    
    async def wait_for_element(self, selector: str, timeout: int = 30000) -> Locator:
        """Wait for an element to be visible."""
        locator = self.page.locator(selector)
        await locator.wait_for(state='visible', timeout=timeout)
        return locator
    
    async def click_and_wait(self, selector: str, wait_for: Optional[str] = None) -> None:
        """Click an element and optionally wait for another element."""
        await self.page.click(selector)
        if wait_for:
            await self.wait_for_element(wait_for)
    
    async def fill_input(self, selector: str, text: str) -> None:
        """Fill an input field."""
        await self.page.fill(selector, text)
    
    async def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        return await self.page.text_content(selector) or ""
    
    async def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is visible."""
        try:
            await self.page.wait_for_selector(selector, state='visible', timeout=timeout)
            return True
        except:
            return False
    
    async def wait_for_api_response(self, url_pattern: str, timeout: int = 30000):
        """Wait for a specific API response."""
        async with self.page.expect_response(
            lambda response: url_pattern in response.url,
            timeout=timeout
        ) as response_info:
            return await response_info.value
    
    async def wait_for_sse_connection(self, session_id: str) -> None:
        """Wait for SSE connection to be established."""
        # Wait for EventSource to be created
        await self.page.wait_for_function(
            """
            () => {
                return window.eventSource !== undefined;
            }
            """,
            timeout=10000
        )
        
        # Wait for connected event
        await self.page.wait_for_function(
            """
            () => {
                const messages = window.sseMessages || [];
                return messages.some(msg => msg.type === 'connected');
            }
            """,
            timeout=10000
        )
    
    async def setup_sse_listener(self, session_id: str) -> None:
        """Set up SSE event listener in the browser."""
        await self.page.evaluate("""
            (sessionId) => {
                window.sseMessages = [];
                window.sseErrors = [];
                
                const eventSource = new EventSource(`/api/events/${sessionId}`);
                
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        window.sseMessages.push(data);
                        console.log('SSE message:', data);
                    } catch (e) {
                        console.error('Failed to parse SSE message:', e);
                    }
                };
                
                eventSource.onerror = (error) => {
                    window.sseErrors.push(error);
                    console.error('SSE error:', error);
                };
                
                window.eventSource = eventSource;
            }
        """, session_id)
    
    async def get_sse_messages(self) -> list:
        """Get all SSE messages received."""
        return await self.page.evaluate("() => window.sseMessages || []")
    
    async def wait_for_sse_message(self, message_type: str, timeout: int = 30000) -> dict:
        """Wait for a specific SSE message type."""
        message = await self.page.wait_for_function(
            """
            (messageType) => {
                const messages = window.sseMessages || [];
                return messages.find(msg => msg.type === messageType || msg.message_type === messageType);
            }
            """,
            message_type,
            timeout=timeout
        )
        return await message.json_value()
    
    async def check_console_errors(self) -> list:
        """Check for console errors."""
        return await self.page.evaluate("""
            () => {
                const errors = [];
                const originalError = console.error;
                console.error = function(...args) {
                    errors.push(args.join(' '));
                    originalError.apply(console, args);
                };
                return errors;
            }
        """)
    
    async def take_screenshot(self, name: str) -> None:
        """Take a screenshot for debugging."""
        await self.page.screenshot(path=f"screenshots/{name}.png", full_page=True)