"""
Logging utilities
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..core.config import settings


def setup_logging(log_dir: Optional[Path] = None) -> logging.Logger:
    """
    Set up application logging

    Args:
        log_dir: Directory for log files. If None, logs to stdout only.

    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger("adm_compliance")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log directory specified)
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"adm_compliance_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger
logger = setup_logging()
