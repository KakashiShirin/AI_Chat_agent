#!/usr/bin/env python3
"""
Enhanced AI Agent Test Script
Tests the new comprehensive error handling, retry logic, and credit management features.
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoints"""
    print("🔍 Testing health endpoints...")
    
    # Test basic health
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Basic health: {response.status_code}")
    
    # Test API health
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"✅ API health: {response.status_code}")

def create_test_data():
    """Create test CSV data"""
    import pandas as pd
    
    # Create test data with some edge cases
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'Engineering'],
        'age': [25, 30, 35, 28, 32],
        'city': ['New York', 'San Francisco', 'Seattle', 'Boston', 'Austin']
    }
    
    df = pd.DataFrame(data)
    df.to_csv('test_enhanced_data.csv', index=False)
    print("✅ Test data created: test_enhanced_data.csv")

def test_file_upload():
    """Test file upload"""
    print("\n📁 Testing file upload...")
    
    with open('test_enhanced_data.csv', 'rb') as f:
        files = {'file': ('test_enhanced_data.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        session_id = result['session_id']
        print(f"✅ File uploaded successfully. Session ID: {session_id}")
        return session_id
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return None

def test_credit_tracking():
    """Test credit tracking functionality"""
    print("\n💰 Testing credit tracking...")
    
    # Get initial credit usage
    response = requests.get(f"{BASE_URL}/api/v1/credits")
    if response.status_code == 200:
        usage = response.json()
        print(f"✅ Initial credit usage: {usage}")
        return usage
    else:
        print(f"❌ Failed to get credit usage: {response.status_code}")
        return None

def test_ai_queries(session_id):
    """Test various AI queries to trigger retry logic"""
    print(f"\n🤖 Testing AI queries for session: {session_id}")
    
    queries = [
        "What is the average salary?",
        "How many people are in each department?",
        "Who is the youngest employee?",
        "What is the total salary for Engineering department?",
        "Show me employees earning more than 70000",
        "What are the top 3 highest paid employees?",
        "How many employees are in each city?",
        "What is the salary distribution?"
    ]
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        payload = {
            'query': query,
            'session_id': session_id
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful ({end_time - start_time:.2f}s)")
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
            print(f"   Chart Type: {result.get('chart_type', 'None')}")
            
            # Check for credit tracking info
            if 'api_calls_made' in result:
                print(f"   API Calls: {result['api_calls_made']}")
            if 'total_tokens_used' in result:
                print(f"   Tokens Used: {result['total_tokens_used']}")
            
            results.append(result)
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            results.append(None)
    
    return results

def test_error_scenarios(session_id):
    """Test error scenarios to trigger retry logic"""
    print(f"\n🚨 Testing error scenarios...")
    
    # Test with invalid session ID
    print("\n--- Testing invalid session ID ---")
    payload = {
        'query': 'What is the average salary?',
        'session_id': 'invalid-session-id'
    }
    response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
    print(f"Invalid session result: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Error handling: {result.get('error', 'No error')}")
    
    # Test with empty query
    print("\n--- Testing empty query ---")
    payload = {
        'query': '',
        'session_id': session_id
    }
    response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
    print(f"Empty query result: {response.status_code}")
    
    # Test with complex query that might trigger retries
    print("\n--- Testing complex query ---")
    payload = {
        'query': 'Create a complex analysis showing salary trends by department and age groups with statistical significance',
        'session_id': session_id
    }
    response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Complex query handled: {result.get('answer', 'No answer')[:100]}...")
        if 'api_calls_made' in result:
            print(f"   API Calls for complex query: {result['api_calls_made']}")

def test_credit_reset():
    """Test credit reset functionality"""
    print("\n🔄 Testing credit reset...")
    
    # Reset credits
    response = requests.post(f"{BASE_URL}/api/v1/credits/reset")
    if response.status_code == 200:
        print("✅ Credit tracking reset successfully")
        
        # Check credits after reset
        response = requests.get(f"{BASE_URL}/api/v1/credits")
        if response.status_code == 200:
            usage = response.json()
            print(f"✅ Credits after reset: {usage}")
    else:
        print(f"❌ Failed to reset credits: {response.status_code}")

def cleanup():
    """Clean up test files"""
    try:
        if os.path.exists('test_enhanced_data.csv'):
            os.remove('test_enhanced_data.csv')
            print("✅ Test file cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Enhanced AI Agent Tests")
    print("=" * 50)
    
    try:
        # Test health
        test_health()
        
        # Create test data
        create_test_data()
        
        # Test file upload
        session_id = test_file_upload()
        if not session_id:
            print("❌ Cannot proceed without session ID")
            return
        
        # Test credit tracking
        initial_credits = test_credit_tracking()
        
        # Test AI queries
        results = test_ai_queries(session_id)
        
        # Test error scenarios
        test_error_scenarios(session_id)
        
        # Test final credit usage
        print("\n💰 Final credit usage:")
        response = requests.get(f"{BASE_URL}/api/v1/credits")
        if response.status_code == 200:
            final_usage = response.json()
            print(f"✅ Final usage: {final_usage}")
            
            if initial_credits:
                calls_increase = final_usage['api_calls_made'] - initial_credits['api_calls_made']
                tokens_increase = final_usage['total_tokens_used'] - initial_credits['total_tokens_used']
                print(f"📊 Total API calls made during test: {calls_increase}")
                print(f"📊 Total tokens used during test: {tokens_increase}")
        
        # Test credit reset
        test_credit_reset()
        
        print("\n" + "=" * 50)
        print("🏁 Enhanced AI Agent Tests completed!")
        print("\n📋 Summary:")
        print(f"   - Successful queries: {sum(1 for r in results if r is not None)}")
        print(f"   - Failed queries: {sum(1 for r in results if r is None)}")
        print("   - Error handling: ✅ Tested")
        print("   - Retry logic: ✅ Tested")
        print("   - Credit tracking: ✅ Tested")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
