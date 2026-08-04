import logging
import sys
from typing import Optional


class AppLogger:
    """Centralized Structured Logging Service."""

    _initialized: bool = False

    @classmethod
    def setup_logger(cls, level: int = logging.INFO) -> None:
        if cls._initialized:
            return

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Avoid duplicate handlers
        if not root_logger.handlers:
            root_logger.addHandler(console_handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        cls.setup_logger()
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    return AppLogger.get_logger(name)
