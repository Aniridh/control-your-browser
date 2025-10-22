"""
LlamaIndex client for PDF processing and RAG operations.
Now uses Friendliai exclusively for both embeddings and reasoning.
"""

import os
import httpx
import logging
from typing import List, Tuple, Optional
import uuid

logger = logging.getLogger(__name__)

class LlamaIndexClient:
    """
    LlamaIndexClient now uses Friendliai embeddings directly.
    Handles PDF text extraction, chunking, and Friendliai embedding generation.
    """

    def __init__(self, settings=None):
        """Initialize LlamaIndex client with Friendliai embeddings."""
        try:
            # Get settings if not provided
            if not settings:
                try:
                    from main import settings
                except ImportError:
                    from server.main import settings
            
            self.friendliai_api_key = settings.FRIENDLIAI_API_KEY if settings else os.getenv("FRIENDLIAI_API_KEY")
            self.friendliai_endpoint = settings.FRIENDLIAI_ENDPOINT if settings else os.getenv("FRIENDLIAI_ENDPOINT")
            
            if not self.friendliai_api_key:
                raise ValueError("FRIENDLIAI_API_KEY is missing from environment.")
            
            # Set embedding endpoint
            if self.friendliai_endpoint and self.friendliai_endpoint.startswith("https://api.friendli.ai"):
                # Use dedicated endpoint for embeddings
                self.embed_url = self.friendliai_endpoint.replace("/chat/completions", "/embeddings")
            else:
                # Use default serverless endpoint
                self.embed_url = "https://api.friendli.ai/v1/embeddings"
            
            logger.info("✅ LlamaIndex (Friendliai) embedder initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex embedder: {str(e)}")
            raise

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Friendliai API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.friendliai_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "input": text,
                "model": "meta-llama/Llama-3-8B-Instruct"
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self.embed_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["data"][0]["embedding"]
                
        except Exception as e:
            logger.error(f"Error getting embedding from Friendliai: {str(e)}")
            raise

    async def build_index(self, context_text: str) -> Tuple[List[str], List[List[float]]]:
        """
        Chunk the input context and create Friendliai embeddings for each chunk.
        
        Args:
            context_text: The text content to index
            
        Returns:
            Tuple of (chunks, embeddings)
        """
        try:
            chunks = [context_text[i:i+1000] for i in range(0, len(context_text), 1000)]
            logger.info(f"Created {len(chunks)} chunks from text")
            
            embeddings = []
            for i, chunk in enumerate(chunks):
                try:
                    emb = await self._get_embedding(chunk)
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

    async def query_index(self, question: str) -> List[float]:
        """
        Generate query embedding for a question using Friendliai.
        
        Args:
            question: The question to generate embedding for
            
        Returns:
            Query embedding vector
        """
        try:
            q_emb = await self._get_embedding(question)
            logger.debug(f"Generated query embedding for question: {question[:50]}...")
            return q_emb
            
        except Exception as e:
            logger.error(f"Error in query_index: {str(e)}")
            raise


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using pdfplumber.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        import pdfplumber
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise