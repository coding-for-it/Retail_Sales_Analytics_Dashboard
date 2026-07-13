# Retail Sales Analytics ETL Pipeline using Python, Snowflake & Power BI
An end-to-end Retail Sales Analytics ETL pipeline that processes raw retail data from multiple CSV sources, applies automated data quality validation, transforms clean records, loads them into Snowflake, and delivers interactive Power BI dashboards using DirectQuery.

The project demonstrates modern data engineering concepts including ETL automation, data validation, Snowflake data warehousing, SQL analytics, ETL auditing, and business intelligence reporting.
---
## 📌 Architecture & Data Flow

```text
                              [ RAW DATA SOURCES ]
                  customers.csv | products.csv | orders.csv
                                     │
                                     ▼
                           [ PYTHON ETL PIPELINE ]
             ┌──────────────────────────────────────────────┐
             │  1. Extract Raw CSV Data                     │
             │  2. Validate (24+ Data Quality Checks)       │
             │  3. Transform & Standardize Data             │
             │  4. Generate Business Metrics                │
             └──────────────────────────────────────────────┘
                         │                       │
               Valid Records              Invalid Records
                         │                       │
                         ▼                       ▼
            ┌─────────────────────┐   ┌──────────────────────┐
            │   CLEANED DATA      │   │   REJECTED DATA      │
            │ customers_clean.csv │   │ customers_rejected   │
            │ products_clean.csv  │   │ products_rejected    │
            │ orders_clean.csv    │   │ orders_rejected      │
            └─────────────────────┘   └──────────────────────┘
                         │
                         ▼
                 [ SNOWFLAKE DATA WAREHOUSE ]
        ┌──────────────────────────────────────────────┐
        │  CUSTOMERS Table                             │
        │  PRODUCTS Table                              │
        │  ORDERS Table                                │
        │  ETL_LOGS (Audit & Pipeline Monitoring)       │
        │  Bulk Loading using Python executemany()      │
        └──────────────────────────────────────────────┘
                         │
                         ▼
                  [ SQL ANALYTICS LAYER ]
        ┌──────────────────────────────────────────────┐
        │  Analytical SQL Queries                      │
        │  VW_ORDERS View                              │
        │  Revenue & Sales Analysis                    │
        │  Customer & Product Insights                 │
        └──────────────────────────────────────────────┘
                         │
                         ▼
                 [ POWER BI DIRECTQUERY ]
        ┌──────────────────────────────────────────────┐
        │ Executive Dashboard                          │
        │ Revenue Trends                               │
        │ Customer Analytics                           │
        │ Product Performance                          │
        │ Regional Sales                               │
        │ ETL Monitoring                               │
        └──────────────────────────────────────────────┘
```
```

---

## 🛠️ Tech Stack

- **Programming Language:** Python 3.x
- **Data Processing:** Pandas, NumPy
- **Data Validation & Transformation:** Python, Regular Expressions (Regex)
- **Data Warehouse:** Snowflake
- **Database Connectivity:** Snowflake Python Connector
- **SQL:** DDL, DML, Views, Aggregations, Window Functions, CTEs
- **Business Intelligence:** Power BI Desktop (DirectQuery, DAX)
- **Environment Management:** python-dotenv
- **Logging:** Python Logging Module
- **Testing:** Pytest
- **Version Control:** Git & GitHub

---

## 📂 Project Structure

```text
Py_ETL_SF-main/
│
├── data/                           # Raw source datasets
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
│
├── cleaned/                        # Valid transformed datasets
│   ├── customers_clean.csv
│   ├── products_clean.csv
│   └── orders_clean.csv
│
├── rejected/                       # Invalid records with rejection reasons
│   ├── customers_rejected.csv
│   ├── products_rejected.csv
│   └── orders_rejected.csv
│
├── logs/                           # ETL execution logs
│   └── etl_YYYYMMDD_HHMMSS.log
│
├── src/
│   ├── __init__.py
│   ├── config.py                   # Project configuration & constants
│   ├── db.py                       # Snowflake connection
│   ├── extract.py                  # CSV extraction
│   ├── validate.py                 # 24+ data quality validation rules
│   ├── transform.py                # Data cleaning & transformations
│   ├── load.py                     # Bulk loading into Snowflake using executemany()
│   ├── utils.py                    # Helper functions & ETL summary
│   ├── logger.py                   # Centralized logging
│   └── main.py                     # ETL pipeline orchestration
│
├── sql/
│   ├── retail_db_setup.sql         # Database, warehouse, tables & views
│   ├── analysis_queries.sql        # Business analytics SQL queries
│   └── vw_orders.sql               # Analytical view used by Power BI
│
├── powerbi/
│   ├── Retail_Sales_Dashboard.pbix
│   └── POWERBI_GUIDE.md
│
├── tests/
│   ├── test_connection.py
│   ├── test_validate.py
│   └── test_transform.py
│
├── scripts/
│   └── generate_data.py            # Generates sample retail datasets
│
├── .env.example                    # Snowflake credential template
├── requirements.txt                # Python dependencies
└── README.md
```
---

## ⚡ Data Quality (24 Validation Rules)

To ensure that only high-quality data reaches the Snowflake warehouse, the ETL pipeline performs **24 automated validation checks** across customer, product, and order datasets. Records failing any validation are tagged with a descriptive `REJECT_REASON` and written to the `rejected/` folder, while valid records continue through the transformation and loading pipeline.

### Customer Validation (8 Rules)

- Blank row detection
- Missing Customer ID
- Duplicate Customer ID
- Missing Customer Name
- Email format validation using Regular Expressions (Regex)
- Phone number validation (10 digits)
- Region validation (`North`, `South`, `East`, `West`)
- Missing City

### Product Validation (6 Rules)

- Blank row detection
- Missing Product ID
- Duplicate Product ID
- Missing Product Name
- Category validation against approved categories
- Positive price validation (Price > 0)

### Order Validation (10 Rules)

- Blank row detection
- Missing Order ID
- Duplicate Order ID
- Missing Customer ID / Product ID
- Foreign Key validation against valid Customers and Products
- Quantity greater than zero
- Unit Price greater than zero
- Order Date cannot be in the future
- Order Status validation
- Payment Method validation
- Discount percentage validation (0–90%)

After validation:

- ✅ Valid records are transformed and loaded into Snowflake.
- ❌ Invalid records are stored separately with rejection reasons for auditing and troubleshooting.

---

# 🚀 Running the Project

## 1. Clone Repository

```bash
git clone <repository-url>
cd Py_ETL_SF-main
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Generate Sample Dataset (Optional)

```bash
python scripts/generate_data.py
```

This creates approximately:

- 520 Customers
- 108 Products
- 5,047 Orders

with realistic validation errors for testing the pipeline.

## 4. Configure Snowflake

Create a `.env` file.

```env
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_ROLE=
```

Run the SQL setup script:

```
sql/retail_db_setup.sql
```

This creates:

- Database
- Warehouse
- Schema
- Tables
- Views

## 5. Execute the ETL Pipeline

```bash
python -m src.main
```

Pipeline Flow:

1. Extract CSV files
2. Validate data (24 checks)
3. Transform clean records
4. Save Cleaned & Rejected CSVs
5. Load validated records into Snowflake using **executemany()**
6. Record ETL execution details in `ETL_LOGS`

---

# ❄️ Snowflake Data Warehouse

## Database Objects

The Snowflake warehouse contains four primary tables:

### CUSTOMERS

Stores cleansed customer master data.

### PRODUCTS

Stores cleansed product master data.

### ORDERS

Fact table containing retail sales transactions.

### ETL_LOGS

Captures ETL execution metadata including:

- Run ID
- Start Time
- End Time
- Rows Read
- Rows Loaded
- Rows Rejected
- Status
- Error Message

---

## SQL Analytics View

A reporting view (`VW_ORDERS`) is created on top of the ORDERS table to simplify reporting and Power BI integration.

The view derives additional analytical attributes including:

- Month Name
- Month Number
- Year
- Quarter

This avoids creating calculated columns inside Power BI and enables efficient DirectQuery reporting.

---

## Data Loading Strategy

The Python ETL pipeline connects to Snowflake using the Snowflake Python Connector.

Validated records are inserted using **parameterized `executemany()` bulk inserts**, providing:

- Faster loading than row-by-row inserts
- Transaction management
- Rollback support
- SQL injection protection
- Better scalability for medium-sized datasets

---

# 📊 Power BI Dashboard

Power BI connects directly to Snowflake using **DirectQuery**, enabling reports to always reflect the latest warehouse data without importing datasets.

The dashboard includes:

### Executive Dashboard

- Revenue KPI
- Orders KPI
- Customers KPI
- Products KPI
- Monthly Revenue Trend
- Order Status Distribution

### Sales Dashboard

- Revenue by State
- Revenue by Region
- Payment Method Analysis
- Monthly Sales Trend

### Customer Dashboard

- Customer Distribution by Region
- Top Customers
- Customer Growth Trend

### Product Dashboard

- Revenue by Category
- Top Selling Products
- Brand Performance
- Product Revenue Ranking

---

# 🔍 SQL Analytics

The project includes **40+ business SQL queries** covering:

- Aggregate Functions
- GROUP BY & HAVING
- Joins
- Common Table Expressions (CTEs)
- Window Functions
- Ranking Functions
- Running Totals
- Moving Averages
- Revenue Analysis
- Customer Analytics
- Product Performance
- Regional Sales Analysis

These queries demonstrate analytical SQL capabilities commonly used in Data Analyst and Data Engineer roles.

---

# 💡 Sample Business Insights

Using the warehouse and Power BI dashboards, the project can identify:

- Highest revenue generating product categories
- Top-performing products by sales
- Best-performing regions and states
- Customer purchase distribution
- Most preferred payment methods
- Monthly revenue trends
- Order status distribution
- Revenue contribution by product category
- Customer growth over time
- Overall ETL execution statistics from `ETL_LOGS`
