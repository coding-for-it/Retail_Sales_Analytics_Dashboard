"""
validate.py
-----------
Data validation layer for the Retail Sales Analytics ETL pipeline.

Each validate_*() function:
  1. Receives a raw DataFrame (all string columns)
  2. Applies multiple validation rules
  3. Tags each invalid row with a REJECT_REASON (multiple reasons separated by '; ')
  4. Returns a (clean_df, rejected_df) tuple

Validation Summary:
  Customers → 8  rules
  Products  → 6  rules
  Orders    → 10 rules
  Total     → 24 validation checks across the pipeline

Design Decisions:
  - A row is rejected if it fails ANY rule
  - A row can fail MULTIPLE rules (all reasons are captured)
  - The clean_df returned has no REJECT_REASON column
  - The rejected_df retains REJECT_REASON for audit and reporting
"""

import re
import logging
from datetime import date

import pandas as pd

from src.config import (
    EMAIL_REGEX,
    PHONE_REGEX,
    VALID_CATEGORIES,
    VALID_ORDER_STATUSES,
    VALID_PAYMENT_METHODS,
    VALID_REGIONS,
    MAX_DISCOUNT_PCT,
    MIN_PRICE,
)

logger = logging.getLogger("retail_etl")

# Capture today's date once at module load — used for future-date validation
_TODAY = date.today()


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _tag_rejected(df: pd.DataFrame, mask: pd.Series, reason: str) -> None:
    """
    Append a rejection reason to rows where mask is True.

    Multiple rejection reasons are separated by '; ' so every failure
    for a row is visible in the REJECT_REASON column.

    Args:
        df    : DataFrame being validated (modified in-place)
        mask  : Boolean Series — True where the rule is violated
        reason: Human-readable description of the validation failure
    """
    if "REJECT_REASON" not in df.columns:
        df["REJECT_REASON"] = ""

    existing = df.loc[mask, "REJECT_REASON"]
    df.loc[mask, "REJECT_REASON"] = existing.apply(
        lambda x: f"{x}; {reason}" if x else reason
    )


def _split_clean_rejected(
    df: pd.DataFrame,
) -> tuple:
    """
    Split a tagged DataFrame into clean and rejected subsets.

    Args:
        df: DataFrame with a REJECT_REASON column

    Returns:
        (clean_df, rejected_df)
          clean_df    → rows where REJECT_REASON is empty, column removed
          rejected_df → rows where REJECT_REASON is not empty, column kept
    """
    rejected_mask = df["REJECT_REASON"].notna() & (df["REJECT_REASON"] != "")
    rejected = df[rejected_mask].copy()
    clean    = df[~rejected_mask].copy()
    clean.drop(columns=["REJECT_REASON"], inplace=True, errors="ignore")
    return clean, rejected


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMERS — 8 VALIDATION RULES
# ─────────────────────────────────────────────────────────────────────────────

def validate_customers(df: pd.DataFrame) -> tuple:
    """
    Apply 8 validation rules to the raw customers DataFrame.

    Rules:
      1. Blank row         — all fields are null
      2. Missing ID        — Customer_ID is null or empty
      3. Duplicate ID      — same Customer_ID appears more than once (keep first)
      4. Missing Name      — Customer_Name is null or empty
      5. Invalid Email     — does not match standard email regex
      6. Invalid Phone     — not exactly 10 digits
      7. Invalid Region    — not in {North, South, East, West}
      8. Missing City      — City is null or empty

    Args:
        df: Raw customers DataFrame (all string columns)

    Returns:
        (clean_df, rejected_df): Tuple of DataFrames
    """
    logger.info("[VALIDATE] Starting customers validation...")
    df = df.copy()
    df["REJECT_REASON"] = ""

    # Rule 1: Blank rows — drop columns we just added before checking
    core_cols = [c for c in df.columns if c != "REJECT_REASON"]
    blank_mask = df[core_cols].isnull().all(axis=1)
    _tag_rejected(df, blank_mask, "Blank row")

    not_blank = ~blank_mask

    # Rule 2: Missing Customer_ID
    null_id = df["Customer_ID"].isnull()
    _tag_rejected(df, null_id & not_blank, "Missing Customer_ID")

    # Rule 3: Duplicate Customer_ID (keep first occurrence)
    dup_id = df.duplicated(subset=["Customer_ID"], keep="first")
    _tag_rejected(df, dup_id, "Duplicate Customer_ID")

    # Rule 4: Missing Customer_Name
    null_name = df["Customer_Name"].isnull()
    _tag_rejected(df, null_name & not_blank, "Missing Customer_Name")

    # Rule 5: Invalid Email
    def _bad_email(val: object) -> bool:
        if val is None or str(val).strip() == "":
            return True
        return not bool(re.match(EMAIL_REGEX, str(val).strip(), re.IGNORECASE))

    _tag_rejected(df, df["Email"].apply(_bad_email), "Invalid Email")

    # Rule 6: Invalid Phone (must be exactly 10 digits)
    def _bad_phone(val: object) -> bool:
        if val is None or str(val).strip() == "":
            return True
        return not bool(re.match(PHONE_REGEX, str(val).strip()))

    _tag_rejected(df, df["Phone"].apply(_bad_phone), "Invalid Phone (must be 10 digits)")

    # Rule 7: Invalid Region
    _tag_rejected(
        df,
        df["Region"].apply(lambda x: x is None or str(x).strip() not in VALID_REGIONS),
        "Invalid Region (must be North/South/East/West)",
    )

    # Rule 8: Missing City
    _tag_rejected(
        df,
        df["City"].isnull() & not_blank,
        "Missing City",
    )

    clean, rejected = _split_clean_rejected(df)
    logger.info(
        f"[VALIDATE] Customers → Clean: {len(clean):,}  |  Rejected: {len(rejected):,}"
    )
    return clean, rejected


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS — 6 VALIDATION RULES
# ─────────────────────────────────────────────────────────────────────────────

def validate_products(df: pd.DataFrame) -> tuple:
    """
    Apply 6 validation rules to the raw products DataFrame.

    Rules:
      1. Blank row         — all fields are null
      2. Missing ID        — Product_ID is null or empty
      3. Duplicate ID      — same Product_ID appears more than once
      4. Missing Name      — Product_Name is null or empty
      5. Invalid Category  — not in the approved category list
      6. Invalid Price     — null, non-numeric, negative, or zero

    Args:
        df: Raw products DataFrame (all string columns)

    Returns:
        (clean_df, rejected_df): Tuple of DataFrames
    """
    logger.info("[VALIDATE] Starting products validation...")
    df = df.copy()
    df["REJECT_REASON"] = ""

    # Rule 1: Blank rows
    core_cols  = [c for c in df.columns if c != "REJECT_REASON"]
    blank_mask = df[core_cols].isnull().all(axis=1)
    _tag_rejected(df, blank_mask, "Blank row")
    not_blank = ~blank_mask

    # Rule 2: Missing Product_ID
    _tag_rejected(df, df["Product_ID"].isnull() & not_blank, "Missing Product_ID")

    # Rule 3: Duplicate Product_ID
    _tag_rejected(
        df,
        df.duplicated(subset=["Product_ID"], keep="first"),
        "Duplicate Product_ID",
    )

    # Rule 4: Missing Product_Name
    _tag_rejected(df, df["Product_Name"].isnull() & not_blank, "Missing Product_Name")

    # Rule 5: Invalid Category
    _tag_rejected(
        df,
        df["Category"].apply(
            lambda x: x is None or str(x).strip() not in VALID_CATEGORIES
        ),
        "Invalid or missing Category",
    )

    # Rule 6: Invalid Price (negative, zero, non-numeric)
    def _bad_price(val: object) -> bool:
        try:
            return float(val) < MIN_PRICE
        except (TypeError, ValueError):
            return True

    _tag_rejected(df, df["Price"].apply(_bad_price) & not_blank, "Negative or zero Price")

    clean, rejected = _split_clean_rejected(df)
    logger.info(
        f"[VALIDATE] Products → Clean: {len(clean):,}  |  Rejected: {len(rejected):,}"
    )
    return clean, rejected


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS — 10 VALIDATION RULES
# ─────────────────────────────────────────────────────────────────────────────

def validate_orders(
    df: pd.DataFrame,
    valid_customer_ids: set,
    valid_product_ids: set,
) -> tuple:
    """
    Apply 10 validation rules to the raw orders DataFrame.

    Rules:
      1.  Blank row              — all fields are null
      2.  Missing Order_ID       — Order_ID is null or empty
      3.  Duplicate Order_ID     — same Order_ID appears more than once
      4.  Missing Customer_ID    — Customer_ID is null or empty
      5.  Invalid Customer_ID    — FK violation (not in clean customers)
      6.  Missing Product_ID     — Product_ID is null or empty
      7.  Invalid Product_ID     — FK violation (not in clean products)
      8.  Invalid Quantity       — null, non-numeric, negative, or zero
      9.  Invalid Unit_Price     — null, non-numeric, or negative
      10. Future/Invalid Date    — Order_Date is in the future or unparseable
      11. Invalid Order_Status   — not in allowed values
      12. Invalid Payment_Method — not in allowed values
      13. Discount out of range  — < 0 or > MAX_DISCOUNT_PCT

    Args:
        df                : Raw orders DataFrame (all string columns)
        valid_customer_ids: Set of Customer_IDs from the clean customers DataFrame
        valid_product_ids : Set of Product_IDs from the clean products DataFrame

    Returns:
        (clean_df, rejected_df): Tuple of DataFrames
    """
    logger.info("[VALIDATE] Starting orders validation...")
    df = df.copy()
    df["REJECT_REASON"] = ""

    # Rule 1: Blank rows
    core_cols  = [c for c in df.columns if c != "REJECT_REASON"]
    blank_mask = df[core_cols].isnull().all(axis=1)
    _tag_rejected(df, blank_mask, "Blank row")
    not_blank = ~blank_mask

    # Rule 2: Missing Order_ID
    _tag_rejected(df, df["Order_ID"].isnull() & not_blank, "Missing Order_ID")

    # Rule 3: Duplicate Order_ID
    _tag_rejected(
        df,
        df.duplicated(subset=["Order_ID"], keep="first"),
        "Duplicate Order_ID",
    )

    # Rule 4: Missing Customer_ID
    null_cid = df["Customer_ID"].isnull()
    _tag_rejected(df, null_cid & not_blank, "Missing Customer_ID")

    # Rule 5: Invalid Customer_ID (FK check)
    def _invalid_customer(val: object) -> bool:
        if val is None:
            return False   # already caught by Rule 4
        return str(val).strip().upper() not in valid_customer_ids

    _tag_rejected(
        df,
        df["Customer_ID"].apply(_invalid_customer) & ~null_cid,
        "Invalid Customer_ID (FK violation)",
    )

    # Rule 6: Missing Product_ID
    null_pid = df["Product_ID"].isnull()
    _tag_rejected(df, null_pid & not_blank, "Missing Product_ID")

    # Rule 7: Invalid Product_ID (FK check)
    def _invalid_product(val: object) -> bool:
        if val is None:
            return False   # already caught by Rule 6
        return str(val).strip().upper() not in valid_product_ids

    _tag_rejected(
        df,
        df["Product_ID"].apply(_invalid_product) & ~null_pid,
        "Invalid Product_ID (FK violation)",
    )

    # Rule 8: Invalid Quantity (null, non-numeric, <= 0)
    def _bad_qty(val: object) -> bool:
        try:
            return int(float(val)) <= 0
        except (TypeError, ValueError):
            return True

    _tag_rejected(df, df["Quantity"].apply(_bad_qty) & not_blank, "Negative or zero Quantity")

    # Rule 9: Invalid Unit_Price (null, non-numeric, or negative)
    def _bad_price(val: object) -> bool:
        try:
            return float(val) < 0
        except (TypeError, ValueError):
            return True

    _tag_rejected(df, df["Unit_Price"].apply(_bad_price) & not_blank, "Negative Unit_Price")

    # Rule 10: Future or unparseable Order_Date
    def _bad_date(val: object) -> bool:
        if val is None or str(val).strip() == "":
            return True
        try:
            return pd.to_datetime(val).date() > _TODAY
        except Exception:
            return True

    _tag_rejected(df, df["Order_Date"].apply(_bad_date) & not_blank, "Future or invalid Order_Date")

    # Rule 11: Invalid Order_Status
    _tag_rejected(
        df,
        df["Order_Status"].apply(
            lambda x: x is None or str(x).strip() not in VALID_ORDER_STATUSES
        ),
        "Invalid Order_Status",
    )

    # Rule 12: Invalid Payment_Method
    _tag_rejected(
        df,
        df["Payment_Method"].apply(
            lambda x: x is None or str(x).strip() not in VALID_PAYMENT_METHODS
        ),
        "Invalid Payment_Method",
    )

    # Rule 13: Discount out of range
    def _bad_discount(val: object) -> bool:
        if val is None:
            return False   # null discount treated as 0 in transform
        try:
            d = float(val)
            return d < 0 or d > MAX_DISCOUNT_PCT
        except (TypeError, ValueError):
            return False

    _tag_rejected(
        df,
        df["Discount"].apply(_bad_discount) & not_blank,
        f"Discount out of range (allowed 0–{MAX_DISCOUNT_PCT}%)",
    )

    clean, rejected = _split_clean_rejected(df)
    logger.info(
        f"[VALIDATE] Orders → Clean: {len(clean):,}  |  Rejected: {len(rejected):,}"
    )
    return clean, rejected
