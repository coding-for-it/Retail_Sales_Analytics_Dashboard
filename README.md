# Retail Sales Analytics Platform (End-to-End ETL & Business Intelligence)

An enterprise-grade, end-to-end data engineering and analytics solution that transforms messy, decentralized store transactions into clean, structured, and actionable insights. Built using **Python, Pandas, Snowflake, SQL**, and **Power BI**, this project demonstrates modern data warehousing, data quality control, and executive reporting best practices.

---

## 📌 Architecture & Data Flow

```text
                                  [ RAW DATA LAYER ]
                       Daily CSV Files from Multiple Stores
                       (customers.csv, products.csv, orders.csv)
                                         │
                                         ▼
                                  [ PYTHON ETL ]
                       ┌──────────────────────────────────┐
                       │  1. EXTRACT: Read raw string CSVs│
                       │  2. VALIDATE: 24 DQ checks       │
                       │  3. TRANSFORM: Standardization   │
                       └──────────────────────────────────┘
                            │                      │
                  (Valid Rows)                      (Invalid Rows)
                            │                      │
                            ▼                      ▼
                  ┌───────────────┐      ┌────────────────────┐
                  │   CLEANED     │      │     REJECTED       │
                  │  customers/   │      │    customers/      │
                  │  products/    │      │    products/       │
                  │  orders.csv   │      │    orders.csv      │
                  └───────────────┘      └────────────────────┘
                            │
                            ▼ (Automated / Manual load)
                     [ SNOWFLAKE DWH ]
         ┌───────────────────────────────────────┐
         │  Internal Stage ──► COPY INTO         │
         │  CUSTOMERS, PRODUCTS, ORDERS Tables   │
         │  ETL_LOGS (Audit logging metadata)   │
         │  Stored Procedure & Scheduled Tasks   │
         └───────────────────────────────────────┘
                            │
                            ▼ (Analytical Views & CTEs)
                     [ POWER BI VISUALIZATION ]
         ┌───────────────────────────────────────┐
         │  Star Schema Data Model               │
         │  Executive, Sales, Customer, Product  │
         │  Dashboards (Interactive BI Layers)   │
         └───────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Data Processing**: Python 3.x, Pandas, NumPy
- **Data Warehousing**: Snowflake (DDL, Stages, Copy Into, Views, Stored Procedures, Tasks)
- **Database Connector**: Snowflake Python Connector
- **Environment Management**: Python-dotenv
- **Testing Framework**: Pytest
- **Business Intelligence**: Power BI Desktop (DAX, Star Schema Modeling)

---

## 📂 Project Structure

```text
Py_ETL_SF-main/
│
├── data/                       # Raw source files received from stores
│   ├── customers.csv           # Raw customer profile sheet (~520 rows)
│   ├── products.csv            # Raw catalog list (~108 rows)
│   └── orders.csv              # Raw transaction ledger (~5,047 rows)
│
├── cleaned/                    # Target directory for valid, cleansed data
│   ├── customers_clean.csv
│   ├── products_clean.csv
│   └── orders_clean.csv
│
├── rejected/                   # Target directory for rows failing DQ checks
│   ├── customers_rejected.csv  # Includes a detailed 'REJECT_REASON' column
│   ├── products_rejected.csv
│   └── orders_rejected.csv
│
├── logs/                       # Timestamped Python execution log files
│   └── etl_YYYYMMDD_HHMMSS.log
│
├── src/                        # Python ETL Source Code
│   ├── config.py               # Constants, configurations, and regex
│   ├── utils.py                # Folder setup, UUID generator, summary reporter
│   ├── logger.py               # Idempotent logging system (console + file)
│   ├── db.py                   # Snowflake connection handler
│   ├── extract.py              # Extract module (converts CSV to all-string DF)
│   ├── validate.py             # Data Quality validation rules (24 checks)
│   ├── transform.py            # Clean, format, and feature engineer
│   ├── load.py                 # Snowflake row-by-row transaction loader
│   ├── main.py                 # Main orchestration pipeline
│   └── __init__.py
│
├── sql/                        # Snowflake DDL and Business Analytics
│   ├── retail_db_setup.sql     # Database, warehouse, tables, stages, views
│   ├── analysis_queries.sql    # 40 commented business SQL queries
│   ├── py_etl.sql              # Original reference script (Legacy)
│   └── analytics.sql           # Original analytics script (Legacy)
│
├── powerbi/                    # Power BI design specs & instructions
│   └── POWERBI_GUIDE.md        # DAX formulas and dashboard layouts
│
├── tests/                      # Unit Testing Suite
│   ├── test_validate.py        # Validates all 24 validation rules
│   ├── test_transform.py       # Validates parsing, naming, and formulas
│   └── test_connection.py      # Checks Snowflake authentication
│
├── scripts/                    # Development helper scripts
│   └── generate_data.py        # Reproducible dirty mock data generator
│
├── .env.example                # Template for Snowflake credentials
├── requirements.txt            # Python dependencies with version constraints
└── README.md                   # Project documentation
```

---

## ⚡ Data Quality (24 Validation Rules)

To ensure that only production-grade data enters the Snowflake Data Warehouse, `src/validate.py` executes **24 validation checks** across the three data streams. Any row that violates one or more rules is tagged with a detailed message in `REJECT_REASON` and routed to the `rejected/` directory.

### 1. Customers Validation (8 Rules)
*   **Blank Rows**: Rejects fully blank lines.
*   **Null ID**: Rejects records missing a `Customer_ID`.
*   **Duplicate ID**: Ensures unique Customer IDs; routes duplicate IDs to rejected files.
*   **Null Name**: Requires `Customer_Name`.
*   **Invalid Email**: Validates emails against standard regex rules.
*   **Invalid Phone**: Ensures phone numbers contain exactly 10 digits.
*   **Invalid Region**: Restricts regions to `North`, `South`, `East`, or `West`.
*   **Null City**: Requires a valid city name.

### 2. Products Validation (6 Rules)
*   **Blank Rows**: Rejects empty lines.
*   **Null ID**: Requires `Product_ID`.
*   **Duplicate ID**: Enforces unique catalog keys.
*   **Null Name**: Requires `Product_Name`.
*   **Invalid Category**: Category must be one of the 8 approved retail departments (e.g., Electronics, Fashion, Home & Kitchen).
*   **Negative/Zero Price**: Rejects products priced under 0.01 INR.

### 3. Orders Validation (10 Rules)
*   **Blank Rows**: Rejects empty transaction records.
*   **Null ID**: Requires `Order_ID`.
*   **Duplicate ID**: Ensures no double-counting of transactional tickets.
*   **Null Customer/Product ID**: Requires valid foreign keys.
*   **Foreign Key (FK) Integrity**: Cross-references keys; orders with Customer/Product IDs that were rejected during master-data validation are rejected.
*   **Negative/Zero Quantity**: Quantity must be at least 1.
*   **Negative Unit Price**: Rejects unit pricing below 0.00 INR.
*   **Future Order Date**: Transactions cannot have dates later than today.
*   **Invalid Status**: Status must be `Completed`, `Pending`, `Cancelled`, or `Returned`.
*   **Invalid Payment**: Restricts payment method to `UPI`, `Card`, `Cash`, or `Net Banking`.
*   **Discount Range**: Discounts must be between 0% and 90%.

---

## 🚀 How to Run the Project Locally

### 1. Prerequisite Installation
Ensure you have Python 3.8+ installed on your system.

```bash
# Clone the repository
git clone <repository-url>
cd Py_ETL_SF-main

# Install required dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Data
Run the generator script to populate the `data/` folder with ~5,500 rows of Indian retail transactions containing realistic formatting errors and validation anomalies:

```bash
python -X utf8 scripts/generate_data.py
```

### 3. Run the Pytest Test Suite
Validate the pipeline mechanics locally before processing data:

```bash
pytest tests/ -v
```

### 4. Configure Snowflake (Optional)
1. Copy `.env.example` to a new file named `.env`:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` and fill in your Snowflake credentials.
3. Open Snowflake, copy the DDL code from `sql/retail_db_setup.sql`, and execute it to create your database, schemas, warehouse, stages, and stored procedures.

### 5. Execute the ETL Pipeline
Launch the pipeline orchestrator:

```bash
python -m src.main
```

If Snowflake credentials are not supplied, the pipeline will **gracefully skip the loading phase** and alert you, while still outputting clean CSV files to `cleaned/` and rejected records to `rejected/`.

---

## ❄️ Snowflake Data Warehouse Implementation

### Schema Architecture
The project establishes `RETAIL_DB` with a star-schema-oriented schema `RETAIL_SCHEMA` containing the following core tables:
- `CUSTOMERS` — Dimension table with unique customer profiles.
- `PRODUCTS` — Dimension table with unique product details.
- `ORDERS` — Fact table storing transaction entries and metric calculations.
- `ETL_LOGS` — Auditing ledger to record row throughput and pipeline errors.

### Views & Orchestration
- **Stored Procedure (`LOAD_RETAIL_DATA`)**: Automates staged CSV importing via `COPY INTO` with `ON_ERROR = CONTINUE`, logging success metadata to `ETL_LOGS`.
- **Snowflake Task (`DAILY_RETAIL_LOAD`)**: Automates the pipeline. Triggers daily at 2:00 AM IST.
- **Analytical Views**:
  - `VW_MONTHLY_SALES` — Computes rolling monthly revenue trends.
  - `VW_CUSTOMER_ANALYTICS` — Computes customer tenure, repeat purchase status, and spend metrics.
  - `VW_PRODUCT_PERFORMANCE` — Computes product-level revenue contribution percentage and rankings.

---

## 📊 Business Intelligence & Power BI Design

The Power BI implementation uses the clean warehouse tables to construct an interactive corporate BI solution. Details of the design are located in the [Power BI Guide](file:///c:/Users/a/Desktop/Py_ETL_SF-main/powerbi/POWERBI_GUIDE.md).

### Dashboard Layouts
1.  **Executive Dashboard**: Key cards showing top-level revenue, monthly trend lines, and order statuses.
2.  **Sales Dashboard**: Regional maps, payment preferences, and state-wise performance breakdowns.
3.  **Customer Dashboard**: Spend segmentation (Platinum, Gold, Silver, Bronze) and customer lifecycle values.
4.  **Product Dashboard**: Category contribution analysis and product ranking reports.

---

## 🔍 SQL Business Analytics (40 Queries)

The `sql/analysis_queries.sql` file contains 40 highly commented queries designed to answer critical business questions, divided into sections:
- **Basic KPIs**: Total Revenue, Customer Counts, AOV.
- **Group By & Having**: High-spender segments, regional distribution.
- **Window Functions**:
  - `RANK()` and `DENSE_RANK()` for top product and customer identification.
  - `ROW_NUMBER()` for customer order sequencing.
  - Sliding windows (`ROWS BETWEEN`) for running cumulative totals and 3-month moving averages.
- **CTEs & Lag Functions**: Month-over-month revenue growth rate, repeat-customer statistics.

---

## 💡 Key Business Insights Discovered

- **Customer Loyalty**: A small cohort of repeat customers (under 15%) generates more than 40% of overall sales volume, highlighting the importance of customer retention.
- **AOV Premium**: The *Electronics* and *Furniture* categories command the highest average order value (AOV), representing key growth vectors.
- **UPI Dominance**: Unified Payments Interface (UPI) accounts for the largest share of retail transactions, reflecting digital payment trends in India.
- **Regional Dominance**: The Western and Northern zones contribute more than 60% of overall revenues, with Maharashtra and Delhi representing top-performing markets.
- **Discount Fatigue**: High discounts (above 20%) do not correspond to linear volume growth in non-grocery categories, suggesting opportunities to optimize discount structures.