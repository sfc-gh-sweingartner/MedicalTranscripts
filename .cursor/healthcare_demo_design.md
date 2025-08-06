# Healthcare Transcription AI Demo - Design Document

## Project Overview
This document defines the design for a Snowflake-based healthcare demonstration showcasing AI-powered analysis of medical notes using the PMC patients dataset. The solution follows a hybrid architecture combining pre-processed insights with real-time AI demonstrations.

## Architecture: Hybrid Approach

### Core Design Principles
1. **Pre-processed Analytics**: Most insights are pre-computed and stored in enriched tables for optimal demo performance
2. **Real-time Demonstrations**: Selected use cases allow live AI processing to showcase Snowflake Cortex capabilities
3. **Physician-First Design**: UI/UX optimized for clinical workflows with secondary views for administrators and researchers
4. **Production-Ready Patterns**: Architecture mirrors real-world healthcare implementations

### System Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   PMC_PATIENTS      │────▶│   Batch AI Pipeline  │────▶│  Enriched Tables    │
│   (167K records)    │     │   (Cortex AI)        │     │  (Pre-computed)     │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
                                      │                              │
                                      │                              ▼
                            ┌─────────────────────┐      ┌─────────────────────┐
                            │  Real-time AI       │      │  Streamlit App      │
                            │  Processing         │◀─────│  (Multi-Page)       │
                            │  (On-demand)        │      └─────────────────────┘
                            └─────────────────────┘               │
                                                                  ▼
                            ┌─────────────────────┐      ┌─────────────────────┐
                            │  Cortex Search      │◀─────│  Patient Search     │
                            │  Service (Active)   │      │  (Sub-second)       │
                            │  167K+ Indexed      │      │  Semantic Search    │
                            └─────────────────────┘      └─────────────────────┘
```

## Database Schema Design

create a database named HEALTHCARE_DEMO

create a schema named MEDICAL_NOTES

use the snowflake warehouse MYWH

### Core Tables

```sql
-- Main analysis table for pre-computed insights
CREATE OR REPLACE TABLE HEALTHCARE_DEMO.MEDICAL_NOTES.PATIENT_ANALYSIS (
    -- Identifiers
    PATIENT_ID NUMBER PRIMARY KEY,
    PATIENT_UID VARCHAR,
    ANALYSIS_VERSION VARCHAR DEFAULT 'v1.0',
    PROCESSED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Clinical Summary (Use Case 3)
    CHIEF_COMPLAINT TEXT,
    CLINICAL_SUMMARY TEXT,
    SBAR_SUMMARY VARIANT, -- {situation, background, assessment, recommendation}
    
    -- Diagnostic Analysis (Use Case 1)
    KEY_FINDINGS VARIANT, -- Array of {finding, category, severity}
    DIFFERENTIAL_DIAGNOSES VARIANT, -- Array of {diagnosis, confidence, evidence}
    DIAGNOSTIC_REASONING TEXT,
    SIMILAR_PATIENT_DIAGNOSES VARIANT, -- From SIMILAR_PATIENTS analysis
    
    -- Treatment Analysis (Use Case 2)
    TREATMENTS_ADMINISTERED VARIANT, -- Array of {treatment, date, outcome}
    TREATMENT_EFFECTIVENESS TEXT,
    EVIDENCE_BASED_RECOMMENDATIONS VARIANT, -- From RELEVANT_ARTICLES
    SIMILAR_PATIENT_TREATMENTS VARIANT, -- Comparative analysis
    
    -- Pattern Recognition (Use Case 4)
    PRESENTATION_TYPE VARCHAR, -- typical, atypical, rare
    RARE_DISEASE_INDICATORS VARIANT,
    SYMPTOM_CLUSTER_ID VARCHAR,
    ANOMALY_SCORE FLOAT,
    
    -- Cost Analysis (Use Case 5)
    HIGH_COST_INDICATORS VARIANT, -- procedures, medications, complications
    ESTIMATED_COST_CATEGORY VARCHAR, -- low, medium, high, very_high
    RESOURCE_UTILIZATION VARIANT,
    
    -- Quality Metrics (Use Case 7)
    CARE_QUALITY_INDICATORS VARIANT,
    GUIDELINE_ADHERENCE_FLAGS VARIANT,
    
    -- Educational Value (Use Case 8)
    TEACHING_POINTS VARIANT,
    CLINICAL_PEARLS TEXT,
    QUIZ_QUESTIONS VARIANT -- Array of Q&A for education
);

-- Real-time processing history
CREATE OR REPLACE TABLE HEALTHCARE_DEMO.MEDICAL_NOTES.REALTIME_ANALYSIS_LOG (
    ANALYSIS_ID VARCHAR DEFAULT UUID_STRING(),
    SESSION_ID VARCHAR,
    USER_NAME VARCHAR,
    ANALYSIS_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PATIENT_ID NUMBER,
    ORIGINAL_TEXT TEXT,
    MODIFIED_TEXT TEXT,
    ANALYSIS_TYPE VARCHAR, -- 'full', 'differential', 'summary', etc.
    AI_MODEL_USED VARCHAR,
    PROCESSING_TIME_MS NUMBER,
    RESULTS VARIANT,
    SUCCESS_FLAG BOOLEAN
);

-- Cohort analysis for population health
CREATE OR REPLACE TABLE HEALTHCARE_DEMO.MEDICAL_NOTES.COHORT_INSIGHTS (
    COHORT_ID VARCHAR DEFAULT UUID_STRING(),
    ANALYSIS_DATE DATE DEFAULT CURRENT_DATE(),
    COHORT_DEFINITION VARIANT, -- Criteria used
    PATIENT_COUNT NUMBER,
    
    -- Aggregate metrics
    COMMON_DIAGNOSES VARIANT,
    TREATMENT_PATTERNS VARIANT,
    OUTCOME_STATISTICS VARIANT,
    COST_ANALYSIS VARIANT,
    QUALITY_METRICS VARIANT,
    
    -- Trends
    TEMPORAL_TRENDS VARIANT,
    EMERGING_PATTERNS TEXT
);

-- Physician workflow optimization
CREATE OR REPLACE TABLE HEALTHCARE_DEMO.MEDICAL_NOTES.PHYSICIAN_INSIGHTS (
    INSIGHT_ID VARCHAR DEFAULT UUID_STRING(),
    GENERATED_DATE DATE DEFAULT CURRENT_DATE(),
    SPECIALTY VARCHAR,
    INSIGHT_TYPE VARCHAR, -- 'clinical_alert', 'best_practice', 'new_evidence'
    INSIGHT_TITLE TEXT,
    INSIGHT_CONTENT TEXT,
    EVIDENCE_LINKS VARIANT,
    APPLICABLE_PATIENTS VARIANT,
    PRIORITY_SCORE NUMBER
);
```

## Cortex Search Implementation

### Search Service Architecture
The application implements **Snowflake Cortex Search** for intelligent patient discovery with the following features:

- **Service Name**: `patient_search_service`
- **Index Status**: ACTIVE (167,034+ patient records indexed)
- **Embedding Model**: `snowflake-arctic-embed-l-v2.0`
- **Refresh Frequency**: 1 hour target lag
- **Warehouse**: `CORTEX_SEARCH_WH` (X-SMALL)

### Search Capabilities
- **Semantic Understanding**: Understands medical terminology and concepts
- **Misspelling Tolerance**: Handles common medical misspellings (e.g., "brest" → "breast")
- **Multi-Column Search**: Searches across patient notes, titles, and metadata
- **Sub-Second Performance**: Vector-based search for near-instantaneous results
- **Relevance Scoring**: Returns similarity scores for result ranking

### Implementation Details
```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE patient_search_service
    ON PATIENT_NOTES
    ATTRIBUTES PATIENT_ID, PATIENT_UID, PATIENT_TITLE, AGE, GENDER
    WAREHOUSE = CORTEX_SEARCH_WH
    TARGET_LAG = '1 hour'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT PATIENT_NOTES, PATIENT_ID, PATIENT_UID, PATIENT_TITLE, AGE, GENDER
        FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
        WHERE PATIENT_NOTES IS NOT NULL AND LENGTH(PATIENT_NOTES) > 50
    );
```

### Integration Points
- **Clinical Decision Support**: Primary search interface for patient discovery
- **API Access**: Python-based queries using Snowflake's core libraries
- **Enhanced Fallback**: Intelligent text search with medical spell correction when needed

## Use Case Implementation Priority

### Phase 1: Core Clinical Use Cases (Physician-focused)

#### 1. On-Demand Patient Summary (Use Case 3)
- **Pre-computed**: SBAR summaries for all patients
- **Real-time**: Allow physicians to modify notes and regenerate summaries
- **Value**: Reduces handoff errors, saves 10-15 minutes per patient

#### 2. Differential Diagnosis Support (Use Case 1)
- **Pre-computed**: Top 5 differential diagnoses with evidence
- **Real-time**: Interactive diagnosis exploration with custom symptoms
- **Value**: Improves diagnostic accuracy, reduces time to diagnosis

#### 3. Evidence-Based Treatment Analysis (Use Case 2)
- **Pre-computed**: Treatment comparisons from similar patients
- **Real-time**: Query specific treatment outcomes
- **Value**: Promotes evidence-based medicine, improves outcomes

#### 4. Rare Disease Pattern Recognition (Use Case 4)
- **Pre-computed**: Anomaly scores and rare disease flags
- **Real-time**: Deep dive into specific symptom clusters
- **Value**: Reduces diagnostic odysseys for rare conditions

### Phase 2: Administrative Use Cases

#### 5. High-Cost Patient Analysis (Use Case 5)
- **Pre-computed**: Cost drivers and utilization patterns
- **Dashboard**: Aggregate views by department/condition
- **Value**: Identifies intervention opportunities, reduces costs

#### 6. Drug Interaction Analysis (Use Case 6)
- **Pre-computed**: Medication lists and known interactions
- **Real-time**: Check new medication combinations
- **Value**: Prevents adverse events, improves safety

### Phase 3: Quality & Education

#### 7. Quality of Care Audits (Use Case 7)
- **Pre-computed**: Adherence to guidelines metrics
- **Dashboard**: Department and physician comparisons
- **Value**: Improves care standardization

#### 8. Educational Case Generation (Use Case 8)
- **Pre-computed**: Teaching cases with quiz questions
- **Interactive**: Case-based learning modules
- **Value**: Enhances medical education

## Streamlit Application Structure

### Page Layout and Navigation

```
Healthcare AI Demo
├── 1_🏥_Data_Foundation.py
├── 2_🩺_Clinical_Decision_Support.py (PRIMARY DEMO)
├── 3_🔬_AI_Processing_Live_Demo.py (REAL-TIME SHOWCASE)
├── 4_📊_Population_Health_Analytics.py
├── 5_🎓_Medical_Education.py
├── 6_💊_Medication_Safety.py
├── 7_📈_Quality_Metrics.py
├── 8_🤖_AI_Model_Performance.py
└── 9_📋_Demo_Guide.py
```

### Page Details

#### Page 1: Data Foundation
- PMC dataset overview and statistics
- Data quality metrics
- Sample patient records
- Processing pipeline status

#### Page 2: Clinical Decision Support (PRIMARY)
- **Patient Search**: Find patients by ID, condition, or symptoms
- **Clinical Summary**: SBAR format with key highlights
- **Differential Diagnosis**: Interactive diagnosis explorer
- **Similar Patients**: View and compare similar cases
- **Treatment Recommendations**: Evidence-based suggestions
- **Literature Links**: Relevant articles from RELEVANT_ARTICLES

#### Page 3: AI Processing Live Demo (REAL-TIME)
- **Based on superannuation demo page 2**
- Select a patient note
- Edit the text freely
- Process with Cortex AI in real-time
- Show step-by-step AI analysis
- Display results progressively

#### Page 4: Population Health Analytics
- Cohort analysis tools
- Disease prevalence maps
- Treatment effectiveness comparisons
- Cost analysis by condition
- Outcome predictions

#### Page 5: Medical Education
- Case-based learning modules
- Auto-generated quiz questions
- Clinical reasoning exercises
- Difficulty levels (student/resident/attending)

#### Page 6: Medication Safety
- Drug interaction checker
- Adverse event analysis
- Medication reconciliation
- Polypharmacy alerts

#### Page 7: Quality Metrics
- Care quality dashboards
- Guideline adherence rates
- Benchmark comparisons
- Improvement opportunities

#### Page 8: AI Model Performance
- Processing metrics
- Model accuracy indicators
- Prompt engineering examples
- Cost/performance analysis

#### Page 9: Demo Guide
- Persona-specific demo scripts
- Use case walkthroughs
- Technical architecture
- ROI calculations

## AI Processing Design

### Batch Processing Pipeline

```python
# Pseudo-code for batch processing
def process_patient_batch():
    patients = get_unprocessed_patients()
    
    for patient in patients:
        # Use Case 3: Summary Generation
        sbar_summary = cortex_complete(
            model='mistral-large',
            prompt=build_sbar_prompt(patient.notes)
        )
        
        # Use Case 1: Differential Diagnosis
        differential = cortex_complete(
            model='mixtral-8x7b',
            prompt=build_differential_prompt(patient.notes, patient.similar_patients)
        )
        
        # Use Case 2: Treatment Analysis
        treatment_analysis = analyze_treatments(
            patient.notes, 
            patient.similar_patients,
            patient.relevant_articles
        )
        
        # Store results
        store_analysis_results(patient.id, {
            'sbar': sbar_summary,
            'differential': differential,
            'treatments': treatment_analysis,
            ...
        })
```

### Real-time Processing Design

```python
# Based on superannuation AI demo pattern
def process_realtime(patient_text, analysis_type):
    with st.spinner("🤖 AI Analysis in Progress..."):
        # Step 1: Extract key information
        extraction = cortex_complete(
            prompt=f"Extract clinical findings from: {patient_text}"
        )
        update_progress("Extraction complete", 25)
        
        # Step 2: Generate diagnosis
        diagnosis = cortex_complete(
            prompt=f"Based on findings {extraction}, suggest differential diagnoses"
        )
        update_progress("Diagnosis generated", 50)
        
        # Step 3: Treatment recommendations
        treatment = cortex_complete(
            prompt=f"Recommend treatments for {diagnosis}"
        )
        update_progress("Treatment plan created", 75)
        
        # Step 4: Compile results
        results = compile_analysis(extraction, diagnosis, treatment)
        update_progress("Analysis complete", 100)
        
    return results
```

## Prompt Engineering Templates

### SBAR Summary Generation
```
You are a clinical documentation specialist. Create an SBAR summary from these notes:

Patient Notes: {patient_notes}

Format your response as:
Situation: [Current clinical situation in 1-2 sentences]
Background: [Relevant medical history and context]
Assessment: [Current diagnosis and clinical status]
Recommendation: [Next steps and treatment plan]
```

### Differential Diagnosis
```
As an expert diagnostician, analyze these clinical findings:

Patient Presentation: {findings}
Similar Cases: {similar_patient_summaries}

Provide 5 differential diagnoses with:
1. Diagnosis name
2. Confidence level (High/Medium/Low)
3. Supporting evidence from the notes
4. Key discriminating features
```

### Treatment Analysis
```
Compare treatment approaches for this patient:

Current Patient: {patient_summary}
Similar Patients Treatments: {similar_treatments}
Relevant Literature: {article_summaries}

Provide:
1. Current treatment effectiveness assessment
2. Alternative treatment options from similar cases
3. Evidence-based recommendations
4. Outcome predictions based on similar patients
```

## Demo Scenarios

### Scenario 1: Complex Diagnostic Case
- **Patient**: 66-year-old with seizures and cardiac arrhythmia
- **Demo Flow**: Show differential diagnosis → Similar patients → Treatment options
- **Key Point**: AI identifies rare cardiac-neurological connection

### Scenario 2: Pediatric Rare Disease
- **Patient**: 11-year-old with multicentric peripheral ossifying fibroma
- **Demo Flow**: Rare disease detection → Literature review → Treatment protocol
- **Key Point**: AI recognizes rare pediatric condition

### Scenario 3: Cost Optimization
- **Patient**: High-utilization patient with multiple conditions
- **Demo Flow**: Cost analysis → Intervention opportunities → Outcome prediction
- **Key Point**: AI identifies cost-saving care coordination

## Technical Specifications

### Snowflake Configuration
- **Database**: HEALTHCARE_DEMO
- **Schema**: MEDICAL_NOTES
- **Warehouse**: COMPUTE_WH (or specified warehouse)
- **Cortex Models**: 
  - mistral-large (summaries)
  - mixtral-8x7b (clinical analysis)
  - llama3.1-70b (education content)

### Performance Requirements
- Batch processing: 1000 patients/hour
- Real-time analysis: < 30 seconds response
- Dashboard queries: < 2 seconds
- Concurrent users: 10-20

### Security Considerations
- All data remains within Snowflake
- No PHI in demo environment
- Role-based access control
- Audit logging for compliance

## Success Metrics

### Demo Success
- Complete patient analysis in < 30 seconds
- Clear value proposition for each persona
- Smooth navigation between use cases
- No technical failures during presentation

### Business Value
- 15-20% reduction in diagnostic time
- 25% improvement in treatment adherence
- 30% reduction in documentation time
- ROI within 6 months of implementation

## Future Enhancements

### Phase 2 Possibilities
- Integration with real EMR systems
- Continuous learning from user feedback
- Multi-language support
- Voice-to-text for note creation
- Mobile application

### Advanced Analytics
- Predictive modeling for outcomes
- Real-time clinical decision support
- Automated quality reporting
- Research cohort identification

---

*This design document serves as the blueprint for the Healthcare AI Demo. All implementation should follow these specifications unless explicitly modified.*