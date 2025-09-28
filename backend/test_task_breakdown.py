#!/usr/bin/env python3
"""
Test script for the new task breakdown system
"""
import requests
import json
import sys

def test_task_breakdown():
    """Test the new task breakdown system with a complex query"""
    print("🧪 Testing Task Breakdown System")
    print("=" * 50)
    
    # Test query similar to what the user asked
    test_query = """Hi. From the dataset, I would like to get info on following data:
1. general description of what the dataset is about
2. piechart of department population spread
3. highest salary
4. which department has the most amount of people from seattle"""
    
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
                
                # Now test the complex query with task breakdown
                payload = {
                    "query": test_query,
                    "session_id": session_id
                }
                
                print(f"📡 Testing complex query with task breakdown...")
                print(f"📝 Query: {test_query[:100]}...")
                
                query_response = requests.post("http://localhost:8000/api/v1/query", json=payload, timeout=120)
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    print(f"✅ Complex query processed with task breakdown!")
                    print(f"📝 Answer: {data.get('answer', 'No answer')[:200]}...")
                    print(f"📊 Chart Type: {data.get('chart_type', 'none')}")
                    print(f"🔢 API Calls Made: {data.get('api_calls_made', 0)}")
                    print(f"🎯 Total Tokens: {data.get('total_tokens_used', 0)}")
                    
                    # Check if tasks were processed
                    tasks = data.get('tasks', [])
                    print(f"📋 Tasks Processed: {len(tasks)}")
                    
                    for i, task in enumerate(tasks):
                        print(f"  📝 Task {i+1}: {task.get('description', 'No description')}")
                        print(f"    Answer: {task.get('answer', 'No answer')[:100]}...")
                        print(f"    Chart: {task.get('chart_type', 'none')}")
                        if task.get('error'):
                            print(f"    Error: {task['error']}")
                    
                    if data.get('chart_data'):
                        print(f"🎉 Chart data generated successfully!")
                        chart_data = data['chart_data']
                        if isinstance(chart_data, dict) and 'data' in chart_data:
                            labels = chart_data['data'].get('labels', [])
                            datasets = chart_data['data'].get('datasets', [])
                            if datasets and len(datasets) > 0:
                                data_values = datasets[0].get('data', [])
                                print(f"📊 Chart labels: {labels}")
                                print(f"📊 Chart data: {data_values}")
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

def test_simple_query():
    """Test with a simple query to ensure it still works"""
    print("\n🔍 Testing Simple Query")
    print("=" * 50)
    
    # Test with a simple query
    simple_query = "What is the highest salary?"
    
    # Use a test session (this might not have data, but we can see the behavior)
    payload = {
        "query": simple_query,
        "session_id": "test-session-123"
    }
    
    try:
        print(f"📡 Testing simple query: {simple_query}")
        response = requests.post("http://localhost:8000/api/v1/query", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simple query processed!")
            print(f"📝 Answer: {data.get('answer', 'No answer')}")
            print(f"📊 Chart Type: {data.get('chart_type', 'none')}")
            
            tasks = data.get('tasks', [])
            print(f"📋 Tasks Processed: {len(tasks)}")
            
        else:
            print(f"❌ Simple query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing simple query: {e}")

if __name__ == "__main__":
    test_task_breakdown()
    test_simple_query()
    
    print("\n" + "=" * 50)
    print("💡 Expected Results:")
    print("1. Complex queries should be broken down into individual tasks")
    print("2. Each task should be processed separately")
    print("3. Charts should be generated for visualization tasks")
    print("4. Simple queries should still work normally")
    print("5. Multiple responses should be combined into one comprehensive answer")
    
    sys.exit(0)
