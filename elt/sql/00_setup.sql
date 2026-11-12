-- =====================================================================
-- SQL_00_SETUP: warehouse, database, schemas, stage, empty tables, seed tables.
-- Safe to re-run: everything is IF NOT EXISTS, except the two small seed tables.
--
-- Part 1 (up to the first SELECT): the infrastructure statements already run and verified
--   in Snowflake by the student (database FRESHCART_DB instead of the reference's FRESHCART).
--   DIM and REF schemas added because the FreshCart SQL needs them.
-- Part 2: the remainder of the reference notebook's SQL_00_SETUP, unchanged
--   (file format, stage, bronze/ref/quarantine/gold tables).
-- =====================================================================
USE ROLE ACCOUNTADMIN;

CREATE WAREHOUSE IF NOT EXISTS FRESHCART_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS FRESHCART_DB;

CREATE SCHEMA IF NOT EXISTS FRESHCART_DB.BRONZE;      -- raw API responses, unchanged
CREATE SCHEMA IF NOT EXISTS FRESHCART_DB.SILVER;      -- cleaned, typed, deduplicated
CREATE SCHEMA IF NOT EXISTS FRESHCART_DB.DIM;         -- dimensions (customers)
CREATE SCHEMA IF NOT EXISTS FRESHCART_DB.REF;         -- reference data (fx, pincodes, tiers)
CREATE SCHEMA IF NOT EXISTS FRESHCART_DB.GOLD;        -- business-ready tables
CREATE SCHEMA IF NOT EXISTS FRESHCART_DB.QUARANTINE;  -- rows that failed validation

USE WAREHOUSE FRESHCART_WH;
USE DATABASE FRESHCART_DB;

SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_ROLE();

-- Landing area inside Snowflake for the files Python uploads
CREATE FILE FORMAT IF NOT EXISTS bronze.ff_ndjson TYPE = JSON COMPRESSION = AUTO;
CREATE STAGE IF NOT EXISTS bronze.landing FILE_FORMAT = bronze.ff_ndjson;

-- ---------- BRONZE: one table per source, raw JSON in a VARIANT column ----------
CREATE TABLE IF NOT EXISTS bronze.orders_raw (
  ingest_seq   NUMBER AUTOINCREMENT START 1 INCREMENT 1 ORDER,   -- arrival order
  source       STRING,          -- 'web' or 'mobile'
  raw          VARIANT,         -- the API record exactly as received
  run_id       STRING,
  extracted_at TIMESTAMP_TZ,
  src_file     STRING,
  src_row      NUMBER,
  loaded_at    TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
CREATE TABLE IF NOT EXISTS bronze.customers_raw (
  ingest_seq NUMBER AUTOINCREMENT START 1 INCREMENT 1 ORDER, source STRING, raw VARIANT,
  run_id STRING, extracted_at TIMESTAMP_TZ, src_file STRING, src_row NUMBER,
  loaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
CREATE TABLE IF NOT EXISTS bronze.fx_raw (
  ingest_seq NUMBER AUTOINCREMENT START 1 INCREMENT 1 ORDER, source STRING, raw VARIANT,
  run_id STRING, extracted_at TIMESTAMP_TZ, src_file STRING, src_row NUMBER,
  loaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
CREATE TABLE IF NOT EXISTS bronze.pincode_raw (
  ingest_seq NUMBER AUTOINCREMENT START 1 INCREMENT 1 ORDER, source STRING, raw VARIANT,
  run_id STRING, extracted_at TIMESTAMP_TZ, src_file STRING, src_row NUMBER,
  loaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ---------- REF: small hand-maintained seed tables ----------
CREATE OR REPLACE TABLE ref.tier_multiplier AS
SELECT * FROM VALUES ('Silver', 1), ('Gold', 2), ('Platinum', 3) AS v(tier, multiplier);

CREATE OR REPLACE TABLE ref.state_region AS
SELECT * FROM VALUES
  ('Tamil Nadu','South'), ('Karnataka','South'), ('Kerala','South'), ('Andhra Pradesh','South'),
  ('Telangana','South'), ('Puducherry','South'),
  ('Maharashtra','West'), ('Gujarat','West'), ('Goa','West'), ('Rajasthan','West'),
  ('Delhi','North'), ('Haryana','North'), ('Punjab','North'), ('Uttar Pradesh','North'),
  ('Himachal Pradesh','North'), ('Jammu and Kashmir','North'), ('Uttarakhand','North'),
  ('West Bengal','East'), ('Odisha','East'), ('Bihar','East'), ('Jharkhand','East'), ('Assam','East'),
  ('Madhya Pradesh','Central'), ('Chhattisgarh','Central')
  AS v(state, region);

-- Filled incrementally from the India Post API (see SQL_32_PINCODE_GEO)
CREATE TABLE IF NOT EXISTS ref.pincode_geo (
  pincode STRING PRIMARY KEY, city STRING, state STRING, region STRING,
  updated_at TIMESTAMP_LTZ
);

-- ---------- QUARANTINE, GOLD ----------
CREATE TABLE IF NOT EXISTS quarantine.orders (
  run_id STRING, quarantined_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
  ingest_seq NUMBER, source STRING, order_id STRING, reasons ARRAY, row_data VARIANT
);

CREATE TABLE IF NOT EXISTS gold.fct_orders (
  order_id STRING PRIMARY KEY, order_date DATE, cust_id STRING, email STRING,
  tier STRING, multiplier NUMBER, amount NUMBER(12,2), currency STRING,
  fx_rate NUMBER(12,4), amount_inr NUMBER(14,2), loyalty_points NUMBER,
  is_high_value BOOLEAN, city STRING, state STRING, region STRING,
  updated_at TIMESTAMP_NTZ, row_hash NUMBER, published_at TIMESTAMP_LTZ
);
