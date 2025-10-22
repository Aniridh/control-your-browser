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
        
        self.base_url = "https://api.friendli.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_answer(self, question: str, context: str) -> Dict[str, Any]:
        """
        Generate an analytical insight using Friendliai API.
        
        Args:
            question: The user's analytical question
            context: The retrieved context from Weaviate
            
        Returns:
            Dictionary containing answer and trace_id
        """
        try:
            # Prepare the analytical prompt
            prompt = f"""Based on the following research documents, please provide a concise, analytical answer to the question: "{question}"

Context from documents:
{context}

Please provide:
1. A direct answer to the question
2. Key insights or findings
3. Relevant data points or evidence
4. Any limitations or caveats

Format your response as clear, human-readable insights suitable for internal research analysis."""

            # Prepare the request payload
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-70b-instruct",  # Friendli's model
                "max_tokens": 1000,
                "temperature": 0.3  # Lower temperature for analytical responses
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
                
                logger.info(f"Generated analytical answer with trace_id: {trace_id}")
                
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
            question: The user's analytical question
            context: The retrieved context from Weaviate
            
        Returns:
            Dictionary containing answer and trace_id
        """
        try:
            # Prepare the analytical prompt
            prompt = f"""Based on the following research documents, please provide a concise, analytical answer to the question: "{question}"

Context from documents:
{context}

Please provide:
1. A direct answer to the question
2. Key insights or findings
3. Relevant data points or evidence
4. Any limitations or caveats

Format your response as clear, human-readable insights suitable for internal research analysis."""

            # Prepare the request payload
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-70b-instruct",  # Friendli's model
                "max_tokens": 1000,
                "temperature": 0.3  # Lower temperature for analytical responses
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
                
                logger.info(f"Generated analytical answer with trace_id: {trace_id}")
                
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
