"""
Test batch processing with just 5 patients to verify functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch_process_all_patients import process_single_patient, save_patient_analysis
from src.connection_helper import get_snowflake_connection
import json

def main():
    print("="*60)
    print("Testing Batch Processing with 5 Patients")
    print("="*60)
    
    conn = get_snowflake_connection()
    if not conn:
        print("Failed to connect to Snowflake")
        return
    
    cursor = conn.cursor()
    
    try:
        # Use database and schema
        cursor.execute("USE DATABASE HEALTHCARE_DEMO")
        cursor.execute("USE SCHEMA MEDICAL_NOTES")
        
        # Get 5 test patients
        print("\nFetching 5 test patients...")
        cursor.execute("""
            SELECT PATIENT_ID, PATIENT_UID, PATIENT_NOTES, 
                   SIMILAR_PATIENTS, RELEVANT_ARTICLES
            FROM PATIENT_SUBSET
            WHERE PATIENT_NOTES IS NOT NULL
            ORDER BY PATIENT_ID
            LIMIT 5
        """)
        
        patients = cursor.fetchall()
        print(f"Found {len(patients)} patients for testing")
        
        # Process each patient
        for row in patients:
            patient_data = {
                'PATIENT_ID': row[0],
                'PATIENT_UID': row[1],
                'PATIENT_NOTES': row[2],
                'SIMILAR_PATIENTS': row[3],
                'RELEVANT_ARTICLES': row[4]
            }
            
            print(f"\n{'='*40}")
            print(f"Processing Patient {patient_data['PATIENT_ID']}")
            print(f"Note length: {len(patient_data['PATIENT_NOTES'])} characters")
            
            try:
                # Process all use cases
                results = process_single_patient(patient_data, conn)
                
                # Display some results
                if results.get('clinical_summary'):
                    print(f"✓ Clinical Summary: {results['clinical_summary'].get('chief_complaint', 'N/A')[:50]}...")
                
                if results.get('differential_diagnosis'):
                    dx_list = results['differential_diagnosis'].get('differential_diagnoses', [])
                    print(f"✓ Differential Diagnoses: {len(dx_list)} found")
                    if dx_list:
                        print(f"  - Top diagnosis: {dx_list[0].get('diagnosis', 'N/A')}")
                
                if results.get('cost_analysis'):
                    print(f"✓ Cost Analysis: {results['cost_analysis'].get('cost_category', 'N/A')} " +
                          f"(${results['cost_analysis'].get('estimated_encounter_cost', 0):,.2f})")
                
                if results.get('medication_safety'):
                    meds = results['medication_safety'].get('extracted_medications', [])
                    print(f"✓ Medications: {len(meds)} found")
                
                # Save results
                if save_patient_analysis(results, conn):
                    print(f"✅ Successfully saved analysis for patient {patient_data['PATIENT_ID']}")
                else:
                    print(f"❌ Failed to save analysis for patient {patient_data['PATIENT_ID']}")
                
            except Exception as e:
                print(f"❌ Error processing patient {patient_data['PATIENT_ID']}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Show summary of saved data
        print(f"\n{'='*60}")
        print("Verification of Saved Data")
        print("="*60)
        
        cursor.execute("""
            SELECT COUNT(*) FROM PATIENT_ANALYSIS
        """)
        pa_count = cursor.fetchone()[0]
        print(f"PATIENT_ANALYSIS records: {pa_count}")
        
        cursor.execute("""
            SELECT COUNT(*) FROM MEDICATION_ANALYSIS
        """)
        ma_count = cursor.fetchone()[0]
        print(f"MEDICATION_ANALYSIS records: {ma_count}")
        
        cursor.execute("""
            SELECT COUNT(*) FROM COST_ANALYSIS
        """)
        ca_count = cursor.fetchone()[0]
        print(f"COST_ANALYSIS records: {ca_count}")
        
        # Show a sample record
        print("\nSample PATIENT_ANALYSIS record:")
        cursor.execute("""
            SELECT PATIENT_ID, CHIEF_COMPLAINT, PRESENTATION_TYPE, 
                   ESTIMATED_COST_CATEGORY, PROCESSED_TIMESTAMP
            FROM PATIENT_ANALYSIS
            LIMIT 1
        """)
        sample = cursor.fetchone()
        if sample:
            print(f"  Patient ID: {sample[0]}")
            print(f"  Chief Complaint: {sample[1][:50] if sample[1] else 'N/A'}...")
            print(f"  Presentation Type: {sample[2]}")
            print(f"  Cost Category: {sample[3]}")
            print(f"  Processed: {sample[4]}")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()