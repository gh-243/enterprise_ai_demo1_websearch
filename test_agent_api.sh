#!/bin/bash
# NEW MULTI-AGENT FEATURE
# Test script for the multi-agent API endpoints

echo "========================================="
echo "Testing Multi-Agent System API"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

echo -e "${BLUE}1. Testing /health endpoint...${NC}"
curl -s "${BASE_URL}/health" | jq .
echo ""

echo -e "${BLUE}2. Listing all available agents...${NC}"
curl -s "${BASE_URL}/v1/agents/list" | jq .
echo ""

echo -e "${BLUE}3. Testing Research Agent (requires OpenAI API key)...${NC}"
echo "Note: This will make an actual API call and search the web"
read -p "Press Enter to continue or Ctrl+C to skip..."

curl -X POST "${BASE_URL}/v1/agents/run" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "research",
    "query": "What is quantum computing in simple terms?"
  }' | jq '.'
echo ""

echo -e "${BLUE}4. Testing Fact-Check Agent (requires OpenAI API key)...${NC}"
echo "Note: This will make actual API calls"
read -p "Press Enter to continue or Ctrl+C to skip..."

curl -X POST "${BASE_URL}/v1/agents/run" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "fact_check",
    "query": "The Great Wall of China is visible from space"
  }' | jq '.'
echo ""

echo -e "${BLUE}5. Testing Standard Pipeline (requires OpenAI API key)...${NC}"
echo "Note: This will run all 4 agents in sequence"
read -p "Press Enter to continue or Ctrl+C to skip..."

curl -X POST "${BASE_URL}/v1/agents/pipeline/standard" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Benefits of remote work",
    "output_format": "summary"
  }' | jq '.'
echo ""

echo -e "${GREEN}========================================="
echo "All tests completed!"
echo "=========================================${NC}"
echo ""
echo "To view interactive API docs, visit:"
echo "  ${BASE_URL}/docs"
echo ""
echo "Available endpoints:"
echo "  GET  ${BASE_URL}/v1/agents/list"
echo "  POST ${BASE_URL}/v1/agents/run"
echo "  POST ${BASE_URL}/v1/agents/pipeline"
echo "  POST ${BASE_URL}/v1/agents/pipeline/standard"
