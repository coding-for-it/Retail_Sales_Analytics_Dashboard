"""
Power BI Dashboard Design Guide
================================
Retail Sales Analytics Platform
================================

This file is your complete reference for building 4 Power BI dashboards
using the data model defined in Snowflake.

Contents:
  1. Data Model (Star Schema)
  2. Snowflake Connection Setup
  3. DAX Measures (20+)
  4. Dashboard 1: Executive Dashboard
  5. Dashboard 2: Sales Dashboard
  6. Dashboard 3: Customer Dashboard
  7. Dashboard 4: Product Dashboard
  8. Slicers & Filters
  9. Bookmarks & Navigation
  10. Drill-Through Configuration
  11. KPI Summary Table
"""


# ====================================================================
# 1. DATA MODEL — STAR SCHEMA
# ====================================================================
"""
The data model follows a Star Schema pattern:

              CUSTOMERS
              (Dimension)
                  |
                  | Customer_ID
                  |
PRODUCTS ─── ORDERS ─── (Fact Table)
(Dimension)   Customer_ID
              Product_ID
              Order_Date
              Quantity
              Unit_Price
              Discount
              Total_Amount
              Order_Status
              Payment_Method

Relationships in Power BI:
  CUSTOMERS[Customer_ID] → ORDERS[Customer_ID]   (1-to-Many)
  PRODUCTS[Product_ID]   → ORDERS[Product_ID]    (1-to-Many)

Also add a Date Table (recommended for time intelligence):
  CALENDAR[Date] → ORDERS[Order_Date]            (1-to-Many)
"""


# ====================================================================
# 2. SNOWFLAKE CONNECTION SETUP
# ====================================================================
"""
Steps to connect Power BI to Snowflake:

1. Open Power BI Desktop
2. Get Data → Snowflake
3. Enter:
     Server   : your_account.snowflakecomputing.com
     Database : RETAIL_DB
4. Select tables:
     CUSTOMERS
     PRODUCTS
     ORDERS
5. Or use DirectQuery to load the Views:
     VW_MONTHLY_SALES
     VW_CUSTOMER_ANALYTICS
     VW_PRODUCT_PERFORMANCE

Recommended: Import Mode for better performance
Use DirectQuery only if data refreshes more than once per hour.
"""


# ====================================================================
# 3. DATE TABLE (Create in Power BI using DAX)
# ====================================================================
"""
In Power BI, go to Modeling → New Table and paste:

CALENDAR =
ADDCOLUMNS(
    CALENDAR(DATE(2024, 1, 1), DATE(2025, 12, 31)),
    "Year",         YEAR([Date]),
    "Month",        MONTH([Date]),
    "Month Name",   FORMAT([Date], "MMMM"),
    "Month Short",  FORMAT([Date], "MMM"),
    "Quarter",      "Q" & QUARTER([Date]),
    "Week",         WEEKNUM([Date]),
    "Day",          DAY([Date]),
    "Day Name",     FORMAT([Date], "dddd"),
    "Year-Month",   FORMAT([Date], "YYYY-MM"),
    "Is Weekend",   IF(WEEKDAY([Date], 2) >= 6, TRUE, FALSE)
)

Mark as Date Table: CALENDAR[Date]
Create relationship: CALENDAR[Date] → ORDERS[Order_Date]
"""


# ====================================================================
# 4. DAX MEASURES
# ====================================================================
"""
Create a dedicated Measures Table (empty table called "_Measures"):

── REVENUE MEASURES ──────────────────────────────────────────────────

Total Revenue =
CALCULATE(
    SUMX(ORDERS, ORDERS[Total_Amount]),
    ORDERS[Order_Status] <> "Cancelled"
)

Completed Revenue =
CALCULATE(
    SUM(ORDERS[Total_Amount]),
    ORDERS[Order_Status] = "Completed"
)

Cancelled Revenue =
CALCULATE(
    SUM(ORDERS[Total_Amount]),
    ORDERS[Order_Status] = "Cancelled"
)

Returned Revenue =
CALCULATE(
    SUM(ORDERS[Total_Amount]),
    ORDERS[Order_Status] = "Returned"
)

── ORDER MEASURES ─────────────────────────────────────────────────────

Total Orders =
DISTINCTCOUNT(ORDERS[Order_ID])

Completed Orders =
CALCULATE(
    DISTINCTCOUNT(ORDERS[Order_ID]),
    ORDERS[Order_Status] = "Completed"
)

Average Order Value =
DIVIDE(
    CALCULATE(SUM(ORDERS[Total_Amount]), ORDERS[Order_Status] <> "Cancelled"),
    CALCULATE(DISTINCTCOUNT(ORDERS[Order_ID]), ORDERS[Order_Status] <> "Cancelled")
)

── CUSTOMER MEASURES ──────────────────────────────────────────────────

Total Customers =
DISTINCTCOUNT(CUSTOMERS[Customer_ID])

Active Customers =
CALCULATE(
    DISTINCTCOUNT(ORDERS[Customer_ID]),
    ORDERS[Order_Status] <> "Cancelled"
)

Repeat Customers =
COUNTROWS(
    FILTER(
        SUMMARIZE(
            ORDERS,
            ORDERS[Customer_ID],
            "OrderCount", DISTINCTCOUNT(ORDERS[Order_ID])
        ),
        [OrderCount] > 1
    )
)

Repeat Customer % =
DIVIDE([Repeat Customers], [Active Customers], 0) * 100

Customer Lifetime Value =
AVERAGEX(
    VALUES(ORDERS[Customer_ID]),
    CALCULATE(SUM(ORDERS[Total_Amount]), ORDERS[Order_Status] <> "Cancelled")
)

── PRODUCT MEASURES ───────────────────────────────────────────────────

Total Products =
DISTINCTCOUNT(PRODUCTS[Product_ID])

Total Units Sold =
CALCULATE(
    SUM(ORDERS[Quantity]),
    ORDERS[Order_Status] <> "Cancelled"
)

Revenue per Unit =
DIVIDE([Total Revenue], [Total Units Sold], 0)

── GROWTH MEASURES ────────────────────────────────────────────────────

Revenue LY (Last Year) =
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(CALENDAR[Date])
)

Revenue YoY Growth % =
VAR CurrentRev = [Total Revenue]
VAR LastYearRev = [Revenue LY]
RETURN
    IF(
        ISBLANK(LastYearRev),
        BLANK(),
        DIVIDE(CurrentRev - LastYearRev, LastYearRev, 0) * 100
    )

MoM Revenue Growth % =
VAR CurrentMonth = [Total Revenue]
VAR LastMonth = CALCULATE(
    [Total Revenue],
    DATEADD(CALENDAR[Date], -1, MONTH)
)
RETURN
    IF(
        ISBLANK(LastMonth),
        BLANK(),
        DIVIDE(CurrentMonth - LastMonth, LastMonth, 0) * 100
    )

Revenue Contribution % =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(PRODUCTS[Category])),
    0
) * 100

── DYNAMIC TITLE MEASURES ─────────────────────────────────────────────

Dynamic Title Revenue =
"Total Revenue: " & FORMAT([Total Revenue], "#,##0.00") & " INR"

Dynamic Title Orders =
"Total Orders: " & FORMAT([Total Orders], "#,##0")

Selected Category =
IF(
    ISFILTERED(PRODUCTS[Category]),
    SELECTEDVALUE(PRODUCTS[Category], "All Categories"),
    "All Categories"
)
"""


# ====================================================================
# 5. DASHBOARD 1: EXECUTIVE DASHBOARD
# ====================================================================
"""
PURPOSE: High-level KPIs for senior management.
AUDIENCE: CEO, VP Sales, Directors

── LAYOUT ─────────────────────────────────────────────────────────────

Row 1 — KPI Cards (4 cards across the top):
  [Total Revenue]   [Total Orders]   [Total Customers]   [Avg Order Value]
  Use: Card visual with conditional formatting

Row 2 — Trend Chart (full width):
  Visual: Line Chart
  X-Axis: CALENDAR[Year-Month]
  Y-Axis: [Total Revenue]
  Secondary: [Total Orders]
  Enable: Data labels, markers

Row 3 — Two Side-by-Side Charts:
  Left:  Donut Chart → Revenue by Region
  Right: Bar Chart   → Revenue by Order Status

Row 4 — Summary Table:
  Visual: Matrix
  Rows:    Region
  Columns: Quarter
  Values:  Total Revenue, Total Orders, Avg Order Value

── SLICERS ────────────────────────────────────────────────────────────
  - Year           (CALENDAR[Year])         → Dropdown
  - Quarter        (CALENDAR[Quarter])      → Dropdown
  - Order Status   (ORDERS[Order_Status])   → Multi-select

── KPIs TO HIGHLIGHT ──────────────────────────────────────────────────
  1. Total Revenue
  2. Month-over-Month Growth %
  3. Repeat Customer %
  4. Average Order Value

── CONDITIONAL FORMATTING ─────────────────────────────────────────────
  On KPI cards: Green if MoM growth > 0, Red if negative
  On matrix: Data bars for revenue column
"""


# ====================================================================
# 6. DASHBOARD 2: SALES DASHBOARD
# ====================================================================
"""
PURPOSE: Detailed sales performance analysis.
AUDIENCE: Sales Managers, Regional Managers

── LAYOUT ─────────────────────────────────────────────────────────────

Row 1 — KPI Cards:
  [Total Revenue]   [Completed Orders]   [Cancelled Orders %]   [Avg Discount %]

Row 2 — Visuals:
  Left:  Clustered Column Chart → Monthly Revenue by Year
  Right: Map Visual              → Revenue by State (bubble size = revenue)

Row 3 — Visuals:
  Left:  Stacked Bar Chart → Revenue by Category + Payment Method
  Right: Treemap           → Revenue by State

Row 4 — Table:
  Monthly sales table with columns:
  Month | Revenue | Orders | Unique Customers | MoM Growth %

── SLICERS ────────────────────────────────────────────────────────────
  - Date Range     (ORDERS[Order_Date])     → Date Range Picker
  - Region         (CUSTOMERS[Region])      → Tile slicer
  - Category       (PRODUCTS[Category])     → Dropdown
  - Payment Method (ORDERS[Payment_Method]) → Multi-select

── TOOLTIPS ───────────────────────────────────────────────────────────
  On map bubbles: Customer Count, Avg Order Value, Top Category
  On bar charts: MoM Growth %, YoY Growth %

── DRILL-THROUGH ──────────────────────────────────────────────────────
  From Region → State → City level
  Right-click a region bar → "See State Detail"
"""


# ====================================================================
# 7. DASHBOARD 3: CUSTOMER DASHBOARD
# ====================================================================
"""
PURPOSE: Customer behavior, segmentation, and loyalty analysis.
AUDIENCE: Marketing Team, CRM Team

── LAYOUT ─────────────────────────────────────────────────────────────

Row 1 — KPI Cards:
  [Total Customers]   [Active Customers]   [Repeat Customers]   [Repeat %]

Row 2 — Visuals:
  Left:  Donut Chart  → Customer Segments (Platinum/Gold/Silver/Bronze)
  Right: Bar Chart    → Top 10 Customers by Revenue

Row 3 — Visuals:
  Left:  Scatter Chart → Customer LTV vs Order Frequency
  Right: Map           → Customer Distribution by State

Row 4 — Table:
  Customer_Name | State | Total Orders | Total Spent | Segment | Last Order Date

── DAX FOR CUSTOMER SEGMENTATION ──────────────────────────────────────
  Customer Segment =
  SWITCH(
    TRUE(),
    [Customer LTV] >= 500000, "Platinum",
    [Customer LTV] >= 200000, "Gold",
    [Customer LTV] >= 50000,  "Silver",
    "Bronze"
  )

── SLICERS ────────────────────────────────────────────────────────────
  - Region         (CUSTOMERS[Region])   → Tile slicer (4 tiles)
  - State          (CUSTOMERS[State])    → Dropdown
  - Join Year      (CUSTOMERS[Join_Date])→ Year slider
  - Segment        → Dropdown

── DRILL-THROUGH ──────────────────────────────────────────────────────
  Target: Customer Detail Page
  Fields: Customer_ID, Customer_Name
  Show: Order history table, spending trend, category preferences

── BOOKMARKS ──────────────────────────────────────────────────────────
  [All Customers] → [Repeat Only] → [High Value Only]
  Create 3 bookmarks, wire to buttons for toggle
"""


# ====================================================================
# 8. DASHBOARD 4: PRODUCT DASHBOARD
# ====================================================================
"""
PURPOSE: Product performance, category analysis, brand comparison.
AUDIENCE: Merchandising Team, Category Managers

── LAYOUT ─────────────────────────────────────────────────────────────

Row 1 — KPI Cards:
  [Total Products]   [Total Units Sold]   [Top Category Revenue]   [Revenue per Unit]

Row 2 — Visuals:
  Left:  Horizontal Bar Chart → Top 15 Products by Revenue
  Right: Treemap              → Revenue by Category

Row 3 — Visuals:
  Left:  Donut Chart          → Revenue Contribution % by Category
  Right: Clustered Bar Chart  → Brand performance within selected category

Row 4 — Table:
  Product_Name | Category | Brand | Units Sold | Total Revenue | Revenue Rank

── SLICERS ────────────────────────────────────────────────────────────
  - Category       (PRODUCTS[Category]) → Multi-select chiclets
  - Brand          (PRODUCTS[Brand])    → Dropdown
  - Order Status   (ORDERS[Order_Status]) → Buttons

── DYNAMIC TITLE EXAMPLE ──────────────────────────────────────────────
  Title DAX:
  "Product Performance — " & [Selected Category]

  Creates: "Product Performance — Electronics"
           "Product Performance — All Categories"

── TOOLTIPS ───────────────────────────────────────────────────────────
  On product bar: Show listed price, avg discount, return rate

── DRILL-THROUGH ──────────────────────────────────────────────────────
  Target: Product Detail Page
  Show: Monthly sales trend, customer age groups, state-wise distribution
"""


# ====================================================================
# 9. KPI SUMMARY TABLE
# ====================================================================
"""
Dashboard    KPI                    Visual Type    DAX Measure
─────────────────────────────────────────────────────────────────────
Executive    Total Revenue          Card           Total Revenue
Executive    MoM Growth %           Card           MoM Revenue Growth %
Executive    Total Orders           Card           Total Orders
Executive    Avg Order Value        Card           Average Order Value
─────────────────────────────────────────────────────────────────────
Sales        Revenue by Region      Map            Total Revenue
Sales        Monthly Revenue        Line Chart     Total Revenue
Sales        Cancelled Order %      Card           (Cancelled / Total) %
Sales        Revenue by Category    Bar Chart      Total Revenue
─────────────────────────────────────────────────────────────────────
Customer     Repeat Customer %      Gauge          Repeat Customer %
Customer     Customer Segments      Donut          Count by Segment
Customer     Top 10 Customers       Bar Chart      Total Revenue
Customer     Customer LTV           Card           Customer Lifetime Value
─────────────────────────────────────────────────────────────────────
Product      Category Contribution  Treemap        Revenue Contribution %
Product      Top Products           Bar Chart      Total Revenue
Product      Units Sold             Card           Total Units Sold
Product      Revenue per Unit       Card           Revenue per Unit
─────────────────────────────────────────────────────────────────────
"""


# ====================================================================
# 10. NAVIGATION & BOOKMARKS
# ====================================================================
"""
Recommended Navigation Setup:

1. Create a top navigation bar on each dashboard with 4 buttons:
   [Executive] [Sales] [Customer] [Product]

2. Use Power BI Page Navigation action on each button.

3. Bookmarks for Customer Dashboard:
   - Bookmark "All Customers"       → Default view
   - Bookmark "Repeat Customers"    → Filter: Order Count > 1
   - Bookmark "Platinum Customers"  → Filter: Segment = Platinum

4. Slicers — Sync across pages:
   View → Sync Slicers → Enable Year and Region across all pages

5. Mobile Layout:
   View → Mobile Layout
   Prioritize KPI cards and top chart for mobile view
"""


# ====================================================================
# 11. BUSINESS INSIGHTS TO HIGHLIGHT ON DASHBOARDS
# ====================================================================
"""
Include text boxes on dashboards with pre-computed insights:

1. "Top 20% of customers contribute approximately 80% of total revenue."
2. "Electronics is the highest-revenue category, followed by Furniture."
3. "UPI is the most popular payment method among customers."
4. "Maharashtra and Delhi are the top 2 states by revenue."
5. "Sales peak in Q4 (Oct-Dec), dip in Q1 (Jan-Mar)."
6. "Repeat customers have 3x the Average Order Value of one-time buyers."
7. "The bottom 10 products contribute less than 2% of total revenue."
8. "North region has the highest customer density."

These can be calculated using the SQL analysis_queries.sql file
and embedded as text cards in the Power BI reports.
"""
