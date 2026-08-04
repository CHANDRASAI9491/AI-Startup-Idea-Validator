import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Application
    APP_NAME = "AI Startup Idea Validator"
    APP_VERSION = "1.0.0"

    # API Keys
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    # Model
    DEFAULT_MODEL = os.getenv("MODEL_NAME", "gemini-2.5-flash")

    # Search
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

    # Directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    EXPORT_DIR = os.getenv("EXPORT_DIR", REPORTS_DIR)

    @classmethod
    def is_gemini_available(cls):
        return bool(cls.GEMINI_API_KEY)

    @classmethod
    def is_tavily_available(cls):
        return bool(cls.TAVILY_API_KEY)


config = Config()