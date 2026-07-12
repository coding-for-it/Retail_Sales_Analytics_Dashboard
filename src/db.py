"""
db.py
-----
Snowflake connection handler for the Retail Sales Analytics ETL pipeline.

Reads credentials from the .env file using python-dotenv.
Provides a single get_connection() function used by load.py.

Environment Variables Required (.env file):
  SNOWFLAKE_USER
  SNOWFLAKE_PASSWORD
  SNOWFLAKE_ACCOUNT
  SNOWFLAKE_WAREHOUSE
  SNOWFLAKE_DATABASE
  SNOWFLAKE_SCHEMA
"""

import os
import logging

import snowflake.connector
from snowflake.connector.errors import Error
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("retail_etl")


def get_connection() -> snowflake.connector.SnowflakeConnection:
    """
    Create and return an authenticated Snowflake connection.

    Returns:
        snowflake.connector.SnowflakeConnection

    Raises:
        ValueError:
            If one or more required environment variables are missing.

        snowflake.connector.errors.Error:
            If Snowflake authentication or connection fails.
    """

    logger.info("Establishing Snowflake connection...")

    required_env = [
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    ]

    missing = [var for var in required_env if not os.getenv(var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    try:
        connection = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )

        logger.info("Snowflake connection established successfully.")
        return connection

    except Error as err:
        logger.error(f"Snowflake connection failed: {err}")
        raise