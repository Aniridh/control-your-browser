"""
Test script for ScreenPilot Research Copilot Backend Service
Run this to test the PDF upload and analytical Q&A endpoints.
"""

import asyncio
import httpx
import json
import os

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

async def test_upload_pdf():
    """Test the PDF upload endpoint."""
    # Create a sample PDF content (you would use a real PDF file)
    sample_pdf_path = "test_sample.pdf"
    
    # For testing, we'll create a simple text file and rename it
    # In real usage, you would upload actual PDF files
    try:
        with open(sample_pdf_path, "wb") as f:
            # Create a minimal PDF-like content for testing
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        
        async with httpx.AsyncClient() as client:
            try:
                with open(sample_pdf_path, "rb") as f:
                    files = {"file": ("test.pdf", f, "application/pdf")}
                    response = await client.post(f"{BASE_URL}/upload", files=files)
                
                print(f"Upload Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"Upload Response: {result}")
                    return result.get("document_id")
                else:
                    print(f"Upload failed: {response.text}")
                    return None
            except Exception as e:
                print(f"Upload request failed: {e}")
                return None
    except Exception as e:
        print(f"Could not create test PDF: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(sample_pdf_path):
            os.remove(sample_pdf_path)

async def test_ask_question():
    """Test the ask endpoint."""
    test_data = {
        "question": "What are the key findings and conclusions in the research documents?"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/ask",
                json=test_data,
                timeout=60.0
            )
            print(f"Ask Endpoint Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Answer: {result['answer']}")
                print(f"Trace ID: {result['trace_id']}")
                print(f"Sources: {len(result.get('sources', []))} sources found")
                for i, source in enumerate(result.get('sources', [])[:2]):  # Show first 2 sources
                    print(f"  Source {i+1}: {source['text'][:100]}...")
            else:
                print(f"Ask failed: {response.text}")
        except Exception as e:
            print(f"Ask endpoint failed: {e}")

async def test_list_documents():
    """Test the documents listing endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/documents")
            print(f"Documents Status: {response.status_code}")
            print(f"Documents Response: {response.json()}")
        except Exception as e:
            print(f"Documents endpoint failed: {e}")

async def main():
    """Run all tests."""
    print("Testing ScreenPilot Research Copilot Backend Service")
    print("=" * 60)
    
    print("\n1. Testing Health Check...")
    await test_health()
    
    print("\n2. Testing PDF Upload...")
    document_id = await test_upload_pdf()
    
    print("\n3. Testing Ask Question...")
    await test_ask_question()
    
    print("\n4. Testing List Documents...")
    await test_list_documents()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("\nNote: For full testing, upload actual PDF documents with research content.")

if __name__ == "__main__":
    asyncio.run(main())
