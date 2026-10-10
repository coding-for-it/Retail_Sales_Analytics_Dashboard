"""
transform.py
------------
Transformation layer for the Retail Sales Analytics ETL pipeline.

Each transform_*() function:
  1. Receives a validated (clean) DataFrame
  2. Strips whitespace, standardizes text, and casts types
  3. Applies business-level feature engineering
  4. Returns a transformed DataFrame ready for loading into Snowflake

Original transform logic is preserved and extended.
"""

import logging

import pandas as pd

from src.config import STATE_MAP
from src.utils import smart_title

logger = logging.getLogger("retail_etl")


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────

def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply transformations to the validated customers DataFrame.

    Operations:
      - Strip leading/trailing whitespace from all string columns
      - Upper-case Customer_ID for consistency
      - Smart title-case Customer_Name (preserving acronyms/brands)
      - Expand State abbreviations to full names (e.g. 'MH' → 'Maharashtra')
      - Smart title-case State if not found in the abbreviation map
      - Parse Join_Date from string to date object (invalid dates → None)
      - Smart title-case City

    Args:
        df: Validated customers DataFrame (all string columns)

    Returns:
        pd.DataFrame: Transformed and type-cast customers DataFrame
    """
    logger.info("[TRANSFORM] Transforming customers...")
    df = df.copy()

    # Strip all string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Standardize Customer_ID
    df["Customer_ID"] = df["Customer_ID"].str.upper()

    # Title-case name with brand/acronym preservation
    df["Customer_Name"] = df["Customer_Name"].apply(smart_title)

    # City title-case
    df["City"] = df["City"].apply(smart_title)

    # Expand state abbreviations → full name
    df["State"] = df["State"].apply(
        lambda x: STATE_MAP.get(str(x).upper().strip(), smart_title(x))
        if pd.notna(x) else x
    )

    # Parse Join_Date to date
    df["Join_Date"] = pd.to_datetime(df["Join_Date"], errors="coerce").dt.date

    logger.info(f"[TRANSFORM] Customers transformed: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────────────────────────────────────────

def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply transformations to the validated products DataFrame.

    Operations:
      - Strip whitespace from all string columns
      - Upper-case Product_ID for consistency
      - Smart title-case Product_Name and Brand (preserving acronyms & brands)
      - Strip Category (keep exact casing from config)
      - Cast Price to float, round to 2 decimal places

    Args:
        df: Validated products DataFrame (all string columns)

    Returns:
        pd.DataFrame: Transformed and type-cast products DataFrame
    """
    logger.info("[TRANSFORM] Transforming products...")
    df = df.copy()

    # Strip all string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Standardize IDs
    df["Product_ID"] = df["Product_ID"].str.upper()

    # Smart title-case names (preserving acronyms & brands)
    df["Product_Name"] = df["Product_Name"].apply(smart_title)
    df["Brand"]        = df["Brand"].apply(smart_title)

    # Category strip (exact values already validated)
    df["Category"] = df["Category"].str.strip()

    # Cast Price to float
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").round(2)

    logger.info(f"[TRANSFORM] Products transformed: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────────────────────────────────

def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply transformations to the validated orders DataFrame.

    Operations:
      - Strip whitespace from all string columns
      - Upper-case Order_ID, Customer_ID, Product_ID
      - Parse Order_Date from string to date object
      - Cast Quantity to int
      - Cast Unit_Price to float, round to 2 dp
      - Fill null Discount with 0.0, cast to float, round to 2 dp
      - Compute Total_Amount = ROUND(Quantity × Unit_Price × (1 − Discount/100), 2)

    Formula:
      Total_Amount = Quantity * Unit_Price * (1 - Discount / 100)

    Args:
        df: Validated orders DataFrame (all string columns)

    Returns:
        pd.DataFrame: Transformed orders DataFrame with Total_Amount computed
    """
    logger.info("[TRANSFORM] Transforming orders...")
    df = df.copy()

    # Strip all string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Standardize IDs
    df["Order_ID"]    = df["Order_ID"].str.upper()
    df["Customer_ID"] = df["Customer_ID"].str.upper()
    df["Product_ID"]  = df["Product_ID"].str.upper()

    # Parse date
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce").dt.date

    # Type casting
    df["Quantity"]   = pd.to_numeric(df["Quantity"],   errors="coerce").fillna(0).astype(int)
    df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce").round(2)
    df["Discount"]   = pd.to_numeric(df["Discount"],   errors="coerce").fillna(0.0).round(2)

    # Feature Engineering: Recalculate Total_Amount to ensure consistency.
    # Formula: Quantity * Unit_Price * (1 - Discount%) 
    df["Total_Amount"] = (
        df["Quantity"] * df["Unit_Price"] * (1 - df["Discount"] / 100)
    ).round(2)

    logger.info(f"[TRANSFORM] Orders transformed: {len(df):,} rows")
    return df