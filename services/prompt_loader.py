import os
import logging
from typing import Dict, Any, Optional
from app.config import config
from services.logger import get_logger

logger = get_logger(__name__)


class PromptLoader:
    """Dynamic Prompt Loader Service for loading prompt templates from markdown files without hardcoding."""

    _cache: Dict[str, str] = {}

    @classmethod
    def load_prompt(cls, prompt_name: str, **kwargs: Any) -> str:
        """
        Loads a prompt template from prompts/<prompt_name>.md and replaces {placeholder} tags safely
        without breaking JSON single curly braces.
        """
        filename = f"{prompt_name}.md" if not prompt_name.endswith(".md") else prompt_name
        filepath = os.path.join(config.PROMPTS_DIR, filename)

        if filename not in cls._cache:
            if not os.path.exists(filepath):
                logger.warning(f"Prompt file not found at '{filepath}'. Returning empty prompt.")
                return ""
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    cls._cache[filename] = f.read().strip()
            except Exception as e:
                logger.error(f"Error reading prompt file '{filepath}': {e}")
                return ""

        prompt_text = cls._cache[filename]

        # Safely replace only explicit kwargs keys without invoking str.format() on raw JSON braces
        for key, val in kwargs.items():
            placeholder = f"{{{key}}}"
            prompt_text = prompt_text.replace(placeholder, str(val if val is not None else ""))

        return prompt_text
