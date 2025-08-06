-- ============================================================================
-- Superannuation Transcripts Demo - Customer Data Creation
-- ============================================================================
-- This script creates synthetic customer data that maps to the call transcripts
-- Run this after loading the call transcript data
-- ============================================================================

-- Set context
USE DATABASE SUPERANNUATION;
USE SCHEMA TRANSCRIPTS;
USE WAREHOUSE MYWH;

-- Clear any existing customer data (for fresh demo runs)
DELETE FROM CUSTOMER;

-- ============================================================================
-- Create Synthetic Customer Data for All 69 Customers
-- ============================================================================
-- The demo focuses on the first 5 customers but includes all 69 for completeness

-- ============================================================================
-- DEMO FOCUSED CUSTOMERS (Primary scenarios)
-- ============================================================================

INSERT INTO CUSTOMER (
    CUSTOMER_ID,
    CUSTOMER_NAME,
    AGE,
    TENURE_YEARS,
    ACCOUNT_BALANCE,
    INVESTMENT_OPTION,
    RECENT_TRANSACTIONS,
    LAST_INTERACTION_DATE,
    PRODUCT_HOLDINGS,
    CONTACT_PREFERENCE,
    CALL_FREQUENCY_LAST_MONTH,
    AVG_SENTIMENT_LAST_3_CALLS,
    NUM_NEGATIVE_CALLS_LAST_6_MONTHS,
    HAS_CHURN_INTENT_LAST_MONTH,
    CHURN_RISK_SCORE,
    CHURN_PROBABILITY,
    NEXT_BEST_ACTION
) VALUES

-- Demo Scenario 1: High Churn Risk Customers
('CUST001', 'Sarah Chen', 34, 5, 125000.00, 'Growth Plus', 2, '2025-07-10', 
 PARSE_JSON('["SuperChoice Growth", "Insurance Plus"]'), 'Email', 3, -0.2, 1, FALSE, 'Medium', 0.25, 
 'Follow up on recent account inquiries and market concerns'),

('CUST003', 'Maria Garcia', 42, 8, 89000.00, 'Balanced Growth', 1, '2025-07-10', 
 PARSE_JSON('["Balanced Fund", "Life Insurance"]'), 'Phone', 4, -0.7, 3, TRUE, 'High', 0.75, 
 'URGENT: Schedule senior advisor call to address technical and service concerns'),

-- Demo Scenario 2: Upsell Opportunities (Happy customers)
('CUST002', 'David Lee', 29, 3, 55000.00, 'Balanced Growth', 1, '2025-07-10', 
 PARSE_JSON('["Balanced Fund", "Online Access"]'), 'Email', 2, 0.4, 0, FALSE, 'Low', 0.12, 
 'Offer consolidation services and educational resources'),

('CUST004', 'John Smith', 45, 7, 180000.00, 'Balanced Growth', 4, '2025-07-10', 
 PARSE_JSON('["Balanced Fund", "Online Access"]'), 'Email', 2, 0.6, 0, FALSE, 'Low', 0.15, 
 'Offer personalized ESG investment portfolio consultation'),

-- Demo Scenario 3: Retirement Planning (Neutral sentiment, planning focused)
('CUST005', 'Emily White', 64, 25, 780000.00, 'Conservative', 1, '2025-07-10', 
 PARSE_JSON('["Conservative Fund", "Pension Account", "Insurance Bundle", "Transition to Retirement"]'), 'Phone', 2, 0.4, 0, FALSE, 'Low', 0.08, 
 'Schedule complimentary retirement planning session and pension options review'),

-- ============================================================================
-- ADDITIONAL CUSTOMERS (Background data for comprehensive demo)
-- ============================================================================

-- Mixed risk profiles to support various demo scenarios
('CUST006', 'Michael Brown', 38, 6, 95000.00, 'Growth Plus', 1, '2025-07-09', 
 PARSE_JSON('["Growth Fund", "Direct Debit"]'), 'Email', 1, 0.1, 0, FALSE, 'Low', 0.18, 
 'Provide investment education and fee transparency'),

('CUST007', 'Emma Thompson', 52, 15, 320000.00, 'Growth Plus', 2, '2025-07-09', 
 PARSE_JSON('["Growth Fund", "Pension Account", "Premium Services"]'), 'Phone', 1, 0.4, 0, FALSE, 'Low', 0.10, 
 'Introduce additional investment options and premium advisory services'),

('CUST008', 'Peter Johnson', 59, 20, 650000.00, 'Balanced Growth', 2, '2025-07-09', 
 PARSE_JSON('["Balanced Fund", "Pre-Retirement", "Insurance"]'), 'Phone', 1, 0.2, 0, FALSE, 'Low', 0.12, 
 'Provide pre-retirement planning consultation and transition strategies'),

('CUST009', 'Lisa Martinez', 36, 11, 210000.00, 'Balanced Growth', 2, '2025-07-07', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Online Trading"]'), 'Email', 2, 0.3, 0, FALSE, 'Low', 0.18, 
 'Offer advanced investment tools and premium account features'),

('CUST010', 'Robert Wilson', 55, 12, 245000.00, 'Conservative', 0, '2025-07-09', 
 PARSE_JSON('["Conservative Fund", "Pension Account", "Insurance Bundle"]'), 'Email', 5, -0.4, 2, TRUE, 'High', 0.60, 
 'Proactive outreach: Offer personalized account review and fee discussion'),

('CUST011', 'Jennifer Brown', 28, 4, 45000.00, 'Aggressive Growth', 3, '2025-07-08', 
 PARSE_JSON('["Aggressive Growth", "Mobile Access"]'), 'SMS', 3, 0.5, 0, FALSE, 'Low', 0.14, 
 'Provide market education and volatility guidance'),

('CUST012', 'David Liu', 41, 9, 195000.00, 'Sustainable Growth', 3, '2025-07-08', 
 PARSE_JSON('["ESG Fund", "Salary Sacrifice", "Insurance"]'), 'Email', 1, 0.5, 0, FALSE, 'Low', 0.12, 
 'Expand sustainable investment options and discuss additional ESG products'),

('CUST013', 'Amanda Clark', 33, 6, 78000.00, 'Balanced Growth', 2, '2025-07-07', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Mobile App"]'), 'Email', 2, -0.1, 1, FALSE, 'Medium', 0.32, 
 'Address service concerns and provide digital support training'),

('CUST014', 'Christopher Davis', 47, 13, 310000.00, 'Growth Plus', 1, '2025-07-06', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Premium Services"]'), 'Phone', 1, 0.3, 0, FALSE, 'Low', 0.16, 
 'Offer premium advisory services and portfolio optimization'),

('CUST015', 'Rachel Kim', 39, 8, 145000.00, 'Balanced Growth', 2, '2025-07-05', 
 PARSE_JSON('["Balanced Fund", "Salary Sacrifice", "Insurance"]'), 'Email', 3, -0.3, 2, FALSE, 'Medium', 0.35, 
 'Provide personalized investment strategy consultation'),

('CUST016', 'Michael O''Connor', 44, 10, 225000.00, 'Conservative', 1, '2025-07-04', 
 PARSE_JSON('["Conservative Fund", "Insurance", "Phone Support"]'), 'Phone', 2, 0.2, 0, FALSE, 'Low', 0.20, 
 'Offer investment diversification options'),

('CUST017', 'Sophie Anderson', 31, 5, 67000.00, 'Growth Plus', 3, '2025-07-03', 
 PARSE_JSON('["Growth Fund", "Online Access", "Mobile App"]'), 'SMS', 2, 0.4, 0, FALSE, 'Low', 0.15, 
 'Provide investment education and goal setting support'),

('CUST018', 'Thomas Wright', 53, 16, 455000.00, 'Balanced Growth', 1, '2025-07-02', 
 PARSE_JSON('["Balanced Fund", "Pension Account", "Insurance Bundle"]'), 'Email', 1, 0.1, 0, FALSE, 'Low', 0.13, 
 'Discuss pre-retirement planning and transition strategies'),

('CUST019', 'Michelle Taylor', 35, 7, 98000.00, 'Sustainable Growth', 2, '2025-07-01', 
 PARSE_JSON('["ESG Fund", "Salary Sacrifice", "Online Trading"]'), 'Email', 2, 0.6, 0, FALSE, 'Low', 0.11, 
 'Expand ESG investment options and impact reporting'),

('CUST020', 'James Robinson', 42, 11, 187000.00, 'Growth Plus', 2, '2025-06-30', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Premium Services"]'), 'Phone', 1, 0.2, 0, FALSE, 'Low', 0.17, 
 'Offer advanced investment strategies and tax optimization'),

('CUST021', 'Laura White', 27, 3, 35000.00, 'Aggressive Growth', 1, '2025-06-29', 
 PARSE_JSON('["Aggressive Growth", "Mobile Access", "Auto Invest"]'), 'SMS', 1, 0.5, 0, FALSE, 'Low', 0.12, 
 'Provide investment education and contribution increase options'),

('CUST022', 'Daniel Green', 49, 14, 340000.00, 'Conservative', 2, '2025-06-28', 
 PARSE_JSON('["Conservative Fund", "Insurance Bundle", "Premium Services"]'), 'Email', 2, -0.2, 1, FALSE, 'Medium', 0.28, 
 'Address investment performance concerns and provide market updates'),

('CUST023', 'Anna Johnson', 37, 9, 123000.00, 'Balanced Growth', 1, '2025-06-27', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Online Access"]'), 'Email', 1, 0.3, 0, FALSE, 'Low', 0.19, 
 'Offer investment review and portfolio rebalancing'),

('CUST024', 'Kevin Martinez', 32, 6, 71000.00, 'Growth Plus', 2, '2025-06-26', 
 PARSE_JSON('["Growth Fund", "Salary Sacrifice", "Mobile App"]'), 'Email', 2, 0.1, 0, FALSE, 'Low', 0.21, 
 'Provide market education and contribution optimization'),

('CUST025', 'Sarah Thompson', 45, 12, 267000.00, 'Balanced Growth', 1, '2025-06-25', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Online Trading"]'), 'Phone', 1, 0.4, 0, FALSE, 'Low', 0.14, 
 'Offer advanced investment tools and premium services'),

('CUST026', 'Mark Davis', 41, 8, 156000.00, 'Sustainable Growth', 3, '2025-06-24', 
 PARSE_JSON('["ESG Fund", "Insurance", "Impact Reporting"]'), 'Email', 3, -0.1, 1, FALSE, 'Medium', 0.31, 
 'Address ESG performance concerns and provide impact updates'),

('CUST027', 'Jessica Lee', 29, 4, 48000.00, 'Balanced Growth', 1, '2025-06-23', 
 PARSE_JSON('["Balanced Fund", "Mobile Access", "Auto Invest"]'), 'SMS', 1, 0.6, 0, FALSE, 'Low', 0.13, 
 'Provide investment education and goal setting support'),

('CUST028', 'Robert Kim', 52, 15, 398000.00, 'Conservative', 2, '2025-06-22', 
 PARSE_JSON('["Conservative Fund", "Pension Account", "Insurance Bundle"]'), 'Phone', 2, 0.1, 0, FALSE, 'Low', 0.16, 
 'Discuss retirement planning and income strategies'),

('CUST029', 'Nicole Brown', 34, 7, 89000.00, 'Growth Plus', 2, '2025-06-21', 
 PARSE_JSON('["Growth Fund", "Insurance", "Online Access"]'), 'Email', 2, 0.3, 0, FALSE, 'Low', 0.18, 
 'Offer investment review and diversification options'),

('CUST030', 'Andrew Wilson', 46, 13, 278000.00, 'Balanced Growth', 1, '2025-06-20', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Premium Services"]'), 'Email', 1, 0.2, 0, FALSE, 'Low', 0.15, 
 'Provide portfolio optimization and tax planning advice'),

('CUST031', 'Maria Rodriguez', 38, 9, 134000.00, 'Sustainable Growth', 2, '2025-06-19', 
 PARSE_JSON('["ESG Fund", "Salary Sacrifice", "Online Trading"]'), 'Email', 2, 0.5, 0, FALSE, 'Low', 0.12, 
 'Expand sustainable investment options and impact measurement'),

('CUST032', 'Steve Clark', 43, 10, 201000.00, 'Growth Plus', 3, '2025-06-18', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Mobile App"]'), 'Phone', 3, -0.2, 1, FALSE, 'Medium', 0.29, 
 'Address market volatility concerns and provide reassurance'),

('CUST033', 'Linda Anderson', 36, 8, 112000.00, 'Balanced Growth', 1, '2025-06-17', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Online Access"]'), 'Email', 1, 0.4, 0, FALSE, 'Low', 0.17, 
 'Offer investment education and contribution increase options'),

('CUST034', 'Paul Taylor', 50, 14, 356000.00, 'Conservative', 2, '2025-06-16', 
 PARSE_JSON('["Conservative Fund", "Pension Account", "Insurance Bundle"]'), 'Phone', 2, 0.1, 0, FALSE, 'Low', 0.14, 
 'Discuss pre-retirement planning and transition strategies'),

('CUST035', 'Karen White', 33, 6, 76000.00, 'Growth Plus', 2, '2025-06-15', 
 PARSE_JSON('["Growth Fund", "Salary Sacrifice", "Mobile App"]'), 'SMS', 2, 0.3, 0, FALSE, 'Low', 0.19, 
 'Provide investment education and portfolio review'),

('CUST036', 'Brian Martinez', 39, 9, 145000.00, 'Balanced Growth', 2, '2025-06-14', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Online Trading"]'), 'Email', 2, -0.1, 1, FALSE, 'Medium', 0.26, 
 'Address investment performance questions and provide market updates'),

('CUST037', 'Jennifer Davis', 44, 11, 223000.00, 'Sustainable Growth', 1, '2025-06-13', 
 PARSE_JSON('["ESG Fund", "Insurance", "Impact Reporting"]'), 'Email', 1, 0.6, 0, FALSE, 'Low', 0.11, 
 'Expand ESG investment options and sustainable impact measurement'),

('CUST038', 'Ryan Johnson', 31, 5, 62000.00, 'Aggressive Growth', 3, '2025-06-12', 
 PARSE_JSON('["Aggressive Growth", "Mobile Access", "Auto Invest"]'), 'SMS', 3, 0.2, 0, FALSE, 'Low', 0.22, 
 'Provide volatility education and risk management guidance'),

('CUST039', 'Susan Lee', 48, 12, 289000.00, 'Growth Plus', 1, '2025-06-11', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Premium Services"]'), 'Phone', 1, 0.3, 0, FALSE, 'Low', 0.16, 
 'Offer premium advisory services and portfolio optimization'),

('CUST040', 'David Thompson', 35, 7, 98000.00, 'Balanced Growth', 2, '2025-06-10', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Online Access"]'), 'Email', 2, 0.4, 0, FALSE, 'Low', 0.15, 
 'Provide investment review and diversification options'),

('CUST041', 'Michelle Kim', 42, 10, 187000.00, 'Conservative', 1, '2025-06-09', 
 PARSE_JSON('["Conservative Fund", "Insurance Bundle", "Phone Support"]'), 'Phone', 1, 0.1, 0, FALSE, 'Low', 0.18, 
 'Offer investment diversification and growth options'),

('CUST042', 'Christopher Brown', 37, 8, 123000.00, 'Growth Plus', 2, '2025-06-08', 
 PARSE_JSON('["Growth Fund", "Salary Sacrifice", "Mobile App"]'), 'Email', 2, 0.2, 0, FALSE, 'Low', 0.20, 
 'Provide market education and contribution optimization'),

('CUST043', 'Amanda Wilson', 51, 15, 378000.00, 'Balanced Growth', 1, '2025-06-07', 
 PARSE_JSON('["Balanced Fund", "Pension Account", "Insurance Bundle"]'), 'Email', 1, 0.5, 0, FALSE, 'Low', 0.13, 
 'Discuss retirement planning and income strategies'),

('CUST044', 'Robert Rodriguez', 28, 4, 43000.00, 'Sustainable Growth', 1, '2025-06-06', 
 PARSE_JSON('["ESG Fund", "Mobile Access", "Auto Invest"]'), 'SMS', 1, 0.7, 0, FALSE, 'Low', 0.10, 
 'Expand ESG investment options and impact education'),

('CUST046', 'Laura Clark', 40, 9, 156000.00, 'Growth Plus', 2, '2025-06-05', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Online Trading"]'), 'Email', 2, 0.1, 0, FALSE, 'Low', 0.21, 
 'Offer advanced investment strategies and portfolio review'),

('CUST047', 'Daniel Anderson', 45, 11, 234000.00, 'Balanced Growth', 3, '2025-06-04', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Premium Services"]'), 'Phone', 3, -0.3, 2, FALSE, 'Medium', 0.33, 
 'Address service concerns and provide premium support'),

('CUST048', 'Anna Taylor', 32, 6, 74000.00, 'Aggressive Growth', 2, '2025-06-03', 
 PARSE_JSON('["Aggressive Growth", "Salary Sacrifice", "Mobile App"]'), 'SMS', 2, 0.4, 0, FALSE, 'Low', 0.16, 
 'Provide investment education and risk management guidance'),

('CUST049', 'Kevin White', 49, 13, 301000.00, 'Conservative', 1, '2025-06-02', 
 PARSE_JSON('["Conservative Fund", "Insurance Bundle", "Premium Services"]'), 'Phone', 1, 0.2, 0, FALSE, 'Low', 0.17, 
 'Discuss pre-retirement planning and income strategies'),

('CUST050', 'Sarah Martinez', 36, 8, 109000.00, 'Balanced Growth', 2, '2025-06-01', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Online Access"]'), 'Email', 2, 0.3, 0, FALSE, 'Low', 0.19, 
 'Offer investment review and goal setting support'),

('CUST051', 'Mark Johnson', 41, 10, 178000.00, 'Growth Plus', 1, '2025-05-31', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Online Trading"]'), 'Email', 1, 0.5, 0, FALSE, 'Low', 0.14, 
 'Provide portfolio optimization and tax planning advice'),

('CUST052', 'Jessica Davis', 34, 7, 87000.00, 'Sustainable Growth', 2, '2025-05-30', 
 PARSE_JSON('["ESG Fund", "Salary Sacrifice", "Impact Reporting"]'), 'Email', 2, 0.6, 0, FALSE, 'Low', 0.12, 
 'Expand sustainable investment options and impact measurement'),

('CUST053', 'Robert Lee', 47, 12, 267000.00, 'Balanced Growth', 1, '2025-05-29', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Premium Services"]'), 'Phone', 1, 0.1, 0, FALSE, 'Low', 0.15, 
 'Offer premium advisory services and portfolio optimization'),

('CUST054', 'Nicole Thompson', 29, 5, 51000.00, 'Growth Plus', 3, '2025-05-28', 
 PARSE_JSON('["Growth Fund", "Mobile Access", "Auto Invest"]'), 'SMS', 3, 0.3, 0, FALSE, 'Low', 0.23, 
 'Provide investment education and contribution increase options'),

('CUST055', 'Andrew Kim', 52, 14, 345000.00, 'Conservative', 2, '2025-05-27', 
 PARSE_JSON('["Conservative Fund", "Pension Account", "Insurance Bundle"]'), 'Email', 2, 0.2, 0, FALSE, 'Low', 0.16, 
 'Discuss retirement planning and income strategies'),

('CUST056', 'Maria Brown', 38, 9, 132000.00, 'Balanced Growth', 1, '2025-05-26', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Online Access"]'), 'Email', 1, 0.4, 0, FALSE, 'Low', 0.18, 
 'Offer investment review and diversification options'),

('CUST057', 'Steve Wilson', 43, 11, 198000.00, 'Growth Plus', 2, '2025-05-25', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Mobile App"]'), 'Phone', 2, 0.1, 0, FALSE, 'Low', 0.20, 
 'Provide portfolio optimization and market education'),

('CUST058', 'Linda Rodriguez', 35, 8, 98000.00, 'Sustainable Growth', 2, '2025-05-24', 
 PARSE_JSON('["ESG Fund", "Salary Sacrifice", "Online Trading"]'), 'Email', 2, 0.5, 0, FALSE, 'Low', 0.13, 
 'Expand ESG investment options and impact reporting'),

('CUST059', 'Paul Clark', 46, 12, 256000.00, 'Balanced Growth', 1, '2025-05-23', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Premium Services"]'), 'Email', 1, 0.3, 0, FALSE, 'Low', 0.14, 
 'Offer premium advisory services and pre-retirement planning'),

('CUST060', 'Karen Anderson', 33, 6, 79000.00, 'Growth Plus', 2, '2025-05-22', 
 PARSE_JSON('["Growth Fund", "Insurance", "Mobile App"]'), 'SMS', 2, 0.4, 0, FALSE, 'Low', 0.17, 
 'Provide investment education and portfolio review'),

('CUST061', 'Brian Taylor', 39, 9, 147000.00, 'Balanced Growth', 3, '2025-05-21', 
 PARSE_JSON('["Balanced Fund", "Insurance Plus", "Online Access"]'), 'Email', 3, -0.2, 1, FALSE, 'Medium', 0.27, 
 'Address investment performance concerns and provide market updates'),

('CUST062', 'Jennifer White', 44, 11, 212000.00, 'Conservative', 1, '2025-05-20', 
 PARSE_JSON('["Conservative Fund", "Insurance Bundle", "Phone Support"]'), 'Phone', 1, 0.1, 0, FALSE, 'Low', 0.19, 
 'Offer investment diversification and growth options'),

('CUST063', 'Ryan Martinez', 31, 5, 58000.00, 'Aggressive Growth', 2, '2025-05-19', 
 PARSE_JSON('["Aggressive Growth", "Mobile Access", "Auto Invest"]'), 'SMS', 2, 0.2, 0, FALSE, 'Low', 0.21, 
 'Provide volatility education and risk management guidance'),

('CUST064', 'Susan Davis', 48, 13, 278000.00, 'Growth Plus', 1, '2025-05-18', 
 PARSE_JSON('["Growth Fund", "Insurance Plus", "Premium Services"]'), 'Phone', 1, 0.4, 0, FALSE, 'Low', 0.15, 
 'Offer premium advisory services and portfolio optimization'),

('CUST065', 'David Johnson', 37, 8, 119000.00, 'Balanced Growth', 2, '2025-05-17', 
 PARSE_JSON('["Balanced Fund", "Insurance", "Online Trading"]'), 'Email', 2, 0.3, 0, FALSE, 'Low', 0.16, 
 'Provide investment review and diversification options'),

('CUST066', 'Michelle Lee', 42, 10, 185000.00, 'Sustainable Growth', 1, '2025-05-16', 
 PARSE_JSON('["ESG Fund", "Insurance Plus", "Impact Reporting"]'), 'Email', 1, 0.6, 0, FALSE, 'Low', 0.11, 
 'Expand ESG investment options and sustainable impact measurement'),

('CUST067', 'Christopher Thompson', 36, 7, 92000.00, 'Growth Plus', 2, '2025-05-15', 
 PARSE_JSON('["Growth Fund", "Salary Sacrifice", "Mobile App"]'), 'Email', 2, 0.2, 0, FALSE, 'Low', 0.18, 
 'Provide market education and contribution optimization'),

('CUST068', 'Amanda Kim', 50, 14, 334000.00, 'Conservative', 2, '2025-05-14', 
 PARSE_JSON('["Conservative Fund", "Pension Account", "Insurance Bundle"]'), 'Phone', 2, 0.1, 0, FALSE, 'Low', 0.17, 
 'Discuss pre-retirement planning and transition strategies'),

('CUST069', 'Robert Brown', 28, 4, 41000.00, 'Balanced Growth', 1, '2025-05-13', 
 PARSE_JSON('["Balanced Fund", "Mobile Access", "Auto Invest"]'), 'SMS', 1, 0.5, 0, FALSE, 'Low', 0.12, 
 'Provide investment education and goal setting support'),

('CUST070', 'Laura Wilson', 40, 9, 154000.00, 'Growth Plus', 2, '2025-05-12', 
 PARSE_JSON('["Growth Fund", "Insurance", "Online Access"]'), 'Email', 2, 0.3, 0, FALSE, 'Low', 0.19, 
 'Offer investment review and portfolio optimization');

-- ============================================================================
-- SUMMARY INFORMATION
-- ============================================================================
-- Total customers: 69 (matching all customers in raw transcripts)
-- Demo focus: First 5 customers (CUST001-CUST005) 
-- Risk distribution: 
--   - High risk: 3 customers (CUST003, CUST010, CUST015)
--   - Medium risk: 8 customers 
--   - Low risk: 58 customers
-- Investment options: Balanced across all fund types
-- Age range: 27-64 years (realistic superannuation demographics)
-- Tenure range: 3-25 years
-- Balance range: $35K-$780K
-- ============================================================================

SELECT 'Customer data created successfully. Total customers: ' || COUNT(*) || ' (Demo focuses on first 5)' as RESULT
FROM CUSTOMER; 