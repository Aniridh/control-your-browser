# ScreenPilot Internal Research Copilot Backend

A FastAPI service that powers the ScreenPilot Internal Research Copilot by processing PDF documents and answering analytical questions using AI.

## 🚀 New Features

This version includes:
- **PDF Upload**: Upload internal research documents (PDFs)
- **Text Extraction**: Robust PDF text extraction using pdfplumber and PyMuPDF
- **Analytical Q&A**: Ask analytical questions about uploaded documents
- **Source Attribution**: Get answers with source document references
- **Research Insights**: AI-powered analysis using Friendliai

## Architecture

The service implements a complete research analysis pipeline:

1. **PDF Processing**: Extract text from uploaded PDF documents
2. **LlamaIndex**: Chunk and embed document text using OpenAI embeddings
3. **Weaviate**: Store and retrieve vector embeddings for similarity search
4. **Friendliai**: Generate analytical insights based on retrieved context

## Setup

### Prerequisites

- Python 3.11+
- Weaviate instance (local or cloud)
- OpenAI API key
- Friendliai API key

### Installation

1. Navigate to the server directory:
```bash
cd server
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

### Environment Variables

Required variables in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key for embeddings
- `FRIENDLIAI_API_KEY`: Your Friendliai API key
- `WEAVIATE_URL`: Weaviate instance URL (default: http://localhost:8080)
- `WEAVIATE_API_KEY`: Weaviate API key (if using cloud instance)

Optional variables:
- `EMBEDDING_MODEL`: OpenAI embedding model (default: text-embedding-ada-002)
- `CHUNK_SIZE`: Text chunk size (default: 512)
- `CHUNK_OVERLAP`: Chunk overlap (default: 50)
- `MAX_FILE_SIZE`: Maximum PDF file size in bytes (default: 10MB)

### Running Weaviate

#### Local Weaviate (Docker)
```bash
docker run -p 8080:8080 -p 50051:50051 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='' \
  -e CLUSTER_HOSTNAME='node1' \
  semitechnologies/weaviate:latest
```

## Usage

### Starting the Service

```bash
python main.py
# Or use the startup script:
./start.sh
```

The service will start on `http://localhost:8000`

### API Endpoints

#### POST `/upload`
Upload a PDF document for analysis.

**Request**: Multipart form data with PDF file
**Response**:
```json
{
  "message": "Successfully processed PDF: document.pdf",
  "document_id": "uuid-document-id",
  "pages_processed": 10,
  "chunks_created": 25
}
```

#### POST `/ask`
Ask an analytical question about uploaded documents.

**Request Body**:
```json
{
  "question": "What are the key findings in the research?"
}
```

**Response**:
```json
{
  "answer": "Based on the research documents, the key findings include...",
  "trace_id": "uuid-trace-id",
  "sources": [
    {
      "id": "doc_chunk_1",
      "text": "Relevant text excerpt...",
      "relevance_score": 0.95
    }
  ]
}
```

#### GET `/health`
Health check endpoint that verifies all service connections.

#### GET `/documents`
List uploaded documents (basic implementation).

#### DELETE `/documents/{document_id}`
Delete a document and all its chunks (basic implementation).

### API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Project Structure

```
server/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── uploads/               # Temporary PDF storage
├── README.md              # This documentation
├── start.sh              # Startup script
├── test_service.py       # Test script
└── utils/
    ├── llamaindex_client.py    # PDF processing & embeddings
    ├── weaviate_client.py      # Vector database
    └── friendliai_client.py    # AI analysis service
```

### Testing

Test the service with curl:

**Upload a PDF**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@research_document.pdf"
```

**Ask a question**:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main conclusions?"}'
```

### Frontend Integration

The service is configured for CORS with `http://localhost:3000` and `http://localhost:3001` for React frontend integration.

## Troubleshooting

### Common Issues

1. **PDF Upload Fails**: Check file size limits and PDF format
2. **Text Extraction Issues**: Ensure PDF contains extractable text (not scanned images)
3. **Weaviate Connection Error**: Verify Weaviate is running and accessible
4. **OpenAI API Error**: Check API key and quota
5. **Friendliai API Error**: Verify API key and endpoint

### Logs

The service logs important events. Check the console output for debugging information.

### Health Check

Use the `/health` endpoint to verify all service connections are working properly.

## Migration from Chrome Extension Version

This Research Copilot version is an evolution of the original Chrome Extension backend:

- **Enhanced**: Added PDF processing capabilities
- **Improved**: Better analytical prompts for research insights
- **Extended**: Source attribution and document management
- **Optimized**: Better error handling and logging

The core architecture remains the same, but with enhanced capabilities for internal research document analysis.