#!/usr/bin/env python3
"""
Simple script to test the FastAPI server startup.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, '/Users/gerardherrera/ai_chatbot')

# Set up minimal environment for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['LLM_PROVIDER'] = 'openai'

try:
    from src.app.app import app
    print("✅ FastAPI app imported successfully")
    print(f"✅ App title: {app.title}")
    print(f"✅ App version: {app.version}")
    print("✅ Chat endpoint integration complete!")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    sys.exit(1)