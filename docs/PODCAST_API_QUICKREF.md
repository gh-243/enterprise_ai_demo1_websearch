# Podcast API Quick Reference

## Generate Podcast

```bash
curl -X POST "http://localhost:8000/v1/podcasts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain machine learning basics",
    "style": "conversational",
    "voice": "nova",
    "format": "mp3",
    "duration_target": 5
  }'
```

**Response:**
```json
{
  "podcast_id": "podcast_20250113_142030",
  "script": "Welcome to today's episode...",
  "audio_file": "podcasts/podcast_20250113_142030.mp3",
  "audio_url": "/v1/podcasts/download/podcast_20250113_142030.mp3",
  "sources": [...],
  "used_documents": true
}
```

## Download Audio

```bash
curl "http://localhost:8000/v1/podcasts/download/podcast_20250113_142030.mp3" \
  --output my_podcast.mp3
```

## List Podcasts

```bash
curl "http://localhost:8000/v1/podcasts/list"
```

## Delete Podcast

```bash
curl -X DELETE "http://localhost:8000/v1/podcasts/podcast_20250113_142030"
```

## Get Options

```bash
curl "http://localhost:8000/v1/podcasts/options"
```

## Health Check

```bash
curl "http://localhost:8000/v1/podcasts/health"
```

## Python Usage

```python
from src.agents import generate_podcast

# Simple generation
result = generate_podcast(
    query="Explain neural networks",
    style="conversational",
    voice="nova",
    duration_target=5
)

print(result["audio_file"])
```

## Options

### Styles
- `conversational` - Friendly, engaging
- `lecture` - Structured, educational
- `summary` - Concise overview
- `storytelling` - Narrative style

### Voices
- `alloy` - Neutral, clear
- `echo` - Warm, friendly
- `fable` - Expressive, animated
- `onyx` - Deep, authoritative
- `nova` - Bright, energetic
- `shimmer` - Soft, calming

### Formats
- `mp3` - Universal (default)
- `opus` - Best compression
- `aac` - High quality
- `flac` - Lossless

### Duration
- Min: 1 minute
- Max: 30 minutes
- Target: ~150 words/minute

## Document-Based Generation

```bash
# With specific document
curl -X POST "http://localhost:8000/v1/podcasts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize Chapter 3",
    "document_id": "doc_123",
    "style": "summary"
  }'
```

## Test Script

```bash
python test_podcast_agent.py
```

## Full Documentation

See `docs/PODCAST_FEATURE_GUIDE.md` for complete guide.
