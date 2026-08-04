import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Config:
    """Centralized Application Configuration Manager."""

    APP_NAME: str = "AI Startup Idea Validator"
    APP_VERSION: str = "2.0.0-SaaS"

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Search Configuration
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"

    # Storage & Reports
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "outputs/reports")
    PROMPTS_DIR: str = os.getenv("PROMPTS_DIR", "prompts")

    @classmethod
    def is_gemini_available(cls) -> bool:
        return bool(cls.GEMINI_API_KEY.strip())

    @classmethod
    def is_tavily_available(cls) -> bool:
        return bool(cls.TAVILY_API_KEY.strip())

    @classmethod
    def ensure_directories(cls) -> None:
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)


config = Config()
config.ensure_directories()
