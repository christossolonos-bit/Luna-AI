#!/usr/bin/env python3
"""
Luna OpenAI-Compatible API Usage Examples
Demonstrates how to use Luna with various OpenAI-compatible clients
"""

import requests
import json
import time

# API Configuration
API_BASE = "http://localhost:8001"
API_KEY = "luna-api-key"  # Any key works with Luna

def example_openai_sdk():
    """Example using OpenAI Python SDK"""
    try:
        import openai
        
        # Configure OpenAI client to use Luna
        openai.api_base = API_BASE
        openai.api_key = API_KEY
        
        print("🤖 OpenAI SDK Example:")
        
        # Chat completion
        response = openai.ChatCompletion.create(
            model="luna-chat",
            messages=[
                {"role": "user", "content": "Hello Luna! How are you today?"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"Response: {response.choices[0].message.content}")
        
    except ImportError:
        print("❌ OpenAI SDK not installed. Install with: pip install openai")
    except Exception as e:
        print(f"❌ OpenAI SDK example failed: {e}")

def example_requests():
    """Example using requests library"""
    print("\n🌐 Requests Library Example:")
    
    try:
        # Chat completion
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "luna-chat",
                "messages": [
                    {"role": "user", "content": "Tell me a short story about a robot"}
                ],
                "temperature": 0.8,
                "max_tokens": 300
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['choices'][0]['message']['content']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Requests example failed: {e}")

def example_streaming():
    """Example using streaming responses"""
    print("\n📡 Streaming Example:")
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "luna-gpt",
                "messages": [
                    {"role": "user", "content": "Write a poem about AI"}
                ],
                "stream": True,
                "temperature": 0.9
            },
            stream=True
        )
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and data['choices']:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(delta['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
            print()  # New line after streaming
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Streaming example failed: {e}")

def example_text_completion():
    """Example using text completion endpoint"""
    print("\n📝 Text Completion Example:")
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "luna-gpt",
                "prompt": "The future of AI is",
                "temperature": 0.7,
                "max_tokens": 200
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['choices'][0]['text']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Text completion example failed: {e}")

def example_list_models():
    """Example listing available models"""
    print("\n📋 List Models Example:")
    
    try:
        response = requests.get(
            f"{API_BASE}/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Available models:")
            for model in data['data']:
                print(f"  • {model['id']} - {model['owned_by']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ List models example failed: {e}")

def example_health_check():
    """Example health check"""
    print("\n🏥 Health Check Example:")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Luna Core Available: {data['luna_core_available']}")
            print(f"Models Available: {data['models_available']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def main():
    """Run all examples"""
    print("🌙 Luna OpenAI-Compatible API Examples")
    print("="*50)
    print(f"API Base URL: {API_BASE}")
    print("Make sure the Luna API server is running!")
    print()
    
    # Run examples
    example_health_check()
    example_list_models()
    example_requests()
    example_text_completion()
    example_streaming()
    example_openai_sdk()
    
    print("\n✅ All examples completed!")
    print("\n💡 Tips:")
    print("  • Use any API key - Luna doesn't require authentication")
    print("  • All models (luna, luna-chat, luna-gpt) work the same")
    print("  • Streaming is supported for real-time responses")
    print("  • Compatible with OpenAI SDK, LangChain, AutoGen, etc.")

if __name__ == "__main__":
    main()
