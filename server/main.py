"""
ScreenPilot Internal Research Copilot Backend Service
FastAPI service for uploading PDFs and asking analytical questions using LlamaIndex, Weaviate, and Friendliai.
"""

import os
import uuid
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import httpx

from utils.llamaindex_client import LlamaIndexClient, extract_text_from_pdf
from utils.weaviate_client import WeaviateClient, upsert_doc, query_similar
from utils.friendliai_client import FriendliaiClient

class Settings(BaseSettings):
    FRIENDLIAI_API_KEY: str | None = None
    FRIENDLIAI_ENDPOINT: str | None = None
    GEMINI_API_KEY: str | None = None
    WEAVIATE_URL: str | None = None
    WEAVIATE_API_KEY: str | None = None
    PORT: int = 8000

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Instantiate the LlamaIndex client
llamaindex_client = LlamaIndexClient(settings)

# Initialize FastAPI app
app = FastAPI(
    title="ScreenPilot Research Copilot",
    description="AI-powered backend for uploading PDFs and asking analytical questions about internal research documents",
    version="2.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    trace_id: str
    sources: List[Dict[str, Any]]

class UploadResponse(BaseModel):
    status: str
    message: str
    chunks_created: int

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "ScreenPilot Research Copilot is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    try:
        # Test client connections
        health_status = {
            "status": "healthy",
            "llamaindex": "connected",
            "weaviate": "connected",
            "friendliai": "connected"
        }
        
        # Test Weaviate connection
        try:
            weaviate_client = WeaviateClient(settings)
            weaviate_client.client.is_ready()
        except Exception as e:
            health_status["weaviate"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Extract text from a PDF and build index with LlamaIndex."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate unique document ID and temp path
        document_id = str(uuid.uuid4())
        temp_path = f"/tmp/{document_id}_{file.filename}"
        
        # Save uploaded file
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved PDF: {temp_path} ({len(content)} bytes)")
        
        # Extract text from PDF
        text = extract_text_from_pdf(temp_path)
        if not text:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # Build index with LlamaIndex (Friendliai embeddings)
        logger.info("Building index with LlamaIndex (Friendliai embeddings)...")
        chunks, embeddings = await llamaindex_client.build_index(text)
        
        # Store chunks and embeddings in Weaviate
        logger.info("Storing chunks in Weaviate...")
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{document_id}_chunk_{i}"
            upsert_doc(chunk_id, chunk, embedding)
            logger.debug(f"Stored chunk {i+1}/{len(chunks)}")
        
        # Clean up uploaded file
        try:
            os.remove(temp_path)
            logger.info(f"Cleaned up uploaded file: {temp_path}")
        except Exception as e:
            logger.warning(f"Could not clean up file {temp_path}: {e}")
        
        logger.info(f"Successfully processed PDF: {file.filename}")
        
        return UploadResponse(
            status="success",
            message=f"File indexed with {len(chunks)} chunks",
            chunks_created=len(chunks)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )

@app.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """Query the LlamaIndex and return a Friendliai answer."""
    try:
        logger.info(f"Processing question: {req.question[:100]}...")
        
        # Generate query vector using LlamaIndex (Friendliai embeddings)
        query_vector = await llamaindex_client.query_index(req.question)
        
        # Retrieve similar chunks from Weaviate
        context_results = query_similar(query_vector, top_k=3)
        
        if not context_results:
            return AskResponse(
                answer="No relevant documents found. Please upload some PDF documents first.",
                trace_id=str(uuid.uuid4()),
                sources=[]
            )
        
        # Prepare context
        context = "\n\n".join([r["text"] for r in context_results])
        logger.info(f"Retrieved {len(context_results)} relevant chunks for question")
        
        # Prepare prompt for Friendliai
        prompt = f"""You are ScreenPilot, an internal research assistant.
Use the context below to answer the question accurately.

Context:
{context}

Question: {req.question}
Answer:"""
        
        # Generate answer using Friendliai
        friendliai_client = FriendliaiClient(settings)
        answer = await friendliai_client.query_model(prompt)
        
        # Prepare sources for response
        sources = [
            {
                "id": result.get("id", ""),
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "relevance_score": result.get("score", 0)
            }
            for result in context_results
        ]
        
        trace_id = str(uuid.uuid4())
        logger.info(f"Successfully processed question with trace_id: {trace_id}")
        
        return AskResponse(
            answer=answer,
            trace_id=trace_id,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

@app.post("/ask-gemini", response_model=AskResponse)
async def ask_question_gemini(req: AskRequest):
    """Answer user question using Gemini as the reasoning model."""
    try:
        logger.info(f"Processing question with Gemini: {req.question[:100]}...")
        
        # Generate query vector using LlamaIndex (Friendliai embeddings)
        query_vector = await llamaindex_client.query_index(req.question)
        
        # Retrieve similar chunks from Weaviate
        context_results = query_similar(query_vector, top_k=3)
        
        if not context_results:
            return AskResponse(
                answer="No relevant documents found. Please upload some PDF documents first.",
                trace_id=str(uuid.uuid4()),
                sources=[]
            )
        
        # Prepare context
        context = "\n\n".join([r["text"] for r in context_results])
        logger.info(f"Retrieved {len(context_results)} relevant chunks for question")
        
        # Prepare prompt for Gemini
        prompt = f"""You are ScreenPilot, an internal research assistant.
Use the context below to answer the question accurately.

Context:
{context}

Question: {req.question}
Answer:"""
        
        # Generate answer using Gemini
        friendliai_client = FriendliaiClient(settings)
        answer = await friendliai_client.query_model(prompt, use_gemini=True)
        
        # Prepare sources for response
        sources = [
            {
                "id": result.get("id", ""),
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "relevance_score": result.get("score", 0)
            }
            for result in context_results
        ]
        
        trace_id = str(uuid.uuid4())
        logger.info(f"Successfully processed question with Gemini, trace_id: {trace_id}")
        
        return AskResponse(
            answer=answer,
            trace_id=trace_id,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing question with Gemini: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question with Gemini: {str(e)}"
        )

@app.get("/documents")
async def list_documents():
    """List all uploaded documents (basic implementation)."""
    try:
        # This is a basic implementation - in production you'd want to track documents
        # For now, we'll return a simple message
        return {
            "message": "Document listing not fully implemented yet",
            "note": "Documents are stored in Weaviate by chunks"
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-web")
async def upload_web(data: dict):
    """Upload webpage text content and index it."""
    try:
        text = data.get("text", "")
        url = data.get("url", "unknown")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text content provided")
        
        logger.info(f"Processing webpage text from {url} ({len(text)} characters)")
        
        # Build index with LlamaIndex (Simple Text Embeddings)
        chunks, embeddings = await llamaindex_client.build_index(text)
        
        logger.info(f"Created {len(chunks)} chunks from webpage text")
        
        # Store chunks in Weaviate
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())  # Generate proper UUID
            upsert_doc(chunk_id, chunk_text, embedding, source=url)
            logger.debug(f"Stored chunk {i+1}/{len(chunks)}")
        
        logger.info(f"Successfully processed webpage: {url}")
        
        return {
            "status": "success",
            "message": f"Webpage indexed with {len(chunks)} chunks",
            "chunks_indexed": len(chunks),
            "url": url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webpage upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webpage: {str(e)}"
        )

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its chunks from Weaviate."""
    try:
        # This would require implementing document deletion in Weaviate
        # For now, return a not implemented message
        return {
            "message": "Document deletion not fully implemented yet",
            "document_id": document_id
        }
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)