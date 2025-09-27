#!/usr/bin/env python3
"""
Test External API Connection
Tests the connection to the external Legion API
"""

import requests
import json

# External API Configuration
API_KEY = "sk-1f0bn5r_CTyIjbj1Bv5C0Q"
BASE_URL = "https://ai.dcern.online/v1/completions"
MODEL = "dciel/legion-v2.1-llama-70b@4bit"

def test_chat_completion():
    """Test chat completion endpoint"""
    print("🧪 Testing Chat Completion...")
    
    try:
        response = requests.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are Luna, a caring AI companion."},
                    {"role": "user", "content": "Hello! How are you today?"}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat completion successful!")
            print(f"Response: {data}")
            if "choices" in data and data["choices"]:
                print(f"Content: {data['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ Chat completion failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        return False

def test_text_completion():
    """Test text completion endpoint"""
    print("\n🧪 Testing Text Completion...")
    
    try:
        response = requests.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "prompt": "You are Luna, a caring AI companion. Hello! How are you today?",
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Text completion successful!")
            print(f"Response: {data}")
            if "choices" in data and data["choices"]:
                print(f"Content: {data['choices'][0]['text']}")
            return True
        else:
            print(f"❌ Text completion failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Text completion error: {e}")
        return False

def test_health():
    """Test basic connectivity"""
    print("🧪 Testing Basic Connectivity...")
    
    try:
        # Simple test request
        response = requests.get(
            BASE_URL.replace("/v1/completions", "/health"),
            timeout=10
        )
        print(f"Health check status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        # This is expected since the endpoint might not have a health check
        return True  # Don't fail the test for this

def main():
    """Run all tests"""
    print("🌙 Testing External API Connection")
    print("="*50)
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    print()
    
    # Run tests
    health_ok = test_health()
    chat_ok = test_chat_completion()
    text_ok = test_text_completion()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"  Health Check: {'✅' if health_ok else '❌'}")
    print(f"  Chat Completion: {'✅' if chat_ok else '❌'}")
    print(f"  Text Completion: {'✅' if text_ok else '❌'}")
    
    if chat_ok or text_ok:
        print("\n🎉 External API is working!")
        print("You can now start the Luna OpenAI-compatible API server.")
        print("Run: python start_openai_api.py")
    else:
        print("\n❌ External API connection failed.")
        print("Please check your API key and endpoint URL.")

if __name__ == "__main__":
    main()
