"""
Test script for ScreenPilot Backend Service
Run this to test the service endpoints locally.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Health Check Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Health check failed: {e}")

async def test_ask():
    """Test the ask endpoint."""
    test_data = {
        "question": "What is the main topic of this text?",
        "context": """
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that can perform tasks that typically require human intelligence. 
        These tasks include learning, reasoning, problem-solving, perception, and language understanding.
        
        Machine Learning is a subset of AI that focuses on the development of algorithms 
        that can learn and make decisions from data. Deep Learning, in turn, is a subset 
        of machine learning that uses neural networks with multiple layers to model and 
        understand complex patterns in data.
        
        The applications of AI are vast and growing, including autonomous vehicles, 
        medical diagnosis, financial trading, and natural language processing.
        """
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/ask",
                json=test_data,
                timeout=60.0
            )
            print(f"Ask Endpoint Status: {response.status_code}")
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Trace ID: {result['trace_id']}")
        except Exception as e:
            print(f"Ask endpoint failed: {e}")

async def test_ask_async():
    """Test the async ask endpoint."""
    test_data = {
        "question": "What are the key applications mentioned?",
        "context": """
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that can perform tasks that typically require human intelligence. 
        These tasks include learning, reasoning, problem-solving, perception, and language understanding.
        
        Machine Learning is a subset of AI that focuses on the development of algorithms 
        that can learn and make decisions from data. Deep Learning, in turn, is a subset 
        of machine learning that uses neural networks with multiple layers to model and 
        understand complex patterns in data.
        
        The applications of AI are vast and growing, including autonomous vehicles, 
        medical diagnosis, financial trading, and natural language processing.
        """
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/ask-async",
                json=test_data,
                timeout=60.0
            )
            print(f"Ask Async Endpoint Status: {response.status_code}")
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Trace ID: {result['trace_id']}")
        except Exception as e:
            print(f"Ask async endpoint failed: {e}")

async def main():
    """Run all tests."""
    print("Testing ScreenPilot Backend Service")
    print("=" * 50)
    
    print("\n1. Testing Health Check...")
    await test_health()
    
    print("\n2. Testing Ask Endpoint...")
    await test_ask()
    
    print("\n3. Testing Ask Async Endpoint...")
    await test_ask_async()
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
