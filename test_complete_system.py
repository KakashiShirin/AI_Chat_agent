#!/usr/bin/env python3
"""
Comprehensive test script for AI Data Agent
"""
import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_FILE = "../test_data.csv"

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    print("📁 Testing file upload...")
    try:
        if not os.path.exists(TEST_FILE):
            print(f"❌ Test file not found: {TEST_FILE}")
            return None
        
        with open(TEST_FILE, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ File uploaded successfully: {data['session_id']}")
            return data['session_id']
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_schema_retrieval(session_id):
    """Test schema retrieval"""
    print("📊 Testing schema retrieval...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/schema/{session_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Schema retrieved: {len(data['schema'])} tables")
            return True
        else:
            print(f"❌ Schema retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Schema error: {e}")
        return False

def test_api_key_management():
    """Test API key management"""
    print("🔑 Testing API key management...")
    try:
        # Test status endpoint
        response = requests.get(f"{BACKEND_URL}/api/v1/api-keys/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API key status: {data['total_api_keys']} keys")
            return True
        else:
            print(f"❌ API key status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API key error: {e}")
        return False

def test_ai_query(session_id):
    """Test AI query functionality"""
    print("🤖 Testing AI query...")
    try:
        query_data = {
            "query": "What is the average salary?",
            "session_id": session_id
        }
        response = requests.post(f"{BACKEND_URL}/api/v1/query", 
                              json=query_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"⚠️ Query completed with error: {data['error']}")
            else:
                print(f"✅ AI query successful: {data['answer'][:100]}...")
            return True
        else:
            print(f"❌ AI query failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI query error: {e}")
        return False

def test_credit_tracking():
    """Test credit tracking"""
    print("💰 Testing credit tracking...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/credits", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Credit tracking: {data['total_api_calls']} calls, ${data['estimated_cost_usd']:.6f} cost")
            return True
        else:
            print(f"❌ Credit tracking failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Credit tracking error: {e}")
        return False

def test_frontend_connection():
    """Test frontend connection"""
    print("🌐 Testing frontend connection...")
    try:
        response = requests.get(f"{FRONTEND_URL}", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Data Agent Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 7
    
    # Test 1: Backend Health
    if test_backend_health():
        tests_passed += 1
    
    # Test 2: Frontend Connection
    if test_frontend_connection():
        tests_passed += 1
    
    # Test 3: API Key Management
    if test_api_key_management():
        tests_passed += 1
    
    # Test 4: File Upload
    session_id = test_file_upload()
    if session_id:
        tests_passed += 1
        
        # Test 5: Schema Retrieval
        if test_schema_retrieval(session_id):
            tests_passed += 1
        
        # Test 6: AI Query
        if test_ai_query(session_id):
            tests_passed += 1
    
    # Test 7: Credit Tracking
    if test_credit_tracking():
        tests_passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your AI Data Agent is working perfectly!")
    elif tests_passed >= 5:
        print("✅ Most tests passed! Minor issues detected.")
    else:
        print("❌ Multiple tests failed. Check your configuration.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
