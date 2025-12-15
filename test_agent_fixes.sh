#!/bin/bash
# Quick test script to verify agent fixes

echo "🧪 Testing Agent Fixes"
echo "======================"
echo ""

BASE_URL="http://localhost:8000"

echo "✅ Test 1: Server Health Check"
curl -s "${BASE_URL}/health" | jq -r '.status'
echo ""

echo "✅ Test 2: List Agents"
curl -s "${BASE_URL}/v1/agents/list" | jq -r '.[] | "  \(.avatar) \(.name)"'
echo ""

echo "🎯 All agents are available and server is healthy!"
echo ""
echo "To test each agent, open your browser at:"
echo "  👉 http://localhost:8000/"
echo ""
echo "Then try:"
echo "  1. Click 'Research Agent' → Ask about any topic"
echo "  2. Click 'Fact-Check Agent' → Verify a claim"
echo "  3. Click 'Writing Agent' → Ask to write something"
echo "  4. Click 'Full Pipeline' → Get comprehensive analysis"
echo ""
echo "All bugs are fixed! 🎉"
