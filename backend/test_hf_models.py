#!/usr/bin/env python3
"""
Hugging Face Model Availability Test
Tests which models are actually available without making expensive API calls.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

def test_model_availability():
    """Test which models are available without making expensive calls"""
    print("🔍 Testing Hugging Face Model Availability...")
    
    if not HF_API_KEY:
        print("❌ HUGGINGFACE_API_KEY not found")
        return
    
    headers = {'Authorization': f'Bearer {HF_API_KEY}'}
    
    # Test models with minimal requests
    models_to_test = [
        "microsoft/DialoGPT-medium",
        "gpt2", 
        "distilgpt2",
        "EleutherAI/gpt-neo-125M",
        "microsoft/DialoGPT-small"
    ]
    
    working_models = []
    
    for model in models_to_test:
        print(f"\n--- Testing {model} ---")
        
        # Very minimal payload to avoid wasting credits
        payload = {
            "inputs": "Hi",
            "parameters": {
                "max_new_tokens": 5,  # Very short response
                "temperature": 0.1
            }
        }
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS! Response: {str(result)[:50]}...")
                working_models.append(model)
            elif response.status_code == 503:
                print(f"⚠️  Model loading (may work later)")
            elif response.status_code == 401:
                print(f"❌ Unauthorized")
            elif response.status_code == 404:
                print(f"❌ Model not found")
            else:
                print(f"❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Working models: {working_models}")
    
    if working_models:
        print(f"\n🎯 RECOMMENDATION:")
        print(f"   Use primary model: {working_models[0]}")
        if len(working_models) > 1:
            print(f"   Use fallback model: {working_models[1]}")
    else:
        print(f"\n❌ NO WORKING MODELS FOUND")
        print(f"   Recommendation: Use Gemini as primary LLM")

if __name__ == "__main__":
    test_model_availability()
