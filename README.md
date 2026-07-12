# Python + Snowflake Automated ETL Pipeline

## Overview

An end-to-end ETL (Extract, Transform, Load) pipeline built using **Python, Pandas, and Snowflake** to process and analyze sales data.

The project demonstrates a complete data engineering workflow where raw CSV data is extracted, validated, transformed, loaded into Snowflake, automated using Snowflake Tasks, and analyzed using SQL queries to generate business insights.

---

# Architecture

```text
CSV Data Source

        ↓

Python Extraction Layer

        ↓

Data Validation & Transformation

        ↓

Snowflake Internal Stage

        ↓

COPY INTO Command

        ↓

Raw Table

        ↓

Stored Procedure + Snowflake Task

        ↓

Final Sales Table

        ↓

SQL Analytics
```

---

# Tech Stack

- Python
- Pandas
- Snowflake
- SQL
- Snowflake Connector for Python
- Python-dotenv
- Pytest

---

# Project Structure

```text
snowflake_etl_project
│
├── data
│   └── sales.csv                 # Input sales dataset
│
├── src
│   ├── db.py                     # Snowflake connection handling
│   ├── extract.py                # Extract data from CSV
│   ├── transform.py              # Data cleaning and validation
│   ├── load.py                   # Load data into Snowflake
│   ├── logger.py                 # Pipeline logging configuration
│   ├── main.py                   # ETL pipeline execution
│   └── __init__.py
│
├── tests
│   ├── test_transform.py         # Transformation testing
│   └── test_connection.py        # Snowflake connection testing
│
├── sql
│   ├── etl_pipeline.sql          # Snowflake database setup and automation
│   └── analytics.sql             # Business analytics queries
│
├── logs
│   └── etl.log                   # Pipeline execution logs
│
├── .env                          # Snowflake credentials
├── pytest.ini                    # Pytest configuration
├── requirements.txt
└── README.md
```

---

# ETL Workflow

## 1. Extract

The extraction layer reads sales data from CSV files using Pandas.

Process:

```text
sales.csv

↓

Pandas DataFrame

↓

ETL Processing
```

Features:

- Input file validation
- Structured data extraction
- Logging of extraction process

---

# 2. Transform

The transformation layer performs data preprocessing and feature creation.

Implemented operations:

- Missing value detection
- Missing value handling
- Duplicate record identification
- Duplicate removal
- Data validation
- Business metric creation


Example:

```text
TOTAL_SALES = QUANTITY × PRICE
```

This creates a calculated revenue field used for analytics.

---

# 3. Data Quality Validation

The pipeline includes validation checks before loading data.

Implemented checks:

- Missing value validation
- Duplicate record detection
- Required column validation
- Transformation verification

This ensures only clean data reaches Snowflake.

---

# 4. Load

The loading layer connects Python with Snowflake using the Snowflake Connector.

Processed data is loaded into Snowflake tables.

Loading process:

```text
Python DataFrame

↓

Snowflake Connection

↓

SALES Table
```

Features:

- Secure credential management using environment variables
- Error handling
- Transaction rollback support
- Execution logging

---

# Snowflake Implementation

## Database

```text
ETL_DB
```

## Schema

```text
SALES_SCHEMA
```

---

# Snowflake Data Flow

```text
CSV File

↓

Snowflake Internal Stage

↓

COPY INTO SALES_RAW

↓

Stored Procedure Transformation

↓

SALES_FINAL

↓

Analytics
```

---

# Snowflake Features Used

## Internal Stage

Used to store and manage incoming CSV files before ingestion.

---

## COPY INTO

Used for loading staged files into Snowflake tables.

---

## Stored Procedure

Created reusable SQL logic for transforming and loading processed sales data.

---

## Snowflake Task

Implemented scheduled execution of data loading workflows.

Example:

```text
Task Schedule:
Every 5 minutes
```

This reduces manual execution of ETL operations.

---

# Database Design

Database:

```text
ETL_DB
```

Schema:

```text
SALES_SCHEMA
```

Tables:

---

## SALES_RAW

Stores incoming raw data.

Columns:

| Column | Description |
|---|---|
| ORDER_ID | Unique order identifier |
| CUSTOMER_NAME | Customer name |
| PRODUCT | Product name |
| QUANTITY | Units purchased |
| PRICE | Product price |
| ORDER_DATE | Date of order |

---

## SALES_FINAL

Stores transformed business-ready data.

Additional column:

| Column | Description |
|---|---|
| TOTAL_SALES | Revenue generated per order |

Formula:

```text
TOTAL_SALES = QUANTITY * PRICE
```

---

# SQL Analytics

Created SQL queries to generate business insights.

Analytics performed:

## Revenue Analysis

- Total revenue calculation
- Overall sales performance

---

## Product Analysis

- Product-wise revenue
- Best-performing products
- Sales ranking

---

## Customer Analysis

- Customer spending analysis
- Order frequency analysis

---

## Sales Trends

- Monthly revenue trends
- Business performance analysis

---

# Testing

Implemented unit testing using Pytest.

Test coverage:

- Transformation logic validation
- Snowflake connection validation

Run tests:

```bash
pytest
```

---

# Installation & Setup

Clone repository:

```bash
git clone <repository-url>
```

Navigate:

```bash
cd snowflake_etl_project
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create `.env` file:

```env
SNOWFLAKE_USER=

SNOWFLAKE_PASSWORD=

SNOWFLAKE_ACCOUNT=

SNOWFLAKE_WAREHOUSE=

SNOWFLAKE_DATABASE=

SNOWFLAKE_SCHEMA=
```

---

# Run Pipeline

Execute:

```bash
python -m src.main
```

Pipeline execution:

```text
Extract Data

↓

Transform Data

↓

Validate Data

↓

Load Into Snowflake

↓

Generate Analytics
```

---

# Key Features

- End-to-end ETL pipeline implementation
- Python and Snowflake integration
- Snowflake internal stage implementation
- COPY INTO data loading
- Data cleaning and validation
- Stored procedure based transformation
- Scheduled Snowflake Task automation
- SQL analytics layer
- Logging and error handling
- Unit testing using Pytest

---

# Future Improvements

- Incremental data processing using Snowflake Streams
- Cloud storage integration (AWS S3 / Azure Blob)
- Advanced monitoring and alerting
- Pipeline performance optimization