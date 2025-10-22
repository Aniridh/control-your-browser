"""
LlamaIndex client for PDF text extraction, chunking and embedding.
Handles PDF processing, text extraction, and embedding generation for ScreenPilot Research Copilot.
"""

import os
import pdfplumber
import fitz  # PyMuPDF
from typing import List, Tuple, Optional
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.schema import NodeWithScore
import logging

logger = logging.getLogger(__name__)

class LlamaIndexClient:
    def __init__(self):
        """Initialize the LlamaIndex client with OpenAI embeddings."""
        self.embed_model = OpenAIEmbedding(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        )
        Settings.embed_model = self.embed_model
        
        # Configure text splitter
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
        self.text_splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using multiple methods for robustness.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            
            # Method 1: Try pdfplumber first (better for complex layouts)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                logger.info(f"Extracted text using pdfplumber: {len(text)} characters")
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}, trying PyMuPDF")
            
            # Method 2: Fallback to PyMuPDF if pdfplumber fails
            if not text.strip():
                try:
                    doc = fitz.open(file_path)
                    for page_num in range(doc.page_count):
                        page = doc[page_num]
                        page_text = page.get_text()
                        if page_text:
                            text += page_text + "\n"
                    doc.close()
                    logger.info(f"Extracted text using PyMuPDF: {len(text)} characters")
                except Exception as e:
                    logger.error(f"PyMuPDF also failed: {e}")
                    raise Exception(f"Failed to extract text from PDF: {e}")
            
            if not text.strip():
                raise Exception("No text could be extracted from the PDF")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embed_model.get_text_embedding(text)
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
        
    def build_index(self, context_text: str) -> Tuple[List[str], List[List[float]]]:
        """
        Process context text and create embeddings.
        
        Args:
            context_text: The text content to process
            
        Returns:
            Tuple of (chunk_texts, embeddings) where:
            - chunk_texts: List of text chunks
            - embeddings: List of embedding vectors
        """
        try:
            # Create document from text
            document = Document(text=context_text)
            
            # Split into chunks
            nodes = self.text_splitter.get_nodes_from_documents([document])
            
            # Generate embeddings for each chunk
            chunk_texts = []
            embeddings = []
            
            for node in nodes:
                # Get embedding for this chunk
                embedding = self.embed_model.get_text_embedding(node.text)
                
                chunk_texts.append(node.text)
                embeddings.append(embedding)
            
            logger.info(f"Created {len(chunk_texts)} chunks with embeddings")
            return chunk_texts, embeddings
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise
    
    def query_index(self, question: str, top_k: int = 3) -> List[float]:
        """
        Generate embedding for a question.
        
        Args:
            question: The question to embed
            top_k: Number of top results to return (for compatibility)
            
        Returns:
            Embedding vector for the question
        """
        try:
            embedding = self.embed_model.get_text_embedding(question)
            return embedding
        except Exception as e:
            logger.error(f"Error querying index: {str(e)}")
            raise
