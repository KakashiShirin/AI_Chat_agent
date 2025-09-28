#!/usr/bin/env python3
"""
Fixed Hugging Face API Test Script
Tests the correct Inference API endpoint and models.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

def test_correct_inference_api():
    """Test the correct Hugging Face Inference API endpoint"""
    print("🔍 Testing Correct Hugging Face Inference API...")
    
    if not HF_API_KEY:
        print("❌ HUGGINGFACE_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {HF_API_KEY[:10]}...")
    
    # Test with a simple, reliable model
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test with microsoft/DialoGPT-medium (which we know exists)
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {
            "max_length": 50,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success! Response: {str(result)[:100]}...")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Unauthorized - Check API key")
            return False
        elif response.status_code == 404:
            print(f"   ❌ Model not found")
            return False
        elif response.status_code == 503:
            print(f"   ⚠️  Model loading - may need time to load")
            return False
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout - Model may be loading")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_working_models():
    """Test models that are known to work with Inference API"""
    print("\n🤖 Testing Known Working Models...")
    
    # Models that typically work with Inference API
    working_models = [
        "microsoft/DialoGPT-medium",
        "microsoft/DialoGPT-small", 
        "gpt2",
        "distilgpt2",
        "bigcode/starcoder",
        "Salesforce/codegen-350M-mono"
    ]
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    successful_models = []
    
    for model in working_models:
        print(f"\n--- Testing: {model} ---")
        
        payload = {
            "inputs": "Write Python code to calculate average:",
            "parameters": {
                "max_length": 100,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success! Response: {str(result)[:100]}...")
                successful_models.append(model)
            elif response.status_code == 503:
                print(f"   ⚠️  Model loading - {model} (may work after loading)")
                # Don't add to successful_models but don't mark as failed
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    return successful_models

def test_model_info():
    """Test getting model information"""
    print("\n📋 Testing Model Information...")
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    
    try:
        # Test getting info about a specific model
        response = requests.get(
            "https://huggingface.co/api/models/microsoft/DialoGPT-medium",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            model_info = response.json()
            print(f"✅ Model info retrieved:")
            print(f"   Model ID: {model_info.get('id', 'N/A')}")
            print(f"   Pipeline Tag: {model_info.get('pipeline_tag', 'N/A')}")
            print(f"   Downloads: {model_info.get('downloads', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to get model info: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception getting model info: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Fixed Hugging Face API Test")
    print("=" * 50)
    
    # Test basic connection
    if not test_correct_inference_api():
        print("\n❌ Basic API test failed")
        return
    
    # Test model info
    test_model_info()
    
    # Test working models
    successful_models = test_working_models()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    print(f"✅ Successful Models: {successful_models}")
    
    if successful_models:
        print("\n🎯 RECOMMENDATIONS:")
        print(f"   - Primary model: {successful_models[0]}")
        if len(successful_models) > 1:
            print(f"   - Fallback model: {successful_models[1]}")
        
        print("\n🔧 SUGGESTED FIXES FOR AI AGENT:")
        print("   1. Update model names in ai_agent.py")
        print("   2. Use correct Inference API endpoint")
        print("   3. Add proper error handling for 503 (model loading)")
        print("   4. Implement retry logic for model loading")
    else:
        print("\n❌ NO WORKING MODELS FOUND")
        print("🔧 TROUBLESHOOTING:")
        print("   1. Check API key validity")
        print("   2. Check internet connection")
        print("   3. Try different model names")
        print("   4. Check Hugging Face service status")

if __name__ == "__main__":
    main()
