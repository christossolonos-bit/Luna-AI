# 🌙 Luna OpenAI-Compatible API

A complete OpenAI-compatible API wrapper for Luna AI, allowing seamless integration with any OpenAI-compatible client, framework, or library.

## 🚀 Features

- **100% OpenAI Compatible** - Works with OpenAI Python SDK, LangChain, AutoGen, CrewAI
- **Multiple Models** - `luna`, `luna-chat`, `luna-gpt` models available
- **Streaming Support** - Real-time streaming responses
- **Chat & Text Completions** - Both chat and completion endpoints
- **Health Monitoring** - Built-in health checks and monitoring
- **Error Handling** - Comprehensive error handling and logging
- **No Authentication** - Simple setup, no API keys required

## 📦 Installation

1. **Install Dependencies:**
```bash
pip install fastapi uvicorn requests
```

2. **Start the API Server:**
```bash
python start_openai_api.py
```

3. **Test the API:**
```bash
python openai_api_examples.py
```

## 🔧 Quick Start

### Using OpenAI Python SDK

```python
import openai

# Configure to use Luna
openai.api_base = "http://localhost:8001"
openai.api_key = "luna-api-key"  # Any key works

# Chat with Luna
response = openai.ChatCompletion.create(
    model="luna-chat",
    messages=[{"role": "user", "content": "Hello Luna!"}],
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Using Requests Library

```python
import requests

response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    headers={"Authorization": "Bearer luna-api-key"},
    json={
        "model": "luna-chat",
        "messages": [{"role": "user", "content": "Hello Luna!"}],
        "temperature": 0.7
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

### Using LangChain

```python
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# For chat models
llm = ChatOpenAI(
    model_name="luna-chat",
    openai_api_base="http://localhost:8001",
    openai_api_key="luna-api-key"
)

# For text completion
llm = OpenAI(
    model_name="luna-gpt",
    openai_api_base="http://localhost:8001",
    openai_api_key="luna-api-key"
)
```

## 📡 API Endpoints

### Models
- `GET /v1/models` - List available models
- `GET /v1/models/{model_id}` - Get model information

### Chat Completions
- `POST /v1/chat/completions` - Create chat completion
- Supports streaming with `"stream": true`

### Text Completions
- `POST /v1/completions` - Create text completion
- Supports streaming with `"stream": true`

### Health & Info
- `GET /health` - Health check endpoint
- `GET /` - API information
- `GET /docs` - Interactive API documentation

## 🤖 Available Models

| Model ID | Description | Max Tokens |
|----------|-------------|------------|
| `luna` | General purpose conversational model | 1000 |
| `luna-chat` | Optimized for chat conversations | 1500 |
| `luna-gpt` | GPT-style text completion | 2000 |

## 🔄 Streaming Responses

```python
import requests
import json

response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    headers={"Authorization": "Bearer luna-api-key"},
    json={
        "model": "luna-chat",
        "messages": [{"role": "user", "content": "Tell me a story"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data_str = line[6:]
            if data_str.strip() != '[DONE]':
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and data['choices']:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            print(delta['content'], end='', flush=True)
                except json.JSONDecodeError:
                    continue
```

## 🛠️ Configuration

Edit `openai_api_config.json` to customize:

```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8001
  },
  "models": {
    "luna": {
      "max_tokens": 1000,
      "temperature_range": [0.0, 2.0]
    }
  },
  "limits": {
    "max_tokens_per_request": 2000,
    "rate_limit_per_minute": 60
  }
}
```

## 🔗 Integration Examples

### AutoGen
```python
from autogen import ConversableAgent

agent = ConversableAgent(
    "luna",
    llm_config={
        "config_list": [{
            "model": "luna-chat",
            "api_base": "http://localhost:8001",
            "api_key": "luna-api-key"
        }]
    }
)
```

### CrewAI
```python
from crewai import Agent

agent = Agent(
    role="AI Assistant",
    goal="Help users with their questions",
    backstory="I am Luna, a caring AI companion",
    llm=ChatOpenAI(
        model_name="luna-chat",
        openai_api_base="http://localhost:8001",
        openai_api_key="luna-api-key"
    )
)
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8001/health
```

### List Models
```bash
curl http://localhost:8001/v1/models
```

### API Documentation
Visit `http://localhost:8001/docs` for interactive API documentation.

## 🚨 Troubleshooting

### Common Issues

1. **"Luna core not available"**
   - Make sure `main.py` is in the same directory
   - Check that Luna's dependencies are installed

2. **Connection refused**
   - Ensure the API server is running on port 8001
   - Check firewall settings

3. **Empty responses**
   - Verify Luna's core functionality is working
   - Check the server logs for errors

### Debug Mode

Set environment variable for verbose logging:
```bash
export LUNNA_DEBUG=1
python start_openai_api.py
```

## 📝 License

This OpenAI-compatible API wrapper is part of the Luna AI project.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the examples
5. Submit a pull request

## 📞 Support

- Check the logs in the terminal for detailed error messages
- Ensure Luna's main functionality is working first
- Test with the provided examples

---

**🌙 Luna OpenAI-Compatible API - Bringing Luna to the OpenAI ecosystem!**
