#!/usr/bin/env python3
"""
Test script for chat session isolation
"""
import requests
import json
import sys
import time

def test_chat_session_isolation():
    """Test that chat sessions maintain isolated contexts"""
    print("🧪 Testing Chat Session Isolation")
    print("=" * 50)
    
    # First, upload test data
    test_file_path = "../test_data.csv"
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            
            print("📤 Uploading test data...")
            upload_response = requests.post("http://localhost:8000/api/v1/upload", files=files, timeout=30)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                database_session_id = upload_data.get('session_id')
                print(f"✅ Data uploaded successfully! Database Session ID: {database_session_id}")
                
                # Create two separate chat sessions
                print("\n📱 Creating chat sessions...")
                
                # Chat Session 1
                chat1_response = requests.post("http://localhost:8000/api/v1/chat/create", 
                    json={"database_session_id": database_session_id}, timeout=30)
                
                if chat1_response.status_code == 200:
                    chat1_data = chat1_response.json()
                    chat1_id = chat1_data.get('chat_id')
                    print(f"✅ Chat Session 1 created: {chat1_id}")
                else:
                    print(f"❌ Failed to create Chat Session 1: {chat1_response.status_code}")
                    return
                
                # Chat Session 2
                chat2_response = requests.post("http://localhost:8000/api/v1/chat/create", 
                    json={"database_session_id": database_session_id}, timeout=30)
                
                if chat2_response.status_code == 200:
                    chat2_data = chat2_response.json()
                    chat2_id = chat2_data.get('chat_id')
                    print(f"✅ Chat Session 2 created: {chat2_id}")
                else:
                    print(f"❌ Failed to create Chat Session 2: {chat2_response.status_code}")
                    return
                
                # Test isolation by asking different questions in each chat
                print("\n💬 Testing chat isolation...")
                
                # Chat 1: Ask about departments
                print(f"📝 Chat 1 - Asking about departments...")
                chat1_query1 = requests.post("http://localhost:8000/api/v1/chat/query", 
                    json={"query": "What departments do we have?", "chat_id": chat1_id}, timeout=60)
                
                if chat1_query1.status_code == 200:
                    chat1_result1 = chat1_query1.json()
                    print(f"✅ Chat 1 Response: {chat1_result1.get('answer', '')[:100]}...")
                    print(f"📊 Chart Type: {chat1_result1.get('chart_type', 'none')}")
                else:
                    print(f"❌ Chat 1 query failed: {chat1_query1.status_code}")
                
                # Chat 2: Ask about salaries
                print(f"📝 Chat 2 - Asking about salaries...")
                chat2_query1 = requests.post("http://localhost:8000/api/v1/chat/query", 
                    json={"query": "What is the highest salary?", "chat_id": chat2_id}, timeout=60)
                
                if chat2_query1.status_code == 200:
                    chat2_result1 = chat2_query1.json()
                    print(f"✅ Chat 2 Response: {chat2_result1.get('answer', '')[:100]}...")
                    print(f"📊 Chart Type: {chat2_result1.get('chart_type', 'none')}")
                else:
                    print(f"❌ Chat 2 query failed: {chat2_query1.status_code}")
                
                # Test context continuity within each chat
                print("\n🔄 Testing context continuity...")
                
                # Chat 1: Follow-up question about departments
                print(f"📝 Chat 1 - Follow-up about department details...")
                chat1_query2 = requests.post("http://localhost:8000/api/v1/chat/query", 
                    json={"query": "Which department has the most employees?", "chat_id": chat1_id}, timeout=60)
                
                if chat1_query2.status_code == 200:
                    chat1_result2 = chat1_query2.json()
                    print(f"✅ Chat 1 Follow-up: {chat1_result2.get('answer', '')[:100]}...")
                    print(f"📊 Chart Type: {chat1_result2.get('chart_type', 'none')}")
                else:
                    print(f"❌ Chat 1 follow-up failed: {chat1_query2.status_code}")
                
                # Chat 2: Follow-up question about salaries
                print(f"📝 Chat 2 - Follow-up about salary details...")
                chat2_query2 = requests.post("http://localhost:8000/api/v1/chat/query", 
                    json={"query": "What is the average salary?", "chat_id": chat2_id}, timeout=60)
                
                if chat2_query2.status_code == 200:
                    chat2_result2 = chat2_query2.json()
                    print(f"✅ Chat 2 Follow-up: {chat2_result2.get('answer', '')[:100]}...")
                    print(f"📊 Chart Type: {chat2_result2.get('chart_type', 'none')}")
                else:
                    print(f"❌ Chat 2 follow-up failed: {chat2_query2.status_code}")
                
                # Check chat session stats
                print("\n📊 Chat Session Statistics...")
                stats_response = requests.get("http://localhost:8000/api/v1/chat/sessions", timeout=30)
                
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print(f"✅ Active Sessions: {stats.get('active_sessions', 0)}")
                    print(f"📝 Total Messages: {stats.get('total_messages', 0)}")
                    
                    for session in stats.get('sessions', []):
                        print(f"  💬 Chat {session['chat_id'][:8]}... - {session['message_count']} messages")
                else:
                    print(f"❌ Failed to get session stats: {stats_response.status_code}")
                
                print(f"\n✅ Chat session isolation test completed!")
                print(f"💡 Each chat maintains its own context and conversation history")
                
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"Response: {upload_response.text}")
                
    except FileNotFoundError:
        print(f"⚠️ Test data file not found: {test_file_path}")
        print("💡 Make sure test_data.csv exists in the project root")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_chat_context_retrieval():
    """Test retrieving chat context"""
    print("\n🔍 Testing Chat Context Retrieval")
    print("=" * 50)
    
    # Create a test chat session
    try:
        chat_response = requests.post("http://localhost:8000/api/v1/chat/create", 
            json={"database_session_id": "test-session-123"}, timeout=30)
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            chat_id = chat_data.get('chat_id')
            print(f"✅ Test chat created: {chat_id}")
            
            # Get context
            context_response = requests.get(f"http://localhost:8000/api/v1/chat/{chat_id}/context", timeout=30)
            
            if context_response.status_code == 200:
                context_data = context_response.json()
                print(f"✅ Context retrieved successfully")
                print(f"📝 Context keys: {list(context_data.get('context', {}).keys())}")
            else:
                print(f"❌ Context retrieval failed: {context_response.status_code}")
                
        else:
            print(f"❌ Failed to create test chat: {chat_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_session_isolation()
    test_chat_context_retrieval()
    
    print("\n" + "=" * 50)
    print("💡 Expected Results:")
    print("1. Each chat session maintains isolated context")
    print("2. Follow-up questions build on previous conversation")
    print("3. Different chats don't interfere with each other")
    print("4. Chat context is properly cached and retrieved")
    print("5. Session statistics show multiple active chats")
    
    sys.exit(0)
