import os
import pytest
from src.db import get_connection

def test_snowflake_connection():
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
        pytest.skip("Snowflake environment variables are not set. Skipping connection test.")

    conn = get_connection()
    assert conn is not None
    conn.close()