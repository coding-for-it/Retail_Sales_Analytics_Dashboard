"""
logger.py
---------
Centralized logging configuration for the Retail Sales Analytics ETL pipeline.

Provides both file and console logging:
  - File handler   → logs/etl_YYYYMMDD_HHMMSS.log  (DEBUG level)
  - Console handler → terminal output               (INFO level)

The get_logger() function is idempotent — handlers are added only once,
preventing duplicate log lines when the function is called from multiple modules.

Original API preserved: get_logger() returns a Logger instance.
"""

import logging
import os
from datetime import datetime

from src.config import LOGS_DIR


def get_logger(name: str = "retail_etl") -> logging.Logger:
    """
    Configure and return the pipeline logger.

    Args:
        name: Logger name (default: 'retail_etl')

    Returns:
        logging.Logger: Configured logger with file + console handlers
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers on repeated calls (e.g. during testing)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist yet
    os.makedirs(LOGS_DIR, exist_ok=True)

    # ── File Handler ──────────────────────────────────────────────────────────
    # One timestamped log file per pipeline run
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file   = os.path.join(LOGS_DIR, f"etl_{timestamp}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(module)-16s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # ── Console Handler ───────────────────────────────────────────────────────
    # Shows INFO and above in the terminal during pipeline execution
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized → {log_file}")
    return logger