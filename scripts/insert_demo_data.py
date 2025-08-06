"""
Insert demo data directly into analysis tables
"""

import snowflake.connector
import tomli
import json

def get_connection():
    """Get Snowflake connection"""
    config_path = '/Users/sweingartner/.snowflake/config.toml'
    with open(config_path, 'rb') as f:
        config = tomli.load(f)
    
    default_conn = config.get('default_connection_name')
    conn_params = config.get('connections', {}).get(default_conn)
    return snowflake.connector.connect(**conn_params)

def main():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use database
    cursor.execute("USE DATABASE HEALTHCARE_DEMO")
    cursor.execute("USE SCHEMA MEDICAL_NOTES")
    
    # Insert demo patient analyses
    demo_data = [
        {
            'patient_id': 163840,
            'patient_uid': '163840-1',
            'chief_complaint': '11-year-old boy with multiple gingival masses in maxillary region',
            'clinical_summary': 'Pediatric patient presenting with multicentric peripheral ossifying fibroma - a rare condition. Multiple lesions affecting both maxilla and mandible, causing functional impairment.',
            'sbar': {
                "situation": "11-year-old with slow-growing painless masses in maxillary regions",
                "background": "Healthy child, lesions started as papules 1 year ago, now 5 lesions total",
                "assessment": "Multiple exophytic lesions, likely peripheral ossifying fibroma",
                "recommendation": "Excisional biopsy and histopathological examination required"
            },
            'dx': [
                {"diagnosis": "Peripheral ossifying fibroma", "confidence": "HIGH", "evidence": "Multiple gingival masses, age, location"},
                {"diagnosis": "Fibrous hyperplasia", "confidence": "MEDIUM", "evidence": "Firm consistency, slow growth"},
                {"diagnosis": "Peripheral giant cell granuloma", "confidence": "LOW", "evidence": "Age and presentation compatible"}
            ]
        },
        {
            'patient_id': 163841,
            'patient_uid': '163841-1',
            'chief_complaint': '41-year-old female with gingival swelling in anterior maxilla',
            'clinical_summary': 'Adult female with peripheral odontogenic myxoma of maxillary gingiva. Successfully treated with surgical excision, no recurrence at 6-month follow-up.',
            'sbar': {
                "situation": "41-year-old female with 6-month history of gingival mass",
                "background": "No trauma or pain, solitary non-tender swelling on labial gingiva",
                "assessment": "Peripheral odontogenic myxoma confirmed by histopathology",
                "recommendation": "Complete excision performed, continue regular follow-up"
            },
            'dx': [
                {"diagnosis": "Peripheral odontogenic myxoma", "confidence": "HIGH", "evidence": "Histopathology confirmed"},
                {"diagnosis": "Fibroma", "confidence": "MEDIUM", "evidence": "Initial clinical presentation"},
                {"diagnosis": "Peripheral ameloblastoma", "confidence": "LOW", "evidence": "Location and age"}
            ]
        }
    ]
    
    for data in demo_data:
        try:
            # Convert dictionaries to JSON strings
            sbar_json = json.dumps(data['sbar'])
            dx_json = json.dumps(data['dx'])
            
            # Insert query
            query = """
            INSERT INTO HEALTHCARE_DEMO.MEDICAL_NOTES.PATIENT_ANALYSIS
            (PATIENT_ID, PATIENT_UID, CHIEF_COMPLAINT, CLINICAL_SUMMARY, 
             SBAR_SUMMARY, DIFFERENTIAL_DIAGNOSES, PRESENTATION_TYPE,
             ESTIMATED_COST_CATEGORY)
            SELECT 
                %(patient_id)s,
                %(patient_uid)s,
                %(chief_complaint)s,
                %(clinical_summary)s,
                PARSE_JSON(%(sbar_json)s),
                PARSE_JSON(%(dx_json)s),
                'typical',
                'medium'
            """
            
            cursor.execute(query, {
                'patient_id': data['patient_id'],
                'patient_uid': data['patient_uid'],
                'chief_complaint': data['chief_complaint'],
                'clinical_summary': data['clinical_summary'],
                'sbar_json': sbar_json,
                'dx_json': dx_json
            })
            
            print(f"✓ Inserted patient {data['patient_id']}")
            
        except Exception as e:
            print(f"✗ Error inserting patient {data['patient_id']}: {str(e)}")
    
    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Demo data insertion complete!")

if __name__ == "__main__":
    main()