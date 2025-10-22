"""
LlamaIndex client for chunking and embedding text content.
Handles text processing and embedding generation for ScreenPilot.
"""

import os
from typing import List, Tuple
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
    
    def query_index(self, question: str) -> List[float]:
        """
        Generate embedding for a question.
        
        Args:
            question: The question to embed
            
        Returns:
            Embedding vector for the question
        """
        try:
            embedding = self.embed_model.get_text_embedding(question)
            return embedding
        except Exception as e:
            logger.error(f"Error querying index: {str(e)}")
            raise
