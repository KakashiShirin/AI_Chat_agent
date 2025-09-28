#!/usr/bin/env python3
"""
Test script to debug DataVisualization issues
"""
import requests
import json
import sys

def test_schema_endpoint():
    """Test the schema endpoint directly"""
    print("🔍 Testing Schema Endpoint")
    print("=" * 50)
    
    # Test with a sample session ID
    test_session_id = "test-session-123"
    url = f"http://localhost:8000/api/v1/schema/{test_session_id}"
    
    try:
        print(f"📡 Testing URL: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response data:")
            print(json.dumps(data, indent=2))
            
            # Check if schema is properly structured
            if 'schema' in data:
                schema = data['schema']
                print(f"\n📋 Schema keys: {list(schema.keys())}")
                
                for table_name, table_info in schema.items():
                    print(f"  📊 Table: {table_name}")
                    print(f"    Columns: {len(table_info.get('columns', []))}")
                    print(f"    Sample data: {len(table_info.get('sample_data', []))}")
            else:
                print("❌ No 'schema' key in response")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Make sure to start the backend with: python start.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    test_health_endpoint()
    test_schema_endpoint()
    
    print("\n" + "=" * 50)
    print("💡 Debugging Tips:")
    print("1. Check if backend is running: python start.py")
    print("2. Check browser console for frontend errors")
    print("3. Check backend logs for API errors")
    print("4. Verify session ID is being passed correctly")
    print("5. Check if data was uploaded successfully")
    
    sys.exit(0)
