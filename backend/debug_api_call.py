#!/usr/bin/env python3
"""
Debug script to test the exact API call the application makes
"""
import google.generativeai as genai
import sys

def test_application_api_call(api_key):
    """Test the exact API call the application makes"""
    try:
        print(f"Testing API key: {api_key[:10]}...{api_key[-4:]}")
        
        # Configure exactly like the application
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test with a simple prompt like the application would use
        prompt = "Generate Python code to analyze this data and answer: what is the data about"
        
        print("Calling generate_content...")
        response = model.generate_content(prompt)
        
        print("✅ API call successful!")
        print(f"Response: {response.text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_api_call.py <API_KEY>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    success = test_application_api_call(api_key)
    sys.exit(0 if success else 1)
