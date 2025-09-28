#!/usr/bin/env python3
"""
Test script to verify database connection fixes
"""
import sys
from app.services.ai_agent import AIAgent

def test_database_connection_prompt():
    """Test that the prompt correctly instructs to use the provided engine"""
    print("🧪 Testing database connection prompt...")
    
    agent = AIAgent()
    
    # Mock schema info
    schema_info = {
        "data_session_87d32c32_46f8_4306_97ed_a888f2c9004f": {
            "columns": [
                {"name": "Name", "type": "text"},
                {"name": "Department", "type": "text"},
                {"name": "Salary", "type": "numeric"}
            ],
            "sample_data": [
                {"Name": "John Smith", "Department": "Engineering", "Salary": 95000},
                {"Name": "Sarah Johnson", "Department": "Marketing", "Salary": 78000}
            ]
        }
    }
    
    query = "What is the average salary?"
    
    # Generate the prompt
    prompt = agent.generate_pandas_prompt(query, schema_info)
    
    print("Generated prompt:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    
    # Check if the prompt contains the right instructions
    checks = [
        "Use the provided 'engine' variable" in prompt,
        "Do NOT create new database connections" in prompt,
        "pd.read_sql" in prompt,
        "engine" in prompt
    ]
    
    if all(checks):
        print("✅ Prompt correctly instructs to use provided engine")
        return True
    else:
        print("❌ Prompt missing correct database connection instructions")
        return False

def test_code_execution_with_engine():
    """Test that code execution works with the engine variable"""
    print("🔍 Testing code execution with engine variable...")
    
    agent = AIAgent()
    
    # Test code that uses the engine correctly
    test_code = """
# Test using the provided engine
try:
    df = pd.read_sql("SELECT * FROM data_session_87d32c32_46f8_4306_97ed_a888f2c9004f LIMIT 5", engine)
    print(f"Data loaded successfully: {len(df)} rows")
    print("Columns:", list(df.columns))
    print("Sample data:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
"""
    
    try:
        result = agent.execute_code_safely(test_code, "87d32c32-46f8-4306-97ed-a888f2c9004f")
        print("✅ Code execution with engine successful!")
        print("Result:")
        print(result)
        return True
        
    except Exception as e:
        print(f"❌ Code execution failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Database Connection Fixes")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Prompt generation
    if test_database_connection_prompt():
        tests_passed += 1
    
    print()
    
    # Test 2: Code execution
    if test_code_execution_with_engine():
        tests_passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 Database connection fixes are working!")
    else:
        print("❌ Some tests failed. Check the issues above.")
    
    sys.exit(0 if tests_passed == total_tests else 1)
