#!/usr/bin/env python3
"""
Populate All Customers Table
============================
This script ensures the CUSTOMER table has all 15 customers with realistic data.
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

def generate_customer_data():
    """Generate comprehensive customer data for all 15 customers"""
    
    customers = [
        {
            'id': 'CUST001', 'name': 'Sarah Chen', 'age': 34, 'tenure': 5,
            'balance': 125000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 1, 'avg_sentiment': 0.1, 'negative_calls': 0,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST002', 'name': 'David Lee', 'age': 42, 'tenure': 8,
            'balance': 180000, 'investment': 'Balanced', 'contact': 'Phone',
            'call_freq': 2, 'avg_sentiment': 0.3, 'negative_calls': 1,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST003', 'name': 'Maria Garcia', 'age': 45, 'tenure': 7,
            'balance': 89000, 'investment': 'Balanced', 'contact': 'Phone',
            'call_freq': 4, 'avg_sentiment': -0.7, 'negative_calls': 6,
            'churn_intent': True, 'risk_score': 'High'
        },
        {
            'id': 'CUST004', 'name': 'John Smith', 'age': 38, 'tenure': 3,
            'balance': 95000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 2, 'avg_sentiment': 0.2, 'negative_calls': 0,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST005', 'name': 'Lisa Thompson', 'age': 52, 'tenure': 12,
            'balance': 220000, 'investment': 'Conservative', 'contact': 'Email',
            'call_freq': 3, 'avg_sentiment': -0.2, 'negative_calls': 2,
            'churn_intent': False, 'risk_score': 'Medium'
        },
        {
            'id': 'CUST006', 'name': 'Emily White', 'age': 64, 'tenure': 15,
            'balance': 780000, 'investment': 'Conservative', 'contact': 'Phone',
            'call_freq': 1, 'avg_sentiment': 0.1, 'negative_calls': 0,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST007', 'name': 'James Wilson', 'age': 41, 'tenure': 6,
            'balance': 145000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 3, 'avg_sentiment': -0.5, 'negative_calls': 4,
            'churn_intent': True, 'risk_score': 'High'
        },
        {
            'id': 'CUST008', 'name': 'Michael Davis', 'age': 48, 'tenure': 9,
            'balance': 165000, 'investment': 'Balanced', 'contact': 'Phone',
            'call_freq': 2, 'avg_sentiment': -0.1, 'negative_calls': 1,
            'churn_intent': False, 'risk_score': 'Medium'
        },
        {
            'id': 'CUST009', 'name': 'Robert Johnson', 'age': 35, 'tenure': 4,
            'balance': 110000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 1, 'avg_sentiment': 0.2, 'negative_calls': 0,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST010', 'name': 'Amanda Martinez', 'age': 43, 'tenure': 7,
            'balance': 175000, 'investment': 'Balanced', 'contact': 'Phone',
            'call_freq': 2, 'avg_sentiment': 0.1, 'negative_calls': 1,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST011', 'name': 'Jennifer Miller', 'age': 39, 'tenure': 5,
            'balance': 135000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 2, 'avg_sentiment': -0.3, 'negative_calls': 2,
            'churn_intent': False, 'risk_score': 'Medium'
        },
        {
            'id': 'CUST012', 'name': 'Patricia Brown', 'age': 46, 'tenure': 8,
            'balance': 155000, 'investment': 'Balanced', 'contact': 'Phone',
            'call_freq': 3, 'avg_sentiment': -0.6, 'negative_calls': 5,
            'churn_intent': True, 'risk_score': 'High'
        },
        {
            'id': 'CUST013', 'name': 'Daniel Anderson', 'age': 37, 'tenure': 4,
            'balance': 120000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 1, 'avg_sentiment': 0.3, 'negative_calls': 0,
            'churn_intent': False, 'risk_score': 'Low'
        },
        {
            'id': 'CUST014', 'name': 'Christopher Taylor', 'age': 44, 'tenure': 6,
            'balance': 140000, 'investment': 'Balanced', 'contact': 'Phone',
            'call_freq': 2, 'avg_sentiment': -0.2, 'negative_calls': 1,
            'churn_intent': False, 'risk_score': 'Medium'
        },
        {
            'id': 'CUST015', 'name': 'Jessica Thomas', 'age': 40, 'tenure': 5,
            'balance': 130000, 'investment': 'Growth', 'contact': 'Email',
            'call_freq': 1, 'avg_sentiment': 0.1, 'negative_calls': 0,
            'churn_intent': False, 'risk_score': 'Low'
        }
    ]
    
    return customers

def populate_customer_table(conn):
    """Populate customer table with all 15 customers"""
    cursor = conn.cursor()
    
    try:
        # Set context
        cursor.execute('USE DATABASE SUPERANNUATION')
        cursor.execute('USE SCHEMA TRANSCRIPTS')
        cursor.execute('USE WAREHOUSE MYWH')
        
        # Clear existing data
        print_info("Clearing existing customer data...")
        cursor.execute('DELETE FROM CUSTOMER')
        
        # Generate customer data
        print_info("Generating customer data...")
        customers = generate_customer_data()
        
        # Insert data
        print_info("Inserting customer data...")
        
        for customer in customers:
            # Generate product holdings as JSON
            product_holdings = f'[\\"{customer["investment"]} Fund\\", \\"Default Insurance\\"]'
            
            # Calculate churn probability based on risk score
            churn_prob = {
                'High': round(random.uniform(0.65, 0.85), 2),
                'Medium': round(random.uniform(0.35, 0.55), 2),
                'Low': round(random.uniform(0.10, 0.30), 2)
            }[customer['risk_score']]
            
            # Generate recent transactions
            recent_transactions = random.randint(1, 5)
            
            # Generate last interaction date (within last 30 days)
            days_ago = random.randint(1, 30)
            
            insert_sql = f"""
            INSERT INTO CUSTOMER (
                CUSTOMER_ID, CUSTOMER_NAME, AGE, TENURE_YEARS, ACCOUNT_BALANCE,
                INVESTMENT_OPTION, RECENT_TRANSACTIONS, LAST_INTERACTION_DATE,
                PRODUCT_HOLDINGS, CONTACT_PREFERENCE, CALL_FREQUENCY_LAST_MONTH,
                AVG_SENTIMENT_LAST_3_CALLS, NUM_NEGATIVE_CALLS_LAST_6_MONTHS,
                HAS_CHURN_INTENT_LAST_MONTH, CHURN_RISK_SCORE, CHURN_PROBABILITY,
                NEXT_BEST_ACTION
            ) 
            SELECT 
                '{customer['id']}',
                '{customer['name']}',
                {customer['age']},
                {customer['tenure']},
                {customer['balance']},
                '{customer['investment']}',
                {recent_transactions},
                CURRENT_DATE - {days_ago},
                PARSE_JSON('{product_holdings}'),
                '{customer['contact']}',
                {customer['call_freq']},
                {customer['avg_sentiment']},
                {customer['negative_calls']},
                {str(customer['churn_intent']).lower()},
                '{customer['risk_score']}',
                {churn_prob},
                'Generated by system'
            """
            cursor.execute(insert_sql)
        
        # Commit the transaction
        conn.commit()
        print_success(f"Successfully populated CUSTOMER table with {len(customers)} records")
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM CUSTOMER')
        count = cursor.fetchone()[0]
        print_success(f"Verification: {count} records in CUSTOMER table")
        
        # Show sample data
        cursor.execute("""
            SELECT 
                CUSTOMER_ID,
                CUSTOMER_NAME,
                AGE,
                INVESTMENT_OPTION,
                ACCOUNT_BALANCE,
                CHURN_RISK_SCORE
            FROM CUSTOMER
            ORDER BY CUSTOMER_ID
            LIMIT 10
        """)
        
        print_info("Sample customer data:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | Age {row[2]} | {row[3]} | ${row[4]:,.0f} | {row[5]} Risk")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to populate customer data: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function"""
    print_header("POPULATE ALL CUSTOMERS TABLE")
    
    # Connect to Snowflake
    print_info("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    if not conn:
        return 1
    
    print_success("Connected to Snowflake")
    
    try:
        # Populate customer data
        if populate_customer_table(conn):
            print_header("CUSTOMER TABLE POPULATION COMPLETED")
            print_success("Customer table has been populated with all 15 customers")
            print_info("All customers now have consistent data across tables")
            return 0
        else:
            print_error("Failed to populate customer data")
            return 1
            
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main()) 