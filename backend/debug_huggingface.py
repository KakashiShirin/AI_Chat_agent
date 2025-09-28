#!/usr/bin/env python3
"""
Hugging Face API Debug Script
Tests different models and configurations to identify the issue.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HF_API_URL = "https://api-inference.huggingface.co/models"

def test_huggingface_connection():
    """Test basic connection to Hugging Face API"""
    print("🔍 Testing Hugging Face API Connection...")
    
    if not HF_API_KEY:
        print("❌ HUGGINGFACE_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {HF_API_KEY[:10]}...")
    return True

def test_model_access(model_name):
    """Test access to a specific model"""
    print(f"\n🤖 Testing model: {model_name}")
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {
            "max_length": 50,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(
            f"{HF_API_URL}/{model_name}",
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
            print(f"   ❌ Model not found - {model_name}")
            return False
        elif response.status_code == 503:
            print(f"   ⚠️  Model loading - {model_name} (may need time to load)")
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

def get_available_models():
    """Get list of available models from Hugging Face"""
    print("\n📋 Fetching available models...")
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    
    try:
        # Try to get model info
        response = requests.get(
            "https://huggingface.co/api/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models)} models")
            
            # Filter for text generation models
            text_models = [m for m in models if 'text-generation' in m.get('tags', [])]
            print(f"📝 Text generation models: {len(text_models)}")
            
            # Show some popular ones
            popular_models = [
                'gpt2', 'microsoft/DialoGPT-medium', 'bigcode/starcoder',
                'mistralai/Mixtral-8x7B-Instruct-v0.1', 'codellama/CodeLlama-34b-Instruct-hf'
            ]
            
            available_popular = []
            for model in popular_models:
                if any(m['id'] == model for m in text_models):
                    available_popular.append(model)
            
            print(f"🎯 Popular models available: {available_popular}")
            return available_popular
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Exception fetching models: {str(e)}")
        return []

def test_code_generation_models():
    """Test models specifically for code generation"""
    print("\n💻 Testing Code Generation Models...")
    
    code_models = [
        "bigcode/starcoder",
        "microsoft/CodeBERT-base", 
        "codellama/CodeLlama-34b-Instruct-hf",
        "bigcode/starcoder2",
        "Salesforce/codegen-350M-mono",
        "microsoft/DialoGPT-medium",
        "gpt2"
    ]
    
    working_models = []
    
    for model in code_models:
        if test_model_access(model):
            working_models.append(model)
    
    return working_models

def test_simple_models():
    """Test simple, reliable models"""
    print("\n🔧 Testing Simple Models...")
    
    simple_models = [
        "gpt2",
        "microsoft/DialoGPT-small",
        "distilgpt2"
    ]
    
    working_models = []
    
    for model in simple_models:
        if test_model_access(model):
            working_models.append(model)
    
    return working_models

def test_inference_api_status():
    """Test Hugging Face Inference API status"""
    print("\n🌐 Testing Inference API Status...")
    
    try:
        response = requests.get("https://api-inference.huggingface.co/status", timeout=10)
        print(f"Status API Response: {response.status_code}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Inference API Status: {status}")
        else:
            print(f"❌ Status API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Status API Exception: {str(e)}")

def main():
    """Main debug function"""
    print("🚀 Hugging Face API Debug Tool")
    print("=" * 50)
    
    # Test basic connection
    if not test_huggingface_connection():
        print("\n❌ Cannot proceed without valid API key")
        return
    
    # Test API status
    test_inference_api_status()
    
    # Test simple models first
    print("\n" + "=" * 50)
    working_simple = test_simple_models()
    
    # Test code generation models
    print("\n" + "=" * 50)
    working_code = test_code_generation_models()
    
    # Get available models
    print("\n" + "=" * 50)
    available_models = get_available_models()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEBUG SUMMARY")
    print("=" * 50)
    
    print(f"✅ Working Simple Models: {working_simple}")
    print(f"✅ Working Code Models: {working_code}")
    print(f"📋 Available Popular Models: {available_models}")
    
    if working_simple or working_code:
        print("\n🎯 RECOMMENDATIONS:")
        if working_simple:
            print(f"   - Use simple model: {working_simple[0]}")
        if working_code:
            print(f"   - Use code model: {working_code[0]}")
        
        print("\n🔧 SUGGESTED FIXES:")
        print("   1. Update model names in ai_agent.py")
        print("   2. Add fallback to working models")
        print("   3. Implement model health checks")
    else:
        print("\n❌ NO WORKING MODELS FOUND")
        print("🔧 TROUBLESHOOTING:")
        print("   1. Check API key validity")
        print("   2. Check internet connection")
        print("   3. Try different model names")
        print("   4. Check Hugging Face service status")

if __name__ == "__main__":
    main()
