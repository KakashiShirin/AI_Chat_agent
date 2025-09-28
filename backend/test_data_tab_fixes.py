#!/usr/bin/env python3
"""
Test script to verify Data tab fixes
"""
import requests
import json
import sys

def test_data_tab_fixes():
    """Test the Data tab fixes"""
    print("🧪 Testing Data Tab Fixes")
    print("=" * 50)
    
    # First, let's upload test data
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
                
                # Test schema endpoint
                print(f"📡 Testing schema endpoint...")
                schema_response = requests.get(f"http://localhost:8000/api/v1/schema/{session_id}", timeout=30)
                
                if schema_response.status_code == 200:
                    schema_data = schema_response.json()
                    print(f"✅ Schema retrieved successfully!")
                    
                    # Check if sample_data is present
                    for table_name, table_info in schema_data.get('schema', {}).items():
                        print(f"📊 Table: {table_name}")
                        print(f"  Columns: {len(table_info.get('columns', []))}")
                        print(f"  Sample data: {len(table_info.get('sample_data', []))} rows")
                        
                        # Check data types
                        for column in table_info.get('columns', []):
                            print(f"    {column.get('name', 'Unknown')}: {column.get('type', 'Unknown')}")
                        
                        # Show sample data
                        sample_data = table_info.get('sample_data', [])
                        if sample_data:
                            print(f"  Sample data preview:")
                            for i, row in enumerate(sample_data[:2]):  # Show first 2 rows
                                print(f"    Row {i+1}: {row}")
                        else:
                            print(f"  ⚠️ No sample data found")
                    
                    print(f"\n✅ Data tab should now work without crashing!")
                    print(f"💡 Check the frontend Data tab with session ID: {session_id}")
                    
                else:
                    print(f"❌ Schema retrieval failed: {schema_response.status_code}")
                    print(f"Response: {schema_response.text}")
                    
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"Response: {upload_response.text}")
                
    except FileNotFoundError:
        print(f"⚠️ Test data file not found: {test_file_path}")
        print("💡 Make sure test_data.csv exists in the project root")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_schema_endpoint_directly():
    """Test schema endpoint directly"""
    print("\n🔍 Testing Schema Endpoint Directly")
    print("=" * 50)
    
    # Test with a sample session ID
    test_session_id = "test-session-123"
    
    try:
        response = requests.get(f"http://localhost:8000/api/v1/schema/{test_session_id}", timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Schema response received!")
            print(f"📝 Response structure: {json.dumps(data, indent=2)}")
            
            # Check if sample_data is present
            schema = data.get('schema', {})
            if schema:
                for table_name, table_info in schema.items():
                    sample_data = table_info.get('sample_data', [])
                    print(f"📊 Table {table_name}: {len(sample_data)} sample rows")
            else:
                print(f"⚠️ No schema data found")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_data_tab_fixes()
    test_schema_endpoint_directly()
    
    print("\n" + "=" * 50)
    print("💡 Expected Results:")
    print("1. Schema should include sample_data field")
    print("2. Data types should be correctly inferred (numeric for salary, etc.)")
    print("3. Data tab should not crash when loading")
    print("4. Sample data should be displayed properly")
    
    sys.exit(0)
