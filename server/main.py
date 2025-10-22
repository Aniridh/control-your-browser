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
from dotenv import load_dotenv

from utils.llamaindex_client import LlamaIndexClient
from utils.weaviate_client import WeaviateClient
from utils.friendliai_client import FriendliaiClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ScreenPilot Research Copilot",
    description="AI-powered backend for uploading PDFs and asking analytical questions about internal research documents",
    version="2.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
try:
    llamaindex_client = LlamaIndexClient()
    weaviate_client = WeaviateClient()
    friendliai_client = FriendliaiClient()
    logger.info("All clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize clients: {str(e)}")
    raise

# Pydantic models
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    trace_id: str
    sources: List[Dict[str, Any]]

class UploadResponse(BaseModel):
    message: str
    document_id: str
    pages_processed: int
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
    """
    Upload a PDF document for analysis.
    
    Pipeline:
    1. Save PDF to uploads directory
    2. Extract text using LlamaIndex
    3. Chunk text and create embeddings
    4. Store embeddings in Weaviate
    5. Return processing summary
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        file_path = f"uploads/{document_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved PDF: {file_path} ({len(content)} bytes)")
        
        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        extracted_text = llamaindex_client.extract_text_from_pdf(file_path)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Process text and create embeddings
        logger.info("Processing text and creating embeddings...")
        chunk_texts, embeddings = llamaindex_client.build_index(extracted_text)
        
        # Store embeddings in Weaviate
        logger.info(f"Storing {len(chunk_texts)} chunks in Weaviate...")
        stored_chunks = 0
        for i, (text, embedding) in enumerate(zip(chunk_texts, embeddings)):
            chunk_id = f"{document_id}_chunk_{i}"
            weaviate_client.upsert_doc(chunk_id, text, embedding)
            stored_chunks += 1
        
        # Clean up uploaded file (optional - you might want to keep it)
        try:
            os.remove(file_path)
            logger.info(f"Cleaned up uploaded file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not clean up file {file_path}: {e}")
        
        logger.info(f"Successfully processed PDF: {file.filename}")
        
        return UploadResponse(
            message=f"Successfully processed PDF: {file.filename}",
            document_id=document_id,
            pages_processed=len(extracted_text.split('\n')),  # Rough estimate
            chunks_created=stored_chunks
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
async def ask_question(request: AskRequest):
    """
    Ask an analytical question about uploaded documents.
    
    Pipeline:
    1. Generate embedding for the question
    2. Retrieve similar chunks from Weaviate
    3. Generate analytical answer using Friendliai
    4. Return answer with sources
    """
    try:
        logger.info(f"Processing analytical question: {request.question[:100]}...")
        
        # Generate embedding for the question using LlamaIndex
        logger.info("Generating question embedding using LlamaIndex...")
        question_embedding = llamaindex_client.get_question_embedding(request.question)
        
        # Retrieve similar chunks from Weaviate
        logger.info("Retrieving relevant document chunks...")
        similar_docs = weaviate_client.query_similar(question_embedding, top_k=5)
        
        if not similar_docs:
            return AskResponse(
                answer="No relevant documents found. Please upload some PDF documents first.",
                trace_id=str(uuid.uuid4()),
                sources=[]
            )
        
        # Prepare context for Friendliai
        retrieved_context = "\n\n".join([doc["text"] for doc in similar_docs])
        logger.info(f"Retrieved {len(similar_docs)} relevant chunks")
        
        # Generate analytical answer using Friendliai (with Gemini fallback option)
        logger.info("Generating analytical answer with Friendliai...")
        result = await friendliai_client.generate_answer(request.question, retrieved_context, use_gemini=False)
        
        # Prepare sources for response
        sources = [
            {
                "id": doc["id"],
                "text": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                "relevance_score": doc.get("score", 0)
            }
            for doc in similar_docs
        ]
        
        logger.info(f"Successfully processed question with trace_id: {result['trace_id']}")
        
        return AskResponse(
            answer=result["answer"],
            trace_id=result["trace_id"],
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

@app.post("/ask-gemini", response_model=AskResponse)
async def ask_question_gemini(request: AskRequest):
    """
    Ask an analytical question using Gemini as the reasoning model.
    This endpoint is for testing Gemini fallback functionality.
    """
    try:
        logger.info(f"Processing analytical question with Gemini: {request.question[:100]}...")
        
        # Generate embedding for the question using LlamaIndex
        logger.info("Generating question embedding using LlamaIndex...")
        question_embedding = llamaindex_client.get_question_embedding(request.question)
        
        # Retrieve similar chunks from Weaviate
        logger.info("Retrieving relevant document chunks...")
        similar_docs = weaviate_client.query_similar(question_embedding, top_k=5)
        
        if not similar_docs:
            return AskResponse(
                answer="No relevant documents found. Please upload some PDF documents first.",
                trace_id=str(uuid.uuid4()),
                sources=[]
            )
        
        # Prepare context for Gemini
        retrieved_context = "\n\n".join([doc["text"] for doc in similar_docs])
        logger.info(f"Retrieved {len(similar_docs)} relevant chunks")
        
        # Generate analytical answer using Gemini
        logger.info("Generating analytical answer with Gemini...")
        result = await friendliai_client.generate_answer(request.question, retrieved_context, use_gemini=True)
        
        # Prepare sources for response
        sources = [
            {
                "id": doc["id"],
                "text": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                "relevance_score": doc.get("score", 0)
            }
            for doc in similar_docs
        ]
        
        logger.info(f"Successfully processed question with Gemini, trace_id: {result['trace_id']}")
        
        return AskResponse(
            answer=result["answer"],
            trace_id=result["trace_id"],
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
    uvicorn.run(app, host="0.0.0.0", port=8000)