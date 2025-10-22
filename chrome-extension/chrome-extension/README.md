# ScreenPilot Chrome Extension

A Chrome Extension that reads webpage content and provides AI-powered answers to user questions about the current page.

## Features

- **Webpage Text Extraction**: Automatically extracts visible text content from any webpage (up to ~5000 characters)
- **AI Question Answering**: Ask questions about the current page and get contextual answers
- **Clean UI**: Simple, minimal popup interface for quick interactions
- **Real-time Analysis**: Instant responses from the backend AI service

## File Structure

```
chrome-extension/
├── manifest.json      # Extension configuration (Manifest V3)
├── popup.html         # Extension popup UI
├── popup.js          # Popup logic and API communication
├── content.js        # Content script for text extraction
├── icon.png          # Extension icon
└── README.md         # This file
```

## Installation & Testing

### Prerequisites

1. **Backend API**: Ensure your backend server is running at `http://localhost:8000`
2. **Chrome Browser**: Chrome version 88+ (for Manifest V3 support)

### Installation Steps

1. **Download/Clone** this extension to your local machine

2. **Start Backend Server** (if not already running):
   ```bash
   # Your backend should be running on localhost:8000
   # The /ask endpoint should accept POST requests with:
   # {
   #   "question": "user question",
   #   "context": "extracted webpage text"
   # }
   ```

3. **Load Extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)
   - Click "Load unpacked"
   - Select the `chrome-extension` folder
   - The ScreenPilot extension should now appear in your extensions list

4. **Pin Extension** (optional):
   - Click the puzzle piece icon in Chrome toolbar
   - Find ScreenPilot and click the pin icon to keep it visible

### Testing Instructions

1. **Navigate to any webpage** (e.g., news article, documentation, blog post)

2. **Click the ScreenPilot extension icon** in your Chrome toolbar

3. **Ask a question** about the current page:
   - "What is this article about?"
   - "Summarize the main points"
   - "What are the key features mentioned?"
   - "What is the conclusion of this page?"

4. **Click "Ask AI"** and wait for the response

5. **Verify the response** is relevant to the page content

### Expected Behavior

- ✅ Extension popup opens when clicked
- ✅ Text area accepts user input
- ✅ "Ask AI" button extracts page content
- ✅ API call is made to `http://localhost:8000/ask`
- ✅ AI response is displayed in the popup
- ✅ Error handling works for network issues
- ✅ Loading states are shown during processing

### Troubleshooting

**Extension not loading:**
- Check Chrome version (needs 88+)
- Verify Developer mode is enabled
- Check console for errors in `chrome://extensions/`

**API errors:**
- Ensure backend server is running on `localhost:8000`
- Check browser console for CORS or network errors
- Verify `/ask` endpoint accepts POST requests with correct format

**No text extracted:**
- Check if content script is injected (look for console logs)
- Some pages may block content script execution
- Try on different websites to isolate the issue

**Permission errors:**
- Extension needs `activeTab`, `scripting`, and `storage` permissions
- Check if host permissions include `http://localhost:8000/*`

## API Format

The extension sends POST requests to `http://localhost:8000/ask` with this format:

```json
{
  "question": "What is this page about?",
  "context": "Extracted webpage text content..."
}
```

Expected response format:
```json
{
  "answer": "AI-generated response about the webpage content"
}
```

## Development Notes

- **Manifest V3**: Uses the latest Chrome extension format
- **Content Script**: Automatically injected on all pages
- **Text Limit**: Page content is limited to ~5000 characters
- **Error Handling**: Comprehensive error handling for network and API issues
- **UI/UX**: Clean, minimal design optimized for quick interactions

## Security Considerations

- Extension only requests necessary permissions
- Content script runs in isolated context
- API calls are made to localhost only
- No sensitive data is stored locally

---

**Ready to test!** Load the extension and start asking questions about any webpage.
