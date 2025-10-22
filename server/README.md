# ScreenPilot Research Copilot Backend

A FastAPI service for uploading PDFs and asking analytical questions about research documents.

### Environment Setup
1. Copy `.env.example` → `.env`
2. Fill in your API keys.
3. Run tests:
   ```bash
   uv run python test_env.py
   ```
4. Start backend:
   ```bash
   uvicorn server.main:app --reload --port 8000
   ```

## Setup & Run Instructions

```bash
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8000
```

## Example Usage

Upload a PDF:
```bash
curl -X POST -F "file=@report.pdf" http://localhost:8000/upload
```

Ask a question:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"question":"summarize key findings"}' http://localhost:8000/ask
```
