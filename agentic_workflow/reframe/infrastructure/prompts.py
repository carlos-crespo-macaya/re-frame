"""Prompt manager that downloads and caches prompts from Langfuse."""

import os

from langfuse import Langfuse

from reframe.config.settings import get_settings


class PromptManager:
    """Manages prompt downloading and caching from Langfuse."""

    def __init__(self) -> None:
        """Initialize the prompt manager."""
        self.settings = get_settings()
        self._prompts: dict[str, str] = {}
        self._langfuse: Langfuse | None = None
        self._cache_dir = "/tmp/reframe_prompts"
        os.makedirs(self._cache_dir, exist_ok=True)

    def _get_langfuse_client(self) -> Langfuse:
        """Get or create Langfuse client."""
        if not self._langfuse:
            self._langfuse = Langfuse(
                host=self.settings.langfuse_host,
                public_key=self.settings.langfuse_public_key,
                secret_key=self.settings.langfuse_secret_key,
            )
        return self._langfuse

    def _get_cache_path(self, prompt_name: str) -> str:
        """Get the cache file path for a prompt."""
        return os.path.join(self._cache_dir, f"{prompt_name}.txt")

    def download_prompt(self, prompt_name: str) -> str:
        """Download a prompt from Langfuse and cache it."""
        try:
            # Try to load from memory cache first
            if prompt_name in self._prompts:
                return self._prompts[prompt_name]

            # Try to load from file cache
            cache_path = self._get_cache_path(prompt_name)
            if os.path.exists(cache_path):
                with open(cache_path, encoding="utf-8") as f:
                    prompt = f.read()
                    self._prompts[prompt_name] = prompt
                    return prompt

            # Download from Langfuse
            langfuse = self._get_langfuse_client()
            prompt_obj = langfuse.get_prompt(prompt_name)
            prompt = str(prompt_obj.compile())

            # Cache in memory and file
            self._prompts[prompt_name] = prompt
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(prompt)

            return prompt

        except Exception as e:
            raise RuntimeError(f"Failed to download prompt '{prompt_name}': {e!s}") from e

    def download_all_prompts(self) -> dict[str, str]:
        """Download all required prompts and cache them."""
        required_prompts = [
            "intake-agent-adk-instructions",
            "reframe-agent-adk-instructions",
            "synthesis-agent-adk-instructions",
        ]

        for prompt_name in required_prompts:
            self.download_prompt(prompt_name)

        return self._prompts

    def get_prompt(self, prompt_name: str) -> str:
        """Get a prompt, downloading if necessary."""
        if prompt_name not in self._prompts:
            return self.download_prompt(prompt_name)
        return self._prompts[prompt_name]

    def clear_cache(self) -> None:
        """Clear all cached prompts."""
        self._prompts.clear()
        # Optionally remove cache files
        for file in os.listdir(self._cache_dir):
            if file.endswith(".txt"):
                os.remove(os.path.join(self._cache_dir, file))


# Global prompt manager instance
prompt_manager = PromptManager()
