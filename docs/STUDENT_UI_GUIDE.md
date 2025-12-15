# Student UI - User Guide

## Overview

The Student Assistant UI provides a modern, intuitive web interface for all learning features. Built as a single-page application with a clean, student-friendly design.

## Access the UI

```bash
# Start the server
uvicorn src.app.app:app --reload

# Open in browser
http://localhost:8000/student
```

## Interface Sections

### 📚 Document Library

**Purpose:** Upload and manage your course materials

**Features:**
- Drag & drop file upload
- Supported formats: PDF, DOCX, EPUB, TXT
- Visual document cards with metadata
- File size and chunk count display
- Instant upload feedback

**Usage:**
1. Click the upload area or drag files
2. Select your course materials
3. Wait for processing confirmation
4. Documents appear in grid view

**Tips:**
- Upload textbooks, lecture notes, PDFs
- Organize by course or topic
- Check chunk count to ensure processing worked
- Large files may take longer to process

### 💬 AI Study Chat

**Purpose:** Interactive learning with document-aware AI

**Features:**
- Real-time chat interface
- Document-first responses
- Web search fallback
- Source citations
- Message history

**Usage:**
1. Type your question in the chat input
2. Press Enter or click Send
3. AI searches your documents first
4. Get answers with sources cited
5. Follow up with more questions

**Example Queries:**
```
"Explain the concept of recursion from my notes"
"What does Chapter 3 say about databases?"
"Help me understand this theorem"
"Summarize the key points from today's lecture"
"Compare what my textbook says vs web sources"
```

**Tips:**
- Be specific in questions
- Reference chapters or topics
- Ask follow-up questions
- Request explanations, summaries, or examples
- AI will cite document sources when used

### 🎙️ Podcast Generator

**Purpose:** Convert content to audio for learning on the go

**Features:**
- Custom topic input
- 4 podcast styles
- 6 professional voices
- Duration control (1-30 minutes)
- Multiple audio formats
- Generated podcast library
- Download and playback

**Settings:**

**Styles:**
- **Conversational**: Friendly, engaging dialogue
- **Lecture**: Structured educational format
- **Summary**: Quick overview of key points
- **Storytelling**: Narrative style for better retention

**Voices:**
- **Nova**: Bright & energetic (recommended for general learning)
- **Alloy**: Neutral & clear (good for technical content)
- **Echo**: Warm & friendly (conversational learning)
- **Fable**: Expressive & animated (storytelling)
- **Onyx**: Deep & authoritative (lectures)
- **Shimmer**: Soft & calming (relaxed studying)

**Formats:**
- **MP3**: Universal compatibility (recommended)
- **Opus**: Best compression for streaming
- **AAC**: High quality, Apple-friendly
- **FLAC**: Lossless quality, large files

**Usage:**
1. Enter your learning topic
2. Select style and voice
3. Set target duration
4. Click "Generate Podcast"
5. Wait for generation (~20-30 seconds)
6. Download or play from library

**Example Topics:**
```
"Explain machine learning fundamentals"
"Summarize Chapter 3 on Neural Networks"
"Create a study guide for midterm topics"
"Review sorting algorithms with examples"
"Explain quantum computing basics"
```

**Tips:**
- Be specific in your topic
- Match style to content complexity
- Start with 5-minute duration
- Try different voices to find your preference
- Conversational style works best for most topics
- Use Summary style for exam prep

### 🔍 Document Search

**Purpose:** Semantic search across all your documents

**Features:**
- Natural language queries
- Semantic similarity matching
- Relevance scores
- Content preview
- Source identification

**Usage:**
1. Enter search query
2. Click Search or press Enter
3. View results sorted by relevance
4. Read content previews
5. Check similarity scores

**Example Searches:**
```
"definition of recursion"
"examples of sorting algorithms"
"neural network architecture"
"database normalization rules"
"proof of Pythagorean theorem"
```

**Tips:**
- Use natural language (not keywords)
- Be specific but not too narrow
- Check similarity scores (>80% is highly relevant)
- Read full context from preview
- Refine query if results aren't relevant

## Workflow Examples

### Daily Study Session

1. **Morning: Upload Materials**
   - Library tab → Upload today's lecture notes
   - Wait for processing confirmation

2. **Afternoon: Interactive Learning**
   - Chat tab → Ask questions about concepts
   - Get document-backed explanations
   - Follow up for clarification

3. **Evening: Podcast Review**
   - Podcast tab → Generate summary podcast
   - Listen during evening walk
   - Reinforce learning aurally

### Exam Preparation

1. **Upload All Materials**
   ```
   Library → Upload chapters 1-5
   Library → Upload practice problems
   Library → Upload lecture summaries
   ```

2. **Create Study Podcasts**
   ```
   Podcast → "Review Chapter 1 key concepts" (Summary, 3 min)
   Podcast → "Review Chapter 2 key concepts" (Summary, 3 min)
   ...
   Podcast → "Comprehensive review" (Lecture, 15 min)
   ```

3. **Interactive Q&A**
   ```
   Chat → "Explain concept X from Chapter 2"
   Chat → "What are the main theorems in Chapter 3?"
   Chat → "Compare approaches in Chapters 4 and 5"
   ```

4. **Targeted Search**
   ```
   Search → "practice problems similar to exam"
   Search → "definitions I need to memorize"
   Search → "step-by-step solutions"
   ```

### Research Project

1. **Foundation Building**
   ```
   Library → Upload research papers
   Library → Upload course materials
   Chat → "Summarize the main argument in paper X"
   ```

2. **Deep Dive**
   ```
   Chat → "Compare methodologies across these papers"
   Chat → "What are the limitations discussed?"
   Podcast → "Lecture on research methodology" (20 min)
   ```

3. **Synthesis**
   ```
   Search → "similar findings"
   Search → "contradicting evidence"
   Chat → "Help me synthesize these viewpoints"
   ```

## Technical Details

### Browser Compatibility

**Supported:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

**Required Features:**
- JavaScript enabled
- Fetch API support
- CSS Grid support
- LocalStorage (optional)

### Performance

**Loading Times:**
- Initial page load: <1 second
- Document upload: 2-10 seconds (depends on size)
- Chat response: 3-8 seconds
- Podcast generation: 20-35 seconds
- Search: 1-3 seconds

**Recommended:**
- Stable internet connection
- Modern browser (last 2 versions)
- Desktop or tablet for best experience
- Mobile works but layout is optimized for larger screens

### Data & Privacy

**Client-Side:**
- No sensitive data stored in browser
- No cookies or tracking
- Messages not persisted (refresh clears)

**Server-Side:**
- Documents stored on server
- Processing done server-side
- API calls over HTTP (HTTPS recommended for production)
- Podcasts stored in `podcasts/` directory

## API Integration

The UI communicates with the backend API:

```javascript
// API Base URL
const API_BASE = 'http://localhost:8000';

// Endpoints Used:
GET  /v1/documents/list          // Load documents
POST /v1/documents/upload        // Upload files
POST /v1/documents/search        // Search documents
POST /v1/agents/research         // Chat with AI
POST /v1/podcasts/generate       // Generate podcast
GET  /v1/podcasts/list           // List podcasts
GET  /v1/podcasts/download/{id}  // Download audio
```

### Customizing API URL

Edit `student.html`:

```javascript
// Change this line
const API_BASE = 'http://localhost:8000';

// To your server URL
const API_BASE = 'https://your-server.com';
```

## Troubleshooting

### Upload Fails

**Problem:** File won't upload

**Solutions:**
- Check file format (PDF, DOCX, EPUB, TXT only)
- Verify file size (<50MB recommended)
- Ensure server is running
- Check browser console for errors
- Try different browser

### Chat Not Working

**Problem:** No response from AI

**Solutions:**
- Verify server running: `http://localhost:8000/health`
- Check OpenAI API key set
- Ensure documents uploaded and processed
- Look for error messages in chat
- Check browser console

### Podcast Generation Fails

**Problem:** Podcast doesn't generate

**Solutions:**
- Verify OpenAI API key configured
- Check API credits available
- Ensure topic field not empty
- Try shorter duration first
- Check server logs for errors

### Search Returns No Results

**Problem:** Search doesn't find anything

**Solutions:**
- Upload documents first
- Wait for processing to complete
- Try different search terms
- Make query more general
- Check documents contain relevant content

### UI Looks Broken

**Problem:** Layout or styling issues

**Solutions:**
- Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
- Clear browser cache
- Try different browser
- Check browser console for errors
- Verify `student.html` loaded correctly

### Slow Performance

**Problem:** UI feels sluggish

**Solutions:**
- Check internet connection
- Reduce concurrent requests
- Clear browser cache
- Close other tabs
- Restart browser
- Check server resources

## Keyboard Shortcuts

**Chat:**
- `Enter`: Send message
- `Shift+Enter`: New line in message

**Search:**
- `Enter`: Execute search

**General:**
- `Tab`: Navigate between fields
- `Ctrl+R` / `Cmd+R`: Refresh page

## Mobile Experience

The UI is responsive and works on mobile devices:

**Optimizations:**
- Single-column layout on small screens
- Touch-friendly buttons
- Scrollable content areas
- Simplified navigation

**Limitations:**
- Smaller screen = less content visible
- Drag & drop may not work (use click to upload)
- Podcast playback depends on browser support

**Recommendations:**
- Use tablet or desktop for best experience
- Portrait orientation for mobile
- Use native audio player for podcasts

## Customization

### Changing Colors

Edit CSS variables in `student.html`:

```css
:root {
    --primary: #667eea;      /* Main color */
    --secondary: #764ba2;    /* Accent color */
    --success: #10b981;      /* Success messages */
    --danger: #ef4444;       /* Error messages */
}
```

### Adjusting Layout

Modify grid columns:

```css
.document-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    /* Change 250px to adjust card width */
}
```

### Adding Custom Tabs

1. Add tab button:
```html
<button class="tab" onclick="switchTab('custom')">
    🔧 Custom
</button>
```

2. Add content section:
```html
<div id="custom-content" class="content">
    <h2>Custom Tab</h2>
    <!-- Your content here -->
</div>
```

## Best Practices

### Document Organization

✅ **Do:**
- Name files descriptively
- Upload by topic/course
- Keep files under 20MB
- Use clear filenames

❌ **Don't:**
- Upload duplicate content
- Use unclear filenames
- Upload non-text files
- Exceed server limits

### Chat Interaction

✅ **Do:**
- Ask specific questions
- Reference your documents
- Follow up for clarity
- Check sources cited

❌ **Don't:**
- Ask vague questions
- Ignore source citations
- Assume 100% accuracy
- Share sensitive info

### Podcast Generation

✅ **Do:**
- Start with 5-minute duration
- Match style to content
- Try different voices
- Be specific in topic

❌ **Don't:**
- Request 30-minute podcasts first
- Use vague topics
- Generate duplicates
- Waste API credits

## Future Enhancements

Coming in Phase 7 & 8:

**Audio Player:**
- Built-in playback controls
- Speed adjustment (0.5x - 2x)
- Chapter markers
- Playlist management

**Learning Features:**
- Quiz generation
- Study guides
- Progress tracking
- Note-taking integration
- Flashcard creation

**Collaboration:**
- Share podcasts
- Study groups
- Peer review
- Discussion forums

## Support

**Issues?**
- Check browser console (F12)
- Review server logs
- Test with `curl` commands
- Check API documentation: http://localhost:8000/docs

**Resources:**
- Full documentation: `docs/`
- API reference: http://localhost:8000/docs
- Test scripts: `test_*.py`

---

**Enjoy your AI-powered learning experience!** 🎓
