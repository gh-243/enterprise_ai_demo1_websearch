# NEW MULTI-AGENT FEATURE
"""
Multi-Agent System Usage Examples

Demonstrates how to use the agent system.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import run_agent, AgentOrchestrator, AgentType


def example_single_agent():
    """Example: Run a single agent."""
    print("=" * 70)
    print("EXAMPLE 1: Single Agent (Research)")
    print("=" * 70)
    
    result = run_agent(
        agent_name="research",
        query="What are the latest developments in quantum computing?"
    )
    
    print(f"\nAgent: {result.agent_name}")
    print(f"Type: {result.agent_type.value}")
    print(f"\nResponse:\n{result.content}")
    print(f"\nSources: {len(result.sources)} found")
    print(f"Tokens used: {result.tokens_used}")


def example_fact_check():
    """Example: Fact-check a claim."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Fact-Check Agent")
    print("=" * 70)
    
    result = run_agent(
        agent_name="fact_check",
        query="The Great Wall of China is visible from space with the naked eye"
    )
    
    print(f"\nAgent: {result.agent_name}")
    print(f"Confidence Score: {result.confidence_score}%")
    print(f"\nResponse:\n{result.content}")


def example_business_analyst():
    """Example: Business analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Business Analyst Agent")
    print("=" * 70)
    
    result = run_agent(
        agent_name="business_analyst",
        query="Analyze the electric vehicle market and Tesla's competitive position"
    )
    
    print(f"\nAgent: {result.agent_name}")
    print(f"\nResponse:\n{result.content}")


def example_standard_pipeline():
    """Example: Standard pipeline (Research → Fact-Check → Business Analyst → Writer)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Standard Pipeline")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    query = "What is the future of artificial intelligence in healthcare?"
    
    print(f"\nQuery: {query}")
    print("\nRunning pipeline: Research → Fact-Check → Business Analyst → Writer\n")
    
    responses = orchestrator.run_standard_pipeline(query, output_format="report")
    
    for i, response in enumerate(responses, 1):
        print(f"\n{'─' * 70}")
        print(f"AGENT {i}: {response.agent_name}")
        print(f"{'─' * 70}")
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
    
    print(f"\n{'═' * 70}")
    print(f"PIPELINE COMPLETE")
    print(f"{'═' * 70}")
    print(f"Total agents: {len(responses)}")
    print(f"Total tokens: {sum(r.tokens_used for r in responses)}")


def example_custom_pipeline():
    """Example: Custom pipeline."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Custom Pipeline")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    # Custom pipeline: Research + Writer (skip fact-check and business analysis)
    pipeline = [
        {
            "agent": AgentType.RESEARCH,
            "query": "What are the best practices for remote team management?"
        },
        {
            "agent": AgentType.WRITING,
            "query": "Write an email to our team about these best practices"
        }
    ]
    
    responses = orchestrator.run_pipeline(pipeline, "remote team management")
    
    print(f"\nCustom Pipeline: Research → Writer\n")
    
    for response in responses:
        print(f"\n{'─' * 70}")
        print(f"{response.agent_name}")
        print(f"{'─' * 70}")
        print(response.content)


def main():
    """Run all examples."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  MULTI-AGENT SYSTEM - USAGE EXAMPLES".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    try:
        # Example 1: Single agent
        example_single_agent()
        
        # Example 2: Fact-check
        # Uncomment to run:
        # example_fact_check()
        
        # Example 3: Business analyst
        # Uncomment to run:
        # example_business_analyst()
        
        # Example 4: Standard pipeline
        # Uncomment to run:
        # example_standard_pipeline()
        
        # Example 5: Custom pipeline
        # Uncomment to run:
        # example_custom_pipeline()
        
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  Examples completed successfully!".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
