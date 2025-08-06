-- ============================================================================
-- Superannuation Transcripts Demo - Database Objects Creation
-- ============================================================================
-- This script creates the base database, schema, and table structure
-- for the superannuation transcripts demo
-- ============================================================================

-- Create database and schema
CREATE DATABASE IF NOT EXISTS SUPERANNUATION;
USE DATABASE SUPERANNUATION;

CREATE SCHEMA IF NOT EXISTS TRANSCRIPTS;
USE SCHEMA TRANSCRIPTS;

-- Set warehouse
USE WAREHOUSE MYWH;

-- ============================================================================
-- Core Data Tables
-- ============================================================================

-- Raw call transcripts table
CREATE TABLE IF NOT EXISTS RAW_CALL_TRANSCRIPTS (
    CALL_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20) NOT NULL,
    AGENT_ID VARCHAR(20),
    CALL_TIMESTAMP TIMESTAMP_NTZ,
    CALL_DURATION_SECONDS INTEGER,
    TRANSCRIPT_TEXT TEXT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Customer master data table
CREATE TABLE IF NOT EXISTS CUSTOMER (
    CUSTOMER_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_NAME VARCHAR(100),
    AGE INTEGER,
    TENURE_YEARS INTEGER,
    ACCOUNT_BALANCE DECIMAL(15,2),
    INVESTMENT_OPTION VARCHAR(50),
    RECENT_TRANSACTIONS INTEGER,
    LAST_INTERACTION_DATE DATE,
    PRODUCT_HOLDINGS VARIANT,
    CONTACT_PREFERENCE VARCHAR(20),
    CALL_FREQUENCY_LAST_MONTH INTEGER,
    AVG_SENTIMENT_LAST_3_CALLS DECIMAL(5,2),
    NUM_NEGATIVE_CALLS_LAST_6_MONTHS INTEGER,
    HAS_CHURN_INTENT_LAST_MONTH BOOLEAN,
    CHURN_RISK_SCORE VARCHAR(10),
    CHURN_PROBABILITY DECIMAL(5,2),
    NEXT_BEST_ACTION TEXT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Enriched transcripts table (AI-processed data)
CREATE TABLE IF NOT EXISTS ENRICHED_TRANSCRIPTS_ALL (
    CALL_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20) NOT NULL,
    CALL_TIMESTAMP TIMESTAMP_NTZ,
    SENTIMENT_SCORE DECIMAL(5,2),
    SENTIMENT_LABEL VARCHAR(20),
    PRIMARY_INTENT VARCHAR(50),
    CALL_SUMMARY TEXT,
    NEXT_BEST_ACTION TEXT,
    CHURN_RISK_SCORE VARCHAR(10),
    CHURN_PROBABILITY DECIMAL(5,2),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMER(CUSTOMER_ID)
);

-- ============================================================================
-- Business Intelligence Tables
-- ============================================================================

-- Customer 360 view table
CREATE TABLE IF NOT EXISTS CUSTOMER_360_VIEW (
    CUSTOMER_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_NAME VARCHAR(100),
    AGE INTEGER,
    TENURE_YEARS INTEGER,
    ACCOUNT_BALANCE DECIMAL(15,2),
    INVESTMENT_OPTION VARCHAR(50),
    RECENT_CALL_COUNT INTEGER,
    LAST_CALL_DATE DATE,
    AVG_SENTIMENT_SCORE DECIMAL(5,2),
    PRIMARY_INTENT VARCHAR(50),
    CHURN_RISK_SCORE VARCHAR(10),
    CHURN_PROBABILITY DECIMAL(5,2),
    NEXT_BEST_ACTION TEXT,
    PRODUCT_HOLDINGS VARIANT,
    CONTACT_PREFERENCE VARCHAR(20),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Customer analytics table
CREATE TABLE IF NOT EXISTS CUSTOMER_ANALYTICS (
    CUSTOMER_ID VARCHAR(20) PRIMARY KEY,
    TOTAL_CALLS INTEGER,
    AVG_CALL_DURATION INTEGER,
    AVG_SENTIMENT_SCORE DECIMAL(5,2),
    COMPLAINT_COUNT INTEGER,
    UPSELL_OPPORTUNITIES INTEGER,
    CHURN_RISK_SCORE VARCHAR(10),
    CHURN_PROBABILITY DECIMAL(5,2),
    LAST_UPDATED TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Manager dashboard metrics table
CREATE TABLE IF NOT EXISTS DASHBOARD_METRICS (
    METRIC_DATE DATE PRIMARY KEY,
    TOTAL_CALLS INTEGER,
    TOTAL_CUSTOMERS INTEGER,
    AVG_SENTIMENT_SCORE DECIMAL(5,2),
    HIGH_CHURN_CUSTOMERS INTEGER,
    MEDIUM_CHURN_CUSTOMERS INTEGER,
    LOW_CHURN_CUSTOMERS INTEGER,
    COMPLAINT_CALLS INTEGER,
    UPSELL_OPPORTUNITIES INTEGER,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- Performance Optimization
-- ============================================================================

-- Add clustering keys for better performance
ALTER TABLE RAW_CALL_TRANSCRIPTS CLUSTER BY (CUSTOMER_ID, CALL_TIMESTAMP);
ALTER TABLE CUSTOMER CLUSTER BY (CUSTOMER_ID);
ALTER TABLE ENRICHED_TRANSCRIPTS_ALL CLUSTER BY (CUSTOMER_ID);
ALTER TABLE CUSTOMER_360_VIEW CLUSTER BY (CUSTOMER_ID);
ALTER TABLE CUSTOMER_ANALYTICS CLUSTER BY (CUSTOMER_ID);
ALTER TABLE DASHBOARD_METRICS CLUSTER BY (METRIC_DATE);

-- ============================================================================
-- Validation
-- ============================================================================

-- Show created tables
SHOW TABLES;

-- Display table structure summary
SELECT 
    'Database objects created successfully!' as STATUS,
    COUNT(*) as TOTAL_TABLES
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'TRANSCRIPTS';

-- ============================================================================
-- Data Ingestion Stage
-- ============================================================================

-- Create internal stage for data loading
CREATE STAGE IF NOT EXISTS TRANSCRIPTS
    FILE_FORMAT = (
        TYPE = 'JSON'
        STRIP_OUTER_ARRAY = TRUE
        DATE_FORMAT = 'AUTO'
        TIMESTAMP_FORMAT = 'AUTO'
    )
    COMMENT = 'Stage for loading call transcript JSON files';

-- Display stage information
DESCRIBE STAGE TRANSCRIPTS; 