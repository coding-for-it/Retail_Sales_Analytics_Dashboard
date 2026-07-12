"""
config.py
---------
Central configuration for the Retail Sales Analytics ETL pipeline.

All constants, file paths, column names, regex patterns, allowed values,
and transformation mappings live here.

No business logic — only configuration.
"""

import os

# ─────────────────────────────────────────────────────────────────────────────
# BASE DIRECTORIES
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR     = os.path.join(BASE_DIR, "data")
CLEANED_DIR  = os.path.join(BASE_DIR, "cleaned")
REJECTED_DIR = os.path.join(BASE_DIR, "rejected")
LOGS_DIR     = os.path.join(BASE_DIR, "logs")

# ─────────────────────────────────────────────────────────────────────────────
# SOURCE FILE PATHS
# ─────────────────────────────────────────────────────────────────────────────

CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.csv")
PRODUCTS_FILE  = os.path.join(DATA_DIR, "products.csv")
ORDERS_FILE    = os.path.join(DATA_DIR, "orders.csv")

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT FILE PATHS
# ─────────────────────────────────────────────────────────────────────────────

CUSTOMERS_CLEAN    = os.path.join(CLEANED_DIR,  "customers_clean.csv")
PRODUCTS_CLEAN     = os.path.join(CLEANED_DIR,  "products_clean.csv")
ORDERS_CLEAN       = os.path.join(CLEANED_DIR,  "orders_clean.csv")

CUSTOMERS_REJECTED = os.path.join(REJECTED_DIR, "customers_rejected.csv")
PRODUCTS_REJECTED  = os.path.join(REJECTED_DIR, "products_rejected.csv")
ORDERS_REJECTED    = os.path.join(REJECTED_DIR, "orders_rejected.csv")

# ─────────────────────────────────────────────────────────────────────────────
# SNOWFLAKE TABLE NAMES
# ─────────────────────────────────────────────────────────────────────────────

TABLE_CUSTOMERS = "CUSTOMERS"
TABLE_PRODUCTS  = "PRODUCTS"
TABLE_ORDERS    = "ORDERS"
TABLE_ETL_LOGS  = "ETL_LOGS"

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION — ALLOWED VALUES
# ─────────────────────────────────────────────────────────────────────────────

VALID_ORDER_STATUSES = {"Completed", "Pending", "Cancelled", "Returned"}

VALID_PAYMENT_METHODS: set = {"UPI", "Card", "Cash", "Net Banking"}

VALID_REGIONS: set = {"North", "South", "East", "West"}

VALID_CATEGORIES: set = {
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Beauty",
    "Sports",
    "Books",
    "Furniture",
    "Groceries",
}

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION — REGEX PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

EMAIL_REGEX = r"^[\w\.\-]+@[\w\.\-]+\.\w{2,}$"
PHONE_REGEX = r"^\d{10}$"

# ─────────────────────────────────────────────────────────────────────────────
# BUSINESS RULES
# ─────────────────────────────────────────────────────────────────────────────

MIN_PRICE          = 0.01      # prices below this are invalid
MAX_DISCOUNT_PCT   = 90.0      # discounts above this % are invalid

# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORMATION — STATE STANDARDIZATION MAP
# Expands common abbreviations to full Indian state names.
# ─────────────────────────────────────────────────────────────────────────────

STATE_MAP: dict = {
    "MH": "Maharashtra",
    "DL": "Delhi",
    "KA": "Karnataka",
    "TN": "Tamil Nadu",
    "GJ": "Gujarat",
    "UP": "Uttar Pradesh",
    "RJ": "Rajasthan",
    "WB": "West Bengal",
    "MP": "Madhya Pradesh",
    "AP": "Andhra Pradesh",
    "TS": "Telangana",
    "HR": "Haryana",
    "PB": "Punjab",
    "KL": "Kerala",
    "BR": "Bihar",
    "OR": "Odisha",
    "JH": "Jharkhand",
    "HP": "Himachal Pradesh",
    "UK": "Uttarakhand",
    "CG": "Chhattisgarh",
    "AS": "Assam",
    "GA": "Goa",
    "JK": "Jammu & Kashmir",
    "MN": "Manipur",
    "TR": "Tripura",
    "NL": "Nagaland",
    "MZ": "Mizoram",
    "SK": "Sikkim",
    "AR": "Arunachal Pradesh",
    "ML": "Meghalaya",
}
