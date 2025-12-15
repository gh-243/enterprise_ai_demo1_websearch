#!/usr/bin/env python3
"""
Test/Demo Script for Podcast Generation Feature

Demonstrates the podcast agent capabilities with various scenarios.
"""

import os
import sys
from pathlib import Path

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import AgentConfig, AgentType, PodcastAgent, generate_podcast


def check_requirements():
    """Check if all required dependencies are available."""
    print("=" * 70)
    print("PODCAST AGENT - REQUIREMENTS CHECK")
    print("=" * 70)
    
    checks = []
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    checks.append(("OpenAI API Key", api_key is not None))
    
    # Check OpenAI library
    try:
        import openai
        checks.append(("OpenAI Library", True))
    except ImportError:
        checks.append(("OpenAI Library", False))
    
    # Check document search
    try:
        from src.documents import get_document_search_service
        doc_service = get_document_search_service()
        has_docs = doc_service.has_documents()
        checks.append(("Document Search Service", True))
        checks.append(("Documents Available", has_docs))
    except ImportError:
        checks.append(("Document Search Service", False))
        checks.append(("Documents Available", False))
    
    # Check podcast directory
    podcast_dir = Path("podcasts")
    checks.append(("Podcast Directory", podcast_dir.exists()))
    
    # Display results
    print()
    for check_name, status in checks:
        status_icon = "✓" if status else "✗"
        status_text = "Available" if status else "Missing"
        print(f"{status_icon} {check_name:<30} {status_text}")
    
    print()
    
    # Summary
    all_critical = all([
        checks[0][1],  # API key
        checks[1][1],  # OpenAI library
    ])
    
    if all_critical:
        print("✅ All critical requirements met - podcast generation ready!")
    else:
        print("⚠️  Some requirements missing - podcast features may be limited")
        if not checks[0][1]:
            print("   → Set OPENAI_API_KEY environment variable")
        if not checks[1][1]:
            print("   → Install openai: pip install openai")
    
    print()
    return all_critical


def test_basic_podcast():
    """Test basic podcast generation without documents."""
    print("=" * 70)
    print("TEST 1: Basic Podcast Generation (No Documents)")
    print("=" * 70)
    print()
    
    query = "Explain the fundamentals of Python programming"
    
    print(f"Query: {query}")
    print(f"Style: conversational")
    print(f"Voice: nova")
    print(f"Duration: 3 minutes")
    print()
    
    try:
        print("Generating podcast...")
        result = generate_podcast(
            query=query,
            style="conversational",
            voice="nova",
            format="mp3",
            duration_target=3
        )
        
        print("✅ Podcast generated successfully!")
        print()
        print(f"Script Preview (first 500 chars):")
        print("-" * 70)
        print(result["script"][:500] + "...")
        print("-" * 70)
        print()
        
        if result["audio_file"]:
            print(f"Audio File: {result['audio_file']}")
            file_path = Path(result['audio_file'])
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"File Size: {size_mb:.2f} MB")
        else:
            print("⚠️  Audio file not generated (TTS may not be available)")
        
        print()
        print(f"Sources: {len(result['sources'])} sources")
        print(f"Used Documents: {result['metadata']['used_documents']}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_document_podcast():
    """Test podcast generation with uploaded documents."""
    print("=" * 70)
    print("TEST 2: Document-Based Podcast Generation")
    print("=" * 70)
    print()
    
    # Check if documents are available
    try:
        from src.documents import get_document_search_service
        doc_service = get_document_search_service()
        
        if not doc_service.is_available():
            print("⚠️  Document search service not available - skipping test")
            print()
            return
        
        if not doc_service.has_documents():
            print("⚠️  No documents uploaded - skipping test")
            print("   Upload documents first using: POST /v1/documents/upload")
            print()
            return
        
        # Test with document search
        query = "Summarize the main concepts from the uploaded materials"
        
        print(f"Query: {query}")
        print(f"Style: summary")
        print(f"Voice: alloy")
        print(f"Duration: 5 minutes")
        print()
        
        print("Generating podcast from documents...")
        result = generate_podcast(
            query=query,
            style="summary",
            voice="alloy",
            format="mp3",
            duration_target=5
        )
        
        print("✅ Podcast generated successfully!")
        print()
        print(f"Script Preview (first 500 chars):")
        print("-" * 70)
        print(result["script"][:500] + "...")
        print("-" * 70)
        print()
        
        if result["audio_file"]:
            print(f"Audio File: {result['audio_file']}")
        
        print()
        print(f"Sources: {len(result['sources'])} sources")
        for i, source in enumerate(result["sources"][:5], 1):
            if source["type"] == "document":
                print(f"  [{i}] Document: {source['title']}")
            else:
                print(f"  [{i}] Web: {source['title']}")
        
        print()
        print(f"Used Documents: {result['metadata']['used_documents']}")
        print()
        
    except ImportError:
        print("⚠️  Document search not available - skipping test")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_different_styles():
    """Test different podcast styles."""
    print("=" * 70)
    print("TEST 3: Different Podcast Styles")
    print("=" * 70)
    print()
    
    query = "What is machine learning?"
    styles = ["conversational", "lecture", "summary", "storytelling"]
    
    for style in styles:
        print(f"Testing style: {style}")
        
        try:
            result = generate_podcast(
                query=query,
                style=style,
                voice="nova",
                format="mp3",
                duration_target=2  # Short for testing
            )
            
            print(f"  ✓ {style.capitalize()} style - Generated successfully")
            print(f"    Script length: {len(result['script'])} chars")
            
        except Exception as e:
            print(f"  ✗ {style.capitalize()} style - Error: {e}")
        
        print()
    
    print()


def test_agent_class():
    """Test using PodcastAgent class directly."""
    print("=" * 70)
    print("TEST 4: PodcastAgent Class Direct Usage")
    print("=" * 70)
    print()
    
    # Create agent configuration
    config = AgentConfig(
        name="Educational Podcast Generator",
        agent_type=AgentType.PODCAST,
        description="Generate engaging educational podcasts",
        model="gpt-4o-mini"
    )
    
    # Create agent
    agent = PodcastAgent(config)
    
    # Test query
    query = "Explain the concept of neural networks"
    
    print(f"Agent: {config.name}")
    print(f"Query: {query}")
    print()
    
    try:
        print("Processing with PodcastAgent...")
        
        context = {
            "style": "conversational",
            "voice": "echo",
            "format": "mp3",
            "duration_target": 4
        }
        
        response = agent.process(query, context)
        
        print("✅ Agent processing successful!")
        print()
        print(f"Agent Name: {response.agent_name}")
        print(f"Agent Type: {response.agent_type.value}")
        print()
        print(f"Script Preview (first 400 chars):")
        print("-" * 70)
        print(response.content[:400] + "...")
        print("-" * 70)
        print()
        
        print("Metadata:")
        for key, value in response.metadata.items():
            if key != "audio_file":
                print(f"  {key}: {value}")
        
        if response.metadata.get("audio_file"):
            print(f"  audio_file: {response.metadata['audio_file']}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def list_generated_podcasts():
    """List all generated podcasts."""
    print("=" * 70)
    print("GENERATED PODCASTS")
    print("=" * 70)
    print()
    
    podcast_dir = Path("podcasts")
    
    if not podcast_dir.exists():
        print("No podcast directory found.")
        print()
        return
    
    podcasts = list(podcast_dir.glob("*.mp3")) + \
                list(podcast_dir.glob("*.opus")) + \
                list(podcast_dir.glob("*.aac")) + \
                list(podcast_dir.glob("*.flac"))
    
    if not podcasts:
        print("No podcasts generated yet.")
        print()
        return
    
    print(f"Found {len(podcasts)} podcast(s):")
    print()
    
    for podcast in sorted(podcasts, key=lambda p: p.stat().st_mtime, reverse=True):
        stat = podcast.stat()
        size_mb = stat.st_size / (1024 * 1024)
        
        print(f"📻 {podcast.name}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Path: {podcast}")
        print()
    
    print()


def main():
    """Run all tests."""
    print()
    print("🎙️  PODCAST AGENT DEMONSTRATION")
    print()
    
    # Check requirements
    requirements_ok = check_requirements()
    
    if not requirements_ok:
        print("Please install missing requirements before running tests.")
        return
    
    # Prompt for test selection
    print("Select tests to run:")
    print("1. Basic podcast generation (no documents)")
    print("2. Document-based podcast generation")
    print("3. Different podcast styles")
    print("4. PodcastAgent class direct usage")
    print("5. List generated podcasts")
    print("6. Run all tests")
    print()
    
    choice = input("Enter choice (1-6) or 'q' to quit: ").strip()
    print()
    
    if choice == "q":
        print("Exiting...")
        return
    
    tests = {
        "1": test_basic_podcast,
        "2": test_document_podcast,
        "3": test_different_styles,
        "4": test_agent_class,
        "5": list_generated_podcasts,
    }
    
    if choice == "6":
        # Run all tests
        for test_func in tests.values():
            test_func()
    elif choice in tests:
        tests[choice]()
    else:
        print("Invalid choice.")
    
    print()
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  • Access API: POST /v1/podcasts/generate")
    print("  • Download: GET /v1/podcasts/download/{filename}")
    print("  • List all: GET /v1/podcasts/list")
    print("  • View docs: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
