"""
extract.py
----------
Extraction layer of the Retail Sales Analytics ETL pipeline.

Reads raw CSV files from the data/ directory and returns Pandas DataFrames.
All columns are read as strings (dtype=str) so that the validate.py module
can perform proper type-checking rather than relying on Pandas inference.

Functions:
  extract_customers() → DataFrame
  extract_products()  → DataFrame
  extract_orders()    → DataFrame
"""

import os
import logging

import pandas as pd

from src.config import CUSTOMERS_FILE, PRODUCTS_FILE, ORDERS_FILE

logger = logging.getLogger("retail_etl")


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _read_csv(file_path: str, label: str) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame with consistent settings and logging.

    - Reads all columns as strings (dtype=str) for safe validation
    - Converts pandas NaN → None for cleaner null checks downstream
    - Logs row count and column list

    Args:
        file_path: Path to the CSV file
        label    : Human-readable entity name for logging

    Returns:
        pd.DataFrame with raw string data

    Raises:
        FileNotFoundError: If the file does not exist at the given path
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"[EXTRACT] {label} source file not found: '{file_path}'\n"
            f"  → Place the CSV file in the data/ directory and retry."
        )

    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

    # Normalize empty strings to None for uniform null handling
    df.replace("", None, inplace=True)

    logger.info(
        f"[EXTRACT] {label}: {len(df)} rows | "
        f"Columns: {list(df.columns)}"
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC EXTRACT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def extract_customers() -> pd.DataFrame:
    """
    Extract raw customer data from customers.csv.

    Expected columns:
      Customer_ID, Customer_Name, Email, Phone,
      City, State, Region, Join_Date

    Returns:
        pd.DataFrame with raw customer data (all columns as strings)
    """
    logger.info("[EXTRACT] Starting extraction → customers.csv")
    df = _read_csv(CUSTOMERS_FILE, "Customers")
    logger.info(f"[EXTRACT] Customers extraction complete: {len(df)} rows read.")
    return df


def extract_products() -> pd.DataFrame:
    """
    Extract raw product data from products.csv.

    Expected columns:
      Product_ID, Product_Name, Category, Brand, Price

    Returns:
        pd.DataFrame with raw product data (all columns as strings)
    """
    logger.info("[EXTRACT] Starting extraction → products.csv")
    df = _read_csv(PRODUCTS_FILE, "Products")
    logger.info(f"[EXTRACT] Products extraction complete: {len(df)} rows read.")
    return df


def extract_orders() -> pd.DataFrame:
    """
    Extract raw order data from orders.csv.

    Expected columns:
      Order_ID, Customer_ID, Product_ID, Order_Date, Quantity,
      Unit_Price, Discount, Total_Amount, Order_Status, Payment_Method

    Returns:
        pd.DataFrame with raw order data (all columns as strings)
    """
    logger.info("[EXTRACT] Starting extraction → orders.csv")
    df = _read_csv(ORDERS_FILE, "Orders")
    logger.info(f"[EXTRACT] Orders extraction complete: {len(df)} rows read.")
    return df