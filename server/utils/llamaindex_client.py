"""
LlamaIndex client for PDF text extraction, chunking and embedding with proper LlamaIndex integration.
Handles PDF processing, text extraction, and embedding generation for ScreenPilot Research Copilot.
"""

import os
import pdfplumber
from typing import List, Tuple, Optional
from llama_index.core import Document, VectorStoreIndex, ServiceContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.schema import NodeWithScore
import logging

logger = logging.getLogger(__name__)

class LlamaIndexClient:
    def __init__(self):
        """Initialize the LlamaIndex client with OpenAI embeddings."""
        self.embed_model = self.get_embedding_model()
        
        # Configure text splitter
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
        self.text_splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def get_embedding_model(self):
        """Get the OpenAI embedding model."""
        return OpenAIEmbedding(model="text-embedding-3-small")
    
    def create_index_from_text(self, text: str) -> VectorStoreIndex:
        """Build a LlamaIndex index from text (chunked)."""
        try:
            # Create document from text
            docs = [Document(text=text)]
            
            # Create service context with embedding model
            service_context = ServiceContext.from_defaults(
                embed_model=self.embed_model,
                node_parser=self.text_splitter
            )
            
            # Create vector store index
            index = VectorStoreIndex.from_documents(
                docs, 
                service_context=service_context
            )
            
            logger.info(f"Created LlamaIndex with {len(docs)} documents")
            return index
            
        except Exception as e:
            logger.error(f"Error creating LlamaIndex: {str(e)}")
            raise
    
    def query_index(self, index: VectorStoreIndex, question: str) -> str:
        """Simple retrieval query using LlamaIndex."""
        try:
            query_engine = index.as_query_engine()
            response = query_engine.query(question)
            return str(response.response)
        except Exception as e:
            logger.error(f"Error querying LlamaIndex: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using pdfplumber.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"Extracted text using pdfplumber: {len(text)} characters")
            
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
    
    def build_index(self, context_text: str) -> Tuple[List[str], List[List[float]]]:
        """
        Process context text and create embeddings using LlamaIndex.
        
        Args:
            context_text: The text content to process
            
        Returns:
            Tuple of (chunk_texts, embeddings) where:
            - chunk_texts: List of text chunks
            - embeddings: List of embedding vectors
        """
        try:
            # Create LlamaIndex from text
            index = self.create_index_from_text(context_text)
            
            # Get nodes from the index
            nodes = index.docstore.get_nodes(list(index.docstore.docs.keys()))
            
            # Generate embeddings for each chunk
            chunk_texts = []
            embeddings = []
            
            for node in nodes:
                # Get embedding for this chunk
                embedding = self.embed_model.get_text_embedding(node.text)
                
                chunk_texts.append(node.text)
                embeddings.append(embedding)
            
            logger.info(f"Created {len(chunk_texts)} chunks with embeddings using LlamaIndex")
            return chunk_texts, embeddings
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise
    
    def get_question_embedding(self, question: str) -> List[float]:
        """
        Generate embedding for a question using LlamaIndex embedding model.
        
        Args:
            question: The question to embed
            
        Returns:
            Embedding vector for the question
        """
        try:
            embedding = self.embed_model.get_text_embedding(question)
            return embedding
        except Exception as e:
            logger.error(f"Error generating question embedding: {str(e)}")
            raise
