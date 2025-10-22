# ScreenPilot Chrome Extension

**AI Research Copilot powered by Friendliai, LlamaIndex, and Weaviate**

A comprehensive Chrome extension that provides a sidebar interface for uploading PDF documents, asking AI-powered questions, and getting intelligent research assistance.

## 🚀 Features

### **Core Functionality**
- **📄 PDF Upload**: Drag-and-drop or click to upload research documents
- **🤖 AI Question Answering**: Ask questions about uploaded documents
- **🔍 Source Citations**: Get answers with relevant source references
- **⚡ Real-time Processing**: Instant upload and response processing
- **🎯 Context-Aware**: AI understands document content for accurate responses

### **User Interface**
- **📋 Sidebar Interface**: Clean, modern sidebar that slides in from the right
- **🎨 Responsive Design**: Works on desktop and mobile viewports
- **⌨️ Keyboard Shortcuts**: Ctrl+Shift+S to toggle sidebar
- **📱 Popup Controls**: Quick access to settings and status
- **🔄 Status Indicators**: Real-time backend connection status

### **AI Models**
- **Primary**: Friendliai (Llama-3-8B-Instruct)
- **Fallback**: Google Gemini 1.5 Pro
- **Auto-routing**: Dynamic endpoint selection based on configuration

## 📦 Installation

### **From Source (Development)**

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd control-your-browser/chrome-extension
   ```

2. **Open Chrome Extensions**:
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right)

3. **Load the Extension**:
   - Click "Load unpacked"
   - Select the `chrome-extension` directory
   - ScreenPilot will appear in your toolbar

### **Prerequisites**

- **Backend Server**: Ensure the ScreenPilot backend is running on `http://localhost:8000`
- **Chrome Browser**: Version 88+ (Manifest V3 support)
- **API Keys**: Configured in backend (Friendliai, Weaviate, OpenAI)

## 🎯 Usage

### **Opening the Sidebar**

1. **Click Extension Icon**: Click ScreenPilot in your Chrome toolbar
2. **Click "Open Sidebar"**: Opens the main interface
3. **Keyboard Shortcut**: Press `Ctrl+Shift+S` on any webpage

### **Uploading Documents**

1. **Select PDF**: Click "Choose PDF file" or drag-and-drop
2. **File Validation**: Automatic size (10MB) and type checking
3. **Upload Processing**: Real-time progress indication
4. **Success Confirmation**: Green checkmark when complete

### **Asking Questions**

1. **Type Question**: Enter your question in the text area
2. **Choose AI Model**: 
   - **Ask AI**: Uses Friendliai (default)
   - **Ask Gemini**: Uses Google Gemini (fallback)
3. **Get Response**: AI-generated answer with source citations

### **Viewing Sources**

- **Source List**: Automatically displayed below AI responses
- **Relevance Scores**: Percentage scores for each source
- **Text Excerpts**: Preview of relevant document sections

## ⚙️ Configuration

### **Backend Settings**

Access settings through the extension popup:

- **Backend URL**: Default `http://localhost:8000`
- **Auto-upload**: Automatically process PDFs
- **Sidebar Enabled**: Toggle sidebar functionality

### **Keyboard Shortcuts**

- `Ctrl+Shift+S`: Toggle sidebar visibility
- `Ctrl+Enter`: Submit question (when focused on input)

## 🏗️ Architecture

### **Manifest V3 Structure**

```
chrome-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker
├── popup.html            # Extension popup
├── popup.js              # Popup functionality
├── content.js            # Content script injection
├── overlay.js            # Sidebar functionality
├── styles.css            # Popup styling
├── overlay.css           # Sidebar styling
├── icon.png              # Extension icon
└── README.md             # This file
```

### **Communication Flow**

1. **Popup** ↔ **Background Script**: Settings and status
2. **Background Script** ↔ **Backend API**: File uploads and questions
3. **Content Script** ↔ **Overlay**: Sidebar control
4. **Overlay** ↔ **Background Script**: User interactions

### **File Processing Pipeline**

1. **PDF Upload**: File → Background Script → Backend API
2. **Text Extraction**: Backend processes PDF with LlamaIndex
3. **Vector Storage**: Embeddings stored in Weaviate
4. **Question Processing**: Question → Embedding → Similarity Search
5. **AI Generation**: Context + Question → Friendliai/Gemini → Response

## 🔧 Development

### **Local Development**

1. **Start Backend**:
   ```bash
   cd ../server
   uvicorn main:app --reload --port 8000
   ```

2. **Load Extension**:
   - Follow installation steps above
   - Enable "Developer mode"
   - Click "Load unpacked"

3. **Test Features**:
   - Upload a test PDF
   - Ask questions about content
   - Verify source citations

### **Debugging**

- **Console Logs**: Check browser DevTools for extension logs
- **Background Script**: Use `chrome://extensions/` → "Inspect views: background page"
- **Content Script**: Check page console for content script logs
- **Backend Logs**: Monitor server console for API requests

### **File Structure**

- **`manifest.json`**: Extension permissions and configuration
- **`background.js`**: Service worker for API communication
- **`popup.html/js`**: Extension popup interface
- **`content.js`**: Injects overlay into web pages
- **`overlay.js`**: Sidebar functionality and UI
- **`styles.css`**: Popup styling
- **`overlay.css`**: Sidebar styling

## 🐛 Troubleshooting

### **Common Issues**

1. **Backend Offline**:
   - Check if server is running on `http://localhost:8000`
   - Verify API keys in backend configuration
   - Check browser console for connection errors

2. **Sidebar Not Opening**:
   - Refresh the webpage
   - Check if extension is enabled
   - Try keyboard shortcut `Ctrl+Shift+S`

3. **Upload Failures**:
   - Ensure PDF file is under 10MB
   - Check file format (PDF only)
   - Verify backend is processing uploads

4. **No AI Responses**:
   - Check backend logs for API errors
   - Verify Friendliai/Gemini API keys
   - Ensure documents are properly uploaded

### **Debug Steps**

1. **Check Extension Status**: `chrome://extensions/`
2. **View Console Logs**: Browser DevTools → Console
3. **Test Backend**: Visit `http://localhost:8000/health`
4. **Reload Extension**: Click "Reload" in extension settings

## 📝 API Integration

### **Backend Endpoints**

- `POST /upload`: PDF file upload and processing
- `POST /ask`: Question answering with Friendliai
- `POST /ask-gemini`: Question answering with Gemini
- `GET /health`: Backend health check

### **Request/Response Format**

**Upload Response**:
```json
{
  "status": "success",
  "message": "File indexed with 15 chunks",
  "chunks_created": 15
}
```

**Question Response**:
```json
{
  "answer": "Based on the research documents...",
  "trace_id": "uuid-here",
  "sources": [
    {
      "id": "chunk-id",
      "text": "Relevant text excerpt...",
      "relevance_score": 0.95
    }
  ]
}
```

## 🚀 Future Enhancements

- **📊 Analytics Dashboard**: Usage statistics and insights
- **🔍 Advanced Search**: Full-text search across documents
- **📚 Document Library**: Manage multiple research collections
- **🤝 Collaboration**: Share documents and insights
- **🎨 Themes**: Customizable sidebar appearance
- **📱 Mobile Support**: Enhanced mobile experience

## 📄 License

This project is licensed under the MIT License - see the main project LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review backend logs for API errors
- Open an issue in the project repository

---

**ScreenPilot Chrome Extension** - Making AI-powered research accessible and intuitive! 🚀