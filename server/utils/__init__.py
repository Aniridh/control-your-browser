"""
ScreenPilot Research Copilot Utils Package

This package contains utility modules for the ScreenPilot Research Copilot backend:
- friendliai_client: AI reasoning with Friendliai and Gemini fallback
- llamaindex_client: PDF processing and RAG integration functions
- weaviate_client: Vector storage and retrieval
"""

from .friendliai_client import FriendliaiClient
from .llamaindex_client import LlamaIndexClient, extract_text_from_pdf, extract_and_store_pdf, answer_question
from .weaviate_client import WeaviateClient, upsert_doc, query_similar

__all__ = [
    "FriendliaiClient",
    "LlamaIndexClient",
    "extract_text_from_pdf",
    "extract_and_store_pdf", 
    "answer_question",
    "WeaviateClient",
    "upsert_doc",
    "query_similar"
]
