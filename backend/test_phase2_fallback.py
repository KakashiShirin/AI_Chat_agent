#!/usr/bin/env python3
"""
Test script for AI Data Agent Backend - Phase 2 with Fallback Testing
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
    """Create a test CSV file with sample data"""
    test_data = """name,age,city,salary,department
John Doe,30,New York,75000,Engineering
Jane Smith,25,Los Angeles,65000,Marketing
Bob Johnson,35,Chicago,80000,Engineering
Alice Brown,28,Boston,70000,Sales
Charlie Wilson,32,Seattle,85000,Engineering
Diana Davis,27,Austin,60000,Marketing
Eve Miller,29,Denver,72000,Sales
Frank Garcia,31,Miami,68000,Engineering
Grace Lee,26,Portland,62000,Marketing
Henry Taylor,33,Atlanta,78000,Sales"""
    
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

def test_ai_query(session_id, query, test_name=""):
    """Test AI query endpoint"""
    if not session_id:
        print("\n❌ No session ID available for AI query test")
        return
        
    print(f"\nTesting AI query{test_name}: '{query}'")
    try:
        # Send as JSON data
        payload = {
            "query": query,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
        
        if response.status_code == 200:
            print("✅ AI query successful")
            result = response.json()
            print(f"Answer: {result.get('answer', 'No answer')}")
            print(f"Chart Type: {result.get('chart_type', 'No chart type')}")
            if result.get('explanation'):
                print(f"Explanation: {result['explanation']}")
            if result.get('error'):
                print(f"⚠️  Warning: {result['error']}")
            if result.get('generated_code'):
                print(f"Generated Code: {result['generated_code'][:100]}...")
        else:
            print(f"❌ AI query failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ AI query failed: {e}")

def test_fallback_scenarios(session_id):
    """Test various fallback scenarios"""
    print(f"\n{'='*60}")
    print("Testing AI Fallback Scenarios")
    print(f"{'='*60}")
    
    # Test different types of queries
    test_queries = [
        ("What is the average salary?", "Basic aggregation"),
        ("How many people are in each department?", "Grouping query"),
        ("Who is the youngest employee?", "Min/max query"),
        ("What is the total salary for Engineering department?", "Filtered aggregation"),
        ("Show me employees earning more than 70000", "Conditional filtering"),
        ("What are the top 3 highest paid employees?", "Ranking query"),
        ("How many employees are in each city?", "Geographic analysis"),
        ("What is the salary distribution?", "Statistical analysis")
    ]
    
    for query, description in test_queries:
        print(f"\n--- {description} ---")
        test_ai_query(session_id, query, f" ({description})")

def test_api_documentation():
    """Test API documentation endpoint"""
    print(f"\n{'='*60}")
    print("Testing API Documentation")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
            print(f"Documentation URL: {BASE_URL}/docs")
        else:
            print(f"❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API documentation failed: {e}")

def main():
    """Run all Phase 2 tests with fallback testing"""
    print("🚀 Starting AI Data Agent Backend Tests - Phase 2 with Fallback")
    print("=" * 70)
    
    # Test health endpoints
    test_health_endpoint()
    test_api_health_endpoint()
    
    # Test file upload
    session_id = test_file_upload()
    
    # Test schema retrieval
    test_schema_endpoint(session_id)
    
    # Test API documentation
    test_api_documentation()
    
    # Test AI queries with fallback scenarios
    if session_id:
        test_fallback_scenarios(session_id)
    
    # Clean up test file
    if os.path.exists("test_data.csv"):
        os.remove("test_data.csv")
        print("\n✅ Test file cleaned up")
    
    print("\n" + "=" * 70)
    print("🏁 Phase 2 Fallback Tests completed")
    print("\n📋 Next Steps:")
    print("1. Update HUGGINGFACE_API_KEY in .env file")
    print("2. Update GEMINI_API_KEY in .env file (optional fallback)")
    print("3. Test with real API keys")
    print("4. Proceed to Phase 3: Frontend Implementation")

if __name__ == "__main__":
    main()
