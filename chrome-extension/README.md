# ScreenPilot Chrome Extension

A Chrome Extension that provides AI-powered research assistance with PDF upload and webpage analysis capabilities. Upload documents or analyze current webpages to get intelligent insights from your content.

## Features

- **PDF Upload**: Upload research documents and reports directly to the backend
- **Webpage Analysis**: Extract and analyze text content from any webpage
- **AI Question Answering**: Ask questions about uploaded documents and analyzed pages
- **Floating Overlay**: Contextual AI responses appear as floating boxes on webpages
- **Real-time Status**: Clear status indicators for all operations
- **Clean Sidebar Interface**: Minimal, focused UI for research workflow

## File Structure

```
chrome-extension/
├── manifest.json      # Extension configuration (Manifest V3)
├── popup.html         # Sidebar UI with upload, analyze, and question interface
├── popup.js          # Upload, webpage analysis, and AI question logic
├── content.js        # Content script for overlay system
├── overlay.js        # Floating suggestion box implementation
├── overlay.css       # Overlay styling
├── styles.css        # Clean minimal styling
├── icon.png          # Extension icon
└── README.md         # This file
```

## Installation & Testing

### Prerequisites

1. **Backend API**: Ensure your backend server is running at `http://localhost:8000`
2. **Chrome Browser**: Chrome version 88+ (for Manifest V3 support)
3. **PDF Files**: Have some PDF documents ready for testing

### Installation Steps

1. **Download/Clone** this extension to your local machine

2. **Start Backend Server** (if not already running):
   ```bash
   # Your backend should be running on localhost:8000
   # Required endpoints:
   # - POST /upload (for PDF upload)
   # - POST /upload-web (for webpage analysis)
   # - POST /ask (for AI questions)
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

1. **Click the ScreenPilot extension icon** in your Chrome toolbar

2. **Upload a PDF document**:
   - Click "Choose PDF file" in the upload area
   - Select a PDF document from your computer
   - Click "Upload" button
   - Wait for "✅ Uploaded successfully" message

3. **Analyze a webpage**:
   - Navigate to any webpage you want to analyze
   - Click the ScreenPilot extension icon
   - Click "Analyze This Page" button
   - Wait for "✅ Page indexed" message with chunk count

4. **Ask questions about your content**:
   - Type your question in the text area
   - Examples:
     - "What are the main findings in this document?"
     - "Summarize the key points from the analyzed page"
     - "What data is presented in the uploaded PDF?"
     - "What are the conclusions?"
   - Click "Ask AI" button
   - Wait for AI response in both popup and floating overlay

5. **Verify responses** are relevant to your uploaded/analyzed content

### Expected Behavior

- ✅ Extension popup opens when clicked
- ✅ PDF file selection works (only .pdf files accepted)
- ✅ Upload button sends PDF to `/upload` endpoint
- ✅ "Analyze This Page" extracts text from current tab
- ✅ Page analysis sends data to `/upload-web` endpoint
- ✅ Question input accepts text
- ✅ Ask AI button sends question to `/ask` endpoint
- ✅ AI response displays in popup AND floating overlay
- ✅ Status bar shows real-time operation feedback
- ✅ Error handling works for network issues

### Troubleshooting

**Extension not loading:**
- Check Chrome version (needs 88+)
- Verify Developer mode is enabled
- Check console for errors in `chrome://extensions/`

**Upload errors:**
- Ensure backend server is running on `localhost:8000`
- Check if `/upload` endpoint accepts multipart/form-data
- Verify PDF file is valid
- Check browser console for CORS or network errors

**Page analysis errors:**
- Ensure `/upload-web` endpoint is working
- Check if page has extractable text content
- Verify scripting permissions are granted
- Check browser console for API errors

**AI question errors:**
- Ensure `/ask` endpoint is working
- Check if documents have been uploaded/analyzed first
- Verify backend is processing questions properly
- Check browser console for API errors

**Permission errors:**
- Extension needs `activeTab`, `scripting`, and `storage` permissions
- Check if host permissions include `http://localhost:8000/*`, `https://*/*`, `http://*/*`

## API Format

### Upload Endpoint
**POST** `http://localhost:8000/upload`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

Expected response:
```json
{
  "message": "File uploaded successfully",
  "file_id": "unique_file_identifier"
}
```

### Webpage Analysis Endpoint
**POST** `http://localhost:8000/upload-web`
- Content-Type: `application/json`
- Body:
```json
{
  "text": "extracted webpage text content...",
  "url": "https://example.com/page"
}
```

Expected response:
```json
{
  "message": "Webpage indexed successfully",
  "chunks_indexed": 15
}
```

### Ask Endpoint
**POST** `http://localhost:8000/ask`
- Content-Type: `application/json`
- Body:
```json
{
  "question": "What are the main findings?",
  "context": ""
}
```

Expected response:
```json
{
  "answer": "AI-generated response about the content"
}
```

## Development Notes

- **Manifest V3**: Uses the latest Chrome extension format
- **File Upload**: Uses FormData for PDF uploads
- **Page Analysis**: Uses chrome.scripting.executeScript for text extraction
- **Overlay System**: Floating boxes appear on webpages with AI responses
- **Error Handling**: Comprehensive error handling for network and API issues
- **UI/UX**: Clean, minimal design optimized for research workflow
- **Status Feedback**: Real-time status updates for all operations

## Security Considerations

- Extension only requests necessary permissions
- File uploads are limited to PDF format
- Page analysis extracts only visible text content
- API calls are made to localhost only (configurable)
- No sensitive data is stored locally
- Content script runs in isolated context

## Future Enhancements

The extension is prepared for additional features:
- Document highlighting and annotations
- Context-aware suggestions
- Multi-document analysis
- Export capabilities
- Advanced search and filtering

---

**Ready to test!** Load the extension, upload PDFs or analyze webpages, and start asking questions about your content.