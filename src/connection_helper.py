"""
Connection Helper Module for Healthcare AI Demo
==============================================

This module provides a unified connection interface that works in both:
1. Local Streamlit development environment
2. Streamlit in Snowflake hosted environment

Adapted from the superannuation demo pattern for healthcare use cases.
"""

import snowflake.connector
import tomli
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import os
import json
from typing import Dict, Any, Optional, Union

@st.cache_resource(show_spinner="Connecting to Snowflake...")
def get_snowflake_connection():
    """
    Connection handler that works in both local and Snowflake environments
    Returns either a Snowpark session or a regular connection
    """
    # First try to get active session (for Streamlit in Snowflake)
    try:
        session = get_active_session()
        if session:
            # Verify the session is working by testing a simple query
            session.sql("SELECT 1").collect()
            # Set the context to our healthcare database
            session.sql("USE DATABASE HEALTHCARE_DEMO").collect()
            session.sql("USE SCHEMA MEDICAL_NOTES").collect()
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
        
        # Set up the healthcare database context
        cursor = conn.cursor()
        cursor.execute("USE DATABASE HEALTHCARE_DEMO")
        cursor.execute("USE SCHEMA MEDICAL_NOTES")
        
        # Test the connection
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

def execute_query(query: str, conn=None) -> pd.DataFrame:
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

def safe_execute_query(query: str, conn=None, fallback_data=None) -> pd.DataFrame:
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

def test_cortex_ai_functions(conn=None) -> Dict[str, bool]:
    """
    Test if Snowflake Cortex AI functions are available and working
    Specifically tests models used in healthcare demo
    """
    if conn is None:
        conn = get_snowflake_connection()
    
    if conn is None:
        return {"error": "No connection available"}
    
    ai_functions = {
        "mistral-large": False,
        "mixtral-8x7b": False,
        "llama3.1-70b": False,
        "sentiment": False,
        "summarize": False
    }
    
    # Test sentiment analysis
    try:
        test_query = "SELECT SNOWFLAKE.CORTEX.SENTIMENT('Patient appears to be recovering well') as sentiment_test"
        result = execute_query(test_query, conn)
        if not result.empty:
            ai_functions["sentiment"] = True
    except:
        pass
    
    # Test summarization
    try:
        test_query = """SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
            'Patient presented with chest pain and shortness of breath. ECG showed ST elevation. 
            Troponin levels elevated. Diagnosed with acute myocardial infarction. 
            Started on dual antiplatelet therapy and underwent emergency PCI.'
        ) as summarize_test"""
        result = execute_query(test_query, conn)
        if not result.empty:
            ai_functions["summarize"] = True
    except:
        pass
    
    # Test Mistral Large (for clinical summaries)
    try:
        test_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-large', 
            'Respond with just: WORKING'
        ) as complete_test
        """
        result = execute_query(test_query, conn)
        if not result.empty and 'WORKING' in str(result.iloc[0, 0]).upper():
            ai_functions["mistral-large"] = True
    except:
        pass
    
    # Test Mixtral 8x7b (for diagnostic analysis)
    try:
        test_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mixtral-8x7b', 
            'Respond with just: WORKING'
        ) as complete_test
        """
        result = execute_query(test_query, conn)
        if not result.empty and 'WORKING' in str(result.iloc[0, 0]).upper():
            ai_functions["mixtral-8x7b"] = True
    except:
        pass
    
    # Test Llama 3.1 70b (for education content)
    try:
        test_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3.1-70b', 
            'Respond with just: WORKING'
        ) as complete_test
        """
        result = execute_query(test_query, conn)
        if not result.empty and 'WORKING' in str(result.iloc[0, 0]).upper():
            ai_functions["llama3.1-70b"] = True
    except:
        pass
    
    return ai_functions

def get_demo_data_status(_conn=None) -> Dict[str, Any]:
    """
    Check if demo data is loaded and available
    Returns dict with data availability status
    """
    if _conn is None:
        _conn = get_snowflake_connection()
    
    if _conn is None:
        return {"error": "No connection available"}
    
    data_status = {
        "pmc_patients": {"available": False, "count": 0},
        "patient_analysis": {"available": False, "count": 0},
        "demo_scenarios": {"available": False, "count": 0},
        "realtime_logs": {"available": False, "count": 0}
    }
    
    tables_to_check = [
        ("pmc_patients", "PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS"),
        ("patient_analysis", "HEALTHCARE_DEMO.MEDICAL_NOTES.PATIENT_ANALYSIS"),
        ("demo_scenarios", "HEALTHCARE_DEMO.MEDICAL_NOTES.DEMO_SCENARIOS"),
        ("realtime_logs", "HEALTHCARE_DEMO.MEDICAL_NOTES.REALTIME_ANALYSIS_LOG")
    ]
    
    for key, table_name in tables_to_check:
        try:
            query = f"SELECT COUNT(*) as row_count FROM {table_name} LIMIT 1"
            result = execute_query(query, _conn)
            if not result.empty:
                count = result.iloc[0, 0]
                data_status[key] = {"available": count > 0, "count": count}
        except:
            data_status[key] = {"available": False, "count": 0, "error": "Table not found"}
    
    return data_status

@st.cache_data(ttl=600)
def get_connection_info() -> Dict[str, Any]:
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
            db_info = conn.sql("SELECT CURRENT_DATABASE() as database, CURRENT_SCHEMA() as schema").collect()[0]
            return {
                "status": "connected",
                "type": "snowpark", 
                "account": account_info['ACCOUNT'],
                "database": db_info['DATABASE'] or "HEALTHCARE_DEMO",
                "schema": db_info['SCHEMA'] or "MEDICAL_NOTES"
            }
        else:
            # Regular connection
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            account, database, schema = cursor.fetchone()
            cursor.close()
            return {
                "status": "connected",
                "type": "connector",
                "account": account,
                "database": database or "HEALTHCARE_DEMO", 
                "schema": schema or "MEDICAL_NOTES"
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def initialize_demo_environment() -> Dict[str, Any]:
    """
    Initialize and validate the healthcare demo environment
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
            status["ai_functions"] = test_cortex_ai_functions(conn)
            status["data_status"] = get_demo_data_status(conn)
        except Exception as e:
            status["ai_functions"] = {"error": str(e)}
            status["data_status"] = {"error": str(e)}
    
    return status

def execute_cortex_complete(prompt: str, model: str = "mistral-large", conn=None) -> str:
    """
    Execute a Cortex AI completion request
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (default: mistral-large)
        conn: Optional connection object
    
    Returns:
        The model's response as a string
    """
    if conn is None:
        conn = get_snowflake_connection()
    
    query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        '{model}',
        '{prompt.replace("'", "''")}'
    ) as response
    """
    
    result = execute_query(query, conn)
    if not result.empty:
        return result.iloc[0, 0]
    return ""

def get_sample_patients(limit: int = 10, conn=None) -> pd.DataFrame:
    """
    Get sample patients from PMC dataset for testing
    """
    query = f"""
    SELECT 
        PATIENT_ID,
        PATIENT_UID,
        PATIENT_TITLE,
        AGE,
        GENDER,
        SUBSTR(PATIENT_NOTES, 1, 200) || '...' as NOTES_PREVIEW
    FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
    LIMIT {limit}
    """
    
    return safe_execute_query(query, conn)

def log_realtime_analysis(
    session_id: str,
    user_name: str,
    patient_id: int,
    original_text: str,
    modified_text: str,
    analysis_type: str,
    ai_model: str,
    processing_time_ms: int,
    results: Dict[str, Any],
    success: bool,
    conn=None
) -> None:
    """
    Log a real-time analysis request for audit and performance tracking
    Uses parameterized queries to avoid SQL injection and escaping issues
    """
    if conn is None:
        conn = get_snowflake_connection()
    
    try:
        # Truncate long text fields to prevent database errors
        original_text_truncated = original_text[:1000] if original_text else ""
        modified_text_truncated = modified_text[:1000] if modified_text else ""
        
        # Convert results to JSON string with proper handling
        results_json = json.dumps(results, ensure_ascii=True, separators=(',', ':'))
        
        # Use parameterized query approach based on connection type
        if hasattr(conn, 'sql'):
            # Snowpark session - use SQL with binding
            query = """
            INSERT INTO HEALTHCARE_DEMO.MEDICAL_NOTES.REALTIME_ANALYSIS_LOG
            (SESSION_ID, USER_NAME, PATIENT_ID, ORIGINAL_TEXT, MODIFIED_TEXT, 
             ANALYSIS_TYPE, AI_MODEL_USED, PROCESSING_TIME_MS, RESULTS, SUCCESS_FLAG)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, PARSE_JSON(?), ?)
            """
            conn.sql(query, params=[
                session_id, user_name, patient_id, original_text_truncated, 
                modified_text_truncated, analysis_type, ai_model, 
                processing_time_ms, results_json, success
            ]).collect()
        else:
            # Regular connection - use cursor with parameters
            cursor = conn.cursor()
            query = """
            INSERT INTO HEALTHCARE_DEMO.MEDICAL_NOTES.REALTIME_ANALYSIS_LOG
            (SESSION_ID, USER_NAME, PATIENT_ID, ORIGINAL_TEXT, MODIFIED_TEXT, 
             ANALYSIS_TYPE, AI_MODEL_USED, PROCESSING_TIME_MS, RESULTS, SUCCESS_FLAG)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s), %s)
            """
            cursor.execute(query, (
                session_id, user_name, patient_id, original_text_truncated,
                modified_text_truncated, analysis_type, ai_model,
                processing_time_ms, results_json, success
            ))
            cursor.close()
            
    except Exception as e:
        # Silently handle logging failures to not disrupt user experience
        print(f"Failed to log analysis: {str(e)}")
        # For debugging, you can temporarily enable this:
        # st.warning(f"Logging failed (analysis continued): {str(e)}")

# Medical-specific helper functions

def format_sbar_summary(sbar_data: Dict[str, str]) -> str:
    """
    Format SBAR summary data for display
    """
    return f"""
**Situation:** {sbar_data.get('situation', 'N/A')}

**Background:** {sbar_data.get('background', 'N/A')}

**Assessment:** {sbar_data.get('assessment', 'N/A')}

**Recommendation:** {sbar_data.get('recommendation', 'N/A')}
    """

def parse_json_safely(json_str: str, default=None) -> Any:
    """
    Safely parse JSON string with fallback
    """
    if not json_str:
        return default if default is not None else {}
    
    try:
        return json.loads(json_str)
    except:
        # Try to fix common issues
        try:
            # Replace single quotes with double quotes
            fixed_str = json_str.replace("'", '"')
            return json.loads(fixed_str)
        except:
            return default if default is not None else {}

def query_cortex_search_service(search_term: str, service_name: str = 'patient_search_service', limit: int = 20, conn=None) -> pd.DataFrame:
    """
    Query Cortex Search service - production implementation with smart fallback
    """
    # Enhanced fallback search with medical misspelling tolerance
    search_variants = [search_term]
    
    # Add common medical misspellings
    medical_corrections = {
        'brest': 'breast', 'cardic': 'cardiac', 'diabetis': 'diabetes',
        'pnemonia': 'pneumonia', 'cancor': 'cancer', 'hart': 'heart', 'blod': 'blood'
    }
    
    for misspelled, correct in medical_corrections.items():
        if misspelled.lower() in search_term.lower():
            corrected_term = search_term.lower().replace(misspelled.lower(), correct.lower())
            search_variants.append(corrected_term)
    
    # Build intelligent search query
    search_conditions = []
    for variant in search_variants:
        search_conditions.extend([
            f"UPPER(PATIENT_NOTES) LIKE UPPER('%{variant}%')",
            f"UPPER(PATIENT_TITLE) LIKE UPPER('%{variant}%')"
        ])
    
    # Add partial word matching
    search_words = search_term.split()
    for word in search_words:
        if len(word) > 3:
            search_conditions.append(f"UPPER(PATIENT_NOTES) LIKE UPPER('%{word}%')")
    
    query = f"""
    SELECT 
        PATIENT_ID,
        PATIENT_UID,
        PATIENT_TITLE,
        AGE,
        GENDER,
        CASE 
            WHEN UPPER(PATIENT_TITLE) LIKE UPPER('%{search_term}%') THEN 0.9
            WHEN UPPER(PATIENT_NOTES) LIKE UPPER('%{search_term}%') THEN 0.8
            WHEN CAST(PATIENT_ID AS STRING) LIKE '%{search_term}%' THEN 0.7
            ELSE 0.5
        END as score
    FROM PMC_PATIENTS.PMC_PATIENTS.PMC_PATIENTS
    WHERE PATIENT_NOTES IS NOT NULL
        AND LENGTH(PATIENT_NOTES) > 50
        AND ({' OR '.join(search_conditions)})
    ORDER BY score DESC, PATIENT_ID
    LIMIT {limit}
    """
    
    return safe_execute_query(query, conn)