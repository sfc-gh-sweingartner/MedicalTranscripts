"""
Batch process all patients in PATIENT_SUBSET through all AI use cases
Supports configurable prompts and re-processing capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connection_helper import get_snowflake_connection, execute_cortex_complete
import json
import time
from datetime import datetime
import concurrent.futures
from typing import Dict, List, Any
import traceback

# Import prompts configuration
from prompts_config import *

def parse_json_response(response: str, default: dict = None) -> dict:
    """Safely parse JSON from AI response"""
    try:
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return default or {}

def process_differential_diagnosis(patient_data: dict, conn) -> dict:
    """Use Case 1: Differential Diagnosis"""
    prompt = DIFFERENTIAL_DIAGNOSIS_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['differential_diagnosis'], conn)
    return parse_json_response(response, {
        "differential_diagnoses": [],
        "key_findings": [],
        "diagnostic_reasoning": "Unable to parse response"
    })

def process_treatment_analysis(patient_data: dict, conn) -> dict:
    """Use Case 2: Treatment Analysis"""
    # Extract similar treatments from SIMILAR_PATIENTS if available
    similar_treatments = ""
    if patient_data.get('SIMILAR_PATIENTS'):
        try:
            similar_data = json.loads(patient_data['SIMILAR_PATIENTS'])
            if isinstance(similar_data, list) and len(similar_data) > 0:
                similar_treatments = "Various treatment approaches from similar cases"
        except:
            pass
    
    prompt = TREATMENT_ANALYSIS_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000],
        similar_treatments=similar_treatments
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['treatment_analysis'], conn)
    return parse_json_response(response, {
        "current_treatments": [],
        "treatment_effectiveness": "Unable to analyze",
        "evidence_based_recommendations": []
    })

def process_clinical_summary(patient_data: dict, conn) -> dict:
    """Use Case 3: Clinical Summary (SBAR)"""
    prompt = CLINICAL_SUMMARY_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['clinical_summary'], conn)
    return parse_json_response(response, {
        "situation": "Unable to parse",
        "background": "Unable to parse",
        "assessment": "Unable to parse", 
        "recommendation": "Unable to parse"
    })

def process_pattern_recognition(patient_data: dict, conn) -> dict:
    """Use Case 4: Pattern Recognition & Rare Disease"""
    prompt = PATTERN_RECOGNITION_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['pattern_recognition'], conn)
    result = parse_json_response(response, {
        "presentation_type": "typical",
        "rare_disease_indicators": [],
        "anomaly_score": 0.0
    })
    
    # Ensure anomaly_score is a float
    try:
        result['anomaly_score'] = float(result.get('anomaly_score', 0))
    except:
        result['anomaly_score'] = 0.0
    
    return result

def process_cost_analysis(patient_data: dict, conn) -> dict:
    """Use Case 5: Cost Analysis"""
    prompt = COST_ANALYSIS_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['cost_analysis'], conn)
    return parse_json_response(response, {
        "extracted_procedures": [],
        "high_cost_indicators": [],
        "cost_drivers": "Unable to analyze"
    })

def process_medication_safety(patient_data: dict, conn) -> dict:
    """Use Case 6: Medication Safety"""
    prompt = MEDICATION_SAFETY_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['medication_safety'], conn)
    return parse_json_response(response, {
        "extracted_medications": [],
        "potential_interactions": [],
        "polypharmacy_count": 0
    })

def process_quality_metrics(patient_data: dict, conn) -> dict:
    """Use Case 7: Quality Metrics"""
    prompt = QUALITY_METRICS_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['quality_metrics'], conn)
    return parse_json_response(response, {
        "quality_indicators": [],
        "guideline_adherence": [],
        "improvement_opportunities": []
    })

def process_educational_value(patient_data: dict, conn) -> dict:
    """Use Case 8: Educational Value"""
    prompt = EDUCATIONAL_VALUE_PROMPT.format(
        patient_notes=patient_data['PATIENT_NOTES'][:3000]
    )
    
    response = execute_cortex_complete(prompt, MODEL_SELECTION['educational_value'], conn)
    return parse_json_response(response, {
        "teaching_points": [],
        "clinical_pearls": "",
        "quiz_questions": []
    })

def estimate_encounter_cost(procedures: list, indicators: list, conn) -> tuple:
    """Estimate total encounter cost based on extracted procedures"""
    cursor = conn.cursor()
    total_cost = 0.0
    cost_category = "low"
    
    try:
        # Look up costs for identified procedures
        for proc in procedures:
            proc_name = proc.get('procedure', '').lower()
            
            # Query procedure costs table for matches
            cursor.execute("""
                SELECT ESTIMATED_COST 
                FROM PROCEDURE_COSTS 
                WHERE LOWER(PROCEDURE_NAME) LIKE %s
                LIMIT 1
            """, (f"%{proc_name}%",))
            
            result = cursor.fetchone()
            if result:
                total_cost += float(result[0])
        
        # Add costs for high-cost indicators
        for indicator in indicators:
            ind_text = indicator.get('indicator', '').lower()
            if 'icu' in ind_text:
                total_cost += 3500  # ICU per day estimate
            elif 'surgery' in ind_text or 'surgical' in ind_text:
                total_cost += 15000  # Generic surgery estimate
            elif 'emergency' in ind_text or 'ed' in ind_text:
                total_cost += 1200  # ED visit
        
        # Determine cost category
        if total_cost < 1000:
            cost_category = "low"
        elif total_cost < 5000:
            cost_category = "medium"
        elif total_cost < 20000:
            cost_category = "high"
        else:
            cost_category = "very_high"
            
    except Exception as e:
        print(f"Error estimating costs: {str(e)}")
    finally:
        cursor.close()
    
    return total_cost, cost_category

def check_drug_interactions(medications: list, conn) -> list:
    """Check for drug interactions from reference table"""
    cursor = conn.cursor()
    interactions = []
    
    try:
        # Check each pair of medications
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                drug1 = medications[i].get('name', '').upper()
                drug2 = medications[j].get('name', '').upper()
                
                # Query interaction database
                cursor.execute("""
                    SELECT SEVERITY, DESCRIPTION
                    FROM DRUG_INTERACTIONS_REFERENCE
                    WHERE (UPPER(DRUG1) = %s AND UPPER(DRUG2) = %s)
                       OR (UPPER(DRUG1) = %s AND UPPER(DRUG2) = %s)
                    LIMIT 1
                """, (drug1, drug2, drug2, drug1))
                
                result = cursor.fetchone()
                if result:
                    interactions.append({
                        "drug1": medications[i].get('name'),
                        "drug2": medications[j].get('name'),
                        "severity": result[0],
                        "description": result[1]
                    })
    except Exception as e:
        print(f"Error checking interactions: {str(e)}")
    finally:
        cursor.close()
    
    return interactions

def process_single_patient(patient_data: dict, conn) -> dict:
    """Process all use cases for a single patient"""
    patient_id = patient_data['PATIENT_ID']
    results = {
        'patient_id': patient_id,
        'success': True,
        'errors': []
    }
    
    try:
        print(f"Processing patient {patient_id}...")
        
        # Use Case 1: Differential Diagnosis
        try:
            diff_dx = process_differential_diagnosis(patient_data, conn)
            results['differential_diagnosis'] = diff_dx
        except Exception as e:
            results['errors'].append(f"Differential diagnosis error: {str(e)}")
            results['differential_diagnosis'] = {}
        
        # Use Case 2: Treatment Analysis
        try:
            treatment = process_treatment_analysis(patient_data, conn)
            results['treatment_analysis'] = treatment
        except Exception as e:
            results['errors'].append(f"Treatment analysis error: {str(e)}")
            results['treatment_analysis'] = {}
        
        # Use Case 3: Clinical Summary
        try:
            summary = process_clinical_summary(patient_data, conn)
            results['clinical_summary'] = summary
        except Exception as e:
            results['errors'].append(f"Clinical summary error: {str(e)}")
            results['clinical_summary'] = {}
        
        # Use Case 4: Pattern Recognition
        try:
            patterns = process_pattern_recognition(patient_data, conn)
            results['pattern_recognition'] = patterns
        except Exception as e:
            results['errors'].append(f"Pattern recognition error: {str(e)}")
            results['pattern_recognition'] = {}
        
        # Use Case 5: Cost Analysis
        try:
            cost = process_cost_analysis(patient_data, conn)
            # Estimate actual costs
            total_cost, cost_category = estimate_encounter_cost(
                cost.get('extracted_procedures', []),
                cost.get('high_cost_indicators', []),
                conn
            )
            cost['estimated_encounter_cost'] = total_cost
            cost['cost_category'] = cost_category
            results['cost_analysis'] = cost
        except Exception as e:
            results['errors'].append(f"Cost analysis error: {str(e)}")
            results['cost_analysis'] = {}
        
        # Use Case 6: Medication Safety
        try:
            meds = process_medication_safety(patient_data, conn)
            # Check drug interactions against reference
            if meds.get('extracted_medications'):
                interactions = check_drug_interactions(meds['extracted_medications'], conn)
                if interactions:
                    meds['potential_interactions'].extend(interactions)
            results['medication_safety'] = meds
        except Exception as e:
            results['errors'].append(f"Medication safety error: {str(e)}")
            results['medication_safety'] = {}
        
        # Use Case 7: Quality Metrics
        try:
            quality = process_quality_metrics(patient_data, conn)
            results['quality_metrics'] = quality
        except Exception as e:
            results['errors'].append(f"Quality metrics error: {str(e)}")
            results['quality_metrics'] = {}
        
        # Use Case 8: Educational Value
        try:
            education = process_educational_value(patient_data, conn)
            results['educational_value'] = education
        except Exception as e:
            results['errors'].append(f"Educational value error: {str(e)}")
            results['educational_value'] = {}
        
        if results['errors']:
            results['success'] = False
            
    except Exception as e:
        results['success'] = False
        results['errors'].append(f"Overall processing error: {str(e)}")
        traceback.print_exc()
    
    return results

def save_patient_analysis(results: dict, conn):
    """Save processed results to PATIENT_ANALYSIS table"""
    cursor = conn.cursor()
    
    try:
        # Extract data for main analysis table
        patient_id = results['patient_id']
        clinical_summary = results.get('clinical_summary', {})
        diff_dx = results.get('differential_diagnosis', {})
        treatment = results.get('treatment_analysis', {})
        patterns = results.get('pattern_recognition', {})
        cost = results.get('cost_analysis', {})
        quality = results.get('quality_metrics', {})
        education = results.get('educational_value', {})
        
        # Insert or update PATIENT_ANALYSIS
        cursor.execute("""
            MERGE INTO PATIENT_ANALYSIS pa
            USING (SELECT %s as PATIENT_ID) s
            ON pa.PATIENT_ID = s.PATIENT_ID
            WHEN MATCHED THEN UPDATE SET
                ANALYSIS_VERSION = 'v1.0',
                PROCESSED_TIMESTAMP = CURRENT_TIMESTAMP(),
                CHIEF_COMPLAINT = %s,
                CLINICAL_SUMMARY = %s,
                SBAR_SUMMARY = PARSE_JSON(%s),
                KEY_FINDINGS = PARSE_JSON(%s),
                DIFFERENTIAL_DIAGNOSES = PARSE_JSON(%s),
                DIAGNOSTIC_REASONING = %s,
                TREATMENTS_ADMINISTERED = PARSE_JSON(%s),
                TREATMENT_EFFECTIVENESS = %s,
                EVIDENCE_BASED_RECOMMENDATIONS = PARSE_JSON(%s),
                PRESENTATION_TYPE = %s,
                RARE_DISEASE_INDICATORS = PARSE_JSON(%s),
                ANOMALY_SCORE = %s,
                HIGH_COST_INDICATORS = PARSE_JSON(%s),
                ESTIMATED_COST_CATEGORY = %s,
                CARE_QUALITY_INDICATORS = PARSE_JSON(%s),
                GUIDELINE_ADHERENCE_FLAGS = PARSE_JSON(%s),
                TEACHING_POINTS = PARSE_JSON(%s),
                CLINICAL_PEARLS = %s,
                QUIZ_QUESTIONS = PARSE_JSON(%s)
            WHEN NOT MATCHED THEN INSERT (
                PATIENT_ID, ANALYSIS_VERSION, CHIEF_COMPLAINT, CLINICAL_SUMMARY,
                SBAR_SUMMARY, KEY_FINDINGS, DIFFERENTIAL_DIAGNOSES, DIAGNOSTIC_REASONING,
                TREATMENTS_ADMINISTERED, TREATMENT_EFFECTIVENESS, EVIDENCE_BASED_RECOMMENDATIONS,
                PRESENTATION_TYPE, RARE_DISEASE_INDICATORS, ANOMALY_SCORE,
                HIGH_COST_INDICATORS, ESTIMATED_COST_CATEGORY,
                CARE_QUALITY_INDICATORS, GUIDELINE_ADHERENCE_FLAGS,
                TEACHING_POINTS, CLINICAL_PEARLS, QUIZ_QUESTIONS
            ) VALUES (
                %s, 'v1.0', %s, %s, PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s), %s,
                PARSE_JSON(%s), %s, PARSE_JSON(%s), %s, PARSE_JSON(%s), %s,
                PARSE_JSON(%s), %s, PARSE_JSON(%s), PARSE_JSON(%s),
                PARSE_JSON(%s), %s, PARSE_JSON(%s)
            )
        """, (
            patient_id,
            # Update values
            clinical_summary.get('chief_complaint', ''),
            clinical_summary.get('clinical_summary', ''),
            json.dumps(clinical_summary),
            json.dumps(diff_dx.get('key_findings', [])),
            json.dumps(diff_dx.get('differential_diagnoses', [])),
            diff_dx.get('diagnostic_reasoning', ''),
            json.dumps(treatment.get('current_treatments', [])),
            treatment.get('treatment_effectiveness', ''),
            json.dumps(treatment.get('evidence_based_recommendations', [])),
            patterns.get('presentation_type', 'typical'),
            json.dumps(patterns.get('rare_disease_indicators', [])),
            patterns.get('anomaly_score', 0.0),
            json.dumps(cost.get('high_cost_indicators', [])),
            cost.get('cost_category', 'medium'),
            json.dumps(quality.get('quality_indicators', [])),
            json.dumps(quality.get('guideline_adherence', [])),
            json.dumps(education.get('teaching_points', [])),
            education.get('clinical_pearls', ''),
            json.dumps(education.get('quiz_questions', [])),
            # Insert values (same as update)
            patient_id,
            clinical_summary.get('chief_complaint', ''),
            clinical_summary.get('clinical_summary', ''),
            json.dumps(clinical_summary),
            json.dumps(diff_dx.get('key_findings', [])),
            json.dumps(diff_dx.get('differential_diagnoses', [])),
            diff_dx.get('diagnostic_reasoning', ''),
            json.dumps(treatment.get('current_treatments', [])),
            treatment.get('treatment_effectiveness', ''),
            json.dumps(treatment.get('evidence_based_recommendations', [])),
            patterns.get('presentation_type', 'typical'),
            json.dumps(patterns.get('rare_disease_indicators', [])),
            patterns.get('anomaly_score', 0.0),
            json.dumps(cost.get('high_cost_indicators', [])),
            cost.get('cost_category', 'medium'),
            json.dumps(quality.get('quality_indicators', [])),
            json.dumps(quality.get('guideline_adherence', [])),
            json.dumps(education.get('teaching_points', [])),
            education.get('clinical_pearls', ''),
            json.dumps(education.get('quiz_questions', []))
        ))
        
        # Save medication analysis
        if results.get('medication_safety'):
            meds = results['medication_safety']
            cursor.execute("""
                MERGE INTO MEDICATION_ANALYSIS ma
                USING (SELECT %s as PATIENT_ID) s
                ON ma.PATIENT_ID = s.PATIENT_ID
                WHEN MATCHED THEN UPDATE SET
                    EXTRACTED_MEDICATIONS = PARSE_JSON(%s),
                    DRUG_INTERACTIONS = PARSE_JSON(%s),
                    CONTRAINDICATIONS = PARSE_JSON(%s),
                    POLYPHARMACY_RISK_SCORE = %s,
                    ANALYSIS_DATE = CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN INSERT (
                    PATIENT_ID, EXTRACTED_MEDICATIONS, DRUG_INTERACTIONS,
                    CONTRAINDICATIONS, POLYPHARMACY_RISK_SCORE
                ) VALUES (%s, PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s), %s)
            """, (
                patient_id,
                json.dumps(meds.get('extracted_medications', [])),
                json.dumps(meds.get('potential_interactions', [])),
                json.dumps(meds.get('contraindications', [])),
                meds.get('polypharmacy_count', 0),
                patient_id,
                json.dumps(meds.get('extracted_medications', [])),
                json.dumps(meds.get('potential_interactions', [])),
                json.dumps(meds.get('contraindications', [])),
                meds.get('polypharmacy_count', 0)
            ))
        
        # Save cost analysis
        if results.get('cost_analysis'):
            cost = results['cost_analysis']
            cursor.execute("""
                MERGE INTO COST_ANALYSIS ca
                USING (SELECT %s as PATIENT_ID) s
                ON ca.PATIENT_ID = s.PATIENT_ID
                WHEN MATCHED THEN UPDATE SET
                    EXTRACTED_PROCEDURES = PARSE_JSON(%s),
                    EXTRACTED_CONDITIONS = PARSE_JSON(%s),
                    HIGH_COST_INDICATORS = PARSE_JSON(%s),
                    ESTIMATED_ENCOUNTER_COST = %s,
                    COST_CATEGORY = %s,
                    COST_DRIVERS = %s,
                    ANALYSIS_DATE = CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN INSERT (
                    PATIENT_ID, EXTRACTED_PROCEDURES, EXTRACTED_CONDITIONS,
                    HIGH_COST_INDICATORS, ESTIMATED_ENCOUNTER_COST,
                    COST_CATEGORY, COST_DRIVERS
                ) VALUES (%s, PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s), %s, %s, %s)
            """, (
                patient_id,
                json.dumps(cost.get('extracted_procedures', [])),
                json.dumps(cost.get('extracted_conditions', [])),
                json.dumps(cost.get('high_cost_indicators', [])),
                cost.get('estimated_encounter_cost', 0),
                cost.get('cost_category', 'medium'),
                cost.get('cost_drivers', ''),
                patient_id,
                json.dumps(cost.get('extracted_procedures', [])),
                json.dumps(cost.get('extracted_conditions', [])),
                json.dumps(cost.get('high_cost_indicators', [])),
                cost.get('estimated_encounter_cost', 0),
                cost.get('cost_category', 'medium'),
                cost.get('cost_drivers', '')
            ))
        
        cursor.close()
        return True
        
    except Exception as e:
        cursor.close()
        print(f"Error saving patient {patient_id}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("Batch Processing All Patients")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
        
        # Create processing batch record
        cursor.execute("""
            INSERT INTO PROCESSING_STATUS 
            (STATUS, TOTAL_PATIENTS, PROCESSED_PATIENTS, FAILED_PATIENTS)
            VALUES ('running', 0, 0, 0)
        """)
        cursor.execute("SELECT LAST_QUERY_ID()")
        batch_id = cursor.fetchone()[0]
        
        # Get patients to process
        print("\nFetching patients from PATIENT_SUBSET...")
        cursor.execute("""
            SELECT PATIENT_ID, PATIENT_UID, PATIENT_NOTES, 
                   SIMILAR_PATIENTS, RELEVANT_ARTICLES
            FROM PATIENT_SUBSET
            WHERE PATIENT_NOTES IS NOT NULL
            ORDER BY PATIENT_ID
        """)
        
        patients = cursor.fetchall()
        total_patients = len(patients)
        print(f"Found {total_patients} patients to process")
        
        # Update batch record
        cursor.execute("""
            UPDATE PROCESSING_STATUS 
            SET TOTAL_PATIENTS = %s
            WHERE BATCH_ID = %s
        """, (total_patients, batch_id))
        
        # Process patients in batches
        processed_count = 0
        failed_count = 0
        batch_size = BATCH_CONFIG['batch_size']
        
        for i in range(0, total_patients, batch_size):
            batch = patients[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total_patients)} of {total_patients})")
            
            # Process each patient in the batch
            for row in batch:
                patient_data = {
                    'PATIENT_ID': row[0],
                    'PATIENT_UID': row[1],
                    'PATIENT_NOTES': row[2],
                    'SIMILAR_PATIENTS': row[3],
                    'RELEVANT_ARTICLES': row[4]
                }
                
                try:
                    # Process all use cases
                    results = process_single_patient(patient_data, conn)
                    
                    # Save results
                    if save_patient_analysis(results, conn):
                        processed_count += 1
                        print(f"✓ Patient {patient_data['PATIENT_ID']} processed successfully")
                    else:
                        failed_count += 1
                        print(f"✗ Patient {patient_data['PATIENT_ID']} save failed")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"✗ Patient {patient_data['PATIENT_ID']} processing failed: {str(e)}")
                    traceback.print_exc()
                
                # Update progress
                if (processed_count + failed_count) % BATCH_CONFIG['progress_update_frequency'] == 0:
                    cursor.execute("""
                        UPDATE PROCESSING_STATUS 
                        SET PROCESSED_PATIENTS = %s, FAILED_PATIENTS = %s
                        WHERE BATCH_ID = %s
                    """, (processed_count, failed_count, batch_id))
                    print(f"\nProgress: {processed_count + failed_count}/{total_patients} " +
                          f"(Success: {processed_count}, Failed: {failed_count})")
        
        # Final update
        cursor.execute("""
            UPDATE PROCESSING_STATUS 
            SET STATUS = 'completed',
                END_TIME = CURRENT_TIMESTAMP(),
                PROCESSED_PATIENTS = %s,
                FAILED_PATIENTS = %s
            WHERE BATCH_ID = %s
        """, (processed_count, failed_count, batch_id))
        
        print("\n" + "="*60)
        print("Batch Processing Complete!")
        print(f"Total processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success rate: {processed_count/total_patients*100:.1f}%")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        traceback.print_exc()
        
        # Update batch status to failed
        try:
            cursor.execute("""
                UPDATE PROCESSING_STATUS 
                SET STATUS = 'failed',
                    END_TIME = CURRENT_TIMESTAMP(),
                    ERROR_DETAILS = PARSE_JSON(%s)
                WHERE BATCH_ID = %s
            """, (json.dumps({"error": str(e)}), batch_id))
        except:
            pass
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()