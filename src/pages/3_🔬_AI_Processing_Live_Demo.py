"""
Page 3: AI Processing Live Demo
================================

Real-time medical note analysis with editable text.
Based on the successful superannuation demo pattern.
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from connection_helper import (
    get_snowflake_connection,
    execute_query,
    safe_execute_query,
    execute_cortex_complete,
    log_realtime_analysis,
    get_sample_patients
)

# Page configuration
st.set_page_config(
    page_title="AI Processing Live Demo - Healthcare AI",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS for demo styling
st.markdown("""
<style>
.processing-pipeline {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}

.pipeline-step {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    margin: 0.25rem 0;
    background-color: #e9ecef;
    border-radius: 0.25rem;
}

.pipeline-step.active {
    background-color: #d4edda;
    border-left: 3px solid #28a745;
}

.pipeline-step.completed {
    background-color: #d1ecf1;
    border-left: 3px solid #17a2b8;
}

.note-editor {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 2px solid #007bff;
    font-family: 'Courier New', monospace;
    margin: 1rem 0;
}

.demo-button {
    background-color: #007bff;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    border: none;
    font-weight: bold;
    margin: 0.5rem;
    cursor: pointer;
}

.demo-button:hover {
    background-color: #0056b3;
}

.ai-result {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #007bff;
    margin: 0.5rem 0;
}

.metric-card {
    background-color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
}

.processing-time {
    color: #6c757d;
    font-size: 0.875rem;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = {}
if 'current_note' not in st.session_state:
    st.session_state.current_note = ""
if 'processing_stage' not in st.session_state:
    st.session_state.processing_stage = None
if 'selected_demo_patient' not in st.session_state:
    st.session_state.selected_demo_patient = None

def get_demo_patient_notes():
    """Get pre-defined demo patient notes"""
    return {
        "Complex Cardiac Case": {
            "id": 163844,
            "notes": """A 66-year-old gentleman presented to the emergency department with new-onset seizures and cardiac arrhythmia. 
            Patient has a history of hypertension, diabetes mellitus type 2, and hyperlipidemia. 
            He experienced a witnessed tonic-clonic seizure lasting approximately 2 minutes, followed by post-ictal confusion. 
            ECG revealed atrial fibrillation with rapid ventricular response. 
            CT head showed no acute intracranial abnormality. 
            Laboratory results showed hyponatremia (Na 128), elevated troponin (0.8), and BNP of 450.
            Patient was loaded with phenytoin and started on diltiazem for rate control.
            Cardiology and neurology consultations were obtained."""
        },
        "Pediatric Rare Disease": {
            "id": 163840,
            "notes": """An 11-year-old boy presented with multiple gingival masses in the maxillary region. 
            The lesions appeared 2 months ago and have been slowly growing. 
            No pain or bleeding reported. No history of trauma. 
            Oral examination revealed firm, pedunculated masses on the buccal gingiva bilaterally.
            Radiographic examination showed superficial erosion of underlying alveolar bone.
            Excisional biopsy was performed. 
            Histopathology revealed cellular fibrous connective tissue with formation of bone trabeculae.
            Diagnosis: Multicentric peripheral ossifying fibroma - a rare presentation in pediatric patients.
            Complete excision with periosteal curettage was performed to prevent recurrence."""
        },
        "Custom Patient Note": {
            "id": 0,
            "notes": "Enter or paste your own patient note here for analysis..."
        }
    }

def process_medical_note(note_text, patient_id, conn):
    """Process medical note through multiple AI analyses"""
    results = {}
    start_time = time.time()
    
    # Update processing stage
    def update_stage(stage, progress):
        st.session_state.processing_stage = stage
        progress_bar.progress(progress)
        status_text.text(f"🔄 {stage}...")
        time.sleep(0.5)  # For demo effect
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Stage 1: Extract Clinical Information
        update_stage("Extracting Clinical Information", 0.2)
        
        extraction_prompt = f"""
        Extract key clinical information from this patient note:
        
        {note_text[:1500]}
        
        Provide a JSON response with:
        {{
            "chief_complaint": "Main reason for visit",
            "key_symptoms": ["symptom1", "symptom2", ...],
            "vital_signs": {{"sign": "value"}},
            "lab_results": {{"test": "result"}},
            "medications": ["med1", "med2", ...],
            "medical_history": ["condition1", "condition2", ...]
        }}
        """
        
        extraction_result = execute_cortex_complete(extraction_prompt, "mistral-large", conn)
        
        # Parse extraction results
        try:
            import re
            json_match = re.search(r'\{.*\}', extraction_result, re.DOTALL)
            if json_match:
                results['extraction'] = json.loads(json_match.group())
            else:
                results['extraction'] = {"error": "Could not parse extraction results"}
        except:
            results['extraction'] = {"raw": extraction_result}
        
        # Stage 2: Generate Clinical Summary
        update_stage("Generating Clinical Summary", 0.4)
        
        summary_prompt = f"""
        Create a concise clinical summary of this patient encounter:
        
        {note_text[:1500]}
        
        Format as a brief paragraph highlighting the most important clinical findings and actions taken.
        """
        
        results['summary'] = execute_cortex_complete(summary_prompt, "mistral-large", conn)
        
        # Stage 3: Risk Assessment
        update_stage("Performing Risk Assessment", 0.6)
        
        risk_prompt = f"""
        Assess clinical risks for this patient based on the notes:
        
        {note_text[:1500]}
        
        Identify:
        1. Immediate risks requiring urgent attention
        2. Short-term risks (next 24-48 hours)
        3. Long-term risks requiring follow-up
        
        Format as JSON with risk_level (HIGH/MEDIUM/LOW) for each category.
        """
        
        risk_result = execute_cortex_complete(risk_prompt, "mixtral-8x7b", conn)
        results['risk_assessment'] = risk_result
        
        # Stage 4: Clinical Recommendations
        update_stage("Generating Clinical Recommendations", 0.8)
        
        recommendation_prompt = f"""
        Based on this patient's presentation, provide clinical recommendations:
        
        {note_text[:1500]}
        
        Include:
        1. Immediate actions required
        2. Diagnostic tests to consider
        3. Specialist consultations needed
        4. Follow-up care plan
        """
        
        results['recommendations'] = execute_cortex_complete(recommendation_prompt, "mixtral-8x7b", conn)
        
        # Stage 5: Complete Processing
        update_stage("Analysis Complete", 1.0)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        results['processing_time'] = processing_time
        
        # Log the analysis
        log_realtime_analysis(
            session_id=st.session_state.get('session_id', 'demo'),
            user_name='demo_user',
            patient_id=patient_id,
            original_text=note_text[:500],
            modified_text=note_text[:500],
            analysis_type='full',
            ai_model='cortex-multiple',
            processing_time_ms=int(processing_time * 1000),
            results=results,
            success=True,
            conn=conn
        )
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return results
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error during processing: {str(e)}")
        return None

def display_results(results):
    """Display processing results in an organized format"""
    if not results:
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️ Processing Time</h3>
            <h2>{:.1f}s</h2>
        </div>
        """.format(results.get('processing_time', 0)), unsafe_allow_html=True)
    
    with col2:
        extraction = results.get('extraction', {})
        symptom_count = len(extraction.get('key_symptoms', []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔍 Symptoms Found</h3>
            <h2>{symptom_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        extraction = results.get('extraction', {})
        med_count = len(extraction.get('medications', []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>💊 Medications</h3>
            <h2>{med_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ AI Models Used</h3>
            <h2>3</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Display detailed results in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Extracted Information",
        "📝 Clinical Summary",
        "⚠️ Risk Assessment",
        "💡 Recommendations"
    ])
    
    with tab1:
        extraction = results.get('extraction', {})
        if isinstance(extraction, dict) and 'error' not in extraction:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Chief Complaint:**")
                st.info(extraction.get('chief_complaint', 'Not identified'))
                
                st.markdown("**Key Symptoms:**")
                symptoms = extraction.get('key_symptoms', [])
                if symptoms:
                    for symptom in symptoms:
                        st.write(f"• {symptom}")
                else:
                    st.write("No symptoms extracted")
                
                st.markdown("**Medical History:**")
                history = extraction.get('medical_history', [])
                if history:
                    for item in history:
                        st.write(f"• {item}")
                else:
                    st.write("No history extracted")
            
            with col2:
                st.markdown("**Vital Signs:**")
                vitals = extraction.get('vital_signs', {})
                if vitals:
                    for sign, value in vitals.items():
                        st.write(f"• {sign}: {value}")
                else:
                    st.write("No vital signs extracted")
                
                st.markdown("**Lab Results:**")
                labs = extraction.get('lab_results', {})
                if labs:
                    for test, result in labs.items():
                        st.write(f"• {test}: {result}")
                else:
                    st.write("No lab results extracted")
                
                st.markdown("**Medications:**")
                meds = extraction.get('medications', [])
                if meds:
                    for med in meds:
                        st.write(f"• {med}")
                else:
                    st.write("No medications extracted")
        else:
            st.json(extraction)
    
    with tab2:
        st.markdown("### Clinical Summary")
        st.markdown(f"""
        <div class="ai-result">
        {results.get('summary', 'No summary generated')}
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Risk Assessment")
        risk_text = results.get('risk_assessment', 'No risk assessment generated')
        
        # Check if the text already contains HTML (AI returned formatted HTML)
        if '<div' in risk_text or '<h4' in risk_text:
            # AI returned formatted HTML - display it directly without additional wrapper
            st.markdown(risk_text, unsafe_allow_html=True)
        else:
            # Try to parse and format JSON risk assessment
            try:
                import re
                json_match = re.search(r'\{.*\}', risk_text, re.DOTALL)
                if json_match:
                    risk_data = json.loads(json_match.group())
                    
                    # Format the risk assessment nicely
                    formatted_risk = ""
                    
                    for risk_category, details in risk_data.items():
                        if isinstance(details, dict):
                            risk_level = details.get('risk_level', 'UNKNOWN')
                            risks = details.get('risks', [])
                            
                            # Format category name
                            category_name = risk_category.replace('_', ' ').title()
                            
                            # Choose emoji and color based on risk level
                            if risk_level == 'HIGH':
                                emoji = "🔴"
                                color = "#dc3545"
                            elif risk_level == 'MEDIUM':
                                emoji = "🟡"
                                color = "#ffc107"
                            else:
                                emoji = "🟢"
                                color = "#28a745"
                            
                            formatted_risk += f"""
                            <div style="margin-bottom: 1rem;">
                            <h4 style="color: {color};">{emoji} {category_name} (Risk Level: {risk_level})</h4>
                            <ul>
                            """
                            
                            for risk in risks:
                                formatted_risk += f"<li>{risk}</li>"
                            
                            formatted_risk += "</ul></div>"
                    
                    # Look for additional notes after the JSON
                    remaining_text = risk_text[json_match.end():].strip()
                    if remaining_text:
                        formatted_risk += f"<div style='margin-top: 1rem; font-style: italic;'>{remaining_text}</div>"
                    
                    st.markdown(f"""
                    <div class="ai-result">
                    {formatted_risk}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # No JSON found, treat as plain text and format it nicely
                    # Split by newlines and format as simple text
                    formatted_text = risk_text.replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="ai-result">
                    {formatted_text}
                    </div>
                    """, unsafe_allow_html=True)
            except (json.JSONDecodeError, Exception):
                # Fallback to original text if parsing fails
                formatted_text = risk_text.replace('\n', '<br>')
                st.markdown(f"""
                <div class="ai-result">
                {formatted_text}
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### Clinical Recommendations")
        recommendations = results.get('recommendations', 'No recommendations generated')
        st.markdown(f"""
        <div class="ai-result">
        {recommendations}
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main function for the live demo page"""
    st.title("🔬 AI Processing Live Demo")
    st.markdown("Watch medical notes being analyzed in real-time with Snowflake Cortex AI")
    
    # Get connection
    conn = get_snowflake_connection()
    if conn is None:
        st.error("Unable to connect to Snowflake. Please check your configuration.")
        st.stop()
    
    # Instructions
    with st.expander("📖 How to use this demo", expanded=True):
        st.markdown("""
        1. **Select a demo patient** or choose "Custom Patient Note" to enter your own text
        2. **Edit the note** - modify any part of the text to show the AI handles any input
        3. **Click Process** to watch the AI analyze the note in real-time
        4. **Review results** across multiple AI-powered analyses
        
        This demonstrates how Snowflake Cortex AI can process unstructured medical text and extract 
        clinically relevant insights in seconds.
        """)
    
    st.markdown("---")
    
    # Patient selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 1️⃣ Select Patient Note")
        demo_patients = get_demo_patient_notes()
        selected_patient = st.radio(
            "Choose a demo scenario:",
            list(demo_patients.keys()),
            key="patient_selector"
        )
        
        patient_info = demo_patients[selected_patient]
        st.session_state.selected_demo_patient = patient_info
        
        if patient_info['id'] > 0:
            st.info(f"Patient ID: {patient_info['id']}")
    
    with col2:
        st.markdown("### 2️⃣ Edit Patient Note")
        st.markdown("*Feel free to modify the text to demonstrate flexibility*")
        
        # Text editor
        edited_note = st.text_area(
            "Patient Note:",
            value=patient_info['notes'],
            height=300,
            key="note_editor"
        )
        
        # Character count
        char_count = len(edited_note)
        st.caption(f"Character count: {char_count}")
    
    st.markdown("---")
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Process with AI", type="primary", use_container_width=True):
            if edited_note and len(edited_note) > 50:
                # Store the note
                st.session_state.current_note = edited_note
                
                # Process the note
                with st.container():
                    st.markdown("### 🤖 AI Processing Pipeline")
                    
                    results = process_medical_note(
                        edited_note,
                        patient_info['id'],
                        conn
                    )
                    
                    if results:
                        st.session_state.processing_results = results
                        st.success("✅ Analysis complete!")
                        st.balloons()
                    else:
                        st.error("❌ Processing failed. Please try again.")
            else:
                st.warning("Please enter a patient note with at least 50 characters.")
    
    # Display results if available
    if st.session_state.processing_results:
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        display_results(st.session_state.processing_results)
        
        # Download results button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            results_json = json.dumps(st.session_state.processing_results, indent=2)
            st.download_button(
                label="📥 Download Results (JSON)",
                data=results_json,
                file_name=f"medical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()