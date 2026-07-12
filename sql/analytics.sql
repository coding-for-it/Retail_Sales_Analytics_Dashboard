-- =====================================================
-- SALES ANALYTICS QUERIES
-- Table Used:
-- SALES_FINAL
--
-- Purpose:
-- Analyze business performance after ETL processing
-- =====================================================


USE DATABASE ETL_DB;

USE SCHEMA SALES_SCHEMA;



-- =====================================================
-- 1. View Complete Sales Data
-- =====================================================

SELECT *

FROM SALES_FINAL;



-- =====================================================
-- 2. Total Revenue Generated
-- Business Question:
-- What is the overall sales revenue?
-- =====================================================

SELECT

SUM(TOTAL_SALES) AS TOTAL_REVENUE


FROM SALES_FINAL;



-- =====================================================
-- 3. Total Number of Orders
-- Business Question:
-- How many orders were placed?
-- =====================================================

SELECT

COUNT(ORDER_ID) AS TOTAL_ORDERS


FROM SALES_FINAL;



-- =====================================================
-- 4. Average Order Value
-- Business Question:
-- What is the average revenue per order?
-- =====================================================

SELECT

AVG(TOTAL_SALES) AS AVG_ORDER_VALUE


FROM SALES_FINAL;



-- =====================================================
-- 5. Product Wise Revenue Analysis
-- Business Question:
-- Which products generate the highest revenue?
-- =====================================================

SELECT

PRODUCT,

SUM(TOTAL_SALES) AS REVENUE


FROM SALES_FINAL


GROUP BY PRODUCT


ORDER BY REVENUE DESC;



-- =====================================================
-- 6. Product Sales Ranking
-- Business Question:
-- Rank products based on revenue
-- =====================================================

SELECT


PRODUCT,


SUM(TOTAL_SALES) AS REVENUE,


RANK() OVER

(

ORDER BY SUM(TOTAL_SALES) DESC

)

AS PRODUCT_RANK


FROM SALES_FINAL


GROUP BY PRODUCT;



-- =====================================================
-- 7. Highest Selling Product
-- Business Question:
-- Which product generated maximum revenue?
-- =====================================================

SELECT


PRODUCT,

SUM(TOTAL_SALES) AS REVENUE


FROM SALES_FINAL


GROUP BY PRODUCT


ORDER BY REVENUE DESC


LIMIT 1;



-- =====================================================
-- 8. Customer Wise Spending Analysis
-- Business Question:
-- Which customers spent the most?
-- =====================================================

SELECT


CUSTOMER_NAME,


SUM(TOTAL_SALES) AS TOTAL_SPENT


FROM SALES_FINAL


GROUP BY CUSTOMER_NAME


ORDER BY TOTAL_SPENT DESC;



-- =====================================================
-- 9. Monthly Sales Trend
-- Business Question:
-- How does revenue change month wise?
-- =====================================================

SELECT


MONTH(ORDER_DATE) AS SALES_MONTH,


SUM(TOTAL_SALES) AS MONTHLY_REVENUE


FROM SALES_FINAL


GROUP BY MONTH(ORDER_DATE)


ORDER BY SALES_MONTH;



-- =====================================================
-- 10. Quantity Sold by Product
-- Business Question:
-- Which products have highest sales volume?
-- =====================================================

SELECT


PRODUCT,


SUM(QUANTITY) AS TOTAL_QUANTITY_SOLD


FROM SALES_FINAL


GROUP BY PRODUCT


ORDER BY TOTAL_QUANTITY_SOLD DESC;



-- =====================================================
-- 11. Expensive Orders
-- Business Question:
-- Find top 5 highest value orders
-- =====================================================

SELECT


ORDER_ID,

CUSTOMER_NAME,

PRODUCT,

TOTAL_SALES


FROM SALES_FINAL


ORDER BY TOTAL_SALES DESC


LIMIT 5;



-- =====================================================
-- 12. Customer Purchase Count
-- Business Question:
-- Which customers placed the most orders?
-- =====================================================

SELECT


CUSTOMER_NAME,


COUNT(ORDER_ID) AS NUMBER_OF_ORDERS


FROM SALES_FINAL


GROUP BY CUSTOMER_NAME


ORDER BY NUMBER_OF_ORDERS DESC;