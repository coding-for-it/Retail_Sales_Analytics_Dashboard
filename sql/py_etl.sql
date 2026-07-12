-- =====================================================
-- Python + Snowflake ETL Pipeline Project
-- Flow:
-- CSV -> Stage -> Raw Table -> Task/Procedure -> Final Table -> Analytics
-- =====================================================



-- =====================================================
-- 1. Create Database and Schema
-- =====================================================

CREATE DATABASE ETL_DB;

USE DATABASE ETL_DB;


CREATE SCHEMA SALES_SCHEMA;


USE SCHEMA SALES_SCHEMA;



-- =====================================================
-- 2. Create Warehouse
-- Warehouse provides compute resources for queries/tasks
-- =====================================================

CREATE WAREHOUSE ETL_WH;



-- =====================================================
-- 3. Create Main Sales Table
-- Final business table for analytics
-- =====================================================

CREATE TABLE SALES
(

ORDER_ID INT,

CUSTOMER_NAME STRING,

PRODUCT STRING,

QUANTITY INT,

PRICE FLOAT,

ORDER_DATE DATE,

TOTAL_SALES FLOAT

);



SELECT *
FROM SALES;



-- =====================================================
-- 4. Create Internal Stage
-- Stage stores files before loading into Snowflake
-- =====================================================

CREATE OR REPLACE STAGE SALES_STAGE;


-- Check uploaded files

LIST @SALES_STAGE;



-- =====================================================
-- 5. Create Raw Table
-- Stores data exactly as received from CSV
-- =====================================================

CREATE OR REPLACE TABLE SALES_RAW
(

ORDER_ID INT,

CUSTOMER_NAME STRING,

PRODUCT STRING,

QUANTITY INT,

PRICE FLOAT,

ORDER_DATE DATE

);



-- =====================================================
-- 6. Load CSV data into Raw Table
-- COPY INTO loads staged file into Snowflake
-- =====================================================

COPY INTO SALES_RAW

FROM @SALES_STAGE/sales.csv

FILE_FORMAT =

(
TYPE='CSV',

SKIP_HEADER=1

);



SELECT *
FROM SALES_RAW;



-- =====================================================
-- 7. Create Final Clean Table
-- Stores transformed data with calculated revenue
-- =====================================================


CREATE OR REPLACE TABLE SALES_FINAL
(

ORDER_ID INT,

CUSTOMER_NAME STRING,

PRODUCT STRING,

QUANTITY INT,

PRICE FLOAT,

ORDER_DATE DATE,

TOTAL_SALES FLOAT

);



-- =====================================================
-- 8. Create Stored Procedure
-- Instead of manually writing transformation SQL,
-- procedure automates data transformation
-- =====================================================


CREATE OR REPLACE PROCEDURE LOAD_SALES()

RETURNS STRING

LANGUAGE SQL

AS

$$

BEGIN


INSERT INTO SALES_FINAL


SELECT


ORDER_ID,

CUSTOMER_NAME,

PRODUCT,

QUANTITY,

PRICE,

ORDER_DATE,


QUANTITY * PRICE AS TOTAL_SALES


FROM SALES_RAW;



RETURN 'DATA LOADED SUCCESSFULLY';



END;


$$;



-- Run procedure

CALL LOAD_SALES();



SELECT *
FROM SALES_FINAL;



-- =====================================================
-- 9. SQL Analytics
-- Business insights from processed data
-- =====================================================


-- Total Revenue

SELECT

SUM(TOTAL_SALES)

FROM SALES_FINAL;



-- Product wise sales ranking

SELECT


PRODUCT,

SUM(TOTAL_SALES)


FROM SALES_FINAL


GROUP BY PRODUCT


ORDER BY 2 DESC;



-- =====================================================
-- 10. Snowflake Task Automation
--
-- Problem:
-- Earlier we manually executed COPY INTO and procedure.
--
-- Solution:
-- Snowflake Task schedules execution automatically.
-- =====================================================



CREATE OR REPLACE TASK SALES_LOAD_TASK

WAREHOUSE = ETL_WH

SCHEDULE = '5 MINUTE'


AS


INSERT INTO SALES


SELECT


ORDER_ID,

CUSTOMER_NAME,

PRODUCT,

QUANTITY,

PRICE,

ORDER_DATE,


QUANTITY * PRICE


FROM SALES_RAW;



-- Enable task

ALTER TASK SALES_LOAD_TASK RESUME;



-- Check task status

SHOW TASKS;



-- For testing:
-- Manually trigger task instead of waiting 5 minutes

EXECUTE TASK SALES_LOAD_TASK;



SELECT *
FROM SALES_RAW;



SELECT *
FROM SALES_FINAL;



-- =====================================================
-- 11. Problem Faced During Testing:
--
-- Uploaded new sales.csv but old data was still visible.
--
-- Reason:
-- Snowflake keeps file load history and remembers files.
--
-- Solution:
-- Remove old staged file and force reload.
-- =====================================================



LIST @SALES_STAGE;



REMOVE @SALES_STAGE/sales.csv;



-- Clear previous test data

TRUNCATE TABLE SALES_RAW;


TRUNCATE TABLE SALES_FINAL;



-- Reload same file forcefully

COPY INTO SALES_RAW

FROM @SALES_STAGE/sales.csv


FILE_FORMAT =

(

TYPE='CSV',

SKIP_HEADER=1

)


FORCE=TRUE;



-- Verify new data

SELECT *

FROM SALES_RAW;



-- =====================================================
-- Final Architecture:
--
-- CSV File
--     |
--     v
-- Snowflake Stage
--     |
--     v
-- SALES_RAW
--     |
--     v
-- Stored Procedure / Task
--     |
--     v
-- SALES_FINAL
--     |
--     v
-- SQL Analytics
--
-- =====================================================