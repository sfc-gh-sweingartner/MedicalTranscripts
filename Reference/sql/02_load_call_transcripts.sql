-- ============================================================================
-- Superannuation Transcripts Demo - Data Ingestion
-- ============================================================================
-- This script loads the call transcript JSON data into Snowflake
-- Run this after creating the database objects
-- ============================================================================

-- Set context
USE DATABASE SUPERANNUATION;
USE SCHEMA TRANSCRIPTS;
USE WAREHOUSE MYWH;

-- ============================================================================
-- Method 1: Load from Local File (for development/testing)
-- ============================================================================

-- Create a file format for JSON data
CREATE OR REPLACE FILE FORMAT JSON_FORMAT
TYPE = JSON
STRIP_OUTER_ARRAY = TRUE
COMMENT = 'File format for loading call transcript JSON data';

-- Load data from local file to stage
-- Note: This requires the file to be uploaded to the stage first
-- You can use SnowSQL or Snowflake web interface to upload the file

-- PUT command (run in SnowSQL with local file path)
-- PUT file:///Users/sweingartner/Cursor/SuperannuationTranscripts/call_transcripts.json @TRANSCRIPTS;

-- ============================================================================
-- Method 2: Load from Already Staged File
-- ============================================================================

-- Clear any existing data (for fresh demo runs)
DELETE FROM RAW_CALL_TRANSCRIPTS;

-- Load JSON data into the raw table
COPY INTO RAW_CALL_TRANSCRIPTS (
    CALL_ID,
    CUSTOMER_ID,
    AGENT_ID,
    CALL_TIMESTAMP,
    CALL_DURATION_SECONDS,
    TRANSCRIPT_TEXT
)
FROM (
    SELECT 
        $1:CALL_ID::VARCHAR(50) as CALL_ID,
        $1:CUSTOMER_ID::VARCHAR(50) as CUSTOMER_ID,
        $1:AGENT_ID::VARCHAR(50) as AGENT_ID,
        $1:CALL_TIMESTAMP::TIMESTAMP as CALL_TIMESTAMP,
        $1:CALL_DURATION_SECONDS::INTEGER as CALL_DURATION_SECONDS,
        $1:TRANSCRIPT_TEXT::TEXT as TRANSCRIPT_TEXT
    FROM @TRANSCRIPTS/call_transcripts.json
)
FILE_FORMAT = JSON_FORMAT
ON_ERROR = 'CONTINUE';

-- ============================================================================
-- Alternative Method: Create External Stage (if file is in cloud storage)
-- ============================================================================

-- If the file is stored in S3, Azure, or GCS, create an external stage
-- Example for S3 (uncomment and modify as needed):
/*
CREATE OR REPLACE STAGE EXTERNAL_TRANSCRIPTS
URL = 's3://your-bucket/path/to/files/'
CREDENTIALS = (AWS_KEY_ID = 'your-key' AWS_SECRET_KEY = 'your-secret')
FILE_FORMAT = JSON_FORMAT;

COPY INTO RAW_CALL_TRANSCRIPTS (
    CALL_ID,
    CUSTOMER_ID,
    AGENT_ID,
    CALL_TIMESTAMP,
    CALL_DURATION_SECONDS,
    TRANSCRIPT_TEXT
)
FROM @EXTERNAL_TRANSCRIPTS/call_transcripts.json
FILE_FORMAT = JSON_FORMAT;
*/

-- ============================================================================
-- Verification and Data Quality Checks
-- ============================================================================

-- Check how many records were loaded
SELECT COUNT(*) as TOTAL_RECORDS_LOADED FROM RAW_CALL_TRANSCRIPTS;

-- Check for any null or empty transcript texts
SELECT 
    COUNT(*) as TOTAL_RECORDS,
    COUNT(CASE WHEN TRANSCRIPT_TEXT IS NULL OR TRANSCRIPT_TEXT = '' THEN 1 END) as EMPTY_TRANSCRIPTS,
    COUNT(CASE WHEN LENGTH(TRANSCRIPT_TEXT) < 50 THEN 1 END) as SHORT_TRANSCRIPTS,
    AVG(LENGTH(TRANSCRIPT_TEXT)) as AVG_TRANSCRIPT_LENGTH,
    MIN(LENGTH(TRANSCRIPT_TEXT)) as MIN_TRANSCRIPT_LENGTH,
    MAX(LENGTH(TRANSCRIPT_TEXT)) as MAX_TRANSCRIPT_LENGTH
FROM RAW_CALL_TRANSCRIPTS;

-- Check data distribution by customer
SELECT 
    COUNT(DISTINCT CUSTOMER_ID) as UNIQUE_CUSTOMERS,
    COUNT(DISTINCT AGENT_ID) as UNIQUE_AGENTS,
    MIN(CALL_TIMESTAMP) as EARLIEST_CALL,
    MAX(CALL_TIMESTAMP) as LATEST_CALL
FROM RAW_CALL_TRANSCRIPTS;

-- Sample of loaded data
SELECT 
    CALL_ID,
    CUSTOMER_ID,
    AGENT_ID,
    CALL_TIMESTAMP,
    CALL_DURATION_SECONDS,
    LEFT(TRANSCRIPT_TEXT, 100) || '...' as TRANSCRIPT_SAMPLE
FROM RAW_CALL_TRANSCRIPTS
ORDER BY CALL_TIMESTAMP
LIMIT 5;

-- Check for duplicate call IDs
SELECT 
    CALL_ID,
    COUNT(*) as DUPLICATE_COUNT
FROM RAW_CALL_TRANSCRIPTS
GROUP BY CALL_ID
HAVING COUNT(*) > 1;

-- ============================================================================
-- Data Quality Validation
-- ============================================================================

-- Create a simple data quality report
CREATE OR REPLACE VIEW DATA_QUALITY_REPORT AS
SELECT 
    'RAW_CALL_TRANSCRIPTS' as TABLE_NAME,
    COUNT(*) as TOTAL_RECORDS,
    COUNT(CASE WHEN CALL_ID IS NULL THEN 1 END) as NULL_CALL_IDS,
    COUNT(CASE WHEN CUSTOMER_ID IS NULL THEN 1 END) as NULL_CUSTOMER_IDS,
    COUNT(CASE WHEN TRANSCRIPT_TEXT IS NULL OR TRANSCRIPT_TEXT = '' THEN 1 END) as NULL_TRANSCRIPTS,
    COUNT(CASE WHEN CALL_TIMESTAMP IS NULL THEN 1 END) as NULL_TIMESTAMPS,
    COUNT(CASE WHEN CALL_DURATION_SECONDS IS NULL OR CALL_DURATION_SECONDS <= 0 THEN 1 END) as INVALID_DURATIONS,
    CURRENT_TIMESTAMP() as CHECKED_AT
FROM RAW_CALL_TRANSCRIPTS;

-- View the data quality report
SELECT * FROM DATA_QUALITY_REPORT;

-- ============================================================================
-- Demo Data Enhancement Preparation
-- ============================================================================

-- Mark specific calls for demo scenarios (we'll update these with enhanced transcripts later)
-- This helps identify which calls to enhance for better demo experience

-- High churn risk scenario candidates
SELECT 
    CALL_ID,
    CUSTOMER_ID,
    LEFT(TRANSCRIPT_TEXT, 150) as TRANSCRIPT_PREVIEW,
    'Consider enhancing for HIGH CHURN scenario' as ENHANCEMENT_NOTE
FROM RAW_CALL_TRANSCRIPTS
WHERE CUSTOMER_ID IN ('CUST003', 'CUST010', 'CUST015', 'CUST020')
ORDER BY CALL_TIMESTAMP;

-- Upsell opportunity scenario candidates  
SELECT 
    CALL_ID,
    CUSTOMER_ID,
    LEFT(TRANSCRIPT_TEXT, 150) as TRANSCRIPT_PREVIEW,
    'Consider enhancing for UPSELL scenario' as ENHANCEMENT_NOTE
FROM RAW_CALL_TRANSCRIPTS
WHERE CUSTOMER_ID IN ('CUST004', 'CUST007', 'CUST012', 'CUST018')
ORDER BY CALL_TIMESTAMP;

-- Success message
SELECT 
    'Call transcript data loaded successfully!' as STATUS,
    COUNT(*) as TOTAL_RECORDS
FROM RAW_CALL_TRANSCRIPTS; 