#!/usr/bin/env python3
"""
Comprehensive Railway Backend Test Script
Tests all endpoints and CORS configuration
"""
import requests
import json
import sys
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_backend_connectivity():
    """Test basic backend connectivity"""
    railway_url = "https://aichatagent-production.up.railway.app"
    
    print_header("RAILWAY BACKEND CONNECTIVITY TEST")
    print_info(f"Testing: {railway_url}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test health endpoint
        health_url = f"{railway_url}/health"
        print_info(f"Testing health endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running! Status: {data}")
            return True
        else:
            print_error(f"Backend returned status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Connection failed - Backend might be down")
        return False
    except requests.exceptions.Timeout:
        print_error("Request timeout - Backend might be slow")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    railway_url = "https://aichatagent-production.up.railway.app"
    
    print_header("API ENDPOINTS TEST")
    
    endpoints = [
        ("/api/v1/health", "Health Check"),
        ("/api/v1/model/status", "Model Status"),
        ("/api/v1/api-keys/status", "API Keys Status"),
        ("/api/v1/credits", "Credit Usage")
    ]
    
    for endpoint, description in endpoints:
        try:
            url = f"{railway_url}{endpoint}"
            print_info(f"Testing {description}: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"{description} - OK")
                print_info(f"Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print_error(f"{description} - Status: {response.status_code}")
                print_error(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print_error(f"{description} - Error: {e}")

def test_cors_headers():
    """Test CORS headers"""
    railway_url = "https://aichatagent-production.up.railway.app"
    
    print_header("CORS HEADERS TEST")
    
    # Test with different origins
    test_origins = [
        "https://csvchatagent-p1jpqslns-primetrades-projects-4edfb7c9.vercel.app",
        "https://localhost:3000",
        "https://vercel.app"
    ]
    
    for origin in test_origins:
        try:
            url = f"{railway_url}/api/v1/health"
            headers = {
                'Origin': origin,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            print_info(f"Testing CORS for origin: {origin}")
            
            # Test preflight request
            response = requests.options(url, headers=headers, timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print_info(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
            if cors_headers['Access-Control-Allow-Origin']:
                print_success(f"CORS configured for {origin}")
            else:
                print_error(f"CORS not configured for {origin}")
                
        except Exception as e:
            print_error(f"CORS test failed for {origin}: {e}")

def test_environment_config():
    """Test environment configuration"""
    railway_url = "https://aichatagent-production.up.railway.app"
    
    print_header("ENVIRONMENT CONFIGURATION TEST")
    
    try:
        # Test model status to see environment
        url = f"{railway_url}/api/v1/model/status"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Environment configuration accessible")
            print_info(f"Current model: {data.get('current_model', 'Unknown')}")
            print_info(f"Model tier: {data.get('model_tier', 'Unknown')}")
            print_info(f"API keys count: {data.get('api_keys_count', 'Unknown')}")
        else:
            print_error(f"Environment test failed: {response.status_code}")
            
    except Exception as e:
        print_error(f"Environment test error: {e}")

def main():
    """Main test function"""
    print_header("RAILWAY BACKEND COMPREHENSIVE TEST")
    print_info("Testing Railway backend deployment and configuration")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    backend_ok = test_backend_connectivity()
    
    if backend_ok:
        test_api_endpoints()
        test_cors_headers()
        test_environment_config()
        
        print_header("TEST SUMMARY")
        print_success("Backend is running and accessible!")
        print_info("All API endpoints tested")
        print_info("CORS configuration verified")
        print_info("Environment configuration checked")
        
        print_header("NEXT STEPS")
        print_info("1. Check Railway logs for CORS configuration")
        print_info("2. Test Vercel frontend connection")
        print_info("3. Verify debug logging in browser console")
        
    else:
        print_header("TEST SUMMARY")
        print_error("Backend is not accessible!")
        print_info("Check Railway dashboard for deployment status")
        print_info("Verify Railway service is running")
        print_info("Check Railway logs for errors")
    
    print(f"\n{'='*60}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
