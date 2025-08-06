#!/usr/bin/env python3
"""
Superannuation Transcripts Demo - One-Command Setup for Sales Engineers
======================================================================

This script automatically sets up the entire demo environment in a few minutes.
Perfect for sales engineers who need to quickly deploy the solution for customer demos.

Usage:
    python deploy_for_sales_engineers.py

Requirements:
    - Python 3.8+
    - Snowflake account access
    - ~/.snowflake/config.toml configured
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step_num, text):
    print(f"\n🔧 Step {step_num}: {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_step(1, "Checking Prerequisites")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ required. Current version: " + sys.version)
        return False
    print_success("Python version OK")
    
    # Check if config file exists
    config_path = Path.home() / ".snowflake" / "config.toml"
    if not config_path.exists():
        print_error(f"Snowflake config not found at {config_path}")
        print("Please create ~/.snowflake/config.toml with your Snowflake credentials:")
        print("""
[default]
account = "your_account"
user = "your_username"
password = "your_password"
warehouse = "COMPUTE_WH"
database = "SUPERANNUATION"
schema = "TRANSCRIPTS"
        """)
        return False
    print_success("Snowflake config found")
    
    # Check if we're in the right directory
    if not os.path.exists("src/streamlit_main.py"):
        print_error("Please run this script from the SuperannuationTranscripts directory")
        return False
    print_success("Project directory OK")
    
    return True

def install_requirements():
    """Install Python requirements"""
    print_step(2, "Installing Python Dependencies")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True, check=True)
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def setup_database():
    """Set up the Snowflake database and load data"""
    print_step(3, "Setting up Snowflake Database and Loading Data")
    
    try:
        # Run the quick deploy script
        result = subprocess.run([sys.executable, "scripts/quick_deploy_phase3_simple.py"], 
                              capture_output=True, text=True, check=True)
        print_success("Database setup completed")
        
        # Verify the setup
        result = subprocess.run([sys.executable, "scripts/verify_all_data.py"], 
                              capture_output=True, text=True, check=True)
        print_success("Data verification completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Database setup failed: {e}")
        print("Error details:", e.stderr)
        return False

def test_streamlit():
    """Test that Streamlit can start properly"""
    print_step(4, "Testing Streamlit Application")
    
    try:
        # Test import of main app
        sys.path.insert(0, 'src')
        import streamlit_main
        print_success("Streamlit application loads successfully")
        return True
    except Exception as e:
        print_error(f"Streamlit test failed: {e}")
        return False

def main():
    """Main deployment function"""
    print_header("Superannuation Transcripts Demo - Sales Engineer Setup")
    print("🚀 Setting up your demo environment...")
    
    start_time = time.time()
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites not met. Please fix the issues above and try again.")
        return False
    
    # Install requirements
    if not install_requirements():
        print_error("Failed to install requirements. Please check the error above.")
        return False
    
    # Set up database
    if not setup_database():
        print_error("Database setup failed. Please check your Snowflake connection and try again.")
        return False
    
    # Test Streamlit
    if not test_streamlit():
        print_error("Streamlit test failed. Please check the error above.")
        return False
    
    # Success!
    elapsed_time = time.time() - start_time
    print_header("🎉 Setup Complete!")
    print(f"✅ Total setup time: {elapsed_time:.1f} seconds")
    print("\n🚀 Ready to demo! Next steps:")
    print("1. Run: streamlit run src/streamlit_main.py")
    print("2. Open your browser to the displayed URL")
    print("3. Navigate to the '❓ Demo Guide' page for presentation instructions")
    print("4. Start with the '🤖 AI Processing Demo' page for maximum impact")
    
    print("\n🎯 Quick Demo Tips:")
    print("• Use CALL003 - Maria Garcia for high-risk churn scenario")
    print("• Use CALL004 - John Smith for positive ESG opportunity")
    print("• The AI Processing Demo is your centerpiece - spend 8-10 minutes there")
    print("• All demo scripts and troubleshooting are in the app's Demo Guide")
    
    print("\n📞 Support:")
    print("• Technical issues: Check the 'Solution Design' page in the app")
    print("• Demo questions: See the 'Demo Guide' page in the app")
    print("• Repository: https://github.com/sfc-gh-sweingartner/SuperannuationTranscripts")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 