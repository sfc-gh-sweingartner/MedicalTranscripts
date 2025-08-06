"""
Healthcare AI Demo - Database Setup Script
==========================================

This script creates the database objects and tests the environment setup.
Run this first to initialize the healthcare demo.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connection_helper import (
    get_snowflake_connection, 
    execute_query, 
    test_cortex_ai_functions,
    get_demo_data_status,
    initialize_demo_environment
)
import pandas as pd
from datetime import datetime

def create_database_objects(conn):
    """Create all database objects from SQL script"""
    print("Creating database objects...")
    
    # Read the SQL script
    with open('sql/01_create_database_objects.sql', 'r') as f:
        sql_script = f.read()
    
    # Split into individual statements (handle both ; and GO as delimiters)
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
    
    # Execute each statement
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        # Skip comments and empty statements
        if not statement or statement.startswith('--'):
            continue
            
        try:
            print(f"Executing statement {i+1}/{len(statements)}...")
            execute_query(statement, conn)
            success_count += 1
        except Exception as e:
            print(f"Error executing statement {i+1}: {str(e)}")
            error_count += 1
            # Continue with other statements
    
    print(f"\nDatabase setup complete: {success_count} successful, {error_count} errors")
    return success_count, error_count

def verify_tables_exist(conn):
    """Verify all required tables exist"""
    print("\nVerifying tables...")
    
    tables_to_check = [
        "PATIENT_ANALYSIS",
        "REALTIME_ANALYSIS_LOG",
        "COHORT_INSIGHTS",
        "PHYSICIAN_INSIGHTS",
        "PROCESSING_STATUS",
        "DEMO_SCENARIOS"
    ]
    
    results = {}
    for table in tables_to_check:
        try:
            query = f"SELECT COUNT(*) FROM HEALTHCARE_DEMO.MEDICAL_NOTES.{table} LIMIT 1"
            execute_query(query, conn)
            results[table] = "✓ Found"
        except Exception as e:
            results[table] = f"✗ Error: {str(e)}"
    
    # Display results
    print("\nTable verification results:")
    for table, status in results.items():
        print(f"  {table}: {status}")
    
    return all("✓" in status for status in results.values())

def test_pmc_access(conn):
    """Test access to PMC patients data"""
    print("\nTesting access to PMC patients data...")
    
    try:
        query = """
        SELECT 
            COUNT(*) as total_patients,
            COUNT(DISTINCT GENDER) as genders,
            MIN(PATIENT_ID) as min_id,
            MAX(PATIENT_ID) as max_id
        FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
        """
        result = execute_query(query, conn)
        
        if not result.empty:
            print(f"  Total patients: {result.iloc[0]['total_patients']:,}")
            print(f"  Patient ID range: {result.iloc[0]['min_id']} - {result.iloc[0]['max_id']}")
            print(f"  Genders: {result.iloc[0]['genders']}")
            
            # Get a sample patient
            sample_query = """
            SELECT PATIENT_ID, PATIENT_TITLE, AGE, GENDER
            FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
            LIMIT 1
            """
            sample = execute_query(sample_query, conn)
            if not sample.empty:
                print(f"\n  Sample patient:")
                print(f"    ID: {sample.iloc[0]['PATIENT_ID']}")
                print(f"    Title: {sample.iloc[0]['PATIENT_TITLE'][:60]}...")
                print(f"    Age: {sample.iloc[0]['AGE']}")
                print(f"    Gender: {sample.iloc[0]['GENDER']}")
            
            return True
    except Exception as e:
        print(f"  ✗ Error accessing PMC data: {str(e)}")
        return False

def test_cortex_models(conn):
    """Test specific Cortex AI models for healthcare"""
    print("\nTesting Cortex AI models...")
    
    ai_status = test_cortex_ai_functions(conn)
    
    print("\nCortex AI function status:")
    for func, available in ai_status.items():
        if func != "error":
            status = "✓ Available" if available else "✗ Not available"
            print(f"  {func}: {status}")
    
    # Test a medical prompt if models are available
    if ai_status.get("mistral-large"):
        print("\nTesting medical prompt with Mistral Large...")
        try:
            test_prompt = """
            Extract the chief complaint from this note in one sentence:
            'A 45-year-old male presents with severe chest pain radiating to left arm, 
            started 2 hours ago while climbing stairs. Associated with sweating and nausea.'
            """
            
            query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{test_prompt}'
            ) as response
            """
            
            result = execute_query(query, conn)
            if not result.empty:
                print(f"  Response: {result.iloc[0][0][:100]}...")
                print("  ✓ Medical prompt test successful")
        except Exception as e:
            print(f"  ✗ Medical prompt test failed: {str(e)}")

def main():
    """Main setup function"""
    print("="*60)
    print("Healthcare AI Demo - Database Setup")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize connection
    print("\nInitializing connection...")
    conn = get_snowflake_connection()
    
    if conn is None:
        print("✗ Failed to establish connection. Please check your configuration.")
        return 1
    
    print("✓ Connection established")
    
    # Get environment status
    print("\nChecking environment...")
    env_status = initialize_demo_environment()
    
    print(f"  Connection type: {env_status['connection']['type']}")
    print(f"  Account: {env_status['connection'].get('account', 'Unknown')}")
    
    # Create database objects
    success, errors = create_database_objects(conn)
    
    if errors > 0:
        print(f"\n⚠ Warning: {errors} errors occurred during setup")
    
    # Verify tables
    tables_ok = verify_tables_exist(conn)
    
    # Test PMC access
    pmc_ok = test_pmc_access(conn)
    
    # Test Cortex AI
    test_cortex_models(conn)
    
    # Summary
    print("\n" + "="*60)
    print("Setup Summary:")
    print(f"  Database objects: {'✓ Created' if success > 0 else '✗ Failed'}")
    print(f"  Tables verified: {'✓ Yes' if tables_ok else '✗ No'}")
    print(f"  PMC data access: {'✓ Yes' if pmc_ok else '✗ No'}")
    print(f"  Cortex AI: See details above")
    
    if tables_ok and pmc_ok:
        print("\n✓ Healthcare demo environment is ready!")
        print("\nNext steps:")
        print("  1. Run scripts/load_sample_data.py to process sample patients")
        print("  2. Run streamlit run src/streamlit_main.py to start the demo")
    else:
        print("\n✗ Setup incomplete. Please check the errors above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return 0 if (tables_ok and pmc_ok) else 1

if __name__ == "__main__":
    exit(main())