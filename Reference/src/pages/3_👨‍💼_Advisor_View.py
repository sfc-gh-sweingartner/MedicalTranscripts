import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from connection_helper import get_snowflake_connection, execute_query, safe_execute_query

# Set page config
st.set_page_config(
    page_title="Advisor View",
    page_icon="👨‍💼",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.customer-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 1rem;
    margin: 1rem 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.action-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}
.urgent-action {
    border-left-color: #dc3545;
    background-color: #fff5f5;
}
.medium-action {
    border-left-color: #ffc107;
    background-color: #fffbf0;
}
.low-action {
    border-left-color: #28a745;
    background-color: #f0fff4;
}
.metric-box {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e9ecef;
    text-align: center;
    margin: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.call-history-item {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #6c757d;
    margin: 0.5rem 0;
}
.positive-sentiment {
    border-left-color: #28a745;
}
.negative-sentiment {
    border-left-color: #dc3545;
}
.neutral-sentiment {
    border-left-color: #ffc107;
}
.action-button {
    background-color: #007bff;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    border: none;
    font-weight: bold;
    margin: 0.5rem;
    cursor: pointer;
    width: 100%;
}
.action-button.urgent {
    background-color: #dc3545;
}
.action-button.medium {
    background-color: #fd7e14;
}
</style>
""", unsafe_allow_html=True)

# Page header
st.title("👨‍💼 Advisor View")
st.markdown("### Customer 360 with Actionable Insights")

# Check connection
@st.cache_resource(show_spinner="Connecting to customer data...")
def get_connection():
    return get_snowflake_connection()

conn = get_connection()

if conn is None:
    st.error("❌ Unable to connect to Snowflake. Please check your connection.")
    st.stop()

# Customer search and selection
st.header("🔍 Customer Lookup")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Load customer list for dropdown
    @st.cache_data(ttl=300)
    def load_customer_list():
        try:
            query = """
            SELECT 
                CUSTOMER_ID,
                CUSTOMER_NAME,
                CHURN_RISK_SCORE,
                CHURN_PROBABILITY
            FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER_360_VIEW
            ORDER BY CHURN_PROBABILITY DESC, CUSTOMER_NAME
            """
            result = execute_query(query, conn)
            return result
        except Exception as e:
            # Fallback data
            return pd.DataFrame({
                'CUSTOMER_ID': ['CUST003', 'CUST005', 'CUST002', 'CUST004', 'CUST001'],
                'CUSTOMER_NAME': ['Maria Garcia', 'Lisa Thompson', 'David Wilson', 'John Smith', 'Sarah Chen'],
                'CHURN_RISK_SCORE': ['High', 'High', 'Medium', 'Low', 'Low'],
                'CHURN_PROBABILITY': [0.78, 0.71, 0.42, 0.18, 0.15]
            })
    
    customers_df = load_customer_list()
    
    # Create customer options with risk indicators
    customer_options = []
    for idx, customer in customers_df.iterrows():
        risk_emoji = "🔴" if customer['CHURN_RISK_SCORE'] == 'High' else ("🟡" if customer['CHURN_RISK_SCORE'] == 'Medium' else "🟢")
        option = f"{risk_emoji} {customer['CUSTOMER_NAME']} ({customer['CUSTOMER_ID']}) - {customer['CHURN_RISK_SCORE']} Risk"
        customer_options.append(option)
    
    # Get selected customer from session state or default to first
    default_customer = st.session_state.get('selected_customer', 'CUST003')
    default_index = 0
    for i, option in enumerate(customer_options):
        if default_customer in option:
            default_index = i
            break
    
    selected_option = st.selectbox(
        "Select Customer:",
        customer_options,
        index=default_index,
        help="Choose a customer to view their 360-degree profile"
    )
    
    # Extract customer ID from selection
    selected_customer_id = selected_option.split('(')[1].split(')')[0]

with col2:
    if st.button("🔄 Refresh Data", help="Reload latest customer data"):
        st.cache_data.clear()
        st.rerun()

with col3:
    if st.button("📞 Call Customer", help="Initiate customer call"):
        st.success("Call initiated...")

# Load selected customer data
@st.cache_data(ttl=300)
def load_customer_360(customer_id):
    """Load comprehensive customer 360 data"""
    try:
        customer_query = """
        SELECT *
        FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER_360_VIEW
        WHERE CUSTOMER_ID = %s
        """
        
        calls_query = """
        SELECT 
            e.CALL_ID,
            e.CALL_TIMESTAMP,
            e.SENTIMENT_SCORE,
            e.SENTIMENT_LABEL,
            e.PRIMARY_INTENT,
            e.CALL_SUMMARY,
            e.CUSTOMER_CONCERNS,
            e.KEY_TOPICS,
            r.CALL_DURATION_SECONDS,
            LEFT(r.TRANSCRIPT_TEXT, 200) as TRANSCRIPT_PREVIEW
        FROM SUPERANNUATION.TRANSCRIPTS.ENRICHED_TRANSCRIPTS_ALL e
        JOIN SUPERANNUATION.TRANSCRIPTS.RAW_CALL_TRANSCRIPTS r ON e.CALL_ID = r.CALL_ID
        WHERE e.CUSTOMER_ID = %s
        ORDER BY e.CALL_TIMESTAMP DESC
        LIMIT 10
        """
        
        customer_data = execute_query(customer_query.replace('%s', f"'{customer_id}'"), conn)
        calls_data = execute_query(calls_query.replace('%s', f"'{customer_id}'"), conn)
        
        return customer_data, calls_data
        
    except Exception as e:
        # Fallback data for demo
        fallback_customer = pd.DataFrame({
            'CUSTOMER_ID': [customer_id],
            'CUSTOMER_NAME': ['Maria Garcia'] if customer_id == 'CUST003' else ['John Smith'],
            'AGE': [42] if customer_id == 'CUST003' else [45],
            'TENURE_YEARS': [8] if customer_id == 'CUST003' else [7],
            'ACCOUNT_BALANCE': [89000] if customer_id == 'CUST003' else [180000],
            'INVESTMENT_OPTION': ['Balanced'] if customer_id == 'CUST003' else ['Growth'],
            'CONTACT_PREFERENCE': ['Phone'],
            'CHURN_PROBABILITY': [0.78] if customer_id == 'CUST003' else [0.18],
            'CHURN_RISK_SCORE': ['High'] if customer_id == 'CUST003' else ['Low'],
            'MODEL_CONFIDENCE': [87.5],
            'NEXT_BEST_ACTION': ['URGENT: Senior advisor intervention required'] if customer_id == 'CUST003' else ['ESG investment opportunity'],
            'NBA_REASONING': ['High churn risk requires immediate intervention'] if customer_id == 'CUST003' else ['Customer shows interest in sustainable investing'],
            'RECENT_CALL_COUNT': [4] if customer_id == 'CUST003' else [2],
            'AVG_SENTIMENT_SCORE': [-0.7] if customer_id == 'CUST003' else [0.3],
            'LAST_CALL_DATE': ['2025-07-10'],
            'LAST_CALL_SENTIMENT': ['Negative'] if customer_id == 'CUST003' else ['Positive'],
            'LAST_CALL_EMOTION': ['Frustrated'] if customer_id == 'CUST003' else ['Interested'],
            'LAST_CALL_INTENT': ['Technical Support'] if customer_id == 'CUST003' else ['Investment Inquiry'],
            'LAST_CALL_SUMMARY': ['Customer experiencing login issues, expressing frustration'] if customer_id == 'CUST003' else ['Customer interested in ESG investment options']
        })
        
        fallback_calls = pd.DataFrame({
            'CALL_ID': ['CALL001'],
            'CALL_TIMESTAMP': ['2025-07-10 09:30:00'],
            'SENTIMENT_SCORE': [-0.8] if customer_id == 'CUST003' else [0.6],
            'SENTIMENT_LABEL': ['Negative'] if customer_id == 'CUST003' else ['Positive'],
            'PRIMARY_INTENT': ['Technical Support'] if customer_id == 'CUST003' else ['Investment Inquiry'],
            'CALL_SUMMARY': ['Customer experiencing repeated login issues'] if customer_id == 'CUST003' else ['Customer interested in ESG investments'],
            'CUSTOMER_INSIGHTS': ['Escalating frustration with technical issues over multiple calls. Strong churn risk signals present.'] if customer_id == 'CUST003' else ['Positive engagement with interest in sustainable investing. Good upsell opportunity.'],
            'CALL_DURATION_SECONDS': [320],
            'TRANSCRIPT_PREVIEW': ['I am having trouble logging into my account again...'] if customer_id == 'CUST003' else ['Hi, I wanted to inquire about ESG investment options...']
        })
        
        return fallback_customer, fallback_calls

customer_data, calls_data = load_customer_360(selected_customer_id)

if customer_data.empty:
    st.error(f"Customer {selected_customer_id} not found")
    st.stop()

customer = customer_data.iloc[0]

# Customer overview card
st.markdown("---")
st.markdown(f"""
<div class="customer-card">
    <h2>👤 {customer['CUSTOMER_NAME']}</h2>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <p><strong>Customer ID:</strong> {customer['CUSTOMER_ID']}</p>
            <p><strong>Age:</strong> {customer['AGE']} years | <strong>Tenure:</strong> {customer['TENURE_YEARS']} years</p>
            <p><strong>Investment Option:</strong> {customer['INVESTMENT_OPTION']} | <strong>Contact:</strong> {customer['CONTACT_PREFERENCE']}</p>
        </div>
        <div style="text-align: right;">
            <h3>${customer['ACCOUNT_BALANCE']:,.0f}</h3>
            <p>Account Balance</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Key metrics dashboard
st.header("📊 Key Metrics & Risk Assessment")

col1, col2, col3, col4 = st.columns(4)

with col1:
    risk_color = "#dc3545" if customer['CHURN_RISK_SCORE'] == 'High' else ("#fd7e14" if customer['CHURN_RISK_SCORE'] == 'Medium' else "#28a745")
    st.markdown(f"""
    <div class="metric-box" style="border-left: 4px solid {risk_color};">
        <h3 style="color: {risk_color}; margin: 0;">{customer['CHURN_RISK_SCORE']}</h3>
        <p style="margin: 0.5rem 0 0 0;">Churn Risk</p>
        <small>{customer['CHURN_PROBABILITY']:.0%} probability</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    sentiment_color = "#28a745" if customer['AVG_SENTIMENT_SCORE'] > 0 else "#dc3545"
    st.markdown(f"""
    <div class="metric-box" style="border-left: 4px solid {sentiment_color};">
        <h3 style="color: {sentiment_color}; margin: 0;">{customer['AVG_SENTIMENT_SCORE']:+.2f}</h3>
        <p style="margin: 0.5rem 0 0 0;">Avg Sentiment</p>
        <small>Recent calls</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <h3 style="color: #007bff; margin: 0;">{customer['MODEL_CONFIDENCE']:.1f}%</h3>
        <p style="margin: 0.5rem 0 0 0;">ML Confidence</p>
        <small>Prediction accuracy</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <h3 style="color: #6f42c1; margin: 0;">{customer['RECENT_CALL_COUNT']}</h3>
        <p style="margin: 0.5rem 0 0 0;">Recent Calls</p>
        <small>Last 30 days</small>
    </div>
    """, unsafe_allow_html=True)

# Next Best Action section
st.markdown("---")
st.header("💡 Recommended Actions")

col1, col2 = st.columns([2, 1])

with col1:
    # Determine action priority styling
    action_class = "urgent-action" if customer['CHURN_RISK_SCORE'] == 'High' else ("medium-action" if customer['CHURN_RISK_SCORE'] == 'Medium' else "low-action")
    
    st.markdown(f"""
    <div class="action-card {action_class}">
        <h4>🎯 Next Best Action</h4>
        <p><strong>{customer['NEXT_BEST_ACTION']}</strong></p>
        <hr>
        <h5>🧠 AI Reasoning</h5>
        <p><em>{customer['NBA_REASONING']}</em></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Quick Actions")
    
    if customer['CHURN_RISK_SCORE'] == 'High':
        if st.button("🚨 Escalate to Senior Advisor", key="escalate", type="primary"):
            st.success("Escalation initiated - Senior advisor will call within 2 hours")
        
        if st.button("📞 Schedule Urgent Call", key="urgent_call"):
            st.success("Urgent call scheduled for today")
    
    if st.button("📧 Send Personalized Email", key="email"):
        st.success("Personalized email sent based on AI insights")
    
    if st.button("📝 Add Customer Note", key="note"):
        note = st.text_area("Add note:", key="customer_note")
        if note:
            st.success("Note added to customer record")
    
    if st.button("📊 Generate Report", key="report"):
        st.success("Customer risk report generated")

# Call history and sentiment analysis
st.markdown("---")
st.header("📞 Call History & Sentiment Analysis")

col1, col2 = st.columns([3, 1])

with col1:
    if not calls_data.empty:
        st.subheader("Recent Call Interactions")
        
        for idx, call in calls_data.iterrows():
            sentiment_class = "positive-sentiment" if call['SENTIMENT_SCORE'] > 0.3 else ("negative-sentiment" if call['SENTIMENT_SCORE'] < -0.3 else "neutral-sentiment")
            
            with st.expander(f"📞 {call['CALL_TIMESTAMP']} - {call['PRIMARY_INTENT']} ({call['SENTIMENT_LABEL']})"):
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.markdown(f"**Call Summary:** {call['CALL_SUMMARY']}")
                    
                    # Display customer concerns if available
                    if call.get('CUSTOMER_CONCERNS') and call['CUSTOMER_CONCERNS'] not in [None, 'null', '']:
                        concerns_text = str(call['CUSTOMER_CONCERNS']).strip('[]"').replace('","', ', ')
                        st.markdown(f"**Customer Concerns:** {concerns_text}")
                    
                    # Display key topics if available
                    if call.get('KEY_TOPICS') and call['KEY_TOPICS'] not in [None, 'null', '']:
                        topics_text = str(call['KEY_TOPICS']).strip('[]"').replace('","', ', ')
                        st.markdown(f"**Key Topics:** {topics_text}")
                    
                    st.markdown(f"**Transcript Preview:** {call['TRANSCRIPT_PREVIEW']}...")
                
                with col_b:
                    st.metric("Sentiment", f"{call['SENTIMENT_SCORE']:+.2f}")
                    st.metric("Duration", f"{call['CALL_DURATION_SECONDS']}s")
                    st.metric("Intent", call['PRIMARY_INTENT'])

with col2:
    if not calls_data.empty:
        st.subheader("Sentiment Trend")
        
        # Create sentiment trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=calls_data['CALL_TIMESTAMP'],
            y=calls_data['SENTIMENT_SCORE'],
            mode='lines+markers',
            name='Sentiment Score',
            line=dict(color='#007bff', width=2),
            marker=dict(size=8)
        ))
        
        # Add neutral line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        
        fig.update_layout(
            title="Sentiment Over Time",
            xaxis_title="Call Date",
            yaxis_title="Sentiment Score",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Intent distribution
        if len(calls_data) > 1:
            intent_counts = calls_data['PRIMARY_INTENT'].value_counts()
            fig_intent = px.pie(
                values=intent_counts.values,
                names=intent_counts.index,
                title="Call Intent Distribution"
            )
            fig_intent.update_layout(height=250)
            st.plotly_chart(fig_intent, use_container_width=True)

# Latest interaction details
if not calls_data.empty:
    latest_call = calls_data.iloc[0]
    
    st.markdown("---")
    st.header("📋 Latest Interaction Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Call Information")
        st.markdown(f"**Date:** {latest_call['CALL_TIMESTAMP']}")
        st.markdown(f"**Duration:** {latest_call['CALL_DURATION_SECONDS']} seconds")
        st.markdown(f"**Intent:** {latest_call['PRIMARY_INTENT']}")
    
    with col2:
        st.markdown("### AI Analysis")
        st.markdown(f"**Sentiment Score:** {latest_call['SENTIMENT_SCORE']:+.2f}")
        st.markdown(f"**Sentiment Label:** {latest_call['SENTIMENT_LABEL']}")
        st.markdown(f"**Call Summary:** {latest_call['CALL_SUMMARY']}")
    
    with col3:
        st.markdown("### Follow-up Required")
        if latest_call['SENTIMENT_SCORE'] < -0.5:
            st.error("🚨 Immediate follow-up required due to negative sentiment")
        elif latest_call['SENTIMENT_SCORE'] < 0:
            st.warning("⚠️ Follow-up recommended within 24 hours")
        else:
            st.success("✅ Standard follow-up timeframe appropriate")

# Customer timeline/activity log
st.markdown("---")
st.header("📅 Customer Activity Timeline")

timeline_data = [
    {"date": "2025-07-10", "event": f"Call - {latest_call['PRIMARY_INTENT'] if not calls_data.empty else 'Technical Support'}", "status": "recent"},
    {"date": "2025-07-08", "event": "Email opened - Investment update", "status": "normal"},
    {"date": "2025-07-05", "event": "Account balance inquiry online", "status": "normal"},
    {"date": "2025-07-01", "event": "Contribution processed - $500", "status": "positive"},
    {"date": "2025-06-28", "event": "Portfolio rebalancing", "status": "normal"}
]

for item in timeline_data:
    icon = "🔴" if item["status"] == "recent" else ("🟢" if item["status"] == "positive" else "🔵")
    st.markdown(f"{icon} **{item['date']}** - {item['event']}")

# Summary and recommendations
st.markdown("---")
st.success(f"""
**👨‍💼 Advisor Summary for {customer['CUSTOMER_NAME']}**: 
{customer['CHURN_RISK_SCORE']} churn risk customer requiring {"immediate" if customer['CHURN_RISK_SCORE'] == 'High' else "proactive"} attention. 
AI analysis indicates {customer['PRIMARY_INTENT'] if 'PRIMARY_INTENT' in customer else 'service-related'} focus with 
{customer['CHURN_PROBABILITY']:.0%} churn probability. Recommended action: {customer['NEXT_BEST_ACTION'][:100]}...
""")

 