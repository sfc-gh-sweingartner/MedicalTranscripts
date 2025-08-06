#!/usr/bin/env python3
"""
Comprehensive Data Verification
===============================
This script verifies that all tables have consistent data for the demo.
"""

import snowflake.connector
import tomli
from pathlib import Path
import sys

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

def verify_data_consistency(conn):
    """Verify data consistency across all tables"""
    cursor = conn.cursor()
    
    try:
        # Set context
        cursor.execute('USE DATABASE SUPERANNUATION')
        cursor.execute('USE SCHEMA TRANSCRIPTS')
        cursor.execute('USE WAREHOUSE MYWH')
        
        print_header("DATA CONSISTENCY VERIFICATION")
        
        # Check table record counts
        tables = ['CUSTOMER', 'CUSTOMER_ANALYTICS', 'ENRICHED_TRANSCRIPTS_ALL', 'RAW_CALL_TRANSCRIPTS']
        table_counts = {}
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            table_counts[table] = count
            print_info(f"{table}: {count} records")
        
        # Verify customer consistency
        print_header("CUSTOMER CONSISTENCY CHECK")
        
        customer_tables = ['CUSTOMER', 'CUSTOMER_ANALYTICS', 'ENRICHED_TRANSCRIPTS_ALL']
        customer_counts = {}
        
        for table in customer_tables:
            cursor.execute(f'SELECT COUNT(DISTINCT CUSTOMER_ID) FROM {table}')
            count = cursor.fetchone()[0]
            customer_counts[table] = count
            print_info(f"{table}: {count} unique customers")
        
        # Check if all tables have same customers
        if len(set(customer_counts.values())) == 1:
            print_success("All tables have consistent customer counts")
        else:
            print_error("Customer counts are inconsistent across tables")
        
        # Test Manager Dashboard queries
        print_header("MANAGER DASHBOARD QUERY VERIFICATION")
        
        # Executive summary query
        cursor.execute("""
            SELECT 
                COUNT(*) as total_customers,
                SUM(CASE WHEN ca.CHURN_RISK_SCORE = 'High' THEN 1 ELSE 0 END) as high_risk_customers,
                SUM(CASE WHEN ca.CHURN_RISK_SCORE = 'Medium' THEN 1 ELSE 0 END) as medium_risk_customers,
                SUM(CASE WHEN ca.CHURN_RISK_SCORE = 'Low' THEN 1 ELSE 0 END) as low_risk_customers,
                AVG(ca.CHURN_PROBABILITY) as avg_churn_probability,
                AVG(ca.MODEL_CONFIDENCE) as avg_model_confidence,
                SUM(c.ACCOUNT_BALANCE) as total_aum
            FROM CUSTOMER_ANALYTICS ca
            JOIN CUSTOMER c ON ca.CUSTOMER_ID = c.CUSTOMER_ID
        """)
        
        summary = cursor.fetchone()
        print_info("Executive Summary:")
        print(f"  Total customers: {summary[0]}")
        print(f"  High risk: {summary[1]}")
        print(f"  Medium risk: {summary[2]}")
        print(f"  Low risk: {summary[3]}")
        print(f"  Avg churn probability: {summary[4]:.1%}")
        print(f"  Avg model confidence: {summary[5]:.1f}%")
        print(f"  Total AUM: ${summary[6]:,.0f}")
        
        # Sentiment trends query
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT DATE_TRUNC('day', CALL_TIMESTAMP)) as unique_days,
                COUNT(*) as total_calls,
                AVG(SENTIMENT_SCORE) as avg_sentiment,
                COUNT(CASE WHEN SENTIMENT_SCORE < -0.3 THEN 1 END) as negative_calls,
                COUNT(CASE WHEN SENTIMENT_SCORE > 0.3 THEN 1 END) as positive_calls
            FROM ENRICHED_TRANSCRIPTS_ALL
            WHERE CALL_TIMESTAMP >= CURRENT_DATE - 30
        """)
        
        sentiment = cursor.fetchone()
        print_info("Sentiment Trends:")
        print(f"  Days with calls: {sentiment[0]}")
        print(f"  Total calls: {sentiment[1]}")
        print(f"  Average sentiment: {sentiment[2]:.2f}")
        print(f"  Negative calls: {sentiment[3]}")
        print(f"  Positive calls: {sentiment[4]}")
        
        # Intent analysis query
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT PRIMARY_INTENT) as unique_intents,
                COUNT(*) as total_calls
            FROM ENRICHED_TRANSCRIPTS_ALL
        """)
        
        intent = cursor.fetchone()
        print_info("Intent Analysis:")
        print(f"  Unique intent types: {intent[0]}")
        print(f"  Total calls with intent: {intent[1]}")
        
        # Test Advisor View query
        print_header("ADVISOR VIEW QUERY VERIFICATION")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_customers,
                COUNT(CASE WHEN CHURN_RISK_SCORE = 'High' THEN 1 END) as high_risk_for_advisor
            FROM CUSTOMER
        """)
        
        advisor = cursor.fetchone()
        print_info("Advisor View:")
        print(f"  Customers available in dropdown: {advisor[0]}")
        print(f"  High risk customers for advisor attention: {advisor[1]}")
        
        # Verification summary
        print_header("VERIFICATION SUMMARY")
        
        all_good = True
        
        # Check expected counts
        if table_counts['CUSTOMER'] != 15:
            print_error(f"Expected 15 customers, got {table_counts['CUSTOMER']}")
            all_good = False
        else:
            print_success("Customer table has correct count (15)")
        
        if table_counts['CUSTOMER_ANALYTICS'] != 15:
            print_error(f"Expected 15 customer analytics records, got {table_counts['CUSTOMER_ANALYTICS']}")
            all_good = False
        else:
            print_success("Customer analytics table has correct count (15)")
        
        if table_counts['ENRICHED_TRANSCRIPTS_ALL'] < 200:
            print_error(f"Expected 200+ enriched transcripts, got {table_counts['ENRICHED_TRANSCRIPTS_ALL']}")
            all_good = False
        else:
            print_success(f"Enriched transcripts table has good count ({table_counts['ENRICHED_TRANSCRIPTS_ALL']})")
        
        if summary[1] != 3:  # High risk customers
            print_error(f"Expected 3 high risk customers, got {summary[1]}")
            all_good = False
        else:
            print_success("Correct number of high risk customers (3)")
        
        if summary[2] != 4:  # Medium risk customers
            print_error(f"Expected 4 medium risk customers, got {summary[2]}")
            all_good = False
        else:
            print_success("Correct number of medium risk customers (4)")
        
        if summary[3] != 8:  # Low risk customers
            print_error(f"Expected 8 low risk customers, got {summary[3]}")
            all_good = False
        else:
            print_success("Correct number of low risk customers (8)")
        
        if sentiment[0] < 20:  # Days with calls
            print_error(f"Expected 20+ days with calls, got {sentiment[0]}")
            all_good = False
        else:
            print_success(f"Good date range coverage ({sentiment[0]} days)")
        
        if all_good:
            print_success("🎉 ALL VERIFICATION CHECKS PASSED!")
            print_info("The demo is ready with:")
            print_info("- 15 customers in all tables")
            print_info("- 3 High, 4 Medium, 8 Low risk customers")
            print_info("- 200+ call records across 20+ days")
            print_info("- Consistent data across all tables")
            print_info("- Manager Dashboard charts will have rich data")
            print_info("- Advisor View dropdown will show all 15 customers")
        else:
            print_error("Some verification checks failed - please review above")
        
        return all_good
        
    except Exception as e:
        print_error(f"Verification failed: {str(e)}")
        return False
    finally:
        cursor.close()

def main():
    """Main function"""
    print_header("COMPREHENSIVE DATA VERIFICATION")
    
    # Connect to Snowflake
    print_info("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    if not conn:
        return 1
    
    print_success("Connected to Snowflake")
    
    try:
        # Verify data consistency
        if verify_data_consistency(conn):
            print_header("VERIFICATION COMPLETED SUCCESSFULLY")
            print_success("All data is consistent and ready for demo")
            return 0
        else:
            print_error("Verification failed - data issues detected")
            return 1
            
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main()) 