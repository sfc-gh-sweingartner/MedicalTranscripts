#!/usr/bin/env python3
"""
Simple Customer Analytics Population
===================================
This script populates the CUSTOMER_ANALYTICS table with realistic data
for all 15 customers to support the Manager Dashboard.
"""

import snowflake.connector
import tomli
from pathlib import Path
import sys
import random

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def get_snowflake_connection():
    """Get Snowflake connection using config file"""
    try:
        config_path = Path('/Users/sweingartner/.snowflake/config.toml')
        with open(config_path, 'rb') as f:
            config = tomli.load(f)
        
        default_conn = config['default_connection_name']
        conn_params = config['connections'][default_conn]
        
        return snowflake.connector.connect(**conn_params)
    except Exception as e:
        print_error(f"Failed to connect to Snowflake: {str(e)}")
        return None

def generate_customer_analytics_data():
    """Generate realistic customer analytics data"""
    
    # Define customer data with realistic risk distribution
    customers = [
        # High risk customers (3 customers)
        {'id': 'CUST003', 'name': 'Maria Garcia', 'risk': 'High', 'prob': 0.78, 'confidence': 88.5},
        {'id': 'CUST007', 'name': 'James Wilson', 'risk': 'High', 'prob': 0.72, 'confidence': 85.2},
        {'id': 'CUST012', 'name': 'Patricia Brown', 'risk': 'High', 'prob': 0.69, 'confidence': 87.1},
        
        # Medium risk customers (4 customers)
        {'id': 'CUST005', 'name': 'Lisa Thompson', 'risk': 'Medium', 'prob': 0.48, 'confidence': 76.8},
        {'id': 'CUST008', 'name': 'Michael Davis', 'risk': 'Medium', 'prob': 0.42, 'confidence': 78.3},
        {'id': 'CUST011', 'name': 'Jennifer Miller', 'risk': 'Medium', 'prob': 0.45, 'confidence': 75.9},
        {'id': 'CUST014', 'name': 'Christopher Taylor', 'risk': 'Medium', 'prob': 0.39, 'confidence': 79.1},
        
        # Low risk customers (8 customers)
        {'id': 'CUST001', 'name': 'Sarah Chen', 'risk': 'Low', 'prob': 0.18, 'confidence': 92.1},
        {'id': 'CUST002', 'name': 'David Lee', 'risk': 'Low', 'prob': 0.22, 'confidence': 91.5},
        {'id': 'CUST004', 'name': 'John Smith', 'risk': 'Low', 'prob': 0.15, 'confidence': 93.2},
        {'id': 'CUST006', 'name': 'Emily White', 'risk': 'Low', 'prob': 0.25, 'confidence': 90.8},
        {'id': 'CUST009', 'name': 'Robert Johnson', 'risk': 'Low', 'prob': 0.19, 'confidence': 91.9},
        {'id': 'CUST010', 'name': 'Amanda Martinez', 'risk': 'Low', 'prob': 0.21, 'confidence': 92.4},
        {'id': 'CUST013', 'name': 'Daniel Anderson', 'risk': 'Low', 'prob': 0.17, 'confidence': 93.1},
        {'id': 'CUST015', 'name': 'Jessica Thomas', 'risk': 'Low', 'prob': 0.23, 'confidence': 91.2},
    ]
    
    # Add NBA recommendations based on risk level
    nba_recommendations = {
        'High': [
            'URGENT: Senior advisor intervention required - customer showing high frustration',
            'Immediate callback required - address service quality concerns',
            'Executive escalation recommended - multiple complaint indicators',
            'Priority retention offer - prevent churn with personalized benefits'
        ],
        'Medium': [
            'Follow up within 24 hours to address concerns',
            'Schedule proactive check-in call within 48 hours',
            'Provide additional technical support resources',
            'Offer account review meeting to discuss concerns'
        ],
        'Low': [
            'Standard follow-up communication',
            'Upsell opportunity - provide investment advisory consultation',
            'Offer consolidation services and educational resources',
            'Provide quarterly portfolio review and recommendations'
        ]
    }
    
    nba_reasoning = {
        'High': [
            'Multiple negative calls and complaints indicate high churn risk',
            'Significant service quality issues and escalating frustration',
            'Pattern of unresolved technical problems affecting satisfaction',
            'Recent complaints about fees and poor investment performance'
        ],
        'Medium': [
            'Some technical issues and concerns noted',
            'Occasional negative sentiment in recent interactions',
            'Minor service issues requiring attention',
            'Moderate dissatisfaction with recent account changes'
        ],
        'Low': [
            'Generally positive customer interactions',
            'Stable account activity with good engagement',
            'Positive sentiment in recent calls',
            'Satisfied customer with growth potential'
        ]
    }
    
    # Assign specific NBA and reasoning to each customer
    for customer in customers:
        risk_level = customer['risk']
        customer['nba'] = random.choice(nba_recommendations[risk_level])
        customer['reasoning'] = random.choice(nba_reasoning[risk_level])
        customer['prediction'] = 1 if risk_level == 'High' else 0
    
    return customers

def populate_customer_analytics_simple(conn):
    """Populate customer analytics table with simple realistic data"""
    cursor = conn.cursor()
    
    try:
        # Set context
        cursor.execute('USE DATABASE SUPERANNUATION')
        cursor.execute('USE SCHEMA TRANSCRIPTS')
        cursor.execute('USE WAREHOUSE MYWH')
        
        # Clear existing data
        print_info("Clearing existing customer analytics data...")
        cursor.execute('DELETE FROM CUSTOMER_ANALYTICS')
        
        # Generate customer data
        print_info("Generating customer analytics data...")
        customers = generate_customer_analytics_data()
        
        # Insert data
        print_info("Inserting customer analytics data...")
        
        for customer in customers:
            insert_sql = f"""
            INSERT INTO CUSTOMER_ANALYTICS (
                CUSTOMER_ID,
                CUSTOMER_NAME,
                CHURN_RISK_SCORE,
                CHURN_PROBABILITY,
                CHURN_PREDICTION,
                NEXT_BEST_ACTION,
                NBA_REASONING,
                MODEL_CONFIDENCE
            ) VALUES (
                '{customer['id']}',
                '{customer['name']}',
                '{customer['risk']}',
                {customer['prob']},
                {customer['prediction']},
                '{customer['nba']}',
                '{customer['reasoning']}',
                {customer['confidence']}
            )
            """
            cursor.execute(insert_sql)
        
        # Commit the transaction
        conn.commit()
        print_success(f"Successfully populated CUSTOMER_ANALYTICS table with {len(customers)} records")
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM CUSTOMER_ANALYTICS')
        count = cursor.fetchone()[0]
        print_success(f"Verification: {count} records in CUSTOMER_ANALYTICS table")
        
        # Show sample data
        cursor.execute("""
            SELECT 
                CUSTOMER_ID,
                CUSTOMER_NAME,
                CHURN_RISK_SCORE,
                CHURN_PROBABILITY,
                MODEL_CONFIDENCE
            FROM CUSTOMER_ANALYTICS
            ORDER BY CHURN_PROBABILITY DESC
            LIMIT 5
        """)
        
        print_info("Sample customer analytics data:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]:.0%} | {row[4]:.1f}% confidence")
        
        # Test the Manager Dashboard query
        cursor.execute("""
            SELECT 
                COUNT(*) as total_customers,
                SUM(CASE WHEN CHURN_RISK_SCORE = 'High' THEN 1 ELSE 0 END) as high_risk_customers,
                SUM(CASE WHEN CHURN_RISK_SCORE = 'Medium' THEN 1 ELSE 0 END) as medium_risk_customers,
                SUM(CASE WHEN CHURN_RISK_SCORE = 'Low' THEN 1 ELSE 0 END) as low_risk_customers,
                AVG(CHURN_PROBABILITY) as avg_churn_probability,
                AVG(MODEL_CONFIDENCE) as avg_model_confidence
            FROM CUSTOMER_ANALYTICS
        """)
        
        stats = cursor.fetchone()
        print_info("Manager Dashboard summary:")
        print(f"  Total customers: {stats[0]}")
        print(f"  High risk: {stats[1]}")
        print(f"  Medium risk: {stats[2]}")
        print(f"  Low risk: {stats[3]}")
        print(f"  Avg churn probability: {stats[4]:.1%}")
        print(f"  Avg model confidence: {stats[5]:.1f}%")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to populate customer analytics data: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function"""
    print_header("SIMPLE CUSTOMER ANALYTICS POPULATION")
    
    # Connect to Snowflake
    print_info("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    if not conn:
        return 1
    
    print_success("Connected to Snowflake")
    
    try:
        # Populate customer analytics data
        if populate_customer_analytics_simple(conn):
            print_header("CUSTOMER ANALYTICS POPULATION COMPLETED")
            print_success("Customer analytics table has been populated with realistic data")
            print_info("Manager Dashboard should now show proper metrics with:")
            print_info("- 15 total customers")
            print_info("- 3 high-risk customers")
            print_info("- 4 medium-risk customers") 
            print_info("- 8 low-risk customers")
            print_info("- Comprehensive sentiment trends from 285 calls over 30 days")
            return 0
        else:
            print_error("Failed to populate customer analytics data")
            return 1
            
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main()) 