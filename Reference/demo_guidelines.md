# Demo Guidelines for Superannuation Transcripts Demo

## Demo Objective
Showcase how a superannuation company can leverage customer call transcripts with Snowflake's AI capabilities to:
1. Predict customer churn risk using ML models
2. Generate personalized Next Best Actions using AI
3. Improve member retention and satisfaction

## Target Audience
- Superannuation Fund executives
- Customer service managers  
- Data and analytics teams
- IT decision makers
- Data scientists and technical architects

## Demo Platform: Streamlit Multi-Page Application

### Application Structure (6 Pages)
1. **🏠 Home** - Demo introduction and scenario selection
2. **📊 Data Foundation** - Raw transcripts, customer data, scale demonstration  
3. **🤖 AI Processing Demo** - ⭐ Interactive real-time AI/ML processing (KEY PAGE)
4. **👨‍💼 Advisor View** - Customer 360 view and action interface
5. **📈 Manager Dashboard** - Aggregated insights and business trends
6. **🔬 ML Model Performance** - Technical deep dive for data scientists

### Navigation Pattern
- **Free Navigation**: Audience can jump between any pages using sidebar
- **Suggested Flow**: Follow numbered sequence for complete story
- **Demo Flexibility**: Can focus on specific pages based on audience interests

## Demo Flow Structure (Updated for Streamlit)

### 1. Opening & App Introduction (2-3 minutes)
**Page**: 🏠 Home
**Setup**: "This demo shows how Snowflake can transform your existing call transcripts into actionable insights using our integrated AI/ML platform"

**Key Points**:
- Millions of customer calls generate valuable unstructured data
- Traditional analysis is manual and reactive  
- Snowflake's hybrid AI+ML approach makes this proactive and scalable
- Live demonstration using real Snowflake AI and ML capabilities

**Demo Actions**:
- Show application overview and navigation
- Introduce demo customer scenarios available
- Select primary demo customer (Maria Garcia - CUST003) for main storyline

### 2. Data Foundation (3-4 minutes)  
**Page**: 📊 Data Foundation
**Show**: Raw call transcripts and customer data in Snowflake

**Key Points**:
- Data already exists in your organization
- Snowflake can ingest and process at scale
- No data movement required - processing happens where data lives
- Show volume and variety of data available

**Demo Actions**:
- Navigate to raw transcripts table
- Show sample transcript data and customer profiles  
- Explain volume and structure (100+ calls, 15+ customers)
- Highlight data quality and completeness

### 3. AI Processing Demo (7-10 minutes) ⭐ **CENTERPIECE**
**Page**: 🤖 AI Processing Demo  
**Show**: Interactive transcript editing with real-time AI/ML processing

**Key Points**:
- Snowflake Cortex AI processes text natively
- ML models predict churn risk with high accuracy
- Results appear in seconds, not hours
- Completely flexible - can handle any customer language

**Demo Actions**:
#### **Option A: Push-Button Demo Scripts** (For colleague demos)
- Click "Load Demo Scenario: Risk Escalation"  
- Show original transcript and analysis
- Click "Transform to High Risk" button
- Watch real-time processing pipeline
- Display dramatic before/after comparison

#### **Option B: Interactive Live Editing** (For engaged audiences)
- Load Maria Garcia's original call: "I'm having login issues but generally satisfied..."
- Edit transcript to: "I'm completely frustrated with these login issues and considering moving my super elsewhere unless this gets fixed immediately!"
- Click "PROCESS TRANSCRIPT WITH AI/ML" 
- Watch live processing pipeline:
  1. 🤖 AI Sentiment Analysis → Changes from +0.1 to -0.8
  2. 🎯 AI Intent Detection → Changes from "Tech Support" to "Churn Risk"  
  3. 📈 ML Churn Prediction → Jumps from 25% to 78%
  4. 💡 AI NBA Generation → Changes from "Standard follow-up" to "URGENT: Senior advisor intervention"
- Show before/after comparison table

**Alternative Scenarios Available**:
- Fee Complaint Scenario (John Smith → Fee sensitivity)
- Upsell Discovery (Transform neutral inquiry to investment interest)
- Custom text processing (Type any customer interaction)

### 4. Advisor View (4-5 minutes)
**Page**: 👨‍💼 Advisor View
**Show**: Front-line advisor interface with actionable insights

**Key Points**:
- Turns agents into proactive advisors
- All ML and AI insights in one place
- Personalized recommendations with reasoning
- Reduces customer churn through early intervention

**Demo Actions**:
- Look up Maria Garcia (CUST003) 
- Show customer 360 view with ML churn probability (78%)
- Display AI-generated sentiment trends and call history
- Review Next Best Action with AI reasoning
- Show call transcript details and emotional state tracking
- Demonstrate how advisor can take immediate action

### 5. Manager Dashboard (3-4 minutes)
**Page**: 📈 Manager Dashboard
**Show**: Management oversight and strategic insights

**Key Points**:
- Strategic view of customer health across portfolio
- Data-driven decision making with ML predictions
- Measure effectiveness of AI-powered interventions  
- Identify trends and patterns across customer base

**Demo Actions**:
- Show churn risk distribution (High/Medium/Low customers)
- Display sentiment trends over time
- Review most common intents and issues
- Show NBA effectiveness metrics
- Demonstrate drill-down capabilities by investment option, age groups

### 6. ML Model Performance (3-4 minutes) **NEW**
**Page**: 🔬 ML Model Performance  
**Show**: Technical sophistication for data science stakeholders

**Key Points**:
- Real ML models with measurable accuracy (87.3%)
- Feature engineering combining structured + AI insights
- Model explainability and confidence scoring
- Continuous improvement through feedback loops

**Demo Actions**:
- Show model accuracy and performance metrics
- Display feature importance (negative sentiment calls, AI churn intent, etc.)
- Review A/B testing results: Hybrid AI+ML vs Rules-based
- Demonstrate model confidence scores and prediction quality
- Show business impact: $2.3M churn prevented vs $1.1M with rules

## Demo Scenarios (Enhanced for Interactive Use)

### Scenario 1: High Churn Risk Customer (Primary)
**Customer**: Maria Garcia (CUST003)  
**Original Profile**: Frustrated with login issues, moderate sentiment
**Interactive Demo**: Edit transcript to add stronger churn language
**Expected Results**: 
- Sentiment: +0.1 → -0.8
- Intent: "Tech Support" → "Churn Risk"  
- Churn Probability: 25% → 78%
- NBA: "Standard follow-up" → "URGENT: Senior advisor intervention"

### Scenario 2: Fee Sensitivity Discovery  
**Customer**: John Smith (CUST004)
**Demo**: Transform investment inquiry to fee complaint
**Expected Results**: NBA changes from "ESG consultation" to "Fee review session"

### Scenario 3: Upsell Opportunity
**Customer**: Emily White (CUST005)  
**Demo**: Add sustainable investing interest to retirement inquiry
**Expected Results**: NBA includes ESG investment options

## Technical Demo Tips

### Before the Demo
- [ ] Test Streamlit app locally and verify all pages load
- [ ] Verify AI processing functions work in real-time
- [ ] Test push-button demo scenarios for reliability  
- [ ] Prepare custom text examples for interactive editing
- [ ] Ensure database connection is stable

### During the Demo  
- [ ] Start with Home page overview and navigation explanation
- [ ] Use push-button scenarios for predictable results
- [ ] Save interactive editing for engaged technical audiences
- [ ] Navigate freely between pages based on audience interest
- [ ] Focus on AI Processing Demo as the centerpiece
- [ ] End with ML Performance page for technical credibility

### Demo Recovery Strategies
- If AI processing fails: Refresh page and try different customer
- If connection fails: Have screenshots of key results ready
- If audience wants deeper dive: Jump to ML Performance page
- If questions arise: Use Demo Guide page for quick reference

## Key Messages to Reinforce

### Business Value (All Pages)
- "Transform reactive support into proactive engagement"  
- "Reduce churn through early intervention powered by ML"
- "Personalize every customer interaction with AI insights"
- "Make data-driven decisions at enterprise scale"

### Technical Capabilities (AI Processing + ML Performance Pages)
- "Real AI and ML processing, not rules-based logic"
- "Processing happens where your data lives - no movement required"
- "Scale from thousands to millions of interactions instantly" 
- "Enterprise-grade ML with measurable business impact"

### Differentiation (Manager Dashboard + ML Performance)
- "Unlike point solutions, this is a unified AI+ML platform"
- "Process structured and unstructured data together"
- "Proven ML models with 87% accuracy and continuous improvement"
- "Complete transparency with model explainability"

## Questions to Anticipate

### Data & Privacy
**Q**: "How do you handle sensitive customer data?"
**A**: Navigate to Data Foundation page - "All processing happens within your Snowflake environment with enterprise-grade security"

### Integration  
**Q**: "How do we get our call data into Snowflake?"
**A**: "Snowflake has 100+ connectors and can ingest data from any source - voice systems, CRM, etc."

### AI/ML Accuracy
**Q**: "How accurate is the AI analysis and ML predictions?"  
**A**: Navigate to ML Performance page - "87.3% accuracy with continuous improvement, using advanced models like Claude-4-Sonnet"

### ROI & Business Impact
**Q**: "What's the return on investment?"
**A**: Show Manager Dashboard metrics - "Customers see 15-25% reduction in churn and $2.3M prevented vs $1.1M with traditional methods"

### Technical Implementation  
**Q**: "How complex is this to implement?"
**A**: "Built on Snowflake's native AI/ML capabilities - no external systems or complex integrations required"

## Success Metrics
- Audience engagement with interactive AI processing demo
- Technical questions about ML model performance and features
- Business questions about ROI and implementation timeline
- Interest in next steps/proof of concept
- Specific use case discussions for their organization

## Follow-up Actions  
- Schedule technical deep-dive session focused on ML implementation
- Provide data assessment questionnaire for their call transcript data
- Connect with customer success team for POC scoping
- Arrange proof of concept discussion with their data science team
- Share Streamlit application access for internal evaluation 