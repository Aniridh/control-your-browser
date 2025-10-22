# ScreenPilot Research Copilot Backend

A FastAPI service for uploading PDFs and asking analytical questions about research documents.

## Setup & Run Instructions

```bash
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8000
```

## Environment Variables

Create a `.env` file in `server/` based on `.env.example`:

- `FRIENDLIAI_API_KEY` — required
- `FRIENDLIAI_ENDPOINT_URL` — optional; if set, the backend will prefer this dedicated endpoint and automatically fall back to serverless if unreachable
- `GEMINI_API_KEY` — optional; enables Gemini fallback
- `WEAVIATE_URL` — required for vector store
- `WEAVIATE_API_KEY` — optional depending on your Weaviate setup

## Auto Endpoint Routing (Friendliai)

The backend automatically selects the Friendliai endpoint:
- If `FRIENDLIAI_ENDPOINT_URL` is provided and reachable, it is used
- Otherwise, the serverless API `https://api.friendli.ai` is used

A lightweight probe to `GET {endpoint}/v1/models` is performed to validate reachability.

## Example Usage

Upload a PDF:
```bash
curl -X POST -F "file=@report.pdf" http://localhost:8000/upload
```

Ask a question:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"question":"summarize key findings"}' http://localhost:8000/ask
```
