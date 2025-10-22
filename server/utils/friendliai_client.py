"""
Friendliai client for AI reasoning and answer generation.
Handles communication with Friendliai API for generating answers.
"""

import os
import httpx
import uuid
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FriendliaiClient:
    def __init__(self):
        """Initialize Friendliai client with API key."""
        self.api_key = os.getenv("FRIENDLIAI_API_KEY")
        if not self.api_key:
            raise ValueError("FRIENDLIAI_API_KEY environment variable is required")
        
        self.base_url = "https://api.friendliai.com"  # Update with actual Friendliai API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_answer(self, question: str, context: str) -> Dict[str, Any]:
        """
        Generate an answer using Friendliai API.
        
        Args:
            question: The user's question
            context: The retrieved context from Weaviate
            
        Returns:
            Dictionary containing answer and trace_id
        """
        try:
            # Prepare the request payload
            payload = {
                "question": question,
                "context": context,
                "model": "gpt-4",  # You can make this configurable
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract answer from response
                answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Generate trace ID for tracking
                trace_id = str(uuid.uuid4())
                
                logger.info(f"Generated answer with trace_id: {trace_id}")
                
                return {
                    "answer": answer,
                    "trace_id": trace_id
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Friendliai API: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Friendliai API error: {e.response.status_code}")
            
        except httpx.RequestError as e:
            logger.error(f"Request error to Friendliai API: {str(e)}")
            raise Exception(f"Failed to connect to Friendliai API: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def generate_answer_sync(self, question: str, context: str) -> Dict[str, Any]:
        """
        Synchronous version of generate_answer for compatibility.
        
        Args:
            question: The user's question
            context: The retrieved context from Weaviate
            
        Returns:
            Dictionary containing answer and trace_id
        """
        try:
            # Prepare the request payload
            payload = {
                "question": question,
                "context": context,
                "model": "gpt-4",
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Make the API request synchronously
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract answer from response
                answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Generate trace ID for tracking
                trace_id = str(uuid.uuid4())
                
                logger.info(f"Generated answer with trace_id: {trace_id}")
                
                return {
                    "answer": answer,
                    "trace_id": trace_id
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Friendliai API: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Friendliai API error: {e.response.status_code}")
            
        except httpx.RequestError as e:
            logger.error(f"Request error to Friendliai API: {str(e)}")
            raise Exception(f"Failed to connect to Friendliai API: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
