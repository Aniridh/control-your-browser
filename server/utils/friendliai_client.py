"""
Friendliai client for AI reasoning and answer generation with Gemini fallback.
Handles communication with Friendliai API and Gemini API for generating answers.
"""

import os
import httpx
import uuid
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FriendliaiClient:
    def __init__(self, settings=None):
        """Initialize Friendliai client with API keys."""
        if settings is None:
            import os
            self.friendliai_api_key = os.getenv("FRIENDLIAI_API_KEY")
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        else:
            self.friendliai_api_key = settings.FRIENDLIAI_API_KEY
            self.gemini_api_key = settings.GEMINI_API_KEY
        
        if not self.friendliai_api_key:
            raise ValueError("FRIENDLIAI_API_KEY environment variable is required")
        
        self.friendliai_base_url = "https://api.friendli.ai"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        self.friendliai_headers = {
            "Authorization": f"Bearer {self.friendliai_api_key}",
            "Content-Type": "application/json"
        }
        
        self.gemini_headers = {
            "Content-Type": "application/json"
        }
    
    async def query_model(self, prompt: str, use_gemini: bool = False) -> str:
        """
        Query either Friendliai or Gemini model based on use_gemini flag.
        
        Args:
            prompt: The prompt to send to the model
            use_gemini: If True, use Gemini; if False, use Friendliai
            
        Returns:
            Generated response text
        """
        try:
            if use_gemini:
                return await self._query_gemini(prompt)
            else:
                return await self._query_friendliai(prompt)
        except Exception as e:
            logger.error(f"Error querying model: {str(e)}")
            # Fallback to the other model if one fails
            if use_gemini:
                logger.info("Gemini failed, falling back to Friendliai")
                return await self._query_friendliai(prompt)
            else:
                logger.info("Friendliai failed, falling back to Gemini")
                return await self._query_gemini(prompt)
    
    async def _query_friendliai(self, prompt: str) -> str:
        """Query Friendliai API."""
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "llama-3.1-70b-instruct",
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.friendliai_base_url}/v1/chat/completions",
                headers=self.friendliai_headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini API."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini fallback")
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }
        
        url = f"{self.gemini_base_url}/models/gemini-1.5-pro:generateContent?key={self.gemini_api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.gemini_headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    
    async def generate_answer(self, question: str, context: str, use_gemini: bool = False) -> Dict[str, Any]:
        """
        Generate an analytical insight using Friendliai or Gemini API.
        
        Args:
            question: The user's analytical question
            context: The retrieved context from Weaviate
            use_gemini: If True, use Gemini; if False, use Friendliai
            
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

            # Generate answer using the selected model
            answer = await self.query_model(prompt, use_gemini=use_gemini)
            
            # Generate trace ID for tracking
            trace_id = str(uuid.uuid4())
            
            logger.info(f"Generated analytical answer with trace_id: {trace_id} using {'Gemini' if use_gemini else 'Friendliai'}")
            
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
    
    def generate_answer_sync(self, question: str, context: str, use_gemini: bool = False) -> Dict[str, Any]:
        """
        Synchronous version of generate_answer for compatibility.
        
        Args:
            question: The user's analytical question
            context: The retrieved context from Weaviate
            use_gemini: If True, use Gemini; if False, use Friendliai
            
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

            # Generate answer using the selected model (synchronous)
            answer = self._query_model_sync(prompt, use_gemini=use_gemini)
            
            # Generate trace ID for tracking
            trace_id = str(uuid.uuid4())
            
            logger.info(f"Generated analytical answer with trace_id: {trace_id} using {'Gemini' if use_gemini else 'Friendliai'}")
            
            return {
                "answer": answer,
                "trace_id": trace_id
            }
                
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def _query_model_sync(self, prompt: str, use_gemini: bool = False) -> str:
        """Synchronous version of query_model."""
        try:
            if use_gemini:
                return self._query_gemini_sync(prompt)
            else:
                return self._query_friendliai_sync(prompt)
        except Exception as e:
            logger.error(f"Error querying model: {str(e)}")
            # Fallback to the other model if one fails
            if use_gemini:
                logger.info("Gemini failed, falling back to Friendliai")
                return self._query_friendliai_sync(prompt)
            else:
                logger.info("Friendliai failed, falling back to Gemini")
                return self._query_gemini_sync(prompt)
    
    def _query_friendliai_sync(self, prompt: str) -> str:
        """Synchronous query to Friendliai API."""
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "llama-3.1-70b-instruct",
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.friendliai_base_url}/v1/chat/completions",
                headers=self.friendliai_headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _query_gemini_sync(self, prompt: str) -> str:
        """Synchronous query to Gemini API."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini fallback")
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }
        
        url = f"{self.gemini_base_url}/models/gemini-1.5-pro:generateContent?key={self.gemini_api_key}"
        
        with httpx.Client() as client:
            response = client.post(
                url,
                headers=self.gemini_headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
