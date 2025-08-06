"""
Connection Helper Module for Superannuation Transcripts Demo
===========================================================

This module provides a unified connection interface that works in both:
1. Local Streamlit development environment
2. Streamlit in Snowflake hosted environment

Based on the pattern from Reference/nation_app.py
"""

import snowflake.connector
import tomli
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import os

@st.cache_resource(show_spinner="Connecting to Snowflake...")
def get_snowflake_connection():
    """
    Connection handler that works in both local and Snowflake environments
    Based on Reference/nation_app.py pattern with enhancements for demo
    """
    # First try to get active session (for Streamlit in Snowflake)
    try:
        session = get_active_session()
        if session:
            # Verify the session is working by testing a simple query
            session.sql("SELECT 1").collect()
            return session
    except Exception:
        # If get_active_session fails, continue to local connection
        pass
            
    # Try local connection using config file
    try:
        config_path = '/Users/sweingartner/.snowflake/config.toml'
        
        # Check if config file exists
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Snowflake config file not found at {config_path}")
            
        with open(config_path, 'rb') as f:
            config = tomli.load(f)
        
        # Get the default connection name
        default_conn = config.get('default_connection_name')
        if not default_conn:
            raise ValueError("No default connection specified in config.toml")
            
        # Get the connection configuration for the default connection
        conn_params = config.get('connections', {}).get(default_conn)
        if not conn_params:
            raise ValueError(f"Connection '{default_conn}' not found in config.toml")
        
        # Create a connection with error handling
        conn = snowflake.connector.connect(**conn_params)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        
        return conn
        
    except FileNotFoundError as e:
        st.error(f"Config file error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {str(e)}")
        return None

def execute_query(query, conn=None):
    """
    Execute a query using either Snowpark session or regular connection
    Returns pandas DataFrame
    """
    if conn is None:
        conn = get_snowflake_connection()
    
    if conn is None:
        raise Exception("No valid Snowflake connection available")
    
    try:
        if hasattr(conn, 'sql'):  # Snowpark session
            result = conn.sql(query).to_pandas()
        else:  # Regular connection
            result = pd.read_sql(query, conn)
        return result
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        raise

def safe_execute_query(query, conn=None, fallback_data=None):
    """
    Safely execute a query with fallback data if query fails
    Useful for demo scenarios where we want graceful degradation
    """
    try:
        return execute_query(query, conn)
    except Exception as e:
        st.warning(f"Query failed, using fallback data: {str(e)}")
        if fallback_data is not None:
            return fallback_data
        else:
            # Return empty dataframe with standard structure
            return pd.DataFrame()

def test_ai_functions(conn=None):
    """
    Test if Snowflake Cortex AI functions are available and working
    Returns dict with function availability status
    """
    if conn is None:
        conn = get_snowflake_connection()
    
    if conn is None:
        return {"error": "No connection available"}
    
    ai_functions = {
        "sentiment": False,
        "summarize": False,
        "complete": False,
        "classify": False
    }
    
    try:
        # Test sentiment analysis
        test_query = "SELECT SNOWFLAKE.CORTEX.SENTIMENT('This is a test message') as sentiment_test"
        result = execute_query(test_query, conn)
        if not result.empty:
            ai_functions["sentiment"] = True
    except:
        pass
    
    try:
        # Test summarization
        test_query = "SELECT SNOWFLAKE.CORTEX.SUMMARIZE('This is a test message for summarization testing. It contains multiple sentences to verify the summarization function works correctly.') as summarize_test"
        result = execute_query(test_query, conn)
        if not result.empty:
            ai_functions["summarize"] = True
    except:
        pass
    
    try:
        # Test completion (claude)
        test_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'claude-3-5-sonnet', 
            'Respond with just the word: WORKING'
        ) as complete_test
        """
        result = execute_query(test_query, conn)
        if not result.empty and 'WORKING' in str(result.iloc[0, 0]).upper():
            ai_functions["complete"] = True
    except:
        pass
    
    try:
        # Test classification
        test_query = """
        SELECT SNOWFLAKE.CORTEX.CLASSIFY_TEXT(
            'This is a positive message', 
            ['positive', 'negative', 'neutral']
        ) as classify_test
        """
        result = execute_query(test_query, conn)
        if not result.empty:
            ai_functions["classify"] = True
    except:
        pass
    
    return ai_functions

def get_demo_data_status(conn=None):
    """
    Check if demo data is loaded and available
    Returns dict with data availability status
    """
    if conn is None:
        conn = get_snowflake_connection()
    
    if conn is None:
        return {"error": "No connection available"}
    
    data_status = {
        "customers": False,
        "transcripts": False,
        "enriched_transcripts": False,
        "customer_analytics": False
    }
    
    tables_to_check = [
        ("customers", "SUPERANNUATION.TRANSCRIPTS.CUSTOMER"),
        ("transcripts", "SUPERANNUATION.TRANSCRIPTS.RAW_CALL_TRANSCRIPTS"),
        ("enriched_transcripts", "SUPERANNUATION.TRANSCRIPTS.ENRICHED_TRANSCRIPTS_ALL"),
        ("customer_analytics", "SUPERANNUATION.TRANSCRIPTS.CUSTOMER_ANALYTICS")
    ]
    
    for key, table_name in tables_to_check:
        try:
            query = f"SELECT COUNT(*) as row_count FROM {table_name} LIMIT 1"
            result = execute_query(query, conn)
            if not result.empty and result.iloc[0, 0] > 0:
                data_status[key] = True
        except:
            pass
    
    return data_status

@st.cache_data(ttl=600)
def get_connection_info():
    """
    Get connection information for display purposes
    Cached for 10 minutes to avoid repeated checks
    """
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return {"status": "disconnected", "type": "none"}
        
        if hasattr(conn, 'sql'):
            # Snowpark session
            account_info = conn.sql("SELECT CURRENT_ACCOUNT() as account").collect()[0]
            return {
                "status": "connected",
                "type": "snowpark", 
                "account": account_info['ACCOUNT'],
                "database": "SUPERANNUATION",
                "schema": "TRANSCRIPTS"
            }
        else:
            # Regular connection
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_ACCOUNT()")
            account = cursor.fetchone()[0]
            cursor.close()
            return {
                "status": "connected",
                "type": "connector",
                "account": account,
                "database": "SUPERANNUATION", 
                "schema": "TRANSCRIPTS"
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def initialize_demo_environment():
    """
    Initialize and validate the demo environment
    Returns comprehensive status information
    """
    status = {
        "connection": get_connection_info(),
        "ai_functions": {"error": "Not tested"},
        "data_status": {"error": "Not tested"}
    }
    
    # Only test AI functions and data if we have a good connection
    if status["connection"]["status"] == "connected":
        try:
            conn = get_snowflake_connection()
            status["ai_functions"] = test_ai_functions(conn)
            status["data_status"] = get_demo_data_status(conn)
        except Exception as e:
            status["ai_functions"] = {"error": str(e)}
            status["data_status"] = {"error": str(e)}
    
    return status 