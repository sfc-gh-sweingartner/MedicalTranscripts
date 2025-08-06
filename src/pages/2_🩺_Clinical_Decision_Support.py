"""
Page 2: Clinical Decision Support
==================================

Primary physician interface for AI-powered clinical insights.
Shows patient summaries, differential diagnoses, and treatment recommendations.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from connection_helper import (
    get_snowflake_connection,
    execute_query,
    safe_execute_query,
    format_sbar_summary,
    parse_json_safely,
    execute_cortex_complete
)

# Page configuration
st.set_page_config(
    page_title="Clinical Decision Support - Healthcare AI Demo",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS for clinical interface
st.markdown("""
<style>
.clinical-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.patient-header {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #0066CC;
    margin-bottom: 1rem;
}

.diagnosis-item {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #0066CC;
}

.treatment-recommendation {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #28a745;
}

.evidence-link {
    color: #0066CC;
    text-decoration: none;
    font-size: 0.875rem;
}

.evidence-link:hover {
    text-decoration: underline;
}

.confidence-high { color: #28a745; font-weight: bold; }
.confidence-medium { color: #ffc107; font-weight: bold; }
.confidence-low { color: #dc3545; font-weight: bold; }

.sbar-section {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background-color: #f8f9fa;
    border-radius: 0.25rem;
}

.similar-patient {
    background-color: #fff3cd;
    padding: 0.75rem;
    border-radius: 0.25rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def search_patients_cortex(search_term, _conn):
    """Search for patients using Cortex AI semantic search"""
    try:
        # First try Cortex-based semantic search
        query = f"""
        SELECT 
            p.PATIENT_ID,
            p.PATIENT_UID,
            p.PATIENT_TITLE,
            p.AGE,
            p.GENDER,
            SUBSTR(p.PATIENT_NOTES, 1, 200) || '...' as NOTES_PREVIEW,
            SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                'Rate how relevant this patient case is to the search term "{search_term}" on a scale of 1-10. Only respond with a number: ' || 
                SUBSTR(p.PATIENT_NOTES, 1, 500)
            ) as RELEVANCE_SCORE
        FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS p
        WHERE p.PATIENT_NOTES IS NOT NULL
        ORDER BY 
            CASE 
                WHEN CAST(p.PATIENT_ID AS STRING) LIKE '%{search_term}%' THEN 1
                WHEN UPPER(p.PATIENT_TITLE) LIKE UPPER('%{search_term}%') THEN 2
                ELSE 3
            END,
            TRY_CAST(RELEVANCE_SCORE AS NUMBER) DESC NULLS LAST
        LIMIT 20
        """
        
        result = safe_execute_query(query, _conn)
        if not result.empty:
            return result
    except Exception as e:
        st.warning(f"Cortex search failed, falling back to basic search: {str(e)}")
    
    # Fallback to basic text search if Cortex fails
    return search_patients_basic(search_term, _conn)

@st.cache_data(ttl=300)
def search_patients_basic(search_term, _conn):
    """Basic text search for patients (fallback)"""
    query = f"""
    SELECT DISTINCT
        p.PATIENT_ID,
        p.PATIENT_UID,
        p.PATIENT_TITLE,
        p.AGE,
        p.GENDER,
        SUBSTR(p.PATIENT_NOTES, 1, 200) || '...' as NOTES_PREVIEW
    FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS p
    WHERE 1=1
        AND (
            CAST(p.PATIENT_ID AS STRING) LIKE '%{search_term}%'
            OR UPPER(p.PATIENT_TITLE) LIKE UPPER('%{search_term}%')
            OR UPPER(p.PATIENT_NOTES) LIKE UPPER('%{search_term}%')
        )
    ORDER BY 
        CASE 
            WHEN CAST(p.PATIENT_ID AS STRING) LIKE '%{search_term}%' THEN 1
            WHEN UPPER(p.PATIENT_TITLE) LIKE UPPER('%{search_term}%') THEN 2
            ELSE 3
        END
    LIMIT 20
    """
    return safe_execute_query(query, _conn)

@st.cache_data(ttl=300)
def get_patient_details(patient_id, _conn):
    """Get full patient details including notes"""
    query = f"""
    SELECT 
        PATIENT_ID,
        PATIENT_UID,
        PATIENT_TITLE,
        AGE,
        GENDER,
        PATIENT_NOTES,
        SIMILAR_PATIENTS,
        RELEVANT_ARTICLES
    FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
    WHERE PATIENT_ID = {patient_id}
    """
    return safe_execute_query(query, _conn)

@st.cache_data(ttl=300)
def get_patient_analysis(patient_id, _conn):
    """Get pre-computed analysis if available"""
    query = f"""
    SELECT *
    FROM HEALTHCARE_DEMO.MEDICAL_NOTES.PATIENT_ANALYSIS
    WHERE PATIENT_ID = {patient_id}
    """
    return safe_execute_query(query, _conn)

def generate_clinical_summary(patient_notes, conn):
    """Generate SBAR clinical summary using Cortex AI"""
    prompt = f"""
    You are an experienced physician creating a clinical summary.
    
    Create an SBAR (Situation, Background, Assessment, Recommendation) summary from these patient notes:
    
    {patient_notes[:2000]}  # Limit to first 2000 chars for prompt
    
    Format your response as a JSON object with exactly these keys:
    {{
        "situation": "Current clinical situation in 1-2 sentences",
        "background": "Relevant medical history and context",
        "assessment": "Current diagnosis and clinical status",
        "recommendation": "Next steps and treatment plan"
    }}
    
    Be concise but comprehensive. Focus on clinically relevant information.
    """
    
    try:
        response = execute_cortex_complete(prompt, "mistral-large", conn)
        # Parse the response
        if response:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        return None
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def generate_differential_diagnosis(patient_notes, similar_patients, conn):
    """Generate differential diagnosis using AI"""
    prompt = f"""
    You are an expert diagnostician analyzing a patient case.
    
    Patient Notes:
    {patient_notes[:1500]}
    
    Based on these findings, provide 5 differential diagnoses.
    
    Format your response as a JSON array with exactly this structure:
    [
        {{
            "diagnosis": "Diagnosis name",
            "confidence": "HIGH/MEDIUM/LOW",
            "evidence": "Key supporting findings from the notes",
            "discriminating_features": "What distinguishes this from other diagnoses"
        }}
    ]
    
    Order by likelihood, with most likely first.
    """
    
    try:
        response = execute_cortex_complete(prompt, "mixtral-8x7b", conn)
        if response:
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        return []
    except Exception as e:
        st.error(f"Error generating diagnoses: {str(e)}")
        return []

def display_patient_header(patient_data):
    """Display patient header information"""
    if patient_data.empty:
        return
    
    patient = patient_data.iloc[0]
    
    st.markdown(f"""
    <div class="patient-header">
        <h3>Patient {patient['PATIENT_ID']}</h3>
        <strong>{patient['PATIENT_TITLE']}</strong><br>
        Age: {patient['AGE']} | Gender: {patient['GENDER']} | UID: {patient['PATIENT_UID']}
    </div>
    """, unsafe_allow_html=True)

def display_sbar_summary(sbar_data):
    """Display SBAR summary in clinical format"""
    if not sbar_data:
        st.info("No clinical summary available. Click 'Generate Clinical Summary' to create one.")
        return
    
    st.markdown("### 📋 Clinical Summary (SBAR Format)")
    
    sections = [
        ("Situation", sbar_data.get("situation", "Not available")),
        ("Background", sbar_data.get("background", "Not available")),
        ("Assessment", sbar_data.get("assessment", "Not available")),
        ("Recommendation", sbar_data.get("recommendation", "Not available"))
    ]
    
    for title, content in sections:
        st.markdown(f"""
        <div class="sbar-section">
            <strong>{title}:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def display_differential_diagnoses(diagnoses):
    """Display differential diagnoses"""
    if not diagnoses:
        st.info("No differential diagnoses available. Click 'Generate Diagnoses' to create them.")
        return
    
    st.markdown("### 🔍 Differential Diagnoses")
    
    for i, dx in enumerate(diagnoses, 1):
        confidence_class = f"confidence-{dx.get('confidence', 'MEDIUM').lower()}"
        
        st.markdown(f"""
        <div class="diagnosis-item">
            <strong>{i}. {dx.get('diagnosis', 'Unknown')}</strong> 
            <span class="{confidence_class}">({dx.get('confidence', 'MEDIUM')} confidence)</span><br>
            <strong>Evidence:</strong> {dx.get('evidence', 'No evidence provided')}<br>
            <strong>Discriminating Features:</strong> {dx.get('discriminating_features', 'None specified')}
        </div>
        """, unsafe_allow_html=True)

def display_similar_patients(similar_patients_json, conn):
    """Display similar patient cases"""
    if not similar_patients_json:
        return
    
    try:
        similar = parse_json_safely(similar_patients_json, {})
        
        # Handle different formats - could be dict or list
        if isinstance(similar, dict) and len(similar) > 0:
            st.markdown("### 👥 Similar Patient Cases")
            
            # Convert dict to list of tuples and sort by score (descending)
            similar_items = list(similar.items())
            # Sort by score if scores are numeric, otherwise keep original order
            try:
                similar_items.sort(key=lambda x: float(x[1]), reverse=True)
            except (ValueError, TypeError):
                pass  # Keep original order if scores aren't numeric
            
            # Show top 3 similar patients
            for i, (patient_key, score) in enumerate(similar_items[:3]):
                # Extract patient ID from key (handle formats like "6077966-1" -> "6077966")
                try:
                    patient_id = patient_key.split('-')[0] if '-' in str(patient_key) else str(patient_key)
                    patient_id = int(patient_id)
                except (ValueError, AttributeError):
                    continue  # Skip if we can't parse the patient ID
                
                # Get basic info about similar patient
                query = f"""
                SELECT PATIENT_TITLE, AGE, GENDER
                FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
                WHERE PATIENT_ID = {patient_id}
                """
                similar_data = safe_execute_query(query, conn)
                
                if not similar_data.empty:
                    sim_patient = similar_data.iloc[0]
                    # Format score for display
                    score_display = f"{float(score):.2f}" if isinstance(score, (int, float)) else str(score)
                    
                    st.markdown(f"""
                    <div class="similar-patient">
                        <strong>Similar Case #{i+1}</strong> (Similarity: {score_display})<br>
                        Patient ID: {patient_id}<br>
                        {sim_patient['PATIENT_TITLE'][:100]}...<br>
                        Age: {sim_patient['AGE']} | Gender: {sim_patient['GENDER']}
                    </div>
                    """, unsafe_allow_html=True)
        
        elif isinstance(similar, list) and len(similar) > 0:
            st.markdown("### 👥 Similar Patient Cases")
            
            # Handle list format (legacy support)
            for i, item in enumerate(similar[:3]):
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    patient_id, score = item[0], item[1]
                else:
                    continue  # Skip malformed items
                
                # Get basic info about similar patient
                query = f"""
                SELECT PATIENT_TITLE, AGE, GENDER
                FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
                WHERE PATIENT_ID = {patient_id}
                """
                similar_data = safe_execute_query(query, conn)
                
                if not similar_data.empty:
                    sim_patient = similar_data.iloc[0]
                    st.markdown(f"""
                    <div class="similar-patient">
                        <strong>Similar Case #{i+1}</strong> (Similarity: {score:.2f})<br>
                        Patient ID: {patient_id}<br>
                        {sim_patient['PATIENT_TITLE'][:100]}...<br>
                        Age: {sim_patient['AGE']} | Gender: {sim_patient['GENDER']}
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying similar patients: {str(e)}")

def main():
    """Main page function"""
    st.title("🩺 Clinical Decision Support")
    st.markdown("AI-powered clinical insights for improved patient care")
    
    # Get connection
    conn = get_snowflake_connection()
    if conn is None:
        st.error("Unable to connect to Snowflake. Please check your configuration.")
        st.stop()
    
    # Patient search section
    st.markdown("---")
    st.markdown("## 🔍 Patient Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "🤖 AI-Powered Patient Search",
            placeholder="e.g., cardiac issues, seizure disorders, rare tumors, hypertension",
            key="patient_search",
            help="Uses Snowflake Cortex AI for semantic search through patient notes"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    # Initialize search results in session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = pd.DataFrame()
    if 'last_search_term' not in st.session_state:
        st.session_state.last_search_term = ""
    
    # Perform search when button is clicked
    if search_term and search_button:
        with st.spinner("🔍 Searching patients with Cortex AI..."):
            st.session_state.search_results = search_patients_cortex(search_term, conn)
            st.session_state.last_search_term = search_term
    
    # Display search results if available
    if not st.session_state.search_results.empty and st.session_state.last_search_term:
        st.markdown(f"### Found {len(st.session_state.search_results)} patients for '{st.session_state.last_search_term}'")
        
        # Add clear results button
        if st.button("🗑️ Clear Search Results", key="clear_search"):
            st.session_state.search_results = pd.DataFrame()
            st.session_state.last_search_term = ""
            st.rerun()
        
        # Display results in a selectable format
        for _, patient in st.session_state.search_results.iterrows():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Show relevance score if available (from Cortex search)
                relevance_info = ""
                if 'RELEVANCE_SCORE' in patient and patient['RELEVANCE_SCORE']:
                    try:
                        score = float(patient['RELEVANCE_SCORE'])
                        if score >= 7:
                            relevance_info = f" 🎯 Relevance: {score}/10"
                        elif score >= 5:
                            relevance_info = f" 📊 Relevance: {score}/10"
                        else:
                            relevance_info = f" 📋 Relevance: {score}/10"
                    except (ValueError, TypeError):
                        pass
                
                st.markdown(f"""
                **Patient {patient['PATIENT_ID']}**: {patient['PATIENT_TITLE'][:80]}...{relevance_info}  
                Age: {patient['AGE']} | Gender: {patient['GENDER']}
                """)
            
            with col2:
                if st.button("Select", key=f"select_{patient['PATIENT_ID']}"):
                    st.session_state.selected_patient_id = patient['PATIENT_ID']
                    # Clear search results after selection
                    st.session_state.search_results = pd.DataFrame()
                    st.session_state.last_search_term = ""
                    st.rerun()
    elif search_term and search_button and st.session_state.search_results.empty:
        st.warning("No patients found matching your search criteria.")
    
    # Quick access to demo scenarios
    st.markdown("---")
    st.markdown("## 🎯 Demo Scenarios")
    
    demo_scenarios = [
        (163844, "Complex Diagnosis", "66-year-old with seizures and cardiac arrhythmia"),
        (163840, "Pediatric Rare Disease", "11-year-old with multicentric peripheral ossifying fibroma"),
        (163841, "Treatment Analysis", "41-year-old female with odontogenic myxoma")
    ]
    
    cols = st.columns(3)
    for i, (patient_id, title, desc) in enumerate(demo_scenarios):
        with cols[i]:
            if st.button(f"{title}\n{desc}", key=f"demo_{patient_id}", use_container_width=True):
                st.session_state.selected_patient_id = patient_id
                st.rerun()
    
    # Display selected patient details
    if 'selected_patient_id' in st.session_state:
        patient_id = st.session_state.selected_patient_id
        
        st.markdown("---")
        
        # Get patient data
        patient_data = get_patient_details(patient_id, conn)
        
        if not patient_data.empty:
            patient = patient_data.iloc[0]
            
            # Display patient header
            display_patient_header(patient_data)
            
            # Check for pre-computed analysis
            analysis_data = get_patient_analysis(patient_id, conn)
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Clinical Summary",
                "🔍 Differential Diagnosis", 
                "💊 Treatment Analysis",
                "📚 Evidence & Literature"
            ])
            
            with tab1:
                # Clinical Summary (SBAR)
                if not analysis_data.empty and analysis_data.iloc[0]['SBAR_SUMMARY']:
                    sbar_data = parse_json_safely(analysis_data.iloc[0]['SBAR_SUMMARY'])
                    display_sbar_summary(sbar_data)
                else:
                    st.info("No pre-computed summary available.")
                    if st.button("Generate Clinical Summary", key="gen_summary"):
                        with st.spinner("Generating clinical summary..."):
                            sbar_data = generate_clinical_summary(patient['PATIENT_NOTES'], conn)
                            if sbar_data:
                                display_sbar_summary(sbar_data)
                                # TODO: Save to database
                            else:
                                st.error("Failed to generate summary.")
                
                # Show clinical notes
                with st.expander("View Full Clinical Notes"):
                    st.text(patient['PATIENT_NOTES'])
            
            with tab2:
                # Differential Diagnosis
                if not analysis_data.empty and analysis_data.iloc[0]['DIFFERENTIAL_DIAGNOSES']:
                    diagnoses = parse_json_safely(analysis_data.iloc[0]['DIFFERENTIAL_DIAGNOSES'], [])
                    display_differential_diagnoses(diagnoses)
                else:
                    st.info("No pre-computed diagnoses available.")
                    if st.button("Generate Differential Diagnoses", key="gen_dx"):
                        with st.spinner("Analyzing patient case..."):
                            diagnoses = generate_differential_diagnosis(
                                patient['PATIENT_NOTES'],
                                patient['SIMILAR_PATIENTS'],
                                conn
                            )
                            if diagnoses:
                                display_differential_diagnoses(diagnoses)
                            else:
                                st.error("Failed to generate diagnoses.")
                
                # Show similar patients
                display_similar_patients(patient['SIMILAR_PATIENTS'], conn)
            
            with tab3:
                # Treatment Analysis
                st.info("Treatment analysis will compare treatments across similar patients.")
                st.markdown("🚧 This feature is coming soon in the next phase of development.")
            
            with tab4:
                # Evidence & Literature
                st.markdown("### 📚 Relevant Medical Literature")
                
                if patient['RELEVANT_ARTICLES']:
                    articles = parse_json_safely(patient['RELEVANT_ARTICLES'], {})
                    if articles:
                        st.markdown("Articles related to this case:")
                        # Handle both dict and list formats
                        if isinstance(articles, dict):
                            # Convert dict to list of tuples and take top 5
                            article_items = list(articles.items())[:5]
                        else:
                            # Assume it's already a list
                            article_items = articles[:5]
                        
                        for i, (pmid, score) in enumerate(article_items):
                            # Handle score formatting
                            score_display = f"{float(score):.2f}" if isinstance(score, (int, float)) else str(score)
                            st.markdown(f"""
                            {i+1}. PMID: [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) 
                            (Relevance Score: {score_display})
                            """)
                else:
                    st.info("No related articles found for this case.")
        else:
            st.error(f"Patient {patient_id} not found in database.")
    else:
        # No patient selected
        st.info("👆 Search for a patient or select a demo scenario to begin.")

if __name__ == "__main__":
    main()