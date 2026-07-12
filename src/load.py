"""
load.py
-------
Loading layer for the Retail Sales Analytics ETL pipeline.

Functions:
  load_customers(df, conn) → inserts into CUSTOMERS table
  load_products(df, conn)  → inserts into PRODUCTS table
  load_orders(df, conn)    → inserts into ORDERS table
  log_etl_run(...)         → inserts run summary into ETL_LOGS table

Design Notes:
  - Uses the same conn/cursor/rollback/finally pattern as the original project
  - Row-by-row INSERT is intentional for readability and debuggability
  - All None/NaN values are converted to SQL NULL before insertion
"""

import logging
from datetime import datetime

import pandas as pd

from src.config import (
    TABLE_CUSTOMERS,
    TABLE_PRODUCTS,
    TABLE_ORDERS,
    TABLE_ETL_LOGS,
)

logger = logging.getLogger("retail_etl")

def clear_tables(conn):
    """
    Remove existing data before loading a fresh dataset.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"TRUNCATE TABLE {TABLE_ORDERS}")
        cursor.execute(f"TRUNCATE TABLE {TABLE_PRODUCTS}")
        cursor.execute(f"TRUNCATE TABLE {TABLE_CUSTOMERS}")
        conn.commit()
        logger.info("[LOAD] Existing data cleared from Snowflake tables.")
    except Exception as e:
        conn.rollback()
        logger.error(f"[LOAD] Failed to clear tables: {e}")
        raise
    finally:
        cursor.close()

# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _batch_insert(
    cursor,
    table: str,
    columns: list,
    df: pd.DataFrame,
    label: str,
) -> int:
    """
    Bulk insert records into Snowflake using executemany().

    Uses parameterized SQL for performance and security.
    Converts NaN/None values to SQL NULL.
    """

    placeholders = ", ".join(["%s"] * len(columns))
    col_list = ", ".join(columns)

    query = f"""
        INSERT INTO {table} ({col_list})
        VALUES ({placeholders})
    """

    values = [
        tuple(
            None if (pd.isna(value) or value is None) else value
            for value in row
        )
        for row in df[columns].itertuples(index=False, name=None)
    ]

    cursor.executemany(query, values)

    logger.info(
        f"[LOAD] {label}: {len(values):,} rows inserted into {table}"
    )

    return len(values)

# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC LOAD FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def load_customers(df: pd.DataFrame, conn) -> int:
    """
    Load transformed customers DataFrame into the CUSTOMERS Snowflake table.

    Args:
        df  : Transformed customers DataFrame
        conn: Active Snowflake connection

    Returns:
        int: Number of rows inserted

    Raises:
        Exception: On Snowflake INSERT failure (triggers rollback)
    """
    columns = [
        "CUSTOMER_ID", "CUSTOMER_NAME", "EMAIL",
        "PHONE", "CITY", "STATE", "REGION", "JOIN_DATE",
    ]

    df_mapped = pd.DataFrame({
        "CUSTOMER_ID"  : df["Customer_ID"],
        "CUSTOMER_NAME": df["Customer_Name"],
        "EMAIL"        : df["Email"],
        "PHONE"        : df["Phone"],
        "CITY"         : df["City"],
        "STATE"        : df["State"],
        "REGION"       : df["Region"],
        "JOIN_DATE"    : df["Join_Date"],
    })

    cursor = conn.cursor()
    try:
        rows = _batch_insert(cursor, TABLE_CUSTOMERS, columns, df_mapped, "Customers")
        conn.commit()
        return rows
    except Exception as e:
        conn.rollback()
        logger.error(f"[LOAD] Customers load failed — rolled back: {e}")
        raise
    finally:
        cursor.close()


def load_products(df: pd.DataFrame, conn) -> int:
    """
    Load transformed products DataFrame into the PRODUCTS Snowflake table.

    Args:
        df  : Transformed products DataFrame
        conn: Active Snowflake connection

    Returns:
        int: Number of rows inserted

    Raises:
        Exception: On Snowflake INSERT failure (triggers rollback)
    """
    columns = ["PRODUCT_ID", "PRODUCT_NAME", "CATEGORY", "BRAND", "PRICE"]

    df_mapped = pd.DataFrame({
        "PRODUCT_ID"  : df["Product_ID"],
        "PRODUCT_NAME": df["Product_Name"],
        "CATEGORY"    : df["Category"],
        "BRAND"       : df["Brand"],
        "PRICE"       : df["Price"],
    })

    cursor = conn.cursor()
    try:
        rows = _batch_insert(cursor, TABLE_PRODUCTS, columns, df_mapped, "Products")
        conn.commit()
        return rows
    except Exception as e:
        conn.rollback()
        logger.error(f"[LOAD] Products load failed — rolled back: {e}")
        raise
    finally:
        cursor.close()


def load_orders(df: pd.DataFrame, conn) -> int:
    """
    Load transformed orders DataFrame into the ORDERS Snowflake table.

    Args:
        df  : Transformed orders DataFrame
        conn: Active Snowflake connection

    Returns:
        int: Number of rows inserted

    Raises:
        Exception: On Snowflake INSERT failure (triggers rollback)
    """
    columns = [
        "ORDER_ID", "CUSTOMER_ID", "PRODUCT_ID", "ORDER_DATE",
        "QUANTITY", "UNIT_PRICE", "DISCOUNT", "TOTAL_AMOUNT",
        "ORDER_STATUS", "PAYMENT_METHOD",
    ]

    df_mapped = pd.DataFrame({
        "ORDER_ID"      : df["Order_ID"],
        "CUSTOMER_ID"   : df["Customer_ID"],
        "PRODUCT_ID"    : df["Product_ID"],
        "ORDER_DATE"    : df["Order_Date"],
        "QUANTITY"      : df["Quantity"],
        "UNIT_PRICE"    : df["Unit_Price"],
        "DISCOUNT"      : df["Discount"],
        "TOTAL_AMOUNT"  : df["Total_Amount"],
        "ORDER_STATUS"  : df["Order_Status"],
        "PAYMENT_METHOD": df["Payment_Method"],
    })

    cursor = conn.cursor()
    try:
        rows = _batch_insert(cursor, TABLE_ORDERS, columns, df_mapped, "Orders")
        conn.commit()
        return rows
    except Exception as e:
        conn.rollback()
        logger.error(f"[LOAD] Orders load failed — rolled back: {e}")
        raise
    finally:
        cursor.close()


def log_etl_run(
    run_id: str,
    start_time: datetime,
    end_time: datetime,
    rows_read: int,
    rows_loaded: int,
    rows_rejected: int,
    status: str,
    error_message: str,
    conn,
) -> None:
    """
    Insert a pipeline run record into the ETL_LOGS Snowflake table.

    Called at the end of every pipeline execution (success or failure)
    to provide a full audit trail of every ETL run.

    Args:
        run_id        : Unique UUID for this run
        start_time    : datetime when the pipeline started
        end_time      : datetime when the pipeline finished
        rows_read     : Total rows read across all 3 source files
        rows_loaded   : Total rows successfully inserted into Snowflake
        rows_rejected : Total rows rejected during validation
        status        : 'SUCCESS' or 'FAILED'
        error_message : Error description (empty string on success)
        conn          : Active Snowflake connection
    """
    query = f"""
        INSERT INTO {TABLE_ETL_LOGS}
        (RUN_ID, START_TIME, END_TIME, ROWS_READ,
         ROWS_LOADED, ROWS_REJECTED, STATUS, ERROR_MESSAGE)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(query, (
            run_id, start_time, end_time,
            rows_read, rows_loaded, rows_rejected,
            status, error_message or "",
        ))
        conn.commit()
        logger.info(
            f"[LOAD] ETL run logged → RUN_ID: {run_id} | Status: {status}"
        )
    except Exception as e:
        logger.warning(f"[LOAD] ETL_LOGS write failed (non-critical): {e}")
    finally:
        cursor.close()