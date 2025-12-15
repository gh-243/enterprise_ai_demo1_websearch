# 🎓 Student Assistant - Quick Start Guide

## Get Started in 3 Steps

### 1. Start the Server
```bash
cd /Users/gerardherrera/ai_chatbot
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
python -m uvicorn src.app.app:app --port 8001 --reload
```

### 2. Upload a Document
```bash
curl -X POST http://localhost:8001/v1/documents/upload \
  -F "file=@your_textbook.pdf" \
  -F "title=My Textbook" \
  -F "subject=Computer Science" \
  -F "tags=textbook,ai"
```

### 3. Ask Questions
```bash
curl -X POST http://localhost:8001/v1/agents/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are neural networks?",
    "model": "gpt-4o-mini"
  }'
```

---

## 📚 Document Management Commands

### Upload Document
```bash
curl -X POST http://localhost:8001/v1/documents/upload \
  -F "file=@document.pdf" \
  -F "title=Document Title" \
  -F "author=Author Name" \
  -F "subject=Subject" \
  -F "description=Description" \
  -F "tags=tag1,tag2"
```

### List All Documents
```bash
curl http://localhost:8001/v1/documents/
```

### Get Document Details
```bash
curl http://localhost:8001/v1/documents/{document_id}
```

### Delete Document
```bash
curl -X DELETE http://localhost:8001/v1/documents/{document_id}
```

### Library Overview
```bash
curl http://localhost:8001/v1/documents/library/overview
```

### Check Capabilities
```bash
curl http://localhost:8001/v1/documents/dependencies
```

---

## 🤖 Using Enhanced Agents

### Research Agent (Searches Documents First)
```bash
curl -X POST http://localhost:8001/v1/agents/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain machine learning concepts",
    "model": "gpt-4o-mini"
  }'
```

**What it does:**
1. Searches your uploaded documents
2. Supplements with web search
3. Provides comprehensive answer with sources

### Fact-Check Agent (Verifies Against Documents)
```bash
curl -X POST http://localhost:8001/v1/agents/fact-check \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Deep learning requires labeled data",
    "model": "gpt-4o-mini"
  }'
```

**What it does:**
1. Checks uploaded documents for verification
2. Cross-references with web sources
3. Provides verdict with confidence score

### Business Analyst Agent (Web-Only)
```bash
curl -X POST http://localhost:8001/v1/agents/business \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Market analysis for AI startups",
    "model": "gpt-4o-mini"
  }'
```

### Writing Agent (Uses All Context)
```bash
curl -X POST http://localhost:8001/v1/agents/writing \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Write a summary of neural networks",
    "context": {...},
    "model": "gpt-4o-mini"
  }'
```

---

## 🐍 Python Examples

### Upload and Search Documents
```python
import requests

# 1. Upload document
with open('textbook.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/v1/documents/upload',
        files={'file': ('textbook.pdf', f, 'application/pdf')},
        data={
            'title': 'AI Textbook',
            'subject': 'Computer Science'
        }
    )
doc_id = response.json()['id']
print(f"Uploaded: {doc_id}")

# 2. Use research agent
response = requests.post(
    'http://localhost:8001/v1/agents/research',
    json={
        'query': 'What are neural networks?',
        'model': 'gpt-4o-mini'
    }
)
result = response.json()

print(f"Response: {result['content']}")
print(f"Sources: {len(result['sources'])}")
print(f"Used documents: {result['metadata']['used_documents']}")
```

### Direct Document Search
```python
from src.documents import search_documents

# Search across all documents
results = search_documents(
    query="neural networks",
    max_results=5,
    similarity_threshold=0.6
)

for result in results:
    print(f"\n{result.document_title} (Score: {result.similarity_score:.2f})")
    print(f"Page {result.page_number}: {result.content[:100]}...")
```

### Use Document Search Service
```python
from src.documents import get_document_search_service

# Get service instance
service = get_document_search_service()

# Check if documents available
if service.has_documents():
    # Search documents
    results = service.search(
        query="machine learning",
        max_results=10,
        similarity_threshold=0.5
    )
    
    # Format for agent consumption
    formatted = service.format_search_results_for_agent(results)
    print(formatted)
```

---

## 🎯 Common Use Cases

### Use Case 1: Study for Exam
```bash
# 1. Upload all relevant chapters
for chapter in chapter*.pdf; do
  curl -X POST http://localhost:8001/v1/documents/upload \
    -F "file=@$chapter" \
    -F "subject=Exam Prep"
done

# 2. Ask study questions
curl -X POST http://localhost:8001/v1/agents/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize key concepts from Chapter 3", "model": "gpt-4o-mini"}'
```

### Use Case 2: Research Paper
```bash
# 1. Upload research papers
curl -X POST http://localhost:8001/v1/documents/upload \
  -F "file=@paper1.pdf" \
  -F "file=@paper2.pdf" \
  -F "subject=Research"

# 2. Find supporting evidence
curl -X POST http://localhost:8001/v1/agents/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Evidence for deep learning in NLP", "model": "gpt-4o-mini"}'
```

### Use Case 3: Fact-Check Homework
```bash
# Upload textbook
curl -X POST http://localhost:8001/v1/documents/upload \
  -F "file=@textbook.pdf"

# Verify answers
curl -X POST http://localhost:8001/v1/agents/fact-check \
  -H "Content-Type: application/json" \
  -d '{"query": "The formula is F = ma", "model": "gpt-4o-mini"}'
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Required
export OPENAI_API_KEY="your-api-key"

# Optional
export CHROMA_DB_PATH="./data/chroma_db"
export EMBEDDING_MODEL="all-MiniLM-L6-v2"
export MAX_FILE_SIZE_MB="100"
export LOG_LEVEL="INFO"
```

### Document Processing Settings
```python
from src.documents import DocumentChunker

chunker = DocumentChunker(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200,    # Overlap between chunks
    min_chunk_size=100    # Minimum chunk size
)
```

### Vector Search Settings
```python
from src.documents import VectorDatabaseService

service = VectorDatabaseService(
    db_path="./data/chroma_db",
    embedding_model="all-MiniLM-L6-v2",  # or "all-mpnet-base-v2"
    collection_name="documents"
)
```

---

## 🐛 Troubleshooting

### Problem: "Module not found" errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Problem: "Vector database not available"
```bash
# Solution: Install vector database packages
pip install chromadb sentence-transformers
```

### Problem: "PDF extraction failed"
```bash
# Solution: Install PDF processing
pip install PyPDF2
```

### Problem: "No documents found"
```bash
# Solution: Upload documents first
curl -X POST http://localhost:8001/v1/documents/upload \
  -F "file=@document.pdf"

# Check if documents are processed
curl http://localhost:8001/v1/documents/library/overview
```

### Problem: "Search returns no results"
```bash
# Solution: Lower similarity threshold
# In Python:
results = search_documents(
    query="...",
    similarity_threshold=0.3  # Lower = more results
)
```

### Problem: "API not responding"
```bash
# Solution: Check if server is running
curl http://localhost:8001/health

# Restart server if needed
python -m uvicorn src.app.app:app --port 8001 --reload
```

---

## 📊 Monitoring

### Check System Status
```bash
# Health check
curl http://localhost:8001/health

# Check dependencies
curl http://localhost:8001/v1/documents/dependencies

# Library statistics
curl http://localhost:8001/v1/documents/library/overview
```

### View Logs
```bash
# Application logs
tail -f logs/app.log

# Error logs
tail -f logs/error.log
```

### Check Vector Database
```python
from src.documents import get_document_search_service

service = get_document_search_service()
stats = service.vector_service.get_collection_stats()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Documents: {stats['unique_documents']}")
```

---

## 🎓 Tips & Best Practices

### Document Upload
- ✅ Use descriptive titles and subjects
- ✅ Add relevant tags for organization
- ✅ Upload complete chapters rather than fragments
- ✅ Verify processing status after upload

### Querying
- ✅ Be specific in your questions
- ✅ Reference chapter/section numbers when relevant
- ✅ Use fact-check agent for verification
- ✅ Check source attribution in responses

### Organization
- ✅ Group documents by subject/course
- ✅ Use consistent naming conventions
- ✅ Delete outdated documents
- ✅ Monitor storage usage

### Performance
- ✅ Process documents during off-peak hours
- ✅ Use appropriate similarity thresholds
- ✅ Limit max_results for faster responses
- ✅ Cache frequently accessed documents

---

## 📚 Additional Resources

- **Full Documentation:** `docs/STUDENT_ASSISTANT_ENHANCEMENTS.md`
- **Architecture:** `docs/STUDENT_ASSISTANT_ARCHITECTURE.md`
- **Progress Report:** `docs/IMPLEMENTATION_PROGRESS.md`
- **API Docs:** `http://localhost:8001/docs` (when server running)
- **Testing:** `test_enhanced_agents.py`

---

## 🆘 Getting Help

### Check Documentation
1. Read error message carefully
2. Check relevant documentation
3. Review examples above
4. Test with simple cases first

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m uvicorn src.app.app:app --port 8001 --reload
```

### Test Scripts
```bash
# Test document processing
python -c "from src.documents import check_dependencies; print(check_dependencies())"

# Test agents
python test_enhanced_agents.py

# Test API
python test_api.py
```

---

**Ready to learn smarter! 🎓✨**

For questions or issues, check the logs in `/logs/` or review the documentation in `/docs/`.