# Student Assistant UI - Testing Guide

## ✅ Server Status

**Server Running**: Yes ✓
**URL**: http://127.0.0.1:8000
**Student UI**: http://127.0.0.1:8000/student

## 🧪 Testing Checklist

### 1. Server Health Check

```bash
curl http://127.0.0.1:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "service": "ai-chatbot"
}
```

**Status**: ✅ PASS

### 2. Student UI Access

**URL**: http://127.0.0.1:8000/student

**Expected**:
- Beautiful purple/blue gradient interface
- 4 tabs visible: Library, Chat, Podcasts, Search
- Header with "Student Assistant" title

**How to Test**:
1. Open http://127.0.0.1:8000/student in your browser
2. Verify page loads without errors
3. Check that all visual elements appear correctly

### 3. Document Upload (Library Tab)

**Test Steps**:
1. Click on "Library" tab (should be active by default)
2. See upload area with "📤 Upload Course Materials"
3. Try uploading a test file:
   - Click the upload area OR drag & drop a file
   - Supported: PDF, DOCX, EPUB, TXT
4. Wait for upload confirmation
5. Document should appear in the grid below

**Expected Behavior**:
- Upload area shows on hover
- File uploads successfully
- Success message appears
- Document card shows in grid with:
  - Document icon 📄
  - File name
  - File type and size
  - Number of chunks

### 4. AI Chat (Chat Tab)

**Test Steps**:
1. Click "Chat" tab
2. See welcome message from AI 🤖
3. Type a question in the input box (e.g., "What is Python?")
4. Press Enter or click "Send"
5. Wait for response

**Expected Behavior**:
- User message appears on the right (purple)
- Loading indicator shows "Thinking..."
- AI response appears on the left with source citations
- Chat scrolls to show new messages

### 5. Podcast Generation (Podcast Tab)

**Test Steps**:
1. Click "Podcasts" tab
2. See podcast generation form
3. Enter a topic (e.g., "Explain machine learning basics")
4. Select options:
   - Style: Conversational
   - Voice: Nova
   - Duration: 5 minutes
   - Format: MP3
5. Click "🎙️ Generate Podcast"
6. Wait for generation (~20-30 seconds)

**Expected Behavior**:
- Button shows loading spinner
- Success message after generation
- New podcast appears in list below
- Download ⬇️ and Play ▶️ buttons available

**Note**: Requires `OPENAI_API_KEY` to be set!

### 6. Document Search (Search Tab)

**Test Steps**:
1. Click "Search" tab
2. Enter a search query
3. Press Enter or click "Search"
4. View results

**Expected Behavior**:
- Search executes quickly
- Results show with similarity scores
- Content previews visible
- Source document identified

**Note**: Requires documents to be uploaded first!

### 7. API Endpoint Tests

Test the backend APIs directly:

```bash
# Health checks
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/documents/health
curl http://127.0.0.1:8000/v1/podcasts/health

# List documents
curl http://127.0.0.1:8000/v1/documents/list

# List podcasts  
curl http://127.0.0.1:8000/v1/podcasts/list

# Get podcast options
curl http://127.0.0.1:8000/v1/podcasts/options
```

### 8. Responsive Design Test

Test on different screen sizes:

**Desktop (>768px)**:
- Multi-column document grid
- Side-by-side form layouts
- Wide content areas

**Tablet (768px)**:
- 2-column grids
- Adjusted spacing

**Mobile (<768px)**:
- Single column layout
- Stacked forms
- Full-width buttons

**How to Test**:
- Resize browser window
- Use browser DevTools responsive mode
- Test on actual mobile device

### 9. Error Handling Tests

Test error scenarios:

**Invalid File Upload**:
- Try uploading unsupported file types (.zip, .exe)
- Try very large files (>100MB)
- Expected: Error message shown

**Empty Chat Message**:
- Click Send with empty input
- Expected: Nothing happens (validation)

**Empty Podcast Topic**:
- Click Generate without entering topic
- Expected: Alert "Please enter a topic"

**No OpenAI Key**:
- Generate podcast without API key set
- Expected: Error message about TTS unavailability

### 10. Performance Tests

**Page Load Speed**:
- Measure initial load time (should be < 1 second)
- Check if all assets load properly

**API Response Times**:
- Document upload: 2-10 seconds (depends on size)
- Chat response: 3-8 seconds
- Podcast generation: 20-35 seconds
- Search: 1-3 seconds

**Browser Console**:
- Open DevTools (F12)
- Check Console tab for errors
- Verify no JavaScript errors

## 🐛 Common Issues & Fixes

### Issue: Page Won't Load

**Symptoms**: Blank page, 404 error, or loading forever

**Solutions**:
1. Check server is running: `curl http://127.0.0.1:8000/health`
2. Verify URL is correct: `http://127.0.0.1:8000/student`
3. Check browser console for errors
4. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
5. Clear browser cache

### Issue: Upload Fails

**Symptoms**: File won't upload, error message

**Solutions**:
1. Check file format (PDF, DOCX, EPUB, TXT only)
2. Verify file size (< 50MB recommended)
3. Check server logs for errors
4. Ensure sufficient disk space
5. Try different file

### Issue: Chat Not Responding

**Symptoms**: No response, loading forever

**Solutions**:
1. Check `OPENAI_API_KEY` is set
2. Verify API key has credits
3. Check browser console for errors
4. Review server logs
5. Try simpler question

### Issue: Podcast Generation Fails

**Symptoms**: Error message, no audio generated

**Solutions**:
1. Verify `OPENAI_API_KEY` is set
2. Check API credits available
3. Try shorter duration (2-3 minutes)
4. Use simpler topic
5. Check server logs

### Issue: Search Returns Nothing

**Symptoms**: No results, empty state

**Solutions**:
1. Upload documents first
2. Wait for processing to complete
3. Try different search terms
4. Make query more general
5. Check documents contain relevant content

### Issue: Styling Looks Broken

**Symptoms**: Layout issues, missing colors

**Solutions**:
1. Hard refresh browser
2. Clear cache
3. Check browser compatibility
4. Verify CSS loaded (DevTools Network tab)
5. Try different browser

## 📊 Test Results Template

Copy this for your testing:

```
Date: ___________
Tester: ___________

✓ = Pass, ✗ = Fail, ⚠ = Partial

[ ] Server Health Check
[ ] Student UI Loads
[ ] Document Upload (Library)
[ ] AI Chat Works
[ ] Podcast Generation
[ ] Document Search
[ ] API Endpoints Respond
[ ] Responsive Design
[ ] Error Handling
[ ] Performance Acceptable

Notes:
_______________________________________
_______________________________________
_______________________________________

Issues Found:
1. _______________________________________
2. _______________________________________
3. _______________________________________

Overall Status: [ ] Ready [ ] Needs Work
```

## 🎯 Manual Testing Workflow

### Quick Test (5 minutes)

1. Open http://127.0.0.1:8000/student
2. Verify all 4 tabs are visible
3. Click each tab to ensure they switch
4. Check that content appears in each tab
5. Try one feature (e.g., chat or search)

### Comprehensive Test (20 minutes)

1. **Setup** (2 min)
   - Start server
   - Open UI in browser
   - Open DevTools console

2. **Library Tab** (5 min)
   - Upload a test PDF/TXT file
   - Verify it appears in grid
   - Check metadata is correct

3. **Chat Tab** (5 min)
   - Ask 2-3 questions
   - Verify responses make sense
   - Check sources are cited

4. **Podcast Tab** (5 min)
   - Generate a short podcast (2-3 min)
   - Wait for generation
   - Try downloading

5. **Search Tab** (3 min)
   - Search uploaded documents
   - Verify results relevance
   - Check similarity scores

## 🔧 Development Testing

For developers making changes:

```bash
# Watch for errors
tail -f logs/error.log

# Run in debug mode
export LOG_LEVEL=DEBUG
python3 -m uvicorn src.app.app:app --reload

# Test specific endpoint
curl -X POST http://127.0.0.1:8000/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_results": 5}'

# Check browser console
# F12 -> Console tab

# Monitor network requests
# F12 -> Network tab -> Filter by "Fetch/XHR"
```

## 📝 Test Report

After testing, document:

1. **What Worked**:
   - List all passing features
   - Note any particularly good UX

2. **What Didn't Work**:
   - List all failing features
   - Include error messages
   - Steps to reproduce

3. **Performance Notes**:
   - Slow operations
   - Quick operations
   - Resource usage

4. **UX Observations**:
   - Confusing elements
   - Missing features
   - Suggested improvements

5. **Browser Compatibility**:
   - Tested browsers and versions
   - Any browser-specific issues

## ✅ Sign-Off

When all tests pass:

```
Student Assistant UI - Phase 6
================================

Tested By: _______________
Date: _______________
Browser: _______________
OS: _______________

All critical features working: [ ] Yes [ ] No

Approved for: [ ] Development [ ] Staging [ ] Production

Signature: _______________
```

---

**Happy Testing!** 🧪✨

For issues or questions, check:
- Browser console (F12)
- Server logs (logs/app.log, logs/error.log)
- API docs (http://127.0.0.1:8000/docs)
