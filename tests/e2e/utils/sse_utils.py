"""
SSE (Server-Sent Events) utilities for E2E tests.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from playwright.async_api import Page


class SSETestClient:
    """Helper for testing SSE connections in Playwright."""
    
    def __init__(self, page: Page):
        self.page = page
        self.messages: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self._setup_complete = False
    
    async def setup(self, session_id: str, api_url: str = "/api/events") -> None:
        """
        Set up SSE event listening in the browser.
        
        This injects JavaScript to create an EventSource and track messages.
        """
        await self.page.evaluate("""
            ({ sessionId, apiUrl }) => {
                // Clear any existing data
                window.sseMessages = [];
                window.sseErrors = [];
                window.sseConnectionState = 'connecting';
                
                // Close any existing connection
                if (window.eventSource) {
                    window.eventSource.close();
                }
                
                // Create new EventSource
                const url = `${apiUrl}/${sessionId}`;
                const eventSource = new EventSource(url);
                
                eventSource.onopen = () => {
                    window.sseConnectionState = 'connected';
                    console.log('SSE connected');
                };
                
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        window.sseMessages.push({
                            ...data,
                            timestamp: new Date().toISOString(),
                            rawData: event.data
                        });
                        console.log('SSE message:', data);
                    } catch (e) {
                        console.error('Failed to parse SSE message:', e, event.data);
                        window.sseErrors.push(`Parse error: ${e.message}`);
                    }
                };
                
                eventSource.onerror = (error) => {
                    window.sseConnectionState = 'error';
                    window.sseErrors.push(`Connection error at ${new Date().toISOString()}`);
                    console.error('SSE error:', error);
                };
                
                window.eventSource = eventSource;
            }
        """, {"sessionId": session_id, "apiUrl": api_url})
        
        self._setup_complete = True
    
    async def wait_for_connection(self, timeout: int = 10000) -> bool:
        """Wait for SSE connection to be established."""
        if not self._setup_complete:
            raise RuntimeError("SSE client not set up. Call setup() first.")
        
        try:
            await self.page.wait_for_function(
                "() => window.sseConnectionState === 'connected'",
                timeout=timeout
            )
            
            # Also wait for the connected message
            await self.wait_for_message(
                lambda msg: msg.get("type") == "connected",
                timeout=timeout
            )
            return True
        except Exception as e:
            print(f"Connection timeout: {e}")
            return False
    
    async def wait_for_message(
        self, 
        predicate: Callable[[Dict[str, Any]], bool],
        timeout: int = 30000
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a message matching the predicate.
        
        Args:
            predicate: Function that returns True for the desired message
            timeout: Maximum time to wait in milliseconds
        """
        try:
            result = await self.page.wait_for_function(
                """
                (predicateStr) => {
                    const predicate = new Function('msg', predicateStr);
                    const messages = window.sseMessages || [];
                    return messages.find(msg => predicate(msg));
                }
                """,
                # Convert predicate to string for evaluation
                f"return ({predicate.__code__.co_code})",
                timeout=timeout
            )
            return await result.json_value()
        except Exception:
            # Fallback to simpler approach
            return await self._wait_for_message_simple(predicate, timeout)
    
    async def _wait_for_message_simple(
        self,
        predicate: Callable[[Dict[str, Any]], bool],
        timeout: int
    ) -> Optional[Dict[str, Any]]:
        """Simple polling-based message wait."""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout / 1000:
            messages = await self.get_messages()
            for msg in messages:
                if predicate(msg):
                    return msg
            await asyncio.sleep(0.1)
        
        return None
    
    async def wait_for_text_message(self, timeout: int = 30000) -> Optional[str]:
        """Wait for a text message and return its content."""
        message = await self.wait_for_message(
            lambda msg: msg.get("mime_type") == "text/plain" and msg.get("data"),
            timeout=timeout
        )
        return message.get("data") if message else None
    
    async def wait_for_turn_complete(self, timeout: int = 30000) -> bool:
        """Wait for turn_complete signal."""
        message = await self.wait_for_message(
            lambda msg: msg.get("turn_complete") is True,
            timeout=timeout
        )
        return message is not None
    
    async def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages received so far."""
        return await self.page.evaluate("() => window.sseMessages || []")
    
    async def get_errors(self) -> List[str]:
        """Get all errors encountered."""
        return await self.page.evaluate("() => window.sseErrors || []")
    
    async def get_connection_state(self) -> str:
        """Get current connection state."""
        return await self.page.evaluate("() => window.sseConnectionState || 'unknown'")
    
    async def close(self) -> None:
        """Close the SSE connection."""
        await self.page.evaluate("""
            () => {
                if (window.eventSource) {
                    window.eventSource.close();
                    window.sseConnectionState = 'closed';
                }
            }
        """)
    
    async def get_full_response(self, timeout: int = 30000) -> str:
        """
        Wait for a complete response and return the full text.
        
        This waits for turn_complete and concatenates all text messages.
        """
        # Wait for turn complete
        if not await self.wait_for_turn_complete(timeout):
            raise TimeoutError("Response did not complete in time")
        
        # Get all messages
        messages = await self.get_messages()
        
        # Filter and concatenate text messages
        text_parts = []
        for msg in messages:
            if msg.get("mime_type") == "text/plain" and msg.get("data"):
                text_parts.append(msg["data"])
        
        return "".join(text_parts)