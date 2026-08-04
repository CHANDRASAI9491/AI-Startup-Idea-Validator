import logging
from typing import Optional, Dict, Any
from app.config import config
from tools.retrieval_utils import extract_json_from_text
from services.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service layer for managing Google Gemini Flash model interactions with robust fallback."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.DEFAULT_MODEL
        self.api_key = config.GEMINI_API_KEY
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"LLMService initialized successfully with model '{self.model_name}'.")
            except Exception as e:
                logger.warning(f"Failed to initialize google.genai Client: {e}")
                self._client = None
        else:
            logger.info("No GEMINI_API_KEY configured. Operating in heuristic fallback mode.")

    def is_available(self) -> bool:
        return self._client is not None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """Generate text using Google Gemini API."""
        if not self._client:
            logger.debug("LLM Client unavailable. Skipping API call.")
            return None

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            logger.error(f"Error invoking Gemini model ({self.model_name}): {e}")
            return None

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate text and cleanly parse JSON result."""
        json_instruction = (system_instruction or "") + "\nRespond strictly with valid JSON. Do not include markdown formatting outer wrappers other than standard JSON."
        text_response = self.generate_text(prompt, system_instruction=json_instruction)
        if text_response:
            parsed = extract_json_from_text(text_response)
            if parsed:
                return parsed
            logger.warning("Failed to extract valid JSON from LLM text response.")
        return None
