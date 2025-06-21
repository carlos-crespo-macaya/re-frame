"""
Google AI Studio (Gemini) configuration and initialization
"""
import google.generativeai as genai
from typing import Optional
import logging

from .settings import settings

logger = logging.getLogger(__name__)


class GeminiConfig:
    """
    Configuration and initialization for Google AI Studio's Gemini models
    """
    
    def __init__(self):
        self.model: Optional[genai.GenerativeModel] = None
        self.generation_config: Optional[genai.GenerationConfig] = None
        self._initialized = False
    
    def initialize(self):
        """
        Initialize Gemini with API key and configuration
        """
        if self._initialized:
            logger.debug("Gemini already initialized")
            return
        
        try:
            # Configure API key
            genai.configure(api_key=settings.google_ai_api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(settings.gemini_model)
            
            # Create generation config
            self.generation_config = genai.GenerationConfig(
                temperature=settings.temperature,
                max_output_tokens=settings.max_output_tokens,
                candidate_count=1,
            )
            
            self._initialized = True
            logger.info(f"Gemini initialized successfully with model: {settings.gemini_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise
    
    def get_model(self) -> genai.GenerativeModel:
        """
        Get the initialized Gemini model
        """
        if not self._initialized:
            self.initialize()
        return self.model
    
    def get_generation_config(self) -> genai.GenerationConfig:
        """
        Get the generation configuration
        """
        if not self._initialized:
            self.initialize()
        return self.generation_config
    
    async def test_connection(self) -> bool:
        """
        Test the connection to Google AI Studio
        """
        try:
            model = self.get_model()
            response = await model.generate_content_async(
                "Say 'OK' if you can hear me.",
                generation_config=self.get_generation_config()
            )
            return "OK" in response.text.upper()
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False


# Global Gemini configuration instance
gemini_config = GeminiConfig()