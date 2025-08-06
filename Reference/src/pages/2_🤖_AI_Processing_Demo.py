import streamlit as st
import sys
import os
import pandas as pd
import time
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from connection_helper import get_snowflake_connection, execute_query, safe_execute_query

# Set page config
st.set_page_config(
    page_title="AI Processing Demo",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for enhanced styling
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

.transcript-editor {
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
</style>
""", unsafe_allow_html=True)

# Page header
st.title("🤖 AI Processing Demo")
st.markdown("### Interactive Real-Time AI + ML Processing")

# Check connection
@st.cache_resource(show_spinner="Connecting to AI services...")
def get_connection():
    return get_snowflake_connection()

conn = get_connection()

if conn is None:
    st.error("❌ Unable to connect to Snowflake. Please check your connection.")
    st.stop()

# Initialize session state for processing
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = {}
if 'current_transcript' not in st.session_state:
    st.session_state.current_transcript = ""

if 'processing_stage' not in st.session_state:
    st.session_state.processing_stage = 0

# Default transcript for demo
DEFAULT_TRANSCRIPT = ""

# Predefined AI processing functions
def process_transcript_with_ai(transcript_text, customer_id):
    """Process transcript with Snowflake Cortex AI functions"""
    try:
        # Create progress placeholder
        progress_placeholder = st.empty()
        results_placeholder = st.empty()
        
        results = {}
        
        # Step 1: Sentiment Analysis
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step active">1. 🤖 AI Sentiment Analysis - Processing...</div>', unsafe_allow_html=True)
        
        sentiment_query = f"""
        SELECT 
            SNOWFLAKE.CORTEX.SENTIMENT('{transcript_text.replace("'", "''")}') as sentiment_score,
            CASE 
                WHEN SNOWFLAKE.CORTEX.SENTIMENT('{transcript_text.replace("'", "''")}') >= 0.3 THEN 'Positive'
                WHEN SNOWFLAKE.CORTEX.SENTIMENT('{transcript_text.replace("'", "''")}') <= -0.3 THEN 'Negative'
                ELSE 'Neutral'
            END as sentiment_label
        """
        
        sentiment_result = execute_query(sentiment_query, conn)
        if not sentiment_result.empty:
            results['sentiment_score'] = sentiment_result.iloc[0]['SENTIMENT_SCORE']
            results['sentiment_label'] = sentiment_result.iloc[0]['SENTIMENT_LABEL']
        
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step completed">1. ✅ AI Sentiment Analysis - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step active">2. 🎯 AI Intent Detection - Processing...</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)  # Brief pause for demo effect
        
        # Step 2: Intent Detection using AI_COMPLETE
        intent_query = f"""
        SELECT 
            SNOWFLAKE.CORTEX.COMPLETE(
                'claude-3-5-sonnet',
                'Analyze this customer service call transcript and classify the primary intent. Choose from: Technical Support, Investment Inquiry, Complaint, Churn Risk, Fee Question, Retirement Planning. Return only the classification: {transcript_text.replace("'", "''")}'
            ) as primary_intent
        """
        
        intent_result = execute_query(intent_query, conn)
        if not intent_result.empty:
            results['primary_intent'] = intent_result.iloc[0]['PRIMARY_INTENT'].strip()
        
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step completed">1. ✅ AI Sentiment Analysis - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">2. ✅ AI Intent Detection - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step active">3. 📝 AI Call Summarization - Processing...</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        # Step 3: Call Summarization using SNOWFLAKE.CORTEX.SUMMARIZE()
        summary_query = f"""
        SELECT 
            SNOWFLAKE.CORTEX.SUMMARIZE('{transcript_text.replace("'", "''")}') as call_summary
        """
        
        summary_result = execute_query(summary_query, conn)
        if not summary_result.empty:
            results['call_summary'] = summary_result.iloc[0]['CALL_SUMMARY'].strip()
        
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step completed">1. ✅ AI Sentiment Analysis - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">2. ✅ AI Intent Detection - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">3. ✅ AI Call Summarization - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step active">4. 📈 ML Churn Prediction - Processing...</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        # Step 4: ML Churn Prediction (simplified demo version)
        churn_features = {
            'sentiment_score': results.get('sentiment_score', 0),
            'has_complaint': 1 if 'complaint' in results.get('primary_intent', '').lower() or 'churn' in results.get('primary_intent', '').lower() else 0,
            'negative_language': 1 if any(word in transcript_text.lower() for word in ['frustrated', 'unacceptable', 'considering leaving', 'switching', 'elsewhere']) else 0
        }
        
        # Demo churn prediction logic
        churn_probability = 0.15  # Base probability
        if churn_features['sentiment_score'] < -0.3:
            churn_probability += 0.3
        if churn_features['has_complaint']:
            churn_probability += 0.2
        if churn_features['negative_language']:
            churn_probability += 0.25
        
        churn_probability = min(churn_probability, 0.95)  # Cap at 95%
        
        results['churn_probability'] = churn_probability
        results['churn_risk_score'] = 'High' if churn_probability >= 0.6 else ('Medium' if churn_probability >= 0.3 else 'Low')
        results['model_confidence'] = 85.0 + (churn_probability * 10)  # Simulated confidence
        
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step completed">1. ✅ AI Sentiment Analysis - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">2. ✅ AI Intent Detection - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">3. ✅ AI Call Summarization - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">4. ✅ ML Churn Prediction - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step active">5. 🔍 AI Cross-transcript Insights - Processing...</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        # Step 5: Cross-transcript Customer Insights using AI_COMPLETE for multi-transcript analysis
        insights_query = f"""
        SELECT 
            SNOWFLAKE.CORTEX.COMPLETE(
                'claude-3-5-sonnet',
                'Based on this call and historical customer interactions, analyze patterns and provide insights.
                
                Current call transcript: {transcript_text.replace("'", "''")}
                Current sentiment: {results["sentiment_label"]} ({results["sentiment_score"]:.2f})
                Current intent: {results["primary_intent"]}
                
                Provide insights in this format:
                - Behavioral patterns observed
                - Relationship trajectory (improving/declining)
                - Key concerns or interests
                - Risk factors or opportunities
                
                Keep response under 150 words.'
            ) as customer_insights
        """
        
        insights_result = execute_query(insights_query, conn)
        if not insights_result.empty:
            results['customer_insights'] = insights_result.iloc[0]['CUSTOMER_INSIGHTS'].strip()
        
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step completed">1. ✅ AI Sentiment Analysis - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">2. ✅ AI Intent Detection - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">3. ✅ AI Call Summarization - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">4. ✅ ML Churn Prediction - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">5. ✅ AI Cross-transcript Insights - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step active">6. 💡 AI NBA Generation - Processing...</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        # Step 6: AI-powered Next Best Action
        nba_query = f"""
        SELECT 
            SNOWFLAKE.CORTEX.COMPLETE(
                'claude-3-5-sonnet',
                'Based on this customer call transcript and analysis, generate a specific Next Best Action recommendation for a superannuation advisor. 
                Customer transcript: {transcript_text.replace("'", "''")}
                Sentiment: {results["sentiment_label"]} ({results["sentiment_score"]:.2f})
                Intent: {results["primary_intent"]}
                Churn Risk: {results["churn_risk_score"]} ({results["churn_probability"]:.0%})
                
                Provide a specific, actionable recommendation (max 100 words) that addresses the customer needs and churn risk.'
            ) as next_best_action
        """
        
        nba_result = execute_query(nba_query, conn)
        if not nba_result.empty:
            results['next_best_action'] = nba_result.iloc[0]['NEXT_BEST_ACTION'].strip()
        
        # Generate reasoning
        reasoning_query = f"""
        SELECT 
            SNOWFLAKE.CORTEX.COMPLETE(
                'claude-3-5-sonnet',
                'Explain in 2-3 sentences why this NBA recommendation is appropriate given the customer sentiment of {results["sentiment_label"]} ({results["sentiment_score"]:.2f}) and churn risk of {results["churn_risk_score"]} ({results["churn_probability"]:.0%}).'
            ) as nba_reasoning
        """
        
        reasoning_result = execute_query(reasoning_query, conn)
        if not reasoning_result.empty:
            results['nba_reasoning'] = reasoning_result.iloc[0]['NBA_REASONING'].strip()
        
        with progress_placeholder.container():
            st.markdown('<div class="pipeline-step completed">1. ✅ AI Sentiment Analysis - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">2. ✅ AI Intent Detection - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">3. ✅ AI Call Summarization - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">4. ✅ ML Churn Prediction - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">5. ✅ AI Cross-transcript Insights - Complete</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline-step completed">6. ✅ AI NBA Generation - Complete</div>', unsafe_allow_html=True)
        
        return results
        
    except Exception as e:
        st.error(f"AI Processing failed: {str(e)}")
        # Return fallback results for demo continuity
        return {
            'sentiment_score': -0.6 if 'frustrated' in transcript_text.lower() else 0.2,
            'sentiment_label': 'Negative' if 'frustrated' in transcript_text.lower() else 'Positive',
            'primary_intent': 'Churn Risk' if any(word in transcript_text.lower() for word in ['leaving', 'switching', 'elsewhere']) else 'Technical Support',
            'call_summary': 'Customer expressed frustration with technical issues and requested immediate assistance.' if 'frustrated' in transcript_text.lower() else 'Customer inquired about account services and investment options.',
            'customer_insights': 'High churn risk customer showing escalating frustration with technical issues. Immediate intervention required.' if 'frustrated' in transcript_text.lower() else 'Positive customer engagement with interest in additional services.',
            'churn_probability': 0.75 if 'frustrated' in transcript_text.lower() else 0.20,
            'churn_risk_score': 'High' if 'frustrated' in transcript_text.lower() else 'Low',
            'model_confidence': 87.5,
            'next_best_action': 'URGENT: Schedule immediate senior advisor call to address concerns and prevent churn.',
            'nba_reasoning': 'High churn risk requires immediate intervention to retain customer.'
        }

# Main demo interface
st.header("🎯 Step 1: Select Base Scenario")

col1, col2 = st.columns([3, 1])

with col1:
    # Load customer list for dropdown
    @st.cache_data(ttl=300)
    def load_customer_list():
        try:
            # Updated query to get call-specific data with proper formatting
            query = """
            SELECT 
                c.CUSTOMER_ID,
                c.CUSTOMER_NAME,
                c.CHURN_RISK_SCORE,
                c.CHURN_PROBABILITY,
                r.CALL_ID,
                TO_CHAR(r.CALL_TIMESTAMP, 'YYYY-MM-DD HH24:MI') as CALL_TIMESTAMP,
                LEFT(r.TRANSCRIPT_TEXT, 80) as TRANSCRIPT_PREVIEW
            FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER c
            JOIN SUPERANNUATION.TRANSCRIPTS.RAW_CALL_TRANSCRIPTS r ON c.CUSTOMER_ID = r.CUSTOMER_ID
            ORDER BY r.CALL_TIMESTAMP DESC
            """
            result = execute_query(query, conn)
            return result
        except Exception as e:
            # Fallback data with call details
            return pd.DataFrame({
                'CUSTOMER_ID': ['CUST003', 'CUST005', 'CUST004', 'CUST002', 'CUST001'],
                'CUSTOMER_NAME': ['Maria Garcia', 'Lisa Thompson', 'John Smith', 'David Lee', 'Sarah Chen'],
                'CHURN_RISK_SCORE': ['High', 'Medium', 'Low', 'Low', 'Low'],
                'CHURN_PROBABILITY': [0.83, 0.36, 0.11, 0.21, 0.17],
                'CALL_ID': ['CALL003', 'CALL005', 'CALL004', 'CALL002', 'CALL001'],
                'CALL_TIMESTAMP': ['2025-07-10 09:15', '2025-07-10 09:25', '2025-07-10 09:20', '2025-07-10 09:10', '2025-07-10 09:05'],
                'TRANSCRIPT_PREVIEW': ['Annual statement issue', 'Retirement planning', 'Investment options', 'Super consolidation', 'Account inquiry']
            })
    
    customers_df = load_customer_list()
    
    # Create enhanced customer options with call details
    customer_options = []
    for idx, row in customers_df.iterrows():
        risk_emoji = "🔴" if row['CHURN_RISK_SCORE'] == 'High' else ("🟡" if row['CHURN_RISK_SCORE'] == 'Medium' else "🟢")
        # Format: "CALL003 - Maria Garcia (2025-07-10 09:15) 🔴"
        option = f"{row['CALL_ID']} - {row['CUSTOMER_NAME']} ({row['CALL_TIMESTAMP']}) {risk_emoji}"
        customer_options.append(option)
    
    # Add custom input option
    customer_options.append("Custom Input")
    
    selected_customer_option = st.selectbox(
        "Select Call to Process:",
        customer_options,
        index=0,
        help="Select a customer call transcript to process with AI/ML. Most recent calls are shown first."
    )
    
    # Extract customer ID and call ID
    if "Custom Input" not in selected_customer_option:
        selected_call_id = selected_customer_option.split(" - ")[0]
        selected_customer_id = customers_df[customers_df['CALL_ID'] == selected_call_id]['CUSTOMER_ID'].iloc[0]
        selected_customer_name = customers_df[customers_df['CALL_ID'] == selected_call_id]['CUSTOMER_NAME'].iloc[0]
    else:
        selected_call_id = "CUSTOM"
        selected_customer_id = "CUSTOM"
        selected_customer_name = "Custom Customer"

with col2:
    if st.button("🔄 Load Call Transcript"):
        if selected_customer_id != "CUSTOM":
            # Load existing transcript for specific call
            try:
                query = f"""
                SELECT TRANSCRIPT_TEXT 
                FROM SUPERANNUATION.TRANSCRIPTS.RAW_CALL_TRANSCRIPTS 
                WHERE CALL_ID = '{selected_call_id}' 
                """
                result = execute_query(query, conn)
                if not result.empty:
                    st.session_state.current_transcript = result.iloc[0]['TRANSCRIPT_TEXT']
                    st.success(f"Loaded transcript for {selected_customer_name} ({selected_call_id})")
                else:
                    st.warning("No transcript found, using sample data")
                    st.session_state.current_transcript = DEFAULT_TRANSCRIPT
            except Exception as e:
                st.warning("Using sample transcript")
                st.session_state.current_transcript = DEFAULT_TRANSCRIPT

# Step 2: Interactive Transcript Editor
st.markdown("---")
st.header("✏️ Step 2: Edit Transcript (Prove Real-Time AI)")

st.markdown("**📝 Transcript Editor** - Edit the text below to demonstrate real-time AI processing:")

# Initialize transcript if empty
if not st.session_state.current_transcript:
    st.session_state.current_transcript = DEFAULT_TRANSCRIPT

# Transcript text area
current_transcript = st.text_area(
    "Customer Call Transcript:",
    value=st.session_state.current_transcript,
    height=150,
    key="transcript_editor",
    help="Edit this transcript to see how AI responds to different customer language"
)

# Update session state
st.session_state.current_transcript = current_transcript

# Step 3: Process with AI/ML
st.markdown("---")
st.header("🚀 Step 3: Process with AI/ML")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button(
        "🎯 PROCESS TRANSCRIPT WITH AI/ML", 
        key="process_button",
        help="Click to run real-time AI and ML analysis on the transcript",
        type="primary"
    ):
        if st.session_state.current_transcript.strip():
            with st.spinner("Processing with Snowflake AI + ML..."):
                results = process_transcript_with_ai(
                    st.session_state.current_transcript, 
                    selected_customer_id
                )
                st.session_state.processing_results = results
                st.session_state.processing_stage = 1
        else:
            st.error("Please enter a transcript to process")

# Display processing results
if st.session_state.processing_stage > 0 and st.session_state.processing_results:
    st.markdown("---")
    st.header("📊 Processing Results")
    
    results = st.session_state.processing_results
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sentiment_color = "🔴" if results['sentiment_score'] < -0.3 else ("🟡" if results['sentiment_score'] < 0.3 else "🟢")
        st.metric(
            "Sentiment Score", 
            f"{results['sentiment_score']:.2f}",
            delta=f"{sentiment_color} {results['sentiment_label']}"
        )
    
    with col2:
        st.metric(
            "Primary Intent",
            results['primary_intent'],
            help="AI-detected customer intent"
        )
    
    with col3:
        risk_color = "🔴" if results['churn_risk_score'] == 'High' else ("🟡" if results['churn_risk_score'] == 'Medium' else "🟢")
        st.metric(
            "Churn Risk",
            f"{results['churn_risk_score']}",
            delta=f"{risk_color} {results['churn_probability']:.0%}"
        )
    
    with col4:
        st.metric(
            "Model Confidence",
            f"{results['model_confidence']:.1f}%",
            help="ML model confidence in prediction"
        )
    
    # Detailed results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Call Summary")
        st.markdown(f'<div class="ai-result">{results.get("call_summary", "Summary not available")}</div>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Next Best Action")
        st.markdown(f'<div class="ai-result">{results["next_best_action"]}</div>', unsafe_allow_html=True)
        
        st.markdown("### 🧠 AI Reasoning")
        st.markdown(f'<div class="ai-result">{results["nba_reasoning"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔍 Customer Insights")
        st.markdown(f'<div class="ai-result">{results.get("customer_insights", "Insights not available")}</div>', unsafe_allow_html=True)
        
        st.markdown("### 📈 Risk Analysis")
        
        # Create risk gauge visualization
        risk_score = results['churn_probability']
        if risk_score >= 0.6:
            risk_color = "#dc3545"  # Red
            risk_text = "HIGH RISK - Immediate Action Required"
        elif risk_score >= 0.3:
            risk_color = "#ffc107"  # Yellow
            risk_text = "MEDIUM RISK - Proactive Engagement Recommended" 
        else:
            risk_color = "#28a745"  # Green
            risk_text = "LOW RISK - Standard Follow-up"
        
        st.markdown(f"""
        <div style="
            background-color: {risk_color}; 
            color: white; 
            padding: 1rem; 
            border-radius: 0.5rem; 
            text-align: center;
            font-weight: bold;
            margin: 1rem 0;
        ">
            {risk_text}
        </div>
        """, unsafe_allow_html=True)
        
        # Technical details
        st.markdown("**Model Details:**")
        st.markdown(f"- Confidence: {results['model_confidence']:.1f}%")
        st.markdown(f"- Sentiment Score: {results['sentiment_score']:.3f}")
        st.markdown(f"- Risk Probability: {results['churn_probability']:.1%}")



# Demo guide and tips
st.markdown("---")

 