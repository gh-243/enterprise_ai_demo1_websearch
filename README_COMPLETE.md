# AI Chatbot with Web Search & Cost Tracking

Enterprise-grade AI chatbot with OpenAI/Anthropic integration, web search capabilities, and comprehensive cost tracking infrastructure.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)

## 🌟 Features

### Core Functionality
- **Multi-Provider LLM Support**: OpenAI (GPT-4o, GPT-4o-mini) and Anthropic (Claude 3.5 Sonnet)
- **Web Search Integration**: DuckDuckGo search for real-time information retrieval
- **Modern Web UI**: Beautiful, responsive chat interface with real-time updates
- **Structured Logging**: JSON-formatted logs with request tracing and correlation

### Enterprise Features
- **Cost Tracking**: Real-time per-request cost accounting with pricing tables
- **ASGI Middleware**: Request/response tracking with UUID generation
- **API Analytics**: REST endpoints for cost summaries and usage metrics
- **Request Tracing**: Complete request correlation with trace IDs
- **Error Handling**: Comprehensive error management and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key (or Anthropic API key)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kaw393939/enterprise_ai_demo1_websearch.git
cd enterprise_ai_demo1_websearch
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EOF
```

5. **Run the application**
```bash
uvicorn src.app.app:app --port 8000 --reload
```

6. **Open your browser**
Navigate to `http://localhost:8000` to use the chat interface.

## 📖 API Documentation

### Chat Endpoint
```http
POST /v1/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "What is machine learning?"}
  ],
  "options": {
    "use_search": true,
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

### Cost Tracking Endpoints

**Get Cost Summary**
```http
GET /v1/costs/latest?limit=100
```

**Get Recent Requests**
```http
GET /v1/costs/requests?limit=50
```

**Health Check**
```http
GET /v1/costs/health
```

## 🏗️ Architecture

```
ai_chatbot/
├── src/
│   ├── api/              # FastAPI routers
│   │   ├── chat_router.py    # Chat endpoint
│   │   └── cost_router.py    # Cost tracking API
│   ├── app/              # Application setup
│   │   └── app.py            # FastAPI app with middleware
│   ├── infra/            # Infrastructure layer
│   │   ├── pricing.py        # LLM cost calculations
│   │   └── middleware.py     # ASGI cost tracking
│   ├── providers/        # LLM provider abstractions
│   │   ├── base.py           # Base provider interface
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   └── factory.py        # Provider factory
│   ├── client.py         # HTTP client utilities
│   ├── models.py         # Pydantic models
│   ├── parser.py         # Response parsing
│   └── search_service.py # Web search integration
├── static/               # Web UI
│   └── index.html           # Chat interface
├── tests/                # Test suite
└── docs/                 # Documentation
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_chat_router.py -v

# Run middleware tests
pytest tests/test_middleware_costs.py -v
```

**Test Coverage:**
- Pricing Module: 100%
- Middleware: 91%
- Cost API: 87%
- 26 tests covering all major features

## 💰 Cost Tracking

The application includes comprehensive cost tracking:

- **Real-time Calculation**: Costs computed per request using current LLM pricing
- **Provider Support**: OpenAI and Anthropic pricing tables
- **In-Memory Buffer**: Recent request metrics stored for analytics
- **JSON Logging**: Structured logs with cost information
- **API Access**: REST endpoints for cost summaries and metrics

### Supported Models & Pricing

**OpenAI:**
- GPT-4o-mini: $0.15/$0.60 per 1M tokens (input/output)
- GPT-4o: $2.50/$10.00 per 1M tokens
- GPT-3.5-turbo: $0.50/$1.50 per 1M tokens

**Anthropic:**
- Claude 3.5 Sonnet: $3.00/$15.00 per 1M tokens

## 🎨 Web UI Features

- **Modern Design**: Gradient-based UI with smooth animations
- **Real-time Updates**: Live cost tracking and message updates
- **Responsive**: Mobile-friendly design
- **Options Toggle**: Enable/disable web search, creative mode
- **Status Indicators**: Connection status and typing indicators
- **Error Handling**: User-friendly error messages

## 📊 Monitoring & Observability

### Structured Logging
```json
{
  "request_id": "uuid4",
  "path": "/v1/chat",
  "method": "POST",
  "status": 200,
  "latency_ms": 1234.5,
  "model": "gpt-4o-mini",
  "tokens_in": 150,
  "tokens_out": 75,
  "cost_usd": 0.0000675
}
```

### Metrics Available
- Request count and rates
- Token usage (input/output)
- Cost per request and total
- Latency measurements
- Model usage distribution
- Error rates and types

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `LLM_PROVIDER` | Provider name (openai/anthropic) | openai |
| `LLM_MODEL` | Model identifier | gpt-4o-mini |

### Application Settings

Configure in `src/app/app.py`:
- CORS origins
- Middleware buffer size
- Logging levels
- Rate limits

## 📚 Documentation

- [Architecture Guide](docs/architecture.md) - System design and patterns
- [Getting Started](docs/GETTING_STARTED.md) - Detailed setup guide
- [TDD Workflow](docs/TDD_WORKFLOW.md) - Testing methodology
- [Student Guide](docs/STUDENT_GUIDE.md) - Learning resources
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

## 🤝 Contributing

This is an educational project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- FastAPI framework
- DuckDuckGo for search capabilities

## 📧 Support

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Built with ❤️ for learning and education**