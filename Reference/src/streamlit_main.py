import streamlit as st
import sys
import os

# Add the src directory to Python path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from connection_helper import get_snowflake_connection
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Superannuation Transcripts",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f4e79;
    text-align: center;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #2e5984;
    text-align: center;
    margin-bottom: 2rem;
}
.scenario-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f4e79;
    margin: 1rem 0;
}
.metric-card {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
    margin: 0.5rem;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.danger-box {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for demo scenarios
if 'selected_customer' not in st.session_state:
    st.session_state.selected_customer = 'CUST003'  # Default to Maria Garcia
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = 'guided'  # guided or free
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None

# Main application header
st.markdown('<h1 class="main-header">🏦 Superannuation Transcripts</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform Customer Interactions with AI + ML Intelligence</p>', unsafe_allow_html=True)

# Connection status check
@st.cache_resource(show_spinner="Connecting to Snowflake...")
def check_connection():
    """Check Snowflake connection and return status"""
    try:
        conn = get_snowflake_connection()
        if conn:
            return "✅ Connected to Snowflake"
        else:
            return "❌ Failed to connect to Snowflake"
    except Exception as e:
        return f"❌ Connection error: {str(e)}"

# Display connection status - only show errors
if st.session_state.connection_status is None:
    st.session_state.connection_status = check_connection()

# Only display connection status if there's an error
if "❌" in st.session_state.connection_status:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div class="danger-box">{st.session_state.connection_status}</div>', unsafe_allow_html=True)

st.markdown("---")

# Demo Overview Section
st.header("🎯 Demo Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("What You'll See")
    st.markdown("""
    - **📊 Data Foundation**: Raw customer data and call transcripts
    - **🤖 AI Processing**: Real-time transcript analysis with ML
    - **👨‍💼 Advisor View**: Customer 360 with actionable insights  
    - **📈 Manager Dashboard**: Strategic oversight and trends
    - **🔬 ML Performance**: Technical model analysis
    """)

with col2:
    st.subheader("Key Capabilities")
    st.markdown("""
    - **Hybrid AI+ML Approach**: 87.3% churn prediction accuracy
    - **Real-time Processing**: Live sentiment and intent analysis
    - **Personalized NBA**: AI-generated next best actions
    - **Enterprise Scale**: Process millions of interactions
    - **Complete Transparency**: Model explainability and confidence
    """)

# Demo Customer Scenarios
st.header("👥 Demo Customer Scenarios")

# Load customer data for scenario selection
@st.cache_data(ttl=300)
def load_demo_customers():
    """Load demo customer data"""
    try:
        conn = get_snowflake_connection()
        if hasattr(conn, 'sql'):  # Snowpark session
            df = conn.sql("""
                SELECT 
                    CUSTOMER_ID,
                    CUSTOMER_NAME,
                    AGE,
                    ACCOUNT_BALANCE,
                    CHURN_RISK_SCORE,
                    CHURN_PROBABILITY,
                    NEXT_BEST_ACTION
                FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER_360_VIEW
                ORDER BY CHURN_PROBABILITY DESC
            """).to_pandas()
        else:  # Regular connection
            df = pd.read_sql("""
                SELECT 
                    CUSTOMER_ID,
                    CUSTOMER_NAME,
                    AGE,
                    ACCOUNT_BALANCE,
                    CHURN_RISK_SCORE,
                    CHURN_PROBABILITY,
                    NEXT_BEST_ACTION
                FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER_360_VIEW
                ORDER BY CHURN_PROBABILITY DESC
            """, conn)
        
        return df
    except Exception as e:
        # Fallback demo data if database connection fails
        return pd.DataFrame({
            'CUSTOMER_ID': ['CUST003', 'CUST005', 'CUST002', 'CUST004', 'CUST001'],
            'CUSTOMER_NAME': ['Maria Garcia', 'Lisa Thompson', 'David Wilson', 'John Smith', 'Sarah Chen'],
            'AGE': [42, 39, 38, 45, 34],
            'ACCOUNT_BALANCE': [89000, 156000, 95000, 180000, 125000],
            'CHURN_RISK_SCORE': ['High', 'High', 'Medium', 'Low', 'Low'],
            'CHURN_PROBABILITY': [0.78, 0.71, 0.42, 0.18, 0.15],
            'NEXT_BEST_ACTION': [
                'URGENT: Senior advisor intervention required',
                'Proactive outreach recommended', 
                'Schedule follow-up call within 48 hours',
                'Offer ESG investment consultation',
                'Standard quarterly review'
            ]
        })

customers_df = load_demo_customers()

# Customer scenario cards
if not customers_df.empty:
    for idx, customer in customers_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                risk_color = "danger" if customer['CHURN_RISK_SCORE'] == 'High' else ("warning" if customer['CHURN_RISK_SCORE'] == 'Medium' else "success")
                st.markdown(f"""
                <div class="{risk_color}-box">
                    <strong>{customer['CUSTOMER_NAME']}</strong> ({customer['CUSTOMER_ID']})<br>
                    Age: {customer['AGE']} | Balance: ${customer['ACCOUNT_BALANCE']:,.0f}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Churn Risk", customer['CHURN_RISK_SCORE'], f"{customer['CHURN_PROBABILITY']:.0%}")
            
            with col3:
                if st.button(f"Select {customer['CUSTOMER_NAME']}", key=f"select_{customer['CUSTOMER_ID']}"):
                    st.session_state.selected_customer = customer['CUSTOMER_ID']
                    st.success(f"Selected {customer['CUSTOMER_NAME']} for demo")
            
            with col4:
                st.caption(customer['NEXT_BEST_ACTION'][:60] + "..." if len(customer['NEXT_BEST_ACTION']) > 60 else customer['NEXT_BEST_ACTION'])

# Selected Customer Summary
if st.session_state.selected_customer:
    selected_customer_data = customers_df[customers_df['CUSTOMER_ID'] == st.session_state.selected_customer]
    if not selected_customer_data.empty:
        customer = selected_customer_data.iloc[0]
        st.markdown("---")
        st.subheader(f"🎯 Selected Customer: {customer['CUSTOMER_NAME']}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Customer ID", customer['CUSTOMER_ID'])
        with col2:
            st.metric("Churn Risk", customer['CHURN_RISK_SCORE'], f"{customer['CHURN_PROBABILITY']:.0%}")
        with col3:
            st.metric("Age", f"{customer['AGE']} years")
        with col4:
            st.metric("Balance", f"${customer['ACCOUNT_BALANCE']:,.0f}")
        
        st.info(f"**Next Best Action**: {customer['NEXT_BEST_ACTION']}")



# Quick Stats Dashboard
if "✅" in st.session_state.connection_status:
    st.markdown("---")
    st.header("📊 Quick Stats")
    
    @st.cache_data(ttl=300)
    def load_quick_stats():
        """Load quick statistics for the demo"""
        try:
            conn = get_snowflake_connection()
            if hasattr(conn, 'sql'):  # Snowpark session
                stats = conn.sql("""
                    SELECT 
                        COUNT(*) as total_customers,
                        SUM(CASE WHEN CHURN_RISK_SCORE = 'High' THEN 1 ELSE 0 END) as high_risk_customers,
                        AVG(CHURN_PROBABILITY) as avg_churn_probability,
                        COUNT(DISTINCT CALL_ID) as total_calls
                    FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER_360_VIEW c
                    LEFT JOIN SUPERANNUATION.TRANSCRIPTS.ENRICHED_TRANSCRIPTS_ALL e ON c.CUSTOMER_ID = e.CUSTOMER_ID
                """).to_pandas()
                # Convert column names to lowercase (Snowflake returns uppercase)
                stats.columns = stats.columns.str.lower()
            else:
                stats = pd.read_sql("""
                    SELECT 
                        COUNT(*) as total_customers,
                        SUM(CASE WHEN CHURN_RISK_SCORE = 'High' THEN 1 ELSE 0 END) as high_risk_customers,
                        AVG(CHURN_PROBABILITY) as avg_churn_probability,
                        COUNT(DISTINCT CALL_ID) as total_calls
                    FROM SUPERANNUATION.TRANSCRIPTS.CUSTOMER_360_VIEW c
                    LEFT JOIN SUPERANNUATION.TRANSCRIPTS.ENRICHED_TRANSCRIPTS_ALL e ON c.CUSTOMER_ID = e.CUSTOMER_ID
                """, conn)
            
            # Convert column names to lowercase (Snowflake returns uppercase)
            stats.columns = stats.columns.str.lower()
            return stats.iloc[0] if not stats.empty else None
        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
            return None

    stats = load_quick_stats()
    if stats is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Customers", f"{int(stats['total_customers'])}")
        with col2:
            st.metric("High Risk Customers", f"{int(stats['high_risk_customers'])}")
        with col3:
            st.metric("Avg Churn Probability", f"{stats['avg_churn_probability']:.1%}")
        with col4:
            st.metric("Call Transcripts", f"{int(stats['total_calls']) if stats['total_calls'] else 0}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p><strong>Powered by Snowflake AI + ML Platform</strong></p>
    <p>Real-time AI processing • Enterprise ML models • Unified data platform</p>
</div>
""", unsafe_allow_html=True)

 