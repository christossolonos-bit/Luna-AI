#!/usr/bin/env python3
"""
Luna OpenAI-Compatible API Startup Script
Starts the OpenAI-compatible API server for Luna AI
"""

import os
import sys
import json
import uvicorn
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install fastapi uvicorn")
        return False

def check_luna_core():
    """Check if Luna core is available"""
    try:
        from main import generate_luna_reply, get_luna_system_prompt
        print("✅ Luna core functionality available")
        return True
    except ImportError as e:
        print(f"⚠️ Luna core not available: {e}")
        print("The API will run but with limited functionality")
        return False

def load_config():
    """Load API configuration"""
    config_file = "openai_api_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✅ Configuration loaded from {config_file}")
            return config
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    # Default configuration
    return {
        "api": {
            "host": "0.0.0.0",
            "port": 8001,
            "title": "Luna OpenAI-Compatible API",
            "version": "1.0.0"
        }
    }

def start_api_server(config):
    """Start the OpenAI-compatible API server"""
    host = config["api"]["host"]
    port = config["api"]["port"]
    
    print(f"\n🚀 Starting Luna OpenAI-Compatible API Server...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print(f"📋 Models: http://{host}:{port}/v1/models")
    
    print(f"\n🌙 Available Models:")
    print(f"  • luna - General purpose conversational model")
    print(f"  • luna-chat - Optimized for chat conversations") 
    print(f"  • luna-gpt - GPT-style text completion")
    print(f"  • dciel/legion-v2.1-llama-70b@4bit - External API model")
    
    print(f"\n🔗 OpenAI-Compatible Base URL:")
    print(f"  • http://{host}:{port}")
    
    print(f"\n💡 Usage Examples:")
    print(f"  • OpenAI SDK: openai.api_base = 'http://{host}:{port}'")
    print(f"  • cURL: curl -X POST http://{host}:{port}/v1/chat/completions")
    print(f"  • LangChain: base_url='http://{host}:{port}'")
    
    print(f"\n🎯 Compatible with:")
    print(f"  • OpenAI Python SDK")
    print(f"  • LangChain")
    print(f"  • AutoGen")
    print(f"  • CrewAI")
    print(f"  • Any OpenAI-compatible client")
    
    print(f"\n" + "="*60)
    print(f"🌙 Luna OpenAI-Compatible API is starting...")
    print(f"="*60)
    
    try:
        uvicorn.run(
            "luna_openai_compat:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

def main():
    """Main startup function"""
    print("🌙 Luna OpenAI-Compatible API Startup")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Luna core
    check_luna_core()
    
    # Load configuration
    config = load_config()
    
    # Start server
    start_api_server(config)

if __name__ == "__main__":
    main()
