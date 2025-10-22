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
        """Initialize Friendliai client with API keys and auto endpoint routing."""
        if settings is None:
            import os
            self.friendliai_api_key = os.getenv("FRIENDLIAI_API_KEY")
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            endpoint_env = os.getenv("FRIENDLIAI_ENDPOINT")
        else:
            self.friendliai_api_key = settings.FRIENDLIAI_API_KEY
            self.gemini_api_key = settings.GEMINI_API_KEY
            endpoint_env = getattr(settings, "FRIENDLIAI_ENDPOINT", None)
        
        if not self.friendliai_api_key:
            raise ValueError("FRIENDLIAI_API_KEY environment variable is required")
        
        # Store the endpoint for dynamic routing
        self.friendliai_endpoint = endpoint_env or "https://api.friendli.ai/v1/chat/completions"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        self.friendliai_headers = {
            "Authorization": f"Bearer {self.friendliai_api_key}",
            "Content-Type": "application/json"
        }
        
        self.gemini_headers = {
            "Content-Type": "application/json"
        }
    
    async def query_model(self, prompt: str, use_gemini: bool = False) -> str:
        """Query Friendliai or Gemini (fallback) dynamically based on .env configuration."""

        # --- Gemini fallback (optional) ---
        if use_gemini and self.gemini_api_key:
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.gemini_api_key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(gemini_url, headers=headers, params=params, json=data)
                resp.raise_for_status()
                out = resp.json()
                
                # Better error handling for Gemini response
                if "candidates" not in out or not out["candidates"]:
                    raise Exception("No candidates in Gemini response")
                
                candidate = out["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"]:
                    raise Exception("Invalid Gemini response structure")
                
                return candidate["content"]["parts"][0]["text"]

        # --- Friendliai routing ---
        endpoint = self.friendliai_endpoint
        headers = {
            "Authorization": f"Bearer {self.friendliai_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "meta-llama/Llama-3-8B-Instruct",
            "messages": [
                {"role": "system", "content": "You are ScreenPilot, an enterprise research copilot."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(endpoint, headers=headers, json=body)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
    
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
