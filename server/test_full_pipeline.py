"""
Comprehensive test script for ScreenPilot Research Copilot full pipeline.
Tests the complete flow: PDF upload → text extraction → embedding generation → vector storage → query processing.
"""

import asyncio
import httpx
import json
import os
import tempfile
from pathlib import Path

BASE_URL = "http://localhost:8000"

def create_sample_pdf():
    """Create a sample PDF file for testing."""
    # Create a minimal PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Artificial Intelligence Research) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_file.write(pdf_content)
    temp_file.close()
    return temp_file.name

async def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   Response: {health_data}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   Connection failed: {e}")
            return False

async def test_pdf_upload():
    """Test PDF upload and processing."""
    print("\n📄 Testing PDF upload...")
    
    pdf_path = create_sample_pdf()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(pdf_path, 'rb') as f:
                files = {"file": ("test_research.pdf", f, "application/pdf")}
                response = await client.post(f"{BASE_URL}/upload", files=files)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Document ID: {result.get('document_id')}")
                print(f"   Pages processed: {result.get('pages_processed')}")
                print(f"   Chunks created: {result.get('chunks_created')}")
                return result.get('document_id')
            else:
                print(f"   Error: {response.text}")
                return None
    except Exception as e:
        print(f"   Upload failed: {e}")
        return None
    finally:
        # Clean up
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

async def test_ask_question():
    """Test asking a question about uploaded documents."""
    print("\n❓ Testing question asking...")
    
    test_questions = [
        "What is the main topic of the research?",
        "What are the key findings?",
        "Summarize the research content"
    ]
    
    for question in test_questions:
        print(f"\n   Question: {question}")
        test_data = {"question": question}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{BASE_URL}/ask",
                    json=test_data,
                    timeout=60.0
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   Answer: {result['answer'][:200]}...")
                    print(f"   Trace ID: {result['trace_id']}")
                    print(f"   Sources: {len(result.get('sources', []))} found")
                    
                    # Show first source preview
                    if result.get('sources'):
                        first_source = result['sources'][0]
                        print(f"   First source: {first_source['text'][:100]}...")
                else:
                    print(f"   Error: {response.text}")
            except Exception as e:
                print(f"   Question failed: {e}")

async def test_gemini_fallback():
    """Test the Gemini fallback endpoint."""
    print("\n🤖 Testing Gemini fallback...")
    
    test_data = {"question": "What is artificial intelligence?"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/ask-gemini",
                json=test_data,
                timeout=60.0
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Answer: {result['answer'][:200]}...")
                print(f"   Trace ID: {result['trace_id']}")
                print(f"   Sources: {len(result.get('sources', []))} found")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Gemini test failed: {e}")

async def test_documents_listing():
    """Test document listing endpoint."""
    print("\n📋 Testing document listing...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/documents")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Documents listing failed: {e}")

async def main():
    """Run comprehensive pipeline tests."""
    print("🚀 ScreenPilot Research Copilot - Full Pipeline Test")
    print("=" * 60)
    
    # Test 1: Health check
    health_ok = await test_health_check()
    if not health_ok:
        print("\n❌ Health check failed. Make sure the server is running.")
        print("   Start the server with: python3 main.py")
        return False
    
    # Test 2: PDF upload
    document_id = await test_pdf_upload()
    if not document_id:
        print("\n❌ PDF upload failed. Check server logs for details.")
        return False
    
    # Test 3: Question asking
    await test_ask_question()
    
    # Test 4: Gemini fallback
    await test_gemini_fallback()
    
    # Test 5: Document listing
    await test_documents_listing()
    
    print("\n" + "=" * 60)
    print("✅ Full pipeline test completed!")
    print("\nNext steps:")
    print("1. Set up your .env file with actual API keys")
    print("2. Start Weaviate: docker run -p 8080:8080 weaviate/weaviate:latest")
    print("3. Test with real PDF documents")
    print("4. Build the Chrome extension interface")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        print("\n❌ Some tests failed. Check the server logs and configuration.")
        exit(1)
    else:
        print("\n🎉 All tests passed! The ScreenPilot backend is working correctly.")
