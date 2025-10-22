"""
ScreenPilot Research Copilot Utils Package

This package contains utility modules for the ScreenPilot Research Copilot backend:
- friendliai_client: AI reasoning with Friendliai and Gemini fallback
- llamaindex_client: PDF processing and LlamaIndex integration
- weaviate_client: Vector storage and retrieval
"""

from .friendliai_client import FriendliaiClient
from .llamaindex_client import LlamaIndexClient
from .weaviate_client import WeaviateClient

__all__ = [
    "FriendliaiClient",
    "LlamaIndexClient", 
    "WeaviateClient"
]
