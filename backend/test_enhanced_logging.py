#!/usr/bin/env python3
"""
Test script to demonstrate enhanced logging
"""
import sys
import time
from app.services.ai_agent import AIAgent

def test_enhanced_logging():
    """Test the enhanced logging functionality"""
    print("🧪 Testing Enhanced Logging System")
    print("=" * 60)
    
    agent = AIAgent()
    
    # Test with a simple query
    test_query = "What is the average salary?"
    test_session = "test-session-123"
    
    print(f"📝 Test Query: {test_query}")
    print(f"🆔 Test Session: {test_session}")
    print("\n🔍 Watch the detailed logs below:")
    print("-" * 60)
    
    try:
        # This will trigger all the enhanced logging
        result = agent.get_answer(test_query, test_session)
        
        print("-" * 60)
        print("📊 Test Results:")
        print(f"✅ Success: {'error' not in result}")
        print(f"📝 Answer Length: {len(result.get('answer', ''))}")
        print(f"🔢 API Calls Made: {result.get('api_calls_made', 0)}")
        print(f"💰 Tokens Used: {result.get('total_tokens_used', 0)}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Answer: {result.get('answer', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_logging()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Enhanced logging test completed!")
        print("📁 Check 'ai_agent_detailed.log' for complete logs")
    else:
        print("❌ Enhanced logging test failed!")
    
    print("\n💡 Logging Features Demonstrated:")
    print("✅ Colored console output")
    print("✅ Detailed file logging")
    print("✅ Query start/end markers")
    print("✅ API call tracking")
    print("✅ Code execution logging")
    print("✅ Performance timing")
    print("✅ Error categorization")
    
    sys.exit(0 if success else 1)
