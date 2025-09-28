#!/usr/bin/env python3
"""
Test script to verify code execution fixes
"""
import sys
from app.services.ai_agent import AIAgent

def test_code_execution():
    """Test that code execution works with exception handling"""
    print("🧪 Testing code execution with exception handling...")
    
    agent = AIAgent()
    
    # Test code that uses exception handling
    test_code = """
try:
    import tabulate
    print("tabulate imported successfully")
    
    # Test basic functionality
    data = [['Name', 'Age'], ['John', 25], ['Jane', 30]]
    table = tabulate.tabulate(data, headers='firstrow', tablefmt='grid')
    print("Table created successfully:")
    print(table)
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")
"""
    
    try:
        result = agent.execute_code_safely(test_code, "test_session")
        print("✅ Code execution successful!")
        print("Result:")
        print(result)
        return True
        
    except Exception as e:
        print(f"❌ Code execution failed: {e}")
        return False

def test_exception_classes():
    """Test that exception classes are available"""
    print("🔍 Testing exception classes availability...")
    
    agent = AIAgent()
    
    test_code = """
# Test that exception classes are available
print("Testing exception classes...")

try:
    raise ValueError("Test error")
except ValueError as e:
    print(f"Caught ValueError: {e}")

try:
    raise ImportError("Test import error")
except ImportError as e:
    print(f"Caught ImportError: {e}")

try:
    raise Exception("Test general exception")
except Exception as e:
    print(f"Caught Exception: {e}")

print("All exception classes work correctly!")
"""
    
    try:
        result = agent.execute_code_safely(test_code, "test_session")
        print("✅ Exception classes test successful!")
        print("Result:")
        print(result)
        return True
        
    except Exception as e:
        print(f"❌ Exception classes test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Code Execution Fixes")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Code execution with tabulate
    if test_code_execution():
        tests_passed += 1
    
    print()
    
    # Test 2: Exception classes
    if test_exception_classes():
        tests_passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All code execution fixes are working!")
    else:
        print("❌ Some tests failed. Check the issues above.")
    
    sys.exit(0 if tests_passed == total_tests else 1)
