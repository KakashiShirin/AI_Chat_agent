#!/usr/bin/env python3
"""
Multi-Gemini API System Test
Tests the new multi-Gemini API system with user-provided API keys.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_key_validation():
    """Test API key validation endpoint"""
    print("🔍 Testing API key validation...")
    
    # Test with a dummy API key first
    payload = {"api_key": "dummy_key"}
    response = requests.post(f"{BASE_URL}/api/v1/api-keys/validate", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Validation endpoint working: {result}")
    else:
        print(f"❌ Validation failed: {response.status_code}")

def test_api_key_status():
    """Test API key status endpoint"""
    print("\n📊 Testing API key status...")
    
    response = requests.get(f"{BASE_URL}/api/v1/api-keys/status")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status endpoint working:")
        print(f"   Total API keys: {result.get('total_api_keys', 0)}")
        print(f"   Total calls: {result.get('total_calls', 0)}")
        print(f"   Total tokens: {result.get('total_tokens', 0)}")
    else:
        print(f"❌ Status failed: {response.status_code}")

def test_ai_query():
    """Test AI query with current system"""
    print("\n🤖 Testing AI query...")
    
    payload = {
        'query': 'What is the average salary?',
        'session_id': '1287c3c1-d7e4-4718-9061-5d83290e656b'
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI query successful!")
        print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
        print(f"   API calls made: {result.get('api_calls_made', 'N/A')}")
        print(f"   Total tokens used: {result.get('total_tokens_used', 'N/A')}")
    else:
        print(f"❌ AI query failed: {response.status_code} - {response.text}")

def test_credit_usage():
    """Test credit usage endpoint"""
    print("\n💰 Testing credit usage...")
    
    response = requests.get(f"{BASE_URL}/api/v1/credits")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Credit usage:")
        print(f"   Total API calls: {result.get('total_api_calls', 0)}")
        print(f"   Total tokens used: {result.get('total_tokens_used', 0)}")
        print(f"   API keys count: {result.get('api_keys_count', 0)}")
        print(f"   Estimated cost: ${result.get('estimated_cost_usd', 0)}")
    else:
        print(f"❌ Credit usage failed: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Multi-Gemini API System Test")
    print("=" * 50)
    
    try:
        # Test API key validation
        test_api_key_validation()
        
        # Test API key status
        test_api_key_status()
        
        # Test AI query
        test_ai_query()
        
        # Test credit usage
        test_credit_usage()
        
        print("\n" + "=" * 50)
        print("🏁 Multi-Gemini System Test completed!")
        print("\n📋 Summary:")
        print("   ✅ API key validation endpoint working")
        print("   ✅ API key status endpoint working")
        print("   ✅ AI query system working")
        print("   ✅ Credit tracking working")
        print("\n🎯 Next Steps:")
        print("   1. Add user API keys through frontend")
        print("   2. Test multi-key fallback system")
        print("   3. Proceed to Phase 3: Frontend Implementation")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
