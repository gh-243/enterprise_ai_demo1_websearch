#!/bin/bash
# Simple API test examples for the multi-agent system

echo "🤖 Multi-Agent System - Quick API Examples"
echo "=========================================="
echo ""

# 1. List agents
echo "📋 Available Agents:"
curl -s http://localhost:8000/v1/agents/list | jq -r '.[] | "  \(.avatar) \(.name) (\(.type))"'
echo ""

# 2. Example: Research Agent
echo "🔍 Example: Research Agent"
echo "curl -X POST http://localhost:8000/v1/agents/run \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"agent_type\": \"research\","
echo "    \"query\": \"What is quantum computing?\""
echo "  }'"
echo ""

# 3. Example: Fact-Check Agent
echo "✅ Example: Fact-Check Agent"
echo "curl -X POST http://localhost:8000/v1/agents/run \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"agent_type\": \"fact_check\","
echo "    \"query\": \"Coffee is bad for your health\""
echo "  }'"
echo ""

# 4. Example: Business Analyst
echo "📊 Example: Business Analyst"
echo "curl -X POST http://localhost:8000/v1/agents/run \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"agent_type\": \"business_analyst\","
echo "    \"query\": \"Should we invest in renewable energy?\""
echo "  }'"
echo ""

# 5. Example: Standard Pipeline
echo "🔄 Example: Full Pipeline (All 4 Agents)"
echo "curl -X POST http://localhost:8000/v1/agents/pipeline/standard \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"query\": \"Future of remote work\","
echo "    \"output_format\": \"report\""
echo "  }'"
echo ""

echo "=========================================="
echo "💡 Tips:"
echo "  • View interactive docs: http://localhost:8000/docs"
echo "  • Add '| jq .' at the end for formatted JSON"
echo "  • Make sure your OpenAI API key is set"
echo "=========================================="
