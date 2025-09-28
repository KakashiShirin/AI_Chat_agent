#!/usr/bin/env python3
"""
Test script to validate Gemini API key
"""
import google.generativeai as genai
import sys

def test_gemini_api_key(api_key):
    """Test if a Gemini API key is valid"""
    try:
        print(f"Testing API key: {api_key[:10]}...{api_key[-4:]}")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Try to create a model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Try a simple test
        response = model.generate_content("Hello, this is a test.")
        
        print("✅ API key is valid!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ API key validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_gemini_key.py <API_KEY>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    success = test_gemini_api_key(api_key)
    sys.exit(0 if success else 1)
