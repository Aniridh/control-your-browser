# ScreenPilot Backend Service

A FastAPI service that powers the ScreenPilot Chrome Extension by processing page text and answering user questions using AI.

## Architecture

The service implements a complete AI pipeline:

1. **LlamaIndex**: Chunks and embeds page text using OpenAI embeddings
2. **Weaviate**: Stores and retrieves vector embeddings for similarity search
3. **Friendliai**: Generates intelligent answers based on retrieved context

## Setup

### Prerequisites

- Python 3.8+
- Weaviate instance (local or cloud)
- OpenAI API key
- Friendliai API key

### Installation

1. Clone the repository and navigate to the server directory:
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

#### Weaviate Cloud
Sign up at [Weaviate Cloud](https://console.weaviate.cloud) and use the provided URL and API key.

## Usage

### Starting the Service

```bash
python main.py
```

The service will start on `http://localhost:8000`

### API Endpoints

#### POST `/ask`
Main endpoint for processing questions with context.

**Request Body:**
```json
{
  "question": "What is the main topic of this page?",
  "context": "Long page text content..."
}
```

**Response:**
```json
{
  "answer": "The main topic is...",
  "trace_id": "uuid-trace-id"
}
```

#### POST `/ask-async`
Async version of the ask endpoint for better performance.

#### GET `/health`
Health check endpoint that verifies all service connections.

#### GET `/`
Basic health check endpoint.

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
└── utils/
    ├── llamaindex_client.py    # LlamaIndex integration
    ├── weaviate_client.py      # Weaviate vector database
    └── friendliai_client.py    # Friendliai AI service
```

### Testing

Test the service with curl:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this page about?",
    "context": "This is a sample page about artificial intelligence and machine learning..."
  }'
```

### Chrome Extension Integration

The Chrome Extension should send requests to:
- `http://localhost:8000/ask` (for development)
- `https://your-domain.com/ask` (for production)

Make sure to configure CORS settings appropriately for your deployment.

## Troubleshooting

### Common Issues

1. **Weaviate Connection Error**: Ensure Weaviate is running and accessible
2. **OpenAI API Error**: Verify your API key and quota
3. **Friendliai API Error**: Check your API key and endpoint URL
4. **Import Errors**: Ensure all dependencies are installed

### Logs

The service logs important events. Check the console output for debugging information.

### Health Check

Use the `/health` endpoint to verify all service connections are working properly.
