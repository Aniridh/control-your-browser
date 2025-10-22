"""
ScreenPilot Backend Service
FastAPI service that processes page text and user questions using LlamaIndex, Weaviate, and Friendliai.
"""

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
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
    title="ScreenPilot Backend",
    description="AI pipeline for Chrome Extension that processes page text and answers questions",
    version="1.0.0"
)

# Add CORS middleware for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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
    context: str

class AskResponse(BaseModel):
    answer: str
    trace_id: str

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "ScreenPilot Backend is running", "status": "healthy"}

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

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Main endpoint for processing questions with context.
    
    Pipeline:
    1. Chunk and embed the context text using LlamaIndex
    2. Store embeddings in Weaviate
    3. Retrieve similar chunks for the question
    4. Generate answer using Friendliai
    5. Return answer with trace_id
    """
    try:
        logger.info(f"Processing question: {request.question[:100]}...")
        
        # Step 1: Process context text with LlamaIndex
        logger.info("Step 1: Chunking and embedding context text")
        chunk_texts, embeddings = llamaindex_client.build_index(request.context)
        
        # Step 2: Store embeddings in Weaviate
        logger.info("Step 2: Storing embeddings in Weaviate")
        doc_ids = []
        for i, (text, embedding) in enumerate(zip(chunk_texts, embeddings)):
            doc_id = weaviate_client.upsert_embedding(text, embedding)
            doc_ids.append(doc_id)
        
        # Step 3: Generate embedding for the question
        logger.info("Step 3: Generating question embedding")
        question_embedding = llamaindex_client.query_index(request.question)
        
        # Step 4: Retrieve similar chunks from Weaviate
        logger.info("Step 4: Retrieving similar chunks")
        similar_docs = weaviate_client.query_similar(question_embedding, top_k=3)
        
        # Step 5: Prepare context for Friendliai
        retrieved_context = "\n\n".join([doc["text"] for doc in similar_docs])
        logger.info(f"Retrieved {len(similar_docs)} relevant chunks")
        
        # Step 6: Generate answer using Friendliai
        logger.info("Step 6: Generating answer with Friendliai")
        result = friendliai_client.generate_answer_sync(request.question, retrieved_context)
        
        logger.info(f"Successfully processed question with trace_id: {result['trace_id']}")
        
        return AskResponse(
            answer=result["answer"],
            trace_id=result["trace_id"]
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

@app.post("/ask-async", response_model=AskResponse)
async def ask_question_async(request: AskRequest):
    """
    Async version of the ask endpoint for better performance.
    """
    try:
        logger.info(f"Processing question (async): {request.question[:100]}...")
        
        # Step 1: Process context text with LlamaIndex
        logger.info("Step 1: Chunking and embedding context text")
        chunk_texts, embeddings = llamaindex_client.build_index(request.context)
        
        # Step 2: Store embeddings in Weaviate
        logger.info("Step 2: Storing embeddings in Weaviate")
        doc_ids = []
        for i, (text, embedding) in enumerate(zip(chunk_texts, embeddings)):
            doc_id = weaviate_client.upsert_embedding(text, embedding)
            doc_ids.append(doc_id)
        
        # Step 3: Generate embedding for the question
        logger.info("Step 3: Generating question embedding")
        question_embedding = llamaindex_client.query_index(request.question)
        
        # Step 4: Retrieve similar chunks from Weaviate
        logger.info("Step 4: Retrieving similar chunks")
        similar_docs = weaviate_client.query_similar(question_embedding, top_k=3)
        
        # Step 5: Prepare context for Friendliai
        retrieved_context = "\n\n".join([doc["text"] for doc in similar_docs])
        logger.info(f"Retrieved {len(similar_docs)} relevant chunks")
        
        # Step 6: Generate answer using Friendliai (async)
        logger.info("Step 6: Generating answer with Friendliai (async)")
        result = await friendliai_client.generate_answer(request.question, retrieved_context)
        
        logger.info(f"Successfully processed question with trace_id: {result['trace_id']}")
        
        return AskResponse(
            answer=result["answer"],
            trace_id=result["trace_id"]
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
