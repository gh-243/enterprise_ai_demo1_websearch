#!/usr/bin/env python3
"""
Test script for document upload API.
"""

import requests
import json
import sys
import os

API_BASE = "http://127.0.0.1:8001/v1/documents"


def test_dependencies():
    """Test dependencies endpoint."""
    print("Testing dependencies endpoint...")
    try:
        response = requests.get(f"{API_BASE}/dependencies")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_upload():
    """Test document upload."""
    print("\nTesting document upload...")
    try:
        file_path = "/Users/gerardherrera/ai_chatbot/test_document.txt"
        
        with open(file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {
                'title': 'Test Document',
                'author': 'Test Author',
                'description': 'A test document for the student assistant',
                'subject': 'Testing',
                'tags': 'test,demo,document'
            }
            
            response = requests.post(f"{API_BASE}/upload", files=files, data=data)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
        else:
            print(f"Error Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_list_documents():
    """Test document listing."""
    print("\nTesting document listing...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_library_overview():
    """Test library overview."""
    print("\nTesting library overview...")
    try:
        response = requests.get(f"{API_BASE}/library/overview")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Student Assistant Document API")
    print("=" * 50)
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("❌ Dependencies test failed!")
        sys.exit(1)
    
    # Test upload
    upload_result = test_upload()
    
    if not upload_result:
        print("❌ Upload test failed!")
        sys.exit(1)
    
    # Test listing
    list_ok = test_list_documents()
    
    if not list_ok:
        print("❌ List test failed!")
        sys.exit(1)
    
    # Test overview
    overview_ok = test_library_overview()
    
    if not overview_ok:
        print("❌ Overview test failed!")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("🎓 Student Assistant Document API is working!")


if __name__ == "__main__":
    main()