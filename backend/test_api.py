#!/usr/bin/env python3
"""
Test script for AI Data Agent Backend
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def test_api_health_endpoint():
    """Test the API health check endpoint"""
    print("\nTesting API health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ API health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API health check failed: {e}")

def create_test_csv():
    """Create a test CSV file"""
    test_data = """name,age,city,salary
John Doe,30,New York,75000
Jane Smith,25,Los Angeles,65000
Bob Johnson,35,Chicago,80000
Alice Brown,28,Boston,70000"""
    
    with open("test_data.csv", "w") as f:
        f.write(test_data)
    print("\n✅ Test CSV file created: test_data.csv")

def test_file_upload():
    """Test file upload endpoint"""
    print("\nTesting file upload...")
    
    # Create test file
    create_test_csv()
    
    try:
        with open("test_data.csv", "rb") as f:
            files = {"file": ("test_data.csv", f, "text/csv")}
            response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
            
        if response.status_code == 200:
            print("✅ File upload successful")
            result = response.json()
            print(f"Session ID: {result['session_id']}")
            print(f"Tables: {len(result['tables'])}")
            return result['session_id']
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ File upload failed: {e}")
    
    # Clean up test file
    if os.path.exists("test_data.csv"):
        os.remove("test_data.csv")
    
    return None

def test_schema_endpoint(session_id):
    """Test schema retrieval endpoint"""
    if not session_id:
        print("\n❌ No session ID available for schema test")
        return
        
    print(f"\nTesting schema endpoint for session: {session_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/schema/{session_id}")
        if response.status_code == 200:
            print("✅ Schema retrieval successful")
            schema = response.json()
            print(f"Session ID: {schema['session_id']}")
            print(f"Tables found: {len(schema['schema'])}")
            for table_name, table_info in schema['schema'].items():
                print(f"  - {table_name}: {len(table_info['columns'])} columns")
        else:
            print(f"❌ Schema retrieval failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Schema retrieval failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting AI Data Agent Backend Tests")
    print("=" * 50)
    
    # Test health endpoints
    test_health_endpoint()
    test_api_health_endpoint()
    
    # Test file upload
    session_id = test_file_upload()
    
    # Test schema retrieval
    test_schema_endpoint(session_id)
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed")

if __name__ == "__main__":
    main()
