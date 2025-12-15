# Podcast Generation Feature - User Guide

## Overview

The Podcast Generation feature transforms educational content into engaging audio podcasts using OpenAI's Text-to-Speech (TTS) technology. Students can convert textbook chapters, lecture notes, or any educational material into conversational audio content for learning on the go.

## Key Features

### 🎙️ **Multiple Podcast Styles**
- **Conversational**: Friendly, engaging explanation as if talking to a friend
- **Lecture**: Structured educational format with clear organization
- **Summary**: Concise overview of key points for quick review
- **Storytelling**: Narrative style that makes content memorable

### 🎤 **Six Professional Voices**
- **Alloy**: Neutral, clear voice
- **Echo**: Warm, friendly voice
- **Fable**: Expressive, animated voice
- **Onyx**: Deep, authoritative voice
- **Nova**: Bright, energetic voice
- **Shimmer**: Soft, calming voice

### 📚 **Document-Aware Generation**
- Searches uploaded documents first for accurate content
- Falls back to web search when documents don't cover the topic
- Cites sources properly (document references or web links)
- Prioritizes your course materials over general web content

### 🎵 **Multiple Audio Formats**
- **MP3**: Universal compatibility, good quality
- **Opus**: Best compression, great for streaming
- **AAC**: High quality, iOS/Apple friendly
- **FLAC**: Lossless quality, largest file size

## Quick Start

### 1. Generate Your First Podcast

**Using Python:**
```python
from src.agents import generate_podcast

result = generate_podcast(
    query="Explain the fundamentals of machine learning",
    style="conversational",
    voice="nova",
    format="mp3",
    duration_target=5  # minutes
)

print(f"Script: {result['script']}")
print(f"Audio: {result['audio_file']}")
```

**Using REST API:**
```bash
curl -X POST "http://localhost:8000/v1/podcasts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the fundamentals of machine learning",
    "style": "conversational",
    "voice": "nova",
    "format": "mp3",
    "duration_target": 5
  }'
```

### 2. Generate from Your Documents

If you've uploaded course materials, the podcast will use them automatically:

```python
result = generate_podcast(
    query="Summarize Chapter 3 on Neural Networks",
    document_id="doc_123",  # Optional: specific document
    style="summary",
    voice="alloy",
    duration_target=3
)
```

### 3. Download and Listen

```bash
# Download generated podcast
curl "http://localhost:8000/v1/podcasts/download/podcast_20250113_142030.mp3" \
  --output my_podcast.mp3

# Play with your favorite audio player
open my_podcast.mp3  # macOS
# or
vlc my_podcast.mp3   # VLC player
```

## Use Cases

### 📖 **Textbook Chapter Summaries**
Convert dense textbook chapters into digestible audio summaries:

```python
result = generate_podcast(
    query="Summarize Chapter 5: Database Normalization",
    style="summary",
    voice="nova",
    duration_target=5
)
```

**Benefits:**
- Review content during commute
- Quick refresh before exams
- Multi-sensory learning reinforcement

### 🎯 **Concept Deep Dives**
Get detailed explanations of complex topics:

```python
result = generate_podcast(
    query="Explain backpropagation in neural networks with examples",
    style="lecture",
    voice="onyx",
    duration_target=10
)
```

**Benefits:**
- Focused learning on difficult concepts
- Step-by-step explanations
- Can pause/replay as needed

### 📝 **Lecture Note Reviews**
Transform your notes into podcast reviews:

```python
result = generate_podcast(
    query="Review my notes on sorting algorithms",
    style="conversational",
    voice="echo",
    duration_target=7
)
```

**Benefits:**
- Reinforce lecture content
- Active recall practice
- Study while doing other tasks

### 📚 **Study Guide Generation**
Create comprehensive study guides:

```python
result = generate_podcast(
    query="Create a study guide for midterm covering chapters 1-5",
    style="summary",
    voice="shimmer",
    duration_target=15
)
```

**Benefits:**
- Organized review of all topics
- Identify knowledge gaps
- Time-efficient studying

### 🗣️ **Language Learning**
Practice listening comprehension:

```python
result = generate_podcast(
    query="Explain French grammar rules for past tense",
    style="conversational",
    voice="fable",
    duration_target=5
)
```

**Benefits:**
- Improve listening skills
- Natural language patterns
- Pronunciation examples

## API Reference

### Generate Podcast

**Endpoint:** `POST /v1/podcasts/generate`

**Request Body:**
```json
{
  "query": "string (required)",
  "document_id": "string (optional)",
  "chapter_id": "string (optional)",
  "style": "conversational|lecture|summary|storytelling",
  "voice": "alloy|echo|fable|onyx|nova|shimmer",
  "format": "mp3|opus|aac|flac",
  "duration_target": 5  // 1-30 minutes
}
```

**Response:**
```json
{
  "podcast_id": "podcast_20250113_142030",
  "query": "Explain machine learning",
  "script": "Full podcast script...",
  "audio_file": "podcasts/podcast_20250113_142030.mp3",
  "audio_url": "/v1/podcasts/download/podcast_20250113_142030.mp3",
  "style": "conversational",
  "voice": "nova",
  "format": "mp3",
  "duration_target": 5,
  "sources": [...],
  "used_documents": true
}
```

### Download Podcast

**Endpoint:** `GET /v1/podcasts/download/{filename}`

**Example:**
```bash
curl "http://localhost:8000/v1/podcasts/download/podcast_20250113_142030.mp3" \
  --output my_podcast.mp3
```

### List Podcasts

**Endpoint:** `GET /v1/podcasts/list`

**Response:**
```json
[
  {
    "podcast_id": "podcast_20250113_142030",
    "query": "[Unknown]",
    "style": "conversational",
    "voice": "nova",
    "format": "mp3",
    "file_path": "podcasts/podcast_20250113_142030.mp3",
    "file_size": 2457600,
    "created_at": "1705156830.0"
  }
]
```

### Delete Podcast

**Endpoint:** `DELETE /v1/podcasts/{podcast_id}`

**Example:**
```bash
curl -X DELETE "http://localhost:8000/v1/podcasts/podcast_20250113_142030"
```

### Get Options

**Endpoint:** `GET /v1/podcasts/options`

**Response:**
```json
{
  "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
  "formats": ["mp3", "opus", "aac", "flac"],
  "styles": ["conversational", "lecture", "summary", "storytelling"]
}
```

### Health Check

**Endpoint:** `GET /v1/podcasts/health`

**Response:**
```json
{
  "status": "healthy",
  "tts_available": true,
  "podcast_directory": "podcasts",
  "podcast_directory_exists": true,
  "document_search_available": true,
  "supported_voices": [...],
  "supported_formats": [...],
  "supported_styles": [...]
}
```

## Style Guide

### When to Use Each Style

| Style | Best For | Duration | Example Topics |
|-------|----------|----------|----------------|
| **Conversational** | General learning, introductory topics | 3-7 min | "What is Python?", "Intro to databases" |
| **Lecture** | Complex topics, detailed explanations | 7-15 min | "Advanced algorithms", "Quantum mechanics" |
| **Summary** | Quick reviews, exam prep | 2-5 min | "Chapter summaries", "Key concepts review" |
| **Storytelling** | Historical content, case studies | 5-10 min | "History of computing", "Business case studies" |

### Voice Selection Tips

| Voice | Personality | Best For |
|-------|-------------|----------|
| **Alloy** | Neutral, professional | Technical content, formal topics |
| **Echo** | Warm, friendly | Conversational learning, beginner topics |
| **Fable** | Expressive, animated | Storytelling, engaging narratives |
| **Onyx** | Deep, authoritative | Lectures, serious topics |
| **Nova** | Bright, energetic | General learning, motivational content |
| **Shimmer** | Soft, calming | Relaxed studying, mindfulness content |

## Advanced Usage

### Podcast Agent Class

For more control, use the `PodcastAgent` class directly:

```python
from src.agents import AgentConfig, AgentType, PodcastAgent

# Create custom configuration
config = AgentConfig(
    name="My Custom Podcast Generator",
    agent_type=AgentType.PODCAST,
    description="Specialized podcast generator",
    model="gpt-4o-mini",
    temperature=0.7
)

# Create agent
agent = PodcastAgent(config)

# Generate podcast with full control
context = {
    "document_id": "doc_123",
    "style": "conversational",
    "voice": "nova",
    "format": "mp3",
    "duration_target": 5
}

response = agent.process(
    query="Explain gradient descent",
    context=context
)

print(f"Script: {response.content}")
print(f"Sources: {response.sources}")
print(f"Metadata: {response.metadata}")
```

### Batch Generation

Generate multiple podcasts at once:

```python
from src.agents import generate_podcast

topics = [
    "Introduction to Python",
    "Variables and data types",
    "Control flow structures",
    "Functions and modules"
]

podcasts = []
for i, topic in enumerate(topics, 1):
    print(f"Generating podcast {i}/{len(topics)}: {topic}")
    
    result = generate_podcast(
        query=topic,
        style="conversational",
        voice="nova",
        format="mp3",
        duration_target=5
    )
    
    podcasts.append(result)
    print(f"  ✓ Generated: {result['audio_file']}")

print(f"\nTotal podcasts generated: {len(podcasts)}")
```

### Custom Duration Targets

Adjust podcast length based on your needs:

```python
# Quick 2-minute overview
quick_review = generate_podcast(
    query="Quick review of sorting algorithms",
    duration_target=2,
    style="summary"
)

# Comprehensive 20-minute deep dive
deep_dive = generate_podcast(
    query="Complete guide to machine learning",
    duration_target=20,
    style="lecture"
)
```

## Integration Examples

### Study Workflow Integration

```python
def create_study_session(chapter_topics: list[str]):
    """Create a complete study session podcast series."""
    
    study_podcasts = []
    
    for topic in chapter_topics:
        # Generate main content podcast
        main = generate_podcast(
            query=f"Explain {topic}",
            style="lecture",
            duration_target=10
        )
        
        # Generate summary podcast
        summary = generate_podcast(
            query=f"Quick summary of {topic}",
            style="summary",
            duration_target=3
        )
        
        study_podcasts.append({
            "topic": topic,
            "main_podcast": main["audio_file"],
            "summary_podcast": summary["audio_file"]
        })
    
    return study_podcasts

# Use it
chapter_3_topics = [
    "Neural network architecture",
    "Activation functions",
    "Backpropagation"
]

session = create_study_session(chapter_3_topics)
```

### Playlist Generation

```python
def create_exam_prep_playlist(exam_topics: list[str], output_dir: str):
    """Create a comprehensive exam prep podcast playlist."""
    import json
    from pathlib import Path
    
    playlist = {
        "name": "Exam Preparation Playlist",
        "created": str(Path().stat().st_mtime),
        "podcasts": []
    }
    
    for i, topic in enumerate(exam_topics, 1):
        result = generate_podcast(
            query=f"Review {topic} for exam preparation",
            style="summary",
            voice="nova",
            duration_target=5
        )
        
        playlist["podcasts"].append({
            "order": i,
            "topic": topic,
            "file": result["audio_file"],
            "duration_target": 5
        })
    
    # Save playlist metadata
    playlist_file = Path(output_dir) / "playlist.json"
    with open(playlist_file, "w") as f:
        json.dump(playlist, f, indent=2)
    
    return playlist

# Create playlist
topics = ["Algorithms", "Data Structures", "Complexity Analysis"]
playlist = create_exam_prep_playlist(topics, "my_exam_prep")
```

## Troubleshooting

### Audio Not Generated

**Problem:** Script generated but no audio file

**Solutions:**
1. Check OpenAI API key is set: `echo $OPENAI_API_KEY`
2. Verify OpenAI library installed: `pip install openai`
3. Check API credits available in OpenAI account
4. Review logs in `logs/app.log` for errors

### Poor Audio Quality

**Problem:** Audio sounds robotic or unclear

**Solutions:**
1. Try different voices (experiment with all 6 options)
2. Use higher quality model (future: `tts-1-hd` instead of `tts-1`)
3. Adjust script for better TTS pronunciation
4. Use FLAC format for lossless quality

### Script Too Long/Short

**Problem:** Generated script doesn't match target duration

**Solutions:**
1. Adjust `duration_target` parameter
2. Be more specific in query
3. Script targets ~150 words per minute
4. For longer content, break into multiple podcasts

### Documents Not Used

**Problem:** `used_documents: false` even with uploaded docs

**Solutions:**
1. Verify documents uploaded: `GET /v1/documents/list`
2. Check document search service: `GET /v1/podcasts/health`
3. Make query more specific to document content
4. Verify document processing completed

### File System Errors

**Problem:** Cannot save/read podcast files

**Solutions:**
1. Check `podcasts/` directory exists and is writable
2. Verify sufficient disk space
3. Check file permissions
4. Ensure no locked files (close audio players)

## Performance & Costs

### Generation Time

Typical podcast generation times:

| Duration | Script Time | Audio Time | Total |
|----------|-------------|------------|-------|
| 2 min | ~5-10 sec | ~3-5 sec | ~10-15 sec |
| 5 min | ~10-15 sec | ~7-10 sec | ~20-25 sec |
| 10 min | ~15-20 sec | ~12-15 sec | ~30-35 sec |
| 20 min | ~25-35 sec | ~20-25 sec | ~50-60 sec |

### OpenAI API Costs

Approximate costs per podcast:

- **Script Generation (GPT-4o-mini)**: $0.001 - $0.01 per podcast
- **Audio Generation (TTS)**: $0.015 per 1,000 characters
- **5-minute podcast**: ~$0.05 - $0.15 total
- **Monthly (100 podcasts)**: ~$5 - $15

### File Sizes

Typical audio file sizes:

| Format | 5 min | 10 min | 20 min |
|--------|-------|--------|--------|
| MP3 | ~2.5 MB | ~5 MB | ~10 MB |
| Opus | ~1.5 MB | ~3 MB | ~6 MB |
| AAC | ~2 MB | ~4 MB | ~8 MB |
| FLAC | ~15 MB | ~30 MB | ~60 MB |

## Best Practices

### 1. **Query Specificity**
```python
# ❌ Too vague
generate_podcast(query="Python")

# ✅ Specific and clear
generate_podcast(query="Explain Python list comprehensions with examples")
```

### 2. **Document Integration**
```python
# ✅ Reference your materials
generate_podcast(
    query="Summarize the key points from Chapter 3 on databases",
    document_id="textbook_db"
)
```

### 3. **Appropriate Duration**
```python
# Match content complexity to duration
simple_topic = generate_podcast(
    query="What is a variable?",
    duration_target=2  # Short for simple
)

complex_topic = generate_podcast(
    query="Explain quantum computing algorithms",
    duration_target=15  # Longer for complexity
)
```

### 4. **Style Selection**
```python
# First-time learning
intro = generate_podcast(style="conversational")

# Exam review
review = generate_podcast(style="summary")

# Deep understanding
advanced = generate_podcast(style="lecture")
```

### 5. **Batch Processing**
```python
# Generate efficiently
import time

for topic in topics:
    podcast = generate_podcast(query=topic)
    time.sleep(1)  # Respect API rate limits
```

## Next Steps

- **Upload documents**: `POST /v1/documents/upload` to enable document-aware podcasts
- **Try different voices**: Experiment to find your preferred learning voice
- **Create playlists**: Organize podcasts by topic/chapter
- **Integrate with study routine**: Generate podcasts as part of your learning workflow
- **Share with classmates**: Create study group playlists

## Support

For issues or questions:
1. Check API documentation: `http://localhost:8000/docs`
2. Review logs: `logs/app.log`
3. Test with demo script: `python test_podcast_agent.py`
4. Check system health: `GET /v1/podcasts/health`

---

**Ready to transform your learning?** Start generating podcasts today! 🎙️
