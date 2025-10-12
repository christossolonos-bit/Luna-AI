#!/usr/bin/env python3
import requests
import json
import time

def test_ollama_speed():
    """Test Ollama response speed with different configurations"""
    
    # Test 1: Minimal prompt
    print("Test 1: Minimal prompt")
    start_time = time.time()
    response = requests.post(
        "http://127.0.0.1:11434/api/chat",
        json={
            "model": "mistral:7b",
            "messages": [{"role": "user", "content": "Say hi"}],
            "options": {"num_predict": 10, "temperature": 0.7},
            "stream": False
        },
        timeout=10
    )
    end_time = time.time()
    print(f"Response time: {end_time - start_time:.2f}s")
    try:
        response_json = response.json()
        print(f"Response: {response_json['message']['content']}")
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Raw response: {response.text[:200]}...")
    
    # Test 2: Medium prompt
    print("\nTest 2: Medium prompt")
    medium_prompt = "You are Luna, a tsundere AI assistant. Respond briefly to: Hello"
    start_time = time.time()
    response = requests.post(
        "http://127.0.0.1:11434/api/chat",
        json={
            "model": "mistral:7b",
            "messages": [{"role": "user", "content": medium_prompt}],
            "options": {"num_predict": 50, "temperature": 0.8}
        },
        timeout=10
    )
    end_time = time.time()
    print(f"Response time: {end_time - start_time:.2f}s")
    print(f"Response: {response.json()['message']['content']}")
    
    # Test 3: Optimized GUI prompt (simulate new Luna config)
    print("\nTest 3: Optimized GUI prompt (new Luna config)")
    optimized_prompt = "You are Luna, a tsundere AI assistant. Respond briefly to: Hello"
    start_time = time.time()
    response = requests.post(
        "http://127.0.0.1:11434/api/chat",
        json={
            "model": "mistral:7b",
            "messages": [{"role": "user", "content": optimized_prompt}],
            "options": {"num_predict": 100, "temperature": 0.6, "top_p": 0.7, "top_k": 40}
        },
        timeout=10
    )
    end_time = time.time()
    print(f"Response time: {end_time - start_time:.2f}s")
    try:
        response_json = response.json()
        print(f"Response: {response_json['message']['content']}")
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Raw response: {response.text[:200]}...")

if __name__ == "__main__":
    test_ollama_speed()
