"""
Medication Safety Page
Analyzes medication extraction, drug interactions, and safety concerns
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.connection_helper import get_snowflake_connection, execute_query

# Page config
st.set_page_config(
    page_title="Medication Safety",
    page_icon="💊",
    layout="wide"
)

def load_medication_overview(conn):
    """Load medication safety overview"""
    query = """
    SELECT 
        COUNT(DISTINCT ma.PATIENT_ID) as total_patients,
        SUM(ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS)) as total_medications,
        AVG(ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS)) as avg_meds_per_patient,
        COUNT(DISTINCT CASE WHEN ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) > 5 THEN ma.PATIENT_ID END) as polypharmacy_patients,
        COUNT(DISTINCT CASE WHEN ARRAY_SIZE(ma.DRUG_INTERACTIONS) > 0 THEN ma.PATIENT_ID END) as patients_with_interactions,
        SUM(ARRAY_SIZE(ma.DRUG_INTERACTIONS)) as total_interactions,
        COUNT(DISTINCT CASE WHEN ARRAY_SIZE(ma.CONTRAINDICATIONS) > 0 THEN ma.PATIENT_ID END) as patients_with_contraindications
    FROM MEDICATION_ANALYSIS ma
    """
    return execute_query(query, conn)

def load_common_medications(conn):
    """Load most commonly prescribed medications"""
    query = """
    WITH meds_expanded AS (
        SELECT 
            ma.PATIENT_ID,
            med.value:name::STRING as medication_name,
            med.value:dosage::STRING as dosage,
            med.value:frequency::STRING as frequency,
            p.AGE_YEARS,
            p.GENDER
        FROM MEDICATION_ANALYSIS ma,
        LATERAL FLATTEN(input => ma.EXTRACTED_MEDICATIONS) med
        JOIN PATIENT_SUBSET p ON ma.PATIENT_ID = p.PATIENT_ID
    )
    SELECT 
        medication_name,
        COUNT(DISTINCT PATIENT_ID) as patient_count,
        COUNT(DISTINCT dosage) as dosage_variations,
        AVG(AGE_YEARS) as avg_patient_age,
        MODE(frequency) as most_common_frequency
    FROM meds_expanded
    WHERE medication_name IS NOT NULL
    GROUP BY medication_name
    HAVING patient_count > 2
    ORDER BY patient_count DESC
    LIMIT 20
    """
    return execute_query(query, conn)

def load_drug_interactions(conn):
    """Load drug interaction data"""
    query = """
    WITH interactions_expanded AS (
        SELECT 
            ma.PATIENT_ID,
            inter.value:drug1::STRING as drug1,
            inter.value:drug2::STRING as drug2,
            inter.value:severity::STRING as severity,
            inter.value:description::STRING as description,
            p.AGE_YEARS
        FROM MEDICATION_ANALYSIS ma,
        LATERAL FLATTEN(input => ma.DRUG_INTERACTIONS) inter
        JOIN PATIENT_SUBSET p ON ma.PATIENT_ID = p.PATIENT_ID
    )
    SELECT 
        drug1,
        drug2,
        severity,
        description,
        COUNT(DISTINCT PATIENT_ID) as affected_patients,
        AVG(AGE_YEARS) as avg_age
    FROM interactions_expanded
    GROUP BY drug1, drug2, severity, description
    ORDER BY 
        CASE severity 
            WHEN 'MAJOR' THEN 1
            WHEN 'MODERATE' THEN 2
            WHEN 'MINOR' THEN 3
        END,
        affected_patients DESC
    """
    return execute_query(query, conn)

def load_polypharmacy_analysis(conn):
    """Load polypharmacy risk analysis"""
    query = """
    SELECT 
        CASE 
            WHEN ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) = 0 THEN '0'
            WHEN ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) <= 2 THEN '1-2'
            WHEN ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) <= 5 THEN '3-5'
            WHEN ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) <= 10 THEN '6-10'
            ELSE '>10'
        END as medication_count_range,
        COUNT(DISTINCT ma.PATIENT_ID) as patient_count,
        AVG(p.AGE_YEARS) as avg_age,
        AVG(ma.POLYPHARMACY_RISK_SCORE) as avg_risk_score,
        SUM(ARRAY_SIZE(ma.DRUG_INTERACTIONS)) as total_interactions
    FROM MEDICATION_ANALYSIS ma
    JOIN PATIENT_SUBSET p ON ma.PATIENT_ID = p.PATIENT_ID
    GROUP BY medication_count_range
    ORDER BY 
        CASE medication_count_range
            WHEN '0' THEN 1
            WHEN '1-2' THEN 2
            WHEN '3-5' THEN 3
            WHEN '6-10' THEN 4
            ELSE 5
        END
    """
    return execute_query(query, conn)

def load_contraindications(conn):
    """Load contraindication data"""
    query = """
    WITH contra_expanded AS (
        SELECT 
            ma.PATIENT_ID,
            contra.value:medication::STRING as medication,
            contra.value:condition::STRING as condition,
            contra.value:risk::STRING as risk_description,
            p.AGE_YEARS
        FROM MEDICATION_ANALYSIS ma,
        LATERAL FLATTEN(input => ma.CONTRAINDICATIONS) contra
        JOIN PATIENT_SUBSET p ON ma.PATIENT_ID = p.PATIENT_ID
    )
    SELECT 
        medication,
        condition,
        risk_description,
        COUNT(DISTINCT PATIENT_ID) as affected_patients,
        AVG(AGE_YEARS) as avg_age
    FROM contra_expanded
    GROUP BY medication, condition, risk_description
    ORDER BY affected_patients DESC
    LIMIT 15
    """
    return execute_query(query, conn)

def load_high_risk_patients(conn, limit=10):
    """Load patients with highest medication risks"""
    query = f"""
    SELECT 
        ma.PATIENT_ID,
        p.AGE_YEARS,
        p.GENDER,
        ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) as medication_count,
        ma.POLYPHARMACY_RISK_SCORE,
        ARRAY_SIZE(ma.DRUG_INTERACTIONS) as interaction_count,
        ARRAY_SIZE(ma.CONTRAINDICATIONS) as contraindication_count,
        pa.CHIEF_COMPLAINT
    FROM MEDICATION_ANALYSIS ma
    JOIN PATIENT_SUBSET p ON ma.PATIENT_ID = p.PATIENT_ID
    LEFT JOIN PATIENT_ANALYSIS pa ON ma.PATIENT_ID = pa.PATIENT_ID
    WHERE ma.POLYPHARMACY_RISK_SCORE > 0 OR ARRAY_SIZE(ma.DRUG_INTERACTIONS) > 0
    ORDER BY ma.POLYPHARMACY_RISK_SCORE DESC, interaction_count DESC
    LIMIT {limit}
    """
    return execute_query(query, conn)

def load_medication_by_age(conn):
    """Load medication patterns by age group"""
    query = """
    WITH age_meds AS (
        SELECT 
            CASE 
                WHEN p.AGE_YEARS < 18 THEN 'Pediatric'
                WHEN p.AGE_YEARS < 65 THEN 'Adult'
                ELSE 'Senior'
            END as age_group,
            ma.PATIENT_ID,
            ARRAY_SIZE(ma.EXTRACTED_MEDICATIONS) as med_count,
            ma.POLYPHARMACY_RISK_SCORE
        FROM MEDICATION_ANALYSIS ma
        JOIN PATIENT_SUBSET p ON ma.PATIENT_ID = p.PATIENT_ID
    )
    SELECT 
        age_group,
        COUNT(DISTINCT PATIENT_ID) as patient_count,
        AVG(med_count) as avg_medications,
        MAX(med_count) as max_medications,
        AVG(POLYPHARMACY_RISK_SCORE) as avg_risk_score
    FROM age_meds
    GROUP BY age_group
    ORDER BY avg_medications DESC
    """
    return execute_query(query, conn)

def create_interaction_network(interactions_df):
    """Create network visualization of drug interactions"""
    if interactions_df.empty:
        return None
    
    # Create network graph
    G = nx.Graph()
    
    # Add nodes and edges
    for _, row in interactions_df.iterrows():
        drug1 = row['DRUG1']
        drug2 = row['DRUG2']
        severity = row['SEVERITY']
        
        # Add nodes
        G.add_node(drug1)
        G.add_node(drug2)
        
        # Add edge with severity as weight
        weight = 3 if severity == 'MAJOR' else 2 if severity == 'MODERATE' else 1
        G.add_edge(drug1, drug2, weight=weight, severity=severity)
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Extract edge traces
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        severity = G[edge[0]][edge[1]]['severity']
        
        color = '#FF0000' if severity == 'MAJOR' else '#FFA500' if severity == 'MODERATE' else '#FFFF00'
        width = 3 if severity == 'MAJOR' else 2 if severity == 'MODERATE' else 1
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=width, color=color),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Node trace
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition="top center",
        marker=dict(
            size=20,
            color='lightblue',
            line=dict(width=2, color='darkblue')
        ),
        hoverinfo='text',
        hovertext=[f"{node}<br>Interactions: {G.degree(node)}" for node in G.nodes()]
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        title="Drug Interaction Network",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

def main():
    st.title("💊 Medication Safety Analysis")
    st.markdown("Extract medications from clinical notes and analyze for safety concerns")
    
    # Initialize connection
    conn = get_snowflake_connection()
    if not conn:
        st.error("Failed to connect to Snowflake. Please check your connection settings.")
        return
    
    # Load overview data
    with st.spinner("Loading medication safety data..."):
        overview_df = load_medication_overview(conn)
    
    if overview_df.empty or overview_df.iloc[0]['TOTAL_PATIENTS'] == 0:
        st.warning("No medication analysis data available. Please run batch processing first.")
        return
    
    overview = overview_df.iloc[0]
    
    # Display key metrics
    st.markdown("### 💊 Medication Safety Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Medications",
            f"{int(overview['TOTAL_MEDICATIONS']):,}",
            f"Avg {overview['AVG_MEDS_PER_PATIENT']:.1f} per patient",
            help="Total medications extracted from clinical notes"
        )
    
    with col2:
        polypharmacy_pct = overview['POLYPHARMACY_PATIENTS'] / overview['TOTAL_PATIENTS'] * 100
        st.metric(
            "Polypharmacy Risk",
            f"{int(overview['POLYPHARMACY_PATIENTS']):,} patients",
            f"{polypharmacy_pct:.1f}% (>5 meds)",
            delta_color="inverse",
            help="Patients taking more than 5 medications"
        )
    
    with col3:
        st.metric(
            "Drug Interactions",
            f"{int(overview['TOTAL_INTERACTIONS']):,}",
            f"{int(overview['PATIENTS_WITH_INTERACTIONS'])} patients affected",
            delta_color="inverse",
            help="Total drug-drug interactions identified"
        )
    
    with col4:
        st.metric(
            "Contraindications",
            f"{int(overview['PATIENTS_WITH_CONTRAINDICATIONS']):,} patients",
            help="Patients with medication-condition contraindications"
        )
    
    # Alert box for critical findings
    if overview['PATIENTS_WITH_INTERACTIONS'] > 0:
        st.error(
            f"⚠️ **Safety Alert**: {int(overview['PATIENTS_WITH_INTERACTIONS'])} patients have potential drug interactions requiring review"
        )
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Common Medications", "Drug Interactions", "Polypharmacy", 
        "Contraindications", "High-Risk Patients", "Age Analysis"
    ])
    
    with tab1:
        st.markdown("### 📋 Most Common Medications")
        
        meds_df = load_common_medications(conn)
        
        if not meds_df.empty:
            # Medication frequency chart
            fig_meds = px.bar(
                meds_df.head(15),
                x='PATIENT_COUNT',
                y='MEDICATION_NAME',
                orientation='h',
                title='Top 15 Most Prescribed Medications',
                labels={'PATIENT_COUNT': 'Number of Patients', 'MEDICATION_NAME': 'Medication'},
                color='AVG_PATIENT_AGE',
                color_continuous_scale='Viridis',
                hover_data=['DOSAGE_VARIATIONS', 'MOST_COMMON_FREQUENCY']
            )
            fig_meds.update_layout(height=600)
            st.plotly_chart(fig_meds, use_container_width=True)
            
            # Medication details table
            st.markdown("#### Medication Prescribing Patterns")
            meds_display = meds_df[['MEDICATION_NAME', 'PATIENT_COUNT', 'DOSAGE_VARIATIONS', 'AVG_PATIENT_AGE']].copy()
            meds_display.columns = ['Medication', 'Patients', 'Dosage Variations', 'Avg Patient Age']
            meds_display['Avg Patient Age'] = meds_display['Avg Patient Age'].round(1)
            st.dataframe(meds_display, hide_index=True, height=400)
            
            # Dosage standardization opportunity
            high_variation = meds_df[meds_df['DOSAGE_VARIATIONS'] > 3]
            if not high_variation.empty:
                st.info(
                    f"💡 **Standardization Opportunity**: {len(high_variation)} medications have >3 dosage variations, "
                    f"indicating potential for dosing standardization protocols."
                )
    
    with tab2:
        st.markdown("### ⚠️ Drug Interactions")
        
        interactions_df = load_drug_interactions(conn)
        
        if not interactions_df.empty:
            # Severity distribution
            col1, col2 = st.columns([1, 2])
            
            with col1:
                severity_counts = interactions_df.groupby('SEVERITY')['AFFECTED_PATIENTS'].sum().reset_index()
                fig_severity = px.pie(
                    severity_counts,
                    values='AFFECTED_PATIENTS',
                    names='SEVERITY',
                    title='Interactions by Severity',
                    color_discrete_map={
                        'MAJOR': '#FF0000',
                        'MODERATE': '#FFA500',
                        'MINOR': '#FFFF00'
                    }
                )
                st.plotly_chart(fig_severity, use_container_width=True)
            
            with col2:
                # Interaction network
                network_fig = create_interaction_network(interactions_df.head(20))
                if network_fig:
                    st.plotly_chart(network_fig, use_container_width=True)
            
            # Major interactions detail
            major_interactions = interactions_df[interactions_df['SEVERITY'] == 'MAJOR']
            if not major_interactions.empty:
                st.error("🚨 **Major Drug Interactions Detected**")
                
                for _, interaction in major_interactions.iterrows():
                    st.warning(
                        f"**{interaction['DRUG1']} + {interaction['DRUG2']}**: "
                        f"{interaction['DESCRIPTION']} "
                        f"({interaction['AFFECTED_PATIENTS']} patients affected)"
                    )
            
            # All interactions table
            st.markdown("#### All Drug Interactions")
            int_display = interactions_df[['DRUG1', 'DRUG2', 'SEVERITY', 'DESCRIPTION', 'AFFECTED_PATIENTS']].copy()
            int_display.columns = ['Drug 1', 'Drug 2', 'Severity', 'Description', 'Affected Patients']
            st.dataframe(
                int_display,
                hide_index=True,
                column_config={
                    "Severity": st.column_config.TextColumn(
                        "Severity",
                        help="Interaction severity level"
                    )
                }
            )
    
    with tab3:
        st.markdown("### 💊 Polypharmacy Analysis")
        
        poly_df = load_polypharmacy_analysis(conn)
        
        if not poly_df.empty:
            # Medication count distribution
            fig_poly = px.bar(
                poly_df,
                x='MEDICATION_COUNT_RANGE',
                y='PATIENT_COUNT',
                title='Patient Distribution by Number of Medications',
                labels={'PATIENT_COUNT': 'Number of Patients', 'MEDICATION_COUNT_RANGE': 'Number of Medications'},
                color='AVG_RISK_SCORE',
                color_continuous_scale='Reds',
                hover_data=['AVG_AGE', 'TOTAL_INTERACTIONS']
            )
            st.plotly_chart(fig_poly, use_container_width=True)
            
            # Risk analysis
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Polypharmacy Risk Factors")
                high_risk = poly_df[poly_df['MEDICATION_COUNT_RANGE'].isin(['6-10', '>10'])]
                if not high_risk.empty:
                    total_high_risk = high_risk['PATIENT_COUNT'].sum()
                    total_interactions = high_risk['TOTAL_INTERACTIONS'].sum()
                    
                    st.metric("High-Risk Patients (>5 meds)", total_high_risk)
                    st.metric("Total Interactions in High-Risk Group", total_interactions)
                    
                    avg_age_high_risk = (high_risk['AVG_AGE'] * high_risk['PATIENT_COUNT']).sum() / total_high_risk
                    st.info(f"Average age of polypharmacy patients: {avg_age_high_risk:.1f} years")
            
            with col2:
                # Risk score visualization
                fig_risk = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=poly_df['AVG_RISK_SCORE'].max(),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Maximum Polypharmacy Risk Score"},
                    gauge={
                        'axis': {'range': [None, 10]},
                        'bar': {'color': "darkred"},
                        'steps': [
                            {'range': [0, 3], 'color': "lightgray"},
                            {'range': [3, 6], 'color': "yellow"},
                            {'range': [6, 10], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 7
                        }
                    }
                ))
                fig_risk.update_layout(height=300)
                st.plotly_chart(fig_risk, use_container_width=True)
    
    with tab4:
        st.markdown("### 🚫 Contraindications")
        
        contra_df = load_contraindications(conn)
        
        if not contra_df.empty:
            st.warning("⚠️ **Medication-Condition Contraindications Detected**")
            
            # Contraindications visualization
            fig_contra = px.sunburst(
                contra_df,
                path=['MEDICATION', 'CONDITION'],
                values='AFFECTED_PATIENTS',
                title='Medication Contraindications by Condition'
            )
            st.plotly_chart(fig_contra, use_container_width=True)
            
            # Detailed contraindications
            st.markdown("#### Contraindication Details")
            for _, contra in contra_df.iterrows():
                with st.expander(f"{contra['MEDICATION']} - {contra['CONDITION']} ({contra['AFFECTED_PATIENTS']} patients)"):
                    st.error(f"**Risk**: {contra['RISK_DESCRIPTION']}")
                    st.write(f"Average patient age: {contra['AVG_AGE']:.1f} years")
    
    with tab5:
        st.markdown("### 🚨 High-Risk Patient Identification")
        
        # Slider for number of patients
        num_patients = st.slider("Number of highest-risk patients to review", 5, 20, 10)
        
        high_risk_df = load_high_risk_patients(conn, num_patients)
        
        if not high_risk_df.empty:
            st.markdown(f"#### Top {num_patients} Highest Risk Patients")
            
            # Risk summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_meds = high_risk_df['MEDICATION_COUNT'].mean()
                st.metric("Avg Medications", f"{avg_meds:.1f}")
            
            with col2:
                avg_interactions = high_risk_df['INTERACTION_COUNT'].mean()
                st.metric("Avg Interactions", f"{avg_interactions:.1f}")
            
            with col3:
                max_risk = high_risk_df['POLYPHARMACY_RISK_SCORE'].max()
                st.metric("Max Risk Score", f"{max_risk:.1f}")
            
            # Patient cards
            for idx, patient in high_risk_df.iterrows():
                risk_color = "🔴" if patient['POLYPHARMACY_RISK_SCORE'] > 7 else "🟡" if patient['POLYPHARMACY_RISK_SCORE'] > 5 else "🟢"
                
                with st.expander(f"{risk_color} Patient {patient['PATIENT_ID']} - Risk Score: {patient['POLYPHARMACY_RISK_SCORE']:.1f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Demographics**")
                        st.text(f"Age: {patient['AGE_YEARS']:.1f}")
                        st.text(f"Gender: {patient['GENDER']}")
                    
                    with col2:
                        st.markdown("**Medication Profile**")
                        st.text(f"Total Medications: {patient['MEDICATION_COUNT']}")
                        st.text(f"Drug Interactions: {patient['INTERACTION_COUNT']}")
                        st.text(f"Contraindications: {patient['CONTRAINDICATION_COUNT']}")
                    
                    with col3:
                        st.markdown("**Clinical Context**")
                        if patient['CHIEF_COMPLAINT']:
                            st.text(f"Chief Complaint: {patient['CHIEF_COMPLAINT'][:50]}...")
                    
                    if patient['INTERACTION_COUNT'] > 0:
                        st.error(f"⚠️ This patient has {patient['INTERACTION_COUNT']} drug interactions requiring immediate review")
    
    with tab6:
        st.markdown("### 👥 Medication Patterns by Age")
        
        age_meds_df = load_medication_by_age(conn)
        
        if not age_meds_df.empty:
            # Age group comparison
            fig_age = go.Figure()
            
            fig_age.add_trace(go.Bar(
                name='Average Medications',
                x=age_meds_df['AGE_GROUP'],
                y=age_meds_df['AVG_MEDICATIONS'],
                yaxis='y',
                marker_color='lightblue'
            ))
            
            fig_age.add_trace(go.Scatter(
                name='Average Risk Score',
                x=age_meds_df['AGE_GROUP'],
                y=age_meds_df['AVG_RISK_SCORE'],
                yaxis='y2',
                marker_color='red',
                mode='lines+markers',
                line=dict(width=3)
            ))
            
            fig_age.update_layout(
                title='Medication Use and Risk by Age Group',
                xaxis=dict(title='Age Group'),
                yaxis=dict(title='Average Medications', side='left'),
                yaxis2=dict(title='Average Risk Score', overlaying='y', side='right'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_age, use_container_width=True)
            
            # Age insights
            seniors = age_meds_df[age_meds_df['AGE_GROUP'] == 'Senior']
            if not seniors.empty and len(seniors) > 0:
                senior_data = seniors.iloc[0]
                st.warning(
                    f"📊 **Senior Population Alert**: Seniors average {senior_data['AVG_MEDICATIONS']:.1f} medications "
                    f"with a risk score of {senior_data['AVG_RISK_SCORE']:.1f}, requiring enhanced medication management protocols."
                )
    
    # Recommendations section
    st.markdown("---")
    st.markdown("### 💡 Medication Safety Recommendations")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Immediate Actions")
        st.success("✅ **Priority Interventions:**")
        st.markdown(f"""
        1. **Review Major Interactions**: {len(interactions_df[interactions_df['SEVERITY'] == 'MAJOR'])} major interactions need immediate review
        2. **Polypharmacy Management**: Target {int(overview['POLYPHARMACY_PATIENTS'])} patients with >5 medications
        3. **Contraindication Alerts**: Address {int(overview['PATIENTS_WITH_CONTRAINDICATIONS'])} patients with contraindications
        4. **Dosage Standardization**: Implement protocols for high-variation medications
        """)
    
    with col2:
        st.markdown("#### System Improvements")
        st.info("🔧 **Recommended System Enhancements:**")
        st.markdown("""
        - Implement real-time drug interaction checking
        - Create automated polypharmacy alerts at >5 medications
        - Establish medication reconciliation protocols
        - Deploy clinical decision support for prescribing
        - Regular medication review workflows for high-risk patients
        """)
    
    # Export functionality
    st.markdown("---")
    if st.button("📥 Generate Medication Safety Report"):
        st.success("Medication safety report generated! (In production, this would create a downloadable PDF)")
    
    conn.close()

if __name__ == "__main__":
    main()