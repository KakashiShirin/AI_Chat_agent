#!/usr/bin/env python3
"""
Test script to verify environment API key fallback
"""
import os
import sys
from app.services.ai_agent import AIAgent

def test_env_api_key_fallback():
    """Test that environment API key is used as fallback"""
    print("🔍 Testing environment API key fallback...")
    
    # Create AI agent instance
    agent = AIAgent()
    
    print(f"Environment API key available: {agent.env_api_key is not None}")
    print(f"Total API keys in pool: {len(agent.gemini_api_keys)}")
    
    if agent.env_api_key:
        print(f"Environment API key: {agent.env_api_key[:10]}...{agent.env_api_key[-4:]}")
        print("✅ Environment API key is loaded")
    else:
        print("❌ No environment API key found")
        return False
    
    # Test the fallback mechanism
    try:
        agent.ensure_env_api_key_available()
        print("✅ Environment API key fallback mechanism works")
        
        # Test a simple API call
        print("🧪 Testing API call...")
        response = agent._call_llm_api("Hello, this is a test. Please respond with 'Test successful'.")
        print(f"✅ API call successful: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_env_api_key_fallback()
    if success:
        print("\n🎉 Environment API key fallback is working correctly!")
    else:
        print("\n❌ Environment API key fallback test failed!")
    
    sys.exit(0 if success else 1)
