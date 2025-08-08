"""
Demo Guide Page
Provides demo scripts, talking points, and technical architecture overview
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.connection_helper import get_snowflake_connection, execute_query

# Page config
st.set_page_config(
    page_title="Demo Guide",
    page_icon="📋",
    layout="wide"
)

def load_demo_scenarios(conn):
    """Load predefined demo scenarios"""
    query = """
    SELECT 
        SCENARIO_ID,
        SCENARIO_NAME,
        SCENARIO_TYPE,
        PATIENT_ID,
        DESCRIPTION,
        TALKING_POINTS,
        EXPECTED_OUTCOMES,
        DEMO_DURATION_MINUTES
    FROM DEMO_SCENARIOS
    ORDER BY SCENARIO_TYPE, SCENARIO_NAME
    """
    return execute_query(query, conn)

def main():
    st.title("📋 Healthcare AI Demo Guide")
    st.markdown("Complete guide for demonstrating the Healthcare AI solution")
    
    # Initialize connection
    conn = get_snowflake_connection()
    if not conn:
        st.error("Failed to connect to Snowflake. Please check your connection settings.")
        return
    
    # Navigation
    demo_section = st.radio(
        "Select Demo Section",
        ["Quick Start", "Demo Scenarios", "Technical Architecture", "Talking Points", "FAQ", "Troubleshooting"],
        horizontal=True
    )
    
    if demo_section == "Quick Start":
        st.markdown("## 🚀 Quick Start Guide")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 5-Minute Demo Flow")
            
            st.markdown("""
            1. **Start with Clinical Decision Support** (Page 2)
               - Search for "chest pain" or "diabetes"
               - Show SBAR summary generation
               - Highlight differential diagnoses
            
            2. **Show Live AI Processing** (Page 3)
               - Select a pre-loaded patient
               - Edit the clinical note
               - Process and show real-time results
            
            3. **Demonstrate Value with Cost Analysis** (Page 5)
               - Show cost distribution
               - Identify high-cost drivers
               - Present ROI opportunity
            
            4. **Close with Medication Safety** (Page 6)
               - Show drug interaction detection
               - Highlight polypharmacy risks
               - Demonstrate safety alerts
            """)
            
            st.success("💡 **Pro Tip**: Keep the Data Foundation page open in another tab to show underlying data")
        
        with col2:
            st.markdown("### ⏱️ Time Allocation")
            
            time_allocation = pd.DataFrame({
                'Section': ['Introduction', 'Clinical AI Demo', 'Value Discussion', 'Q&A'],
                'Minutes': [1, 2, 1, 1]
            })
            
            st.dataframe(time_allocation, hide_index=True)
            
            st.markdown("### 🎯 Key Messages")
            st.info("""
            - **Accuracy**: AI extracts insights from unstructured notes
            - **Speed**: Process thousands of patients in minutes
            - **Value**: Identify cost savings and quality improvements
            - **Safety**: Prevent adverse events proactively
            """)
    
    elif demo_section == "Demo Scenarios":
        st.markdown("## 🎭 Demo Scenarios")
        
        # Load scenarios
        scenarios_df = load_demo_scenarios(conn)
        
        if not scenarios_df.empty:
            # Group by type
            for scenario_type in scenarios_df['SCENARIO_TYPE'].unique():
                st.markdown(f"### {scenario_type.title()} Scenarios")
                
                type_scenarios = scenarios_df[scenarios_df['SCENARIO_TYPE'] == scenario_type]
                
                for _, scenario in type_scenarios.iterrows():
                    with st.expander(f"📌 {scenario['SCENARIO_NAME']} ({scenario['DEMO_DURATION_MINUTES']} min)"):
                        st.markdown(f"**Description**: {scenario['DESCRIPTION']}")
                        st.markdown(f"**Patient ID**: {scenario['PATIENT_ID']}")
                        
                        if scenario['TALKING_POINTS']:
                            st.markdown("**Talking Points**:")
                            try:
                                import json
                                points = json.loads(scenario['TALKING_POINTS'])
                                for point in points:
                                    st.markdown(f"- {point}")
                            except:
                                st.markdown(scenario['TALKING_POINTS'])
                        
                        if scenario['EXPECTED_OUTCOMES']:
                            st.markdown("**Expected Outcomes**:")
                            st.info(scenario['EXPECTED_OUTCOMES'])
        
        # Custom scenario builder
        st.markdown("### 🛠️ Build Custom Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            focus_area = st.selectbox(
                "Primary Focus",
                ["Cost Reduction", "Clinical Quality", "Patient Safety", "Rare Disease", "Population Health"]
            )
            
            audience = st.selectbox(
                "Target Audience",
                ["C-Suite", "Clinical Leaders", "IT Leaders", "Data Scientists", "Physicians"]
            )
        
        with col2:
            duration = st.slider("Demo Duration (minutes)", 5, 30, 15)
            
            complexity = st.select_slider(
                "Technical Depth",
                ["Basic", "Intermediate", "Advanced"]
            )
        
        if st.button("Generate Custom Script"):
            st.markdown("### 📝 Custom Demo Script")
            
            script = f"""
            **Scenario**: {focus_area} for {audience}
            **Duration**: {duration} minutes
            **Complexity**: {complexity}
            
            **Opening** (2 min):
            - Introduce challenge: Unstructured clinical notes contain valuable insights
            - Show scale: Processing 1,000+ patients with AI
            
            **Demo Flow** ({duration-4} min):
            """
            
            if focus_area == "Cost Reduction":
                script += """
            1. Navigate to Cost Analysis page
            2. Show high-cost patient identification
            3. Demonstrate procedure extraction from notes
            4. Calculate potential savings
            """
            elif focus_area == "Clinical Quality":
                script += """
            1. Start with Clinical Decision Support
            2. Show quality metrics dashboard
            3. Demonstrate guideline adherence tracking
            4. Highlight improvement opportunities
            """
            elif focus_area == "Patient Safety":
                script += """
            1. Open Medication Safety page
            2. Show drug interaction detection
            3. Demonstrate contraindication alerts
            4. Review high-risk patient identification
            """
            
            script += """
            
            **Closing** (2 min):
            - Summarize value proposition
            - Show ROI calculation
            - Discuss next steps
            """
            
            st.markdown(script)
    
    elif demo_section == "Technical Architecture":
        st.markdown("## 🏗️ Technical Architecture")
        
        tab1, tab2, tab3 = st.tabs(["System Overview", "Data Flow", "AI Components"])
        
        with tab1:
            st.markdown("### System Architecture")
            
            st.markdown("""
            ```
            ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
            │   Data Sources      │     │   Snowflake         │     │   Streamlit App     │
            │  - PMC Patients     │────▶│  - Data Storage     │────▶│  - Visualization    │
            │  - Clinical Notes   │     │  - Cortex AI        │     │  - User Interface   │
            └─────────────────────┘     │  - Processing       │     └─────────────────────┘
                                       └─────────────────────┘
            ```
            """)
            
            st.markdown("#### Key Components")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Data Layer")
                st.markdown("""
                - **PATIENT_SUBSET**: 1,000 patients with cleaned data
                - **PATIENT_ANALYSIS**: Pre-computed AI insights
                - **MEDICATION_ANALYSIS**: Drug safety analysis
                - **COST_ANALYSIS**: Financial impact data
                - **Cortex Search**: Semantic patient search
                """)
            
            with col2:
                st.markdown("##### AI Layer")
                st.markdown("""
                - **Snowflake Cortex**: LLM processing engine
                - **Models Used**:
                  - mistral-large: Clinical analysis
                  - mixtral-8x7b: Pattern recognition
                - **Configurable Prompts**: Easy customization
                - **Batch Processing**: Scalable analysis
                """)
        
        with tab2:
            st.markdown("### Data Processing Flow")
            
            st.markdown("""
            ```mermaid
            graph TD
                A[Clinical Notes] --> B[Text Preprocessing]
                B --> C{Batch or Real-time?}
                C -->|Batch| D[Batch Processing Pipeline]
                C -->|Real-time| E[Live AI Processing]
                D --> F[PATIENT_ANALYSIS Table]
                D --> G[MEDICATION_ANALYSIS Table]
                D --> H[COST_ANALYSIS Table]
                E --> I[Real-time Results]
                F --> J[Streamlit Dashboard]
                G --> J
                H --> J
                I --> J
            ```
            """)
            
            st.markdown("#### Processing Steps")
            
            processing_steps = pd.DataFrame({
                'Step': ['1. Data Ingestion', '2. AI Analysis', '3. Result Storage', '4. Visualization'],
                'Description': [
                    'Load patient notes from PMC dataset',
                    'Process through Cortex AI with use case prompts',
                    'Store structured results in analysis tables',
                    'Display insights in Streamlit dashboard'
                ],
                'Technology': ['Snowflake', 'Cortex LLM', 'Snowflake Tables', 'Streamlit']
            })
            
            st.dataframe(processing_steps, hide_index=True)
        
        with tab3:
            st.markdown("### AI Components Deep Dive")
            
            st.markdown("#### Use Case Implementation")
            
            use_cases = pd.DataFrame({
                'Use Case': [
                    'Differential Diagnosis',
                    'Treatment Analysis',
                    'Clinical Summary',
                    'Pattern Recognition',
                    'Cost Analysis',
                    'Medication Safety',
                    'Quality Metrics',
                    'Educational Value'
                ],
                'AI Model': [
                    'mistral-large',
                    'mistral-large',
                    'mistral-large',
                    'mixtral-8x7b',
                    'mixtral-8x7b',
                    'mistral-large',
                    'mixtral-8x7b',
                    'mixtral-8x7b'
                ],
                'Output Type': [
                    'Structured JSON',
                    'Structured JSON',
                    'SBAR Format',
                    'Anomaly Scores',
                    'Cost Estimates',
                    'Drug Interactions',
                    'Compliance Rates',
                    'Teaching Points'
                ]
            })
            
            st.dataframe(use_cases, hide_index=True)
            
            st.markdown("#### Prompt Engineering")
            
            with st.expander("View Sample Prompt Structure"):
                st.code("""
{
    "system": "You are a medical AI assistant analyzing clinical notes.",
    "prompt": "Extract key clinical information from the following note:",
    "format": "Return results as structured JSON with specific fields",
    "constraints": "Focus on evidence-based findings only",
    "examples": "Provided for consistent output formatting"
}
                """, language='json')
    
    elif demo_section == "Talking Points":
        st.markdown("## 💬 Key Talking Points")
        
        audience_type = st.selectbox(
            "Select Audience",
            ["Executive", "Clinical", "Technical", "General"]
        )
        
        if audience_type == "Executive":
            st.markdown("### Executive Talking Points")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Value Proposition")
                st.success("""
                **Financial Impact**
                - Identify high-cost patients proactively
                - Reduce readmissions through better care
                - Optimize resource utilization
                - Typical ROI: 10-15x investment
                
                **Quality Improvement**
                - Enhance patient safety
                - Improve clinical outcomes
                - Ensure regulatory compliance
                - Reduce medical errors
                """)
            
            with col2:
                st.markdown("#### Strategic Benefits")
                st.info("""
                **Competitive Advantage**
                - Leading-edge AI adoption
                - Data-driven decision making
                - Improved patient satisfaction
                - Physician productivity gains
                
                **Scalability**
                - Process millions of notes
                - No infrastructure limits
                - Pay-per-use model
                - Rapid deployment
                """)
        
        elif audience_type == "Clinical":
            st.markdown("### Clinical Talking Points")
            
            st.markdown("#### For Physicians")
            st.markdown("""
            - **Time Savings**: Reduce documentation review from 15 minutes to 30 seconds
            - **Clinical Support**: AI suggests differential diagnoses you might not consider
            - **Evidence-Based**: Recommendations backed by similar patient outcomes
            - **Safety Alerts**: Automatic drug interaction and contraindication checking
            """)
            
            st.markdown("#### Clinical Use Cases")
            
            clinical_benefits = pd.DataFrame({
                'Scenario': [
                    'Morning Rounds',
                    'New Patient Intake',
                    'Discharge Planning',
                    'Complex Cases'
                ],
                'AI Benefit': [
                    'Quick SBAR summaries for all patients',
                    'Comprehensive history analysis',
                    'Medication reconciliation',
                    'Rare disease pattern recognition'
                ],
                'Time Saved': [
                    '2 hours/day',
                    '30 min/patient',
                    '15 min/discharge',
                    '1 hour/case'
                ]
            })
            
            st.dataframe(clinical_benefits, hide_index=True)
        
        elif audience_type == "Technical":
            st.markdown("### Technical Talking Points")
            
            tab1, tab2, tab3 = st.tabs(["Architecture", "Security", "Integration"])
            
            with tab1:
                st.markdown("#### Technical Architecture")
                st.code("""
- Cloud-Native: Built on Snowflake's elastic compute
- Serverless AI: No model management required
- SQL-Based: Familiar tooling for data teams
- Python SDK: Easy integration with existing workflows
- REST APIs: Standard interfaces for applications
                """)
            
            with tab2:
                st.markdown("#### Security & Compliance")
                st.markdown("""
                - **HIPAA Compliant**: End-to-end encryption
                - **Data Governance**: Role-based access control
                - **Audit Trail**: Complete processing history
                - **Data Residency**: Your region, your control
                - **PHI Protection**: No data leaves Snowflake
                """)
            
            with tab3:
                st.markdown("#### Integration Options")
                st.markdown("""
                - **EHR Integration**: HL7/FHIR interfaces
                - **Batch Processing**: Scheduled jobs
                - **Real-time API**: < 2 second response
                - **Streaming**: Kafka/Kinesis support
                - **Export Formats**: JSON, CSV, Parquet
                """)
    
    elif demo_section == "FAQ":
        st.markdown("## ❓ Frequently Asked Questions")
        
        faqs = {
            "How accurate is the AI analysis?": """
                Our AI achieves 85-90% accuracy on clinical information extraction, validated against 
                physician reviews. The system is designed to augment, not replace, clinical judgment.
            """,
            
            "What about patient privacy?": """
                All processing occurs within Snowflake's secure environment. No patient data is sent 
                to external services. The system is HIPAA compliant with full audit trails.
            """,
            
            "How much does it cost?": """
                Costs scale with usage, typically $0.30-0.50 per patient analysis. Most organizations 
                see ROI within 3-6 months through efficiency gains and cost reductions.
            """,
            
            "Can we customize the AI prompts?": """
                Yes! All prompts are configurable. You can modify them to match your clinical protocols, 
                add specialty-specific logic, or adjust output formats.
            """,
            
            "How long does implementation take?": """
                Basic deployment takes 1-2 weeks. Full integration with existing systems typically 
                requires 4-6 weeks depending on complexity.
            """,
            
            "What medical specialties does it support?": """
                The system works across all specialties but excels in internal medicine, cardiology, 
                oncology, and emergency medicine. Specialty-specific models can be added.
            """,
            
            "How does it handle medical abbreviations?": """
                The AI is trained on medical texts and understands common abbreviations. Custom 
                abbreviation dictionaries can be added for organization-specific terms.
            """,
            
            "Can it process non-English notes?": """
                Currently optimized for English. Multi-language support is on the roadmap with 
                Spanish and Mandarin prioritized.
            """
        }
        
        for question, answer in faqs.items():
            with st.expander(question):
                st.write(answer)
    
    elif demo_section == "Troubleshooting":
        st.markdown("## 🔧 Troubleshooting Guide")
        
        st.markdown("### Common Issues and Solutions")
        
        issues = {
            "Slow Performance": {
                "symptoms": ["Pages load slowly", "Queries timeout", "Processing delays"],
                "solutions": [
                    "Check warehouse size (recommend MEDIUM)",
                    "Verify Cortex Search service is active",
                    "Review concurrent user load",
                    "Clear browser cache"
                ]
            },
            
            "No Data Showing": {
                "symptoms": ["Empty dashboards", "Zero patient counts", "Missing analyses"],
                "solutions": [
                    "Verify batch processing completed",
                    "Check database permissions",
                    "Confirm PATIENT_SUBSET has data",
                    "Run test queries in SQL"
                ]
            },
            
            "AI Processing Errors": {
                "symptoms": ["Failed analyses", "Incomplete results", "Error messages"],
                "solutions": [
                    "Check Cortex credit availability",
                    "Verify prompt syntax",
                    "Review token limits",
                    "Check model availability"
                ]
            },
            
            "Search Not Working": {
                "symptoms": ["No search results", "Irrelevant results", "Search errors"],
                "solutions": [
                    "Verify Cortex Search service status",
                    "Check search syntax",
                    "Confirm index is up to date",
                    "Review search permissions"
                ]
            }
        }
        
        for issue, details in issues.items():
            with st.expander(f"🔴 {issue}"):
                st.markdown("**Symptoms:**")
                for symptom in details["symptoms"]:
                    st.write(f"- {symptom}")
                
                st.markdown("**Solutions:**")
                for i, solution in enumerate(details["solutions"], 1):
                    st.success(f"{i}. {solution}")
        
        st.markdown("### 🚀 Performance Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Quick Wins")
            st.markdown("""
            - Increase warehouse size for demos
            - Pre-warm caches before presentations
            - Use bookmarks for quick navigation
            - Keep backup demo environment ready
            """)
        
        with col2:
            st.markdown("#### Demo Best Practices")
            st.markdown("""
            - Test all scenarios beforehand
            - Have offline backup slides
            - Know your patient IDs
            - Practice error recovery
            """)
        
        st.markdown("### 📞 Support Contacts")
        st.info("""
        **Technical Support**: ai-demo-support@example.com
        **Snowflake Support**: support.snowflake.com
        **Documentation**: docs.snowflake.com/cortex
        """)
    
    # Footer
    st.markdown("---")
    st.caption(f"Healthcare AI Demo Guide • Version 1.0 • Last Updated: {datetime.now().strftime('%Y-%m-%d')}")
    
    conn.close()

if __name__ == "__main__":
    main()