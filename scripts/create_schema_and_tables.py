"""
Create schema and tables using direct SQL execution
"""

import snowflake.connector
import tomli
import os

def get_connection():
    """Get Snowflake connection"""
    try:
        config_path = '/Users/sweingartner/.snowflake/config.toml'
        with open(config_path, 'rb') as f:
            config = tomli.load(f)
        
        default_conn = config.get('default_connection_name')
        conn_params = config.get('connections', {}).get(default_conn)
        
        conn = snowflake.connector.connect(**conn_params)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def main():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # First, use the database
        print("Using HEALTHCARE_DEMO database...")
        cursor.execute("USE DATABASE HEALTHCARE_DEMO")
        print("✓ Database selected")
        
        # Create schema
        print("\nCreating MEDICAL_NOTES schema...")
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS MEDICAL_NOTES
            COMMENT = 'Schema containing patient notes analysis tables and views'
        """)
        print("✓ Schema created")
        
        # Use the schema
        cursor.execute("USE SCHEMA MEDICAL_NOTES")
        print("✓ Schema selected")
        
        # Create each table individually
        tables = [
            ("PATIENT_ANALYSIS", """
                CREATE OR REPLACE TABLE PATIENT_ANALYSIS (
                    PATIENT_ID NUMBER PRIMARY KEY,
                    PATIENT_UID VARCHAR,
                    ANALYSIS_VERSION VARCHAR DEFAULT 'v1.0',
                    PROCESSED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    CHIEF_COMPLAINT TEXT,
                    CLINICAL_SUMMARY TEXT,
                    SBAR_SUMMARY VARIANT,
                    KEY_FINDINGS VARIANT,
                    DIFFERENTIAL_DIAGNOSES VARIANT,
                    DIAGNOSTIC_REASONING TEXT,
                    SIMILAR_PATIENT_DIAGNOSES VARIANT,
                    TREATMENTS_ADMINISTERED VARIANT,
                    TREATMENT_EFFECTIVENESS TEXT,
                    EVIDENCE_BASED_RECOMMENDATIONS VARIANT,
                    SIMILAR_PATIENT_TREATMENTS VARIANT,
                    PRESENTATION_TYPE VARCHAR,
                    RARE_DISEASE_INDICATORS VARIANT,
                    SYMPTOM_CLUSTER_ID VARCHAR,
                    ANOMALY_SCORE FLOAT,
                    HIGH_COST_INDICATORS VARIANT,
                    ESTIMATED_COST_CATEGORY VARCHAR,
                    RESOURCE_UTILIZATION VARIANT,
                    CARE_QUALITY_INDICATORS VARIANT,
                    GUIDELINE_ADHERENCE_FLAGS VARIANT,
                    TEACHING_POINTS VARIANT,
                    CLINICAL_PEARLS TEXT,
                    QUIZ_QUESTIONS VARIANT
                ) COMMENT = 'Pre-computed AI analysis results for patient notes'
            """),
            
            ("REALTIME_ANALYSIS_LOG", """
                CREATE OR REPLACE TABLE REALTIME_ANALYSIS_LOG (
                    ANALYSIS_ID VARCHAR DEFAULT UUID_STRING(),
                    SESSION_ID VARCHAR,
                    USER_NAME VARCHAR,
                    ANALYSIS_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PATIENT_ID NUMBER,
                    ORIGINAL_TEXT TEXT,
                    MODIFIED_TEXT TEXT,
                    ANALYSIS_TYPE VARCHAR,
                    AI_MODEL_USED VARCHAR,
                    PROCESSING_TIME_MS NUMBER,
                    RESULTS VARIANT,
                    SUCCESS_FLAG BOOLEAN
                ) COMMENT = 'Log of real-time AI processing requests and results'
            """),
            
            ("COHORT_INSIGHTS", """
                CREATE OR REPLACE TABLE COHORT_INSIGHTS (
                    COHORT_ID VARCHAR DEFAULT UUID_STRING(),
                    ANALYSIS_DATE DATE DEFAULT CURRENT_DATE(),
                    COHORT_DEFINITION VARIANT,
                    PATIENT_COUNT NUMBER,
                    COMMON_DIAGNOSES VARIANT,
                    TREATMENT_PATTERNS VARIANT,
                    OUTCOME_STATISTICS VARIANT,
                    COST_ANALYSIS VARIANT,
                    QUALITY_METRICS VARIANT,
                    TEMPORAL_TRENDS VARIANT,
                    EMERGING_PATTERNS TEXT
                ) COMMENT = 'Aggregated insights for patient cohorts'
            """),
            
            ("PHYSICIAN_INSIGHTS", """
                CREATE OR REPLACE TABLE PHYSICIAN_INSIGHTS (
                    INSIGHT_ID VARCHAR DEFAULT UUID_STRING(),
                    GENERATED_DATE DATE DEFAULT CURRENT_DATE(),
                    SPECIALTY VARCHAR,
                    INSIGHT_TYPE VARCHAR,
                    INSIGHT_TITLE TEXT,
                    INSIGHT_CONTENT TEXT,
                    EVIDENCE_LINKS VARIANT,
                    APPLICABLE_PATIENTS VARIANT,
                    PRIORITY_SCORE NUMBER
                ) COMMENT = 'Curated insights for physician workflows'
            """),
            
            ("PROCESSING_STATUS", """
                CREATE OR REPLACE TABLE PROCESSING_STATUS (
                    BATCH_ID VARCHAR DEFAULT UUID_STRING(),
                    START_TIME TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    END_TIME TIMESTAMP_NTZ,
                    STATUS VARCHAR,
                    TOTAL_PATIENTS NUMBER,
                    PROCESSED_PATIENTS NUMBER,
                    FAILED_PATIENTS NUMBER,
                    ERROR_DETAILS VARIANT,
                    PROCESSING_METRICS VARIANT
                ) COMMENT = 'Track batch processing jobs'
            """),
            
            ("DEMO_SCENARIOS", """
                CREATE OR REPLACE TABLE DEMO_SCENARIOS (
                    SCENARIO_ID VARCHAR PRIMARY KEY,
                    SCENARIO_NAME VARCHAR,
                    SCENARIO_TYPE VARCHAR,
                    PATIENT_ID NUMBER,
                    DESCRIPTION TEXT,
                    TALKING_POINTS VARIANT,
                    EXPECTED_OUTCOMES VARIANT,
                    DEMO_DURATION_MINUTES NUMBER
                ) COMMENT = 'Pre-configured demo scenarios for consistent presentations'
            """)
        ]
        
        # Create each table
        print("\nCreating tables...")
        for table_name, create_sql in tables:
            print(f"  Creating {table_name}...")
            cursor.execute(create_sql)
            print(f"  ✓ {table_name} created")
        
        # Create view
        print("\nCreating patient summary view...")
        cursor.execute("""
            CREATE OR REPLACE VIEW V_PATIENT_SUMMARY AS
            SELECT 
                p.PATIENT_ID,
                p.PATIENT_UID,
                pmc.PATIENT_TITLE,
                pmc.AGE,
                pmc.GENDER,
                p.CHIEF_COMPLAINT,
                p.CLINICAL_SUMMARY,
                p.PRESENTATION_TYPE,
                p.ESTIMATED_COST_CATEGORY,
                p.PROCESSED_TIMESTAMP
            FROM PATIENT_ANALYSIS p
            LEFT JOIN PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS pmc
                ON p.PATIENT_ID = pmc.PATIENT_ID
            ORDER BY p.PROCESSED_TIMESTAMP DESC
        """)
        print("✓ View created")
        
        # Insert demo scenarios
        print("\nInserting demo scenarios...")
        cursor.execute("""
            INSERT INTO DEMO_SCENARIOS (SCENARIO_ID, SCENARIO_NAME, SCENARIO_TYPE, PATIENT_ID, DESCRIPTION, DEMO_DURATION_MINUTES)
            VALUES 
                ('COMPLEX_DIAGNOSIS', 'Complex Diagnostic Case', 'diagnostic', 163844, 
                 '66-year-old with seizures and cardiac arrhythmia requiring differential diagnosis', 5),
                ('RARE_DISEASE', 'Pediatric Rare Disease', 'diagnostic', 163840,
                 '11-year-old with multicentric peripheral ossifying fibroma', 5),
                ('COST_OPTIMIZATION', 'High-Cost Patient Analysis', 'cost', 163841,
                 'Patient with multiple procedures and complications', 5)
        """)
        print("✓ Demo scenarios inserted")
        
        # Create stage
        print("\nCreating stage...")
        cursor.execute("""
            CREATE STAGE IF NOT EXISTS MEDICAL_NOTES_STAGE
            COMMENT = 'Stage for uploading medical data files and Streamlit app'
        """)
        print("✓ Stage created")
        
        print("\n✅ All database objects created successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()