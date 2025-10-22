"""
Weaviate client for vector storage and retrieval with RAG integration.
Handles storing embeddings from LlamaIndex and performing similarity searches.
Compatible with Weaviate Python Client v4.
"""

import os
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.collections import Collection
from weaviate.collections.classes.config import Configure, Property, DataType
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WeaviateClient:
    """Weaviate v4 client wrapper for ScreenPilot."""

    def __init__(self, settings=None):
        """Initialize Weaviate client with proper v4 syntax."""
        try:
            # Get settings if not provided
            if not settings:
                try:
                    from main import settings
                except ImportError:
                    from server.main import settings
            
            api_key = settings.WEAVIATE_API_KEY if settings else os.getenv("WEAVIATE_API_KEY")
            cluster_url = settings.WEAVIATE_URL if settings else os.getenv("WEAVIATE_URL")

            if api_key and cluster_url and cluster_url.startswith("https"):
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=cluster_url,
                    auth_credentials=AuthApiKey(api_key),
                )
                logger.info("Connected to Weaviate Cloud")
            else:
                # Local Docker connection with HTTP only (no gRPC)
                self.client = weaviate.connect_to_local(
                    host="localhost",
                    port=8080,
                    skip_init_checks=True
                )
                logger.info("Connected to local Weaviate instance (HTTP only)")

            self.init_schema()
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise RuntimeError(f"Failed to connect to Weaviate: {e}")

    def init_schema(self):
        """Create the PageContext collection if it does not exist."""
        try:
            # Check if collection exists using the exists method
            if self.client.collections.exists("PageContext"):
                logger.info("PageContext collection already exists")
                return
            
            # Create collection
            self.client.collections.create(
                name="PageContext",
                vectorizer_config=Configure.Vectorizer.none(),
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                ],
            )
            logger.info("Created PageContext collection")
            
        except Exception as e:
            logger.error(f"Error initializing schema: {str(e)}")
            raise

    def upsert_embedding(self, text: str, embedding: list, doc_id: Optional[str] = None):
        """Insert a document and its vector embedding."""
        try:
            collection: Collection = self.client.collections.get("PageContext")
            
            # Generate UUID if not provided
            if doc_id is None:
                import uuid
                doc_id = str(uuid.uuid4())
            
            obj = collection.data.insert(
                properties={"text": text, "source": doc_id},
                vector=embedding,
                uuid=doc_id
            )
            
            logger.debug(f"Upserted document {doc_id} with embedding")
            return str(obj)  # Fixed: obj instead of obj.uuid
            
        except Exception as e:
            logger.error(f"Error upserting embedding: {str(e)}")
            raise

    def query_similar(self, embedding: list, top_k: int = 3):
        """Retrieve most similar chunks."""
        try:
            collection: Collection = self.client.collections.get("PageContext")
            res = collection.query.near_vector(
                near_vector=embedding, 
                limit=top_k,
                return_metadata=["distance", "score"]
            )
            
            similar_docs = []
            for obj in res.objects:
                similar_docs.append({
                    "id": str(obj.uuid),
                    "text": obj.properties.get("text", ""),
                    "source": obj.properties.get("source", ""),
                    "distance": obj.metadata.distance,
                    "score": obj.metadata.score
                })
            
            logger.debug(f"Found {len(similar_docs)} similar documents")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error querying similar documents: {str(e)}")
            raise

    def upsert_doc(self, doc_id: str, text: str, embedding: List[float]) -> str:
        """Store document with its embedding in Weaviate."""
        return self.upsert_embedding(text, embedding, doc_id)
    
    def delete_collection(self):
        """Delete the PageContext collection (useful for testing/cleanup)."""
        try:
            if self.client.collections.exists("PageContext"):
                self.client.collections.delete("PageContext")
                logger.info("Deleted PageContext collection")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise

    def is_ready(self):
        """Check if Weaviate is ready."""
        try:
            return self.client.is_ready()
        except Exception as e:
            logger.error(f"Error checking Weaviate readiness: {str(e)}")
            return False

    def close(self):
        """Close Weaviate connection gracefully."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("Closed Weaviate client connection")
        except Exception as e:
            logger.error(f"Error closing Weaviate client: {str(e)}")


# Standalone functions for backward compatibility
def get_client():
    """Get Weaviate client using settings configuration."""
    try:
        from main import settings
    except ImportError:
        from server.main import settings
    
    # Create a temporary client instance
    client_instance = WeaviateClient(settings)
    return client_instance.client

def upsert_doc(doc_id: str, text: str, embedding: List[float]) -> str:
    """Store document with its embedding in Weaviate."""
    try:
        client_instance = WeaviateClient()
        return client_instance.upsert_doc(doc_id, text, embedding)
    except Exception as e:
        logger.error(f"Error upserting document: {str(e)}")
        raise

def query_similar(embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """Query for similar documents using vector similarity."""
    try:
        client_instance = WeaviateClient()
        return client_instance.query_similar(embedding, top_k)
    except Exception as e:
        logger.error(f"Error querying similar documents: {str(e)}")
        raise