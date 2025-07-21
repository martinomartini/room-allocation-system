#!/usr/bin/env python3
"""
Railway Startup Debugging Script
This script helps diagnose startup issues for the Room Allocation System
"""

import sys
import os
import traceback

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except Exception as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except Exception as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        from data.storage import storage
        print("✅ Storage module imported successfully")
    except Exception as e:
        print(f"❌ Storage module import failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    try:
        from data.models import TeamPreference, OasisPreference, ValidationHelper
        print("✅ Data models imported successfully")
    except Exception as e:
        print(f"❌ Data models import failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    try:
        from utils.security import security_manager, input_validator, rate_limiter, session_manager
        print("✅ Security utils imported successfully")
    except Exception as e:
        print(f"❌ Security utils import failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    return True

def test_storage():
    """Test storage functionality"""
    print("\n🔍 Testing storage...")
    
    try:
        from data.storage import storage
        
        # Test basic storage operations
        admin_settings = storage.get_admin_settings()
        print("✅ Admin settings loaded successfully")
        
        capacity_info = storage.get_capacity_info()
        print("✅ Capacity info loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_streamlit_config():
    """Test Streamlit configuration"""
    print("\n🔍 Testing Streamlit configuration...")
    
    config_file = ".streamlit/config.toml"
    if os.path.exists(config_file):
        print("✅ Streamlit config file exists")
        
        with open(config_file, 'r') as f:
            content = f.read()
            
        # Check for problematic config options
        if "client.caching" in content:
            print("❌ Deprecated 'client.caching' found in config")
            return False
        
        if "client.displayEnabled" in content:
            print("❌ Deprecated 'client.displayEnabled' found in config")
            return False
        
        print("✅ Streamlit config looks good")
        return True
    else:
        print("⚠️ No Streamlit config file found")
        return True

def main():
    """Main diagnostic function"""
    print("🚀 Railway Deployment Diagnostic")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")
    
    print("\n" + "=" * 50)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_storage():
        tests_passed += 1
    
    if test_streamlit_config():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! The application should start successfully.")
        
        # Try importing the main app
        try:
            print("\n🔍 Testing main app import...")
            import app
            print("✅ Main app imported successfully")
            print("🚀 Ready for Streamlit launch!")
        except Exception as e:
            print(f"❌ Main app import failed: {e}")
            print(f"Error details: {traceback.format_exc()}")
            sys.exit(1)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
