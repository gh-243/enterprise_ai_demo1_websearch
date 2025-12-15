# Student Assistant Enhancements - Document Search Integration

## Overview

The AI chatbot has been enhanced to become a comprehensive student assistant with document-aware agents. Students can now upload their course materials (textbooks, lecture notes, papers) and have the agents search within these documents before falling back to web search.

## What's New

### 🎓 Student-Focused Architecture

The system now prioritizes uploaded course materials over general web content, making it ideal for:
- Studying from textbooks
- Researching within course materials
- Fact-checking against authoritative sources
- Learning from uploaded documents

### 📚 Document Processing Pipeline

**Supported Formats:**
- PDF documents
- DOCX (Word documents)
- EPUB (e-books)
- TXT (plain text)

**Features:**
- Automatic text extraction
- Chapter detection
- Metadata extraction (author, title, etc.)
- Semantic chunking for better search

### 🔍 Vector Database Integration

**Technology Stack:**
- **ChromaDB**: Persistent vector storage
- **sentence-transformers**: State-of-the-art embeddings (all-MiniLM-L6-v2)
- **Semantic Search**: Find relevant passages even with different wording

**Capabilities:**
- Fast similarity search
- Document-scoped queries
- Relevance scoring
- Metadata filtering

### 🤖 Enhanced Agents

#### Research Agent (Enhanced)
**Before:** Only searched the web
**Now:** 
1. Searches uploaded documents first
2. Falls back to web search if needed
3. Clearly indicates source of information
4. Prioritizes course materials

**Example Usage:**
```
Query: "What are the key concepts in Chapter 3?"
- Searches student's uploaded textbook
- Finds relevant passages from Chapter 3
- Supplements with web research if needed
- Cites document pages and sources
```

#### Fact-Check Agent (Enhanced)
**Before:** Only used web sources for verification
**Now:**
1. Checks uploaded documents for authoritative information
2. Uses web sources for additional verification
3. Shows clear evidence from both sources
4. Higher confidence when documents match

**Example Usage:**
```
Claim: "The formula for calculating compound interest is..."
- Checks student's finance textbook
- Verifies against web sources
- Shows evidence from both
- Provides confidence score
```

## API Endpoints

### Document Management

#### Upload Document
```http
POST /v1/documents/upload
Content-Type: multipart/form-data

Parameters:
- file: Document file (required)
- title: Document title (optional)
- author: Author name (optional)
- description: Description (optional)
- subject: Subject/category (optional)
- tags: Comma-separated tags (optional)
```

#### List Documents
```http
GET /v1/documents/
Query Parameters:
- subject: Filter by subject
- author: Filter by author
- processing_status: Filter by status
- limit: Max results (default: 50)
- offset: Pagination offset
```

#### Get Document Details
```http
GET /v1/documents/{document_id}
```

#### Delete Document
```http
DELETE /v1/documents/{document_id}
```

#### Library Overview
```http
GET /v1/documents/library/overview
Returns:
- total_documents
- total_size_mb
- processing_count
- completed_count
- recent_uploads
```

#### Check Dependencies
```http
GET /v1/documents/dependencies
Returns: Available file processors and capabilities
```

## Usage Flow

### 1. Upload Documents
```bash
curl -X POST http://localhost:8001/v1/documents/upload \
  -F "file=@textbook.pdf" \
  -F "title=Introduction to AI" \
  -F "subject=Computer Science" \
  -F "tags=textbook,ai,ml"
```

### 2. Query with Agents
```bash
curl -X POST http://localhost:8001/v1/agents/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain neural networks",
    "model": "gpt-4o-mini"
  }'
```

### 3. Agent Behavior
- **Research Agent**: Searches documents → Supplements with web
- **Fact-Check Agent**: Verifies against documents → Cross-checks web
- **Writing Agent**: Uses context from documents and web
- **Business Agent**: Maintains original web-only behavior

## Technical Architecture

### Document Processing Flow
```
Upload → Validation → Text Extraction → Chunking → Embedding → Vector DB
```

### Search Flow
```
Query → Document Search (Vector DB) → Format Results → Web Search → Combine → LLM
```

### Data Storage
```
/uploads/              # Uploaded files
/data/chroma_db/       # Vector database
/logs/                 # Application logs
```

## Configuration

### Environment Variables
```bash
# Vector Database
CHROMA_DB_PATH=./data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Document Processing
MAX_FILE_SIZE_MB=100
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# OpenAI (existing)
OPENAI_API_KEY=your-key-here
```

### Dependencies
All required packages are in `requirements.txt`:
```
# Document Processing
aiofiles==24.1.0
python-multipart==0.0.9
PyPDF2==3.0.1
python-docx==1.1.2
ebooklib==0.18

# Vector Database
chromadb==0.5.23
sentence-transformers==3.1.1
```

## Benefits for Students

### 📖 Study Smarter
- Search across all course materials instantly
- Find relevant sections without manual searching
- Get answers from authoritative sources

### ✅ Verify Information
- Fact-check against textbooks
- Cross-reference multiple sources
- Build confidence in learning

### 📝 Research Efficiently
- Find supporting evidence quickly
- Combine course materials with web research
- Cite sources properly

### 🎯 Focus on Learning
- Less time searching, more time understanding
- AI helps navigate complex materials
- Personalized assistance based on your documents

## Example Scenarios

### Scenario 1: Studying for Exam
**Student uploads:** Textbook chapters 1-5
**Query:** "What are the main differences between supervised and unsupervised learning?"
**Result:** Agent searches textbook, finds relevant definitions and examples, supplements with current research

### Scenario 2: Writing Paper
**Student uploads:** Research papers, course notes
**Query:** "Find evidence for the effectiveness of deep learning in NLP"
**Result:** Agent pulls quotes from uploaded papers, adds recent web findings, provides citations

### Scenario 3: Homework Help
**Student uploads:** Textbook, lecture slides
**Query:** "How do I solve problem 3.5?"
**Result:** Agent finds relevant formulas from textbook, explains step-by-step using course materials

## Future Enhancements

### Planned Features (Already Architected)
- ✅ Podcast generation from chapters
- ✅ Study guide creation
- ✅ Quiz generation
- ✅ Progress tracking
- ✅ Collaborative learning

See `STUDENT_ASSISTANT_ARCHITECTURE.md` for complete roadmap.

## Monitoring and Debugging

### Check Document Search Status
```bash
curl http://localhost:8001/v1/documents/dependencies
```

### View Collection Stats
```python
from src.documents import get_document_search_service

service = get_document_search_service()
stats = service.vector_service.get_collection_stats()
print(stats)
```

### Test Document Search
```python
from src.documents import search_documents

results = search_documents(
    query="neural networks",
    max_results=5,
    similarity_threshold=0.6
)

for result in results:
    print(f"{result.document_title}: {result.similarity_score:.2f}")
    print(result.content[:100])
```

## Performance Considerations

### Vector Search
- Embedding generation: ~50ms per chunk
- Search latency: <100ms for typical queries
- Scales to thousands of documents

### Document Processing
- PDF extraction: ~2-5 seconds per document
- Chunking: <1 second for typical documents
- Embedding generation: ~5-10 seconds per document

### Caching
- Embeddings are cached in ChromaDB
- No re-processing needed after initial upload
- Persistent storage across restarts

## Security Notes

### File Upload Security
- File type validation
- Size limits enforced (100MB default)
- Sanitized file names
- Isolated storage directory

### Access Control
Currently implements basic user isolation via `user_id` parameter.
**TODO for Production:**
- Implement proper authentication
- Add authorization checks
- Encrypt sensitive documents
- Audit logging

## Support and Troubleshooting

### Common Issues

**Issue:** "Vector database not available"
**Solution:** Install chromadb and sentence-transformers
```bash
pip install chromadb sentence-transformers
```

**Issue:** "PDF extraction failed"
**Solution:** Install PyPDF2
```bash
pip install PyPDF2
```

**Issue:** "Document search returns no results"
**Solution:** 
1. Check if documents are uploaded
2. Verify processing status
3. Lower similarity threshold

### Logging
Check application logs for detailed information:
```bash
tail -f logs/app.log
```

## Credits

**Architecture:** Comprehensive student assistant design
**Implementation:** Vector database integration, document processing, agent enhancement
**Technologies:** ChromaDB, sentence-transformers, FastAPI, OpenAI

---

**Ready to learn smarter! 🎓✨**