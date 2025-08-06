import streamlit as st
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set page config
st.set_page_config(
    page_title="Demo Guide",
    page_icon="❓",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
.medium-font {
    font-size:16px !important;
    font-weight: bold;
}
.highlight-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
}
.info-box {
    background-color: #e8f4fd;
    border: 1px solid #bee5eb;
    color: #0c5460;
}
.primary-box {
    background-color: #cce5ff;
    border: 1px solid #b3d9ff;
    color: #004085;
}
</style>
""", unsafe_allow_html=True)

# Page header
st.title("❓ Demo Guide")
st.markdown("### Presenter Instructions & Best Practices")

# Demo overview
st.markdown("""
<div class="highlight-box primary-box">
<h3>🎯 Demo Objective</h3>
<p>Showcase Snowflake's hybrid AI+ML capabilities for superannuation customer churn prediction and personalized engagement. This demo proves how Snowflake transforms reactive customer service into proactive, AI-powered retention strategies.</p>
<p><strong>Key Message:</strong> "Process customer interactions where your data lives, using enterprise AI+ML for real business impact."</p>
</div>
""", unsafe_allow_html=True)

# Target audiences
st.header("👥 Target Audiences")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🎯 Business Executives")
    st.markdown("**Focus Pages:**")
    st.markdown("- Manager Dashboard (ROI, metrics)")
    st.markdown("- AI Processing Demo (business value)")
    st.markdown("- Advisor View (operational impact)")
    st.markdown("**Key Points:**")
    st.markdown("- 15-25% churn reduction")
    st.markdown("- $2.3M revenue protection")
    st.markdown("- 87% prediction accuracy")

with col2:
    st.subheader("🔧 Technical Teams")
    st.markdown("**Focus Pages:**")
    st.markdown("- ML Model Performance (deep dive)")
    st.markdown("- AI Processing Demo (technical proof)")
    st.markdown("- Data Foundation (architecture)")
    st.markdown("**Key Points:**")
    st.markdown("- Real Snowflake ML models")
    st.markdown("- Native AI function integration")
    st.markdown("- Enterprise-grade performance")

with col3:
    st.subheader("👨‍💼 Operational Teams")
    st.markdown("**Focus Pages:**")
    st.markdown("- Advisor View (daily workflow)")
    st.markdown("- AI Processing Demo (practical use)")
    st.markdown("- Manager Dashboard (oversight)")
    st.markdown("**Key Points:**")
    st.markdown("- Real-time customer insights")
    st.markdown("- Actionable recommendations")
    st.markdown("- Intuitive user interface")

# Demo scenarios
st.markdown("---")
st.header("🎭 Key Demo Scenarios")

st.markdown("""
<div class="highlight-box info-box">
<h4>🎯 Top 3 Demo Calls (Always at top of dropdown)</h4>
<p>These calls are specifically designed for compelling demo scenarios:</p>
</div>
""", unsafe_allow_html=True)

# Red scenario
st.markdown("#### 🔴 CALL003 - Maria Garcia (High Churn Risk)")
st.markdown("- **Scenario:** Annual statement issue + login problems")
st.markdown("- **Key phrases:** 'I'm a bit frustrated', 'having trouble logging in'")
st.markdown("- **Demo value:** Perfect for showing churn risk escalation (83% probability)")
st.markdown("- **NBA:** Urgent senior advisor call to address technical and service concerns")

# Yellow scenario
st.markdown("#### 🟡 CALL005 - Lisa Thompson (Medium Risk - Upsell Opportunity)")
st.markdown("- **Scenario:** Retirement planning inquiry")
st.markdown("- **Key phrases:** 'thinking of retiring soon', 'what are my options'")
st.markdown("- **Demo value:** Great for showing positive engagement and upsell opportunities")
st.markdown("- **NBA:** Schedule complimentary retirement planning consultation")

# Green scenario
st.markdown("#### 🟢 CALL004 - John Smith (Low Risk - Positive Engagement)")
st.markdown("- **Scenario:** ESG investment interest")
st.markdown("- **Key phrases:** 'sustainable investing', 'ESG-focused fund'")
st.markdown("- **Demo value:** Excellent for showing positive customer engagement")
st.markdown("- **NBA:** Offer personalized ESG investment portfolio consultation")

# Demo flow guide
st.markdown("---")
st.header("🎬 Recommended Demo Flow")

# Flow step 1
st.markdown("### 📊 Step 1: Data Foundation (3-4 minutes)")
st.markdown("**Purpose:** Establish data credibility and scale")
st.markdown("**Key Actions:**")
st.markdown("- Show raw transcript volume and quality (97.5% accuracy)")
st.markdown("- Highlight customer data completeness (99.8%)")
st.markdown("- Emphasize real-time data pipeline capability")
st.markdown("- Point out AI/ML readiness of data structure")

st.success("**Key Message:** 'Your existing data is already AI-ready in Snowflake'")

st.info("**📊 Data Foundation Summary:** We have a robust data foundation with high-quality customer and interaction data ready for AI/ML processing. Our voice-to-text pipeline provides near real-time transcript availability with 97.5% accuracy, while customer data completeness exceeds 99.8%.")

# Flow step 2
st.markdown("### 🤖 Step 2: AI Processing Demo ⭐ (7-10 minutes) **CENTERPIECE**")
st.markdown("**Purpose:** Prove real AI/ML capabilities with interactive demonstration")

st.warning("**⚡ Quick Start:** Select 'CALL003 - Maria Garcia' → Click '🔄 Load Call Transcript' → Click 'PROCESS TRANSCRIPT WITH AI/ML' → Watch the magic happen!")

st.markdown("#### 🎯 Recommended Demo Calls (Top of dropdown list):")
st.markdown("- **CALL003 - Maria Garcia (High Risk 🔴):** Annual statement issue, login problems - perfect for churn risk escalation")
st.markdown("- **CALL005 - Lisa Thompson (Medium Risk 🟡):** Retirement planning inquiry - great for upsell opportunity")
st.markdown("- **CALL004 - John Smith (Low Risk 🟢):** ESG investment interest - excellent for positive engagement")

st.markdown("#### Option A: Push-Button Demo (Recommended for groups)")
st.markdown("1. Select 'CALL003 - Maria Garcia' (shows frustrated customer)")
st.markdown("2. Click '🔄 Load Call Transcript'")
st.markdown("3. Show original transcript (login issues, frustration)")
st.markdown("4. Click 'PROCESS TRANSCRIPT WITH AI/ML'")
st.markdown("5. Watch real-time AI+ML processing pipeline")
st.markdown("6. Highlight: High churn risk (83%) + urgent NBA recommendation")

st.markdown("#### Option B: Live Editing (For engaged technical audiences)")
st.markdown("1. Select 'CALL003 - Maria Garcia' and load transcript")
st.markdown("2. Edit: Add 'I'm considering moving my super elsewhere' at the end")
st.markdown("3. Click 'PROCESS TRANSCRIPT WITH AI/ML'")
st.markdown("4. Show live processing: Sentiment → Intent → ML Prediction → NBA")
st.markdown("5. Highlight dramatic churn probability increase and urgent NBA")

st.success("**Key Message:** 'Watch Snowflake AI+ML process any customer language in real-time'")

# Flow step 3
st.markdown("### 👨‍💼 Step 3: Advisor View (4-5 minutes)")
st.markdown("**Purpose:** Show practical daily workflow for front-line staff")
st.markdown("**Key Actions:**")
st.markdown("- Look up Maria Garcia (CUST003) from Step 2 processing")
st.markdown("- Show customer 360 view with ML churn probability (83%)")
st.markdown("- Review AI-generated Next Best Action with reasoning")
st.markdown("- Demonstrate quick action buttons (escalate, call, email)")
st.markdown("- Show call history with sentiment trends")
st.markdown("- Compare with John Smith (CUST004) - positive ESG engagement opportunity")

st.success("**Key Message:** 'Transform agents into proactive advisors with AI insights'")

# Flow step 4
st.markdown("### 📈 Step 4: Manager Dashboard (3-4 minutes)")
st.markdown("**Purpose:** Demonstrate strategic oversight and business impact")
st.markdown("**Key Actions:**")
st.markdown("- Review executive KPIs (total customers, high-risk count, AUM)")
st.markdown("- Show churn risk distribution and trends")
st.markdown("- Highlight business impact: $2.3M revenue protection")
st.markdown("- Compare AI+ML vs traditional approaches (87% vs 63% accuracy)")
st.markdown("- Point out real-time alerts and monitoring")

st.success("**Key Message:** 'Data-driven decisions with measurable business impact'")

# Flow step 5
st.markdown("### 🔬 Step 5: ML Model Performance (3-4 minutes) **TECHNICAL**")
st.markdown("**Purpose:** Showcase technical sophistication for data science stakeholders")
st.markdown("**Key Actions:**")
st.markdown("- Show model accuracy metrics (87.3% accuracy, 0.89 AUC-ROC)")
st.markdown("- Review feature importance (AI features dominate top rankings)")
st.markdown("- Compare hybrid AI+ML vs traditional approaches")
st.markdown("- Demonstrate model monitoring and drift detection")
st.markdown("- Show actual Snowflake ML code examples")

st.success("**Key Message:** 'Enterprise-grade AI+ML with full explainability and monitoring'")

# Demo scenarios
st.markdown("---")
st.header("🎭 Pre-Built Demo Scenarios")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔴 Scenario 1: Risk Escalation")
    st.markdown("**Customer:** Maria Garcia (CUST003)")
    st.markdown("**Original:** Minor login issues, generally satisfied")
    st.markdown("**Transform:** Frustrated, considering leaving")
    st.markdown("**Results:**")
    st.markdown("- Sentiment: +0.1 → -0.8")
    st.markdown("- Churn Risk: 25% → 78%")
    st.markdown("- NBA: Standard → URGENT intervention")
    st.markdown("**Use For:** Proving AI sensitivity to language")

with col2:
    st.markdown("#### 🟡 Scenario 2: Fee Sensitivity")
    st.markdown("**Customer:** John Smith (CUST004)")
    st.markdown("**Original:** Account balance inquiry")
    st.markdown("**Transform:** Fees outrageous, switching providers")
    st.markdown("**Results:**")
    st.markdown("- Intent: Account Query → Fee Complaint")
    st.markdown("- Risk: Low → Medium")
    st.markdown("- NBA: Standard → Fee review session")
    st.markdown("**Use For:** Hidden complaint discovery")

with col3:
    st.markdown("#### 🟢 Scenario 3: Upsell Discovery")
    st.markdown("**Customer:** Emily White (CUST005)")
    st.markdown("**Original:** Basic retirement inquiry")
    st.markdown("**Transform:** Interested in ESG investing")
    st.markdown("**Results:**")
    st.markdown("- Intent: Retirement → Investment Opportunity")
    st.markdown("- NBA: Standard → ESG consultation")
    st.markdown("- Risk: Medium → Low")
    st.markdown("**Use For:** Revenue growth opportunities")

# Best practices
st.markdown("---")
st.header("💡 Demo Best Practices")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Do's")
    st.markdown("- **Start with AI Processing Demo** - It's the most compelling")
    st.markdown("- **Use push-button scenarios** for predictable results")
    st.markdown("- **Show real-time processing** - Don't just show static results")
    st.markdown("- **Emphasize business value** - Revenue protection, churn reduction")
    st.markdown("- **Highlight ML sophistication** - 87% accuracy, feature engineering")
    st.markdown("- **Demo interactively** - Let audience ask questions")
    st.markdown("- **Navigate freely** - Jump to relevant pages for questions")
    st.markdown("- **Test beforehand** - Verify all connections and processing")

with col2:
    st.subheader("❌ Don'ts")
    st.markdown("- **Don't rush AI Processing** - It's the key differentiator")
    st.markdown("- **Don't skip the before/after** - Shows dramatic AI impact")
    st.markdown("- **Don't get stuck on one page** - Use free navigation")
    st.markdown("- **Don't ignore technical questions** - Jump to ML Performance page")
    st.markdown("- **Don't promise exact features** - This is a demo, not production")
    st.markdown("- **Don't oversell** - Let the results speak for themselves")
    st.markdown("- **Don't skip connection testing** - Always verify before demo")

# Handling questions
st.markdown("---")
st.header("🤔 Handling Common Questions")

st.subheader("Technical Questions")
with st.expander("Q: How accurate is the AI analysis?"):
    st.markdown("""
    **Answer:** Navigate to ML Model Performance page and show:
    - 87.3% model accuracy with 0.89 AUC-ROC score
    - Real Snowflake ML models, not rules-based logic
    - Continuous monitoring and drift detection
    - Feature importance rankings show AI features dominate
    """)

with st.expander("Q: How do you handle data privacy and security?"):
    st.markdown("""
    **Answer:** Point to Data Foundation page:
    - All processing happens within your Snowflake environment
    - No data movement required - AI functions are native
    - Enterprise-grade security and compliance built-in
    - Customer data never leaves your controlled environment
    """)

with st.expander("Q: How fast can this process new transcripts?"):
    st.markdown("""
    **Answer:** Demonstrate in AI Processing Demo:
    - Real-time processing in under 3 seconds
    - Native Snowflake functions, no external API calls
    - Scales automatically with Snowflake compute
    - Show live processing pipeline in action
    """)

st.subheader("Business Questions")
with st.expander("Q: What's the ROI on this investment?"):
    st.markdown("""
    **Answer:** Navigate to Manager Dashboard:
    - $2.3M potential revenue protection vs $1.1M with traditional methods
    - 15-25% churn reduction typically achieved
    - 87% accuracy vs 63% with rules-based approaches
    - 125x lower cost per prediction ($0.02 vs $2.50)
    """)

with st.expander("Q: How long does implementation take?"):
    st.markdown("""
    **Answer:** Emphasize Snowflake advantages:
    - Data already in Snowflake - no movement required
    - AI functions are native - no external integrations
    - ML models deploy serverlessly - no infrastructure setup
    - Typical POC in 2-4 weeks, production in 3-6 months
    """)

# Demo recovery strategies
st.markdown("---")
st.header("🛠️ Demo Recovery Strategies")

st.info("""
**If AI Processing Fails:**
- Refresh the page and try a different customer scenario
- Use the push-button scenarios instead of live editing
- Show the before/after comparison from previous successful run
- Explain: "AI processing temporarily unavailable, but here's what typically happens..."
""")

st.info("""
**If Connection Issues:**
- Have screenshots of key results ready as backup
- Switch focus to ML Model Performance page (less data-dependent)
- Use fallback data that's built into each page
- Emphasize the architecture and approach rather than live demo
""")

st.info("""
**If Questions Go Deep Technical:**
- Navigate immediately to ML Model Performance page
- Show actual Snowflake ML code examples
- Discuss feature engineering with AI-derived features
- Offer follow-up technical deep-dive session
""")

# Success metrics
st.markdown("---")
st.header("📈 Demo Success Metrics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("During Demo")
    st.markdown("- **Audience Engagement**: Questions and discussion")
    st.markdown("- **Technical Interest**: Requests to see ML Performance page")
    st.markdown("- **Business Interest**: ROI and timeline questions")
    st.markdown("- **Interactive Participation**: Suggesting transcript edits")
    st.markdown("- **Real-time Validation**: 'This actually works!' reactions")

with col2:
    st.subheader("After Demo")
    st.markdown("- **Next Steps Requested**: POC discussion, technical deep-dive")
    st.markdown("- **Specific Use Cases**: Customer-specific scenario discussions")
    st.markdown("- **Team Expansion**: Requests to include more stakeholders")
    st.markdown("- **Timeline Acceleration**: Urgency for implementation")
    st.markdown("- **Reference Requests**: Customer case studies and validation")

# Call to action
st.markdown("---")
st.success("""
**🎯 Demo Summary**: You now have a comprehensive, interactive demo showcasing Snowflake's hybrid AI+ML 
capabilities. Focus on the AI Processing Demo as your centerpiece, use push-button scenarios for reliability, 
and navigate freely based on audience interests. Remember: let the technology speak for itself - the results 
are compelling enough without overselling.
""")

st.info("**📞 Next Steps**: Schedule technical deep-dive sessions, discuss POC parameters, and connect prospects with customer success teams for implementation planning.")

# Add the new AI/ML capabilities section
st.markdown("---")
st.header("🤖 Snowflake AI/ML Capabilities Used in Demo")

st.markdown("""
This demo showcases multiple Snowflake AI and ML capabilities working together to transform customer service 
transcripts into actionable business insights. Here's what each capability does and how we use it:
""")

# Snowflake Cortex AI SQL Functions
st.subheader("🧠 Snowflake Cortex AI SQL Functions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 SNOWFLAKE.CORTEX.SENTIMENT()")
    st.markdown("**What it does:** Analyzes text to determine emotional sentiment with scores from -1 (very negative) to +1 (very positive).")
    st.markdown("**How we use it:** We process every call transcript to immediately understand customer emotional state. This drives churn risk calculations and helps prioritize which customers need urgent attention.")
    st.markdown("**Business Impact:** Enables proactive intervention when customers show negative sentiment patterns across multiple calls.")

    st.markdown("#### 🎯 AI_CLASSIFY()")
    st.markdown("**What it does:** Categorizes text into predefined classes using advanced language models, handling complex business-specific classifications.")
    st.markdown("**How we use it:** We classify call intents (complaint, investment inquiry, churn risk), emotional states (frustrated, satisfied, concerned), and business outcomes (upsell opportunity, retention risk). This replaces manual categorization with 90%+ accuracy.")
    st.markdown("**Business Impact:** Automatically routes customers to appropriate advisors and identifies revenue opportunities in real-time.")

with col2:
    st.markdown("#### 📝 SNOWFLAKE.CORTEX.SUMMARIZE()")
    st.markdown("**What it does:** Generates concise summaries of long text documents, extracting key information and themes.")
    st.markdown("**How we use it:** We create brief, actionable summaries of lengthy customer calls, highlighting the main issues, requests, and outcomes. This saves advisors time when reviewing customer history.")
    st.markdown("**Business Impact:** Reduces call preparation time by 70% and ensures consistent understanding of customer interactions across team members.")

    st.markdown("#### 🧪 SNOWFLAKE.CORTEX.COMPLETE()")
    st.markdown("**What it does:** Uses advanced LLMs (like Claude-3.5-Sonnet) to generate contextual responses, analysis, and recommendations based on prompts.")
    st.markdown("**How we use it:** We generate personalized Next Best Action recommendations, detailed JSON analysis of customer situations, and specific retention strategies. The AI considers customer history, sentiment, and business context to create tailored advice.")
    st.markdown("**Business Impact:** Provides advisors with specific, actionable recommendations that have increased customer retention by 25% in pilot programs.")

# AI_AGG function
st.markdown("#### 🔍 AI_AGG()")
st.markdown("**What it does:** Aggregates insights across multiple text records using AI, identifying patterns and themes that span many customer interactions.")
st.markdown("**How we use it:** We analyze all of a customer's call transcripts together to identify recurring pain points, escalating concerns, and relationship health trends. This provides a complete customer story rather than isolated interaction analysis.")
st.markdown("**Business Impact:** Reveals hidden churn signals and relationship issues that wouldn't be visible in individual call analysis, enabling more effective retention strategies.")

# Snowflake ML Functions
st.subheader("🔬 Snowflake ML Functions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🤖 SNOWFLAKE.ML.CLASSIFICATION")
    st.markdown("**What it does:** Trains and deploys machine learning models directly in Snowflake using gradient boosting and other algorithms for classification tasks.")
    st.markdown("**How we use it:** We build churn prediction models that combine traditional customer features (age, tenure, balance) with AI-derived features (sentiment scores, intent patterns, emotional state classifications). The model predicts churn probability with 87.3% accuracy.")
    st.markdown("**Business Impact:** Enables data-driven prioritization of retention efforts and resource allocation, with each prediction costing only $0.02 vs $2.50 for manual analysis.")

with col2:
    st.markdown("#### ⚡ Real-time Model Inference")
    st.markdown("**What it does:** Deploys trained ML models as functions that can be called directly in SQL queries for instant predictions on new data.")
    st.markdown("**How we use it:** Every new call transcript is immediately scored for churn risk using our trained models. The system generates predictions within seconds of call completion, enabling real-time advisor alerts and intervention workflows.")
    st.markdown("**Business Impact:** Reduces response time from days to minutes, allowing immediate action on high-risk customers while relationships can still be saved.")

# Hybrid AI+ML Approach
st.subheader("🔄 Hybrid AI+ML Integration")

st.success("""
**🎯 The Power of Hybrid Processing**

**What makes this unique:** We combine structured ML models with unstructured AI analysis to get the best of both worlds.

**ML Component:** Quantitative churn prediction using engineered features, providing precise probability scores and confidence intervals.

**AI Component:** Qualitative insight generation using language models, providing context, reasoning, and personalized recommendations.

**Integration:** ML predictions inform AI prompts for contextual NBA generation, while AI insights become features for ML model training.

**Business Result:** 87.3% prediction accuracy with explainable, actionable recommendations that advisors can immediately act upon.
""")

# Performance and Scale
st.subheader("📈 Performance & Enterprise Scale")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🚀 Processing Speed:**")
    st.markdown("- Sentiment analysis: <1 second per transcript")
    st.markdown("- Intent classification: <2 seconds per transcript")
    st.markdown("- NBA generation: <3 seconds per customer")
    st.markdown("- ML churn prediction: <0.5 seconds per customer")
    st.markdown("- Complete pipeline: <10 seconds end-to-end")

with col2:
    st.markdown("**📊 Enterprise Capabilities:**")
    st.markdown("- Processes millions of transcripts daily")
    st.markdown("- Auto-scales with Snowflake compute")
    st.markdown("- No external API dependencies")
    st.markdown("- Enterprise security and compliance")
    st.markdown("- Real-time monitoring and alerting")

# Final call to action
st.markdown("---")
st.success("""
**🎯 Key Takeaway**: This demo showcases how Snowflake's native AI+ML capabilities work together seamlessly 
to transform raw customer data into actionable business insights. Every function processes data where it lives, 
with no data movement, no external integrations, and enterprise-grade security. The result is a complete 
customer intelligence platform that drives measurable business outcomes.
""")

st.info("**💡 For Technical Audiences**: All these capabilities are available through standard SQL, making them accessible to your existing analytics teams without requiring specialized AI/ML expertise.")

 