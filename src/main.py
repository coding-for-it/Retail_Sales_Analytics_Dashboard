"""
main.py
-------
Pipeline orchestrator for the Retail Sales Analytics ETL.

Execution Order:
  1. Setup      → create output directories, initialize logger, generate run ID
  2. Extract    → read customers.csv, products.csv, orders.csv
  3. Validate   → apply 24 validation rules across 3 entities
  4. Transform  → clean, standardize, type-cast, compute Total_Amount
  5. Save       → write clean and rejected CSVs to cleaned/ and rejected/
  6. Load       → INSERT into Snowflake (skipped gracefully if .env not set)
  7. Summary    → print and log the ETL summary report

Run:
  python -m src.main
"""

import time
import logging
from datetime import datetime

from src.logger import get_logger
from src.utils import (
    ensure_directories,
    generate_run_id,
    save_csv,
    generate_etl_summary,
    print_separator,
)
from src.extract import extract_customers, extract_products, extract_orders
from src.validate import validate_customers, validate_products, validate_orders
from src.transform import transform_customers, transform_products, transform_orders
from src.config import (
    CUSTOMERS_CLEAN, PRODUCTS_CLEAN, ORDERS_CLEAN,
    CUSTOMERS_REJECTED, PRODUCTS_REJECTED, ORDERS_REJECTED,
)
from src.load import (
    clear_tables,
    load_customers,
    load_products,
    load_orders,
    log_etl_run,
)


# Initialize logger at module level (same pattern as original project)
logger = get_logger()


def run_pipeline() -> None:
    """
    Execute the full Retail Sales Analytics ETL pipeline end-to-end.

    The pipeline is designed to:
      - Always generate cleaned/ and rejected/ CSV files
      - Gracefully skip Snowflake loading if credentials are not configured
      - Log every step with timestamps and row counts
      - Print a formatted summary report at the end

    Pipeline Steps:
      1. Setup          → directories and run ID
      2. Extract        → raw CSVs into DataFrames
      3. Validate       → 24 rules, produce clean and rejected splits
      4. Transform      → standardize, type-cast, feature engineer
      5. Save outputs   → cleaned/ and rejected/ CSVs
      6. Load Snowflake → INSERT into CUSTOMERS, PRODUCTS, ORDERS
      7. Log ETL run    → INSERT into ETL_LOGS
      8. Summary        → formatted report to console and log file
    """
    run_id     = generate_run_id()
    start_time = time.time()
    start_dt   = datetime.now()
    status     = "SUCCESS"
    error_msg  = ""

    # Track row counts per entity for the summary report
    stats = {
        "customers": {"read": 0, "loaded": 0, "rejected": 0},
        "products":  {"read": 0, "loaded": 0, "rejected": 0},
        "orders":    {"read": 0, "loaded": 0, "rejected": 0},
    }

    print_separator("RETAIL SALES ANALYTICS — ETL PIPELINE")
    logger.info(f"Pipeline started | Run ID: {run_id}")

    # ── Step 1: Setup ─────────────────────────────────────────────────────────
    ensure_directories()

    try:
        # ── Step 2: Extract ───────────────────────────────────────────────────
        print_separator("PHASE 1 — EXTRACT")
        raw_customers = extract_customers()
        raw_products  = extract_products()
        raw_orders    = extract_orders()

        stats["customers"]["read"] = len(raw_customers)
        stats["products"]["read"]  = len(raw_products)
        stats["orders"]["read"]    = len(raw_orders)

        # ── Step 3: Validate ──────────────────────────────────────────────────
        print_separator("PHASE 2 — VALIDATE")

        clean_customers, rejected_customers = validate_customers(raw_customers)
        clean_products,  rejected_products  = validate_products(raw_products)

        # Build FK reference sets from validated entities
        valid_customer_ids = set(clean_customers["Customer_ID"].str.upper())
        valid_product_ids  = set(clean_products["Product_ID"].str.upper())

        clean_orders, rejected_orders = validate_orders(
            raw_orders, valid_customer_ids, valid_product_ids
        )

        stats["customers"]["rejected"] = len(rejected_customers)
        stats["products"]["rejected"]  = len(rejected_products)
        stats["orders"]["rejected"]    = len(rejected_orders)

        # ── Step 4: Transform ─────────────────────────────────────────────────
        print_separator("PHASE 3 — TRANSFORM")
        transformed_customers = transform_customers(clean_customers)
        transformed_products  = transform_products(clean_products)
        transformed_orders    = transform_orders(clean_orders)

        # ── Step 5: Save outputs ──────────────────────────────────────────────
        print_separator("PHASE 4 — SAVE OUTPUTS")
        save_csv(transformed_customers, CUSTOMERS_CLEAN,    "customers_clean")
        save_csv(transformed_products,  PRODUCTS_CLEAN,     "products_clean")
        save_csv(transformed_orders,    ORDERS_CLEAN,       "orders_clean")

        save_csv(rejected_customers,    CUSTOMERS_REJECTED, "customers_rejected")
        save_csv(rejected_products,     PRODUCTS_REJECTED,  "products_rejected")
        save_csv(rejected_orders,       ORDERS_REJECTED,    "orders_rejected")

        # ── Step 6 & 7: Load Snowflake ────────────────────────────────────────
        print_separator("PHASE 5 — LOAD TO SNOWFLAKE")
        try:
            from src.db   import get_connection
            from src.load import (
                clear_tables,load_customers, load_products,
                load_orders, log_etl_run,
            )

            conn = get_connection()
            #remove previous data
            clear_tables(conn)


            stats["customers"]["loaded"] = load_customers(transformed_customers, conn)
            stats["products"]["loaded"]  = load_products(transformed_products,  conn)
            stats["orders"]["loaded"]    = load_orders(transformed_orders,      conn)

            end_dt = datetime.now()
            log_etl_run(
                run_id        = run_id,
                start_time    = start_dt,
                end_time      = end_dt,
                rows_read     = sum(s["read"]     for s in stats.values()),
                rows_loaded   = sum(s["loaded"]   for s in stats.values()),
                rows_rejected = sum(s["rejected"] for s in stats.values()),
                status        = status,
                error_message = error_msg,
                conn          = conn,
            )
            conn.close()

        except Exception as sf_err:
            logger.warning(
                f"Snowflake load skipped: {sf_err}\n"
                "→ Cleaned CSV files saved. Configure .env to enable Snowflake loading."
            )
            print(
                "\n  ⚠  Snowflake not configured — data saved locally.\n"
                "     Add credentials to .env and re-run to load into Snowflake.\n"
            )

    except Exception as pipeline_err:
        status    = "FAILED"
        error_msg = str(pipeline_err)
        logger.error(f"Pipeline failed: {pipeline_err}", exc_info=True)

    # ── Step 8: Summary ───────────────────────────────────────────────────────
    summary = generate_etl_summary(run_id, start_time, stats, status, error_msg)
    print(summary)
    logger.info(summary)
    logger.info("Pipeline finished.")


if __name__ == "__main__":
    run_pipeline()