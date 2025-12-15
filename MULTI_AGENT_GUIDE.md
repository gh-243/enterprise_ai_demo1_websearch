# NEW MULTI-AGENT FEATURE
# Multi-Agent System Documentation

## 🎉 Welcome to the Multi-Agent System!

Your AI Chatbot now has 4 specialized agents that can work individually or together in pipelines!

---

## 📁 What Was Added

### New Files (Zero Changes to Existing Code!)
```
src/agents/
├── __init__.py                    # Agent module exports
├── base_agent.py                  # Base agent class
├── agent_config.py                # Agent configurations & prompts
├── research_agent.py              # Research agent implementation
├── fact_check_agent.py            # Fact-check agent implementation
├── business_analyst_agent.py      # Business analyst implementation
├── writing_agent.py               # Writing agent implementation
└── agent_orchestrator.py          # Pipeline coordination

src/api/
└── agent_router.py                # NEW - Agent API endpoints

src/app/
└── app.py                         # MODIFIED - Added agent router (2 lines)

static/
└── agent_selector.html            # NEW - UI component (optional)

demo_agents.py                     # NEW - Usage examples
```

---

## 🤖 The Four Agents

### 1. Research Agent 🔍
- **Personality**: Neutral, academic, fact-focused
- **Uses**: Your existing web search pipeline
- **Output**: Comprehensive research summary with citations
- **Temperature**: 0.3 (focused on accuracy)

```python
from src.agents import run_agent

result = run_agent(
    "research",
    "What is quantum computing?"
)
print(result.content)
```

### 2. Fact-Check Agent ✅
- **Personality**: Skeptical, "show me the receipts"
- **Uses**: Multiple search queries for verification
- **Output**: Verdict + Confidence score + Evidence
- **Temperature**: 0.2 (maximum accuracy)

```python
result = run_agent(
    "fact_check",
    "The Great Wall of China is visible from space"
)
print(f"Confidence: {result.confidence_score}%")
```

### 3. Business Analyst Agent 📊
- **Personality**: Strategic, consulting-style (McKinsey-esque)
- **Uses**: Market research + competitive analysis
- **Output**: SWOT/PESTEL analysis with recommendations
- **Temperature**: 0.5 (balanced)

```python
result = run_agent(
    "business_analyst",
    "Analyze Tesla's position in the EV market"
)
```

### 4. Writing Agent ✍️
- **Personality**: Clear, professional but friendly
- **Uses**: Content from other agents (no search)
- **Output**: Polished reports, emails, summaries
- **Temperature**: 0.7 (creative)

```python
# Requires context from previous agents
result = run_agent(
    "writing",
    "Write a professional email",
    context={"content": previous_research}
)
```

---

## 🚀 Quick Start

### Option 1: API Endpoints (Recommended)

#### List Available Agents
```bash
curl http://localhost:8000/v1/agents/list
```

#### Run Single Agent
```bash
curl -X POST http://localhost:8000/v1/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "research",
    "query": "What is machine learning?"
  }'
```

#### Run Full Pipeline
```bash
curl -X POST http://localhost:8000/v1/agents/pipeline/standard \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Future of AI in healthcare",
    "output_format": "report"
  }'
```

### Option 2: Python Code

```python
# Single agent
from src.agents import run_agent

result = run_agent("research", "quantum computing")
print(result.content)

# Full pipeline
from src.agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
responses = orchestrator.run_standard_pipeline(
    "AI in healthcare",
    output_format="report"
)

for response in responses:
    print(f"\n{response.agent_name}:")
    print(response.content)
```

### Option 3: Demo Script

```bash
python demo_agents.py
```

---

## 🔄 Pipeline Mode

The standard pipeline runs all 4 agents in sequence:

```
User Query
    ↓
1. Research Agent (gathers information)
    ↓
2. Fact-Check Agent (verifies claims)
    ↓
3. Business Analyst (strategic analysis)
    ↓
4. Writing Agent (polished document)
    ↓
Final Output
```

**Example:**
```python
from src.agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
results = orchestrator.run_standard_pipeline(
    query="Electric vehicle market trends",
    output_format="report"  # or "email" or "summary"
)

# Get just the final polished output
final_document = results[-1].content
```

---

## 🎨 UI Integration (Optional)

### Add Agent Selector to Your Chat UI

The file `static/agent_selector.html` contains a ready-to-use component.

**To integrate:**

1. Open `static/index.html`
2. Find the `<div class="chat-input-container">` section
3. Insert the content from `agent_selector.html` right before it
4. The UI will automatically have agent selection!

**What you get:**
- Agent selection buttons with emojis
- Agent descriptions
- Pipeline mode option
- Automatic UI updates

---

## 📊 API Documentation

Once your server is running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **Agent endpoints**: Look for the "agents" tag

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/agents/list` | GET | List all available agents |
| `/v1/agents/run` | POST | Run a single agent |
| `/v1/agents/pipeline` | POST | Run custom pipeline |
| `/v1/agents/pipeline/standard` | POST | Run standard 4-agent pipeline |

---

## 🔧 Customization

### Create Custom Pipelines

```python
from src.agents import AgentOrchestrator, AgentType

orchestrator = AgentOrchestrator()

# Custom: Research + Writing only
pipeline = [
    {"agent": AgentType.RESEARCH, "query": "best practices"},
    {"agent": AgentType.WRITING, "query": "create executive summary"}
]

results = orchestrator.run_pipeline(pipeline, "remote work")
```

### Modify Agent Personalities

Edit `src/agents/agent_config.py`:

```python
RESEARCH_AGENT_CONFIG = AgentConfig(
    name="Research Agent",
    # ... 
    system_prompt="Your custom prompt here...",
    temperature=0.3,  # Adjust creativity
)
```

---

## 🧪 Testing

### Test Single Agent
```bash
python demo_agents.py
```

### Test Via API
```bash
# Start server
uvicorn src.app.app:app --port 8000

# Test in another terminal
curl http://localhost:8000/v1/agents/list
```

### Check Server Logs
```bash
# In Docker
docker-compose logs -f chatbot

# Local
# Watch the terminal where uvicorn is running
```

---

## 💡 Usage Examples

### Example 1: Research a Topic
```python
from src.agents import run_agent

result = run_agent("research", "Benefits of meditation")
print(result.content)
print(f"Sources: {len(result.sources)}")
```

### Example 2: Verify a Claim
```python
result = run_agent("fact_check", "Coffee is bad for health")
print(f"Verdict: {result.content}")
print(f"Confidence: {result.confidence_score}%")
```

### Example 3: Business Analysis
```python
result = run_agent(
    "business_analyst",
    "Should we enter the remote work software market?"
)
print(result.content)  # SWOT analysis with recommendations
```

### Example 4: Create Document
```python
# First, get research
research = run_agent("research", "Best project management tools")

# Then, create polished document
document = run_agent(
    "writing",
    "Write an executive summary",
    context={"content": research.content, "sources": research.sources}
)
print(document.content)
```

### Example 5: Full Pipeline
```python
from src.agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
results = orchestrator.run_standard_pipeline(
    "Future of renewable energy",
    output_format="report"
)

# Access each stage
research_output = results[0].content
factcheck_output = results[1].content
analysis_output = results[2].content
final_report = results[3].content
```

---

## 🔒 Important Notes

### What Was NOT Changed
- ✅ `search_service.py` - Untouched, agents use it
- ✅ `chat_router.py` - Untouched, still works
- ✅ Existing chat functionality - Works exactly as before
- ✅ Cost tracking - Still operational
- ✅ Web search - Still works

### What WAS Added
- ✅ New `/agents/` folder with all agent code
- ✅ New `/v1/agents/*` API endpoints
- ✅ 2 lines in `app.py` to include agent router
- ✅ Optional UI component

### Gradual Integration
You can:
1. ✅ Keep using standard chat (default)
2. ✅ Try individual agents via API
3. ✅ Test pipelines
4. ✅ Add UI selector when ready
5. ✅ Roll back by removing 2 lines from app.py

---

## 🐛 Troubleshooting

### Agent Not Found Error
```python
# Make sure you're using the correct agent names:
# ✅ "research", "fact_check", "business_analyst", "writing"
# ❌ "Research Agent" (use lowercase, underscores)
```

### Import Error
```python
# If you get import errors, make sure you're in the project root:
import sys
sys.path.insert(0, '/path/to/ai_chatbot')
```

### API Key Error
```python
# Agents need your OpenAI API key
export OPENAI_API_KEY="your-key"
# or pass directly:
orchestrator = AgentOrchestrator(api_key="your-key")
```

---

## 📈 Next Steps

1. ✅ **Test the demo**: `python demo_agents.py`
2. ✅ **Try the API**: Visit http://localhost:8000/docs
3. ✅ **Add UI**: Integrate `agent_selector.html`
4. ✅ **Customize**: Edit agent prompts in `agent_config.py`
5. ✅ **Create pipelines**: Build custom agent workflows

---

## 🎓 Learning Path

### Beginner
- Run single agents via API
- Try the demo script
- Read agent responses

### Intermediate
- Create custom pipelines
- Modify agent prompts
- Integrate UI selector

### Advanced
- Add new agent types
- Create domain-specific pipelines
- Build multi-step workflows

---

## 📚 API Examples

See `demo_agents.py` for complete working examples of:
- Single agent execution
- Fact-checking
- Business analysis
- Standard pipeline
- Custom pipelines

---

## 🆘 Support

- **API Docs**: http://localhost:8000/docs
- **Demo Script**: `python demo_agents.py`
- **Code Examples**: See `demo_agents.py`
- **Configuration**: Edit `src/agents/agent_config.py`

---

**🎉 Your multi-agent system is ready! Start with `python demo_agents.py` to see it in action!**
