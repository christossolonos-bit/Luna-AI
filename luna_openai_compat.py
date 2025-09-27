"""
Luna OpenAI-Compatible API Module
Provides OpenAI-compatible endpoints for Luna AI integration
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
import threading
from datetime import datetime

# External API Configuration
EXTERNAL_API_CONFIG = {
    "api_key": "sk-1f0bn5r_CTyIjbj1Bv5C0Q",
    "base_url": "https://ai.dcern.online/v1/completions",
    "model": "dciel/legion-v2.1-llama-70b@4bit"
}

# Import Luna's core functionality (optional fallback)
try:
    from main import generate_luna_reply, get_luna_system_prompt
    LUNA_CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Luna core not available: {e}")
    LUNA_CORE_AVAILABLE = False

# OpenAI-compatible models (using external API)
OPENAI_MODELS = {
    "luna": {
        "id": "luna",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "luna-ai"
    },
    "luna-chat": {
        "id": "luna-chat", 
        "object": "model",
        "created": int(time.time()),
        "owned_by": "luna-ai"
    },
    "luna-gpt": {
        "id": "luna-gpt",
        "object": "model", 
        "created": int(time.time()),
        "owned_by": "luna-ai"
    },
    "dciel/legion-v2.1-llama-70b@4bit": {
        "id": "dciel/legion-v2.1-llama-70b@4bit",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "external-api"
    }
}

# Pydantic models for OpenAI compatibility
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class ModelInfo(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: ChatUsage

class CompletionChoice(BaseModel):
    text: str
    index: int
    finish_reason: str

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: ChatUsage

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

# Initialize FastAPI app
app = FastAPI(
    title="Luna OpenAI-Compatible API",
    description="OpenAI-compatible endpoints for Luna AI",
    version="1.0.0"
)

def get_system_message():
    """Get Luna's system prompt"""
    if LUNA_CORE_AVAILABLE:
        try:
            return get_luna_system_prompt()
        except:
            return "You are Luna, a caring AI companion. Respond naturally and helpfully."
    return "You are Luna, a caring AI companion. Respond naturally and helpfully."

def generate_luna_response(messages: List[ChatMessage], user_id: str = "user") -> str:
    """Generate Luna response using external API"""
    try:
        # Convert messages to external API format
        api_messages = []
        for message in messages:
            if message.role == "system":
                # Add system message with Luna personality
                api_messages.append({
                    "role": "system",
                    "content": f"You are Luna, a caring AI companion. {message.content}"
                })
            elif message.role in ["user", "assistant"]:
                api_messages.append({
                    "role": message.role,
                    "content": message.content
                })
        
        # If no system message, add Luna's personality
        if not any(msg.get("role") == "system" for msg in api_messages):
            api_messages.insert(0, {
                "role": "system",
                "content": "You are Luna, a caring AI companion. Respond naturally and helpfully."
            })
        
        # Call external API
        response = requests.post(
            EXTERNAL_API_CONFIG["base_url"],
            headers={
                "Authorization": f"Bearer {EXTERNAL_API_CONFIG['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": EXTERNAL_API_CONFIG["model"],
                "messages": api_messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ Unexpected API response format: {data}")
                return "I'm having trouble thinking right now. Could you try again?"
        else:
            print(f"❌ External API error: {response.status_code} - {response.text}")
            return "I'm having trouble connecting to my AI brain right now. Could you try again?"
            
    except requests.exceptions.Timeout:
        print("❌ External API timeout")
        return "I'm taking too long to think. Could you try a shorter question?"
    except requests.exceptions.RequestException as e:
        print(f"❌ External API connection error: {e}")
        return "I'm having trouble connecting right now. Could you try again?"
    except Exception as e:
        print(f"❌ Luna generation error: {e}")
        return "I'm having trouble thinking right now. Could you try again?"

def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token)"""
    return len(text) // 4

# OpenAI-compatible endpoints

@app.get("/v1/models")
async def list_models():
    """List available models"""
    models = list(OPENAI_MODELS.values())
    return ModelsResponse(data=models)

@app.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get specific model info"""
    if model_id not in OPENAI_MODELS:
        raise HTTPException(status_code=404, detail="Model not found")
    return OPENAI_MODELS[model_id]

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """Create chat completion (OpenAI compatible)"""
    if request.model not in OPENAI_MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{request.model}' not found")
    
    # Generate response
    user_id = request.user or "user"
    response_text = generate_luna_response(request.messages, user_id)
    
    # Create response
    response_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
    created_time = int(time.time())
    
    # Estimate tokens
    prompt_tokens = sum(estimate_tokens(msg.content) for msg in request.messages)
    completion_tokens = estimate_tokens(response_text)
    
    if request.stream:
        # Streaming response
        def generate_stream():
            # Send initial chunk
            yield f"data: {json.dumps({'id': response_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': request.model, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
            
            # Stream the response word by word
            words = response_text.split()
            for i, word in enumerate(words):
                is_last = i == len(words) - 1
                chunk_data = {
                    'id': response_id,
                    'object': 'chat.completion.chunk',
                    'created': created_time,
                    'model': request.model,
                    'choices': [{
                        'index': 0,
                        'delta': {'content': word + (' ' if not is_last else '')},
                        'finish_reason': 'stop' if is_last else None
                    }]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                time.sleep(0.05)  # Small delay for streaming effect
            
            # Send final chunk
            yield f"data: {json.dumps({'id': response_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': request.model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    else:
        # Non-streaming response
        return ChatCompletionResponse(
            id=response_id,
            created=created_time,
            model=request.model,
            choices=[ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=response_text),
                finish_reason="stop"
            )],
            usage=ChatUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )

@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """Create text completion (OpenAI compatible)"""
    if request.model not in OPENAI_MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{request.model}' not found")
    
    # Generate response using external API
    try:
        response = requests.post(
            EXTERNAL_API_CONFIG["base_url"],
            headers={
                "Authorization": f"Bearer {EXTERNAL_API_CONFIG['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": EXTERNAL_API_CONFIG["model"],
                "prompt": f"You are Luna, a caring AI companion. {request.prompt}",
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 1000,
                "stream": request.stream or False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and data["choices"]:
                response_text = data["choices"][0]["text"]
            else:
                response_text = "I'm having trouble thinking right now. Could you try again?"
        else:
            response_text = "I'm having trouble connecting to my AI brain right now. Could you try again?"
            
    except Exception as e:
        print(f"❌ Completion API error: {e}")
        response_text = "I'm having trouble thinking right now. Could you try again?"
    
    # Create response
    response_id = f"cmpl-{uuid.uuid4().hex[:29]}"
    created_time = int(time.time())
    
    # Estimate tokens
    prompt_tokens = estimate_tokens(request.prompt)
    completion_tokens = estimate_tokens(response_text)
    
    if request.stream:
        # Streaming response
        def generate_stream():
            # Send initial chunk
            yield f"data: {json.dumps({'id': response_id, 'object': 'text_completion', 'created': created_time, 'model': request.model, 'choices': [{'index': 0, 'text': '', 'finish_reason': None}]})}\n\n"
            
            # Stream the response word by word
            words = response_text.split()
            for i, word in enumerate(words):
                is_last = i == len(words) - 1
                chunk_data = {
                    'id': response_id,
                    'object': 'text_completion',
                    'created': created_time,
                    'model': request.model,
                    'choices': [{
                        'index': 0,
                        'text': word + (' ' if not is_last else ''),
                        'finish_reason': 'stop' if is_last else None
                    }]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                time.sleep(0.05)  # Small delay for streaming effect
            
            # Send final chunk
            yield f"data: {json.dumps({'id': response_id, 'object': 'text_completion', 'created': created_time, 'model': request.model, 'choices': [{'index': 0, 'text': '', 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    else:
        # Non-streaming response
        return CompletionResponse(
            id=response_id,
            created=created_time,
            model=request.model,
            choices=[CompletionChoice(
                text=response_text,
                index=0,
                finish_reason="stop"
            )],
            usage=ChatUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test external API connection
    external_api_status = "unknown"
    try:
        test_response = requests.post(
            EXTERNAL_API_CONFIG["base_url"],
            headers={
                "Authorization": f"Bearer {EXTERNAL_API_CONFIG['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": EXTERNAL_API_CONFIG["model"],
                "prompt": "Hello",
                "max_tokens": 10
            },
            timeout=10
        )
        external_api_status = "healthy" if test_response.status_code == 200 else "error"
    except Exception as e:
        external_api_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy",
        "external_api": {
            "status": external_api_status,
            "base_url": EXTERNAL_API_CONFIG["base_url"],
            "model": EXTERNAL_API_CONFIG["model"]
        },
        "luna_core_available": LUNA_CORE_AVAILABLE,
        "models_available": len(OPENAI_MODELS),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Luna OpenAI-Compatible API",
        "version": "1.0.0",
        "description": "OpenAI-compatible endpoints for Luna AI",
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions",
            "completions": "/v1/completions",
            "health": "/health"
        },
        "models": list(OPENAI_MODELS.keys())
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "invalid_request_error",
                "code": exc.status_code
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "server_error",
                "code": 500
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Luna OpenAI-Compatible API Server...")
    print("📡 Available endpoints:")
    print("  • GET  /v1/models - List available models")
    print("  • GET  /v1/models/{model_id} - Get model info")
    print("  • POST /v1/chat/completions - Chat completions")
    print("  • POST /v1/completions - Text completions")
    print("  • GET  /health - Health check")
    print("  • GET  / - API information")
    print("\n🌙 Luna models available: luna, luna-chat, luna-gpt")
    print("🔗 OpenAI-compatible base URL: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
