"""
AI Model Performance Page
Monitors AI processing metrics, prompt effectiveness, and model performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.connection_helper import get_snowflake_connection, execute_query

# Page config
st.set_page_config(
    page_title="AI Model Performance",
    page_icon="🤖",
    layout="wide"
)

def load_processing_overview(conn):
    """Load AI processing overview statistics"""
    query = """
    SELECT 
        COUNT(DISTINCT ps.BATCH_ID) as total_batches,
        SUM(ps.TOTAL_PATIENTS) as total_patients_processed,
        SUM(ps.PROCESSED_PATIENTS) as successful_processes,
        SUM(ps.FAILED_PATIENTS) as failed_processes,
        AVG(DATEDIFF('minute', ps.START_TIME, ps.END_TIME)) as avg_batch_duration_min,
        COUNT(DISTINCT ral.SESSION_ID) as realtime_sessions,
        COUNT(DISTINCT ral.ANALYSIS_ID) as realtime_analyses
    FROM PROCESSING_STATUS ps
    FULL OUTER JOIN REALTIME_ANALYSIS_LOG ral ON 1=1
    WHERE ps.STATUS IN ('completed', 'running')
    """
    return execute_query(query, conn)

def load_model_usage(conn):
    """Load AI model usage statistics"""
    query = """
    WITH model_stats AS (
        SELECT 
            AI_MODEL_USED as model,
            COUNT(*) as usage_count,
            AVG(PROCESSING_TIME_MS) as avg_time_ms,
            COUNT(CASE WHEN SUCCESS_FLAG THEN 1 END) as success_count,
            COUNT(CASE WHEN NOT SUCCESS_FLAG THEN 1 END) as failure_count
        FROM REALTIME_ANALYSIS_LOG
        WHERE AI_MODEL_USED IS NOT NULL
        GROUP BY AI_MODEL_USED
    )
    SELECT 
        model,
        usage_count,
        avg_time_ms,
        success_count,
        failure_count,
        ROUND(100.0 * success_count / NULLIF(usage_count, 0), 1) as success_rate
    FROM model_stats
    ORDER BY usage_count DESC
    """
    return execute_query(query, conn)

def load_analysis_type_performance(conn):
    """Load performance by analysis type"""
    query = """
    SELECT 
        ANALYSIS_TYPE,
        COUNT(*) as analysis_count,
        AVG(PROCESSING_TIME_MS) as avg_processing_time,
        MIN(PROCESSING_TIME_MS) as min_time,
        MAX(PROCESSING_TIME_MS) as max_time,
        STDDEV(PROCESSING_TIME_MS) as time_stddev,
        COUNT(CASE WHEN SUCCESS_FLAG THEN 1 END) as success_count
    FROM REALTIME_ANALYSIS_LOG
    WHERE ANALYSIS_TYPE IS NOT NULL
    GROUP BY ANALYSIS_TYPE
    ORDER BY analysis_count DESC
    """
    return execute_query(query, conn)

def load_processing_trends(conn):
    """Load processing trends over time"""
    query = """
    WITH hourly_stats AS (
        SELECT 
            DATE_TRUNC('hour', ANALYSIS_TIMESTAMP) as hour,
            COUNT(*) as analyses,
            AVG(PROCESSING_TIME_MS) as avg_time,
            COUNT(CASE WHEN SUCCESS_FLAG THEN 1 END) as successes
        FROM REALTIME_ANALYSIS_LOG
        WHERE ANALYSIS_TIMESTAMP >= DATEADD('day', -7, CURRENT_TIMESTAMP())
        GROUP BY hour
    )
    SELECT 
        hour,
        analyses,
        avg_time,
        successes,
        ROUND(100.0 * successes / analyses, 1) as success_rate
    FROM hourly_stats
    ORDER BY hour DESC
    LIMIT 168  -- Last 7 days of hourly data
    """
    return execute_query(query, conn)

def load_batch_processing_stats(conn):
    """Load batch processing statistics"""
    query = """
    SELECT 
        BATCH_ID,
        START_TIME,
        END_TIME,
        STATUS,
        TOTAL_PATIENTS,
        PROCESSED_PATIENTS,
        FAILED_PATIENTS,
        DATEDIFF('minute', START_TIME, END_TIME) as duration_minutes,
        ROUND(100.0 * PROCESSED_PATIENTS / NULLIF(TOTAL_PATIENTS, 0), 1) as success_rate
    FROM PROCESSING_STATUS
    ORDER BY START_TIME DESC
    LIMIT 20
    """
    return execute_query(query, conn)

def load_prompt_effectiveness(conn):
    """Analyze prompt effectiveness by measuring output quality"""
    query = """
    WITH quality_metrics AS (
        SELECT 
            pa.PATIENT_ID,
            -- Measure completeness of outputs
            CASE WHEN pa.CHIEF_COMPLAINT IS NOT NULL THEN 1 ELSE 0 END as has_chief_complaint,
            CASE WHEN ARRAY_SIZE(pa.DIFFERENTIAL_DIAGNOSES) > 0 THEN 1 ELSE 0 END as has_diagnoses,
            CASE WHEN ARRAY_SIZE(pa.KEY_FINDINGS) > 0 THEN 1 ELSE 0 END as has_findings,
            CASE WHEN pa.SBAR_SUMMARY IS NOT NULL THEN 1 ELSE 0 END as has_sbar,
            CASE WHEN pa.DIAGNOSTIC_REASONING IS NOT NULL THEN 1 ELSE 0 END as has_reasoning,
            -- Count populated fields
            ARRAY_SIZE(pa.DIFFERENTIAL_DIAGNOSES) as dx_count,
            ARRAY_SIZE(pa.KEY_FINDINGS) as finding_count,
            pa.ANOMALY_SCORE
        FROM PATIENT_ANALYSIS pa
    )
    SELECT 
        COUNT(*) as total_analyses,
        -- Completeness metrics
        AVG(has_chief_complaint) * 100 as chief_complaint_rate,
        AVG(has_diagnoses) * 100 as diagnosis_rate,
        AVG(has_findings) * 100 as findings_rate,
        AVG(has_sbar) * 100 as sbar_rate,
        AVG(has_reasoning) * 100 as reasoning_rate,
        -- Quality metrics
        AVG(dx_count) as avg_diagnoses_per_patient,
        AVG(finding_count) as avg_findings_per_patient,
        AVG(CASE WHEN anomaly_score > 0 THEN anomaly_score END) as avg_anomaly_score
    FROM quality_metrics
    """
    return execute_query(query, conn)

def load_error_analysis(conn):
    """Load error patterns and failure analysis"""
    query = """
    WITH error_patterns AS (
        SELECT 
            CASE 
                WHEN ERROR_DETAILS:error LIKE '%timeout%' THEN 'Timeout'
                WHEN ERROR_DETAILS:error LIKE '%token%' THEN 'Token Limit'
                WHEN ERROR_DETAILS:error LIKE '%connection%' THEN 'Connection Error'
                WHEN ERROR_DETAILS:error LIKE '%parse%' THEN 'Parse Error'
                ELSE 'Other'
            END as error_type,
            COUNT(*) as error_count
        FROM PROCESSING_STATUS
        WHERE STATUS = 'failed' AND ERROR_DETAILS IS NOT NULL
        GROUP BY error_type
        
        UNION ALL
        
        SELECT 
            'Processing Failure' as error_type,
            COUNT(*) as error_count
        FROM REALTIME_ANALYSIS_LOG
        WHERE SUCCESS_FLAG = FALSE
    )
    SELECT 
        error_type,
        SUM(error_count) as total_errors
    FROM error_patterns
    GROUP BY error_type
    ORDER BY total_errors DESC
    """
    return execute_query(query, conn)

def load_cost_effectiveness(conn):
    """Calculate AI processing cost effectiveness"""
    query = """
    WITH processing_value AS (
        SELECT 
            COUNT(DISTINCT pa.PATIENT_ID) as patients_analyzed,
            -- Value metrics
            COUNT(DISTINCT CASE WHEN pa.PRESENTATION_TYPE = 'rare' THEN pa.PATIENT_ID END) as rare_diseases_found,
            COUNT(DISTINCT CASE WHEN ARRAY_SIZE(ma.DRUG_INTERACTIONS) > 0 THEN ma.PATIENT_ID END) as interactions_found,
            COUNT(DISTINCT CASE WHEN ca.COST_CATEGORY IN ('high', 'very_high') THEN ca.PATIENT_ID END) as high_cost_identified,
            -- Processing metrics
            AVG(ral.PROCESSING_TIME_MS) / 1000.0 as avg_processing_seconds
        FROM PATIENT_ANALYSIS pa
        LEFT JOIN MEDICATION_ANALYSIS ma ON pa.PATIENT_ID = ma.PATIENT_ID
        LEFT JOIN COST_ANALYSIS ca ON pa.PATIENT_ID = ca.PATIENT_ID
        LEFT JOIN REALTIME_ANALYSIS_LOG ral ON pa.PATIENT_ID = ral.PATIENT_ID
    )
    SELECT 
        patients_analyzed,
        rare_diseases_found,
        interactions_found,
        high_cost_identified,
        avg_processing_seconds,
        -- Calculate value metrics
        ROUND(100.0 * rare_diseases_found / NULLIF(patients_analyzed, 0), 1) as rare_disease_rate,
        ROUND(100.0 * interactions_found / NULLIF(patients_analyzed, 0), 1) as interaction_rate,
        ROUND(100.0 * high_cost_identified / NULLIF(patients_analyzed, 0), 1) as high_cost_rate
    FROM processing_value
    """
    return execute_query(query, conn)

def main():
    st.title("🤖 AI Model Performance")
    st.markdown("Monitor AI processing metrics, model effectiveness, and system performance")
    
    # Initialize connection
    conn = get_snowflake_connection()
    if not conn:
        st.error("Failed to connect to Snowflake. Please check your connection settings.")
        return
    
    # Load overview data
    with st.spinner("Loading AI performance data..."):
        overview_df = load_processing_overview(conn)
    
    if overview_df.empty:
        st.warning("No AI processing data available yet.")
        return
    
    overview = overview_df.iloc[0]
    
    # Display key metrics
    st.markdown("### 🎯 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_processed = overview['SUCCESSFUL_PROCESSES'] or 0
        st.metric(
            "Total Analyses",
            f"{int(total_processed):,}",
            help="Total successful AI analyses completed"
        )
    
    with col2:
        success_rate = 0
        if overview['TOTAL_PATIENTS_PROCESSED'] and overview['TOTAL_PATIENTS_PROCESSED'] > 0:
            success_rate = (overview['SUCCESSFUL_PROCESSES'] / overview['TOTAL_PATIENTS_PROCESSED']) * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            help="Percentage of successful AI processing"
        )
    
    with col3:
        avg_duration = overview['AVG_BATCH_DURATION_MIN'] or 0
        st.metric(
            "Avg Batch Duration",
            f"{avg_duration:.0f} min",
            help="Average time to process a batch"
        )
    
    with col4:
        realtime_count = overview['REALTIME_ANALYSES'] or 0
        st.metric(
            "Real-time Analyses",
            f"{int(realtime_count):,}",
            help="Number of real-time AI analyses performed"
        )
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Model Usage", "Processing Speed", "Quality Metrics", "Error Analysis", "Cost-Benefit", "Prompt Engineering"
    ])
    
    with tab1:
        st.markdown("### 🤖 AI Model Usage Statistics")
        
        model_df = load_model_usage(conn)
        
        if not model_df.empty:
            # Model usage distribution
            fig_models = px.pie(
                model_df,
                values='USAGE_COUNT',
                names='MODEL',
                title='AI Model Usage Distribution',
                hole=0.4
            )
            st.plotly_chart(fig_models, use_container_width=True)
            
            # Model performance comparison
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Performance metrics by model
                fig_perf = px.bar(
                    model_df,
                    x='MODEL',
                    y=['SUCCESS_RATE', 'AVG_TIME_MS'],
                    title='Model Performance Comparison',
                    labels={'value': 'Metric Value', 'variable': 'Metric'},
                    barmode='group'
                )
                st.plotly_chart(fig_perf, use_container_width=True)
            
            with col2:
                # Model recommendations
                st.markdown("#### Model Selection Guide")
                
                best_accuracy = model_df.loc[model_df['SUCCESS_RATE'].idxmax()]
                best_speed = model_df.loc[model_df['AVG_TIME_MS'].idxmin()]
                
                st.success(f"**Highest Accuracy**: {best_accuracy['MODEL']} ({best_accuracy['SUCCESS_RATE']:.1f}%)")
                st.info(f"**Fastest**: {best_speed['MODEL']} ({best_speed['AVG_TIME_MS']:.0f}ms)")
                
                # Model details table
                model_display = model_df[['MODEL', 'USAGE_COUNT', 'SUCCESS_RATE', 'AVG_TIME_MS']].copy()
                model_display.columns = ['Model', 'Uses', 'Success %', 'Avg Time (ms)']
                st.dataframe(model_display, hide_index=True)
    
    with tab2:
        st.markdown("### ⚡ Processing Speed Analysis")
        
        # Load analysis type performance
        analysis_df = load_analysis_type_performance(conn)
        
        if not analysis_df.empty:
            # Processing time by analysis type
            fig_speed = px.box(
                analysis_df,
                x='ANALYSIS_TYPE',
                y='AVG_PROCESSING_TIME',
                title='Processing Time by Analysis Type',
                labels={'AVG_PROCESSING_TIME': 'Average Processing Time (ms)', 'ANALYSIS_TYPE': 'Analysis Type'}
            )
            st.plotly_chart(fig_speed, use_container_width=True)
            
            # Performance trends
            trends_df = load_processing_trends(conn)
            
            if not trends_df.empty and len(trends_df) > 1:
                # Time series of processing performance
                fig_trends = go.Figure()
                
                fig_trends.add_trace(go.Scatter(
                    x=trends_df['HOUR'],
                    y=trends_df['AVG_TIME'],
                    mode='lines',
                    name='Avg Processing Time (ms)',
                    yaxis='y'
                ))
                
                fig_trends.add_trace(go.Scatter(
                    x=trends_df['HOUR'],
                    y=trends_df['SUCCESS_RATE'],
                    mode='lines',
                    name='Success Rate (%)',
                    yaxis='y2',
                    line=dict(color='green')
                ))
                
                fig_trends.update_layout(
                    title='Processing Performance Over Time',
                    xaxis_title='Time',
                    yaxis=dict(title='Processing Time (ms)', side='left'),
                    yaxis2=dict(title='Success Rate (%)', overlaying='y', side='right'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
            
            # Speed optimization insights
            if len(analysis_df) > 0:
                slowest = analysis_df.loc[analysis_df['AVG_PROCESSING_TIME'].idxmax()]
                fastest = analysis_df.loc[analysis_df['AVG_PROCESSING_TIME'].idxmin()]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.warning(f"⚠️ Slowest: **{slowest['ANALYSIS_TYPE']}** ({slowest['AVG_PROCESSING_TIME']:.0f}ms avg)")
                
                with col2:
                    st.success(f"✅ Fastest: **{fastest['ANALYSIS_TYPE']}** ({fastest['AVG_PROCESSING_TIME']:.0f}ms avg)")
    
    with tab3:
        st.markdown("### 📊 AI Output Quality Metrics")
        
        quality_df = load_prompt_effectiveness(conn)
        
        if not quality_df.empty and len(quality_df) > 0:
            quality = quality_df.iloc[0]
            
            # Completeness metrics
            st.markdown("#### Output Completeness Rates")
            
            completeness_data = {
                'Chief Complaint': quality['CHIEF_COMPLAINT_RATE'],
                'Diagnoses': quality['DIAGNOSIS_RATE'],
                'Key Findings': quality['FINDINGS_RATE'],
                'SBAR Summary': quality['SBAR_RATE'],
                'Clinical Reasoning': quality['REASONING_RATE']
            }
            
            fig_complete = px.bar(
                x=list(completeness_data.keys()),
                y=list(completeness_data.values()),
                title='AI Output Completeness by Field',
                labels={'x': 'Output Field', 'y': 'Completion Rate (%)'},
                color=list(completeness_data.values()),
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig_complete.add_hline(y=90, line_dash="dash", line_color="gray", 
                                 annotation_text="Target: 90%")
            st.plotly_chart(fig_complete, use_container_width=True)
            
            # Quality indicators
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Avg Diagnoses per Patient",
                    f"{quality['AVG_DIAGNOSES_PER_PATIENT']:.1f}",
                    help="Average number of differential diagnoses generated"
                )
            
            with col2:
                st.metric(
                    "Avg Key Findings",
                    f"{quality['AVG_FINDINGS_PER_PATIENT']:.1f}",
                    help="Average clinical findings extracted"
                )
            
            with col3:
                anomaly_score = quality['AVG_ANOMALY_SCORE'] or 0
                st.metric(
                    "Avg Anomaly Detection",
                    f"{anomaly_score:.2f}",
                    help="Average anomaly score for unusual cases"
                )
            
            # Quality insights
            low_completion = [k for k, v in completeness_data.items() if v < 80]
            if low_completion:
                st.warning(f"⚠️ Fields needing improvement: {', '.join(low_completion)}")
    
    with tab4:
        st.markdown("### 🚨 Error Analysis")
        
        error_df = load_error_analysis(conn)
        
        if not error_df.empty and len(error_df) > 0:
            # Error distribution
            fig_errors = px.pie(
                error_df,
                values='TOTAL_ERRORS',
                names='ERROR_TYPE',
                title='Error Distribution by Type',
                color_discrete_map={
                    'Timeout': '#FF6B6B',
                    'Token Limit': '#4ECDC4',
                    'Connection Error': '#45B7D1',
                    'Parse Error': '#F7DC6F',
                    'Processing Failure': '#BB8FCE',
                    'Other': '#85929E'
                }
            )
            st.plotly_chart(fig_errors, use_container_width=True)
            
            # Error mitigation strategies
            st.markdown("#### Error Mitigation Strategies")
            
            for _, error in error_df.iterrows():
                error_type = error['ERROR_TYPE']
                count = error['TOTAL_ERRORS']
                
                if error_type == 'Timeout':
                    st.error(f"**Timeout Errors ({count})**: Consider increasing timeout limits or optimizing prompts")
                elif error_type == 'Token Limit':
                    st.warning(f"**Token Limit ({count})**: Reduce prompt size or chunk large inputs")
                elif error_type == 'Connection Error':
                    st.info(f"**Connection Errors ({count})**: Check network stability and retry logic")
                elif error_type == 'Parse Error':
                    st.warning(f"**Parse Errors ({count})**: Improve prompt formatting for consistent JSON output")
        else:
            st.success("✅ No significant errors detected!")
        
        # Batch processing status
        batch_df = load_batch_processing_stats(conn)
        
        if not batch_df.empty:
            st.markdown("#### Batch Processing History")
            
            # Status indicators
            def status_icon(status):
                if status == 'completed':
                    return "✅"
                elif status == 'running':
                    return "🔄"
                else:
                    return "❌"
            
            batch_df['Status_Icon'] = batch_df['STATUS'].apply(status_icon)
            
            batch_display = batch_df[['Status_Icon', 'BATCH_ID', 'TOTAL_PATIENTS', 'SUCCESS_RATE', 'DURATION_MINUTES']].head(10)
            batch_display.columns = ['Status', 'Batch ID', 'Patients', 'Success %', 'Duration (min)']
            
            st.dataframe(batch_display, hide_index=True)
    
    with tab5:
        st.markdown("### 💰 Cost-Benefit Analysis")
        
        value_df = load_cost_effectiveness(conn)
        
        if not value_df.empty and len(value_df) > 0:
            value = value_df.iloc[0]
            
            # Value metrics
            st.markdown("#### AI Value Generation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Rare Diseases Found",
                    f"{int(value['RARE_DISEASES_FOUND']):,}",
                    f"{value['RARE_DISEASE_RATE']:.1f}% of patients",
                    help="Rare or unusual presentations identified"
                )
            
            with col2:
                st.metric(
                    "Drug Interactions",
                    f"{int(value['INTERACTIONS_FOUND']):,}",
                    f"{value['INTERACTION_RATE']:.1f}% of patients",
                    help="Potential drug interactions detected"
                )
            
            with col3:
                st.metric(
                    "High-Cost Cases",
                    f"{int(value['HIGH_COST_IDENTIFIED']):,}",
                    f"{value['HIGH_COST_RATE']:.1f}% of patients",
                    help="High-cost patients identified for intervention"
                )
            
            # ROI calculation
            st.markdown("#### Return on Investment")
            
            # Estimate value generated
            rare_disease_value = value['RARE_DISEASES_FOUND'] * 50000  # Early diagnosis value
            interaction_value = value['INTERACTIONS_FOUND'] * 10000    # Prevented adverse events
            cost_reduction_value = value['HIGH_COST_IDENTIFIED'] * 5000  # Cost optimization
            
            total_value = rare_disease_value + interaction_value + cost_reduction_value
            
            # Processing cost estimate (simplified)
            total_analyses = value['PATIENTS_ANALYZED']
            processing_cost = total_analyses * 0.50  # Estimated $0.50 per analysis
            
            roi = ((total_value - processing_cost) / processing_cost * 100) if processing_cost > 0 else 0
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Estimated Value Generated**: ${total_value:,.0f}")
                st.caption("Based on early detection and prevention benefits")
            
            with col2:
                st.success(f"**Estimated ROI**: {roi:,.0f}%")
                st.caption(f"Processing cost: ${processing_cost:,.0f}")
            
            # Value breakdown
            fig_value = px.pie(
                values=[rare_disease_value, interaction_value, cost_reduction_value],
                names=['Rare Disease Detection', 'Drug Safety', 'Cost Optimization'],
                title='Value Generation by Category'
            )
            st.plotly_chart(fig_value, use_container_width=True)
    
    with tab6:
        st.markdown("### 🔧 Prompt Engineering Insights")
        
        # Display current prompt configuration
        st.markdown("#### Active Prompt Templates")
        
        with st.expander("View Configurable Prompts"):
            st.code("""
# Example prompt structure for differential diagnosis:

DIFFERENTIAL_DIAGNOSIS_PROMPT = '''
Analyze these patient notes and provide differential diagnoses:

{patient_notes}

Create a JSON response with the following structure:
{{
    "chief_complaint": "Main presenting complaint",
    "key_findings": [...],
    "differential_diagnoses": [...],
    "diagnostic_reasoning": "Brief explanation"
}}

Focus on the most likely diagnoses based on the clinical presentation.
'''
            """, language='python')
        
        st.markdown("#### Prompt Optimization Tips")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### ✅ Best Practices")
            st.markdown("""
            - Clear JSON structure specification
            - Specific field requirements
            - Context-appropriate instructions
            - Output format examples
            - Focused scope definition
            """)
        
        with col2:
            st.markdown("##### ❌ Common Issues")
            st.markdown("""
            - Vague output requirements
            - Missing structure definition
            - Overly complex prompts
            - Inconsistent formatting
            - Token limit exceeded
            """)
        
        # Prompt testing interface
        st.markdown("#### Test Prompt Modifications")
        
        st.info("💡 In production, this interface would allow real-time prompt testing and comparison")
        
        test_prompt = st.text_area(
            "Test Prompt Template",
            value="Enter a modified prompt template here to test effectiveness...",
            height=150
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Test Prompt", type="primary"):
                st.success("Prompt test initiated (demo mode)")
        
        with col2:
            if st.button("Compare Prompts"):
                st.info("Comparison analysis started (demo mode)")
        
        with col3:
            if st.button("Save Template"):
                st.success("Template saved to configuration (demo mode)")
    
    # System recommendations
    st.markdown("---")
    st.markdown("### 🎯 Performance Optimization Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Immediate Optimizations")
        st.markdown("""
        1. **Cache Frequent Queries**: Implement result caching for common analyses
        2. **Batch Size Tuning**: Optimize batch sizes based on performance data
        3. **Model Selection**: Use faster models for time-sensitive operations
        4. **Prompt Refinement**: Simplify prompts to reduce token usage
        """)
    
    with col2:
        st.markdown("#### Long-term Improvements")
        st.markdown("""
        1. **Fine-tune Models**: Create specialized models for medical domain
        2. **Parallel Processing**: Implement concurrent analysis pipelines
        3. **Smart Routing**: Route requests to optimal models by complexity
        4. **Continuous Learning**: Implement feedback loops for quality improvement
        """)
    
    conn.close()

if __name__ == "__main__":
    main()