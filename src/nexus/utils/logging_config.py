"""Logging configuration for NEXUS Smart Resource Monitor."""
import logging
from pathlib import Path
from src.nexus.config import LOGS_DIR

def setup_logger(name: str = "nexus", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a structured logger writing to console and local log file."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(level)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (safe creation of logs directory)
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOGS_DIR / "nexus.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as exc:
        logger.warning(f"Unable to initialize file logger in {LOGS_DIR}: {exc}")

    return logger
