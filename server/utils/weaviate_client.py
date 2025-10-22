"""
Weaviate client for vector storage and retrieval.
Handles storing embeddings and performing similarity searches.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
import weaviate
from weaviate.classes.config import Property, DataType
import logging

logger = logging.getLogger(__name__)

class WeaviateClient:
    def __init__(self):
        """Initialize Weaviate client connection."""
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        # Initialize client
        auth_config = None
        if self.weaviate_api_key:
            auth_config = weaviate.AuthApiKey(api_key=self.weaviate_api_key)
        
        self.client = weaviate.Client(
            url=self.weaviate_url,
            auth_client_secret=auth_config
        )
        
        # Ensure collection exists
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create the PageContext collection if it doesn't exist."""
        collection_name = "PageContext"
        
        try:
            # Check if collection exists
            if self.client.collections.exists(collection_name):
                logger.info(f"Collection {collection_name} already exists")
                return
            
            # Create collection
            self.client.collections.create(
                name=collection_name,
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                ],
                vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
                vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw(
                    distance_metric=weaviate.classes.config.VectorDistances.COSINE
                )
            )
            logger.info(f"Created collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")
            raise
    
    def upsert_doc(self, doc_id: str, text: str, embedding: List[float]) -> str:
        """
        Store document with its embedding in Weaviate.
        
        Args:
            doc_id: Document ID
            text: The text content
            embedding: The embedding vector
            
        Returns:
            The document ID
        """
        return self.upsert_embedding(text, embedding, doc_id)
    
    def upsert_embedding(self, text: str, embedding: List[float], doc_id: Optional[str] = None) -> str:
        """
        Store text and its embedding in Weaviate.
        
        Args:
            text: The text content
            embedding: The embedding vector
            doc_id: Optional document ID, generates UUID if not provided
            
        Returns:
            The document ID
        """
        try:
            if doc_id is None:
                doc_id = str(uuid.uuid4())
            
            collection = self.client.collections.get("PageContext")
            
            # Insert document with embedding
            collection.data.insert(
                properties={"text": text},
                vector=embedding,
                uuid=doc_id
            )
            
            logger.info(f"Upserted document {doc_id} with embedding")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error upserting embedding: {str(e)}")
            raise
    
    def query_similar(self, vector: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query for similar documents using vector similarity.
        
        Args:
            vector: Query vector
            top_k: Number of top results to return
            
        Returns:
            List of similar documents with text and metadata
        """
        try:
            collection = self.client.collections.get("PageContext")
            
            # Perform vector search
            results = collection.query.near_vector(
                near_vector=vector,
                limit=top_k,
                return_metadata=["distance", "score"]
            )
            
            # Format results
            similar_docs = []
            for obj in results.objects:
                similar_docs.append({
                    "id": str(obj.uuid),
                    "text": obj.properties["text"],
                    "distance": obj.metadata.distance,
                    "score": obj.metadata.score
                })
            
            logger.info(f"Found {len(similar_docs)} similar documents")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error querying similar documents: {str(e)}")
            raise
    
    def delete_collection(self):
        """Delete the PageContext collection (useful for testing/cleanup)."""
        try:
            collection_name = "PageContext"
            if self.client.collections.exists(collection_name):
                self.client.collections.delete(collection_name)
                logger.info(f"Deleted collection {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
