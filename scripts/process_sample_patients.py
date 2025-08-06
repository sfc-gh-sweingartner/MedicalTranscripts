"""
Process sample patients to populate the analysis tables
This creates pre-computed insights for demo purposes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connection_helper import get_snowflake_connection, execute_query, execute_cortex_complete
import json
from datetime import datetime

def process_patient(conn, patient_id):
    """Process a single patient and store results"""
    cursor = conn.cursor()
    
    try:
        # Get patient data
        cursor.execute(f"""
            SELECT PATIENT_ID, PATIENT_UID, PATIENT_NOTES, SIMILAR_PATIENTS, RELEVANT_ARTICLES
            FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
            WHERE PATIENT_ID = {patient_id}
        """)
        
        result = cursor.fetchone()
        if not result:
            print(f"Patient {patient_id} not found")
            return False
        
        patient_notes = result[2]
        
        print(f"Processing patient {patient_id}...")
        
        # Generate SBAR summary
        sbar_prompt = f"""
        Create an SBAR summary from these notes:
        {patient_notes[:2000]}
        
        Format as JSON:
        {{
            "situation": "Current clinical situation",
            "background": "Medical history and context", 
            "assessment": "Clinical assessment",
            "recommendation": "Treatment recommendations"
        }}
        """
        
        sbar_response = execute_cortex_complete(sbar_prompt, "mistral-large", conn)
        
        # Extract JSON from response
        import re
        sbar_match = re.search(r'\{.*\}', sbar_response, re.DOTALL)
        sbar_json = sbar_match.group() if sbar_match else '{}'
        
        # Generate differential diagnoses
        dx_prompt = f"""
        Based on these notes, list 3 differential diagnoses:
        {patient_notes[:1500]}
        
        Format as JSON array:
        [
            {{"diagnosis": "name", "confidence": "HIGH/MEDIUM/LOW", "evidence": "supporting findings"}}
        ]
        """
        
        dx_response = execute_cortex_complete(dx_prompt, "mixtral-8x7b", conn)
        dx_match = re.search(r'\[.*\]', dx_response, re.DOTALL)
        dx_json = dx_match.group() if dx_match else '[]'
        
        # Extract chief complaint
        chief_prompt = f"""
        Extract the chief complaint from these notes in one sentence:
        {patient_notes[:1000]}
        """
        
        chief_complaint = execute_cortex_complete(chief_prompt, "mistral-large", conn)
        chief_complaint = chief_complaint.strip()[:200]
        
        # Create clinical summary
        summary_prompt = f"""
        Create a brief clinical summary (2-3 sentences) of this case:
        {patient_notes[:1500]}
        """
        
        clinical_summary = execute_cortex_complete(summary_prompt, "mistral-large", conn)
        clinical_summary = clinical_summary.strip()[:500]
        
        # Clean and escape JSON strings
        sbar_json_clean = sbar_json.replace("'", "''").replace("\n", " ").replace("\r", "")
        dx_json_clean = dx_json.replace("'", "''").replace("\n", " ").replace("\r", "")
        
        # Insert into analysis table
        insert_query = f"""
        INSERT INTO HEALTHCARE_DEMO.MEDICAL_NOTES.PATIENT_ANALYSIS
        (PATIENT_ID, PATIENT_UID, CHIEF_COMPLAINT, CLINICAL_SUMMARY, 
         SBAR_SUMMARY, DIFFERENTIAL_DIAGNOSES, PRESENTATION_TYPE,
         ESTIMATED_COST_CATEGORY)
        VALUES (
            {patient_id},
            '{result[1]}',
            '{chief_complaint.replace("'", "''")}',
            '{clinical_summary.replace("'", "''")}',
            PARSE_JSON('{sbar_json_clean}'),
            PARSE_JSON('{dx_json_clean}'),
            'typical',
            'medium'
        )
        """
        
        cursor.execute(insert_query)
        print(f"✓ Patient {patient_id} processed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error processing patient {patient_id}: {str(e)}")
        return False
    finally:
        cursor.close()

def main():
    print("="*60)
    print("Processing Sample Patients")
    print("="*60)
    
    conn = get_snowflake_connection()
    if not conn:
        print("Failed to connect to Snowflake")
        return
    
    # Use database
    cursor = conn.cursor()
    cursor.execute("USE DATABASE HEALTHCARE_DEMO")
    cursor.execute("USE SCHEMA MEDICAL_NOTES")
    cursor.close()
    
    # Process demo scenario patients
    demo_patients = [163840, 163841, 163842, 163843, 163844]
    
    success_count = 0
    for patient_id in demo_patients:
        if process_patient(conn, patient_id):
            success_count += 1
    
    print(f"\nProcessed {success_count}/{len(demo_patients)} patients successfully")
    
    # Log a sample real-time analysis
    print("\nCreating sample real-time analysis log...")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO HEALTHCARE_DEMO.MEDICAL_NOTES.REALTIME_ANALYSIS_LOG
            (SESSION_ID, USER_NAME, PATIENT_ID, ORIGINAL_TEXT, MODIFIED_TEXT,
             ANALYSIS_TYPE, AI_MODEL_USED, PROCESSING_TIME_MS, SUCCESS_FLAG)
            VALUES ('demo_session', 'demo_user', 163840, 
                    'Sample original text', 'Sample modified text',
                    'demo', 'mistral-large', 1500, TRUE)
        """)
        cursor.close()
        print("✓ Sample log entry created")
    except Exception as e:
        print(f"✗ Failed to create log entry: {str(e)}")
    
    conn.close()
    print("\n✅ Sample data processing complete!")

if __name__ == "__main__":
    main()