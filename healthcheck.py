#!/usr/bin/env python3
"""
Health check script for Railway deployment
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Test imports
    from data.storage import storage
    from data.models import ValidationHelper
    
    # Test storage initialization
    storage.get_admin_settings()
    
    print("✅ All systems operational")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Health check failed: {e}")
    sys.exit(1)
