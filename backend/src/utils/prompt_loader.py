"""Utility for loading language-specific prompts."""

from pathlib import Path


class PromptLoader:
    """Loads prompts in the appropriate language."""

    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
    DEFAULT_LANGUAGE = "en"

    @classmethod
    def load_prompt(cls, prompt_name: str, language: str = "en") -> str:
        """
        Load a prompt file in the specified language.

        Args:
            prompt_name: Name of the prompt (without extension)
            language: Language code (e.g., 'en', 'es')

        Returns:
            The prompt content

        Raises:
            FileNotFoundError: If prompt file not found
        """
        # Try language-specific version first
        if language != cls.DEFAULT_LANGUAGE:
            localized_path = cls.PROMPTS_DIR / f"{prompt_name}_{language}.md"
            if localized_path.exists():
                return localized_path.read_text(encoding="utf-8")

        # Fall back to default language
        default_path = cls.PROMPTS_DIR / f"{prompt_name}.md"
        if default_path.exists():
            return default_path.read_text(encoding="utf-8")

        raise FileNotFoundError(
            f"Prompt '{prompt_name}' not found for language '{language}' or default"
        )

    @classmethod
    def get_available_languages(cls, prompt_name: str) -> list[str]:
        """
        Get list of available languages for a prompt.

        Args:
            prompt_name: Name of the prompt

        Returns:
            List of available language codes
        """
        languages = []

        # Check for default version
        if (cls.PROMPTS_DIR / f"{prompt_name}.md").exists():
            languages.append(cls.DEFAULT_LANGUAGE)

        # Check for localized versions
        for file in cls.PROMPTS_DIR.glob(f"{prompt_name}_*.md"):
            # Extract language code from filename
            language = file.stem.split("_")[-1]
            if language and len(language) == 2:
                languages.append(language)

        return sorted(set(languages))
