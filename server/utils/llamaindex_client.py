"""
LlamaIndex client for PDF text extraction, chunking and embedding with RAG integration.
Handles PDF processing, text extraction, and embedding generation for ScreenPilot Research Copilot.
"""

import os
import pdfplumber
import uuid
import asyncio
from typing import List, Tuple, Optional, Dict, Any
from llama_index.embeddings.openai import OpenAIEmbedding
import logging

logger = logging.getLogger(__name__)

class LlamaIndexClient:
    """LlamaIndex client for PDF processing and RAG operations."""
    
    def __init__(self, settings=None):
        """Initialize LlamaIndex client with settings."""
        self.settings = settings
        self.embedder = None
        self._initialize_embedder()
    
    def _initialize_embedder(self):
        """Initialize the embedding model."""
        try:
            # Import here to avoid circular imports
            if not self.settings:
                try:
                    from main import settings
                except ImportError:
                    from server.main import settings
                self.settings = settings
            
            api_key = self.settings.LLAMAINDEX_API_KEY or self.settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OPENAI_API_KEY or LLAMAINDEX_API_KEY is required for embeddings")
            
            self.embedder = OpenAIEmbedding(api_key=api_key)
            logger.info("LlamaIndex embedder initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex embedder: {str(e)}")
            raise
    
    def build_index(self, text: str) -> Tuple[List[str], List[List[float]]]:
        """
        Build index from text by chunking and creating embeddings.
        
        Args:
            text: The text content to index
            
        Returns:
            Tuple of (chunks, embeddings)
        """
        try:
            if not self.embedder:
                self._initialize_embedder()
            
            # Create chunks (1000 characters each)
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            logger.info(f"Created {len(chunks)} chunks from text")
            
            # Generate embeddings for each chunk
            embeddings = []
            for i, chunk in enumerate(chunks):
                try:
                    emb = self.embedder.get_text_embedding(chunk)
                    embeddings.append(emb)
                    logger.debug(f"Generated embedding for chunk {i+1}/{len(chunks)}")
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {i}: {e}")
                    raise
            
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return chunks, embeddings
            
        except Exception as e:
            logger.error(f"Error in build_index: {str(e)}")
            raise
    
    def query_index(self, question: str) -> List[float]:
        """
        Generate query embedding for a question.
        
        Args:
            question: The question to generate embedding for
            
        Returns:
            Query embedding vector
        """
        try:
            if not self.embedder:
                self._initialize_embedder()
            
            q_emb = self.embedder.get_text_embedding(question)
            logger.debug(f"Generated query embedding for question: {question[:50]}...")
            return q_emb
            
        except Exception as e:
            logger.error(f"Error in query_index: {str(e)}")
            raise

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF pages."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text.strip()

async def extract_and_store_pdf(file_path: str, document_id: str) -> int:
    """Embed and store PDF text chunks into Weaviate."""
    try:
        # Import here to avoid circular imports
        from server.main import settings
        from utils.weaviate_client import upsert_doc
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        if not text:
            raise Exception("No text could be extracted from the PDF")
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # Initialize embedder
        api_key = settings.LLAMAINDEX_API_KEY or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY or LLAMAINDEX_API_KEY is required for embeddings")
        
        embedder = OpenAIEmbedding(api_key=api_key)
        
        # Create chunks (1000 characters each)
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        logger.info(f"Created {len(chunks)} chunks from PDF")
        
        # Embed and store each chunk
        for i, chunk in enumerate(chunks):
            try:
                emb = embedder.get_text_embedding(chunk)
                chunk_id = f"{document_id}_chunk_{i}"
                upsert_doc(chunk_id, chunk, emb)
                logger.debug(f"Stored chunk {i+1}/{len(chunks)}")
            except Exception as e:
                logger.error(f"Error storing chunk {i}: {e}")
                raise
        
        logger.info(f"Successfully stored {len(chunks)} chunks in Weaviate")
        return len(chunks)
        
    except Exception as e:
        logger.error(f"Error in extract_and_store_pdf: {str(e)}")
        raise

async def answer_question(question: str, use_gemini: bool = False) -> Tuple[str, str, List[dict]]:
    """Retrieve context from Weaviate and generate answer with Friendliai."""
    try:
        # Import here to avoid circular imports
        from server.main import settings
        from utils.weaviate_client import query_similar
        from utils.friendliai_client import FriendliaiClient
        
        # Initialize embedder
        api_key = settings.LLAMAINDEX_API_KEY or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY or LLAMAINDEX_API_KEY is required for embeddings")
        
        embedder = OpenAIEmbedding(api_key=api_key)
        
        # Generate question embedding
        q_emb = embedder.get_text_embedding(question)
        
        # Retrieve similar chunks from Weaviate
        matches = query_similar(q_emb, top_k=3)
        
        if not matches:
            return "No relevant documents found. Please upload some PDF documents first.", str(uuid.uuid4()), []
        
        # Prepare context
        context = "\n\n".join([m["text"] for m in matches])
        logger.info(f"Retrieved {len(matches)} relevant chunks for question")
        
        # Prepare prompt for Friendliai
        prompt = f"""You are ScreenPilot, an internal research assistant.
Use the context below to answer the question accurately.

Context:
{context}

Question: {question}
Answer:"""
        
        # Generate answer using Friendliai
        friendliai_client = FriendliaiClient(settings)
        answer = await friendliai_client.query_model(prompt, use_gemini=use_gemini)
        
        # Prepare sources for response
        sources = [
            {
                "id": match.get("id", ""),
                "text": match["text"][:200] + "..." if len(match["text"]) > 200 else match["text"],
                "relevance_score": match.get("score", 0)
            }
            for match in matches
        ]
        
        trace_id = str(uuid.uuid4())
        logger.info(f"Generated answer with trace_id: {trace_id}")
        
        return answer, trace_id, sources
        
    except Exception as e:
        logger.error(f"Error in answer_question: {str(e)}")
        raise
