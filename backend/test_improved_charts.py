#!/usr/bin/env python3
"""
Test script for improved chart generation
"""
import requests
import json
import sys

def test_chart_generation():
    """Test the improved chart generation with a complex query"""
    print("🧪 Testing Improved Chart Generation")
    print("=" * 50)
    
    # Test query similar to what the user asked
    test_query = "describe the dataset and give me a spread of the various departments using a graph and what are the no. of unique cities per department"
    
    # We need a real session ID with data
    # Let's first check what sessions exist
    print("📡 Checking available sessions...")
    
    # For now, let's test with a mock query to see the improved logging
    url = "http://localhost:8000/api/v1/query"
    
    payload = {
        "query": test_query,
        "session_id": "test-session-123"  # This might not have data, but we can see the improved logging
    }
    
    try:
        print(f"📡 Testing query: {test_query}")
        print(f"📊 Session ID: {payload['session_id']}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received!")
            print(f"📝 Answer: {data.get('answer', 'No answer')[:200]}...")
            print(f"📊 Chart Type: {data.get('chart_type', 'none')}")
            print(f"📈 Chart Data: {data.get('chart_data', 'None')}")
            print(f"🔢 API Calls Made: {data.get('api_calls_made', 0)}")
            print(f"🎯 Total Tokens: {data.get('total_tokens_used', 0)}")
            
            if data.get('chart_data'):
                print(f"🎉 Chart data generated successfully!")
            else:
                print(f"⚠️ No chart data generated")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Make sure to start the backend with: python start.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_real_data():
    """Test with actual uploaded data if available"""
    print("\n🔍 Testing with Real Data")
    print("=" * 50)
    
    # First, let's try to upload the test data
    test_file_path = "../test_data.csv"
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            
            print("📤 Uploading test data...")
            upload_response = requests.post("http://localhost:8000/api/v1/upload", files=files, timeout=30)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                session_id = upload_data.get('session_id')
                print(f"✅ Data uploaded successfully! Session ID: {session_id}")
                
                # Now test the complex query
                test_query = "describe the dataset and give me a spread of the various departments using a graph and what are the no. of unique cities per department"
                
                payload = {
                    "query": test_query,
                    "session_id": session_id
                }
                
                print(f"📡 Testing complex query with real data...")
                query_response = requests.post("http://localhost:8000/api/v1/query", json=payload, timeout=60)
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    print(f"✅ Complex query processed!")
                    print(f"📝 Answer: {data.get('answer', 'No answer')}")
                    print(f"📊 Chart Type: {data.get('chart_type', 'none')}")
                    
                    if data.get('chart_data'):
                        print(f"🎉 Chart data: {json.dumps(data['chart_data'], indent=2)}")
                    else:
                        print(f"⚠️ No chart data generated")
                        
                else:
                    print(f"❌ Query failed: {query_response.status_code}")
                    print(f"Response: {query_response.text}")
                    
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"Response: {upload_response.text}")
                
    except FileNotFoundError:
        print(f"⚠️ Test data file not found: {test_file_path}")
        print("💡 Make sure test_data.csv exists in the project root")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chart_generation()
    test_with_real_data()
    
    print("\n" + "=" * 50)
    print("💡 Next Steps:")
    print("1. Check backend logs for detailed chart generation process")
    print("2. Verify that the synthesis prompt is working correctly")
    print("3. Test with real data to see chart generation in action")
    print("4. Check frontend to see if charts are displayed properly")
    
    sys.exit(0)
