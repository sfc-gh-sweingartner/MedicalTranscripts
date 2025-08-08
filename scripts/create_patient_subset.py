"""
Create patient subset table with cleaned age data and additional analysis tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connection_helper import get_snowflake_connection, execute_query
import time

def main():
    print("="*60)
    print("Creating Patient Subset and Additional Tables")
    print("="*60)
    
    conn = get_snowflake_connection()
    if not conn:
        print("Failed to connect to Snowflake")
        return
    
    cursor = conn.cursor()
    
    try:
        # Use database and schema
        print("Setting database context...")
        cursor.execute("USE DATABASE HEALTHCARE_DEMO")
        cursor.execute("USE SCHEMA MEDICAL_NOTES")
        
        # Create patient subset table
        print("\nCreating PATIENT_SUBSET table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE PATIENT_SUBSET (
                PATIENT_ID NUMBER PRIMARY KEY,
                PATIENT_UID VARCHAR,
                PATIENT_TITLE TEXT,
                PATIENT_NOTES TEXT,
                AGE_YEARS NUMBER(5,2),
                AGE_ORIGINAL VARCHAR,
                GENDER VARCHAR,
                SIMILAR_PATIENTS VARIANT,
                RELEVANT_ARTICLES VARIANT,
                CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            ) COMMENT = 'Subset of 1,000 patients for development and demonstration with cleaned age data'
        """)
        print("✓ PATIENT_SUBSET table created")
        
        # Populate patient subset with age cleaning
        print("\nPopulating PATIENT_SUBSET with cleaned age data...")
        cursor.execute("""
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
                            TRY_CAST(REGEXP_SUBSTR(AGE, '(\\\\d+)\\\\s*\\\\[years\\\\]', 1, 1, 'e', 1) AS NUMBER) +
                            (TRY_CAST(REGEXP_SUBSTR(AGE, '(\\\\d+)\\\\s*\\\\[months\\\\]', 1, 1, 'e', 1) AS NUMBER) / 12.0)
                        -- Handle "X [years]" format
                        WHEN AGE LIKE '%[years]%' THEN
                            TRY_CAST(REGEXP_SUBSTR(AGE, '(\\\\d+)\\\\s*\\\\[years\\\\]', 1, 1, 'e', 1) AS NUMBER)
                        -- Handle "X [months]" format (convert to years)
                        WHEN AGE LIKE '%[months]%' THEN
                            TRY_CAST(REGEXP_SUBSTR(AGE, '(\\\\d+)\\\\s*\\\\[months\\\\]', 1, 1, 'e', 1) AS NUMBER) / 12.0
                        -- Handle "X [days]" format (convert to years)
                        WHEN AGE LIKE '%[days]%' THEN
                            TRY_CAST(REGEXP_SUBSTR(AGE, '(\\\\d+)\\\\s*\\\\[days\\\\]', 1, 1, 'e', 1) AS NUMBER) / 365.25
                        -- Try to extract any number
                        ELSE TRY_CAST(REGEXP_SUBSTR(AGE, '(\\\\d+)', 1, 1, 'e', 1) AS NUMBER)
                    END AS AGE_YEARS_PARSED
                FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
                WHERE PATIENT_NOTES IS NOT NULL 
                    AND LENGTH(PATIENT_NOTES) > 100
                ORDER BY PATIENT_ID
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
                TRY_PARSE_JSON(SIMILAR_PATIENTS) AS SIMILAR_PATIENTS,
                TRY_PARSE_JSON(RELEVANT_ARTICLES) AS RELEVANT_ARTICLES,
                CURRENT_TIMESTAMP() AS CREATED_DATE
            FROM age_parsed
            WHERE AGE_YEARS_PARSED IS NOT NULL
        """)
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM PATIENT_SUBSET")
        count = cursor.fetchone()[0]
        print(f"✓ Populated PATIENT_SUBSET with {count} records")
        
        # Create medication analysis table
        print("\nCreating MEDICATION_ANALYSIS table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE MEDICATION_ANALYSIS (
                PATIENT_ID NUMBER PRIMARY KEY,
                EXTRACTED_MEDICATIONS VARIANT,
                DRUG_INTERACTIONS VARIANT,
                CONTRAINDICATIONS VARIANT,
                POLYPHARMACY_RISK_SCORE NUMBER,
                ANALYSIS_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            ) COMMENT = 'Medication extraction and safety analysis results'
        """)
        print("✓ MEDICATION_ANALYSIS table created")
        
        # Create cost analysis table
        print("\nCreating COST_ANALYSIS table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE COST_ANALYSIS (
                PATIENT_ID NUMBER PRIMARY KEY,
                EXTRACTED_PROCEDURES VARIANT,
                EXTRACTED_CONDITIONS VARIANT,
                HIGH_COST_INDICATORS VARIANT,
                ESTIMATED_ENCOUNTER_COST NUMBER(10,2),
                COST_CATEGORY VARCHAR,
                COST_DRIVERS TEXT,
                ANALYSIS_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            ) COMMENT = 'Cost analysis based on extracted procedures and conditions'
        """)
        print("✓ COST_ANALYSIS table created")
        
        # Create procedure costs reference table
        print("\nCreating PROCEDURE_COSTS reference table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE PROCEDURE_COSTS (
                PROCEDURE_NAME VARCHAR,
                CPT_CODE VARCHAR,
                ESTIMATED_COST NUMBER(10,2),
                COST_RANGE_LOW NUMBER(10,2),
                COST_RANGE_HIGH NUMBER(10,2),
                CATEGORY VARCHAR,
                PRIMARY KEY (PROCEDURE_NAME, CPT_CODE)
            ) COMMENT = 'Reference table for procedure cost estimates'
        """)
        print("✓ PROCEDURE_COSTS table created")
        
        # Insert procedure costs
        print("\nPopulating PROCEDURE_COSTS reference data...")
        procedure_costs = [
            # Imaging procedures
            ('MRI Brain without contrast', '70551', 1500.00, 800.00, 3000.00, 'Imaging'),
            ('MRI Brain with contrast', '70552', 2000.00, 1200.00, 3500.00, 'Imaging'),
            ('CT Head without contrast', '70450', 825.00, 500.00, 1500.00, 'Imaging'),
            ('CT Chest with contrast', '71260', 1200.00, 700.00, 2000.00, 'Imaging'),
            ('X-ray Chest', '71045', 150.00, 100.00, 300.00, 'Imaging'),
            ('Echocardiogram', '93306', 800.00, 500.00, 1500.00, 'Imaging'),
            # Laboratory tests
            ('Complete Blood Count', '85025', 30.00, 20.00, 50.00, 'Laboratory'),
            ('Comprehensive Metabolic Panel', '80053', 50.00, 30.00, 80.00, 'Laboratory'),
            ('Lipid Panel', '80061', 75.00, 50.00, 120.00, 'Laboratory'),
            ('Hemoglobin A1C', '83036', 60.00, 40.00, 100.00, 'Laboratory'),
            ('Thyroid Function Tests', '84443', 85.00, 60.00, 150.00, 'Laboratory'),
            # Procedures
            ('Colonoscopy', '45380', 1800.00, 1200.00, 3000.00, 'Procedure'),
            ('Upper Endoscopy', '43235', 1500.00, 1000.00, 2500.00, 'Procedure'),
            ('Cardiac Catheterization', '93458', 5000.00, 3000.00, 8000.00, 'Procedure'),
            ('Bronchoscopy', '31622', 2500.00, 1500.00, 4000.00, 'Procedure'),
            # Surgery
            ('Appendectomy', '44970', 15000.00, 10000.00, 25000.00, 'Surgery'),
            ('Cholecystectomy', '47562', 20000.00, 15000.00, 30000.00, 'Surgery'),
            ('Total Knee Replacement', '27447', 35000.00, 25000.00, 50000.00, 'Surgery'),
            ('Coronary Artery Bypass', '33533', 75000.00, 50000.00, 120000.00, 'Surgery'),
            # ICU/Critical Care
            ('ICU per day', '99291', 3500.00, 2500.00, 5000.00, 'Critical Care'),
            ('Ventilator per day', '94002', 1500.00, 1000.00, 2500.00, 'Critical Care'),
            ('Dialysis session', '90935', 500.00, 350.00, 800.00, 'Critical Care')
        ]
        
        for proc in procedure_costs:
            cursor.execute("""
                INSERT INTO PROCEDURE_COSTS 
                (PROCEDURE_NAME, CPT_CODE, ESTIMATED_COST, COST_RANGE_LOW, COST_RANGE_HIGH, CATEGORY)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, proc)
        
        print(f"✓ Inserted {len(procedure_costs)} procedure cost records")
        
        # Create drug interactions reference table
        print("\nCreating DRUG_INTERACTIONS_REFERENCE table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE DRUG_INTERACTIONS_REFERENCE (
                DRUG1 VARCHAR,
                DRUG2 VARCHAR,
                SEVERITY VARCHAR,
                DESCRIPTION TEXT,
                PRIMARY KEY (DRUG1, DRUG2)
            ) COMMENT = 'Reference table for known drug interactions'
        """)
        print("✓ DRUG_INTERACTIONS_REFERENCE table created")
        
        # Insert drug interactions
        print("\nPopulating DRUG_INTERACTIONS_REFERENCE...")
        drug_interactions = [
            ('Warfarin', 'Aspirin', 'MAJOR', 'Increased risk of bleeding'),
            ('Warfarin', 'Amiodarone', 'MAJOR', 'Increased INR and bleeding risk'),
            ('Metformin', 'Contrast dye', 'MAJOR', 'Risk of lactic acidosis'),
            ('ACE inhibitors', 'Potassium supplements', 'MODERATE', 'Risk of hyperkalemia'),
            ('Statins', 'Clarithromycin', 'MAJOR', 'Increased risk of rhabdomyolysis'),
            ('SSRIs', 'NSAIDs', 'MODERATE', 'Increased risk of GI bleeding'),
            ('Digoxin', 'Amiodarone', 'MAJOR', 'Digoxin toxicity risk'),
            ('Methotrexate', 'NSAIDs', 'MAJOR', 'Increased methotrexate toxicity')
        ]
        
        for interaction in drug_interactions:
            cursor.execute("""
                INSERT INTO DRUG_INTERACTIONS_REFERENCE 
                (DRUG1, DRUG2, SEVERITY, DESCRIPTION)
                VALUES (%s, %s, %s, %s)
            """, interaction)
        
        print(f"✓ Inserted {len(drug_interactions)} drug interaction records")
        
        # Enable change tracking
        print("\nEnabling change tracking on PATIENT_SUBSET...")
        cursor.execute("ALTER TABLE PATIENT_SUBSET SET CHANGE_TRACKING = TRUE")
        print("✓ Change tracking enabled")
        
        # Drop existing Cortex Search service
        print("\nDropping existing Cortex Search service...")
        cursor.execute("DROP CORTEX SEARCH SERVICE IF EXISTS patient_search_service")
        print("✓ Existing service dropped")
        
        # Wait a moment before recreating
        time.sleep(2)
        
        # Create new Cortex Search service
        print("\nCreating new Cortex Search service on PATIENT_SUBSET...")
        cursor.execute("""
            CREATE OR REPLACE CORTEX SEARCH SERVICE HEALTHCARE_DEMO.MEDICAL_NOTES.patient_search_service
                ON PATIENT_NOTES
                ATTRIBUTES PATIENT_ID, PATIENT_UID, PATIENT_TITLE, AGE_YEARS, GENDER
                WAREHOUSE = CORTEX_SEARCH_WH
                TARGET_LAG = '1 hour'
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
                )
        """)
        print("✓ Cortex Search service created")
        
        # Verify the data
        print("\n" + "="*60)
        print("Data Verification")
        print("="*60)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_patients,
                AVG(AGE_YEARS) as avg_age,
                MIN(AGE_YEARS) as min_age,
                MAX(AGE_YEARS) as max_age,
                COUNT(DISTINCT GENDER) as gender_count
            FROM PATIENT_SUBSET
        """)
        
        result = cursor.fetchone()
        print(f"Total patients: {result[0]}")
        print(f"Average age: {result[1]:.1f} years")
        print(f"Age range: {result[2]:.1f} - {result[3]:.1f} years")
        print(f"Gender categories: {result[4]}")
        
        # Show sample of cleaned age data
        print("\nSample of cleaned age data:")
        cursor.execute("""
            SELECT 
                PATIENT_ID,
                AGE_ORIGINAL,
                AGE_YEARS,
                LEFT(PATIENT_TITLE, 60) as PATIENT_TITLE_TRUNC
            FROM PATIENT_SUBSET
            WHERE AGE_ORIGINAL LIKE '%months%' OR AGE_ORIGINAL LIKE '%days%'
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"  ID: {row[0]}, Original: {row[1]}, Cleaned: {row[2]} years")
            print(f"    Title: {row[3]}...")
        
        print("\n✅ All tables created successfully!")
        print("✅ Patient subset ready with cleaned age data!")
        print("✅ Cortex Search service updated!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()