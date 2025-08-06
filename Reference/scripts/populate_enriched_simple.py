#!/usr/bin/env python3
"""
Simple Enriched Transcripts Population
====================================
This script populates the ENRICHED_TRANSCRIPTS_ALL table with basic data
using direct SQL INSERT statements.
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

def populate_enriched_transcripts(conn):
    """Populate enriched transcripts with demo data"""
    cursor = conn.cursor()
    
    try:
        # Set context
        cursor.execute('USE DATABASE SUPERANNUATION')
        cursor.execute('USE SCHEMA TRANSCRIPTS')
        cursor.execute('USE WAREHOUSE MYWH')
        
        # Clear existing enriched data
        print_info("Clearing existing enriched transcript data...")
        cursor.execute('DELETE FROM ENRICHED_TRANSCRIPTS_ALL')
        
        # Insert enriched data for demo customers using direct SQL
        enriched_inserts = [
            # CUST001 - Sarah Chen
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL001', 'CUST001', '2025-07-10 09:05:12', 0.1, 'Neutral',
                   PARSE_JSON('"Account Inquiry"'), 
                   'Customer inquiring about account balance and recent deductions, concerned about market performance',
                   'Standard follow-up communication', FALSE, PARSE_JSON('"Low"')
            """,
            
            # CUST002 - David Lee
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL002', 'CUST002', '2025-07-10 09:10:45', 0.4, 'Positive',
                   PARSE_JSON('"Super Consolidation"'), 
                   'Customer seeking help with superannuation consolidation from previous employer',
                   'Upsell opportunity - provide investment advisory consultation', FALSE, PARSE_JSON('"Low"')
            """,
            
            # CUST003 - Maria Garcia
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL003', 'CUST003', '2025-07-10 09:15:20', -0.6, 'Negative',
                   PARSE_JSON('"Complaint"'), 
                   'Customer frustrated about not receiving annual statement, service quality concerns',
                   'URGENT: Senior advisor intervention required - customer showing high frustration', TRUE, PARSE_JSON('"High"')
            """,
            
            # CUST004 - John Smith
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL004', 'CUST004', '2025-07-10 09:20:00', 0.5, 'Positive',
                   PARSE_JSON('"Investment Inquiry"'), 
                   'Customer interested in exploring investment options and portfolio diversification',
                   'Upsell opportunity - provide investment advisory consultation', FALSE, PARSE_JSON('"Low"')
            """,
            
            # CUST005 - Emily White
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL005', 'CUST005', '2025-07-10 09:25:30', 0.2, 'Neutral',
                   PARSE_JSON('"Retirement Planning"'), 
                   'Customer approaching retirement seeking advice on withdrawal strategies',
                   'Standard follow-up communication', FALSE, PARSE_JSON('"Low"')
            """,
            
            # CUST006-CUST010 with basic data
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL006', 'CUST006', '2025-07-10 09:30:00', 0.3, 'Positive',
                   PARSE_JSON('"General Inquiry"'), 
                   'Customer making general inquiries about account features',
                   'Standard follow-up communication', FALSE, PARSE_JSON('"Low"')
            """,
            
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL007', 'CUST007', '2025-07-10 09:35:00', 0.1, 'Neutral',
                   PARSE_JSON('"Account Update"'), 
                   'Customer updating personal details and contact information',
                   'Standard follow-up communication', FALSE, PARSE_JSON('"Low"')
            """,
            
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL008', 'CUST008', '2025-07-10 09:40:00', 0.4, 'Positive',
                   PARSE_JSON('"Investment Inquiry"'), 
                   'Customer interested in sustainable investment options',
                   'Upsell opportunity - provide investment advisory consultation', FALSE, PARSE_JSON('"Low"')
            """,
            
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL009', 'CUST009', '2025-07-10 09:45:00', -0.2, 'Neutral',
                   PARSE_JSON('"Technical Support"'), 
                   'Customer experiencing minor technical issues with online access',
                   'Follow up within 24 hours to address concerns', TRUE, PARSE_JSON('"Medium"')
            """,
            
            """
            INSERT INTO ENRICHED_TRANSCRIPTS_ALL (
                CALL_ID, CUSTOMER_ID, CALL_TIMESTAMP, SENTIMENT_SCORE, SENTIMENT_LABEL,
                PRIMARY_INTENT, CALL_SUMMARY, NEXT_BEST_ACTION, HAS_CHURN_INDICATORS,
                CHURN_RISK_CATEGORY
            ) 
            SELECT 'CALL010', 'CUST010', '2025-07-10 09:50:00', 0.6, 'Positive',
                   PARSE_JSON('"Insurance Inquiry"'), 
                   'Customer inquiring about insurance coverage options',
                   'Upsell opportunity - provide insurance advisory consultation', FALSE, PARSE_JSON('"Low"')
            """
        ]
        
        # Execute all inserts
        for i, insert_sql in enumerate(enriched_inserts, 1):
            cursor.execute(insert_sql)
            print_info(f"Inserted enriched data for customer {i}")
        
        # Commit the transaction
        conn.commit()
        print_success(f"Successfully populated enriched transcript data for 10 customers")
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM ENRICHED_TRANSCRIPTS_ALL')
        count = cursor.fetchone()[0]
        print_success(f"Verification: {count} records in ENRICHED_TRANSCRIPTS_ALL table")
        
        # Show sample data
        cursor.execute("""
            SELECT 
                CALL_ID,
                CUSTOMER_ID,
                SENTIMENT_LABEL,
                PRIMARY_INTENT,
                CHURN_RISK_CATEGORY
            FROM ENRICHED_TRANSCRIPTS_ALL
            ORDER BY CUSTOMER_ID
            LIMIT 5
        """)
        
        print_info("Sample enriched data:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to populate enriched transcript data: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function"""
    print_header("POPULATE ENRICHED TRANSCRIPTS (SIMPLE)")
    
    # Connect to Snowflake
    print_info("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    if not conn:
        return 1
    
    print_success("Connected to Snowflake")
    
    try:
        # Populate enriched transcript data
        if populate_enriched_transcripts(conn):
            print_header("ENRICHED TRANSCRIPT POPULATION COMPLETED")
            print_success("Demo transcript data has been processed and enriched")
            print_info("You can now refresh your Streamlit app to see the transcript data")
            return 0
        else:
            print_error("Failed to populate enriched transcript data")
            return 1
            
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main()) 