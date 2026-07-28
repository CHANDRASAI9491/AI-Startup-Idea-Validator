import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "outputs/reports")

    @classmethod
    def is_gemini_available(cls) -> bool:
        return bool(cls.GEMINI_API_KEY.strip())


config = Config()
