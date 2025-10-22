# ScreenPilot: Internal Research Copilot

ScreenPilot is an AI-powered research copilot that helps you analyze internal research documents through a Chrome extension and FastAPI backend. It combines multiple AI services to provide intelligent document analysis and question-answering capabilities.

## 🚀 Features

- **PDF Document Upload**: Upload research PDFs through a clean Chrome extension interface
- **Retrieval-Augmented Generation (RAG)**: Complete RAG pipeline with LlamaIndex, Weaviate, and Friendliai
- **AI-Powered Analysis**: Ask questions about your documents using Friendliai's advanced reasoning
- **Vector Search**: Leverage LlamaIndex and Weaviate for semantic document retrieval
- **Auto-Endpoint Routing**: Automatically detects and uses dedicated Friendliai endpoints or falls back to serverless API
- **Gemini Fallback**: Optional Gemini integration as a backup reasoning model
- **Real-time Processing**: Fast document processing and instant AI responses

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chrome        │    │   FastAPI       │    │   AI Services   │
│   Extension     │◄──►│   Backend       │◄──►│                 │
│                 │    │                 │    │ • Friendliai    │
│ • PDF Upload    │    │ • RAG Pipeline  │    │ • LlamaIndex    │
│ • Q&A Interface │    │ • PDF Processing│    │ • Weaviate      │
│ • Results Display│   │ • Embeddings    │    │ • Gemini        │
└─────────────────┘    │ • Vector Search │    └─────────────────┘
                       │ • AI Generation │
                       └─────────────────┘
```

### RAG Pipeline Flow

1. **Document Upload**: PDF → Text Extraction → Chunking → Embedding Generation
2. **Vector Storage**: Embeddings stored in Weaviate with metadata
3. **Question Processing**: Question → Embedding → Similarity Search
4. **Context Retrieval**: Top-k relevant chunks retrieved from Weaviate
5. **Answer Generation**: Context + Question → Friendliai → Structured Response

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LlamaIndex**: Document processing and embeddings
- **Weaviate**: Vector database for semantic search
- **Friendliai**: Primary AI reasoning API
- **Gemini**: Fallback AI model
- **OpenAI**: Embedding generation

### Frontend
- **Chrome Extension**: Manifest V3 extension
- **Vanilla JavaScript**: Clean, lightweight interface
- **CSS3**: Modern styling with responsive design

## 📋 Prerequisites

- Python 3.8+
- Node.js (for Chrome extension development)
- Docker (for local Weaviate instance)
- API Keys:
  - Friendliai API key
  - OpenAI API key
  - Weaviate instance (local or cloud)
  - Gemini API key (optional)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd control-your-browser
```

### 2. Set Up the Backend

```bash
cd server

# Install dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Configure Environment Variables

Edit the `.env` file with your API keys:

```env
# Friendliai Configuration
FRIENDLIAI_API_KEY=your_friendliai_api_key_here
FRIENDLIAI_ENDPOINT=https://api.friendli.ai/dedicated  # Optional: Replace with custom deployment URL

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here
LLAMAINDEX_API_KEY=your_llamaindex_api_key_here  # Optional: Falls back to OPENAI_API_KEY

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key_here  # Optional for local

# Gemini Configuration (fallback model)
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
PORT=8000
```

### 4. Start Weaviate (Local)

```bash
# Using Docker
docker run -p 8080:8080 weaviate/weaviate:latest

# Or use Weaviate Cloud (update WEAVIATE_URL in .env)
```

### 5. Start the Backend Server

```bash
# Using the startup script
./start.sh

# Or manually
python3 main.py
```

The server will be available at `http://localhost:8000`

### 6. Install the Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome-extension` directory
5. The ScreenPilot extension will appear in your toolbar

## 🧪 Testing

### Test Auto-Endpoint Routing

```bash
cd server
python3 test_endpoint_routing.py
```

### Test Full Pipeline

```bash
cd server
python3 test_full_pipeline.py
```

### Manual Testing

1. Start the backend server
2. Open the Chrome extension
3. Upload a PDF document
4. Ask questions about the content

## 🚀 Running the Full AI Pipeline

### 1. Start Weaviate (local or cloud)

**Local Weaviate:**
```bash
docker run -p 8080:8080 weaviate/weaviate:latest
```

**Weaviate Cloud:**
Update `WEAVIATE_URL` in your `.env` file to your cloud instance URL.

### 2. Run Backend

```bash
uvicorn server.main:app --reload --port 8000
```

The server will be available at `http://localhost:8000`

### 3. Upload a PDF

```bash
curl -X POST -F "file=@sample.pdf" http://localhost:8000/upload
```

**Response:**
```json
{
  "status": "success",
  "message": "File indexed with 15 chunks",
  "chunks_created": 15
}
```

### 4. Ask a Question

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "Summarize this document"}' \
  http://localhost:8000/ask
```

**Response:**
```json
{
  "answer": "Based on the research documents, the main findings include...",
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

### 5. Optional: Test Gemini Fallback

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What are the key insights?"}' \
  http://localhost:8000/ask-gemini
```

## 📚 API Endpoints

### Health Check
- `GET /health` - Check service status and connections

### Document Management
- `POST /upload` - Upload PDF documents
- `GET /documents` - List uploaded documents
- `DELETE /documents/{id}` - Delete a document

### AI Analysis
- `POST /ask` - Ask questions using Friendliai
- `POST /ask-gemini` - Ask questions using Gemini

## 🔧 Configuration

### Friendliai Endpoint Auto-Routing

By default, ScreenPilot uses the serverless Friendliai API:
```
FRIENDLIAI_ENDPOINT=https://api.friendli.ai/v1/chat/completions
```

If you have your own deployed endpoint, replace it in `.env`:
```
FRIENDLIAI_ENDPOINT=https://api.friendli.ai/v1/deployments/your-endpoint/invoke
```

### Embedding Configuration

- **Model**: OpenAI text-embedding-ada-002
- **Chunk Size**: 512 tokens (configurable)
- **Chunk Overlap**: 50 tokens (configurable)

### Vector Search

- **Database**: Weaviate with HNSW indexing
- **Distance Metric**: Cosine similarity
- **Collection**: PageContext

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Python version (3.8+ required)
   - Verify all dependencies are installed
   - Check API keys in `.env` file

2. **Chrome extension can't connect**
   - Ensure backend server is running on port 8000
   - Check CORS settings
   - Verify host permissions in manifest.json

3. **PDF upload fails**
   - Check file size (10MB limit)
   - Verify PDF is not corrupted
   - Check server logs for detailed errors

4. **AI responses are slow**
   - Check Friendliai API status
   - Verify network connectivity
   - Consider using dedicated endpoint for better performance

### Debug Mode

Enable debug logging by setting the log level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Considerations

- API keys are stored in `.env` file (never commit to version control)
- CORS is configured for localhost development
- File uploads are validated for type and size
- All API requests include proper error handling

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Use secure environment variable management
2. **HTTPS**: Enable SSL/TLS for production
3. **Database**: Use managed Weaviate instance
4. **Monitoring**: Add logging and monitoring
5. **Scaling**: Consider load balancing for high traffic

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Friendliai** for providing the AI reasoning API
- **LlamaIndex** for document processing capabilities
- **Weaviate** for vector database functionality
- **FastAPI** for the excellent web framework
- **Chrome Extensions** team for the extension platform

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation at `/docs`
- Open an issue on GitHub

---

**ScreenPilot** - Making research analysis faster and more intelligent 🚀