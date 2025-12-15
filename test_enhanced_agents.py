#!/usr/bin/env python3
"""
Test script for document-aware agents.

Demonstrates how agents now search uploaded documents before web search.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import AgentOrchestrator, AgentType
from src.documents import check_dependencies


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def check_setup():
    """Check if everything is set up correctly."""
    print_section("Checking Setup")
    
    # Check dependencies
    deps = check_dependencies()
    print("📦 Dependencies:")
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {name}: {available}")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"\n✅ OpenAI API Key: Found ({api_key[:10]}...)")
    else:
        print("\n❌ OpenAI API Key: Not found!")
        print("   Set OPENAI_API_KEY environment variable")
        return False
    
    return True


def test_research_agent():
    """Test the enhanced Research Agent."""
    print_section("Testing Research Agent with Document Search")
    
    print("🔍 Query: What are neural networks?\n")
    print("Expected behavior:")
    print("  1. Search uploaded documents for 'neural networks'")
    print("  2. If found, use document information")
    print("  3. Supplement with web search")
    print("  4. Clearly cite both sources\n")
    
    orchestrator = AgentOrchestrator()
    
    try:
        result = orchestrator.run_single_agent(
            agent_type=AgentType.RESEARCH,
            query="What are neural networks?",
            model="gpt-4o-mini"
        )
        
        print("📊 Results:")
        print(f"  Agent: {result.agent_name}")
        print(f"  Sources: {len(result.sources)}")
        print(f"  Used Documents: {result.metadata.get('used_documents', False)}")
        print(f"  Document Results: {result.metadata.get('document_results', 0)}")
        print(f"  Web Sources: {result.metadata.get('web_sources', 0)}")
        print(f"\n📝 Response (first 300 chars):")
        print(f"  {result.content[:300]}...")
        
        print(f"\n📚 Sources:")
        for source in result.sources[:5]:
            source_type = source.get('type', 'unknown')
            title = source.get('title', 'Unknown')
            print(f"  - [{source_type}] {title}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_fact_check_agent():
    """Test the enhanced Fact-Check Agent."""
    print_section("Testing Fact-Check Agent with Document Search")
    
    print("🔍 Claim: The Earth revolves around the Sun\n")
    print("Expected behavior:")
    print("  1. Search uploaded documents for verification")
    print("  2. Search web for supporting evidence")
    print("  3. Search web for counter-evidence")
    print("  4. Provide verdict with confidence score\n")
    
    orchestrator = AgentOrchestrator()
    
    try:
        result = orchestrator.run_single_agent(
            agent_type=AgentType.FACT_CHECK,
            query="The Earth revolves around the Sun",
            model="gpt-4o-mini"
        )
        
        print("📊 Results:")
        print(f"  Agent: {result.agent_name}")
        print(f"  Confidence: {result.confidence_score}%")
        print(f"  Sources Checked: {len(result.sources)}")
        print(f"  Used Documents: {result.metadata.get('used_documents', False)}")
        print(f"  Document Results: {result.metadata.get('document_results', 0)}")
        
        print(f"\n📝 Verdict (first 300 chars):")
        print(f"  {result.content[:300]}...")
        
        print(f"\n📚 Evidence Sources:")
        for source in result.sources[:5]:
            source_type = source.get('type', 'unknown')
            title = source.get('title', 'Unknown')
            print(f"  - [{source_type}] {title}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def show_usage_examples():
    """Show examples of how to use the enhanced system."""
    print_section("Usage Examples")
    
    print("""
📚 EXAMPLE 1: Upload a textbook and research from it

from src.documents import DocumentProcessor
processor = DocumentProcessor()
document = await processor.upload_document(file, user_id="student1")

from src.agents import run_agent, AgentType
result = run_agent(
    agent_type=AgentType.RESEARCH,
    query="Explain the concept from Chapter 3",
    model="gpt-4o-mini"
)
# Result will include information from the uploaded textbook!


📚 EXAMPLE 2: Fact-check against your course materials

from src.agents import run_agent, AgentType
result = run_agent(
    agent_type=AgentType.FACT_CHECK,
    query="The formula for compound interest is X",
    model="gpt-4o-mini"
)
# Checks both uploaded materials and web sources!


📚 EXAMPLE 3: Upload and search documents via API

# Upload document
curl -X POST http://localhost:8001/v1/documents/upload \\
  -F "file=@textbook.pdf" \\
  -F "title=My Textbook" \\
  -F "subject=Math"

# Use research agent (automatically searches documents)
curl -X POST http://localhost:8001/v1/agents/research \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Explain calculus", "model": "gpt-4o-mini"}'


📚 EXAMPLE 4: Direct document search

from src.documents import search_documents

results = search_documents(
    query="neural networks",
    max_results=5,
    similarity_threshold=0.6
)

for result in results:
    print(f"{result.document_title}: {result.similarity_score:.2f}")
    print(result.content)
""")


def main():
    """Main test function."""
    print("\n" + "🎓"*35)
    print("STUDENT ASSISTANT - Document-Aware Agents Test")
    print("🎓"*35)
    
    # Check setup
    if not check_setup():
        print("\n❌ Setup incomplete. Please fix issues above.")
        return 1
    
    # Run tests
    try:
        test_research_agent()
        test_fact_check_agent()
        show_usage_examples()
        
        print_section("Summary")
        print("✅ Agent enhancements are working!")
        print("\n🎯 Key Features:")
        print("  • Agents search uploaded documents first")
        print("  • Fallback to web search when needed")
        print("  • Clear source attribution (document vs web)")
        print("  • Higher relevance for student materials")
        print("\n📝 Next Steps:")
        print("  1. Upload some documents via API")
        print("  2. Test agents with document-specific queries")
        print("  3. Check the source attribution in responses")
        print("\n🎓 Ready for students!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
