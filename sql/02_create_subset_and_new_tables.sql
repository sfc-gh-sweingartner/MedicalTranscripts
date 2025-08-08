-- Healthcare AI Demo - Patient Subset and Additional Tables
-- This script creates the patient subset table and additional analysis tables
-- Author: Snowflake Sales Engineering
-- Date: Created for Phase 3 development

USE DATABASE HEALTHCARE_DEMO;
USE SCHEMA MEDICAL_NOTES;

-- Create patient subset table with cleaned age data
CREATE OR REPLACE TABLE PATIENT_SUBSET (
    PATIENT_ID NUMBER PRIMARY KEY,
    PATIENT_UID VARCHAR,
    PATIENT_TITLE TEXT,
    PATIENT_NOTES TEXT,
    AGE_YEARS NUMBER(5,2), -- Cleaned age in decimal years (e.g., 12.5)
    AGE_ORIGINAL VARCHAR, -- Original age string for reference
    GENDER VARCHAR,
    SIMILAR_PATIENTS VARIANT,
    RELEVANT_ARTICLES VARIANT,
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Subset of 1,000 patients for development and demonstration with cleaned age data';

-- Populate patient subset with age cleaning
INSERT INTO PATIENT_SUBSET
WITH age_parsed AS (
    SELECT 
        PATIENT_ID,
        PATIENT_UID,
        PATIENT_TITLE,
        PATIENT_NOTES,
        AGE,
        GENDER,
        SIMILAR_PATIENTS,
        RELEVANT_ARTICLES,
        -- Parse age from various formats
        CASE 
            -- Handle "X [years] Y [months]" format
            WHEN AGE LIKE '%[years]%[months]%' THEN
                TRY_CAST(REGEXP_SUBSTR(AGE, '(\\d+)\\s*\\[years\\]', 1, 1, 'e', 1) AS NUMBER) +
                (TRY_CAST(REGEXP_SUBSTR(AGE, '(\\d+)\\s*\\[months\\]', 1, 1, 'e', 1) AS NUMBER) / 12.0)
            -- Handle "X [years]" format
            WHEN AGE LIKE '%[years]%' THEN
                TRY_CAST(REGEXP_SUBSTR(AGE, '(\\d+)\\s*\\[years\\]', 1, 1, 'e', 1) AS NUMBER)
            -- Handle "X [months]" format (convert to years)
            WHEN AGE LIKE '%[months]%' THEN
                TRY_CAST(REGEXP_SUBSTR(AGE, '(\\d+)\\s*\\[months\\]', 1, 1, 'e', 1) AS NUMBER) / 12.0
            -- Handle "X [days]" format (convert to years)
            WHEN AGE LIKE '%[days]%' THEN
                TRY_CAST(REGEXP_SUBSTR(AGE, '(\\d+)\\s*\\[days\\]', 1, 1, 'e', 1) AS NUMBER) / 365.25
            -- Try to extract any number
            ELSE TRY_CAST(REGEXP_SUBSTR(AGE, '(\\d+)', 1, 1, 'e', 1) AS NUMBER)
        END AS AGE_YEARS_PARSED
    FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
    WHERE PATIENT_NOTES IS NOT NULL 
        AND LENGTH(PATIENT_NOTES) > 100
    LIMIT 1000
)
SELECT 
    PATIENT_ID,
    PATIENT_UID,
    PATIENT_TITLE,
    PATIENT_NOTES,
    ROUND(AGE_YEARS_PARSED, 2) AS AGE_YEARS,
    AGE AS AGE_ORIGINAL,
    GENDER,
    SIMILAR_PATIENTS,
    RELEVANT_ARTICLES,
    CURRENT_TIMESTAMP() AS CREATED_DATE
FROM age_parsed
WHERE AGE_YEARS_PARSED IS NOT NULL;

-- Drug safety analysis table
CREATE OR REPLACE TABLE MEDICATION_ANALYSIS (
    PATIENT_ID NUMBER PRIMARY KEY,
    EXTRACTED_MEDICATIONS VARIANT, -- Array of {name, dosage, frequency, route}
    DRUG_INTERACTIONS VARIANT, -- Array of {drug1, drug2, severity, description}
    CONTRAINDICATIONS VARIANT, -- Array of {medication, condition, risk_level}
    POLYPHARMACY_RISK_SCORE NUMBER, -- Risk score based on number and types of meds
    ANALYSIS_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Medication extraction and safety analysis results';

-- Cost analysis table
CREATE OR REPLACE TABLE COST_ANALYSIS (
    PATIENT_ID NUMBER PRIMARY KEY,
    EXTRACTED_PROCEDURES VARIANT, -- Array of {procedure, CPT_code, estimated_cost}
    EXTRACTED_CONDITIONS VARIANT, -- Array of {condition, ICD10_code, cost_impact}
    HIGH_COST_INDICATORS VARIANT, -- ICU, surgery, complications, etc.
    ESTIMATED_ENCOUNTER_COST NUMBER(10,2),
    COST_CATEGORY VARCHAR, -- 'low', 'medium', 'high', 'very_high'
    COST_DRIVERS TEXT, -- Narrative explanation
    ANALYSIS_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Cost analysis based on extracted procedures and conditions';

-- Procedure cost reference table
CREATE OR REPLACE TABLE PROCEDURE_COSTS (
    PROCEDURE_NAME VARCHAR,
    CPT_CODE VARCHAR,
    ESTIMATED_COST NUMBER(10,2),
    COST_RANGE_LOW NUMBER(10,2),
    COST_RANGE_HIGH NUMBER(10,2),
    CATEGORY VARCHAR,
    PRIMARY KEY (PROCEDURE_NAME, CPT_CODE)
) COMMENT = 'Reference table for procedure cost estimates';

-- Insert common procedure costs (sample data)
INSERT INTO PROCEDURE_COSTS (PROCEDURE_NAME, CPT_CODE, ESTIMATED_COST, COST_RANGE_LOW, COST_RANGE_HIGH, CATEGORY)
VALUES 
    -- Imaging procedures
    ('MRI Brain without contrast', '70551', 1500.00, 800.00, 3000.00, 'Imaging'),
    ('MRI Brain with contrast', '70552', 2000.00, 1200.00, 3500.00, 'Imaging'),
    ('CT Head without contrast', '70450', 825.00, 500.00, 1500.00, 'Imaging'),
    ('CT Chest with contrast', '71260', 1200.00, 700.00, 2000.00, 'Imaging'),
    ('X-ray Chest', '71045', 150.00, 100.00, 300.00, 'Imaging'),
    ('Echocardiogram', '93306', 800.00, 500.00, 1500.00, 'Imaging'),
    
    -- Laboratory tests
    ('Complete Blood Count', '85025', 30.00, 20.00, 50.00, 'Laboratory'),
    ('Comprehensive Metabolic Panel', '80053', 50.00, 30.00, 80.00, 'Laboratory'),
    ('Lipid Panel', '80061', 75.00, 50.00, 120.00, 'Laboratory'),
    ('Hemoglobin A1C', '83036', 60.00, 40.00, 100.00, 'Laboratory'),
    ('Thyroid Function Tests', '84443', 85.00, 60.00, 150.00, 'Laboratory'),
    
    -- Procedures
    ('Colonoscopy', '45380', 1800.00, 1200.00, 3000.00, 'Procedure'),
    ('Upper Endoscopy', '43235', 1500.00, 1000.00, 2500.00, 'Procedure'),
    ('Cardiac Catheterization', '93458', 5000.00, 3000.00, 8000.00, 'Procedure'),
    ('Bronchoscopy', '31622', 2500.00, 1500.00, 4000.00, 'Procedure'),
    
    -- Surgery
    ('Appendectomy', '44970', 15000.00, 10000.00, 25000.00, 'Surgery'),
    ('Cholecystectomy', '47562', 20000.00, 15000.00, 30000.00, 'Surgery'),
    ('Total Knee Replacement', '27447', 35000.00, 25000.00, 50000.00, 'Surgery'),
    ('Coronary Artery Bypass', '33533', 75000.00, 50000.00, 120000.00, 'Surgery'),
    
    -- ICU/Critical Care
    ('ICU per day', '99291', 3500.00, 2500.00, 5000.00, 'Critical Care'),
    ('Ventilator per day', '94002', 1500.00, 1000.00, 2500.00, 'Critical Care'),
    ('Dialysis session', '90935', 500.00, 350.00, 800.00, 'Critical Care');

-- Common drug interactions reference table
CREATE OR REPLACE TABLE DRUG_INTERACTIONS_REFERENCE (
    DRUG1 VARCHAR,
    DRUG2 VARCHAR,
    SEVERITY VARCHAR, -- 'MAJOR', 'MODERATE', 'MINOR'
    DESCRIPTION TEXT,
    PRIMARY KEY (DRUG1, DRUG2)
) COMMENT = 'Reference table for known drug interactions';

-- Insert common drug interactions
INSERT INTO DRUG_INTERACTIONS_REFERENCE (DRUG1, DRUG2, SEVERITY, DESCRIPTION)
VALUES 
    ('Warfarin', 'Aspirin', 'MAJOR', 'Increased risk of bleeding'),
    ('Warfarin', 'Amiodarone', 'MAJOR', 'Increased INR and bleeding risk'),
    ('Metformin', 'Contrast dye', 'MAJOR', 'Risk of lactic acidosis'),
    ('ACE inhibitors', 'Potassium supplements', 'MODERATE', 'Risk of hyperkalemia'),
    ('Statins', 'Clarithromycin', 'MAJOR', 'Increased risk of rhabdomyolysis'),
    ('SSRIs', 'NSAIDs', 'MODERATE', 'Increased risk of GI bleeding'),
    ('Digoxin', 'Amiodarone', 'MAJOR', 'Digoxin toxicity risk'),
    ('Methotrexate', 'NSAIDs', 'MAJOR', 'Increased methotrexate toxicity');

-- Enable change tracking on new table for Cortex Search
ALTER TABLE PATIENT_SUBSET SET CHANGE_TRACKING = TRUE;

-- Drop the existing Cortex Search service
DROP CORTEX SEARCH SERVICE IF EXISTS patient_search_service;

-- Create new Cortex Search service on subset
CREATE OR REPLACE CORTEX SEARCH SERVICE patient_search_service
    ON PATIENT_SUBSET
    ATTRIBUTES PATIENT_ID, PATIENT_UID, PATIENT_TITLE, AGE_YEARS, GENDER
    WAREHOUSE = CORTEX_SEARCH_WH
    TARGET_LAG = '1 hour'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT
            PATIENT_NOTES,
            PATIENT_ID,
            PATIENT_UID, 
            PATIENT_TITLE,
            AGE_YEARS,
            GENDER
        FROM HEALTHCARE_DEMO.MEDICAL_NOTES.PATIENT_SUBSET
        WHERE PATIENT_NOTES IS NOT NULL
            AND LENGTH(PATIENT_NOTES) > 50
    );

-- Verify the data
SELECT 
    COUNT(*) as total_patients,
    AVG(AGE_YEARS) as avg_age,
    MIN(AGE_YEARS) as min_age,
    MAX(AGE_YEARS) as max_age,
    COUNT(DISTINCT GENDER) as gender_count
FROM PATIENT_SUBSET;

-- Show sample of cleaned age data
SELECT 
    PATIENT_ID,
    AGE_ORIGINAL,
    AGE_YEARS,
    PATIENT_TITLE
FROM PATIENT_SUBSET
WHERE AGE_ORIGINAL LIKE '%months%' OR AGE_ORIGINAL LIKE '%days%'
LIMIT 10;

-- Display confirmation
SELECT 'Patient subset created with ' || COUNT(*) || ' records and Cortex Search service updated' as STATUS
FROM PATIENT_SUBSET;