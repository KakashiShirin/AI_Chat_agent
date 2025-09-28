#!/usr/bin/env python3
"""
Test script to verify the new chat response format
"""
import sys
from app.services.ai_agent import AIAgent

def test_new_response_format():
    """Test the new chat-friendly response format"""
    print("🧪 Testing New Chat Response Format")
    print("=" * 60)
    
    agent = AIAgent()
    
    # Test queries that should generate different response types
    test_queries = [
        "What is the average salary?",
        "How many employees are in each department?",
        "What departments exist in the data?",
        "Show me the salary distribution"
    ]
    
    test_session = "test-session-123"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            result = agent.get_answer(query, test_session)
            
            print(f"✅ Response Type: {'Error' if 'error' in result else 'Success'}")
            print(f"📝 Answer: {result.get('answer', '')[:100]}...")
            print(f"📊 Chart Type: {result.get('chart_type', 'none')}")
            print(f"📈 Chart Data: {'Present' if result.get('chart_data') else 'None'}")
            
            if result.get('chart_data'):
                print(f"🔍 Chart Data Type: {type(result['chart_data']).__name__}")
                if isinstance(result['chart_data'], dict):
                    print(f"🔍 Chart Data Keys: {list(result['chart_data'].keys())}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 New response format test completed!")
    print("\n💡 Expected Improvements:")
    print("✅ Chat-friendly responses (no JSON)")
    print("✅ Actual chart data generation")
    print("✅ Better chart suggestions")
    print("✅ Cleaner frontend display")

if __name__ == "__main__":
    test_new_response_format()
    sys.exit(0)
