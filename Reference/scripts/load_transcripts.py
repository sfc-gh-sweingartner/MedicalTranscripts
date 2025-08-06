#!/usr/bin/env python3
"""
Load Call Transcripts from JSON to Snowflake
===========================================
This script loads the call transcript data from the JSON file into Snowflake.
"""

import json
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

def load_json_data(file_path):
    """Load and parse JSON data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print_success(f"Loaded {len(data)} records from JSON file")
        return data
    except Exception as e:
        print_error(f"Failed to load JSON data: {str(e)}")
        return None

def insert_transcripts(conn, transcript_data):
    """Insert transcript data into Snowflake"""
    cursor = conn.cursor()
    
    try:
        # Set context
        cursor.execute('USE DATABASE SUPERANNUATION')
        cursor.execute('USE SCHEMA TRANSCRIPTS')
        cursor.execute('USE WAREHOUSE MYWH')
        
        # Clear existing data
        print_info("Clearing existing transcript data...")
        cursor.execute('DELETE FROM RAW_CALL_TRANSCRIPTS')
        
        # Prepare insert statement
        insert_sql = """
        INSERT INTO RAW_CALL_TRANSCRIPTS (
            CALL_ID,
            CUSTOMER_ID,
            AGENT_ID,
            CALL_TIMESTAMP,
            CALL_DURATION_SECONDS,
            TRANSCRIPT_TEXT
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Insert data in batches
        batch_size = 50
        total_records = len(transcript_data)
        
        for i in range(0, total_records, batch_size):
            batch = transcript_data[i:i+batch_size]
            batch_data = []
            
            for record in batch:
                # Convert timestamp format if needed
                timestamp = record.get('CALL_TIMESTAMP', '').replace('T', ' ').replace('Z', '')
                
                batch_data.append((
                    record.get('CALL_ID'),
                    record.get('CUSTOMER_ID'),
                    record.get('AGENT_ID'),
                    timestamp,
                    record.get('CALL_DURATION_SECONDS'),
                    record.get('TRANSCRIPT_TEXT')
                ))
            
            cursor.executemany(insert_sql, batch_data)
            print_info(f"Inserted batch {i//batch_size + 1} ({len(batch)} records)")
        
        # Commit the transaction
        conn.commit()
        print_success(f"Successfully inserted {total_records} call transcripts")
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM RAW_CALL_TRANSCRIPTS')
        count = cursor.fetchone()[0]
        print_success(f"Verification: {count} records in RAW_CALL_TRANSCRIPTS table")
        
        # Show sample data
        cursor.execute("""
            SELECT 
                CALL_ID,
                CUSTOMER_ID,
                CALL_TIMESTAMP,
                LEFT(TRANSCRIPT_TEXT, 100) as TRANSCRIPT_PREVIEW
            FROM RAW_CALL_TRANSCRIPTS
            ORDER BY CALL_TIMESTAMP
            LIMIT 5
        """)
        
        print_info("Sample data:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}...")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to insert transcript data: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function"""
    print_header("LOAD CALL TRANSCRIPTS TO SNOWFLAKE")
    
    # Check if JSON file exists
    json_file = Path('call_transcripts_fixed.json')
    if not json_file.exists():
        print_error(f"JSON file not found: {json_file}")
        return 1
    
    # Load JSON data
    print_info(f"Loading data from {json_file}")
    transcript_data = load_json_data(json_file)
    if not transcript_data:
        return 1
    
    # Connect to Snowflake
    print_info("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    if not conn:
        return 1
    
    print_success("Connected to Snowflake")
    
    try:
        # Insert transcript data
        if insert_transcripts(conn, transcript_data):
            print_header("TRANSCRIPT LOADING COMPLETED SUCCESSFULLY")
            print_success("All call transcripts have been loaded into Snowflake")
            print_info("You can now refresh your Streamlit app to see the transcript data")
            return 0
        else:
            print_error("Failed to load transcript data")
            return 1
            
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main()) 