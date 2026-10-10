"""
utils.py
--------
Shared utility functions for the Retail Sales Analytics ETL pipeline.

These helpers are used across multiple modules to avoid code duplication.
No business logic lives here — only general-purpose utilities.
"""

import os
import uuid
import time
import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from src.config import CLEANED_DIR, REJECTED_DIR, LOGS_DIR

logger = logging.getLogger("retail_etl")


# ─────────────────────────────────────────────────────────────────────────────
# DIRECTORY SETUP
# ─────────────────────────────────────────────────────────────────────────────

def ensure_directories() -> None:
    """
    Create required output directories if they do not already exist.

    Directories created:
      - cleaned/   → validated and transformed CSV files
      - rejected/  → rows that failed validation
      - logs/      → timestamped ETL log files
    """
    for directory in [CLEANED_DIR, REJECTED_DIR, LOGS_DIR]:
        os.makedirs(directory, exist_ok=True)
    logger.info("Output directories verified: cleaned/, rejected/, logs/")


# ─────────────────────────────────────────────────────────────────────────────
# RUN IDENTIFIER
# ─────────────────────────────────────────────────────────────────────────────

def generate_run_id() -> str:
    """
    Generate a unique run ID for each ETL pipeline execution.

    Returns:
        UUID string (e.g. '3f2504e0-4f89-11d3-9a0c-0305e82c3301')
    """
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# FILE I/O
# ─────────────────────────────────────────────────────────────────────────────

def save_csv(df: pd.DataFrame, path: str, label: str = "") -> None:
    """
    Save a DataFrame to a CSV file and log the operation.

    Args:
        df    : DataFrame to save
        path  : Full destination file path
        label : Human-readable name for logging (e.g. 'customers_clean')
    """
    df.to_csv(path, index=False)
    tag = f" [{label}]" if label else ""
    logger.info(f"[SAVE] {len(df)} rows → {path}{tag}")


# ─────────────────────────────────────────────────────────────────────────────
# TIME HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def elapsed(start_time: float) -> str:
    """
    Return a human-readable elapsed time string.

    Args:
        start_time: Value returned by time.time() at pipeline start

    Returns:
        Formatted string like '3.45 seconds' or '1 min 07 sec'
    """
    seconds = time.time() - start_time
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    minutes = int(seconds // 60)
    secs    = int(seconds % 60)
    return f"{minutes} min {secs:02d} sec"


# ─────────────────────────────────────────────────────────────────────────────
# CONSOLE DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

def print_separator(title: str = "") -> None:
    """
    Print a formatted section separator to the terminal.

    Args:
        title: Optional section title displayed inside the separator
    """
    line = "=" * 62
    if title:
        print(f"\n{line}")
        print(f"  {title}")
        print(f"{line}")
    else:
        print(line)


# ─────────────────────────────────────────────────────────────────────────────
# ETL SUMMARY REPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_etl_summary(
    run_id: str,
    start_time: float,
    stats: dict,
    status: str,
    error_message: Optional[str] = None,
) -> str:
    """
    Build a formatted ETL summary report string.

    Args:
        run_id        : Unique run identifier (UUID)
        start_time    : Pipeline start time from time.time()
        stats         : Dict mapping entity → {read, loaded, rejected}
        status        : 'SUCCESS' or 'FAILED'
        error_message : Optional error description

    Returns:
        Multi-line formatted string for console and log output

    Example stats dict:
        {
          'customers': {'read': 500, 'loaded': 480, 'rejected': 20},
          'products' : {'read': 100, 'loaded':  97, 'rejected':  3},
          'orders'   : {'read': 5000,'loaded': 4870,'rejected': 130},
        }
    """
    duration = elapsed(start_time)
    now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_read     = sum(s.get("read",     0) for s in stats.values())
    total_loaded   = sum(s.get("loaded",   0) for s in stats.values())
    total_rejected = sum(s.get("rejected", 0) for s in stats.values())

    lines = [
        "",
        "=" * 62,
        "  RETAIL SALES ANALYTICS - ETL PIPELINE SUMMARY",
        "=" * 62,
        f"  Run ID        : {run_id}",
        f"  Completed At  : {now}",
        f"  Duration      : {duration}",
        f"  Status        : {status}",
        "-" * 62,
        f"  {'ENTITY':<14} {'READ':>7}  {'LOADED':>7}  {'REJECTED':>9}",
        "-" * 62,
    ]

    for entity, counts in stats.items():
        lines.append(
            f"  {entity.upper():<14} "
            f"{counts.get('read',     0):>7}  "
            f"{counts.get('loaded',   0):>7}  "
            f"{counts.get('rejected', 0):>9}"
        )

    lines += [
        "-" * 62,
        f"  {'TOTAL':<14} {total_read:>7}  {total_loaded:>7}  {total_rejected:>9}",
        "=" * 62,
    ]

    if error_message:
        lines.append(f"\n  ERROR : {error_message}")
        lines.append("=" * 62)

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# TITLE CASING & BRAND / ACRONYM PRESERVATION
# ─────────────────────────────────────────────────────────────────────────────

SPECIAL_CASING: dict = {
    "boat": "boAt",
    "iphone": "iPhone",
    "ipad": "iPad",
    "airpods": "AirPods",
    "airdopes": "Airdopes",
    "oneplus": "OnePlus",
    "realme": "Realme",
    "h&m": "H&M",
    "hp": "HP",
    "lg": "LG",
    "tv": "TV",
    "oled": "OLED",
    "lcd": "LCD",
    "led": "LED",
    "usb": "USB",
    "gps": "GPS",
    "wifi": "WiFi",
    "4k": "4K",
    "5g": "5G",
    "xxl": "XXL",
    "gb": "GB",
    "tb": "TB",
    "mb": "MB",
    "jbl": "JBL",
    "dsc": "DSC",
    "upi": "UPI",
    "fhd": "FHD",
    "qhd": "QHD",
    "uhd": "UHD",
    "8k": "8K",
    "ac1200": "AC1200",
    "l'oreal": "L'Oreal",
    "levi's": "Levi's",
}


def smart_title(text: object) -> object:
    """
    Title-case text while preserving brand names and acronyms.

    - Preserves known brand casing (e.g. 'boAt', 'iPhone', 'H&M', 'L'Oreal', "Levi's")
    - Preserves acronyms (e.g. 'HP', 'LG', 'TV', 'OLED', 'USB', '4K', '5G')
    - Title-cases standard words (e.g. 'samsung galaxy' -> 'Samsung Galaxy')
    """
    if pd.isna(text) or text is None:
        return text
    s = str(text).strip()
    if not s:
        return s

    words = s.split()
    transformed_words = []
    for w in words:
        w_lower = w.lower()
        if w_lower in SPECIAL_CASING:
            transformed_words.append(SPECIAL_CASING[w_lower])
        elif w.isupper() and len(w) >= 2:
            transformed_words.append(w)
        elif any(c.isupper() for c in w[1:]):
            transformed_words.append(w)
        else:
            transformed_words.append(w.capitalize())

    return " ".join(transformed_words)

