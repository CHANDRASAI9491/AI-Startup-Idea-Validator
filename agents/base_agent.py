import logging
from typing import Optional, Dict, Any
from app.config import config
from tools.retrieval_utils import extract_json_from_text

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class providing unified LLM invocation using google.genai with fallback handling."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.DEFAULT_MODEL
        self.api_key = config.GEMINI_API_KEY
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google.genai Client: {e}")
                self._client = None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        if not self._client:
            return None

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            return response.text if response else None
        except Exception as e:
            logger.error(f"Error invoking Gemini model ({self.model_name}): {e}")
            return None

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        text_response = self.generate_text(prompt, system_instruction)
        if text_response:
            return extract_json_from_text(text_response)
        return None
