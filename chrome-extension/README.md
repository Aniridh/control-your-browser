# ScreenPilot Chrome Extension

A Chrome Extension that provides AI-powered research assistance for internal reports and documents. Upload PDFs and ask questions to get intelligent insights from your documents.

## Features

- **PDF Upload**: Upload research documents and reports (up to 10MB)
- **AI Question Answering**: Ask questions about uploaded documents
- **Clean Sidebar Interface**: Minimal, focused UI for research workflow
- **Real-time Analysis**: Instant responses from Friendliai AI backend
- **Document Processing**: Automatic text extraction and indexing

## File Structure

```
chrome-extension/
├── manifest.json      # Extension configuration (Manifest V3)
├── popup.html         # Sidebar UI with upload and question interface
├── popup.js          # Upload and AI question logic
├── content.js        # Content script (placeholder for future overlay features)
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
   - Wait for "PDF uploaded successfully!" message

3. **Ask questions about the document**:
   - Type your question in the text area
   - Examples:
     - "What are the main findings in this report?"
     - "Summarize the key recommendations"
     - "What data is presented in this document?"
     - "What are the conclusions?"
   - Click "Ask AI" button
   - Wait for AI response

4. **Verify the response** is relevant to your uploaded document

### Expected Behavior

- ✅ Extension popup opens when clicked
- ✅ PDF file selection works (only .pdf files accepted)
- ✅ File size validation (10MB limit)
- ✅ Upload button sends PDF to `/upload` endpoint
- ✅ Success message shows after upload
- ✅ Question input accepts text
- ✅ Ask AI button sends question to `/ask` endpoint
- ✅ AI response displays in the response area
- ✅ Error handling works for network issues
- ✅ Loading states are shown during operations

### Troubleshooting

**Extension not loading:**
- Check Chrome version (needs 88+)
- Verify Developer mode is enabled
- Check console for errors in `chrome://extensions/`

**Upload errors:**
- Ensure backend server is running on `localhost:8000`
- Check if `/upload` endpoint accepts multipart/form-data
- Verify PDF file is valid and under 10MB
- Check browser console for CORS or network errors

**AI question errors:**
- Ensure `/ask` endpoint is working
- Check if question is being sent correctly
- Verify backend is processing questions properly
- Check browser console for API errors

**Permission errors:**
- Extension needs `activeTab`, `scripting`, and `storage` permissions
- Check if host permissions include `http://localhost:8000/*`

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

### Ask Endpoint
**POST** `http://localhost:8000/ask`
- Content-Type: `application/json`
- Body:
```json
{
  "question": "What are the main findings?"
}
```

Expected response:
```json
{
  "answer": "AI-generated response about the document content"
}
```

## Development Notes

- **Manifest V3**: Uses the latest Chrome extension format
- **File Upload**: Uses FormData for PDF uploads
- **Error Handling**: Comprehensive error handling for network and API issues
- **UI/UX**: Clean, minimal design optimized for research workflow
- **File Validation**: PDF type and size validation
- **Loading States**: Visual feedback during operations

## Security Considerations

- Extension only requests necessary permissions
- File uploads are limited to PDF format and 10MB size
- API calls are made to localhost only
- No sensitive data is stored locally
- Content script runs in isolated context

## Future Enhancements

The content script is prepared for future overlay features:
- Document highlighting
- Inline annotations
- Context-aware suggestions
- Research assistant overlays

---

**Ready to test!** Load the extension, upload a PDF, and start asking questions about your research documents.
