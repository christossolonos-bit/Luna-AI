# test_graphiti_integration.py
"""
Test script for Luna's Graphiti integration
"""

import sqlite3
from luna_graphiti_integration import LunaGraphitiIntegration

def test_graphiti_integration():
    """Test the Graphiti integration with Luna's memory database"""
    
    print("🧪 Testing Luna Graphiti Integration...")
    
    # Initialize Graphiti integration
    integration = LunaGraphitiIntegration()
    
    if not integration.is_initialized:
        print("❌ Graphiti integration failed to initialize")
        return False
    
    print("✅ Graphiti integration initialized successfully")
    
    # Test conversation extraction
    print("\n📊 Testing conversation extraction...")
    conversations = integration.extract_conversations_from_db(limit=10)
    print(f"✅ Extracted {len(conversations)} conversations from database")
    
    if conversations:
        print(f"📝 Sample conversation: {conversations[0]['user_message'][:50]}...")
    
    # Test Graphiti search
    print("\n🔍 Testing Graphiti search...")
    search_results = integration.search_graphiti_memories("hello", limit=3)
    print(f"✅ Graphiti search returned {len(search_results)} results")
    
    if search_results:
        print(f"📝 Sample result: {search_results[0]['content'][:100]}...")
    
    # Test insights
    print("\n📈 Testing insights...")
    insights = integration.get_conversation_insights()
    print(f"✅ Got insights: {insights}")
    
    print("\n🎉 Graphiti integration test completed successfully!")
    return True

if __name__ == "__main__":
    test_graphiti_integration()
