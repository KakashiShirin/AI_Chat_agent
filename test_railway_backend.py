#!/usr/bin/env python3
"""
Test script to check Railway backend connectivity
"""
import requests
import sys

def test_backend_connection():
    """Test if Railway backend is accessible"""
    railway_url = "https://aichatagent-production.up.railway.app"
    
    print(f"🔍 Testing Railway backend: {railway_url}")
    
    try:
        # Test health endpoint
        health_url = f"{railway_url}/health"
        print(f"📡 Testing health endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Backend is running! Status: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Backend might be down")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Backend might be slow")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    railway_url = "https://aichatagent-production.up.railway.app"
    
    endpoints = [
        "/api/v1/health",
        "/api/v1/model/status",
        "/api/v1/api-keys/status"
    ]
    
    print(f"\n🔍 Testing API endpoints...")
    
    for endpoint in endpoints:
        try:
            url = f"{railway_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Railway Backend Connectivity Test")
    print("=" * 50)
    
    if test_backend_connection():
        test_api_endpoints()
        print("\n✅ Backend appears to be working!")
    else:
        print("\n❌ Backend is not accessible!")
        print("\nPossible issues:")
        print("1. Railway app might be sleeping (takes time to wake up)")
        print("2. Railway app might have crashed")
        print("3. Railway app might not be deployed correctly")
        print("4. Check Railway dashboard for logs")
    
    print("\n" + "=" * 50)
